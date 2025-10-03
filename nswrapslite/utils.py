# !/usr/bin/env python3
"""
==============================================================
Description  : 核心工具函数模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-09-28 16:41:00
Github       : https://github.com/sandorn/nswrapslite

提供核心工具函数，支持装饰器实现。
==============================================================
"""

from __future__ import annotations

import contextlib
import inspect
from collections.abc import Callable

# 使用现代类型注解
from typing import Any


def _get_function_location(func: Callable[..., Any]) -> str:
    """
    获取函数的位置信息(文件、行号、函数名)

    Args:
        func: 要获取位置信息的函数

    Returns:
        str: 格式为 "文件路径:行号@函数名 | " 的字符串，用于日志记录
    """
    # 基础检查
    if not callable(func):
        return 'unknown:0@unknown | '

    # 获取原始函数(处理装饰器情况)
    original_func: Callable[..., Any] = func
    with contextlib.suppress(Exception):
        original_func = inspect.unwrap(func)

    # 尝试使用__code__属性获取位置信息(最可靠的方法)
    if hasattr(original_func, '__code__'):
        code = original_func.__code__
        func_name = getattr(original_func, '__name__', 'unknown')
        return f'{code.co_filename}:{code.co_firstlineno}@{func_name} |'

    # 回退方案：使用inspect.getfile
    try:
        file_path = inspect.getfile(original_func)
        _source_lines, line_no = inspect.getsourcelines(original_func)
        func_name = getattr(original_func, '__name__', 'unknown')
        return f'{file_path}:{line_no}@{func_name} |'
    except Exception:
        # 最后的回退方案
        module_name = getattr(original_func, '__module__', 'unknown') or 'unknown'
        func_name = getattr(original_func, '__name__', 'unknown') or 'unknown'
        return f'{module_name}:0@{func_name} |'


def _is_async_function(func: Callable) -> bool:
    """检查函数是否为异步函数

    Args:
        func: 要检查的函数

    Returns:
        bool: 如果是异步函数返回True，否则返回False
    """
    return inspect.iscoroutinefunction(func)


def _is_sync_function(func: Callable) -> bool:
    """检查函数是否为同步函数

    Args:
        func: 要检查的函数

    Returns:
        bool: 如果是同步函数返回True，否则返回False
    """
    return not inspect.iscoroutinefunction(func)


def _get_function_signature(func: Callable) -> str:
    """获取函数的签名信息

    Args:
        func: 要获取签名的函数

    Returns:
        str: 函数的签名字符串
        print(get_function_signature(get_function_signature))
        输出: get_function_signature(func: 'Callable') -> 'str'
    """
    try:
        sig = inspect.signature(func)
        return f'{func.__name__}{sig}'
    except (ValueError, TypeError):
        return f'{func.__name__}()'


__all__ = [
    '_get_function_location',
    '_is_async_function',
    '_is_sync_function',
    '_get_function_signature',
]