#!/usr/bin/env python3
"""
==============================================================
Description  : 缓存装饰器模块 - 提供函数结果缓存功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-01 15:45:00
Github       : https://github.com/sandorn/nswrapslite

本模块提供以下核心功能：
- cache_wrapper：函数结果缓存装饰器，基于functools.lru_cache
- clear_cache：清除指定函数的缓存
- CacheManager：缓存管理器类，管理多个函数的缓存

主要特性：
- 基于Python内置的lru_cache实现高效缓存
- 支持配置缓存大小和过期时间
- 支持清除特定函数或所有函数的缓存
- 同时支持同步和异步函数
- 保留原始函数的元数据
- 完整的类型注解支持
==============================================================
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache, wraps
from typing import Any


def cache_wrapper(
    maxsize: int = 128,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cached_func: Callable[..., Any] = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return cached_func(*args, **kwargs)
            except TypeError as e:
                if 'unhashable' in str(e):
                    # 遇到不可哈希参数，直接调用原函数（不缓存）
                    return func(*args, **kwargs)
                raise  # 重新抛出其他 TypeError

        return wrapper

    return decorator


__all__ = ['cache_wrapper']