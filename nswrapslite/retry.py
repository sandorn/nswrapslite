# !/usr/bin/env python3
"""
==============================================================
Description  : 重试机制模块 - 提供函数执行失败自动重试功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-01 14:30:00
Github       : https://github.com/sandorn/nswrapslite

本模块提供以下核心功能：
- RetryStrategy：重试策略类，定义重试逻辑和参数
- retry_wraps：函数重试装饰器，支持同步和异步函数
- retry_wraps_with_strategy：使用自定义策略的函数重试装饰器
- exponential_backoff：指数退避等待时间计算函数

主要特性：
- 同时支持同步和异步函数
- 可配置的重试次数、等待时间和异常类型
- 多种重试等待策略（固定、随机、指数退避）
- 支持自定义重试条件和成功条件
- 完整的类型注解支持
- 保留原始函数的元数据
==============================================================
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable, Sequence
from concurrent.futures import Future
from functools import wraps
from typing import Any, Protocol

from xtlog import mylog

from .exception import _handle_exception
from .utils import get_function_location, is_async_function


class RequestLike(Protocol):
    """请求类接口协议，用于类型提示"""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class RetryStrategy:
    """重试策略类 - 封装所有重试相关配置，统一参数管理"""

    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        jitter: float = 0.1,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        retry_on_result: Callable[[Any], bool] | None = None,
        re_raise: bool = False,
        default_return: Any = None,
        handler: Callable[[Exception], Any] | None = None,
        log_traceback: bool = True,
        custom_message: str | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.jitter = jitter
        self.exceptions = exceptions
        self.retry_on_result = retry_on_result
        self.re_raise = re_raise
        self.default_return = default_return
        self.handler = handler
        self.log_traceback = log_traceback
        self.custom_message = custom_message  # 策略级别的默认消息

    def calculate_delay(self, attempt: int) -> float:
        """计算带抖动的退避延迟"""
        delay = self.delay * (self.backoff ** (attempt - 1))
        if self.jitter:
            import random

            delay *= 1 + random.SystemRandom().uniform(-self.jitter, self.jitter)
        return delay

    def should_retry_on_exception(self, exception: Exception) -> bool:
        """判断异常是否需要重试"""
        return isinstance(exception, self.exceptions)

    def should_retry_on_result(self, result: Any) -> bool:
        """判断结果是否需要重试"""
        return self.retry_on_result(result) if self.retry_on_result else False


def retry_wraps(
    fn: Callable[..., Any] | None = None,
    *,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_result: Callable[[Any], bool] | None = None,
    re_raise: bool = False,
    default_return: Any = None,
    handler: Callable[[Exception], Any] | None = None,
    log_traceback: bool = True,
    custom_message: str | None = None,
) -> Callable[..., Any]:
    """重试装饰器入口，根据函数类型选择同步/异步包装器

    Args:
        fn: 被装饰的函数
        max_retries: 最大重试次数，默认3
        delay: 初始等待时间（秒），默认1.0
        backoff: 退避因子，默认2.0
        jitter: 抖动范围（0-1），默认0.1
        exceptions: 触发重试的异常类型元组，默认(Exception,)
        retry_on_result: 自定义结果判断函数，默认None
        re_raise: 是否重新抛出异常，默认False
        default_return: 不抛出异常时的默认返回值，默认None
        handler: 异常处理函数，默认None
        log_traceback: 是否记录完整堆栈信息，默认True
        custom_message: 自定义错误提示信息，默认None

    Returns:
        Callable[..., Any]: 包装后的函数，根据原函数类型选择同步/异步包装器
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        current_location = get_function_location(func)
        # 创建统一的重试策略对象
        strategy = RetryStrategy(
            max_retries=max_retries,
            delay=delay,
            backoff=backoff,
            jitter=jitter,
            exceptions=exceptions,
            retry_on_result=retry_on_result,
            re_raise=re_raise,
            default_return=default_return,
            handler=handler,
            log_traceback=log_traceback,
            custom_message=f'{custom_message} {current_location}' if custom_message else current_location,
        )

        # 根据函数类型选择包装器
        if is_async_function(func):
            return _create_async_wrapper(func, strategy)
        return _create_sync_wrapper(func, strategy)

    return decorator(fn) if fn else decorator


