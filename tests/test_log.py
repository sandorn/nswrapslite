# !/usr/bin/env python3
"""
日志工具模块测试
"""

import asyncio
import os
import sys
from unittest.mock import patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nswrapslite.log import log_wraps


def test_log_wraps_sync_function():
    """测试log_wraps装饰同步函数"""
    with patch('nswrapslite.log.mylog') as mock_mylog:

        @log_wraps
        def sample_function(x: int, y: int) -> int:
            return x + y

        # 调用被装饰的函数
        result = sample_function(3, 5)

        # 验证结果正确
        assert result == 8

        # 验证日志记录被调用
        assert mock_mylog.info.called or mock_mylog.debug.called


@pytest.mark.asyncio
async def test_log_wraps_async_function():
    """测试log_wraps装饰异步函数"""
    with patch('nswrapslite.log.mylog') as mock_mylog:

        @log_wraps
        async def sample_function(x: int, y: int) -> int:
            await asyncio.sleep(0.01)
            return x + y

        # 调用被装饰的函数
        result = await sample_function(3, 5)

        # 验证结果正确
        assert result == 8

        # 验证日志记录被调用
        assert mock_mylog.info.called or mock_mylog.debug.called


def test_log_wraps_with_exception():
    """测试log_wraps处理异常情况"""
    with patch('nswrapslite.log.mylog') as mock_mylog:

        @log_wraps
        def error_function():
            raise ValueError('测试异常')

        # 验证异常被正确传播
        with pytest.raises(ValueError, match='测试异常'):
            error_function()

        # 验证错误日志被记录
        assert mock_mylog.error.called or mock_mylog.critical.called


@pytest.mark.asyncio
async def test_log_wraps_async_with_exception():
    """测试log_wraps处理异步函数异常"""
    with patch('nswrapslite.log.mylog') as mock_mylog:

        @log_wraps
        async def error_function():
            await asyncio.sleep(0.01)
            raise ValueError('测试异步异常')

        # 验证异常被正确传播
        with pytest.raises(ValueError, match='测试异步异常'):
            await error_function()

        # 验证错误日志被记录
        assert mock_mylog.error.called or mock_mylog.critical.called
