# !/usr/bin/env python3
"""
xt_wraps.strategy模块示例程序
本示例演示如何使用strategy模块中的装饰器基类创建自定义装饰器
包括：基础装饰器继承、同步/异步装饰器实现、组合装饰器等
"""
from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Any

from xtlog import mylog

from nswrapslite.strategy import AsyncFunctionWrapper, SyncFunctionWrapper, TimerStrategy, UniversalFunctionWrapper

# 配置日志级别
mylog.set_level('INFO')


def demo_base_wrapper_usage():
    """演示基础装饰器基类的使用"""
    print("\n=== 演示基础装饰器基类的使用 ===")
    
    # 创建一个继承自UniversalFunctionWrapper的自定义装饰器
    class LoggingWrapper(UniversalFunctionWrapper):
        """简单的日志记录装饰器"""
        
        def __init__(self, prefix: str = ""):
            """初始化日志装饰器
            
            Args:
                prefix: 日志前缀
            """
            super().__init__(prefix=prefix)
            self.prefix = prefix
        
        def _execute_sync(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """执行同步函数并记录日志"""
            print(f"{self.prefix}[同步] 开始执行: {func.__name__}")
            result = super()._execute_sync(func, args, kwargs)
            print(f"{self.prefix}[同步] 执行完成: {func.__name__}")
            return result
        
        async def _execute_async(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """执行异步函数并记录日志"""
            print(f"{self.prefix}[异步] 开始执行: {func.__name__}")
            result = await super()._execute_async(func, args, kwargs)
            print(f"{self.prefix}[异步] 执行完成: {func.__name__}")
            return result
    
    # 使用自定义装饰器
    @LoggingWrapper("[业务逻辑]")
    def process_data(data: list[int]) -> int:
        """处理数据的同步函数"""
        time.sleep(0.5)  # 模拟耗时操作
        return sum(data)
    
    @LoggingWrapper("[API调用]")
    async def fetch_data(url: str) -> dict[str, Any]:
        """获取数据的异步函数"""
        await asyncio.sleep(0.5)  # 模拟网络延迟
        return {"url": url, "data": f"来自{url}的数据", "timestamp": time.time()}
    
    # 测试同步函数
    result1 = process_data([1, 2, 3, 4, 5])
    print(f"同步函数结果: {result1}")
    
    # 测试异步函数
    async def test_async():
        result2 = await fetch_data("https://example.com")
        print(f"异步函数结果: {result2}")
    
    asyncio.run(test_async())


def demo_sync_function_wrapper():
    """演示同步函数装饰器基类的使用"""
    print("\n=== 演示同步函数装饰器基类的使用 ===")
    
    # 创建一个继承自SyncFunctionWrapper的装饰器
    class CacheWrapper(SyncFunctionWrapper):
        """简单的缓存装饰器，仅支持同步函数"""
        
        def __init__(self):
            """初始化缓存装饰器"""
            super().__init__()
            self.cache = {}
        
        def _execute_sync(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """执行同步函数并缓存结果"""
            # 创建缓存键
            cache_key = (func.__name__, args, frozenset(kwargs.items()))
            
            # 检查缓存
            if cache_key in self.cache:
                print(f"[缓存命中] {func.__name__}")
                return self.cache[cache_key]
            
            # 执行函数并缓存结果
            print(f"[缓存未命中] {func.__name__}")
            result = func(*args, **kwargs)
            self.cache[cache_key] = result
            return result
    
    # 创建缓存装饰器实例
    cache_decorator = CacheWrapper()
    
    # 应用装饰器
    @cache_decorator
    def expensive_calculation(a: int, b: int) -> int:
        """模拟耗时计算"""
        print(f"执行计算: {a} + {b}")
        time.sleep(0.8)  # 模拟耗时操作
        return a + b
    
    # 测试缓存功能
    print("第一次调用:")
    start_time = time.time()
    result1 = expensive_calculation(5, 3)
    end_time = time.time()
    print(f"结果: {result1}, 耗时: {end_time - start_time:.2f}秒")
    
    print("\n第二次调用相同参数(应该命中缓存):")
    start_time = time.time()
    result2 = expensive_calculation(5, 3)
    end_time = time.time()
    print(f"结果: {result2}, 耗时: {end_time - start_time:.2f}秒")
    
    print("\n调用不同参数(应该不命中缓存):")
    start_time = time.time()
    result3 = expensive_calculation(10, 20)
    end_time = time.time()
    print(f"结果: {result3}, 耗时: {end_time - start_time:.2f}秒")
    
    # 测试异步函数（应该抛出异常）
    try:
        @cache_decorator
        async def async_function():
            pass
    except TypeError as e:
        print(f"\n预期的异常: {e}")


def demo_async_function_wrapper():
    """演示异步函数装饰器基类的使用"""
    print("\n=== 演示异步函数装饰器基类的使用 ===")
    
    # 创建一个继承自AsyncFunctionWrapper的装饰器
    class RetryAsyncWrapper(AsyncFunctionWrapper):
        """异步重试装饰器，仅支持异步函数"""
        
        def __init__(self, max_retries: int = 3, delay: float = 0.5):
            """初始化重试装饰器
            
            Args:
                max_retries: 最大重试次数
                delay: 重试间隔（秒）
            """
            super().__init__(max_retries=max_retries, delay=delay)
            self.max_retries = max_retries
            self.delay = delay
        
        async def _execute_async(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """执行异步函数并在失败时重试"""
            retries = 0
            
            while retries <= self.max_retries:
                try:
                    if retries > 0:
                        print(f"第 {retries} 次重试 {func.__name__}")
                        await asyncio.sleep(self.delay)  # 等待一段时间后重试
                    
                    return await func(*args, **kwargs)
                except Exception:
                    retries += 1
                    if retries > self.max_retries:
                        print(f"达到最大重试次数 {self.max_retries}，操作失败")
                        raise
            return None
        
    # 创建重试装饰器实例
    retry_decorator = RetryAsyncWrapper(max_retries=3, delay=0.3)
    
    # 模拟一个不稳定的异步函数
    class UnstableService:
        def __init__(self, fail_times: int = 2):
            self.fail_times = fail_times
            self.call_count = 0
        
        @retry_decorator
        async def fetch_data(self, id: int) -> dict[str, Any]:
            """模拟不稳定的API调用"""
            self.call_count += 1
            print(f"调用服务获取数据: id={id}, 调用次数={self.call_count}")
            
            # 前几次调用失败
            if self.call_count <= self.fail_times:
                raise ConnectionError(f"服务暂时不可用 (第{self.call_count}次调用)")
            
            # 成功调用
            await asyncio.sleep(0.2)  # 模拟网络延迟
            return {"id": id, "data": f"数据{id}", "timestamp": time.time()}
    
    # 测试重试功能
    async def test_retry():
        service = UnstableService(fail_times=2)
        
        try:
            # 这个调用会失败2次，然后成功
            result = await service.fetch_data(1)
            print(f"最终获取数据成功: {result}")
        except Exception as e:
            print(f"最终获取数据失败: {e}")
        
        # 重置调用计数，测试同步函数（应该抛出异常）
        try:
            @retry_decorator
            def sync_function():
                pass
        except TypeError as e:
            print(f"预期的异常: {e}")
    
    asyncio.run(test_retry())


def demo_timer_strategy():
    """演示TimerStrategy装饰器的使用"""
    print("\n=== 演示TimerStrategy装饰器的使用 ===")
    
    # 创建不同配置的TimerStrategy装饰器
    # 1. 默认配置
    default_timer = TimerStrategy()
    
    # 2. 详细日志配置，记录参数和结果
    detailed_timer = TimerStrategy(log_args=True, log_result=True)
    
    # 3. 自定义日志级别
    debug_timer = TimerStrategy(log_level='DEBUG')
    
    # 应用默认计时器装饰器到同步函数
    @default_timer
    def process_batch(data: list[int]) -> dict[str, Any]:
        """处理一批数据"""
        time.sleep(0.6)  # 模拟耗时操作
        return {
            'sum': sum(data),
            'count': len(data),
            'average': sum(data) / len(data) if data else 0
        }
    
    # 应用详细计时器装饰器到同步函数
    @detailed_timer
    def calculate_factorial(n: int) -> int:
        """计算阶乘"""
        time.sleep(0.4)  # 模拟耗时操作
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    # 应用调试级别计时器装饰器到异步函数
    @debug_timer
    async def download_file(url: str, size_mb: float) -> dict[str, Any]:
        """模拟下载文件"""
        print(f"开始下载 {url}，大小 {size_mb}MB")
        # 模拟下载时间（假设下载速度为10MB/s）
        download_time = size_mb / 10
        await asyncio.sleep(download_time)
        return {
            'url': url,
            'size_mb': size_mb,
            'status': 'completed',
            'timestamp': time.time()
        }
    
    # 测试同步函数
    print("测试默认计时器...")
    result1 = process_batch([1, 2, 3, 4, 5])
    print(f"处理结果: {result1}")
    
    print("\n测试详细日志计时器...")
    result2 = calculate_factorial(5)
    print(f"阶乘结果: {result2}")
    
    # 测试异步函数
    async def test_async_timers():
        print("\n测试调试级别计时器（异步）...")
        result3 = await download_file("https://example.com/file.zip", 2.5)
        print(f"下载结果: {result3}")
        
        # 测试异常情况
        try:
            @default_timer
            async def failing_operation():
                await asyncio.sleep(0.2)
                raise ValueError("模拟操作失败")
            
            await failing_operation()
        except ValueError as e:
            print(f"预期的异常被捕获: {e}")
    
    asyncio.run(test_async_timers())


def demo_custom_strategy_implementation():
    """演示自定义策略装饰器的实现与组合"""
    print("\n=== 演示自定义策略装饰器的实现与组合 ===")
    
    # 创建一个参数验证装饰器
    class ValidationWrapper(UniversalFunctionWrapper):
        """参数验证装饰器"""
        
        def __init__(self, **validators):
            """初始化验证装饰器
            
            Args:
                **validators: 参数名到验证函数的映射
            """
            super().__init__(validators=validators)
            self.validators = validators
        
        def _execute_sync(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """验证同步函数参数并执行"""
            self._validate_args(func, args, kwargs)
            return super()._execute_sync(func, args, kwargs)
        
        async def _execute_async(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """验证异步函数参数并执行"""
            self._validate_args(func, args, kwargs)
            return await super()._execute_async(func, args, kwargs)
        
        def _validate_args(self, func: Callable, args: tuple, kwargs: dict) -> None:
            """验证函数参数
            
            Args:
                func: 被装饰的函数
                args: 位置参数
                kwargs: 关键字参数
                
            Raises:
                ValueError: 当参数验证失败时
            """
            # 获取函数参数信息
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 验证参数
            for param_name, validator in self.validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(f"参数验证失败: {param_name}={value}")
    
    # 创建一个权限检查装饰器
    class AuthorizationWrapper(UniversalFunctionWrapper):
        """权限检查装饰器"""
        
        def __init__(self, required_permission: str):
            """初始化权限检查装饰器
            
            Args:
                required_permission: 所需的权限
            """
            super().__init__(required_permission=required_permission)
            self.required_permission = required_permission
        
        def _execute_sync(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """检查同步函数权限并执行"""
            self._check_permission(kwargs.get('user', {}))
            return super()._execute_sync(func, args, kwargs)
        
        async def _execute_async(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """检查异步函数权限并执行"""
            self._check_permission(kwargs.get('user', {}))
            return await super()._execute_async(func, args, kwargs)
        
        def _check_permission(self, user: dict[str, Any]) -> None:
            """检查用户权限
            
            Args:
                user: 用户信息字典
                
            Raises:
                PermissionError: 当用户没有所需权限时
            """
            permissions = user.get('permissions', [])
            if self.required_permission not in permissions:
                username = user.get('username', 'Unknown')
                raise PermissionError(f"用户 {username} 没有 {self.required_permission} 权限")
            
            print(f"用户 {user.get('username')} 已通过 {self.required_permission} 权限检查")
    
    # 创建一个数据转换装饰器
    class TransformationWrapper(UniversalFunctionWrapper):
        """数据转换装饰器"""
        
        def __init__(self, input_transformer: Callable | None = None, output_transformer: Callable | None = None):
            """初始化数据转换装饰器
            
            Args:
                input_transformer: 输入数据转换器
                output_transformer: 输出数据转换器
            """
            super().__init__(input_transformer=input_transformer, output_transformer=output_transformer)
            self.input_transformer = input_transformer
            self.output_transformer = output_transformer
        
        def _execute_sync(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """转换同步函数的输入和输出数据"""
            # 转换输入
            if self.input_transformer:
                args, kwargs = self.input_transformer(args, kwargs)
            
            # 执行函数
            result = super()._execute_sync(func, args, kwargs)
            
            # 转换输出
            if self.output_transformer:
                result = self.output_transformer(result)
            
            return result
        
        async def _execute_async(self, func: Callable, args: tuple, kwargs: dict) -> Any:
            """转换异步函数的输入和输出数据"""
            # 转换输入
            if self.input_transformer:
                args, kwargs = self.input_transformer(args, kwargs)
            
            # 执行函数
            result = await super()._execute_async(func, args, kwargs)
            
            # 转换输出
            if self.output_transformer:
                result = self.output_transformer(result)
            
            return result
    
    # 定义验证器
    def is_positive(value):
        return isinstance(value, (int, float)) and value > 0
    
    def is_non_empty_list(value):
        return isinstance(value, list) and len(value) > 0
    
    # 定义转换器
    def input_transformer(args, kwargs):
        # 例如：将单个数字转换为列表
        if args and len(args) == 1 and isinstance(args[0], (int, float)):
            return ([args[0]], kwargs)
        return (args, kwargs)
    
    def output_transformer(result):
        # 例如：将结果包装在统一的响应格式中
        return {
            'success': True,
            'data': result,
            'timestamp': time.time()
        }
    
    # 组合使用装饰器
    @ValidationWrapper(
        amount=is_positive,
        items=is_non_empty_list
    )
    @AuthorizationWrapper("process_order")
    @TransformationWrapper(output_transformer=output_transformer)
    def process_order(amount: float, items: list[str], user: dict[str, Any] | None = None) -> dict[str, Any]:
        """处理订单的同步函数"""
        time.sleep(0.5)  # 模拟处理时间
        return {
            'order_id': f"ORD-{int(time.time())}",
            'amount': amount,
            'items': items,
            'status': 'processed'
        }
    
    # 测试同步函数的装饰器组合
    print("测试装饰器组合（同步函数）...")
    
    # 模拟用户信息
    admin_user = {
        'username': 'admin',
        'permissions': ['process_order', 'view_reports']
    }
    
    guest_user = {
        'username': 'guest',
        'permissions': ['view_products']
    }
    
    try:
        # 成功案例
        result1 = process_order(amount=100.0, items=['item1', 'item2'], user=admin_user)
        print(f"成功处理订单: {result1}")
        
        # 权限不足
        process_order(amount=50.0, items=['item3'], user=guest_user)
    except PermissionError as e:
        print(f"预期的权限错误: {e}")
    
    try:
        # 参数验证失败
        process_order(amount=-10, items=[], user=admin_user)
    except ValueError as e:
        print(f"预期的参数验证错误: {e}")
    
    # 创建异步版本的组合装饰器
    @ValidationWrapper(value=is_positive)
    @TransformationWrapper(input_transformer=input_transformer)
    async def async_process_data(value: float) -> float:
        """异步处理数据"""
        await asyncio.sleep(0.3)  # 模拟异步处理
        return value * 2
    
    # 测试异步函数的装饰器组合
    async def test_async_combo():
        print("\n测试装饰器组合（异步函数）...")
        
        # 直接传递数字（会被转换为列表）
        result = await async_process_data(42.0)
        print(f"异步处理结果: {result}")
        
        # 传递另一个有效数字
        result = await async_process_data(10.5)
        print(f"异步处理另一个数字结果: {result}")
    
    asyncio.run(test_async_combo())


def main():
    """主函数，运行所有演示"""
    print("===== xt_wraps.strategy模块示例程序 =====")
    
    demo_base_wrapper_usage()
    demo_sync_function_wrapper()
    demo_async_function_wrapper()
    demo_timer_strategy()
    demo_custom_strategy_implementation()
    
    print("\n===== 示例程序运行完毕 =====")


if __name__ == "__main__":
    main()