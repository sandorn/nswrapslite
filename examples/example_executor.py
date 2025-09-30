# !/usr/bin/env python3
"""
NSWrapsLite 执行器模块示例程序

本示例展示了 NSWrapsLite 库中执行器模块的功能用法，包括:
1. executor_wraps 装饰器：异步执行同步函数或增强异步函数
2. run_executor_wraps 装饰器：同步运行异步函数
3. future_wraps 装饰器：将函数转换为返回 Future 对象的函数
4. future_wraps_result 函数：等待 Future 完成并获取结果

每个示例都包含详细的注释和输出，帮助您理解如何在实际项目中使用这些执行器功能。
"""
from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from nswrapslite.executor import (
    executor_wraps,
    future_wraps,
    future_wraps_result,
    run_executor_wraps,
)


# 同步函数示例
@executor_wraps
def blocking_io_operation(duration: float, value: str) -> str:
    """模拟一个阻塞的IO操作"""
    print(f'执行阻塞操作: 持续{duration}秒, 值={value}')
    time.sleep(duration)  # 模拟IO阻塞
    return f'完成阻塞操作: {value}'


# 异步函数示例
@executor_wraps
async def async_operation(duration: float, value: str) -> str:
    """模拟一个异步操作"""
    print(f'执行异步操作: 持续{duration}秒, 值={value}')
    await asyncio.sleep(duration)  # 异步等待
    return f'完成异步操作: {value}'


async def test_basic_executor_wraps():
    """测试executor_wraps的基本用法"""
    print('\n测试同步函数转为异步函数:')
    # 虽然blocking_io_operation是同步函数，但装饰后可以使用await
    result1 = await blocking_io_operation(0.5, 'test1')
    print(f'结果: {result1}')

    print('\n测试异步函数增强:')
    # 异步函数也可以被executor_wraps装饰，获得统一的异常处理等增强功能
    result2 = await async_operation(0.3, 'test2')
    print(f'结果: {result2}')

    print('\n测试并发执行:')
    # 并发执行多个操作
    start_time = time.time()
    results = await asyncio.gather(
        blocking_io_operation(0.5, 'concurrent1'),
        blocking_io_operation(0.5, 'concurrent2'),
        async_operation(0.3, 'concurrent3'),
    )
    elapsed_time = time.time() - start_time
    print(f'并发执行结果: {results}')
    print(f'并发执行耗时: {elapsed_time:.3f}秒 (应该小于串行执行的1.3秒)')


@executor_wraps(background=True)
def background_task(duration: float, task_id: str) -> str:
    """在后台执行的任务"""
    print(f'启动后台任务 {task_id}: 持续{duration}秒')
    time.sleep(duration)
    result = f'完成后台任务 {task_id}'
    print(result)
    return result


@executor_wraps(background=True)
async def background_async_task(duration: float, task_id: str) -> str:
    """在后台执行的异步任务"""
    print(f'启动后台异步任务 {task_id}: 持续{duration}秒')
    await asyncio.sleep(duration)
    result = f'完成后台异步任务 {task_id}'
    print(result)
    return result


async def test_background_execution():
    """测试后台执行模式"""
    print('\n启动后台同步任务:')
    # 启动后台任务，但不等待其完成
    future1 = background_task(2.0, 'T1')

    print('\n启动后台异步任务:')
    future2 = background_async_task(1.5, 'T2')

    # 主线程可以继续执行其他操作
    print('\n主线程继续执行其他操作...')
    time.sleep(0.5)
    print('主线程执行其他操作完成')

    # 稍后可以选择等待后台任务完成并获取结果
    print('\n等待后台任务完成并获取结果:')
    result1 = await future1
    result2 = await future2
    print(f'后台任务结果: {result1}, {result2}')


# 创建自定义线程池执行器
custom_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix='CustomExecutor')


import threading


# 使用自定义执行器的函数
@executor_wraps(executor=custom_executor)
def custom_executor_task(task_id: int) -> str:
    """使用自定义执行器的任务"""
    # 在线程池中运行时，应使用threading模块获取线程名而不是asyncio
    thread_name = threading.current_thread().name
    print(f'[{thread_name}] 执行自定义执行器任务: {task_id}')
    time.sleep(0.2)
    return f'自定义执行器任务 {task_id} 完成'


