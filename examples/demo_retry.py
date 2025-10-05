# !/usr/bin/env python3
"""retry.py模块示例程序

这个文件演示了xt_wraps/retry.py模块中重试机制的使用方法,包括:
- RetryStrategy类的基本使用
- retry_wraps同步函数重试装饰器
- retry_wraps异步函数重试装饰器
- retry_request HTTP请求重试函数
- retry_future Future对象重试函数
- 不同重试策略的配置（退避算法、抖动、自定义异常等）
- 实际应用场景展示
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import random
import time

from xtlog import mylog

# 导入retry模块中的功能和日志模块
from nswrapslite.retry import RetryStrategy, retry_future, retry_request, retry_wraps

# 配置日志级别
mylog.set_level('INFO')


# 1. RetryStrategy类的基本使用示例
def demo_retry_strategy():
    """演示RetryStrategy类的基本使用"""
    print('\n=== 1. RetryStrategy类的基本使用示例 ===')

    # 创建重试策略
    strategy = RetryStrategy(max_retries=5, delay=0.5, backoff=1.5, jitter=0.2, exceptions=(ConnectionError, TimeoutError), retry_on_result=lambda x: x is None)

    # 测试计算延迟
    print('计算各次重试的延迟时间:')
    for attempt in range(1, strategy.max_retries + 1):
        delay = strategy.calculate_delay(attempt)
        print(f'  第{attempt}次重试: {delay:.4f}秒')

    # 测试异常重试条件
    print('\n测试异常重试条件:')
    print(f'  ConnectionError: {strategy.should_retry_on_exception(ConnectionError("连接错误"))}')
    print(f'  TimeoutError: {strategy.should_retry_on_exception(TimeoutError("超时错误"))}')
    print(f'  ValueError: {strategy.should_retry_on_exception(ValueError("值错误"))}')

    # 测试结果重试条件
    print('\n测试结果重试条件:')
    print(f'  None: {strategy.should_retry_on_result(None)}')
    print(f'  空字符串: {strategy.should_retry_on_result("")}')
    print(f'  0: {strategy.should_retry_on_result(0)}')
    print(f"  'data': {strategy.should_retry_on_result('data')}")


# 2. retry_wraps同步函数重试装饰器示例
def demo_retry_wraps():
    """演示retry_wraps同步函数重试装饰器的使用"""
    print('\n=== 2. retry_wraps同步函数重试装饰器示例 ===')

    # 模拟不稳定的函数,前几次调用会失败
    class UnstableService:
        def __init__(self):
            self.call_count = 0

        def unstable_operation(self):
            self.call_count += 1
            print(f'  调用次数: {self.call_count}')
            if self.call_count <= 2:
                raise ConnectionError(f'服务暂时不可用 (第{self.call_count}次调用)')
            return f'操作成功 (第{self.call_count}次调用)'

        def get_data(self):
            self.call_count += 1
            print(f'  获取数据调用次数: {self.call_count}')
            if self.call_count <= 2:
                return None  # 前两次返回None,表示没有获取到数据
            return {'id': 1, 'name': '测试数据'}

    # 创建服务实例
    service = UnstableService()

    # 示例1: 基于异常的重试
    @retry_wraps(max_retries=3, delay=0.5, backoff=1.5)
    def call_unstable_service():
        return service.unstable_operation()

    # 示例2: 基于结果的重试
    @retry_wraps(max_retries=3, delay=0.3, retry_on_result=lambda x: x is None)
    def fetch_data():
        return service.get_data()

    # 示例3: 自定义异常类型和重试次数
    @retry_wraps(max_retries=2, exceptions=(ValueError, TypeError))
    def process_data(value):
        if not isinstance(value, int):
            raise TypeError('值必须是整数')
        if value < 0:
            raise ValueError('值必须是非负的')
        return value * 2

    # 运行示例
    print('\n--- 基于异常的重试示例 ---')
    try:
        result1 = call_unstable_service()
        print(f'结果: {result1}')
    except Exception as e:
        print(f'最终失败: {e}')

    # 重置调用计数
    service.call_count = 0

    print('\n--- 基于结果的重试示例 ---')
    result2 = fetch_data()
    print(f'结果: {result2}')

    print('\n--- 自定义异常类型示例 ---')
    try:
        # 这应该成功
        result3 = process_data(10)
        print(f'处理正整数结果: {result3}')

        # 这应该抛出ValueError并重试,但只重试2次
        process_data(-5)
    except ValueError as e:
        print(f'捕获到预期的ValueError: {e}')

    try:
        # 这应该抛出TypeError并重试
        process_data('not a number')
    except TypeError as e:
        print(f'捕获到预期的TypeError: {e}')


# 3. retry_wraps异步函数重试装饰器示例
async def demo_retry_wraps_async():
    """演示retry_wraps异步函数重试装饰器的使用"""
    print('\n=== 3. retry_wraps异步函数重试装饰器示例 ===')

    # 模拟不稳定的异步服务
    class AsyncUnstableService:
        def __init__(self):
            self.call_count = 0

        async def unstable_operation(self):
            self.call_count += 1
            print(f'  异步调用次数: {self.call_count}')
            await asyncio.sleep(0.1)  # 模拟网络延迟
            if self.call_count <= 2:
                raise ConnectionError(f'异步服务暂时不可用 (第{self.call_count}次调用)')
            return f'异步操作成功 (第{self.call_count}次调用)'

        async def fetch_data_async(self):
            self.call_count += 1
            print(f'  异步获取数据次数: {self.call_count}')
            await asyncio.sleep(0.1)
            if self.call_count <= 2:
                return None  # 前两次返回None
            return ['item1', 'item2', 'item3']

    # 创建异步服务实例
    async_service = AsyncUnstableService()

    # 示例1: 异步函数异常重试
    @retry_wraps(max_retries=3, delay=0.4, backoff=2.0, jitter=0.1)
    async def call_async_service():
        return await async_service.unstable_operation()

    # 示例2: 异步函数结果重试
    @retry_wraps(max_retries=3, delay=0.3, retry_on_result=lambda x: x is None)
    async def get_async_data():
        return await async_service.fetch_data_async()

    # 运行示例
    print('\n--- 异步函数异常重试示例 ---')
    try:
        result1 = await call_async_service()
        print(f'结果: {result1}')
    except Exception as e:
        print(f'最终失败: {e}')

    # 重置调用计数
    async_service.call_count = 0

    print('\n--- 异步函数结果重试示例 ---')
    result2 = await get_async_data()
    print(f'结果: {result2}')


# 4. retry_request HTTP请求重试函数示例
def demo_retry_request():
    """演示retry_request HTTP请求重试函数的使用"""
    print('\n=== 4. retry_request HTTP请求重试函数示例 ===')

    # 模拟HTTP请求函数
    class MockHttpClient:
        def __init__(self):
            self.request_count = 0

        def get(self, url, **kwargs):
            self.request_count += 1
            print(f'  HTTP GET 请求次数: {self.request_count}, URL: {url}')

            # 模拟不同的响应情况
            if self.request_count <= 2:
                # 前两次返回503服务不可用
                return MockResponse(503, 'Service Unavailable')
            if url == 'https://api.example.com/error':
                # 特定URL总是返回错误
                return MockResponse(404, 'Not Found')
            # 成功响应
            return MockResponse(200, 'OK', {'data': 'success'})

    # 模拟HTTP响应对象
    class MockResponse:
        def __init__(self, status_code, reason, data=None):
            self.status_code = status_code
            self.reason = reason
            self.data = data or {}

        def json(self):
            return self.data

        def __str__(self):
            return f'Response({self.status_code}, {self.reason})'

    # 创建模拟HTTP客户端
    http_client = MockHttpClient()

    # 示例1: 基本HTTP请求重试
    print('\n--- 基本HTTP请求重试示例 ---')
    try:
        response1 = retry_request(http_client.get, 'https://api.example.com/data', max_retries=3, delay=0.3, retry_on_status=[500, 502, 503, 504, 429])
        print(f'响应状态码: {response1.status_code}')
        print(f'响应数据: {response1.json()}')
    except Exception as e:
        print(f'请求失败: {e}')

    # 重置请求计数
    http_client.request_count = 0

    # 示例2: 带有超时和自定义异常的HTTP请求
    print('\n--- 带超时和自定义异常的HTTP请求示例 ---')
    try:
        # 模拟请求函数可能抛出超时异常
        def http_get_with_possible_timeout(url, **kwargs):
            if random.random() < 0.3:
                raise TimeoutError('请求超时')
            return http_client.get(url, **kwargs)

        response2 = retry_request(http_get_with_possible_timeout, 'https://api.example.com/data', max_retries=3, delay=0.2, exceptions=(ConnectionError, TimeoutError), retry_on_status=[503])
        print(f'响应状态码: {response2.status_code}')
    except Exception as e:
        print(f'请求失败: {e}')


# 5. retry_future Future对象重试函数示例
async def demo_retry_future():
    """演示retry_future Future对象重试函数的使用"""
    print('\n=== 5. retry_future Future对象重试函数示例 ===')

    # 创建线程池执行器
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # 模拟不稳定的同步函数
        class FutureBasedService:
            def __init__(self):
                self.call_count = 0

            def unstable_task(self):
                self.call_count += 1
                print(f'  Future任务调用次数: {self.call_count}')
                time.sleep(0.1)  # 模拟耗时操作
                if self.call_count <= 2:
                    raise RuntimeError(f'任务执行失败 (第{self.call_count}次调用)')
                return f'Future任务成功 (第{self.call_count}次调用)'

            def generate_result(self):
                self.call_count += 1
                print(f'  生成结果调用次数: {self.call_count}')
                time.sleep(0.1)
                if self.call_count <= 2:
                    return 'invalid'  # 前两次返回无效结果
                return 'valid_data'

        # 创建服务实例
        future_service = FutureBasedService()

        # 示例1: 基于异常的Future重试
        print('\n--- 基于异常的Future重试示例 ---')
        try:
            # 创建Future工厂函数
            def future_factory():
                return executor.submit(future_service.unstable_task)

            # 使用retry_future重试Future操作
            result1 = await retry_future(future_factory, max_retries=3, delay=0.3, backoff=1.5)
            print(f'结果: {result1}')
        except Exception as e:
            print(f'最终失败: {e}')

        # 重置调用计数
        future_service.call_count = 0

        # 示例2: 基于结果的Future重试
        print('\n--- 基于结果的Future重试示例 ---')
        try:

            def result_factory():
                # 对于演示,我们直接返回结果,而不是真正的Future
                # 在实际使用中,这里应该返回一个Future对象
                return future_service.generate_result()

            result2 = await retry_future(result_factory, max_retries=3, delay=0.2, retry_on_result=lambda x: x == 'invalid')
            print(f'结果: {result2}')
        except Exception as e:
            print(f'最终失败: {e}')


# 6. 实际应用场景示例
def demo_real_world_scenarios():
    """演示retry模块在实际应用场景中的使用"""
    print('\n=== 6. 实际应用场景示例 ===')

    # 场景1: 数据库连接重试
    print('\n--- 数据库连接重试示例 ---')

    class DatabaseConnection:
        def __init__(self):
            self.connect_count = 0

        def connect(self):
            self.connect_count += 1
            print(f'  数据库连接尝试次数: {self.connect_count}')
            # 模拟前两次连接失败
            if self.connect_count <= 2:
                raise ConnectionError('数据库连接失败: 连接超时')
            print('  数据库连接成功')
            return {'status': 'connected', 'connection_id': f'conn_{self.connect_count}'}

    db = DatabaseConnection()

    @retry_wraps(max_retries=3, delay=0.5, backoff=2.0, exceptions=(ConnectionError, TimeoutError), retry_on_result=lambda x: x.get('status', '') != 'connected')
    def establish_db_connection():
        return db.connect()

    try:
        connection = establish_db_connection()
        print(f'数据库连接结果: {connection}')
    except Exception as e:
        print(f'数据库连接最终失败: {e}')

    # 场景2: 外部API调用重试
    print('\n--- 外部API调用重试示例 ---')

    class ExternalApiClient:
        def __init__(self):
            self.call_count = 0

        def make_api_call(self, endpoint, **params):
            self.call_count += 1
            print(f'  API调用尝试次数: {self.call_count}, 端点: {endpoint}')

            # 模拟不同的失败情况
            if self.call_count == 1:
                raise ConnectionError('网络连接问题')
            if self.call_count == 2:
                # 模拟返回429 Too Many Requests
                return MockResponse(429, 'Too Many Requests')
            if self.call_count == 3:
                # 模拟返回503 Service Unavailable
                return MockResponse(503, 'Service Unavailable')
            # 成功响应
            return MockResponse(200, 'OK', {'data': f'来自{endpoint}的数据'})

    api_client = ExternalApiClient()

    # 模拟HTTP响应对象（复用前面定义的）
    class MockResponse:
        def __init__(self, status_code, reason, data=None):
            self.status_code = status_code
            self.reason = reason
            self.data = data or {}

        def json(self):
            return self.data

    # 使用retry_request处理API调用
    try:
        response = retry_request(
            api_client.make_api_call,
            'users/profile',
            user_id=123,
            max_retries=5,
            delay=0.3,
            backoff=1.5,
            jitter=0.1,
            exceptions=(ConnectionError, TimeoutError),
            retry_on_status=[429, 500, 502, 503, 504],
        )
        print(f'API调用结果: {response.json()}')
    except Exception as e:
        print(f'API调用最终失败: {e}')


# 主函数
async def main():
    """运行所有示例"""
    print('===== retry.py 模块示例程序 =====')

    # 运行同步示例
    demo_retry_strategy()
    demo_retry_wraps()
    demo_retry_request()
    demo_real_world_scenarios()

    # 运行异步示例
    await demo_retry_wraps_async()
    await demo_retry_future()

    print('\n===== 所有示例运行完成 =====')


if __name__ == '__main__':
    # 如果是在__main__上下文中运行,执行主函数
    asyncio.run(main())
