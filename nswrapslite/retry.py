#!/usr/bin/env python3
"""
==============================================================
Description  : 重试机制模块 - 提供函数重试和异常处理功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-09-01 08:40:27
LastEditTime : 2025-09-11 16:40:00
Github       : https://github.com/sandorn/nswraps

本模块提供以下核心功能：
- retry_wraps：函数重试装饰器，支持自定义重试策略
- retry_async_wraps：异步函数重试装饰器
- retry_request：HTTP请求重试函数，支持自定义重试策略
- retry_future：Future对象重试函数，支持自定义重试策略

主要特性：
- 支持同步和异步函数的重试
- 灵活的重试策略配置（次数、间隔、退避算法）
- 自定义异常过滤和重试条件
- 完整的日志记录和异常处理
- 支持HTTP请求和Future对象的重试
==============================================================
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable, Coroutine, Sequence
from concurrent.futures import Future
from functools import wraps
from typing import Any, Protocol, TypeVar

# 导入异常处理模块

# 类型变量
T = TypeVar('T')
R = TypeVar('R')


class RequestLike(Protocol):
    """请求类接口协议，用于类型提示"""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class RetryStrategy:
    """重试策略类 - 封装重试相关的配置和逻辑"""

    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        jitter: float = 0.1,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        retry_on_result: Callable[[Any], bool] | None = None,
    ) -> None:
        """
        初始化重试策略

        Args:
            max_retries: 最大重试次数，默认3次
            delay: 初始延迟时间（秒），默认1秒
            backoff: 退避系数，每次重试延迟时间会乘以此系数，默认2
            jitter: 抖动系数，为延迟时间添加随机抖动，默认0.1
            exceptions: 需要重试的异常类型，默认为所有Exception
            retry_on_result: 根据结果决定是否重试的函数，默认为None
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.jitter = jitter
        self.exceptions = exceptions
        self.retry_on_result = retry_on_result

    def calculate_delay(self, attempt: int) -> float:
        """
        计算当前重试的延迟时间

        Args:
            attempt: 当前重试次数（从1开始）

        Returns:
            计算后的延迟时间（秒）
        """
        delay = self.delay * (self.backoff ** (attempt - 1))
        if self.jitter:
            # 使用random.SystemRandom来满足安全要求
            import random

            delay = delay * (1 + random.SystemRandom().uniform(-self.jitter, self.jitter))
        return delay

    def should_retry_on_exception(self, exception: Exception) -> bool:
        """
        判断是否应该对指定异常进行重试

        Args:
            exception: 捕获到的异常

        Returns:
            是否应该重试
        """
        return isinstance(exception, self.exceptions)

    def should_retry_on_result(self, result: Any) -> bool:
        """
        判断是否应该对指定结果进行重试

        Args:
            result: 函数执行结果

        Returns:
            是否应该重试
        """
        if self.retry_on_result is None:
            return False
        return self.retry_on_result(result)


