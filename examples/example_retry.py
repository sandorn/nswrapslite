# !/usr/bin/env python3
"""
==============================================================
Description  : 重试机制模块示例程序 - 演示如何使用nswrapslite库中的重试功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-09-01 08:40:27
LastEditTime : 2025-09-29 16:00:00
Github       : https://github.com/sandorn/nswraps

示例内容:
- 基本同步函数重试
- 异步函数重试
- 特定异常类型重试
- 基于结果的重试
- HTTP请求重试
- Future对象重试
- 高级重试策略配置
- 实际应用场景
==============================================================
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import random
import time
from typing import Any

from nswrapslite.retry import (
    retry_async_wraps,
    retry_future,
    retry_request,
    retry_wraps,
)


# 模拟不稳定的同步函数
@retry_wraps(max_retries=3, delay=0.5)
def unstable_operation() -> str:
    """模拟一个不稳定的操作，有50%的概率失败"""
    print(f'执行不稳定操作: {time.strftime("%H:%M:%S")}')
    if random.random() < 0.5:
        raise ConnectionError('连接失败')
    return '操作成功'


# 模拟不稳定的异步函数
@retry_async_wraps(max_retries=5, delay=1.0, backoff=1.5, jitter=0.2)
async def unstable_async_operation() -> str:
    """模拟一个不稳定的异步操作，有60%的概率失败"""
    print(f'执行不稳定异步操作: {time.strftime("%H:%M:%S")}')
    await asyncio.sleep(0.1)  # 模拟异步操作
    if random.random() < 0.6:
        raise TimeoutError('操作超时')
    return '异步操作成功'


# 特定异常类型重试
def api_request(endpoint: str) -> dict[str, Any]:
    """模拟API请求，根据不同端点抛出不同异常"""
    print(f'请求API端点: {endpoint}')
    if endpoint == 'users':
        raise ConnectionError('数据库连接失败')
    if endpoint == 'products':
        raise ValueError('无效的产品ID')
    return {'status': 'success', 'data': []}


# 使用retry_wraps只重试特定异常类型
connection_retry = retry_wraps(max_retries=3, exceptions=(ConnectionError,))
safe_api_request = connection_retry(api_request)


# 基于结果的重试
def fetch_data(attempt_limit: int = 2) -> str | None:
    """模拟获取数据，可能返回None"""
    print('尝试获取数据')
    # 前几次尝试返回None，最后一次返回有效数据
    if fetch_data.attempt_count < attempt_limit:
        fetch_data.attempt_count += 1
        return None
    return '有效的数据'


# 初始化尝试计数器
fetch_data.attempt_count = 0

# 使用retry_wraps基于结果进行重试
data_retry = retry_wraps(max_retries=5, retry_on_result=lambda x: x is None)
safe_fetch_data = data_retry(fetch_data)


# HTTP请求重试示例（模拟）
class MockResponse:
    """模拟HTTP响应对象"""

    def __init__(self, status_code: int, text: str = ''):
        self.status_code = status_code
        self.text = text

    def json(self) -> dict[str, Any]:
        return {'status_code': self.status_code, 'message': self.text}


def mock_http_get(url: str, **kwargs: Any) -> MockResponse:
    """模拟HTTP GET请求"""
    print(f'发送HTTP GET请求到: {url}')
    # 模拟API限流或临时故障
    if url.endswith('/rate-limited'):
        # 前两次返回429 Too Many Requests，第三次返回200 OK
        if hasattr(mock_http_get, 'rate_limit_count'):
            mock_http_get.rate_limit_count += 1
        else:
            mock_http_get.rate_limit_count = 1

        if mock_http_get.rate_limit_count <= 2:
            return MockResponse(429, 'Too Many Requests')
    elif url.endswith('/unstable'):
        # 随机返回500 Internal Server Error或200 OK
        if random.random() < 0.6:
            return MockResponse(500, 'Internal Server Error')

    return MockResponse(200, 'Success')


# Future对象重试示例
def cpu_bound_task(task_id: int) -> str:
    """模拟CPU密集型任务"""
    print(f'执行CPU密集型任务 #{task_id}')
    time.sleep(1)  # 模拟耗时操作
    # 有30%的概率失败
    if random.random() < 0.3:
        raise RuntimeError(f'任务 #{task_id} 失败')
    return f'任务 #{task_id} 完成'


# 高级重试策略示例 - 自定义退避和抖动
@retry_wraps(max_retries=4, delay=0.2, backoff=3.0, jitter=0.3)
def sensitive_operation() -> str:
    """模拟需要精细控制重试策略的敏感操作"""
    print(f'执行敏感操作: {time.strftime("%H:%M:%S")}')
    # 模拟高失败率的敏感操作
    if random.random() < 0.7:
        raise PermissionError('权限验证失败')
    return '敏感操作成功'


# 数据库操作重试示例
class DatabaseOperation:
    """数据库操作类，演示如何在实际场景中使用重试机制"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        self.connect_attempts = 0

    def connect(self) -> bool:
        """尝试连接到数据库"""
        self.connect_attempts += 1
        print(f'尝试连接到数据库 (第{self.connect_attempts}次)')

        # 模拟连接失败的情况
        if self.connect_attempts <= 2:
            raise ConnectionError('数据库连接超时')

        # 模拟连接成功
        self.connection = {'status': 'connected'}
        print('数据库连接成功')
        return True

    @retry_wraps(max_retries=3, exceptions=(ConnectionError,), delay=1.0)
    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """执行数据库查询，自动处理连接和重试"""
        if not self.connection:
            self.connect()  # 这会触发重试逻辑

        print(f'执行查询: {query}')
        # 模拟查询结果
        return [{'id': 1, 'name': 'example'}]


