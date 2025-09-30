# !/usr/bin/env python3
"""
==============================================================
Description  : 日志模块示例程序 - 演示如何使用nswrapslite库中的日志功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2022-12-22 17:35:56
LastEditTime : 2025-09-29 16:00:00
Github       : https://github.com/sandorn/nswraps

示例内容:
- mylog基本日志记录功能
- log_wraps装饰器的同步/异步函数使用
- 不同日志级别与参数配置
- 异常处理与日志集成
- 实际应用场景展示
==============================================================
"""
from __future__ import annotations

import asyncio
from typing import Any

from xtlog import mylog

from nswrapslite.log import log_wraps


@log_wraps
def add_numbers(a: int, b: int) -> int:
    """示例同步函数，使用默认的log_wraps配置"""
    return a + b


@log_wraps(log_args=True, log_result=False)
def multiply_numbers(a: int, b: int) -> int:
    """示例同步函数，配置log_wraps只记录参数不记录结果"""
    return a * b


@log_wraps(re_raise=True, log_traceback=True)
def divide_numbers(a: int, b: int) -> float:
    """示例同步函数，演示异常处理（re_raise=True）"""
    return a / b


@log_wraps(re_raise=False, default_return=0)
def safe_divide(a: int, b: int) -> float:
    """示例同步函数，演示异常处理（re_raise=False）"""
    return a / b


@log_wraps
async def async_add_numbers(a: int, b: int) -> int:
    """示例异步函数，使用默认的log_wraps配置"""
    await asyncio.sleep(0.1)  # 模拟异步操作
    return a + b


@log_wraps(re_raise=True, log_traceback=True)
async def async_divide_numbers(a: int, b: int) -> float:
    """示例异步函数，演示异常处理"""
    await asyncio.sleep(0.1)  # 模拟异步操作
    return a / b


@log_wraps(custom_message='执行计算操作')
def calculate_with_custom_message(a: int, b: int) -> int:
    """示例函数，使用自定义消息"""
    return a + b * 2


@log_wraps
def complex_data_handling(data: list[dict[str, Any]]) -> dict[str, int]:
    """示例函数，处理复杂数据结构"""
    result: dict[str, int] = {}
    for item in data:
        name = item.get('name', 'unknown')
        value = item.get('value', 0)
        result[name] = value * 2
    return result


def log_wraps_sync_example() -> None:
    """log_wraps装饰器同步函数示例"""
    print('\n=== log_wraps装饰器同步函数示例 ===')

    # 基本使用示例
    result = add_numbers(5, 3)
    print(f'函数返回结果: {result}')

    # # 只记录参数不记录结果
    # multiply_numbers(4, 7)

    # # 异常处理示例 (re_raise=True)
    # try:
    #     divide_numbers(10, 0)
    # except ZeroDivisionError:
    #     print('捕获到ZeroDivisionError异常，这是预期的行为')

    # # 异常处理示例 (re_raise=False)
    # result = safe_divide(10, 0)
    # print(f'安全除法返回默认值: {result}')

    # # 自定义消息示例
    # calculate_with_custom_message(3, 5)

    # # 复杂数据处理示例
    # data = [{'name': 'item1', 'value': 5}, {'name': 'item2', 'value': 10}]
    # complex_result = complex_data_handling(data)
    # print(f'复杂数据处理结果: {complex_result}')


async def log_wraps_async_example() -> None:
    """log_wraps装饰器异步函数示例"""
    print('\n=== log_wraps装饰器异步函数示例 ===')

    # 基本使用示例
    result = await async_add_numbers(8, 2)
    print(f'异步函数返回结果: {result}')

    # 异常处理示例
    try:
        await async_divide_numbers(15, 0)
    except ZeroDivisionError:
        print('捕获到ZeroDivisionError异常，这是预期的行为')


class DataProcessor:
    """演示log_wraps装饰器在类方法中的应用"""

    @log_wraps
    def process_data(self, data: str) -> str:
        """处理数据的同步方法"""
        mylog.info(f'处理数据: {data}', callfrom=self.process_data)
        return data.upper()

    @log_wraps
    async def async_process_data(self, data: str) -> str:
        """异步处理数据的方法"""
        await asyncio.sleep(0.2)  # 模拟异步操作
        mylog.info(f'异步处理数据: {data}', callfrom=self.async_process_data)
        return data.lower()


async def class_method_logging_example() -> None:
    """演示log_wraps装饰器在类方法中的应用"""
    print('\n=== log_wraps装饰器在类方法中的应用 ===')

    processor = DataProcessor()

    # 测试同步方法
    result = processor.process_data('Hello World')
    print(f'同步处理结果: {result}')

    # 测试异步方法
    async_result = await processor.async_process_data('Hello World')
    print(f'异步处理结果: {async_result}')


async def nested_function_logging() -> None:
    """嵌套函数中的日志记录示例"""
    print('\n=== 嵌套函数中的日志记录 ===')

    @log_wraps
    def outer_function(x: int) -> int:
        """外层函数"""

        @log_wraps
        def inner_function(y: int) -> int:
            """内层函数"""
            return y * 2

        result = inner_function(x)
        return result + 10

    # 调用外层函数，查看日志输出
    result = outer_function(5)
    print(f'嵌套函数调用结果: {result}')


async def main() -> None:
    """主函数"""
    # log_wraps同步函数示例
    log_wraps_sync_example()

    # log_wraps异步函数示例
    await log_wraps_async_example()

    # log_wraps在类方法中的应用
    await class_method_logging_example()

    # 嵌套函数中的日志记录
    await nested_function_logging()


if __name__ == '__main__':
    # 设置日志级别为DEBUG，以便看到所有日志

    # 运行主函数
    asyncio.run(main())
