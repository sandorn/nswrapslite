# !/usr/bin/env python3

"""
xt_wraps/factory.py 模块示例程序

本示例展示了 factory.py 模块中装饰器工厂功能的使用方法，包括：
- decorator_factory：通用装饰器工厂，支持同步/异步函数和钩子系统
- timer_wrapper_factory：计时装饰器工厂，记录函数执行时间
- exc_wrapper_factory：异常处理装饰器，支持同步/异步函数
- log_wrapper_factory：日志装饰器，记录函数调用信息
- 实际应用场景：性能监控、异常捕获、日志记录、自定义装饰器创建等
"""
from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Any

from xtlog import mylog

# 导入 factory 模块中的函数
from nswrapslite.factory import decorator_factory, exc_wrapper_factory, log_wrapper_factory, timer_wrapper_factory

# 配置日志级别
mylog.set_level('INFO')


def demo_basic_decorator_factory() -> None:
    """演示 decorator_factory 的基本使用"""
    print("\n=== 演示 decorator_factory 的基本使用 ===")
    
    # 示例1: 创建简单的日志装饰器
    print("\n示例1: 创建简单的日志装饰器")

    def log_before_hook(func: Callable, args: tuple, kwargs: dict, context: dict) -> None:
        """前置钩子：记录函数调用信息"""
        print(f"调用函数: {func.__name__}, 参数: {args}, {kwargs}")
        # 可以在上下文中存储信息，供后续钩子使用
        context['start_time'] = time.time()
    
    def log_after_hook(func: Callable, args: tuple, kwargs: dict, result: Any, context: dict) -> Any:
        """后置钩子：记录函数返回信息"""
        start_time = context.get('start_time', time.time())
        elapsed = time.time() - start_time
        print(f"函数 {func.__name__} 执行完成，结果: {result}，耗时: {elapsed:.4f}秒")
        return result  # 返回原始结果或修改后的结果
    
    def log_except_hook(func: Callable, args: tuple, kwargs: dict, exc: Exception, context: dict) -> Any:
        """异常钩子：处理函数执行异常"""
        print(f"函数 {func.__name__} 执行出错: {type(exc).__name__}: {exc}")
        # 返回默认值或重新抛出异常
        return "错误处理后的默认值"
    
    # 创建装饰器
    log_decorator = decorator_factory(
        before_hook=log_before_hook,
        after_hook=log_after_hook,
        except_hook=log_except_hook
    )
    
    # 使用装饰器装饰同步函数
    @log_decorator
    def add(a: int, b: int) -> int:
        """简单的加法函数"""
        return a + b
    
    # 使用装饰器装饰会抛出异常的函数
    @log_decorator
    def divide(a: int, b: int) -> float:
        """可能抛出异常的除法函数"""
        return a / b
    
    # 测试装饰器
    print("\n测试同步函数装饰器:")
    result1 = add(5, 3)
    print(f"测试结果: {result1}")
    
    result2 = divide(10, 0)  # 会触发异常钩子
    print(f"异常处理结果: {result2}")
    
    # 示例2: 异步函数支持
    print("\n示例2: 异步函数支持")
    # 使用相同的钩子创建装饰器
    async_log_decorator = decorator_factory(
        before_hook=log_before_hook,
        after_hook=log_after_hook,
        except_hook=log_except_hook
    )
    
    # 装饰异步函数
    @async_log_decorator
    async def async_add(a: int, b: int) -> int:
        """异步加法函数"""
        await asyncio.sleep(0.1)  # 模拟异步操作
        return a + b
    
    @async_log_decorator
    async def async_divide(a: int, b: int) -> float:
        """异步除法函数"""
        await asyncio.sleep(0.1)  # 模拟异步操作
        return a / b
    
    # 运行异步测试
    async def test_async_decorator():
        print("\n测试异步函数装饰器:")
        result3 = await async_add(7, 8)
        print(f"异步加法结果: {result3}")
        
        result4 = await async_divide(20, 0)  # 会触发异常钩子
        print(f"异步异常处理结果: {result4}")
    
    asyncio.run(test_async_decorator())
    
    # 示例3: 条件执行和提前返回
    print("\n示例3: 条件执行和提前返回")

    def validation_hook(func: Callable, args: tuple, kwargs: dict, context: dict) -> str | None:
        """验证参数，如果不满足条件则提前返回"""
        if args and isinstance(args[0], int) and args[0] < 0:
            print(f"参数验证失败: {args[0]} 不能为负数")
            return "参数验证失败"
        return None  # 返回None表示继续执行原函数
    
    validate_decorator = decorator_factory(before_hook=validation_hook)
    
    @validate_decorator
    def process_positive_number(num: int) -> str:
        """处理正数的函数"""
        return f"处理成功: {num}"
    
    print("\n测试条件执行装饰器:")
    result5 = process_positive_number(10)
    print(f"有效参数结果: {result5}")
    
    result6 = process_positive_number(-5)
    print(f"无效参数结果: {result6}")


