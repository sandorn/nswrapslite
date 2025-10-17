# !/usr/bin/env python3
"""
xt_wraps.tenacityretry模块示例程序
本示例演示如何使用tenacityretry模块中的重试功能
包括：同步函数重试、异步函数重试、自定义重试策略和异常处理
"""
from __future__ import annotations

import asyncio
import random
import time
from typing import Any

from xtlog import mylog

from nswrapslite.tenacityretry import retry_wraps_tenacity

# 配置日志级别
mylog.set_level('INFO')


def demo_basic_retry():
    """演示基本的同步函数重试功能"""
    print("\n=== 演示基本的同步函数重试功能 ===")
    
    # 模拟一个不稳定的网络请求函数
    class UnstableNetworkService:
        def __init__(self, fail_rate: float = 0.7):
            """初始化不稳定的网络服务
            
            Args:
                fail_rate: 失败概率
            """
            self.fail_rate = fail_rate
            self.call_count = 0
        
        @retry_wraps_tenacity
        def fetch_data(self, url: str) -> dict[str, Any]:
            """获取数据，默认配置（3次重试，随机等待0-1秒）"""
            self.call_count += 1
            print(f"执行请求: {url}, 调用次数: {self.call_count}")
            
            # 随机失败
            if random.random() < self.fail_rate:
                error_msg = f"请求 {url} 失败"
                print(f"{error_msg}，将重试...")
                raise ConnectionError(error_msg)
            
            # 模拟网络延迟
            time.sleep(0.2)
            
            # 成功响应
            return {
                "url": url,
                "status": 200,
                "data": f"从 {url} 获取的数据",
                "timestamp": time.time()
            }
    
    # 测试基本重试功能
    service = UnstableNetworkService(fail_rate=0.7)
    
    print("\n调用不稳定的网络请求函数:")
    try:
        result = service.fetch_data("https://api.example.com/data")
        print(f"请求成功，结果: {result}")
        print(f"总共调用了 {service.call_count} 次")
    except Exception as e:
        print(f"达到最大重试次数，请求失败: {e}")
        print(f"总共调用了 {service.call_count} 次")


def demo_custom_retry_config():
    """演示自定义重试配置"""
    print("\n=== 演示自定义重试配置 ===")
    
    # 1. 自定义重试次数和等待时间
    @retry_wraps_tenacity(
        max_attempts=5,        # 最大重试5次
        min_wait=0.5,          # 最小等待时间0.5秒
        max_wait=2.0           # 最大等待时间2.0秒
    )
    def unstable_operation(operation_id: int) -> str:
        """不稳定的操作，配置了自定义的重试参数"""
        print(f"执行操作 {operation_id}，当前时间: {time.strftime('%H:%M:%S')}")
        
        # 随机失败
        if random.random() < 0.6:
            error_msg = f"操作 {operation_id} 随机失败"
            print(f"{error_msg}，将重试...")
            raise TimeoutError(error_msg)
        
        return f"操作 {operation_id} 成功完成"
    
    # 2. 自定义重试异常类型
    @retry_wraps_tenacity(
        retry_exceptions=(ConnectionError, TimeoutError),  # 只对特定异常重试
        max_attempts=3
    )
    def specific_exception_retry(operation: str) -> str:
        """只对特定异常进行重试"""
        print(f"执行特定异常重试操作: {operation}")
        
        if operation == "network":
            raise ConnectionError("网络连接失败")
        if operation == "timeout":
            raise TimeoutError("操作超时")
        if operation == "value":
            raise ValueError("值错误，不会重试")
        
        return f"操作 {operation} 成功"
    
    # 3. 设置默认返回值
    @retry_wraps_tenacity(
        max_attempts=3,
        default_return={"status": "failed", "message": "操作无法完成"}  # 重试失败时的默认返回值
    )
    def function_with_default_return(param: str) -> dict[str, Any]:
        """设置了默认返回值的函数"""
        print(f"执行带默认返回值的函数，参数: {param}")
        
        # 总是失败，测试默认返回值
        raise RuntimeError(f"函数执行失败，参数: {param}")
    
    # 测试自定义重试次数和等待时间
    print("\n测试自定义重试次数和等待时间 (观察时间间隔):")
    try:
        result = unstable_operation(1)
        print(f"操作结果: {result}")
    except Exception as e:
        print(f"达到最大重试次数: {e}")
    
    # 测试自定义重试异常类型
    print("\n测试自定义重试异常类型:")
    test_operations = ["network", "timeout", "value", "success"]
    for op in test_operations:
        print(f"\n测试操作: {op}")
        try:
            result = specific_exception_retry(op)
            print(f"结果: {result}")
        except Exception as e:
            print(f"未重试的异常: {type(e).__name__}: {e}")
    
    # 测试默认返回值
    print("\n测试默认返回值:")
    result = function_with_default_return("test_param")
    print(f"函数返回: {result}")


