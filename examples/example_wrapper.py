# !/usr/bin/env python3
"""
NSWrapsLite 装饰器工具模块示例程序

本示例展示了 NSWrapsLite 库中装饰器工具模块的所有功能用法，包括:
1. decorator_factory - 通用装饰器工厂，支持自定义钩子函数
2. timer_wrapper - 计时装饰器，记录函数执行时间
3. exc_wrapper - 异常处理装饰器，统一处理异常逻辑
4. log_wrapper - 日志装饰器，记录函数调用信息

每个示例都包含同步和异步函数的用法、基本配置和高级配置选项。
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

from nswrapslite.wrapper import (
    decorator_factory,
    exc_wrapper,
    log_wrapper,
    timer_wrapper,
)

# ======================================================
# 示例 1: decorator_factory 通用装饰器工厂
# ======================================================

# 方式1: 创建简单的日志装饰器
print('\n=== 示例1: decorator_factory 通用装饰器工厂 ===')


# 定义钩子函数
def log_before(func, args, kwargs, context):
    """函数执行前的日志钩子"""
    print(f'[前置钩子] 调用函数: {func.__name__}')
    # 可以在上下文中存储信息供后续钩子使用
    context['start_time'] = time.time()
    # 如果钩子返回非None值，函数将直接返回该值而不执行原函数
    # return "Hook early return"  # 取消注释测试提前返回功能


def log_after(func, args, kwargs, result, context):
    """函数执行后的日志钩子"""
    start_time = context.get('start_time')
    if start_time:
        execution_time = time.time() - start_time
        print(f'[后置钩子] 函数 {func.__name__} 执行耗时: {execution_time:.4f}秒')
    print(f'[后置钩子] 函数 {func.__name__} 返回结果: {result}')
    # 可以修改返回值
    # return f"Modified: {result}"  # 取消注释测试修改返回值功能
    return result


def log_exception(func, args, kwargs, exc, context):
    """函数异常时的钩子"""
    print(f'[异常钩子] 函数 {func.__name__} 发生异常: {type(exc).__name__}: {exc}')
    # 可以返回默认值或者重新抛出异常
    # return "Default on exception"  # 取消注释测试异常默认值
    raise  # 重新抛出异常


# 使用装饰器工厂创建自定义装饰器
custom_log_decorator = decorator_factory(before_hook=log_before, after_hook=log_after, except_hook=log_exception)


# 应用自定义装饰器到同步函数
@custom_log_decorator
def calculate_sum(a: int, b: int) -> int:
    """计算两个数的和（演示同步函数装饰器）"""
    time.sleep(0.1)  # 模拟耗时操作
    return a + b


# 应用自定义装饰器到异步函数
@custom_log_decorator
async def async_multiply(x: int, y: int) -> int:
    """计算两个数的乘积（演示异步函数装饰器）"""
    await asyncio.sleep(0.2)  # 模拟异步耗时操作
    return x * y


# 应用自定义装饰器到会抛出异常的函数
@custom_log_decorator
def divide_with_error(a: int, b: int) -> float:
    """除法函数，演示异常处理（当b=0时抛出异常）"""
    time.sleep(0.05)  # 模拟耗时操作
    return a / b


# ======================================================
# 示例 2: timer_wrapper 计时装饰器
# ======================================================
print('\n=== 示例2: timer_wrapper 计时装饰器 ===')


# 方式1: 直接装饰同步函数
@timer_wrapper
def process_data(data: list[int]) -> list[int]:
    """处理数据列表（演示同步函数计时）"""
    result = []
    for item in data:
        time.sleep(0.01)  # 模拟每个元素的处理时间
        result.append(item * 2)
    return result


# 方式2: 带括号装饰异步函数
@timer_wrapper()
async def fetch_data(url: str) -> str:
    """模拟从网络获取数据（演示异步函数计时）"""
    await asyncio.sleep(0.3)  # 模拟网络延迟
    return f'Data from {url}'


# 方式3: 计时会抛出异常的函数
@timer_wrapper
def error_operation() -> None:
    """会抛出异常的操作（演示异常时的计时）"""
    time.sleep(0.15)  # 模拟耗时操作
    raise ValueError('测试异常')


# ======================================================
# 示例 3: exc_wrapper 异常处理装饰器
# ======================================================
print('\n=== 示例3: exc_wrapper 异常处理装饰器 ===')


# 方式1: 基本用法，捕获所有异常
@exc_wrapper(re_raise=False, default_return=0)
def safe_divide(a: int, b: int) -> float:
    """安全除法函数（演示基本异常处理）"""
    return a / b


# 方式2: 只捕获特定异常
@exc_wrapper(
    allowed_exceptions=(ValueError, TypeError),
    re_raise=False,
    default_return='Error occurred',
    custom_message='数据验证失败',
)
def validate_data(data: Any) -> str:
    """数据验证函数（演示特定异常捕获）"""
    if not isinstance(data, (int, float)):
        raise TypeError('数据必须是数字')
    if data < 0:
        raise ValueError('数据不能为负数')
    return f'验证通过: {data}'


# 方式3: 异步函数异常处理
@exc_wrapper(
    re_raise=False,
    default_return=None,
    log_traceback=False,  # 不记录完整堆栈
)
async def async_fetch_data(url: str) -> dict[str, Any] | None:
    """异步获取数据（演示异步函数异常处理）"""
    if not url.startswith('http'):
        raise ValueError('无效的URL格式')
    await asyncio.sleep(0.2)  # 模拟网络请求
    return {'url': url, 'status': 'success'}


# ======================================================
# 示例 4: log_wrapper 日志装饰器
# ======================================================
print('\n=== 示例4: log_wrapper 日志装饰器 ===')


# 方式1: 基本用法，记录参数和结果
@log_wrapper
def add_numbers(x: int, y: int) -> int:
    """加法函数（演示基本日志记录）"""
    return x + y


# 方式2: 自定义配置，不记录参数
@log_wrapper(
    log_args=False,  # 不记录参数
    log_result=True,  # 记录结果
    re_raise=False,  # 发生异常不重新抛出
    default_return=-1,  # 异常时的默认返回值
)
def complex_calculation(a: int, b: int, c: int) -> int:
    """复杂计算函数（演示自定义日志配置）"""
    result = a * b + c
    if result > 100:
        raise ValueError('计算结果过大')
    return result


# 方式3: 异步函数日志记录
@log_wrapper(log_args=True, log_result=True, custom_message='异步计算完成')
async def async_calculate(values: list[int]) -> int:
    """异步计算函数（演示异步函数日志记录）"""
    await asyncio.sleep(0.1)  # 模拟异步操作
    return sum(values)


# ======================================================
# 示例 5: 多个装饰器组合使用
# ======================================================
print('\n=== 示例5: 多个装饰器组合使用 ===')


# 组合使用多个装饰器
# 注意：装饰器的顺序很重要，从下到上执行
@log_wrapper(custom_message='组合装饰器测试')
@timer_wrapper
@exc_wrapper(re_raise=False, default_return=None)
def combined_operation(value: int) -> float | None:
    """组合操作函数（演示多个装饰器的组合使用）"""
    if value % 2 != 0:
        raise ValueError('值必须是偶数')
    time.sleep(0.1)  # 模拟耗时操作
    return value / 2


# 异步函数组合装饰器
@timer_wrapper
@exc_wrapper(re_raise=True)
async def async_combined_operation(data: dict[str, Any]) -> dict[str, Any]:
    """异步组合操作（演示异步函数的装饰器组合）"""
    if 'id' not in data:
        raise KeyError("缺少必需的'id'字段")
    await asyncio.sleep(0.2)  # 模拟异步操作
    data['processed'] = True
    return data


# ======================================================
# 主函数 - 演示所有装饰器功能
# ======================================================
async def main() -> None:
    """主函数，演示所有装饰器工具的用法"""
    print('=' * 80)
    print('NSWrapsLite 装饰器工具模块示例程序')
    print('=' * 80)

    # 1. 演示 decorator_factory 通用装饰器工厂
    print('\n' + '-' * 80)
    print('1. decorator_factory 通用装饰器工厂示例')
    print('-' * 80)

    # 测试同步函数
    sum_result = calculate_sum(10, 20)
    print(f'calculate_sum 结果: {sum_result}')

    # 测试异步函数
    multiply_result = await async_multiply(5, 6)
    print(f'async_multiply 结果: {multiply_result}')

    # 测试异常处理
    print('测试异常处理...')
    try:
        divide_with_error(10, 0)
    except ZeroDivisionError as e:
        print(f'预期的除零异常: {e}')

    # 2. 演示 timer_wrapper 计时装饰器
    print('\n' + '-' * 80)
    print('2. timer_wrapper 计时装饰器示例')
    print('-' * 80)

    # 测试同步函数计时
    processed_data = process_data([1, 2, 3, 4, 5])
    print(f'process_data 结果: {processed_data}')

    # 测试异步函数计时
    fetched_data = await fetch_data('https://example.com')
    print(f'fetch_data 结果: {fetched_data}')

    # 测试异常时的计时
    print('测试异常时的计时...')
    try:
        error_operation()
    except ValueError as e:
        print(f'预期的异常: {e}')

    # 3. 演示 exc_wrapper 异常处理装饰器
    print('\n' + '-' * 80)
    print('3. exc_wrapper 异常处理装饰器示例')
    print('-' * 80)

    # 测试正常除法
    result1 = safe_divide(10, 2)
    print(f'safe_divide(10, 2) 结果: {result1}')

    # 测试除零保护
    result2 = safe_divide(10, 0)
    print(f'safe_divide(10, 0) 结果: {result2} (预期的默认返回值)')

    # 测试数据验证
    result3 = validate_data(42)
    print(f'validate_data(42) 结果: {result3}')

    # 测试类型错误
    result4 = validate_data('not a number')
    print(f"validate_data('not a number') 结果: {result4} (预期的默认返回值)")

    # 测试异步函数异常处理
    async_result1 = await async_fetch_data('https://example.com')
    print(f'async_fetch_data(valid url) 结果: {async_result1}')

    async_result2 = await async_fetch_data('invalid-url')
    print(f'async_fetch_data(invalid url) 结果: {async_result2} (预期的默认返回值)')

    # 4. 演示 log_wrapper 日志装饰器
    print('\n' + '-' * 80)
    print('4. log_wrapper 日志装饰器示例')
    print('-' * 80)

    # 测试基本日志记录
    log_result1 = add_numbers(3, 4)
    print(f'add_numbers 结果: {log_result1}')

    # 测试自定义日志配置
    log_result2 = complex_calculation(10, 5, 20)
    print(f'complex_calculation(10, 5, 20) 结果: {log_result2}')

    # 测试异常日志
    log_result3 = complex_calculation(10, 10, 5)
    print(f'complex_calculation(10, 10, 5) 结果: {log_result3} (预期的默认返回值)')

    # 测试异步函数日志
    async_log_result = await async_calculate([1, 2, 3, 4, 5])
    print(f'async_calculate 结果: {async_log_result}')

    # 5. 演示多个装饰器组合使用
    print('\n' + '-' * 80)
    print('5. 多个装饰器组合使用示例')
    print('-' * 80)

    # 测试同步函数组合装饰器
    combined_result1 = combined_operation(4)
    print(f'combined_operation(4) 结果: {combined_result1}')

    combined_result2 = combined_operation(5)
    print(f'combined_operation(5) 结果: {combined_result2} (预期的默认返回值)')

    # 测试异步函数组合装饰器
    try:
        async_combined_result1 = await async_combined_operation({'id': 1, 'name': 'test'})
        print(f'async_combined_operation(valid) 结果: {async_combined_result1}')

        # 这应该抛出异常
        async_combined_result2 = await async_combined_operation({'name': 'test'})
        print(f'async_combined_operation(invalid) 结果: {async_combined_result2}')
    except KeyError as e:
        print(f'预期的KeyError异常: {e}')

    print('\n' + '=' * 80)
    print('NSWrapsLite 装饰器工具模块示例程序 演示完毕')
    print('=' * 80)


if __name__ == '__main__':
    asyncio.run(main())
