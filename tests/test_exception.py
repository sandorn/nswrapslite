# !/usr/bin/env python3
"""
异常处理模块测试
"""

import os
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nswrapslite.exception import handle_exception


def test_handle_exception_re_raise_true():
    """测试handle_exception函数在re_raise=True时的行为"""
    with pytest.raises(ValueError, match='测试异常'):
        handle_exception(ValueError('测试异常'), re_raise=True)


def test_handle_exception_re_raise_false():
    """测试handle_exception函数在re_raise=False时的行为"""
    result = handle_exception(ValueError('测试异常'), re_raise=False)
    assert result is None


def test_handle_exception_with_default_return():
    """测试handle_exception函数在设置默认返回值时的行为"""
    result = handle_exception(ValueError('测试异常'), re_raise=False, default_return=42)
    assert result == 42


def test_handle_exception_with_callfrom():
    """测试handle_exception函数在提供callfrom参数时的行为"""

    def sample_func(x: int) -> int:
        return x * 2

    result = handle_exception(ValueError('测试异常'), re_raise=False, callfrom=sample_func)
    assert result is None


def test_handle_exception_with_custom_message():
    """测试handle_exception函数在提供自定义消息时的行为"""
    result = handle_exception(ValueError('测试异常'), re_raise=False, custom_message='自定义错误消息')
    assert result is None


def test_handle_exception_log_traceback_false():
    """测试handle_exception函数在禁用堆栈跟踪记录时的行为"""
    result = handle_exception(ValueError('测试异常'), re_raise=False, log_traceback=False)
    assert result is None


def test_handle_exception_different_exceptions():
    """测试handle_exception函数处理不同类型的异常"""
    # 测试TypeError
    result = handle_exception(TypeError('类型错误'), re_raise=False, default_return='类型错误处理')
    assert result == '类型错误处理'

    # 测试KeyError
    result = handle_exception(KeyError('键错误'), re_raise=False, default_return='键错误处理')
    assert result == '键错误处理'

    # 测试ZeroDivisionError
    result = handle_exception(ZeroDivisionError('除零错误'), re_raise=False, default_return='除零错误处理')
    assert result == '除零错误处理'