def demo_timer_wrapper_factory() -> None:
    """演示 timer_wrapper_factory 的使用"""
    print("\n=== 演示 timer_wrapper_factory 的使用 ===")
    
    # 示例1: 基本用法
    print("\n示例1: 基本用法")

    @timer_wrapper_factory
    def slow_sync_function(duration: float) -> str:
        """模拟耗时的同步操作"""
        time.sleep(duration)
        return f"同步函数执行完成，耗时 {duration} 秒"
    
    # 测试同步函数计时
    print("\n测试同步函数计时:")
    result1 = slow_sync_function(0.5)
    print(f"结果: {result1}")
    
    # 示例2: 异步函数支持
    print("\n示例2: 异步函数支持")

    @timer_wrapper_factory
    async def slow_async_function(duration: float) -> str:
        """模拟耗时的异步操作"""
        await asyncio.sleep(duration)
        return f"异步函数执行完成，耗时 {duration} 秒"
    
    # 测试异步函数计时
    async def test_async_timer():
        print("\n测试异步函数计时:")
        result2 = await slow_async_function(0.6)
        print(f"结果: {result2}")
    
    asyncio.run(test_async_timer())
    
    # 示例3: 带异常的函数计时
    print("\n示例3: 带异常的函数计时")

    @timer_wrapper_factory
    def function_with_error() -> None:
        """会抛出异常的函数"""
        time.sleep(0.3)
        raise ValueError("测试异常")
    
    # 测试异常函数计时
    print("\n测试异常函数计时:")
    try:
        function_with_error()
    except ValueError as e:
        print(f"捕获到异常: {e}")
    
    # 示例4: 实际应用 - 性能监控
    print("\n示例4: 实际应用 - 性能监控")

    @timer_wrapper_factory
    def process_large_data(data: list[int]) -> dict[str, Any]:
        """处理大量数据的函数"""
        # 模拟数据处理
        time.sleep(0.8)
        return {
            "sum": sum(data),
            "average": sum(data) / len(data) if data else 0,
            "count": len(data)
        }
    
    # 生成测试数据
    test_data = list(range(1, 100001))
    print(f"\n处理 {len(test_data)} 条数据:")
    result4 = process_large_data(test_data)
    print(f"处理结果: {result4}")


