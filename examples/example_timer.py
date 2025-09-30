# !/usr/bin/env python3
"""
NSWrapsLite 计时工具模块示例程序

本示例展示了 NSWrapsLite 库中计时工具模块的所有功能用法，包括:
1. timer_wraps 装饰器 (以及其简写形式 timer)
2. TimerWrapt 类 (支持装饰器和上下文管理器两种模式)

每个示例都包含同步和异步函数的计时、异常处理、自定义消息等场景。
"""

import asyncio
import os
import sys
import time
from typing import Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nswrapslite.timer import TimerWrapt, timer, timer_wraps

# ======================================================
# 示例 1: 使用 timer_wraps 装饰器
# ======================================================


# 方式1: 直接装饰同步函数
@timer_wraps
def calculate_sum(a: int, b: int) -> int:
    """计算两个整数的和（演示同步函数计时）

    Args:
        a: 第一个整数
        b: 第二个整数

    Returns:
        两个整数的和
    """
    # 模拟耗时操作
    time.sleep(0.2)
    return a + b


# 方式2: 带括号装饰异步函数
@timer_wraps()
async def fetch_data(url: str) -> str:
    """模拟从网络获取数据（演示异步函数计时）

    Args:
        url: 请求的URL

    Returns:
        获取的数据
    """
    # 模拟网络延迟
    await asyncio.sleep(0.3)
    return f'Data from {url}'


# 方式3: 使用简写形式 timer
@timer
def process_list(data: list[int]) -> list[int]:
    """处理整数列表（演示timer简写形式）

    Args:
        data: 待处理的整数列表

    Returns:
        处理后的整数列表
    """
    # 模拟复杂计算
    result = []
    for item in data:
        # 模拟每个元素的处理时间
        time.sleep(0.01)
        result.append(item * 2)
    return result


# ======================================================
# 示例 2: 使用 TimerWrapt 类作为装饰器
# ======================================================


# 方式1: 作为装饰器使用
@TimerWrapt
def complex_operation(param1: int, param2: str) -> str:
    """执行复杂操作（演示TimerWrapt作为装饰器）

    Args:
        param1: 整数参数
        param2: 字符串参数

    Returns:
        操作结果
    """
    # 模拟复杂操作
    time.sleep(0.4)
    return f'Result: {param1} - {param2}'


# 方式2: 作为异步函数的装饰器
@TimerWrapt
async def async_complex_task(delay: float) -> str:
    """执行异步复杂任务（演示TimerWrapt作为异步函数装饰器）

    Args:
        delay: 模拟的延迟时间（秒）

    Returns:
        任务完成信息
    """
    # 模拟异步操作
    await asyncio.sleep(delay)
    return f'Async task completed with delay {delay}s'


# ======================================================
# 示例 3: 使用 TimerWrapt 类作为上下文管理器
# ======================================================
def demonstrate_context_manager():
    """演示TimerWrapt作为上下文管理器的用法"""

    # 方式1: 基本上下文管理器用法
    with TimerWrapt('基本上下文管理器'):
        # 模拟代码块执行
        time.sleep(0.25)
        print('在上下文管理器中执行代码')

    # 方式2: 带描述的上下文管理器
    with TimerWrapt('复杂数据处理'):
        # 模拟复杂数据处理
        total = 0
        for i in range(100000):
            total += i
        print(f'计算结果: {total}')

    # 方式3: 处理异常的上下文管理器
    try:
        with TimerWrapt('异常处理测试'):
            # 模拟代码执行异常
            time.sleep(0.1)
            raise ValueError('测试异常')
    except ValueError as e:
        print(f'捕获到异常: {e}')