def demo_async_retry():
    """演示异步函数重试功能"""
    print("\n=== 演示异步函数重试功能 ===")
    
    # 模拟一个不稳定的异步网络服务
    class AsyncUnstableNetworkService:
        def __init__(self, fail_rate: float = 0.7):
            """初始化异步不稳定网络服务
            
            Args:
                fail_rate: 失败概率
            """
            self.fail_rate = fail_rate
            self.call_count = 0
        
        @retry_wraps_tenacity(
            max_attempts=4,
            min_wait=0.3,
            max_wait=1.0
        )
        async def fetch_data_async(self, url: str) -> dict[str, Any]:
            """异步获取数据，支持重试"""
            self.call_count += 1
            print(f"异步执行请求: {url}, 调用次数: {self.call_count}")
            
            # 模拟网络延迟
            await asyncio.sleep(0.2)
            
            # 随机失败
            if random.random() < self.fail_rate:
                error_msg = f"异步请求 {url} 失败"
                print(f"{error_msg}，将重试...")
                raise ConnectionError(error_msg)
            
            # 成功响应
            return {
                "url": url,
                "status": 200,
                "data": f"从 {url} 异步获取的数据",
                "timestamp": time.time(),
                "call_count": self.call_count
            }
    
    # 测试异步重试功能
    async def test_async_retry():
        service = AsyncUnstableNetworkService(fail_rate=0.7)
        
        print("\n调用不稳定的异步网络请求函数:")
        try:
            result = await service.fetch_data_async("https://api.example.com/async/data")
            print(f"异步请求成功，结果: {result}")
            print(f"总共调用了 {service.call_count} 次")
        except Exception as e:
            print(f"达到最大重试次数，异步请求失败: {e}")
            print(f"总共调用了 {service.call_count} 次")
        
        # 测试带默认返回值的异步函数
        @retry_wraps_tenacity(
            max_attempts=2,
            default_return={"status": "failed", "async": True}
        )
        async def async_function_with_default() -> dict[str, Any]:
            """带默认返回值的异步函数"""
            print("执行带默认返回值的异步函数")
            await asyncio.sleep(0.1)
            raise RuntimeError("异步函数故意失败")
        
        print("\n测试带默认返回值的异步函数:")
        result = await async_function_with_default()
        print(f"异步函数返回: {result}")
    
    # 运行异步测试
    asyncio.run(test_async_retry())


