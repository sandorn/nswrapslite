#!/usr/bin/env python3
"""
==============================================================
Description  : 异步执行器模块 - 提供异步执行同步函数和后台任务的功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-09-01 08:40:27
LastEditTime : 2025-09-11 16:40:00
Github       : https://github.com/sandorn/nswraps

本模块提供以下核心功能：
- executor_wraps：异步执行同步函数，支持后台执行模式
- run_executor_wraps：同步运行异步函数，无需await
- future_wraps：将同步函数包装为返回Future对象的函数
- future_wraps_result：等待Future完成并返回结果，含超时处理

主要特性：
- 自动识别并适配同步和异步函数
- 支持后台执行模式，不阻塞主程序流程
- 统一的异常处理机制
- 支持自定义线程池执行器
- 提供超时控制和Future结果处理
- 完整的类型提示支持
==============================================================
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from concurrent.futures import Future as ThreadFuture
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from typing import Any, TypeVar, cast

# 导入异常处理模块
from .exception import handle_exception

# 类型变量
T = TypeVar('T')
R = TypeVar('R')
FutureT = TypeVar('FutureT', bound=asyncio.Future[Any] | ThreadFuture[Any])

# 常量定义
DEFAULT_EXECUTOR_MAX_WORKERS = 10  # 默认线程池最大工作线程数
DEFAULT_FUTURE_TIMEOUT = 30.0  # 默认Future超时时间(秒)

# 默认线程池执行器
_default_executor = ThreadPoolExecutor(max_workers=DEFAULT_EXECUTOR_MAX_WORKERS, thread_name_prefix='XtExecutor')


def _create_exception_handler() -> Callable[[asyncio.Future[Any]], None]:
    """创建统一的异常处理回调函数"""

    def exception_handler(fut: asyncio.Future[Any]) -> None:
        # 单独处理CancelledError，因为这是预期行为
        if fut.cancelled():
            return
        try:
            exc = fut.exception()
            if exc is not None:
                handle_exception(exc)
        except Exception as err:
            handle_exception(err)

    return exception_handler


def run_on_executor(
    executor: ThreadPoolExecutor | None = None, background: bool = False
) -> Callable[
    [Callable[..., T | Awaitable[T]]],
    Callable[..., Coroutine[Any, Any, T] | asyncio.Future[T]],
]:
    """
    异步装饰器
    - 支持同步函数使用 executor 加速
    - 异步函数和同步函数都可以使用 `await` 语法等待返回结果
    - 异步函数和同步函数都支持后台任务，无需等待
    Args:
        executor: 函数执行器, 装饰同步函数的时候使用
        background: 是否后台执行，默认False
    """

    # 复用已有的executor_wraps装饰器实现，降低复杂度
    def _run_on_executor(
        func: Callable[..., T | Awaitable[T]],
    ) -> Callable[..., Coroutine[Any, Any, T] | asyncio.Future[T]]:
        # 使用现有的executor_wraps装饰器处理各种情况
        decorator = ExecutorDecorators.executor_wraps(background=background, executor=executor)
        return decorator(func)  # type: ignore

    return _run_on_executor


class WrapperFactory:
    """包装器工厂类 - 集中管理各种包装器的创建逻辑"""

    @staticmethod
    def create_async_background_wrapper(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., asyncio.Task[T]]:
        """创建异步后台执行包装器"""

        @wraps(func)
        def async_background_wrapper(*args: Any, **kwargs: Any) -> asyncio.Task[T]:
            async def task_wrapper() -> T:
                try:
                    # 明确指定为协程调用
                    coro = func(*args, **kwargs)
                    return await coro
                except Exception as err:
                    return cast(T, handle_exception(err, re_raise=True))

            return asyncio.create_task(task_wrapper())

        return async_background_wrapper

    @staticmethod
    def create_async_wrapper(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        """创建异步包装器"""

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                return cast(T, handle_exception(err, re_raise=True))

        return async_wrapper

    @staticmethod
    def create_sync_background_wrapper(func: Callable[..., T], executor: ThreadPoolExecutor) -> Callable[..., asyncio.Future[T]]:
        """创建同步后台执行包装器"""

        @wraps(func)
        def sync_background_wrapper(*args: Any, **kwargs: Any) -> asyncio.Future[T]:
            loop = asyncio.get_event_loop()
            task_func = partial(func, *args, **kwargs)
            future = loop.run_in_executor(executor, task_func)
            future.add_done_callback(_create_exception_handler())
            return future

        return sync_background_wrapper

    @staticmethod
    def create_sync_wrapper(func: Callable[..., T], executor: ThreadPoolExecutor) -> Callable[..., Coroutine[Any, Any, T]]:
        """创建同步包装器"""

        @wraps(func)
        async def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            loop = asyncio.get_event_loop()
            task_func = partial(func, *args, **kwargs)
            try:
                return await loop.run_in_executor(executor, task_func)
            except Exception as err:
                return cast(T, handle_exception(errinfo=err, re_raise=True))

        return sync_wrapper


class EventLoopManager:
    """事件循环管理类 - 统一处理事件循环的创建和获取逻辑"""

    @staticmethod
    def get_event_loop() -> asyncio.AbstractEventLoop:
        """获取或创建事件循环"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            # 如果没有事件循环,创建一个新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    @staticmethod
    def run_in_new_thread(func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        """在新线程中运行异步函数，避免与已有事件循环冲突"""
        result: list[T] = []
        error: list[BaseException] = []

        def _run_in_new_loop():
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                # 确保func返回的是可等待对象
                coro = func(*args, **kwargs)
                result.append(new_loop.run_until_complete(coro))
            except BaseException as e:
                error.append(e)
            finally:
                new_loop.close()

        # 创建并启动新线程
        import threading

        thread = threading.Thread(target=_run_in_new_loop)
        thread.start()
        thread.join()

        # 处理结果或异常
        if error:
            raise error[0] from None
        return result[0]


class ExecutorDecorators:
    """执行器装饰器集合 - 提供各类执行器装饰器功能"""

    @staticmethod
    def executor_wraps(
        fn: Callable[..., T] | None = None,
        *,
        background: bool = False,
        executor: ThreadPoolExecutor | None = None,
    ) -> Callable[[Callable[..., T]], Callable[..., T]] | Callable[..., T]:
        """
        异步执行器装饰器 - 将同步函数转换为异步函数执行，或增强异步函数的执行能力

        核心功能：
        - 自动识别并适配同步/异步函数
        - 支持后台执行模式，不阻塞主程序流程
        - 统一的异常处理机制
        - 支持自定义线程池执行器

        Args:
            fn: 要装饰的函数，可选（支持同步和异步函数）
            background: 是否在后台执行，默认为False
                        - False: 返回协程对象，需要await等待执行完成
                        - True: 返回Future/Task对象，立即返回不阻塞
            executor: 自定义线程池执行器，默认为None（使用默认执行器）

        Returns:
            装饰后的函数，根据参数和原函数类型返回不同对象：
            - 当background=False时：返回协程对象，需要await
            - 当background=True时：返回Future/Task对象，可后续await获取结果
        """

        def decorator(func: Callable[..., T]) -> Callable[..., Any]:
            used_executor = executor or _default_executor

            if asyncio.iscoroutinefunction(func):
                if background:
                    # 返回Task包装器
                    return WrapperFactory.create_async_background_wrapper(func)
                # 返回协程包装器
                return WrapperFactory.create_async_wrapper(func)

            if background:
                # 返回Future包装器
                return WrapperFactory.create_sync_background_wrapper(func, used_executor)
            # 返回协程包装器
            return WrapperFactory.create_sync_wrapper(func, used_executor)

        # 处理装饰器调用方式
        return decorator(fn) if fn else decorator

    @staticmethod
    def run_executor_wraps(
        fn: Callable[..., T] | None = None,
    ) -> Callable[[Callable[..., T]], Callable[..., T]] | Callable[..., T]:
        """
        同步运行异步函数装饰器 - 将异步函数转换为可直接调用的同步函数

        核心功能：
        - 自动适配异步和同步函数
        - 智能事件循环管理（处理循环已运行、未创建等情况）
        - 统一的异常处理机制

        Args:
            fn: 要装饰的函数（支持同步和异步函数），可选

        Returns:
            同步函数，可以直接调用而不需要await
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                if asyncio.iscoroutinefunction(func):
                    try:
                        loop = EventLoopManager.get_event_loop()
                        if loop.is_running():
                            # 如果有正在运行的事件循环，在新线程中运行
                            return EventLoopManager.run_in_new_thread(func, *args, **kwargs)
                        # 直接运行协程
                        return loop.run_until_complete(func(*args, **kwargs))
                    except Exception as err:
                        # 异常处理函数可能返回默认值，需要明确返回
                        return cast(
                            T,
                            handle_exception(err, re_raise=False, default_return=None),
                        )
                else:
                    try:
                        return func(*args, **kwargs)
                    except Exception as err:
                        # 异常处理函数可能返回默认值，需要明确返回
                        return cast(
                            T,
                            handle_exception(err, re_raise=False, default_return=None),
                        )

            return sync_wrapper

        # 处理装饰器调用方式
        return decorator(fn) if fn else decorator

    @staticmethod
    def future_wraps(
        fn: Callable[..., T] | None = None,
        *,
        executor: ThreadPoolExecutor | None = None,
    ) -> Callable[[Callable[..., T]], Callable[..., asyncio.Future[T]]] | Callable[..., asyncio.Future[T]]:
        """
        Future执行器装饰器 - 将同步函数包装成返回asyncio.Future对象的函数

        核心功能：
        - 将同步函数转换为返回Future的函数
        - 支持自定义线程池执行器
        - 自动异常捕获和处理

        Args:
            fn: 要装饰的同步函数，可选
            executor: 自定义线程池执行器，默认为None（使用默认执行器）

        Returns:
            装饰后的函数，返回asyncio.Future对象，可通过await获取结果
        """

        def decorator(func: Callable[..., T]) -> Callable[..., asyncio.Future[T]]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> asyncio.Future[T]:
                try:
                    loop = asyncio.get_event_loop()
                    used_executor = executor or _default_executor
                    future = loop.run_in_executor(used_executor, lambda: func(*args, **kwargs))
                    future.add_done_callback(_create_exception_handler())
                    return future
                except Exception as err:
                    # 创建一个已完成的future并设置异常
                    loop = asyncio.get_event_loop()
                    future = loop.create_future()
                    future.set_exception(err)
                    return future

            return wrapper

        return decorator(fn) if fn else decorator


# 导出装饰器函数
executor_wraps = ExecutorDecorators.executor_wraps
run_executor_wraps = ExecutorDecorators.run_executor_wraps
future_wraps = ExecutorDecorators.future_wraps


async def future_wraps_result[T](future: asyncio.Future[T]) -> T:
    """
    Future结果获取器 - 等待Future完成并返回结果，带超时处理和异常管理

    核心功能：
    - 等待Future完成并获取结果
    - 自动超时处理，避免永久阻塞
    - 统一的异常处理机制
    - 自动取消超时的Future

    Args:
        future: 要等待的Future对象

    Returns:
        Future完成后的结果

    Raises:
        asyncio.TimeoutError: 当Future在DEFAULT_FUTURE_TIMEOUT(30秒)内未完成时
        asyncio.CancelledError: 当Future被取消时
        其他可能的异常: 由Future执行过程中抛出的原始异常

    示例:
        # 假设已有一个Future对象
        future = some_async_operation()

        try:
            # 等待Future完成并获取结果
            result = await future_wraps_result(future)
            print(f"结果: {result}")
        except asyncio.TimeoutError:
            print("操作超时")
        except Exception as e:
            print(f"发生错误: {e}")
    """
    try:
        # 添加超时机制,避免永久等待
        return await asyncio.wait_for(future, timeout=DEFAULT_FUTURE_TIMEOUT)
    except TimeoutError as timerr:
        # 如果超时,取消任务并抛出异常
        if not future.done():
            try:
                future.cancel()
                # 等待任务确认取消
                if future._state != 'CANCELLED':  # type: ignore[attr-defined]
                    await asyncio.sleep(0.01)
            except Exception as e:
                # 记录取消任务时的异常但不抛出
                handle_exception(errinfo=e, re_raise=False)
        return cast(T, handle_exception(errinfo=timerr, re_raise=True))
    except asyncio.CancelledError as cancerr:
        # CancelledError不是Exception的子类，需要特殊处理
        return cast(T, handle_exception(errinfo=cancerr, re_raise=True))
    except Exception as err:
        return cast(T, handle_exception(errinfo=err, re_raise=True))
