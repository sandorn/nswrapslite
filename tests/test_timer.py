# !/usr/bin/env python3
"""
计时工具模块测试
"""

import asyncio
import os
import sys
from unittest.mock import patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nswrapslite.timer import timer, timer_wraps


def test_timer_wraps_sync_function():
    """测试timer_wraps装饰同步函数"""
    with patch('nswrapslite.timer.mylog') as mock_mylog:

        @timer_wraps
        def sample_function(x: int, y: int) -> int:
            # 模拟一些操作
            result = 0
            for i in range(1000):
                result += i
            return x + y

        # 调用被装饰的函数
        result = sample_function(3, 5)

        # 验证结果正确
        assert result == 8

        # 验证日志记录被调用（记录了执行时间）
        assert mock_mylog.info.called or mock_mylog.debug.called


@pytest.mark.asyncio
async def test_timer_wraps_async_function():
    """测试timer_wraps装饰异步函数"""
    with patch('nswrapslite.timer.mylog') as mock_mylog:

        @timer_wraps
        async def sample_function(x: int, y: int) -> int:
            await asyncio.sleep(0.01)  # 模拟异步操作
            return x + y

        # 调用被装饰的函数
        result = await sample_function(3, 5)

        # 验证结果正确
        assert result == 8

        # 验证日志记录被调用（记录了执行时间）
        assert mock_mylog.info.called or mock_mylog.debug.called


def test_timer_alias():
    """测试timer别名"""
    # 验证timer是timer_wraps的别名
    assert timer is timer_wraps


def test_timer_wraps_with_exception():
    """测试timer_wraps处理异常情况"""
    with patch('nswrapslite.timer.mylog') as mock_mylog:

        @timer_wraps
        def error_function():
            raise ValueError('测试异常')

        # 验证异常被正确传播
        with pytest.raises(ValueError, match='测试异常'):
            error_function()

        # 验证日志记录被调用（应该记录了执行时间和异常）
        assert mock_mylog.info.called or mock_mylog.debug.called or mock_mylog.error.called


@pytest.mark.asyncio
async def test_timer_wraps_async_with_exception():
    """测试timer_wraps处理异步函数异常"""
    with patch('nswrapslite.timer.mylog') as mock_mylog:

        @timer_wraps
        async def error_function():
            await asyncio.sleep(0.01)
            raise ValueError('测试异步异常')

        # 验证异常被正确传播
        with pytest.raises(ValueError, match='测试异步异常'):
            await error_function()

        # 验证日志记录被调用（应该记录了执行时间和异常）
        assert mock_mylog.info.called or mock_mylog.debug.called or mock_mylog.error.called


def test_timer_wraps_performance_comparison():
    """测试timer_wraps对函数性能的影响（应该很小）"""
    import time

    # 原始函数
    def original_function():
        result = 0
        for i in range(100000):
            result += i
        return result

    # 装饰后的函数
    @timer_wraps
    def decorated_function():
        result = 0
        for i in range(100000):
            result += i
        return result

    # 测量原始函数执行时间
    start_time = time.perf_counter()
    original_result = original_function()
    original_time = time.perf_counter() - start_time

    # 测量装饰后函数执行时间
    start_time = time.perf_counter()
    decorated_result = decorated_function()
    decorated_time = time.perf_counter() - start_time

    # 验证结果相同
    assert original_result == decorated_result

    # 验证性能影响很小（装饰后的函数不应比原始函数慢10%以上）
    overhead_ratio = (decorated_time - original_time) / original_time
    assert overhead_ratio < 0.1  # 允许最多10%的性能损失
