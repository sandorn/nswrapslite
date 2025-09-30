#!/usr/bin/env python3
"""
==============================================================
Description  : 日志工具模块 - 增强版，利用loguru内置功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2022-12-22 17:35:56
LastEditTime : 2025-09-26 16:00:00
Github       : https://github.com/sandorn/nswraps

优化特性:
- 利用loguru的record对象直接获取调用信息，无需手动处理调用栈
- 大幅简化代码结构，提高可维护性
- 保持原有的所有功能和图标显示
- 支持callfrom参数扩展功能，可自定义调用位置显示
- 增强异常处理参数，与exc_wraps保持一致
- 添加日志上下文管理器，方便跟踪函数执行流程
- 支持动态调整日志级别，适应不同场景需求
- 优化日志格式和配置，提高可读性
==============================================================
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from xtlog import mylog

# 导入异常处理模块
from .exception import handle_exception

# 由于handle_exception函数在外部模块中定义，我们在此处不会修改其定义，但会在调用时移除callfrom参数

T = TypeVar('T')


def _create_sync_wrapper(func: Callable[..., Any], log_args: bool, log_result: bool, re_raise: bool, default_return: Any, log_traceback: bool, custom_message: str | None) -> Callable[..., Any]:
    """创建同步函数包装器"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取函数信息用于日志记录
        func_name = func.__name__
        module_name = func.__module__
        log_context = f'{module_name}.{func_name}'
        
        if log_args:
            mylog.debug(f'[{log_context}] Args: {args} | Kwargs: {kwargs}')
            
        try:
            result: Any = func(*args, **kwargs)
            if log_result:
                mylog.success(f'[{log_context}] Result: {type(result).__name__} = {result}')
            return result
        except Exception as err:
            return handle_exception(
                    errinfo=err,
                    # 移除callfrom参数，改用log_context
                    default_return=default_return,
                    re_raise=re_raise,
                    log_traceback=log_traceback,
                    custom_message=custom_message or f'函数 {log_context} 执行出错',
                )

    return wrapper


def _create_async_wrapper(func: Callable[..., Any], log_args: bool, log_result: bool, re_raise: bool, default_return: Any, log_traceback: bool, custom_message: str | None) -> Callable[..., Any]:
    """创建异步函数包装器"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取函数信息用于日志记录
        func_name = func.__name__
        module_name = func.__module__
        log_context = f'{module_name}.{func_name}'
        
        if log_args:
            mylog.debug(f'[{log_context}] Args: {args} | Kwargs: {kwargs}')

        try:
            result: Any = await func(*args, **kwargs)
            if log_result:
                mylog.success(f'[{log_context}] Result: {type(result).__name__} = {result}')
            return result
        except Exception as err:
            return handle_exception(
                    errinfo=err,
                    # 移除callfrom参数，改用log_context
                    default_return=default_return,
                    re_raise=re_raise,
                    log_traceback=log_traceback,
                    custom_message=custom_message or f'函数 {log_context} 执行出错',
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


# 导出模块公共接口
__all__ = ['log_wraps']