def demo_exc_wrapper_factory() -> None:
    """演示 exc_wrapper_factory 的使用"""
    print("\n=== 演示 exc_wrapper_factory 的使用 ===")
    
    # 示例1: 基本异常处理
    print("\n示例1: 基本异常处理")

    @exc_wrapper_factory(re_raise=False, default_return=0)
    def safe_divide(a: int, b: int) -> float:
        """安全的除法函数"""
        return a / b
    
    print("\n测试基本异常处理:")
    result1 = safe_divide(10, 2)
    print(f"正常除法结果: {result1}")
    
    result2 = safe_divide(10, 0)  # 会触发异常处理
    print(f"除零异常处理结果: {result2}")
    
    # 示例2: 只捕获特定异常
    print("\n示例2: 只捕获特定异常")

    @exc_wrapper_factory(
        allowed_exceptions=(ZeroDivisionError,),
        re_raise=False,
        default_return="除零错误"
    )
    def specific_exception_handler(a: int, b: int) -> float:
        """只处理特定异常的函数"""
        if a < 0:
            raise ValueError("参数不能为负数")
        return a / b
    
    print("\n测试特定异常处理:")
    result3 = specific_exception_handler(8, 0)
    print(f"除零异常处理结果: {result3}")
    
    try:
        result4 = specific_exception_handler(-5, 2)  # 这个异常不会被处理
        print(f"结果: {result4}")
    except ValueError as e:
        print(f"未捕获的异常: {e}")
    
    # 示例3: 自定义错误消息
    print("\n示例3: 自定义错误消息")

    @exc_wrapper_factory(
        re_raise=False,
        custom_message="数据处理失败",
        log_traceback=True,
        default_return=None,
        allowed_exceptions=(Exception,)
    )
    def process_data(data: list[int]) -> dict[str, Any]:
        """处理数据的函数"""
        if not data:
            raise ValueError("数据不能为空")
        return {"result": sum(data)}
    
    print("\n测试自定义错误消息:")
    result5 = process_data([1, 2, 3, 4, 5])
    print(f"正常数据处理结果: {result5}")
    
    try:
        result6 = process_data([])  # 会触发自定义错误消息
        print(f"空数据处理结果: {result6}")
    except ValueError as e:
        print(f"捕获到预期的ValueError: {e}")
    
    # 示例4: 异步函数支持
    print("\n示例4: 异步函数支持")

    @exc_wrapper_factory(re_raise=False, default_return="异步操作失败")
    async def async_operation(value: int) -> str:
        """异步操作函数"""
        await asyncio.sleep(0.2)
        if value < 0:
            raise ValueError("值不能为负数")
        return f"异步操作成功，值为 {value}"
    
    async def test_async_exception_handler():
        print("\n测试异步异常处理:")
        result7 = await async_operation(5)
        print(f"正常异步操作结果: {result7}")
        
        result8 = await async_operation(-3)  # 会触发异常处理
        print(f"异常异步操作结果: {result8}")
    
    asyncio.run(test_async_exception_handler())
    
    # 示例5: 实际应用 - API请求处理
    print("\n示例5: 实际应用 - API请求处理")

    class ApiService:
        @exc_wrapper_factory(
            re_raise=False,
            default_return={"error": "API请求失败"},
            custom_message="API请求异常",
            allowed_exceptions=(ConnectionError, TimeoutError, ValueError)
        )
        def make_request(self, endpoint: str, timeout: float = 5.0) -> dict[str, Any]:
            """模拟API请求"""
            # 模拟网络延迟
            time.sleep(0.5)
            
            # 模拟不同的错误情况
            if endpoint == "/timeout":
                raise TimeoutError("请求超时")
            if endpoint == "/connection":
                raise ConnectionError("连接失败")
            if endpoint == "/invalid":
                raise ValueError("无效的请求参数")
            if endpoint == "/success":
                return {"status": 200, "data": {"message": "请求成功"}}
            
            raise ValueError("未知的端点")
    
    # 测试API服务
    api = ApiService()
    print("\n测试API请求处理:")
    print(f"成功请求: {api.make_request('/success')}")
    print(f"超时请求: {api.make_request('/timeout')}")
    print(f"连接错误: {api.make_request('/connection')}")