def retry_wraps[T](
    fn: Callable[..., T] | None = None,
    *,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_result: Callable[[Any], bool] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]] | Callable[..., T]:
    """
    重试装饰器 - 为函数添加自动重试功能

    核心功能：
    - 自动重试失败的函数调用
    - 支持指数退避策略和随机抖动
    - 可自定义重试条件和异常类型
    - 详细的日志记录

    Args:
        fn: 要装饰的函数，可选
        max_retries: 最大重试次数，默认3次
        delay: 初始延迟时间（秒），默认1秒
        backoff: 退避系数，每次重试延迟时间会乘以此系数，默认2
        jitter: 抖动系数，为延迟时间添加随机抖动，默认0.1
        exceptions: 需要重试的异常类型，默认为所有Exception
        retry_on_result: 根据结果决定是否重试的函数，默认为None

    Returns:
        装饰后的函数，具有重试功能

    示例:
        @retry_wraps(max_retries=5, delay=2.0)
        def unstable_function():
            # 可能失败的操作
            pass

        # 或者使用自定义重试条件
        @retry_wraps(retry_on_result=lambda x: x is None)
        def get_data():
            # 尝试获取数据，可能返回None
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        strategy = RetryStrategy(
            max_retries=max_retries,
            delay=delay,
            backoff=backoff,
            jitter=jitter,
            exceptions=exceptions,
            retry_on_result=retry_on_result,
        )

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(1, strategy.max_retries + 2):  # +2 因为第一次不是重试,最后一次是最终尝试
                try:
                    result = func(*args, **kwargs)

                    # 检查结果是否需要重试
                    if attempt <= strategy.max_retries and strategy.should_retry_on_result(result):
                        retry_delay = strategy.calculate_delay(attempt)
                        time.sleep(retry_delay)
                        continue

                    return result
                except Exception as e:
                    last_exception = e

                    # 检查是否应该重试此异常
                    if attempt <= strategy.max_retries and strategy.should_retry_on_exception(e):
                        retry_delay = strategy.calculate_delay(attempt)
                        time.sleep(retry_delay)
                        continue

                    # 如果不应该重试或已达到最大重试次数,则抛出最后一个异常
                    raise

            # 这里理论上不会执行到,因为要么返回结果,要么抛出异常
            if last_exception is None:
                raise RuntimeError('Unexpected state: last_exception is None when it should contain an exception')
            raise last_exception

        return wrapper

    # 处理装饰器调用方式
    return decorator if fn is None else decorator(fn)


def retry_async_wraps[T](
    fn: Callable[..., Awaitable[T]] | None = None,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_result: Callable[[Any], bool] | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Coroutine[Any, Any, T]]] | Callable[..., Coroutine[Any, Any, T]]:
    """
    异步重试装饰器 - 为异步函数添加自动重试功能

    核心功能：
    - 自动重试失败的异步函数调用
    - 支持指数退避策略和随机抖动
    - 可自定义重试条件和异常类型
    - 详细的日志记录

    Args:
        fn: 要装饰的异步函数，可选
        max_retries: 最大重试次数，默认3次
        delay: 初始延迟时间（秒），默认1秒
        backoff: 退避系数，每次重试延迟时间会乘以此系数，默认2
        jitter: 抖动系数，为延迟时间添加随机抖动，默认0.1
        exceptions: 需要重试的异常类型，默认为所有Exception
        retry_on_result: 根据结果决定是否重试的函数，默认为None

    Returns:
        装饰后的异步函数，具有重试功能

    示例:
        @retry_async_wraps(max_retries=5, delay=2.0)
        async def unstable_async_function():
            # 可能失败的异步操作
            pass
    """

    def decorator(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        strategy = RetryStrategy(
            max_retries=max_retries,
            delay=delay,
            backoff=backoff,
            jitter=jitter,
            exceptions=exceptions,
            retry_on_result=retry_on_result,
        )

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(1, strategy.max_retries + 2):  # +2 因为第一次不是重试,最后一次是最终尝试
                try:
                    result = await func(*args, **kwargs)

                    # 检查结果是否需要重试
                    if attempt <= strategy.max_retries and strategy.should_retry_on_result(result):
                        retry_delay = strategy.calculate_delay(attempt)
                        await asyncio.sleep(retry_delay)
                        continue

                    return result
                except Exception as e:
                    last_exception = e

                    # 检查是否应该重试此异常
                    if attempt <= strategy.max_retries and strategy.should_retry_on_exception(e):
                        retry_delay = strategy.calculate_delay(attempt)
                        await asyncio.sleep(retry_delay)
                        continue

                    # 如果不应该重试或已达到最大重试次数,则抛出最后一个异常
                    raise

            # 这里理论上不会执行到,因为要么返回结果,要么抛出异常
            if last_exception is None:
                raise RuntimeError('Unexpected state: last_exception is None when it should contain an exception')
            raise last_exception

        return wrapper

    # 处理装饰器调用方式
    return decorator(fn) if fn else decorator


async def retry_future[T](
    future_factory: Callable[[], Future[T]],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_result: Callable[[Any], bool] | None = None,
) -> T:
    """
    Future重试函数 - 为Future对象添加重试功能

    核心功能：
    - 自动重试失败的Future操作
    - 支持指数退避策略和随机抖动
    - 可自定义重试条件和异常类型
    - 详细的日志记录

    Args:
        future_factory: 创建Future对象的工厂函数
        max_retries: 最大重试次数，默认3次
        delay: 初始延迟时间（秒），默认1秒
        backoff: 退避系数，每次重试延迟时间会乘以此系数，默认2
        jitter: 抖动系数，为延迟时间添加随机抖动，默认0.1
        exceptions: 需要重试的异常类型，默认为所有Exception
        retry_on_result: 根据结果决定是否重试的函数，默认为None

    Returns:
        Future完成后的结果

    示例:
        async def get_data():
            future = executor.submit(fetch_data)
            return await retry_future(
                lambda: executor.submit(fetch_data),
                max_retries=5
            )
    """
    strategy = RetryStrategy(
        max_retries=max_retries,
        delay=delay,
        backoff=backoff,
        jitter=jitter,
        exceptions=exceptions,
        retry_on_result=retry_on_result,
    )

    last_exception: Exception | None = None

    for attempt in range(1, strategy.max_retries + 2):  # +2 因为第一次不是重试,最后一次是最终尝试
        future = future_factory()

        try:
            # 等待Future完成
            result = await asyncio.wrap_future(future)

            # 检查结果是否需要重试
            if attempt <= strategy.max_retries and strategy.should_retry_on_result(result):
                retry_delay = strategy.calculate_delay(attempt)
                await asyncio.sleep(retry_delay)
                continue

            return result

        except Exception as e:
            last_exception = e

            # 检查是否应该重试此异常
            if attempt <= strategy.max_retries and strategy.should_retry_on_exception(e):
                retry_delay = strategy.calculate_delay(attempt)
                await asyncio.sleep(retry_delay)
                continue

            # 如果不应该重试或已达到最大重试次数,则抛出最后一个异常
            raise

    # 这里理论上不会执行到,因为要么返回结果,要么抛出异常
    if last_exception is None:
        raise RuntimeError('Unexpected state: last_exception is None when it should contain an exception')
    raise last_exception


def retry_request(
    request_func: RequestLike,
    *args: Any,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_status: Sequence[int] | None = None,
    **kwargs: Any,
) -> Any:
    """
    HTTP请求重试函数 - 为HTTP请求添加重试功能

    核心功能：
    - 自动重试失败的HTTP请求
    - 支持指数退避策略和随机抖动
    - 可自定义重试条件和异常类型
    - 支持基于HTTP状态码的重试
    - 详细的日志记录

    Args:
        request_func: HTTP请求函数（如requests.get）
        *args: 传递给请求函数的位置参数
        max_retries: 最大重试次数，默认3次
        delay: 初始延迟时间（秒），默认1秒
        backoff: 退避系数，每次重试延迟时间会乘以此系数，默认2
        jitter: 抖动系数，为延迟时间添加随机抖动，默认0.1
        exceptions: 需要重试的异常类型，默认为所有Exception
        retry_on_status: 需要重试的HTTP状态码列表，默认为None
        **kwargs: 传递给请求函数的关键字参数

    Returns:
        HTTP请求的响应对象

    示例:
        response = retry_request(
            requests.get,
            "https://api.example.com/data",
            max_retries=5,
            retry_on_status=[429, 500, 502, 503, 504],
            timeout=10
        )
    """

    # 定义基于状态码的重试条件
    def should_retry_on_response(response: Any) -> bool:
        if retry_on_status is None:
            return False

        # 尝试获取响应的状态码
        status_code = getattr(response, 'status_code', None)
        if status_code is None:
            return False

        return status_code in retry_on_status

    # 使用重试装饰器包装请求函数
    @retry_wraps(
        max_retries=max_retries,
        delay=delay,
        backoff=backoff,
        jitter=jitter,
        exceptions=exceptions,
        retry_on_result=should_retry_on_response,
    )
    def wrapped_request() -> Any:
        return request_func(*args, **kwargs)

    # 执行包装后的请求函数
    return wrapped_request()


# 导出模块公共接口
__all__ = ['retry_async_wraps', 'retry_future', 'retry_request', 'retry_wraps']