def demo_practical_applications():
    """演示实际应用中的重试场景"""
    print("\n=== 演示实际应用中的重试场景 ===")
    
    try:
        import requests
        from requests.exceptions import RequestException
        
        # 1. HTTP请求重试
        @retry_wraps_tenacity(
            max_attempts=3,
            min_wait=1.0,
            max_wait=2.0,
            retry_exceptions=(RequestException, ConnectionError, TimeoutError)
        )
        def http_get_request(url: str, timeout: int = 5) -> dict[str, Any]:
            """HTTP GET请求，支持重试"""
            print(f"发送HTTP GET请求到: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # 抛出HTTP错误
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": len(response.content),
                "url": url
            }
        
        # 2. 数据库操作重试
        class DatabaseOperation:
            def __init__(self):
                """初始化数据库操作类"""
                self.retry_count = 0
                self.fail_count = 2  # 前两次操作失败
            
            @retry_wraps_tenacity(
                max_attempts=3,
                min_wait=0.5,
                max_wait=1.5,
                retry_exceptions=(ConnectionError, TimeoutError)
            )
            def execute_database_query(self, query: str) -> list[dict[str, Any]]:
                """执行数据库查询，支持重试"""
                self.retry_count += 1
                print(f"执行数据库查询: {query[:30]}..., 尝试次数: {self.retry_count}")
                
                # 模拟数据库操作延迟
                time.sleep(0.3)
                
                # 模拟前几次失败
                if self.retry_count <= self.fail_count:
                    error_type = random.choice([ConnectionError, TimeoutError])
                    error_msg = f"数据库操作失败 (尝试 {self.retry_count}/{self.fail_count + 1})"
                    print(f"{error_type.__name__}: {error_msg}")
                    raise error_type(error_msg)
                
                # 模拟成功结果
                print("数据库查询成功")
                return [
                    {"id": 1, "name": "用户1", "email": "user1@example.com"},
                    {"id": 2, "name": "用户2", "email": "user2@example.com"}
                ]
        
        # 创建一个模拟的HTTP服务类
        class MockHTTPService:
            def __init__(self):
                """初始化模拟HTTP服务"""
                self.call_count = 0
                self.fail_count = 1  # 前1次请求失败
            
            @retry_wraps_tenacity(
                max_attempts=3,
                default_return={"status": "failed", "mock": True}
            )
            def mock_http_request(self, endpoint: str) -> dict[str, Any]:
                """模拟HTTP请求"""
                self.call_count += 1
                print(f"模拟HTTP请求到: {endpoint}, 调用次数: {self.call_count}")
                
                # 模拟网络延迟
                time.sleep(0.3)
                
                # 模拟前几次失败
                if self.call_count <= self.fail_count:
                    error_code = random.choice([408, 500, 502, 503, 504])
                    print(f"请求失败，模拟状态码: {error_code}")
                    raise RequestException(f"模拟HTTP错误，状态码: {error_code}")
                
                # 模拟成功响应
                print("请求成功")
                return {
                    "status_code": 200,
                    "endpoint": endpoint,
                    "data": f"来自 {endpoint} 的数据",
                    "timestamp": time.time()
                }
        
        # 测试数据库操作重试
        print("\n测试数据库操作重试:")
        db_op = DatabaseOperation()
        try:
            results = db_op.execute_database_query("SELECT * FROM users WHERE active = true")
            print(f"查询结果行数: {len(results)}")
        except Exception as e:
            print(f"数据库操作失败: {e}")
        
        # 测试模拟HTTP请求重试
        print("\n测试模拟HTTP请求重试:")
        mock_http = MockHTTPService()
        result = mock_http.mock_http_request("/api/users")
        print(f"模拟HTTP请求结果: {result}")
        
        # 注意：实际HTTP请求可能会超时或连接失败，这里为了演示不实际发送请求
        print("\n注意: 为了避免实际网络请求，这里不执行真实的HTTP请求示例")
        print("在实际应用中，您可以使用http_get_request函数发送真实的HTTP请求")
        
        # 展示http_get_request函数的使用方式
        print("\nhttp_get_request函数使用示例:")
        print("# response = http_get_request('https://api.github.com')")
        print("# print(response)")
    except ImportError:
        print("\n警告: 未安装requests库，无法演示HTTP请求重试功能")
        print("请安装requests库: pip install requests")


def demo_retry_with_different_exceptions():
    """演示对不同类型异常的重试处理"""
    print("\n=== 演示对不同类型异常的重试处理 ===")
    
    # 定义一个会抛出不同类型异常的函数
    class ExceptionGenerator:
        def __init__(self):
            """初始化异常生成器"""
            self.call_sequence = []
        
        def generate_exception(self, exception_type: str) -> None:
            """生成指定类型的异常
            
            Args:
                exception_type: 异常类型名称
            """
            self.call_sequence.append(exception_type)
            
            if exception_type == "connection":
                raise ConnectionError("连接错误")
            if exception_type == "timeout":
                raise TimeoutError("超时错误")
            if exception_type == "value":
                raise ValueError("值错误")
            if exception_type == "key":
                raise KeyError("键错误")
            if exception_type == "index":
                raise IndexError("索引错误")
            if exception_type == "runtime":
                raise RuntimeError("运行时错误")
            
    # 测试不同异常类型的重试配置
    
    # 1. 只对连接和超时异常重试
    @retry_wraps_tenacity(
        retry_exceptions=(ConnectionError, TimeoutError),
        max_attempts=2,
        default_return="重试失败"
    )
    def handle_network_exceptions(generator: ExceptionGenerator, exception_type: str) -> str:
        """只处理网络相关异常"""
        generator.generate_exception(exception_type)
        return "成功处理"
    
    # 2. 对所有标准异常重试
    @retry_wraps_tenacity(
        retry_exceptions=(Exception,),
        max_attempts=2,
        default_return="全局异常重试失败"
    )
    def handle_all_exceptions(generator: ExceptionGenerator, exception_type: str) -> str:
        """处理所有标准异常"""
        generator.generate_exception(exception_type)
        return "成功处理"
    
    # 测试异常处理
    print("\n测试只对网络异常的重试处理:")
    
    generator = ExceptionGenerator()
    
    test_exceptions = [
        "connection", "timeout", "value", "key", "runtime"
    ]
    
    for exc_type in test_exceptions:
        print(f"\n测试异常类型: {exc_type}")
        result = handle_network_exceptions(generator, exc_type)
        print(f"结果: {result}")
    
    print(f"\n调用序列: {generator.call_sequence}")
    
    # 重置调用序列
    generator.call_sequence = []
    
    print("\n测试对所有标准异常的重试处理:")
    
    for exc_type in test_exceptions:
        print(f"\n测试异常类型: {exc_type}")
        result = handle_all_exceptions(generator, exc_type)
        print(f"结果: {result}")
    
    print(f"\n调用序列: {generator.call_sequence}")


