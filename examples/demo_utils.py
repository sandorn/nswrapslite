# !/usr/bin/env python3
"""
xt_wraps.utils模块示例程序
本示例演示如何使用utils模块中的工具函数
包括：获取函数位置信息、检查函数类型和获取函数签名
"""
from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from typing import Any

from xtlog import mylog

from nswrapslite.utils import _get_function_location, _get_function_signature, _is_async_function, _is_sync_function

# 配置日志级别
mylog.set_level('INFO')


def demo_get_function_location():
    """演示_get_function_location函数的使用"""
    print("\n=== 演示_get_function_location函数的使用 ===")
    
    # 定义一些测试函数
    def simple_function() -> None:
        """一个简单的测试函数"""
        pass
    
    async def async_test_function() -> None:
        """一个异步测试函数"""
        pass
    
    class TestClass:
        def method1(self) -> str:
            """类的方法1"""
            return "method1"
        
        @staticmethod
        def static_method() -> str:
            """静态方法"""
            return "static_method"
        
        @classmethod
        def class_method(cls) -> str:
            """类方法"""
            return "class_method"
    
    # 获取普通函数的位置信息
    print("普通函数的位置信息:")
    func_loc = _get_function_location(simple_function)
    print(f"{simple_function.__name__}: {func_loc}")
    
    # 获取异步函数的位置信息
    print("\n异步函数的位置信息:")
    async_func_loc = _get_function_location(async_test_function)
    print(f"{async_test_function.__name__}: {async_func_loc}")
    
    # 获取类方法的位置信息
    print("\n类方法的位置信息:")
    test_instance = TestClass()
    
    # 实例方法
    method_loc = _get_function_location(test_instance.method1)
    print(f"实例方法 (method1): {method_loc}")
    
    # 静态方法
    static_loc = _get_function_location(TestClass.static_method)
    print(f"静态方法 (static_method): {static_loc}")
    
    # 类方法
    class_loc = _get_function_location(TestClass.class_method)
    print(f"类方法 (class_method): {class_loc}")
    
    # 内置函数的位置信息
    print("\n内置函数的位置信息:")
    builtin_loc = _get_function_location(len)
    print(f"内置函数 (len): {builtin_loc}")
    
    # lambda函数的位置信息
    print("\nlambda函数的位置信息:")

    def lambda_func(x):
        return x * 2
    lambda_loc = _get_function_location(lambda_func)
    print(f"lambda函数: {lambda_loc}")


