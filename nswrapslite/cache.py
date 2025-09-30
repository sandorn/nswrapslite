#!/usr/bin/env python3
"""
==============================================================
Description  : 缓存装饰器模块 - 基于lru_cache的通用缓存装饰器
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-09-06 12:54:07
LastEditTime : 2025-09-14 13:37:42
Github       : https://github.com/sandorn/nswraps

本模块提供基于functools.lru_cache的通用缓存装饰器，支持同步函数的缓存功能。
==============================================================
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache, wraps
from typing import ParamSpec, TypeVar

T = TypeVar('T')
P = ParamSpec('P')


def cache_wrapper(
    maxsize: int = 128,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cached_func: Callable[..., T] = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return cached_func(*args, **kwargs)
            except TypeError as e:
                if 'unhashable' in str(e):
                    # 遇到不可哈希参数，直接调用原函数（不缓存）
                    return func(*args, **kwargs)
                raise  # 重新抛出其他 TypeError

        return wrapper

    return decorator
