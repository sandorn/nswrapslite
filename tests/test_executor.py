# !/usr/bin/env python3
"""
执行器模块测试
"""

import asyncio
import os
import sys
from concurrent.futures import Future as ThreadFuture

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nswrapslite.executor import executor_wraps, future_wraps, run_executor_wraps


@pytest.mark.asyncio
async def test_executor_wraps_sync_function():
    """测试executor_wraps装饰同步函数"""

    @executor_wraps
    def sync_function(x: int, y: int) -> int:
        # 模拟耗时操作
        import time

        time.sleep(0.1)
        return x + y

    # 测试异步调用
    result = await sync_function(5, 3)
    assert result == 8


@pytest.mark.asyncio
async def test_executor_wraps_async_function():
    """测试executor_wraps装饰异步函数(应保持不变)"""

    @executor_wraps
    async def async_function(x: int, y: int) -> int:
        await asyncio.sleep(0.1)  # 模拟异步操作
        return x + y

    # 测试异步调用
    result = await async_function(5, 3)
    assert result == 8


@pytest.mark.asyncio
async def test_executor_wraps_with_executor():
    """测试executor_wraps使用自定义执行器"""
    from concurrent.futures import ThreadPoolExecutor

    custom_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='TestExecutor')

    @executor_wraps(executor=custom_executor)
    def sync_function(x: int, y: int) -> int:
        import time

        time.sleep(0.1)
        return x + y

    result = await sync_function(5, 3)
    assert result == 8

    # 清理资源
    custom_executor.shutdown()


@pytest.mark.asyncio
async def test_run_executor_wraps():
    """测试run_executor_wraps装饰器"""

    @run_executor_wraps
    async def async_function(x: int, y: int) -> int:
        await asyncio.sleep(0.1)
        return x + y

    # 测试同步调用异步函数
    result = async_function(5, 3)
    assert result == 8


@pytest.mark.asyncio
async def test_future_wraps():
    """测试future_wraps装饰器"""

    @future_wraps
    def sync_function(x: int, y: int) -> int:
        import time

        time.sleep(0.1)
        return x + y

    # 获取Future对象
    future = sync_function(5, 3)
    assert isinstance(future, ThreadFuture)

    # 等待Future完成并获取结果
    result = future.result()
    assert result == 8


@pytest.mark.asyncio
async def test_executor_wraps_exception_handling():
    """测试executor_wraps的异常处理"""

    @executor_wraps
    def error_function() -> None:
        raise ValueError('测试异常')

    # 测试异常是否正确传播
    with pytest.raises(ValueError, match='测试异常'):
        await error_function()


@pytest.mark.asyncio
async def test_run_executor_wraps_exception_handling():
    """测试run_executor_wraps的异常处理"""

    @run_executor_wraps
    async def error_function() -> None:
        await asyncio.sleep(0.01)
        raise ValueError('测试异常')

    # 测试异常是否正确传播
    with pytest.raises(ValueError, match='测试异常'):
        error_function()