async def test_custom_executor():
    """测试自定义执行器"""
    print('\n使用自定义执行器执行多个任务:')
    start_time = time.time()

    # 并发执行多个任务
    tasks = [custom_executor_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks)

    elapsed_time = time.time() - start_time
    print(f'自定义执行器任务结果: {results}')
    print(f'自定义执行器任务总耗时: {elapsed_time:.3f}秒')

    # 注意：实际应用中应在适当的时候关闭自定义执行器
    # custom_executor.shutdown(wait=True)


async def original_async_function(duration: float, name: str) -> str:
    """原始的异步函数"""
    print(f'原始异步函数 {name}: 开始执行，持续{duration}秒')
    await asyncio.sleep(duration)
    return f'原始异步函数 {name} 完成'


@run_executor_wraps
async def wrapped_async_function(duration: float, name: str) -> str:
    """使用run_executor_wraps装饰的异步函数"""
    print(f'包装的异步函数 {name}: 开始执行，持续{duration}秒')
    await asyncio.sleep(duration)
    return f'包装的异步函数 {name} 完成'


def test_run_executor_wraps():
    """测试run_executor_wraps装饰器"""
    print('\n尝试直接调用原始异步函数 (这会失败):')
    try:
        # 直接调用异步函数会返回coroutine对象，而不是结果
        result = original_async_function(0.5, 'test')
        print(f'结果类型: {type(result)}')
        # 需要await才能获取结果，但在同步上下文中不能使用await
        # 清理未使用的协程对象以避免警告
        asyncio.create_task(result).cancel()
    except Exception as e:
        print(f'错误: {type(e).__name__}: {e}')

    print('\n调用包装的异步函数 (可以直接调用):')
    # 使用run_executor_wraps装饰后，可以直接调用异步函数而不需要await
    result = wrapped_async_function(0.5, 'test')
    print(f'结果: {result}')

    print('\n在普通函数中使用包装的异步函数:')

    def normal_function():
        print('普通函数开始执行')
        # 在普通函数中可以直接调用包装的异步函数
        result = wrapped_async_function(0.3, 'inner')
        print(f'普通函数中获取结果: {result}')
        print('普通函数执行完成')

    normal_function()


@future_wraps
def future_task(task_id: int) -> dict[str, Any]:
    """返回Future对象的任务"""
    print(f'开始执行future任务 {task_id}')
    time.sleep(0.5)
    return {
        'task_id': task_id,
        'result': f'任务 {task_id} 完成',
        'timestamp': time.time(),
    }


@future_wraps(executor=custom_executor)
def custom_future_task(task_id: int) -> list[int]:
    """使用自定义执行器返回Future对象的任务"""
    print(f'开始执行自定义future任务 {task_id}')
    time.sleep(0.3)
    return [task_id] * (task_id + 1)


async def test_future_wraps():
    """测试future_wraps装饰器"""
    print('\n创建多个Future对象:')
    # 创建多个Future对象，但不立即等待它们完成
    futures = [future_task(i) for i in range(3)]
    custom_futures = [custom_future_task(i) for i in range(2)]

    print('\nFuture对象创建完成，可以稍后处理...')

    # 等待所有Future完成并获取结果
    print('\n等待所有Future完成:')
    results = await asyncio.gather(*futures, *custom_futures)
    print(f'所有Future结果: {results}')

    # 单独处理Future对象
    print('\n单独处理Future对象:')
    future = future_task(999)
    # 可以在创建Future后检查其状态
    print(f'Future状态 (创建后): done={future.done()}, cancelled={future.cancelled()}')

    # 等待Future完成并获取结果
    result = await future
    print(f'单独Future结果: {result}')
    print(f'Future状态 (完成后): done={future.done()}, cancelled={future.cancelled()}')


@future_wraps
def long_running_task(duration: float, task_id: int) -> str:
    """长时间运行的任务"""
    print(f'开始执行长时间任务 {task_id}: 持续{duration}秒')
    time.sleep(duration)
    return f'长时间任务 {task_id} 完成'