async def basic_retry_example() -> None:
    """基本的同步函数重试示例"""
    print('\n=== 基本的同步函数重试示例 ===')
    try:
        result = unstable_operation()
        print(f'最终结果: {result}')
    except Exception as e:
        print(f'所有重试都失败了: {e}')


async def async_retry_example() -> None:
    """异步函数重试示例"""
    print('\n=== 异步函数重试示例 ===')
    try:
        result = await unstable_async_operation()
        print(f'最终结果: {result}')
    except Exception as e:
        print(f'所有重试都失败了: {e}')


async def specific_exception_retry_example() -> None:
    """特定异常类型的重试示例"""
    print('\n=== 特定异常类型的重试示例 ===')

    # 测试会重试的异常类型
    print('\n测试ConnectionError（会重试）:')
    try:
        result = safe_api_request('users')
        print(f'结果: {result}')
    except Exception as e:
        print(f'重试后仍然失败: {e}')

    # 测试不会重试的异常类型
    print('\n测试ValueError（不会重试）:')
    try:
        result = safe_api_request('products')
        print(f'结果: {result}')
    except Exception as e:
        print(f'直接失败（未重试）: {e}')


async def result_based_retry_example() -> None:
    """基于结果的重试示例"""
    print('\n=== 基于结果的重试示例 ===')
    result = safe_fetch_data()
    print(f'最终获取的数据: {result}')


async def http_request_retry_example() -> None:
    """HTTP请求重试示例"""
    print('\n=== HTTP请求重试示例 ===')

    # 测试基于状态码的重试
    print('\n测试基于状态码的重试（429 Too Many Requests）:')
    response = retry_request(
        mock_http_get,
        'https://api.example.com/rate-limited',
        max_retries=3,
        retry_on_status=[429, 500, 502, 503, 504],
    )
    print(f'最终响应状态码: {response.status_code}')

    # 测试随机故障的API
    print('\n测试随机故障的API:')
    response = retry_request(
        mock_http_get,
        'https://api.example.com/unstable',
        max_retries=5,
        delay=0.5,
        backoff=1.5,
        retry_on_status=[500],
    )
    print(f'最终响应状态码: {response.status_code}')


async def future_retry_example() -> None:
    """Future对象重试示例"""
    print('\n=== Future对象重试示例 ===')

    # 创建线程池执行器
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # 测试Future对象的重试
        try:
            result = await retry_future(lambda: executor.submit(cpu_bound_task, 1), max_retries=3, delay=1.0)
            print(f'Future结果: {result}')
        except Exception as e:
            print(f'所有Future重试都失败了: {e}')


async def advanced_retry_strategy_example() -> None:
    """高级重试策略示例"""
    print('\n=== 高级重试策略示例 ===')
    try:
        result = sensitive_operation()
        print(f'敏感操作结果: {result}')
    except Exception as e:
        print(f'敏感操作所有重试都失败了: {e}')


async def database_operation_example() -> None:
    """数据库操作重试示例"""
    print('\n=== 数据库操作重试示例 ===')

    # 创建数据库操作实例
    db = DatabaseOperation('mysql://localhost:3306/test_db')

    try:
        # 执行查询，这会自动处理连接重试
        results = db.execute_query('SELECT * FROM users')
        print(f'查询结果: {results}')
    except Exception as e:
        print(f'数据库操作失败: {e}')


async def combined_retry_example() -> None:
    """组合使用多种重试功能示例"""
    print('\n=== 组合使用多种重试功能示例 ===')

    # 定义一个复杂的业务操作
    @retry_async_wraps(max_retries=3, delay=1.0)
    async def complex_business_operation() -> dict[str, Any]:
        """复杂业务操作，结合多种重试策略"""
        print('开始复杂业务操作')

        # 步骤1: 异步API调用
        api_result = await unstable_async_operation()
        print(f'API调用结果: {api_result}')

        # 步骤2: 数据库查询
        db = DatabaseOperation('mysql://localhost:3306/test_db')
        db_results = db.execute_query('SELECT * FROM products')
        print(f'数据库查询结果: {db_results}')

        # 步骤3: HTTP请求
        http_response = retry_request(
            mock_http_get,
            'https://api.example.com/validate',
            max_retries=2,
            retry_on_status=[429, 500],
        )
        print(f'HTTP请求结果: {http_response.status_code}')

        return {
            'api_result': api_result,
            'db_results': db_results,
            'http_status': http_response.status_code,
        }

    try:
        # 执行复杂业务操作
        result = await complex_business_operation()
        print(f'复杂业务操作完成: {result}')
    except Exception as e:
        print(f'复杂业务操作失败: {e}')


async def main() -> None:
    """主函数"""
    print('重试机制示例程序')
    print('=' * 50)

    # 设置随机种子以保证结果可重现
    random.seed(42)

    # 执行各个示例
    await basic_retry_example()
    await async_retry_example()
    await specific_exception_retry_example()
    await result_based_retry_example()
    await http_request_retry_example()
    await future_retry_example()
    await advanced_retry_strategy_example()
    await database_operation_example()
    await combined_retry_example()

    # 重试最佳实践总结
    print('\n=== 重试机制最佳实践 ===')
    print('1. 为不稳定的操作（网络请求、数据库操作等）添加重试机制')
    print('2. 使用适当的重试次数和延迟策略，避免重试风暴')
    print('3. 对不同类型的异常设置不同的重试策略')
    print('4. 对于HTTP请求，根据状态码决定是否重试')
    print('5. 使用退避算法和随机抖动避免重试冲突')
    print('6. 对同步和异步函数分别使用对应的重试装饰器')
    print('7. 在实际业务场景中组合使用多种重试功能')


if __name__ == '__main__':
    asyncio.run(main())
