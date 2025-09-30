# !/usr/bin/env python3
"""
重试机制模块测试
"""

import asyncio
import os
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nswrapslite.retry import retry_wraps


def test_retry_wraps_sync_function():
    """测试retry_wraps装饰同步函数"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @retry_wraps(max_retries=3, exceptions=(ValueError,))
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:  # 前两次调用失败，第三次成功
            raise ValueError('模拟临时错误')
        return '成功'

    # 调用函数，应该在第三次尝试时成功
    result = flaky_function()
    assert result == '成功'
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_wraps_async_function():
    """测试retry_wraps装饰异步函数"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @retry_wraps(max_retries=3, exceptions=(ValueError,))
    async def async_flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:  # 前两次调用失败，第三次成功
            await asyncio.sleep(0.01)  # 模拟异步操作
            raise ValueError('模拟临时错误')
        return '成功'

    # 调用函数，应该在第三次尝试时成功
    result = await async_flaky_function()
    assert result == '成功'
    assert call_count == 3


def test_retry_wraps_max_retries_exceeded():
    """测试retry_wraps在超过最大重试次数时的行为"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @retry_wraps(max_retries=2, exceptions=(ValueError,))
    def always_failing_function():
        nonlocal call_count
        call_count += 1
        raise ValueError('总是失败')

    # 调用函数，应该在重试2次后抛出异常
    with pytest.raises(ValueError, match='总是失败'):
        always_failing_function()

    assert call_count == 3  # 1次原始调用 + 2次重试


def test_retry_wraps_with_custom_delay():
    """测试retry_wraps使用自定义延迟策略"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0
    delays = []
    start_time = None

    def custom_delay(retry_count):
        """自定义延迟函数：指数退避"""
        return 0.01 * (2**retry_count)

    @retry_wraps(max_retries=3, exceptions=(ValueError,), delay=custom_delay)
    def flaky_function():
        nonlocal call_count, start_time
        if start_time is None:
            start_time = asyncio.get_event_loop().time()
        else:
            # 记录实际延迟时间
            current_time = asyncio.get_event_loop().time()
            delays.append(current_time - start_time)
            start_time = current_time

        call_count += 1
        if call_count < 4:  # 前三次调用失败，第四次成功
            raise ValueError('模拟临时错误')
        return '成功'

    # 调用函数
    result = flaky_function()
    assert result == '成功'
    assert call_count == 4

    # 验证延迟时间大致符合预期（考虑到执行时间）
    for i, actual_delay in enumerate(delays):
        expected_delay = custom_delay(i + 1)
        # 允许一定的误差范围
        assert abs(actual_delay - expected_delay) < 0.02


def test_retry_wraps_without_retryable_exception():
    """测试retry_wraps对于非重试异常的处理"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0

    @retry_wraps(max_retries=3, exceptions=(ValueError,))
    def function_with_non_retryable_exception():
        nonlocal call_count
        call_count += 1
        raise TypeError('这是一个非重试异常')

    # 调用函数，应该立即抛出异常，不进行重试
    with pytest.raises(TypeError, match='这是一个非重试异常'):
        function_with_non_retryable_exception()

    assert call_count == 1  # 只调用了一次


def test_retry_wraps_with_retry_callback():
    """测试retry_wraps使用重试回调函数"""
    # 计数器，用于验证函数被调用的次数
    call_count = 0
    retry_details = []

    def retry_callback(retry_count, exception, delay):
        """记录重试详情"""
        retry_details.append({'retry_count': retry_count, 'exception': str(exception), 'delay': delay})

    @retry_wraps(
        max_retries=2,
        exceptions=(ValueError,),
        delay=0.01,
        retry_callback=retry_callback,
    )
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:  # 前两次调用失败，第三次成功
            raise ValueError(f'第{call_count}次失败')
        return '成功'

    # 调用函数
    result = flaky_function()
    assert result == '成功'
    assert call_count == 3

    # 验证回调函数被调用
    assert len(retry_details) == 2
    assert retry_details[0]['retry_count'] == 1
    assert '第1次失败' in retry_details[0]['exception']
    assert retry_details[1]['retry_count'] == 2
    assert '第2次失败' in retry_details[1]['exception']