def demo_retry_in_concurrent_environment():
    """演示在并发环境中使用重试装饰器"""
    print("\n=== 演示在并发环境中使用重试装饰器 ===")
    
    # 模拟一个共享资源服务
    class SharedResourceService:
        def __init__(self):
            """初始化共享资源服务"""
            self.current_users = 0
            self.max_concurrent = 2
            self.lock = asyncio.Lock()  # 使用异步锁
            self.call_count = 0
        
        @retry_wraps_tenacity(
            max_attempts=3,
            min_wait=0.2,
            max_wait=0.5,
            retry_exceptions=(ResourceWarning,)
        )
        async def access_shared_resource(self, user_id: int) -> dict[str, Any]:
            """访问共享资源，限制并发访问"""
            self.call_count += 1
            print(f"用户 {user_id} 尝试访问共享资源 (调用 #{self.call_count})")
            
            # 使用异步锁控制并发访问
            async with self.lock:
                # 检查并发用户数
                if self.current_users >= self.max_concurrent:
                    # 当并发用户达到上限时，抛出异常触发重试
                    error_msg = f"用户 {user_id}：共享资源忙，当前用户数: {self.current_users}"
                    print(error_msg)
                    raise ResourceWarning(error_msg)
                
                # 增加当前用户数
                self.current_users += 1
            
            try:
                # 模拟使用共享资源
                print(f"用户 {user_id} 成功访问共享资源，当前用户数: {self.current_users}")
                await asyncio.sleep(random.uniform(0.1, 0.5))  # 模拟资源使用时间
                
                # 模拟可能的失败
                if random.random() < 0.2:
                    raise ConnectionError(f"用户 {user_id}：资源访问中断")
                
                # 返回成功结果
                return {
                    "user_id": user_id,
                    "success": True,
                    "current_users": self.current_users,
                    "timestamp": time.time()
                }
            finally:
                # 释放资源，减少当前用户数
                async with self.lock:
                    self.current_users -= 1
                    print(f"用户 {user_id} 释放共享资源，当前用户数: {self.current_users}")
    
    # 并发测试函数
    async def test_concurrent_access():
        service = SharedResourceService()
        
        # 创建10个并发任务
        tasks = []
        for user_id in range(10):
            task = asyncio.create_task(
                service.access_shared_resource(user_id)
            )
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        error_count = sum(1 for r in results if isinstance(r, Exception))
        
        print("\n并发访问结果统计:")
        print(f"- 总任务数: {len(tasks)}")
        print(f"- 成功任务数: {success_count}")
        print(f"- 失败任务数: {error_count}")
        print(f"- 总调用次数: {service.call_count}")
    
    # 运行并发测试
    asyncio.run(test_concurrent_access())


def main():
    """主函数，运行所有演示"""
    print("===== xt_wraps.tenacityretry模块示例程序 =====")
    
    # 基本功能演示
    demo_basic_retry()
    demo_custom_retry_config()
    demo_async_retry()
    
    # 实际应用场景
    demo_practical_applications()
    
    # 高级功能演示
    demo_retry_with_different_exceptions()
    demo_retry_in_concurrent_environment()
    
    print("\n===== 示例程序运行完毕 =====")


if __name__ == "__main__":
    main()