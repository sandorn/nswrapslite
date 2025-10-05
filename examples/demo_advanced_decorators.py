# !/usr/bin/env python3
"""
==============================================================
Description  : nswrapslite模块高级功能示例
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-01 13:15:00
Github       : https://github.com/sandorn

演示nswrapslite模块中的高级装饰器使用方法
==============================================================
"""

from __future__ import annotations

import asyncio
import time

from xtlog import mylog

from nswrapslite import async_executor, cache_wrapper, exception_wraps, logging_wraps

# 配置日志级别
mylog.set_level('INFO')


# 演示缓存装饰器
def demo_cache():
    """演示缓存装饰器的使用"""
    print('\n=== 缓存装饰器示例 ===')

    @cache_wrapper(maxsize=10)  # 最多缓存10个结果
    def expensive_calculation(x: int, y: int) -> int:
        """模拟一个耗时的计算"""
        print(f'执行计算: {x} + {y}')
        time.sleep(0.5)  # 模拟耗时操作
        return x + y

    # 第一次调用 - 会执行实际计算
    start = time.time()
    result1 = expensive_calculation(5, 3)
    print(f'第一次结果: {result1}, 耗时: {time.time() - start:.4f}秒')

    # 第二次调用 - 应该从缓存获取
    start = time.time()
    result2 = expensive_calculation(5, 3)
    print(f'第二次结果: {result2}, 耗时: {time.time() - start:.4f}秒')

    # 不同参数调用 - 会执行实际计算
    start = time.time()
    result3 = expensive_calculation(10, 20)
    print(f'不同参数结果: {result3}, 耗时: {time.time() - start:.4f}秒')

    # 注意：当前版本的cache_wrapper不支持异步函数
    # 以下代码为演示目的，但实际执行会报错
    # 如需异步缓存功能，请关注未来版本更新


# 演示异常处理装饰器
def demo_exception_handler():
    """演示异常处理装饰器的使用"""
    print('\n=== 异常处理装饰器示例 ===')

    @exception_wraps(re_raise=False, default_return='操作失败')
    def risky_operation(should_fail: bool = False) -> str:
        """一个可能失败的操作"""
        if should_fail:
            raise ValueError('操作故意失败')
        return '操作成功'

    # 正常调用
    result1 = risky_operation(should_fail=False)
    print(f'正常调用结果: {result1}')

    # 触发异常的调用
    result2 = risky_operation(should_fail=True)
    print(f'异常调用结果: {result2}')

    # 测试自定义异常处理
    @exception_wraps(
        re_raise=False,
        handler=lambda e: {
            ValueError: lambda e: f'值错误: {e!s}',
            TypeError: lambda e: f'类型错误: {e!s}',
        }.get(type(e), lambda e: f'未知错误: {type(e).__name__}')(e),
    )
    def complex_operation(error_type: str = 'none') -> str:
        """根据参数抛出不同类型的异常"""
        if error_type == 'value':
            raise ValueError('值不合法')
        if error_type == 'type':
            raise TypeError('类型不匹配')
        if error_type == 'other':
            raise RuntimeError('运行时错误')
        return '操作成功完成'

    print(f'无异常: {complex_operation()}')
    print(f'值错误处理: {complex_operation(error_type="value")}')
    print(f'类型错误处理: {complex_operation(error_type="type")}')
    print(f'其他错误处理: {complex_operation(error_type="other")}')


# 演示日志装饰器
def demo_log_decorator():
    """演示日志装饰器的使用"""
    print('\n=== 日志装饰器示例 ===')

    @logging_wraps(log_args=True, log_result=True)
    def process_data(data: str, factor: int = 2) -> str:
        """处理数据的函数"""
        return data * factor

    # 调用带日志的函数
    result = process_data('test', 3)
    print(f'处理结果: {result}')

    # 测试异步函数日志
    @logging_wraps(log_args=True, log_result=True)
    async def async_process_data(data: list[int]) -> list[int]:
        """异步处理数据"""
        await asyncio.sleep(0.2)
        return [x * 2 for x in data]

    async def run_async_log():
        result = await async_process_data([1, 2, 3, 4, 5])
        print(f'异步处理结果: {result}')

    asyncio.run(run_async_log())


# 演示执行器包装器
def demo_executor_wrapper():
    """演示执行器包装器的使用"""
    print('\n=== 执行器包装器示例 ===')

    # 将同步函数转换为可在异步代码中使用的函数
    @async_executor
    def cpu_intensive_task(n: int) -> int:
        """模拟CPU密集型任务"""
        print(f'开始CPU密集型任务: {n}')
        result = 0
        for i in range(n * 100000):
            result += i
        return result

    async def run_in_executor():
        # 直接等待执行器包装的函数
        result1 = await cpu_intensive_task(5)
        print(f'CPU密集型任务结果: {result1}')

        # 并发执行多个任务
        tasks = [cpu_intensive_task(i) for i in range(1, 4)]
        results = await asyncio.gather(*tasks)
        print(f'并发执行结果: {results}')

    asyncio.run(run_in_executor())


# 主函数，运行所有高级示例
def main():
    """运行所有高级装饰器示例"""
    print('==== xt_wraps 高级装饰器示例 ====')

    demo_cache()
    demo_exception_handler()
    demo_log_decorator()
    demo_executor_wrapper()

    print('\n==== 所有高级示例运行完毕 ====')


if __name__ == '__main__':
    main()