def demo_log_wrapper_factory() -> None:
    """演示 log_wrapper_factory 的使用"""
    print("\n=== 演示 log_wrapper_factory 的使用 ===")
    
    # 示例1: 基本日志记录
    print("\n示例1: 基本日志记录")

    @log_wrapper_factory
    def calculate_sum(a: int, b: int) -> int:
        """计算两个数的和"""
        return a + b
    
    print("\n测试基本日志记录:")
    result1 = calculate_sum(10, 20)
    print(f"结果: {result1}")
    
    # 示例2: 配置日志选项
    print("\n示例2: 配置日志选项")

    @log_wrapper_factory(
        log_args=False,  # 不记录参数
        log_result=True,  # 记录结果
        re_raise=False,  # 不重新抛出异常
        default_return=None  # 异常时返回None
    )
    def configure_log_function(a: int, b: int) -> float:
        """配置了日志选项的函数"""
        return a / b
    
    print("\n测试配置日志选项:")
    result2 = configure_log_function(20, 4)
    print(f"正常结果: {result2}")
    
    try:
        result3 = configure_log_function(10, 0)  # 会触发异常日志
        print(f"异常结果: {result3}")
    except ZeroDivisionError as e:
        print(f"捕获到预期的ZeroDivisionError: {e}")
    
    # 示例3: 自定义日志消息
    print("\n示例3: 自定义日志消息")

    @log_wrapper_factory(custom_message="用户管理操作")
    def create_user(username: str, email: str) -> dict[str, str]:
        """创建用户的函数"""
        return {"username": username, "email": email, "status": "active"}
    
    print("\n测试自定义日志消息:")
    user = create_user("john_doe", "john@example.com")
    print(f"创建的用户: {user}")
    
    # 示例4: 异步函数支持
    print("\n示例4: 异步函数支持")

    @log_wrapper_factory
    async def async_log_function(data: list[int]) -> dict[str, Any]:
        """异步日志函数"""
        await asyncio.sleep(0.2)  # 模拟异步操作
        return {"sum": sum(data), "count": len(data)}
    
    async def test_async_log():
        print("\n测试异步日志功能:")
        result4 = await async_log_function([1, 2, 3, 4, 5])
        print(f"异步结果: {result4}")
    
    asyncio.run(test_async_log())
    
    # 示例5: 实际应用 - 业务流程日志
    print("\n示例5: 实际应用 - 业务流程日志")

    class OrderService:
        @log_wrapper_factory(
            log_args=True,  # 记录订单详情
            log_result=True,  # 记录订单处理结果
            custom_message="订单处理流程"
        )
        def process_order(self, order_id: str, items: list[dict[str, Any]], customer: dict[str, str]) -> dict[str, Any]:
            """处理订单的函数"""
            # 模拟订单处理
            time.sleep(0.3)
            
            total = sum(item["price"] * item["quantity"] for item in items)
            
            # 模拟异常情况
            if not items:
                raise ValueError("订单不能为空")
            
            return {
                "order_id": order_id,
                "status": "processed",
                "total_amount": total,
                "customer": customer["name"],
                "items_count": len(items)
            }
    
    # 测试订单服务
    order_service = OrderService()
    print("\n测试订单处理日志:")
    
    # 正常订单
    order_items = [
        {"id": "item1", "name": "产品A", "price": 199.99, "quantity": 2},
        {"id": "item2", "name": "产品B", "price": 99.99, "quantity": 1}
    ]
    
    customer_info = {"id": "cust1", "name": "张三", "email": "zhangsan@example.com"}
    
    order_result = order_service.process_order("order-001", order_items, customer_info)
    print(f"订单处理结果: {order_result}")
    
    # 异常订单
    try:
        empty_order = order_service.process_order("order-002", [], customer_info)
        print(f"空订单结果: {empty_order}")
    except ValueError as e:
        print(f"空订单异常: {e}")