def demo_function_type_checking():
    """演示_is_async_function和_is_sync_function函数的使用"""
    print("\n=== 演示函数类型检查功能 ===")
    
    # 定义测试函数
    def sync_function(x: int, y: int) -> int:
        """同步函数"""
        return x + y
    
    async def async_function(url: str) -> dict[str, Any]:
        """异步函数"""
        await asyncio.sleep(0.1)  # 模拟异步操作
        return {"url": url, "status": 200}
    
    # 定义装饰器
    def my_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """一个简单的装饰器"""
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"装饰器: 调用函数 {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    
    # 定义被装饰的函数
    @my_decorator
    def decorated_sync_function() -> None:
        """被装饰的同步函数"""
        pass
    
    # 使用functools.wraps的装饰器
    import functools
    
    def wraps_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """使用functools.wraps的装饰器"""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"使用wraps的装饰器: 调用函数 {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    
    @wraps_decorator
    def decorated_sync_function_with_wraps() -> None:
        """使用functools.wraps装饰的同步函数"""
        pass
    
    @wraps_decorator
    async def decorated_async_function_with_wraps() -> None:
        """使用functools.wraps装饰的异步函数"""
        await asyncio.sleep(0.1)
    
    # 测试函数类型
    print("检查各种函数的类型:")
    
    # 普通函数
    print(f"同步函数 (sync_function) 是异步函数? {_is_async_function(sync_function)}")
    print(f"同步函数 (sync_function) 是同步函数? {_is_sync_function(sync_function)}")
    
    # 异步函数
    print(f"异步函数 (async_function) 是异步函数? {_is_async_function(async_function)}")
    print(f"异步函数 (async_function) 是同步函数? {_is_sync_function(async_function)}")
    
    # 被装饰的函数(未使用functools.wraps)
    print(f"被装饰的同步函数 (decorated_sync_function) 是异步函数? {_is_async_function(decorated_sync_function)}")
    print(f"被装饰的同步函数 (decorated_sync_function) 是同步函数? {_is_sync_function(decorated_sync_function)}")
    
    # 使用functools.wraps装饰的函数
    print(f"使用wraps的同步函数 (decorated_sync_function_with_wraps) 是异步函数? {_is_async_function(decorated_sync_function_with_wraps)}")
    print(f"使用wraps的同步函数 (decorated_sync_function_with_wraps) 是同步函数? {_is_sync_function(decorated_sync_function_with_wraps)}")
    
    # 使用functools.wraps装饰的异步函数
    print(f"使用wraps的异步函数 (decorated_async_function_with_wraps) 是异步函数? {_is_async_function(decorated_async_function_with_wraps)}")
    print(f"使用wraps的异步函数 (decorated_async_function_with_wraps) 是同步函数? {_is_sync_function(decorated_async_function_with_wraps)}")
    
    # 内置函数
    print(f"内置函数 (len) 是异步函数? {_is_async_function(len)}")
    print(f"内置函数 (len) 是同步函数? {_is_sync_function(len)}")
    
    # lambda函数
    def lambda_func(x):
        return x * 2
    print(f"lambda函数 是异步函数? {_is_async_function(lambda_func)}")
    print(f"lambda函数 是同步函数? {_is_sync_function(lambda_func)}")


def demo_get_function_signature():
    """演示_get_function_signature函数的使用"""
    print("\n=== 演示_get_function_signature函数的使用 ===")
    
    # 定义各种类型的函数
    def simple_func() -> None:
        """无参数无返回值的函数"""
        pass
    
    def complex_func(a: int, b: str, c: list[float] | None = None) -> dict[str, Any]:
        """有参数和返回值的函数"""
        return {"a": a, "b": b, "c": c}
    
    async def async_func(param: str, timeout: float = 30.0) -> tuple[bool, str]:
        """异步函数"""
        await asyncio.sleep(0.1)
        return True, "Success"
    
    class ExampleClass:
        def method_with_args(self, x: int, y: int) -> int:
            """带参数的实例方法"""
            return x + y
        
        @staticmethod
        def static_method(z: str) -> str:
            """静态方法"""
            return z.upper()
        
        @classmethod
        def class_method(cls, value: int) -> str:
            """类方法"""
            return f"{cls.__name__}: {value}"
    
    # 获取各种函数的签名
    print("获取函数签名:")
    
    # 简单函数
    sig1 = _get_function_signature(simple_func)
    print(f"简单函数: {sig1}")
    
    # 复杂函数
    sig2 = _get_function_signature(complex_func)
    print(f"复杂函数: {sig2}")
    
    # 异步函数
    sig3 = _get_function_signature(async_func)
    print(f"异步函数: {sig3}")
    
    # 实例方法
    example = ExampleClass()
    sig4 = _get_function_signature(example.method_with_args)
    print(f"实例方法: {sig4}")
    
    # 静态方法
    sig5 = _get_function_signature(ExampleClass.static_method)
    print(f"静态方法: {sig5}")
    
    # 类方法
    sig6 = _get_function_signature(ExampleClass.class_method)
    print(f"类方法: {sig6}")
    
    # 内置函数
    sig7 = _get_function_signature(len)
    print(f"内置函数 (len): {sig7}")
    
    # lambda函数
    def lambda_func(x, y=10):
        return x + y
    sig8 = _get_function_signature(lambda_func)
    print(f"lambda函数: {sig8}")


