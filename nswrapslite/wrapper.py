# !/usr/bin/env python3
"""
==============================================================
Description  : 装饰器工具模块 - 提供通用装饰器工厂和常用装饰器
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-09-27 01:00:00
LastEditTime : 2025-09-27 01:00:00
Github       : https://github.com/sandorn/nswraps

本模块提供以下核心功能:
- 通用装饰器工厂，支持同步/异步函数
- 计时装饰器，记录函数执行时间
- 异常处理装饰器，统一异常处理逻辑
- 日志装饰器，记录函数调用信息

主要特性:
- 支持同步和异步函数
- 模块化设计，职责分离清晰
- 完整类型注解，符合现代Python语法
- Google风格文档字符串
==============================================================
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import Any, TypeAlias, Protocol, TypeVar

from xtlog import mylog, get_function_location

# 导入异常处理函数
from .exception import handle_exception

# 类型别名
ExceptionTypes: TypeAlias = tuple[type[Exception], ...]


# 定义钩子函数的协议类型
class BeforeHook(Protocol):
    def __call__(
        self,
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        context: dict[str, Any],
    ) -> Any: ...


class AfterHook(Protocol):
    def __call__(self, func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any], result: Any, context: dict[str, Any]) -> Any: ...


class ExceptHook(Protocol):
    def __call__(self, func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any], exc: Exception, context: dict[str, Any]) -> Any: ...


# 定义一个通用的可等待函数类型
T = TypeVar('T')
AwaitableCallable = Callable[..., T]


async def maybe_await(fn: Callable[..., T] | None, *args: Any, **kwargs: Any) -> T | None:
    """根据函数类型执行同步或异步调用

    Args:
        fn: 要执行的函数，可为None
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        Any: 函数执行结果，如果fn为None则返回None

    Example:
        >>> async def async_func(x):
        ...     return x * 2
        >>> def sync_func(x):
        ...     return x * 2
        >>> # 异步函数调用
        >>> result = await maybe_await(async_func, 5)
        >>> # 同步函数调用
        >>> result = await maybe_await(sync_func, 5)
    """
    if fn is None:
        return None
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


def decorator_factory(
    before_hook: BeforeHook | None = None,
    after_hook: AfterHook | None = None,
    except_hook: ExceptHook | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """通用装饰器工厂，支持同步/异步函数

    Args:
        before_hook: 前置钩子函数，签名为(func, args, kwargs, context)
        after_hook: 后置钩子函数，签名为(func, args, kwargs, result, context)
        except_hook: 异常钩子函数，签名为(func, args, kwargs, exc, context)

    Returns:
        Callable[[Callable], Callable]: 装饰器函数

    Example:
        >>> # 创建简单的日志装饰器
        >>> def log_before(func, args, kwargs, context):
        ...     print(f'调用函数: {func.__name__}')
        >>> @decorator_factory(before_hook=log_before)
        ... def my_function(x):
        ...     return x * 2

    Note:
        该工厂支持同步和异步函数，会自动检测函数类型并创建相应的包装器
    """

    def _build_async_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        """构建异步函数包装器

        Args:
            func: 被装饰的异步函数

        Returns:
            Callable: 异步包装器函数
        """

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """异步函数包装器实现"""
            context: dict[str, Any] = {}
            if before_hook:
                hook_result = await maybe_await(before_hook, func, args, kwargs, context)
                if hook_result is not None:
                    return hook_result
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                if except_hook:
                    return await maybe_await(except_hook, func, args, kwargs, e, context)
                raise
            if after_hook:
                after_result = await maybe_await(after_hook, func, args, kwargs, result, context)
                return after_result if after_result is not None else result
            return result

        return async_wrapper

    def _build_sync_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        """构建同步函数包装器

        Args:
            func: 被装饰的同步函数

        Returns:
            Callable: 同步包装器函数
        """

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """同步函数包装器实现"""
            context: dict[str, Any] = {}
            if before_hook:
                hook_result = before_hook(func, args, kwargs, context)
                if hook_result is not None:
                    return hook_result
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if except_hook:
                    return except_hook(func, args, kwargs, e, context)
                raise
            if after_hook:
                after_result = after_hook(func, args, kwargs, result, context)
                return after_result if after_result is not None else result
            return result

        return sync_wrapper

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """实际的装饰器函数

        Args:
            func: 被装饰的函数

        Returns:
            Callable: 包装后的函数
        """
        if asyncio.iscoroutinefunction(func):
            return _build_async_wrapper(func)
        return _build_sync_wrapper(func)

    return decorator


def timer_wrapper(
    func: Callable[..., Any] | None = None,
) -> Callable[..., Any]:
    """计时装饰器，记录函数执行时间

    Args:
        func: 被装饰的函数，支持直接装饰和带参数装饰两种方式

    Returns:
        Callable: 包装后的函数

    Raises:
        Exception: 被装饰函数抛出的任何异常

    Example:
        >>> @timer_wrapper
        ... def slow_function():
        ...     import time
        ...
        ...     time.sleep(1)
        ...     return '完成'

        >>> @timer_wrapper
        ... def error_function():
        ...     raise ValueError('测试异常')

        >>> # 异步函数支持
        >>> @timer_wrapper
        ... async def async_slow_function():
        ...     await asyncio.sleep(1)
        ...     return '异步完成'
    """

    def _before(
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        context: dict[str, Any],
    ) -> None:
        """执行前记录开始时间

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数
            context: 上下文字典
        """
        context['start'] = perf_counter()

    def _after(
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        result: Any,
        context: dict[str, Any],
    ) -> Any:
        """执行后记录结束时间

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数
            result: 函数执行结果
            context: 上下文字典
        """
        start = context.get('start')
        if start is not None:
            end = perf_counter()
            func_location = get_function_location(func)
            mylog.info(f'[{func_location}] 执行耗时: {end - start:.4f}秒')
        return result

    def _except(
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        exc: Exception,
        context: dict[str, Any],
    ) -> None:
        """异常处理钩子，记录异常发生时的执行时间

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数
            exc: 捕获的异常
            context: 上下文字典

        Raises:
            Exception: 重新抛出原始异常
        """
        start = context.get('start')
        if start is not None:
            end = perf_counter()
            func_location = get_function_location(func)
            mylog.error(f'[{func_location}] 失败耗时: {end - start:.4f}秒')
        raise exc

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """实际的装饰器函数

        Args:
            func: 被装饰的函数

        Returns:
            Callable: 包装后的函数
        """
        decorator_instance = decorator_factory(before_hook=_before, after_hook=_after, except_hook=_except)
        return decorator_instance(func)

    return decorator if func is None else decorator(func)


def exc_wrapper(
    func: Callable[..., Any] | None = None,
    *,
    re_raise: bool = True,
    default_return: Any = None,
    allowed_exceptions: ExceptionTypes = (Exception,),
    log_traceback: bool = True,
    custom_message: str | None = None,
) -> Callable[..., Any]:
    """通用异常处理装饰器，支持同步和异步函数

    Args:
        func: 被装饰的函数，支持直接装饰和带参数装饰两种方式
        re_raise: 是否重新抛出异常，默认False
        default_return: 发生异常时的默认返回值，默认None
        allowed_exceptions: 允许捕获的异常类型元组，默认捕获所有异常
        log_traceback: 是否记录完整堆栈信息，默认True
        custom_message: 自定义错误提示信息，默认None

    Returns:
        Callable: 装饰后的函数

    Raises:
        Exception: 当re_raise=True且异常不在allowed_exceptions中时抛出

    Example:
        >>> # 基本使用，捕获所有异常并返回None
        >>> @exc_wrapper
        ... def divide(a: int, b: int) -> float:
        ...     return a / b

        >>> # 只捕获特定异常，其他异常会重新抛出
        >>> @exc_wrapper(allowed_exceptions=(ZeroDivisionError,), re_raise=False, default_return=0)
        ... def safe_divide(a: int, b: int) -> float:
        ...     return a / b

        >>> # 自定义错误消息
        >>> @exc_wrapper(custom_message='除法运算失败', re_raise=False)
        ... def custom_divide(a: int, b: int) -> float:
        ...     return a / b

        >>> # 异步函数支持
        >>> @exc_wrapper
        ... async def async_divide(a: int, b: int) -> float:
        ...     return a / b

    Note:
        该装饰器会自动检测函数类型并创建相应的同步或异步包装器
    """

    def _except_hook(
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        exc: Exception,
        context: dict[str, Any],
    ) -> Any:
        """异常钩子函数，处理捕获的异常

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数
            exc: 捕获的异常
            context: 上下文字典

        Raises:
            Exception: 当异常不在allowed_exceptions中时重新抛出
        """
        # 检查异常类型是否在允许捕获的列表中
        if not isinstance(exc, allowed_exceptions):
            raise exc

        # 使用统一的异常处理函数
        func_location = get_function_location(func)
        custom_msg = f'{custom_message} [{func_location}]' if custom_message else f'[{func_location}]'
        return handle_exception(
            errinfo=exc,
            re_raise=re_raise,
            default_return=default_return,
            log_traceback=log_traceback,
            custom_message=custom_msg,
        )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """装饰器内部函数

        Args:
            func: 被装饰的函数

        Returns:
            Callable: 包装后的函数
        """
        # 使用decorator_factory创建装饰器
        decorator_instance = decorator_factory(except_hook=_except_hook)
        return decorator_instance(func)

    return decorator if func is None else decorator(func)


def log_wrapper(
    func: Callable[..., Any] | None = None,
    *,
    re_raise: bool = True,
    default_return: Any = None,
    log_args: bool = True,
    log_result: bool = True,
    log_traceback: bool = True,
    custom_message: str | None = None,
) -> Callable[..., Any]:
    """日志装饰器，记录函数调用信息

    Args:
        func: 被装饰的函数，支持直接装饰和带参数装饰两种方式
        re_raise: 是否重新抛出异常，默认False
        default_return: 发生异常时的默认返回值，默认None
        log_args: 是否记录函数参数，默认True
        log_result: 是否记录函数结果，默认True
        log_traceback: 是否记录完整堆栈信息，默认True
        custom_message: 自定义日志消息，默认None

    Returns:
        Callable: 包装后的函数

    Example:
        >>> @log_wrapper
        ... def add(a: int, b: int) -> int:
        ...     return a + b

        >>> # 异步函数支持
        >>> @log_wrapper
        ... async def async_add(a: int, b: int) -> int:
        ...     return a + b

        >>> # 自定义配置
        >>> @log_wrapper(log_args=False, log_result=False)
        ... def silent_function(x):
        ...     return x * 2
    """

    def _before(
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        context: dict[str, Any],
    ) -> None:
        """日志装饰器前置钩子

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数
            context: 上下文字典
        """
        if log_args:
            func_location = get_function_location(func)
            mylog.debug(f'[{func_location}] args: {args}, kwargs: {kwargs}')

    def _after(
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        result: Any,
        context: dict[str, Any],
    ) -> Any:
        """日志装饰器后置钩子

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数
            result: 函数执行结果
            context: 上下文字典
        """
        if log_result:
            func_location = get_function_location(func)
            mylog.success(f'[{func_location}] result: {type(result).__name__} = {result}')
        return result

    def _except(
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        exc: Exception,
        context: dict[str, Any],
    ) -> Any:
        """日志装饰器异常钩子

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数
            exc: 捕获的异常
            context: 上下文字典
        """
        func_location = get_function_location(func)
        custom_msg = f'{custom_message} [{func_location}]' if custom_message else f'[{func_location}]'
        return handle_exception(
            errinfo=exc,
            re_raise=re_raise,
            default_return=default_return,
            log_traceback=log_traceback,
            custom_message=custom_msg,
        )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """装饰器内部函数

        Args:
            func: 被装饰的函数

        Returns:
            Callable: 包装后的函数
        """
        # 使用decorator_factory创建装饰器
        decorator_instance = decorator_factory(
            before_hook=_before,
            after_hook=_after,
            except_hook=_except,
        )
        return decorator_instance(func)

    return decorator if func is None else decorator(func)


__all__ = [
    'decorator_factory',
    'exc_wrapper',
    'log_wrapper',
    'timer_wrapper',
]

if __name__ == '__main__':
    """模块功能测试"""
    import time

    # ruff: noqa
    # 测试装饰器工厂
    print('=== 测试装饰器工厂 ===')

    def test_before_hook(func, args, kwargs, context):
        print(f'前置钩子: 调用函数 {func.__name__}')

    def test_after_hook(func, args, kwargs, result, context):
        print(f'后置钩子: 函数 {func.__name__} 返回 {result}')

    @decorator_factory(before_hook=test_before_hook, after_hook=test_after_hook)
    def test_factory(x: int) -> int:
        return x * 2

    result = test_factory(5)
    print(f'装饰器工厂测试结果: {result}')

    # 测试计时装饰器
    print('\n=== 测试计时装饰器 ===')

    @timer_wrapper
    def test_timer_success() -> str:
        time.sleep(0.5)
        return '成功完成'

    @timer_wrapper
    def test_timer_error() -> None:
        time.sleep(0.3)
        raise ValueError('测试异常')

    try:
        result = test_timer_success()
        print(f'计时器成功测试: {result}')
    except Exception as e:
        print(f'计时器成功测试异常: {e}')

    try:
        test_timer_error()
    except Exception as e:
        print(f'计时器错误测试异常: {e}')

    # 测试异常处理装饰器
    print('\n=== 测试异常处理装饰器 ===')

    @exc_wrapper
    def test_divide(a: int, b: int) -> float:
        return a / b

    @exc_wrapper(default_return=0, allowed_exceptions=(ZeroDivisionError,), re_raise=False)
    def test_safe_divide(a: int, b: int) -> float:
        return a / b

    result1 = test_divide(10, 2)
    print(f'正常除法结果: {result1}')

    result2 = test_safe_divide(10, 0)
    print(f'除零保护结果: {result2}')

    # 测试异步异常处理装饰器
    async def test_async_divide(a: int, b: int) -> float:
        return a / b

    async def test_async_safe_divide(a: int, b: int) -> float:
        return a / b

    async def run_async_tests():
        print('\n=== 测试异步异常处理装饰器 ===')

        decorated_async_divide = exc_wrapper(test_async_divide)
        decorated_async_safe_divide = exc_wrapper(default_return=0, allowed_exceptions=(ZeroDivisionError,), re_raise=False)(test_async_safe_divide)

        result3 = await decorated_async_divide(10, 2)
        print(f'异步正常除法结果: {result3}')

        result4 = await decorated_async_safe_divide(10, 0)
        print(f'异步除零保护结果: {result4}')

    # 测试日志装饰器
    print('\n=== 测试日志装饰器 ===')

    @log_wrapper
    def test_log_function(x: int, y: int) -> int:
        return x + y

    result5 = test_log_function(3, 4)
    print(f'日志装饰器测试结果: {result5}')

    # 运行异步测试
    asyncio.run(run_async_tests())

    print('\n=== 所有测试完成 ===')