@future_wraps
def exception_task():
    """会抛出异常的任务"""
    print('执行会抛出异常的任务')
    raise ValueError('任务执行失败')

    # 注意：以下代码永远不会执行到
    print('异常任务完成')  # 永远不会执行到
    return '这不会返回'


async def test_future_wraps_result():
    """测试future_wraps_result函数"""

    print('\n测试正常完成的Future:')
    normal_future = long_running_task(1.0, 1)
    try:
        result = await future_wraps_result(normal_future, timeout=5.0)  # 明确指定超时
        print(f'正常Future结果: {result}')
    except Exception as e:
        print(f'正常Future错误: {type(e).__name__}: {e}')

    print('\n测试超时的Future:')
    timeout_future = long_running_task(5.0, 2)
    try:
        # 直接使用 future_wraps_result 的超时参数
        result = await future_wraps_result(timeout_future, timeout=2.0)
        print(f'超时Future结果: {result}')  # 不会执行到这里
    except TimeoutError:
        print('捕获到超时异常')
    except Exception as e:
        print(f'超时Future其他错误: {type(e).__name__}: {e}')

    print('\n测试异常的Future:')
    try:
        exception_future = exception_task()
        result = await future_wraps_result(exception_future, timeout=5.0)
        print(f'异常Future结果: {result}')  # 不会执行到这里
    except ValueError as e:
        print(f'捕获到预期异常9: {e}')
    except Exception as e:
        print(f'捕获到其他异常0: {type(e).__name__}: {e}')