def _create_sync_wrapper(func: Callable[..., Any], strategy: RetryStrategy) -> Callable[..., Any]:
    """创建同步函数的重试包装器"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exception: Exception | None = None

        for attempt in range(1, strategy.max_retries + 1):
            mylog.info(f'{strategy.custom_message} 第 {attempt} 次尝试')
            try:
                result = func(*args, **kwargs)
                # 修正：检查是否需要根据结果重试
                if strategy.should_retry_on_result(result) and attempt < strategy.max_retries:  # 还有重试次数
                    time.sleep(strategy.calculate_delay(attempt))
                    continue
                return result

            except Exception as exc:
                last_exception = exc
                if attempt < strategy.max_retries and strategy.should_retry_on_exception(exc):
                    time.sleep(strategy.calculate_delay(attempt))
                    continue
                # 没有重试次数了：退出循环，后续统一处理
                break

        # 所有重试失败后的处理
        return _handle_exception(
            exc=last_exception,
            re_raise=strategy.re_raise,
            handler=strategy.handler,
            default_return=strategy.default_return,
            log_traceback=strategy.log_traceback,
            custom_message=strategy.custom_message,
        )

    return wrapper


def _create_async_wrapper(func: Callable[..., Awaitable[Any]], strategy: RetryStrategy) -> Callable[..., Any]:
    """创建异步函数的重试包装器"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exception: Exception | None = None

        for attempt in range(1, strategy.max_retries + 1):
            mylog.info(f'{strategy.custom_message} 第 {attempt} 次尝试')
            try:
                result = await func(*args, **kwargs)
                # 修正：检查是否需要根据结果重试
                if strategy.should_retry_on_result(result) and attempt < strategy.max_retries:  # 还有重试次数
                    await asyncio.sleep(strategy.calculate_delay(attempt))
                    continue
                return result

            except Exception as exc:
                last_exception = exc
                if attempt < strategy.max_retries and strategy.should_retry_on_exception(exc):
                    await asyncio.sleep(strategy.calculate_delay(attempt))
                    continue
                # 没有重试次数了：退出循环，后续统一处理
                break

        # 所有重试失败后的处理
        return _handle_exception(
            exc=last_exception,
            re_raise=strategy.re_raise,
            handler=strategy.handler,
            default_return=strategy.default_return,
            log_traceback=strategy.log_traceback,
            custom_message=strategy.custom_message,
        )

    return wrapper


async def retry_future(
    future_factory: Callable[[], Future[Any]],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_result: Callable[[Any], bool] | None = None,
    re_raise: bool = False,
    default_return: Any = None,
    handler: Callable[[Exception], Any] | None = None,
    log_traceback: bool = True,
    custom_message: str | None = None,
) -> Any:
    """
    Future重试函数 - 复用_create_async_wrapper实现的新版本

    核心功能：
    - 自动重试失败的Future操作
    - 复用_create_async_wrapper确保逻辑一致性
    - 支持指数退避策略和随机抖动
    - 可自定义重试条件和异常类型
    - 详细的日志记录

    Args:
        future_factory: 创建Future对象的工厂函数
        max_retries: 最大重试次数，默认3次
        delay: 初始延迟时间(秒)，默认1秒
        backoff: 退避系数，每次重试延迟时间会乘以此系数，默认2
        jitter: 抖动系数，为延迟时间添加随机抖动，默认0.1
        exceptions: 需要重试的异常类型，默认为所有Exception
        retry_on_result: 根据结果决定是否重试的函数，默认为None
        re_raise: 是否重新抛出异常，默认False
        default_return: 默认返回值，当所有重试都失败时返回，默认None
        handler: 异常处理函数，默认None
        log_traceback: 是否记录异常堆栈跟踪，默认True
        custom_message: 自定义异常消息，默认None

    Returns:
        Future完成后的结果
    """

    # 创建异步包装函数，用于等待Future完成
    async def wait_future() -> Any:
        future = future_factory()
        return await asyncio.wrap_future(future)

    # 创建重试策略
    strategy = RetryStrategy(
        max_retries=max_retries,
        delay=delay,
        backoff=backoff,
        jitter=jitter,
        exceptions=exceptions,
        retry_on_result=retry_on_result,
        re_raise=re_raise,
        default_return=default_return,
        handler=handler,
        log_traceback=log_traceback,
        custom_message=custom_message or 'Future操作',
    )

    # 复用_create_async_wrapper创建重试包装器并执行
    wrapped_func = _create_async_wrapper(wait_future, strategy)
    return await wrapped_func()


def retry_request(
    request_func: RequestLike,
    *args: Any,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_status: Sequence[int] | None = [429, 500, 502, 503, 504],
    re_raise: bool = False,
    default_return: Any = None,
    handler: Callable[[Exception], Any] | None = None,
    log_traceback: bool = True,
    custom_message: str | None = None,
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
        request_func: HTTP请求函数(如requests.get)
        *args: 传递给请求函数的位置参数
        max_retries: 最大重试次数，默认3次
        delay: 初始延迟时间(秒)，默认1秒
        backoff: 退避系数，每次重试延迟时间会乘以此系数，默认2
        jitter: 抖动系数，为延迟时间添加随机抖动，默认0.1
        exceptions: 需要重试的异常类型，默认为所有Exception
        retry_on_status: 需要重试的HTTP状态码列表，默认为None
        re_raise: 是否重新抛出异常，默认False
        default_return: 默认返回值，当所有重试都失败时返回，默认None
        handler: 异常处理函数，默认None
        log_traceback: 是否记录异常堆栈跟踪，默认True
        custom_message: 自定义异常消息，默认None
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
        re_raise=re_raise,
        default_return=default_return,
        handler=handler,
        log_traceback=log_traceback,
        custom_message=custom_message,
    )
    def wrapped_request() -> Any:
        return request_func(*args, **kwargs)

    # 执行包装后的请求函数
    return wrapped_request()


# 导出模块公共接口
__all__ = ['retry_future', 'retry_request', 'retry_wraps']
