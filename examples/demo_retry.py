# !/usr/bin/env python3
"""retry.py模块示例程序

这个文件演示了xt_wraps/retry.py模块中重试机制的使用方法,包括:
- retry_wraps同步函数重试装饰器
- retry_wraps异步函数重试装饰器
- retry_request HTTP请求重试函数
- retry_future Future对象重试函数
- 不同重试策略的配置(退避算法、抖动、自定义异常等)
- 实际应用场景展示
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import random
import time

# 新增导入requests库用于真实HTTP请求测试
import requests
from xtlog import mylog

# 导入retry模块中的功能和日志模块
from nswrapslite import retry_future, retry_request, retry_wraps, spider_retry

# 配置日志级别
mylog.set_level('INFO')


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

    # 示例1: 基本HTTP请求重试(使用163.com)
    print('\n--- 基本HTTP请求重试示例 (163.com) ---')
    try:
        response1 = retry_request(
            requests.get,
            'https://www.aliyun.com',
            max_retries=3,
            delay=0.3,
        )
        # 安全地检查响应
        if response1 is not None:
            print(f'{response1.url} | 响应状态码: {response1.status_code}')
            print(f'响应内容长度: {len(response1.text)} 字符')
        else:
            print('请求失败:所有重试尝试均未成功')
    except Exception as e:
        print(f'请求失败: {e}')

    # 示例2: 测试超时重试(使用小超时时间故意触发超时)
    print('\n--- 超时重试示例 (小超时测试) ---')
    try:
        response2 = retry_request(
            requests.get,
            'https://www.sina.com.cn',
            max_retries=2,  # 减少重试次数，因为肯定会超时
            delay=0.2,
            exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError),
            timeout=0.001,  # 极短的超时时间
            verify=False,
        )
        if response2 is not None:
            print(f'{response2.url} | 响应状态码: {response2.status_code}')
        else:
            print('请求失败:所有重试尝试均超时(符合预期)')
    except Exception as e:
        print(f'请求失败: {e}')

    # 示例3: 测试方法错误(使用GET方法请求POST接口)
    print('\n--- 方法错误示例 (GET请求POST接口) ---')
    try:
        response3 = retry_request(
            requests.get,
            'https://httpbin.org/post',
            max_retries=2,
            delay=0.2,
            retry_on_status=[405],  # 即使状态码是405也重试
            verify=False,
        )
        if response3 is not None:
            print(f'{response3.url} | 响应状态码: {response3.status_code}')
            print(f'响应原因: {response3.reason}')
            print(f'响应内容: {response3.text[:100]}...')
        else:
            print('请求失败:所有重试尝试均返回405状态码')
    except Exception as e:
        print(f'请求失败: {e}')

    # 示例4: 测试不存在的域名，验证异常处理
    print('\n--- 不存在域名示例 (DNS解析失败) ---')
    try:
        response4 = retry_request(
            requests.get,
            'https://this-domain-does-not-exist-123456789.com',
            max_retries=2,
            delay=0.3,
            exceptions=(requests.exceptions.ConnectionError, requests.exceptions.Timeout),
            verify=False,
        )
        if response4 is not None:
            print(f'{response4.url} | 响应状态码: {response4.status_code}')
        else:
            print('请求失败:域名解析失败(符合预期)')
    except Exception as e:
        print(f'请求失败: {e}')

    # 示例5: 自定义重试条件和日志消息
    print('\n--- 自定义重试条件示例 ---')
    try:

        def custom_request(url, **kwargs):
            class Fake503Response:
                status_code = 503
                reason = 'Service Unavailable'
                text = '{"error": "service temporarily unavailable"}'
                headers = {}

            return Fake503Response()

        response5 = retry_request(
            custom_request,
            'https://httpbin.org/get',  # 使用更可靠的测试URL
            max_retries=3,
            delay=0.2,
            retry_on_status=[503],
            custom_message='自定义请求测试',
            verify=False,
        )
        if response5 is not None:
            print(f'响应状态码: {response5.status_code}')
            if response5.status_code == 503:
                print('模拟的503服务不可用响应')
            else:
                print('成功获取正常响应')
        else:
            print('请求失败:所有重试尝试均未成功')
    except Exception as e:
        print(f'请求失败: {e}')

    # 示例6: 使用更可靠的测试服务
    print('\n--- 可靠服务测试示例 (httpbin.org) ---')
    try:
        response6 = retry_request(
            requests.get,
            'https://httpbin.org/json',
            max_retries=2,
            delay=0.3,
        )
        if response6 is not None:
            print(f'响应状态码: {response6.status_code}')
            print(f'服务测试成功: {response6.json().get("slideshow", {}).get("title", "Unknown")}')
        else:
            print('请求失败')
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

    # 模拟HTTP响应对象(复用前面定义的)
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


def demo_spider_retry():
    """演示spider_retry爬虫专用重试装饰器的使用"""
    print('\n=== 7. spider_retry 爬虫专用重试装饰器示例 ===')

    # 示例1：同步函数的爬虫重试
    @spider_retry(max_retries=2, delay=0.5, custom_message='测试爬虫请求')
    def make_spider_request(url):
        """模拟爬虫请求函数"""
        print(f'发送请求到: {url}')
        response = requests.get(url, timeout=3)
        response.raise_for_status()  # 对于非200状态码抛出异常
        return response

    # 测试成功的请求
    print('\n--- 成功的爬虫请求示例 ---')
    result1 = make_spider_request('https://httpbin.org/get')
    print(f'请求结果1: {type(result1).__name__}({result1})')

    # 测试超时的请求
    print('\n--- 超时的爬虫请求示例 ---')
    result2 = make_spider_request('https://httpbin.org/delay/10')  # 这个接口会延迟10秒响应
    print(f'请求结果2: {type(result2).__name__}({result2})')

    # 测试404错误的请求
    print('\n--- 404错误的爬虫请求示例 ---')
    result3 = make_spider_request('https://httpbin.org/status/404')
    print(f'请求结果3: {type(result3).__name__}({result3})')

    # 示例2：使用状态码判断的爬虫重试
    @spider_retry(max_retries=3, delay=0.3, retry_on_status=[429, 500, 502, 503, 504], custom_message='带状态码判断的爬虫请求')
    def make_conditional_request(url):
        """带条件判断的爬虫请求函数"""
        try:
            print(f'  发送条件请求到: {url}')
            response = requests.get(url, timeout=2)
            # 模拟某些情况下返回None
            if random.random() < 0.3:
                print('  模拟返回None')
                return None
            return response
        except Exception as e:
            print(f'  请求异常: {e!s}')
            raise

    print('\n--- 带结果判断的爬虫请求示例 ---')
    result4 = make_conditional_request('https://httpbin.org/get')
    print(f'请求结果4: {type(result4).__name__}({result4})')


# 更新main函数，添加对demo_spider_retry的调用
async def main():
    """运行所有示例"""
    print('===== retry.py 模块示例程序 =====')

    # 运行同步示例
    # demo_retry_strategy()
    # demo_retry_wraps()
    # demo_retry_request()
    demo_spider_retry()
    # demo_real_world_scenarios()

    # 运行异步示例
    # await demo_retry_wraps_async()
    # await demo_retry_future()

    print('\n===== 所有示例运行完成 =====')


if __name__ == '__main__':
    # 如果是在__main__上下文中运行,执行主函数
    asyncio.run(main())