@executor_wraps
def database_query(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """模拟数据库查询操作"""
    print(f'执行数据库查询: {query}, 参数: {params}')
    # 模拟数据库查询延迟
    time.sleep(0.5)
    # 模拟查询结果
    return [
        {'id': 1, 'name': 'Item 1', 'value': 100},
        {'id': 2, 'name': 'Item 2', 'value': 200},
    ]


@executor_wraps(background=True)
def api_call(endpoint: str, method: str = 'GET', data: dict[str, Any] | None = None) -> dict[str, Any]:
    """模拟API调用"""
    print(f'调用API: {method} {endpoint}, 数据: {data}')
    # 模拟网络延迟
    time.sleep(0.8)
    # 模拟API响应
    return {
        'status': 200,
        'data': {'result': 'success', 'items': 42},
        'headers': {'content-type': 'application/json'},
    }


@executor_wraps(executor=ThreadPoolExecutor(max_workers=2))
def cpu_intensive_task(data: list[int]) -> dict[str, Any]:
    """模拟计算密集型任务"""
    print(f'执行计算密集型任务，数据长度: {len(data)}')
    # 模拟计算延迟
    time.sleep(1.0)
    # 模拟计算结果
    return {
        'sum': sum(data),
        'average': sum(data) / len(data) if data else 0,
        'max': max(data) if data else 0,
        'min': min(data) if data else 0,
    }


async def test_practical_scenarios():
    """测试实际应用场景"""
    print('\n场景1: 数据库查询 (异步执行):')
    # 异步执行数据库查询
    db_result = await database_query('SELECT * FROM items WHERE status = :status', {'status': 'active'})
    print(f'数据库查询结果: {db_result}')

    print('\n场景2: API调用 (后台执行):')
    # 后台执行API调用，不阻塞主流程
    api_future = api_call('/api/v1/users', 'POST', {'name': 'New User'})

    print('\n场景3: 计算密集型任务 (使用专用执行器):')
    # 使用专用执行器执行计算密集型任务
    calc_task = cpu_intensive_task(list(range(1000000)))

    print('\n场景4: 组合操作 (并发执行多个任务):')
    # 并发执行多个不同类型的任务
    start_time = time.time()
    results = await asyncio.gather(
        database_query('SELECT * FROM logs LIMIT 10'),
        api_future,  # 等待之前启动的API调用完成
        calc_task,  # 等待计算密集型任务完成
    )
    elapsed_time = time.time() - start_time

    db_results, api_results, calc_results = results
    print(f'组合操作 - 数据库结果: {db_results[:1]}...')  # 只显示部分结果
    print(f'组合操作 - API结果: {api_results}')
    print(f'组合操作 - 计算结果: {calc_results}')
    print(f'组合操作总耗时: {elapsed_time:.3f}秒')


class BusinessService:
    """业务服务类，演示执行器的最佳实践组合"""

    def __init__(self):
        # 创建专用执行器
        self.io_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix='IOExecutor')
        self.cpu_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='CPUExecutor')

    async def close(self):
        """关闭执行器"""
        self.io_executor.shutdown(wait=True)
        self.cpu_executor.shutdown(wait=True)

    @executor_wraps(executor=ThreadPoolExecutor(max_workers=10))
    def fetch_data(self, source: str) -> list[dict[str, Any]]:
        """从数据源获取数据"""
        print(f'从 {source} 获取数据')
        time.sleep(0.3)  # 模拟IO延迟
        return [{'id': i, 'source': source, 'value': i * 10} for i in range(5)]

    @executor_wraps(executor=ThreadPoolExecutor(max_workers=2))
    def process_data(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """处理数据"""
        print(f'处理数据，长度: {len(data)}')
        time.sleep(0.5)  # 模拟计算延迟
        total_value = sum(item['value'] for item in data)
        return {
            'total_items': len(data),
            'total_value': total_value,
            'average_value': total_value / len(data) if data else 0,
        }

    @executor_wraps(background=True)
    def save_results(self, results: dict[str, Any]) -> dict[str, Any]:
        """保存结果 (后台执行)"""
        print(f'保存结果: {results}')
        time.sleep(0.2)  # 模拟IO延迟
        return {
            'status': 'success',
            'saved_at': time.time(),
            'record_count': results['total_items'],
        }

    async def business_process(self) -> dict[str, Any]:
        """完整的业务流程"""
        print('\n开始业务流程...')

        # 1. 并发获取多源数据
        print('\n1. 并发获取多源数据...')
        data_sources = ['db1', 'db2', 'api1']
        fetch_tasks = [self.fetch_data(source) for source in data_sources]
        all_data = await asyncio.gather(*fetch_tasks)

        # 合并所有数据
        merged_data = [item for sublist in all_data for item in sublist]
        print(f'获取到 {len(merged_data)} 条数据')

        # 2. 处理数据
        print('\n2. 处理数据...')
        processed_results = await self.process_data(merged_data)
        print(f'处理结果: {processed_results}')

        # 3. 后台保存结果
        print('\n3. 后台保存结果...')
        save_future = self.save_results(processed_results)

        # 4. 同时执行其他操作
        print('\n4. 同时执行其他操作...')
        await asyncio.sleep(0.1)
        print('其他操作完成')

        # 5. 等待保存完成
        print('\n5. 等待保存完成...')
        save_result = await save_future
        print(f'保存结果: {save_result}')

        print('\n业务流程完成!')
        return {
            'status': 'completed',
            'processed_results': processed_results,
            'save_result': save_result,
            'total_sources': len(data_sources),
        }


async def test_best_practices():
    """测试最佳实践组合"""
    service = BusinessService()
    try:
        # 调用业务流程
        # 由于business_process使用了run_executor_wraps装饰，也可以在同步代码中直接调用
        # 但在这里我们在异步上下文中调用它
        result = await service.business_process()
        print(f'\n最终业务流程结果: {result}')
    finally:
        # 清理资源
        await service.close()


# ======================================================
# 主函数 - 演示所有执行器功能
# ======================================================
async def main() -> None:
    """主函数，演示所有执行器工具的用法"""
    print('NSWrapsLite 执行器模块示例程序')

    print('1. 基本用法 - executor_wraps')
    await test_basic_executor_wraps()

    print('2. 后台执行模式')
    await test_background_execution()

    print('3. 自定义执行器')
    await test_custom_executor()

    print('4. 同步运行异步函数')
    test_run_executor_wraps()

    print('5. Future执行器')
    await test_future_wraps()

    print('6. Future结果获取器')
    await test_future_wraps_result()

    print('7. 实际应用场景')
    await test_practical_scenarios()

    print('8. 最佳实践组合')
    await test_best_practices()


if __name__ == '__main__':
    # 运行主函数
    asyncio.run(main())