# 异步上下文管理器示例
async def demonstrate_async_context_manager():
    """演示TimerWrapt作为异步上下文管理器的用法"""

    # 方式1: 基本异步上下文管理器
    async with TimerWrapt('异步上下文管理器'):
        # 模拟异步代码执行
        await asyncio.sleep(0.3)
        print('在异步上下文管理器中执行代码')

    # 方式2: 带描述的异步上下文管理器
    async with TimerWrapt('异步数据获取'):
        # 模拟异步数据获取
        await asyncio.sleep(0.2)
        print('异步数据获取完成')

    # 方式3: 处理异常的异步上下文管理器
    try:
        async with TimerWrapt('异步异常处理测试'):
            # 模拟异步代码执行异常
            await asyncio.sleep(0.1)
            raise RuntimeError('异步测试异常')
    except RuntimeError as e:
        print(f'捕获到异步异常: {e}')


# ======================================================
# 示例 4: 嵌套计时和装饰器组合使用
# ======================================================


# 装饰器组合使用
@timer_wraps
@TimerWrapt
def combined_decorators(n: int) -> int:
    """演示多个计时装饰器的组合使用

    Args:
        n: 计算次数

    Returns:
        计算结果
    """
    result = 0
    for i in range(n):
        time.sleep(0.001)  # 模拟小的耗时操作
        result += i
    return result


# 嵌套上下文管理器
def nested_context_managers():
    """演示嵌套上下文管理器的用法"""
    with TimerWrapt('外层操作'):
        # 外层操作
        time.sleep(0.1)

        with TimerWrapt('内层操作1'):
            # 内层操作1
            time.sleep(0.05)

        with TimerWrapt('内层操作2'):
            # 内层操作2
            time.sleep(0.08)


# ======================================================
# 示例 5: 性能测试函数
# ======================================================
def performance_test():
    """执行一些简单的性能测试"""
    print('\n执行性能测试...')

    # 测试不同规模的输入
    for size in [10, 100, 1000]:
        data = list(range(size))
        print(f'\n测试列表大小: {size}')
        result = process_list(data)
        print(f'处理结果长度: {len(result)}')


# ======================================================
# 主函数 - 演示所有计时功能
# ======================================================
async def main() -> None:
    """主函数，演示所有计时工具的用法"""
    print('=' * 80)
    print('NSWrapsLite 计时工具模块示例程序')
    print('=' * 80)

    # 1. 演示 timer_wraps 装饰器
    print('\n' + '-' * 80)
    print('1. timer_wraps 装饰器示例')
    print('-' * 80)

    # 测试同步函数
    result = calculate_sum(10, 20)
    print(f'calculate_sum 结果: {result}')

    # 测试异步函数
    data = await fetch_data('https://example.com')
    print(f'fetch_data 结果: {data}')

    # 测试 timer 简写形式
    processed = process_list([1, 2, 3, 4, 5])
    print(f'process_list 结果: {processed}')

    # 2. 演示 TimerWrapt 作为装饰器
    print('\n' + '-' * 80)
    print('2. TimerWrapt 作为装饰器示例')
    print('-' * 80)

    # 测试同步函数装饰器
    op_result = complex_operation(42, 'test')
    print(f'complex_operation 结果: {op_result}')

    # 测试异步函数装饰器
    async_result = await async_complex_task(0.5)
    print(f'async_complex_task 结果: {async_result}')

    # 3. 演示 TimerWrapt 作为上下文管理器
    print('\n' + '-' * 80)
    print('3. TimerWrapt 作为同步上下文管理器示例')
    print('-' * 80)
    demonstrate_context_manager()

    print('\n' + '-' * 80)
    print('4. TimerWrapt 作为异步上下文管理器示例')
    print('-' * 80)
    await demonstrate_async_context_manager()

    # 4. 演示嵌套计时和装饰器组合
    print('\n' + '-' * 80)
    print('5. 嵌套计时和装饰器组合示例')
    print('-' * 80)

    # 测试装饰器组合
    combined_result = combined_decorators(1000)
    print(f'combined_decorators 结果: {combined_result}')

    # 测试嵌套上下文管理器
    nested_context_managers()

    # 5. 执行性能测试
    print('\n' + '-' * 80)
    print('6. 性能测试示例')
    print('-' * 80)
    performance_test()

    print('\n' + '=' * 80)
    print('NSWrapsLite 计时工具模块示例程序 演示完毕')
    print('=' * 80)


if __name__ == '__main__':
    asyncio.run(main())
