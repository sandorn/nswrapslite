# !/usr/bin/env python3
"""
测试配置文件，提供测试环境的通用配置和工具函数
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging

import pytest

# 配置测试日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 禁用第三方库的日志
for name in logging.root.manager.loggerDict:
    if name.startswith('urllib3') or name.startswith('requests'):
        logging.getLogger(name).setLevel(logging.WARNING)


@pytest.fixture(scope='session')
def event_loop():
    """创建一个会话范围的事件循环，用于异步测试"""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def sample_sync_function():
    """提供一个简单的同步函数用于测试"""

    def func(x: int, y: int) -> int:
        return x + y

    return func


@pytest.fixture
def sample_async_function():
    """提供一个简单的异步函数用于测试"""
    import asyncio

    async def func(x: int, y: int) -> int:
        await asyncio.sleep(0.01)  # 模拟异步操作
        return x + y

    return func


@pytest.fixture
def error_sync_function():
    """提供一个会抛出异常的同步函数用于测试"""

    def func():
        raise ValueError('测试异常')

    return func


@pytest.fixture
def error_async_function():
    """提供一个会抛出异常的异步函数用于测试"""
    import asyncio

    async def func():
        await asyncio.sleep(0.01)  # 模拟异步操作
        raise ValueError('测试异步异常')

    return func
