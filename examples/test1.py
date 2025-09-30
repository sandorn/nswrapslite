# !/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
import sys
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, Dict, List, Optional, TypeVar, Union

from xtlog import mylog

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nswrapslite.exception import handle_exception
from nswrapslite.log import log_wraps as log_wraps_decorator

T = TypeVar('T')


def _create_sync_wrapper(func: Callable[..., Any], log_args: bool, log_result: bool, re_raise: bool, default_return: Any, log_traceback: bool, custom_message: str | None) -> Callable[..., Any]:
    """创建同步函数包装器"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if log_args:
            mylog.debug(' Args: {} | Kwargs: {}', args, kwargs, callfrom=func)

        try:
            result: Any = func(*args, **kwargs)
            if log_result:
                mylog.success(' Result: {} = {}', type(result).__name__, result, callfrom=func)
            return result
        except Exception as err:
            return handle_exception(
                    errinfo=err,
                    callfrom=func,
                    default_return=default_return,
                    re_raise=re_raise,
                    log_traceback=log_traceback,
                    custom_message=custom_message,
            )

    return wrapper


def _create_async_wrapper(func: Callable[..., Any], log_args: bool, log_result: bool, re_raise: bool, default_return: Any, log_traceback: bool, custom_message: str | None) -> Callable[..., Any]:
    """创建异步函数包装器"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if log_args:
            mylog.debug(' Args: {} | Kwargs: {}', args, kwargs, callfrom=func)

        try:
            result: Any = await func(*args, **kwargs)
            if log_result:
                mylog.success(' Result: {} = {}', type(result).__name__, result, callfrom=func)
            return result
        except Exception as err:
            return handle_exception(
                    errinfo=err,
                    callfrom=func,
                    default_return=default_return,
                    re_raise=re_raise,
                    log_traceback=log_traceback,
                    custom_message=custom_message,
            )

    return wrapper


def log_wraps[T](
    func: Callable[..., T] | None = None,
    *,
    re_raise: bool = False,
    default_return: Any = None,
    log_args: bool = True,
    log_result: bool = True,
    log_traceback: bool = True,
    custom_message: str | None = None,
) -> Callable[..., Any]:
    """
    简化版日志装饰器 - 利用callfrom参数传递调用者信息

    这个装饰器可以为函数自动添加日志记录功能，包括：
    - 记录函数调用时的参数
    - 记录函数的返回值
    - 自动处理同步和异步函数
    - 支持异常处理和重新抛出

    Args:
        func: 被装饰的函数（装饰器语法糖参数）
        log_args: 是否记录函数参数，默认为True
        log_result: 是否记录函数返回值，默认为True
        log_traceback: 是否记录完整堆栈信息，默认为True
        re_raise: 是否重新抛出异常，默认为True
        default_return: 异常时的默认返回值，默认为None
        custom_message: 自定义日志消息，默认None

    Returns:
        Callable: 装饰后的函数

    Example:
        >>> @log_wraps
        >>> def my_function(x, y):
        >>>     return x + y

        >>> @log_wraps(log_args=True, log_result=False)
        >>> async def async_function(data):
        >>>     return await process_data(data)
    """

    def decorator(func_inner: Callable[..., Any]) -> Callable[..., Any]:
        """实际的装饰器实现"""
        if asyncio.iscoroutinefunction(func_inner):
            return _create_async_wrapper(func_inner, log_args, log_result, re_raise, default_return, log_traceback, custom_message)
        return _create_sync_wrapper(func_inner, log_args, log_result, re_raise, default_return, log_traceback, custom_message)

    return decorator(func) if func else decorator


if __name__ == "__main__":

    @log_wraps
    def add_numbers(a: int, b: int) -> int:
        """示例同步函数，使用默认的log_wraps配置"""
        return a + b
    
    @log_wraps_decorator
    async def async_add_numbers(a: int, b: int) -> int:
        """示例异步函数，使用默认的log_wraps配置"""
        return a + b

    def log_wraps_sync_example() -> None:
        """log_wraps装饰器同步函数示例"""
        print('\n=== log_wraps装饰器同步函数示例 ===')

        # 基本使用示例
        result = add_numbers(5, 3)
        print(f'函数返回结果: {result}')

    async def main() -> None:
        """主函数"""
        # log_wraps同步函数示例
        log_wraps_sync_example()
        # log_wraps异步函数示例
        result = await async_add_numbers(5, 3)
        print(f'异步函数返回结果: {result}')

    mylog.set_level(30)  # DEBUG级别

    # 运行主函数
    asyncio.run(main())