def demo_combined_decorators() -> None:
    """演示多个装饰器的组合使用"""
    print("\n=== 演示多个装饰器的组合使用 ===")
    
    # 示例1: 结合日志和计时装饰器
    print("\n示例1: 结合日志和计时装饰器")

    @log_wrapper_factory
    @timer_wrapper_factory
    def complex_operation(a: int, b: int) -> list[int]:
        """复杂操作函数"""
        # 模拟复杂计算
        time.sleep(0.5)
        result = []
        for i in range(a, b):
            if i % 2 == 0:
                result.append(i)
        return result
    
    print("\n测试组合装饰器:")
    result1 = complex_operation(1, 10000)
    print(f"结果长度: {len(result1)}")
    
    # 示例2: 结合异常处理和日志装饰器
    print("\n示例2: 结合异常处理和日志装饰器")

    @exc_wrapper_factory(re_raise=False, default_return=[])
    @log_wrapper_factory(custom_message="数据转换操作")
    def convert_data(data: Any) -> list[str]:
        """数据转换函数"""
        # 尝试将输入数据转换为字符串列表
        if isinstance(data, list):
            return [str(item) for item in data]
        if isinstance(data, dict):
            return [f"{k}:{v}" for k, v in data.items()]
        raise TypeError(f"不支持的数据类型: {type(data).__name__}")
    
    print("\n测试数据转换装饰器组合:")
    print(f"列表转换: {convert_data([1, 2, 3, 4, 5])}")
    print(f"字典转换: {convert_data({"a": 1, "b": 2})}")
    print(f"错误类型转换: {convert_data(123)}")  # 会触发异常处理
    
    # 示例3: 异步函数的装饰器组合
    print("\n示例3: 异步函数的装饰器组合")

    @timer_wrapper_factory
    @exc_wrapper_factory(re_raise=False, default_return="异步操作失败")
    async def async_combined_operation(value: int) -> str:
        """异步组合操作函数"""
        await asyncio.sleep(0.3)  # 模拟异步操作
        if value < 0:
            raise ValueError("值不能为负数")
        return f"成功处理值: {value}"
    
    async def test_async_combined():
        print("\n测试异步装饰器组合:")
        result2 = await async_combined_operation(42)
        print(f"正常结果: {result2}")
        
        result3 = await async_combined_operation(-10)  # 会触发异常处理
        print(f"异常结果: {result3}")
    
    asyncio.run(test_async_combined())
    
    # 示例4: 实际应用 - 完整的服务层装饰器组合
    print("\n示例4: 实际应用 - 完整的服务层装饰器组合")

    class UserService:
        @timer_wrapper_factory  # 记录性能
        @log_wrapper_factory(custom_message="用户服务操作")  # 记录详细日志
        @exc_wrapper_factory(
            re_raise=False, 
            default_return={"error": "操作失败"}, 
            custom_message="用户服务异常"
        )  # 统一异常处理
        def get_user_profile(self, user_id: str) -> dict[str, Any]:
            """获取用户个人资料"""
            # 模拟数据库查询
            time.sleep(0.4)
            
            # 模拟用户存在和不存在的情况
            if user_id in ["user1", "user2", "user3"]:
                return {
                    "id": user_id,
                    "name": f"用户{user_id[-1]}",
                    "email": f"user{user_id[-1]}@example.com",
                    "created_at": "2023-01-01"
                }
            raise ValueError(f"用户 {user_id} 不存在")
    
    # 测试用户服务
    user_service = UserService()
    print("\n测试用户服务装饰器组合:")
    print(f"存在用户: {user_service.get_user_profile('user1')}")
    print(f"不存在用户: {user_service.get_user_profile('user999')}")


