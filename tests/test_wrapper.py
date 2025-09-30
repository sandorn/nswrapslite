# !/usr/bin/env python3
"""
通用装饰器模块测试
"""

import asyncio
import os
import sys
from unittest.mock import patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nswrapslite.wrapper import (
    decorator_factory,
    exc_wrapper,
    log_wrapper,
    timer_wrapper,
)


def test_decorator_factory_sync_function():
    """测试decorator_factory创建同步装饰器"""

    # 创建一个简单的装饰器工厂
    def simple_decorator_factory(prefix=''):
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return f'{prefix}{result}'

            return wrapper

        return decorator

    # 使用decorator_factory包装
    smart_decorator = decorator_factory(simple_decorator_factory)

    # 测试无参调用
    @smart_decorator
    def greet(name):
        return f'Hello, {name}!'

    # 测试有参调用
    @smart_decorator(prefix='[INFO] ')
    def greet_with_prefix(name):
        return f'Hello, {name}!'

    # 验证结果
    assert greet('World') == 'Hello, World!'
    assert greet_with_prefix('World') == '[INFO] Hello, World!'


@pytest.mark.asyncio
async def test_decorator_factory_async_function():
    """测试decorator_factory创建异步装饰器"""

    # 创建一个简单的异步装饰器工厂
    def async_decorator_factory(suffix=''):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                return f'{result}{suffix}'

            return wrapper

        return decorator

    # 使用decorator_factory包装
    smart_decorator = decorator_factory(async_decorator_factory)

    # 测试异步函数装饰
    @smart_decorator(suffix='!')
    async def async_greet(name):
        await asyncio.sleep(0.01)
        return f'Hello, {name}'

    # 验证结果
    result = await async_greet('World')
    assert result == 'Hello, World!'


def test_exc_wrapper():
    """测试exc_wrapper装饰器"""
    with patch('nswrapslite.wrapper.handle_exception') as mock_handle_exception:
        # 配置mock返回值
        mock_handle_exception.return_value = '处理后的结果'

        @exc_wrapper
        def function_with_exception():
            raise ValueError('测试异常')

        # 调用函数，应该返回处理后的结果
        result = function_with_exception()
        assert result == '处理后的结果'

        # 验证handle_exception被调用
        mock_handle_exception.assert_called_once()


@pytest.mark.asyncio
async def test_exc_wrapper_async():
    """测试exc_wrapper装饰异步函数"""
    with patch('nswrapslite.wrapper.handle_exception') as mock_handle_exception:
        # 配置mock返回值
        mock_handle_exception.return_value = '处理后的异步结果'

        @exc_wrapper
        async def async_function_with_exception():
            await asyncio.sleep(0.01)
            raise ValueError('测试异步异常')

        # 调用函数，应该返回处理后的结果
        result = await async_function_with_exception()
        assert result == '处理后的异步结果'

        # 验证handle_exception被调用
        mock_handle_exception.assert_called_once()


def test_log_wrapper():
    """测试log_wrapper装饰器"""
    with patch('nswrapslite.wrapper.log_wraps') as mock_log_wraps:
        # 配置mock返回原始函数
        def mock_decorator(func):
            return func

        mock_log_wraps.return_value = mock_decorator

        @log_wrapper
        def sample_function():
            return '成功'

        # 调用函数，应该返回原始结果
        result = sample_function()
        assert result == '成功'

        # 验证log_wraps被调用
        mock_log_wraps.assert_called_once()


@pytest.mark.asyncio
async def test_log_wrapper_async():
    """测试log_wrapper装饰异步函数"""
    with patch('nswrapslite.wrapper.log_wraps') as mock_log_wraps:
        # 配置mock返回原始函数
        def mock_decorator(func):
            return func

        mock_log_wraps.return_value = mock_decorator

        @log_wrapper
        async def async_sample_function():
            await asyncio.sleep(0.01)
            return '成功'

        # 调用函数，应该返回原始结果
        result = await async_sample_function()
        assert result == '成功'

        # 验证log_wraps被调用
        mock_log_wraps.assert_called_once()


def test_timer_wrapper():
    """测试timer_wrapper装饰器"""
    with patch('nswrapslite.wrapper.timer_wraps') as mock_timer_wraps:
        # 配置mock返回原始函数
        def mock_decorator(func):
            return func

        mock_timer_wraps.return_value = mock_decorator

        @timer_wrapper
        def sample_function():
            return '成功'

        # 调用函数，应该返回原始结果
        result = sample_function()
        assert result == '成功'

        # 验证timer_wraps被调用
        mock_timer_wraps.assert_called_once()


@pytest.mark.asyncio
async def test_timer_wrapper_async():
    """测试timer_wrapper装饰异步函数"""
    with patch('nswrapslite.wrapper.timer_wraps') as mock_timer_wraps:
        # 配置mock返回原始函数
        def mock_decorator(func):
            return func

        mock_timer_wraps.return_value = mock_decorator

        @timer_wrapper
        async def async_sample_function():
            await asyncio.sleep(0.01)
            return '成功'

        # 调用函数，应该返回原始结果
        result = await async_sample_function()
        assert result == '成功'

        # 验证timer_wraps被调用
        mock_timer_wraps.assert_called_once()
