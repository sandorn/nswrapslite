# !/usr/bin/env python3
"""
缓存工具模块测试
"""

import asyncio
import os
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nswrapslite.cache import cache_wrapper


def test_cache_wrapper_sync_function():
    """测试cache_wrapper装饰同步函数"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @cache_wrapper()
    def expensive_function(x: int, y: int) -> int:
        nonlocal call_count
        call_count += 1
        # 模拟耗时操作
        import time

        time.sleep(0.01)
        return x + y

    # 第一次调用，应该执行函数
    result1 = expensive_function(3, 5)
    assert result1 == 8
    assert call_count == 1

    # 第二次调用相同参数，应该使用缓存结果
    result2 = expensive_function(3, 5)
    assert result2 == 8
    assert call_count == 1  # 调用次数没有增加

    # 使用不同参数调用，应该执行函数
    result3 = expensive_function(4, 6)
    assert result3 == 10
    assert call_count == 2


@pytest.mark.asyncio
async def test_cache_wrapper_async_function():
    """测试cache_wrapper装饰异步函数"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @cache_wrapper()
    async def async_expensive_function(x: int, y: int) -> int:
        nonlocal call_count
        call_count += 1
        # 模拟异步耗时操作
        await asyncio.sleep(0.01)
        return x + y

    # 第一次调用，应该执行函数
    result1 = await async_expensive_function(3, 5)
    assert result1 == 8
    assert call_count == 1

    # 第二次调用相同参数，应该使用缓存结果
    result2 = await async_expensive_function(3, 5)
    assert result2 == 8
    assert call_count == 1  # 调用次数没有增加


def test_cache_wrapper_with_max_size():
    """测试cache_wrapper设置最大缓存大小"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @cache_wrapper(max_size=2)  # 只缓存最近2个结果
    def function_with_limited_cache(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # 调用三个不同的参数
    function_with_limited_cache(1)  # 缓存: {1: 2}
    function_with_limited_cache(2)  # 缓存: {1: 2, 2: 4}
    function_with_limited_cache(3)  # 缓存: {2: 4, 3: 6} (1的缓存被淘汰)

    # 再次调用第一个参数，应该重新执行函数
    function_with_limited_cache(1)

    # 总调用次数应该是4次（包括被淘汰后重新调用的1次）
    assert call_count == 4


def test_cache_wrapper_with_ttl():
    """测试cache_wrapper设置缓存过期时间"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @cache_wrapper(ttl=0.1)  # 缓存100毫秒后过期
    def function_with_ttl(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # 第一次调用
    function_with_ttl(1)
    assert call_count == 1

    # 立即再次调用，应该使用缓存
    function_with_ttl(1)
    assert call_count == 1

    # 等待缓存过期
    import time

    time.sleep(0.11)

    # 再次调用，应该重新执行函数
    function_with_ttl(1)
    assert call_count == 2


def test_cache_wrapper_with_clear_cache():
    """测试手动清除缓存功能"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @cache_wrapper()
    def function_with_cache(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # 调用函数
    function_with_cache(1)
    assert call_count == 1

    # 再次调用，应该使用缓存
    function_with_cache(1)
    assert call_count == 1

    # 清除缓存
    function_with_cache.clear_cache()

    # 再次调用，应该重新执行函数
    function_with_cache(1)
    assert call_count == 2


def test_cache_wrapper_with_different_param_types():
    """测试cache_wrapper处理不同类型的参数"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @cache_wrapper()
    def function_with_different_params(x, y, z=None):
        nonlocal call_count
        call_count += 1
        return f'{x}-{y}-{z}'

    # 测试不同类型的参数
    function_with_different_params(1, 'test')
    assert call_count == 1

    function_with_different_params(1, 'test')  # 相同参数，应该使用缓存
    assert call_count == 1

    function_with_different_params(1, 'test', z=42)  # 不同参数，应该执行函数
    assert call_count == 2
