# !/usr/bin/env python3
"""
==============================================================
Description  : 异常处理模块 - 提供统一、可配置的异常处理和堆栈信息管理功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-09-05 17:32:29
LastEditTime : 2025-09-06 10:30:00
Github       : https://github.com/sandorn/nswraps

本模块提供了两个核心功能：
- get_simplified_traceback: 获取精简的堆栈跟踪信息，支持自定义显示帧数、过滤库文件帧等
- handle_exception: 统一的异常处理函数，支持日志记录、堆栈简化、异常重抛等功能

使用场景：
- 简化调试过程中的异常信息分析
- 统一应用程序的异常处理逻辑
- 在不同环境中动态调整异常信息的详细程度
- 提供友好的错误反馈和日志记录
==============================================================
"""

from __future__ import annotations

import asyncio
import traceback
from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from xtlog import mylog

# 定义类型变量
T = TypeVar('T')
R = TypeVar('R')
P = ParamSpec('P')

# 类型别名
ExceptionHandler = Callable[[Exception], R]
ExceptionTypes = tuple[type[Exception], ...]


def handle_exception[R](
    errinfo: BaseException,
    re_raise: bool = True,
    default_return: R | None = None,
    log_traceback: bool = True,
    custom_message: str | None = None,
) -> R | None:
    """
    统一的异常处理函数，提供完整的异常捕获、记录和处理机制

    Args:
        errinfo: 异常对象
        re_raise: 是否重新抛出异常，默认True（抛出异常）
        default_return: 不抛出异常时的默认返回值，default_return为None时返回错误信息字符串
        log_traceback: 是否记录完整堆栈信息，默认True
        custom_message: 自定义错误提示信息，默认None

    Returns:
        Any: 如果re_raise=True，重新抛出异常；否则返回default_return或错误信息字符串

    Example:
        >>> # 基本使用
        >>> try:
        ...     result = 10 / 0
        ... except Exception as e:
        ...     # 记录异常但不中断程序
        ...     result = handle_exception(e, re_raise=False, default_return=0)
        >>> print(result)  # 输出: 0
    """

    # 构建错误信息
    error_type = type(errinfo).__name__
    error_msg = str(errinfo)

    # 统一的日志格式
    error_message = f'except: {error_type} | {error_msg} | {custom_message or ""}'
    # 记录警告日志
    mylog.error(error_message)

    # 如果需要,记录完整堆栈信息
    if log_traceback:
        mylog.error(traceback.format_exc())

    # 根据需要重新抛出异常
    if re_raise:
        raise errinfo

    return default_return


def _create_async_wrapper(
    func: Callable[..., Awaitable[R]],
    re_raise: bool,
    default_return: R | None,
    allowed_exceptions: ExceptionTypes,
    log_traceback: bool,
    custom_message: str | None,
) -> Callable[..., Coroutine[Any, Any, R | None]]:
    """创建异步包装器"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R | None:
        """异步函数包装器"""
        try:
            # 确保返回的是R类型
            return await func(*args, **kwargs)
        except allowed_exceptions as err:
            # 直接调用handle_exception，如果re_raise=True，它会抛出异常
            result = handle_exception(
                errinfo=err,
                re_raise=re_raise,
                default_return=default_return,
                log_traceback=log_traceback,
                custom_message=custom_message,
            )
            return result  # type: ignore # noqa
        except Exception as err:
            raise err  # 保持异常链完整性

    return wrapper


def _create_sync_wrapper(
    func: Callable[..., R],
    re_raise: bool,
    default_return: R | None,
    allowed_exceptions: ExceptionTypes,
    log_traceback: bool,
    custom_message: str | None,
) -> Callable[..., R | None]:
    """创建同步包装器"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R | None:
        """同步函数包装器"""
        try:
            return func(*args, **kwargs)
        except allowed_exceptions as err:
            # 直接调用handle_exception，如果re_raise=True，它会抛出异常
            return handle_exception(
                errinfo=err,
                re_raise=re_raise,
                default_return=default_return,
                log_traceback=log_traceback,
                custom_message=custom_message,
            )
        except Exception as err:
            raise err  # 保持异常链完整性

    return wrapper


def exc_wraps(
    func: Callable[..., R] | None = None,
    *,
    re_raise: bool = True,
    default_return: R | None = None,
    allowed_exceptions: ExceptionTypes = (Exception,),
    log_traceback: bool = True,
    custom_message: str | None = None,
) -> Callable[[Callable[..., R]], Callable[..., R | None]] | Callable[..., R | None]:
    """
    通用异常处理装饰器 - 支持同步和异步函数

    Args:
        func: 被装饰的函数(支持直接装饰和带参数装饰两种方式)
        re_raise: 是否重新抛出异常，默认True
        default_return: 发生异常时的默认返回值，None时返回错误信息字符串
        allowed_exceptions: 允许捕获的异常类型元组，默认捕获所有异常
        log_traceback: 是否记录完整堆栈信息，默认True
        custom_message: 自定义错误提示信息，默认None

    Returns:
        装饰后的函数，保持原函数签名和功能

    Example:
        >>> # 基本使用，捕获所有异常并返回None
        >>> @exc_wraps
        ... def divide(a, b):
        ...     return a / b

        >>> # 只捕获特定异常，其他异常会重新抛出
        >>> @exc_wraps(allowed_exceptions=(ZeroDivisionError,), re_raise=False, default_return=0)
        ... def safe_divide(a, b):
        ...     return a / b

        >>> # 自定义错误消息
        >>> @exc_wraps(custom_message='除法运算失败', re_raise=False)
        ... def custom_divide(a, b):
        ...     return a / b

        >>> # 异步函数支持
        >>> @exc_wraps
        ... async def async_divide(a, b):
        ...     return a / b
    """

    def decorator(f: Callable[..., R]) -> Callable[..., R | None]:
        """装饰器内部函数"""
        if asyncio.iscoroutinefunction(f):
            wrapper = _create_async_wrapper(
                f,
                re_raise,
                default_return,
                allowed_exceptions,
                log_traceback,
                custom_message,
            )
        else:
            wrapper = _create_sync_wrapper(
                f,
                re_raise,
                default_return,
                allowed_exceptions,
                log_traceback,
                custom_message,
            )

        # 保留原始函数的__annotations__属性
        wrapper.__annotations__ = f.__annotations__
        return cast(Callable[..., R | None], wrapper)

    # 支持两种调用方式:@exc_wraps 或 @exc_wraps()
    if func is None:
        return decorator
    return decorator(func)