def demo_practical_application():
    """演示utils工具函数在实际应用中的使用"""
    print("\n=== 演示utils工具函数在实际应用中的使用 ===")
    
    # 场景1: 构建自定义装饰器
    print("\n场景1: 构建自定义装饰器")
    
    def my_custom_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """一个自定义的装饰器，使用utils工具函数"""
        
        # 获取函数信息
        func_loc = _get_function_location(func)
        func_sig = _get_function_signature(func)
        
        # 检查函数类型
        if _is_async_function(func):
            # 异步函数的包装器
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                print(f"[装饰器] 开始执行异步函数: {func_sig}")
                print(f"[装饰器] 函数位置: {func_loc}")
                try:
                    result = await func(*args, **kwargs)
                    print(f"[装饰器] 异步函数执行完成: {func_sig}")
                    return result
                except Exception as e:
                    print(f"[装饰器] 异步函数执行出错: {e}")
                    raise
            return async_wrapper
        # 同步函数的包装器

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"[装饰器] 开始执行同步函数: {func_sig}")
            print(f"[装饰器] 函数位置: {func_loc}")
            try:
                result = func(*args, **kwargs)
                print(f"[装饰器] 同步函数执行完成: {func_sig}")
                return result
            except Exception as e:
                print(f"[装饰器] 同步函数执行出错: {e}")
                raise
        return sync_wrapper
    
    # 使用自定义装饰器
    @my_custom_decorator
    def process_data(data: list[int]) -> int:
        """处理数据的同步函数"""
        return sum(data)
    
    @my_custom_decorator
    async def fetch_data(url: str) -> dict[str, str]:
        """获取数据的异步函数"""
        await asyncio.sleep(0.2)  # 模拟网络请求
        return {"url": url, "status": "success"}
    
    # 测试自定义装饰器
    print("\n测试自定义装饰器包装的同步函数:")
    result1 = process_data([1, 2, 3, 4, 5])
    print(f"同步函数结果: {result1}")
    
    # 测试异步函数
    async def test_async_decorator():
        print("\n测试自定义装饰器包装的异步函数:")
        result2 = await fetch_data("https://api.example.com")
        print(f"异步函数结果: {result2}")
    
    asyncio.run(test_async_decorator())
    
    # 场景2: 函数信息记录器
    print("\n场景2: 函数信息记录器")
    
    def log_function_info(func: Callable[..., Any]) -> dict[str, str]:
        """记录函数的详细信息"""
        return {
            "name": func.__name__,  # 函数名
            "signature": _get_function_signature(func),  # 函数签名
            "location": _get_function_location(func),  # 函数位置
            "type": "async" if _is_async_function(func) else "sync",  # 函数类型
            "doc": inspect.getdoc(func) or "No documentation"  # 函数文档
        }
    
    # 记录多个函数的信息
    functions_to_log = [
        process_data,
        fetch_data,
        len,
        lambda x: x**2
    ]
    
    for func in functions_to_log:
        info = log_function_info(func)
        print(f"\n函数信息 - {info['name']}:")
        print(f"  类型: {info['type']}")
        print(f"  签名: {info['signature']}")
        print(f"  位置: {info['location']}")
        # 只显示文档的前50个字符
        doc_preview = info['doc'][:50] + '...' if len(info['doc']) > 50 else info['doc']
        print(f"  文档: {doc_preview}")
    
    # 场景3: 函数执行跟踪器
    print("\n场景3: 函数执行跟踪器")
    
    class FunctionTracker:
        """函数执行跟踪器"""
        
        def __init__(self):
            """初始化跟踪器"""
            self.tracking_history: list[dict[str, Any]] = []
        
        def track(self, func: Callable[..., Any]) -> Callable[..., Any]:
            """跟踪函数执行"""
            func_loc = _get_function_location(func)
            func_sig = _get_function_signature(func)
            
            if _is_async_function(func):
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    # 记录执行开始
                    start_info = {
                        "function": func_sig,
                        "location": func_loc,
                        "type": "async",
                        "args": args,
                        "kwargs": kwargs,
                        "started_at": asyncio.get_event_loop().time()
                    }
                    
                    try:
                        result = await func(*args, **kwargs)
                        # 记录执行完成
                        start_info.update({
                            "completed": True,
                            "result": result,
                            "ended_at": asyncio.get_event_loop().time()
                        })
                        self.tracking_history.append(start_info)
                        return result
                    except Exception as e:
                        # 记录执行失败
                        start_info.update({
                            "completed": False,
                            "error": str(e),
                            "ended_at": asyncio.get_event_loop().time()
                        })
                        self.tracking_history.append(start_info)
                        raise
                return async_wrapper

            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                # 记录执行开始
                import time
                start_info = {
                    "function": func_sig,
                    "location": func_loc,
                    "type": "sync",
                    "args": args,
                    "kwargs": kwargs,
                    "started_at": time.time()
                }

                try:
                    result = func(*args, **kwargs)
                    # 记录执行完成
                    start_info.update({
                        "completed": True,
                        "result": result,
                        "ended_at": time.time()
                    })
                    self.tracking_history.append(start_info)
                    return result
                except Exception as e:
                    # 记录执行失败
                    start_info.update({
                        "completed": False,
                        "error": str(e),
                        "ended_at": time.time()
                    })
                    self.tracking_history.append(start_info)
                    raise
            return sync_wrapper
        
        def get_history(self) -> list[dict[str, Any]]:
            """获取跟踪历史"""
            return self.tracking_history
        
        def print_summary(self) -> None:
            """打印跟踪摘要"""
            print("\n函数执行跟踪摘要:")
            print(f"总共跟踪了 {len(self.tracking_history)} 个函数调用")
            
            success_count = sum(1 for record in self.tracking_history if record['completed'])
            failed_count = len(self.tracking_history) - success_count
            
            print(f"成功调用: {success_count}")
            print(f"失败调用: {failed_count}")
            
            # 计算总执行时间
            total_time = 0.0
            for record in self.tracking_history:
                if 'started_at' in record and 'ended_at' in record:
                    total_time += record['ended_at'] - record['started_at']
            
            print(f"总执行时间: {total_time:.4f}秒")
            
            # 显示每个函数的执行情况
            for i, record in enumerate(self.tracking_history, 1):
                status = "成功" if record['completed'] else "失败"
                exec_time = record['ended_at'] - record['started_at'] if record.get('ended_at') else 0
                print(f"{i}. {record['function']} - {status} - 耗时: {exec_time:.4f}秒")
    
    # 创建跟踪器实例
    tracker = FunctionTracker()
    
    # 装饰函数进行跟踪
    @tracker.track
    def calculate_factorial(n: int) -> int:
        """计算阶乘"""
        if n < 0:
            raise ValueError("负数没有阶乘")
        if n == 0 or n == 1:
            return 1
        return n * calculate_factorial(n - 1)
    
    @tracker.track
    async def process_batch_data(data: list[int]) -> dict[str, Any]:
        """异步处理批量数据"""
        await asyncio.sleep(0.1)  # 模拟处理时间
        return {
            "count": len(data),
            "sum": sum(data),
            "average": sum(data) / len(data) if data else 0
        }
    
    # 测试函数跟踪
    print("\n测试函数执行跟踪:")
    
    # 测试正常执行
    try:
        result = calculate_factorial(5)
        print(f"阶乘计算结果: {result}")
    except ValueError as e:
        print(f"计算错误: {e}")
    
    # 测试异常执行
    try:
        calculate_factorial(-1)
    except ValueError as e:
        print(f"预期的错误: {e}")
    
    # 测试异步函数跟踪
    async def test_async_tracking():
        result = await process_batch_data([10, 20, 30, 40, 50])
        print(f"异步处理结果: {result}")
    
    asyncio.run(test_async_tracking())
    
    # 打印跟踪摘要
    tracker.print_summary()


def main():
    """主函数，运行所有演示"""
    print("===== xt_wraps.utils模块示例程序 =====")
    
    # 基本功能演示
    demo_get_function_location()
    demo_function_type_checking()
    demo_get_function_signature()
    
    # 实际应用场景
    demo_practical_application()
    
    print("\n===== 示例程序运行完毕 =====")


if __name__ == "__main__":
    main()