def demo_custom_decorators_creation() -> None:
    """演示如何使用 decorator_factory 创建自定义装饰器"""
    print("\n=== 演示如何使用 decorator_factory 创建自定义装饰器 ===")
    
    # 示例1: 创建缓存装饰器
    print("\n示例1: 创建缓存装饰器")
    # 简单的内存缓存字典
    cache = {}
    
    def cache_before_hook(func: Callable, args: tuple, kwargs: dict, context: dict) -> Any | None:
        """缓存前置钩子：检查缓存中是否有结果"""
        # 创建缓存键
        cache_key = (func.__name__, args, frozenset(kwargs.items()))
        context['cache_key'] = cache_key
        
        # 检查缓存
        if cache_key in cache:
            print(f"缓存命中: {func.__name__}")
            return cache[cache_key]
        
        print(f"缓存未命中: {func.__name__}")
        return None  # 继续执行原函数
    
    def cache_after_hook(func: Callable, args: tuple, kwargs: dict, result: Any, context: dict) -> Any:
        """缓存后置钩子：将结果存入缓存"""
        cache_key = context.get('cache_key')
        if cache_key:
            cache[cache_key] = result
            print(f"结果已缓存: {func.__name__}")
        return result
    
    # 创建缓存装饰器
    cache_decorator = decorator_factory(
        before_hook=cache_before_hook,
        after_hook=cache_after_hook
    )
    
    @cache_decorator
    def expensive_computation(a: int, b: int) -> int:
        """模拟昂贵的计算操作"""
        print(f"执行昂贵计算: {a}, {b}")
        time.sleep(0.5)  # 模拟计算耗时
        return a * b
    
    print("\n测试缓存装饰器:")
    # 第一次调用，缓存未命中
    result1 = expensive_computation(10, 20)
    print(f"结果1: {result1}")
    
    # 第二次调用相同参数，应该命中缓存
    result2 = expensive_computation(10, 20)
    print(f"结果2: {result2}")
    
    # 不同参数，缓存未命中
    result3 = expensive_computation(5, 30)
    print(f"结果3: {result3}")
    
    # 示例2: 创建重试装饰器
    print("\n示例2: 创建重试装饰器")

    def create_retry_decorator(max_retries: int = 3, delay: float = 0.1) -> Callable:
        """创建重试装饰器的工厂函数"""
        def retry_before_hook(func: Callable, args: tuple, kwargs: dict, context: dict) -> None:
            """重试前置钩子：初始化重试计数"""
            context['retry_count'] = 0
        
        def retry_except_hook(func: Callable, args: tuple, kwargs: dict, exc: Exception, context: dict) -> Any:
            """重试异常钩子：处理重试逻辑"""
            context['retry_count'] += 1
            retry_count = context['retry_count']
            
            if retry_count <= max_retries:
                print(f"函数 {func.__name__} 失败，第 {retry_count} 次重试...")
                time.sleep(delay)  # 等待一段时间后重试
                # 手动执行原函数进行重试
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 如果重试仍然失败，递归调用异常钩子
                    return retry_except_hook(func, args, kwargs, e, context)
            else:
                print(f"函数 {func.__name__} 达到最大重试次数 {max_retries}")
                raise exc  # 达到最大重试次数，抛出异常
        
        # 创建并返回装饰器
        return decorator_factory(
            before_hook=retry_before_hook,
            except_hook=retry_except_hook
        )
    
    # 使用装饰器工厂创建重试装饰器
    retry_on_error = create_retry_decorator(max_retries=3, delay=0.2)
    
    # 定义一个可能随机失败的函数
    import random
    
    @retry_on_error
    def unstable_operation() -> str:
        """不稳定的操作，有一定概率失败"""
        if random.random() < 0.7:  # 70% 的概率失败
            raise ConnectionError("模拟连接失败")
        return "操作成功"
    
    print("\n测试重试装饰器:")
    try:
        result4 = unstable_operation()
        print(f"最终结果: {result4}")
    except ConnectionError as e:
        print(f"最终失败: {e}")


def main() -> None:
    """主函数，运行所有示例"""
    print("=== xt_wraps/factory.py 模块示例程序 ===")
    
    # 运行各个功能的示例
    demo_basic_decorator_factory()
    demo_timer_wrapper_factory()
    demo_exc_wrapper_factory()
    demo_log_wrapper_factory()
    demo_combined_decorators()
    demo_custom_decorators_creation()
    
    print("\n=== 所有示例运行完毕 ===")


if __name__ == "__main__":
    main()