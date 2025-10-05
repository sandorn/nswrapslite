# !/usr/bin/env python3
"""log.py模块示例程序

这个文件演示了xt_wraps/log.py模块中log_wraps装饰器的使用方法，包括:
- 基本的日志记录功能
- 同步函数和异步函数的支持
- 不同配置选项的使用（记录参数、记录结果、异常处理等）
- 实际应用场景展示
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

from xtlog import mylog

# 导入log模块中的功能
from nswrapslite.log import logging_wraps

# 配置日志级别
mylog.set_level('INFO')


# 1. 基本的日志记录功能示例
def demo_basic_logging():
    """演示log_wraps装饰器的基本日志记录功能"""
    print("\n=== 1. 基本的日志记录功能示例 ===")
    
    # 使用默认配置的装饰器
    @logging_wraps
    def add_numbers(x: int, y: int) -> int:
        """简单的加法函数"""
        return x + y
    
    # 执行函数并观察日志输出
    result = add_numbers(5, 3)
    print(f"函数返回结果: {result}")


# 2. 配置选项示例
def demo_configuration_options():
    """演示log_wraps装饰器的不同配置选项"""
    print("\n=== 2. 配置选项示例 ===")
    
    # 配置1: 只记录参数，不记录结果
    @logging_wraps(log_args=True, log_result=False)
    def multiply_numbers(x: int, y: int) -> int:
        """简单的乘法函数"""
        return x * y
    
    # 配置2: 只记录结果，不记录参数
    @logging_wraps(log_args=False, log_result=True)
    def subtract_numbers(x: int, y: int) -> int:
        """简单的减法函数"""
        return x - y
    
    # 配置3: 既不记录参数也不记录结果（仅记录执行情况）
    @logging_wraps(log_args=False, log_result=False)
    def divide_numbers(x: int, y: int) -> float:
        """简单的除法函数"""
        return x / y
    
    # 执行这些函数并观察日志输出
    multiply_numbers(4, 7)
    subtract_numbers(10, 3)
    divide_numbers(20, 4)


# 3. 异常处理示例
def demo_exception_handling():
    """演示log_wraps装饰器的异常处理功能"""
    print("\n=== 3. 异常处理示例 ===")
    
    # 配置1: 捕获异常但不重新抛出，返回默认值
    @logging_wraps(re_raise=False, default_return=0, log_traceback=True)
    def safe_divide(x: int, y: int) -> float:
        """安全的除法函数，处理除零异常"""
        return x / y
    
    # 配置2: 捕获异常并重新抛出
    @logging_wraps(re_raise=True, log_traceback=True)
    def risky_divide(x: int, y: int) -> float:
        """有风险的除法函数，会重新抛出异常"""
        return x / y
    
    # 配置3: 不记录完整堆栈信息
    @logging_wraps(re_raise=False, default_return=None, log_traceback=False)
    def minimal_error_handling(x: int, y: int) -> float | None:
        """最小化错误处理，不记录完整堆栈"""
        return x / y
    
    # 执行安全除法函数（除零）
    print("执行安全除法函数（除零）:")
    result1 = safe_divide(10, 0)
    print(f"安全除法结果: {result1}")
    
    # 执行最小化错误处理函数（除零）
    print("\n执行最小化错误处理函数（除零）:")
    result2 = minimal_error_handling(10, 0)
    print(f"最小化错误处理结果: {result2}")
    
    # 执行有风险的除法函数（除零）
    print("\n执行有风险的除法函数（除零）:")
    try:
        risky_divide(10, 0)
    except ZeroDivisionError:
        print("异常已被重新抛出并在外部捕获")


# 4. 异步函数支持示例
async def demo_async_function_support():
    """演示log_wraps装饰器对异步函数的支持"""
    print("\n=== 4. 异步函数支持示例 ===")
    
    # 装饰异步函数
    @logging_wraps
    async def async_task(task_name: str, duration: float) -> str:
        """异步任务示例"""
        await asyncio.sleep(duration)  # 模拟异步操作
        return f"Task '{task_name}' completed after {duration} seconds"
    
    # 装饰会抛出异常的异步函数
    @logging_wraps(re_raise=False, default_return="Task failed")
    async def failing_async_task():
        """会失败的异步任务"""
        await asyncio.sleep(0.1)
        raise ValueError("模拟异步任务失败")
    
    # 执行异步函数
    result1 = await async_task("Task 1", 0.2)
    print(f"异步任务结果: {result1}")
    
    # 并发执行多个异步任务
    print("\n并发执行多个异步任务:")
    tasks = [
        async_task("Concurrent Task 1", 0.3),
        async_task("Concurrent Task 2", 0.1),
        async_task("Concurrent Task 3", 0.2)
    ]
    results = await asyncio.gather(*tasks)
    print(f"并发任务结果: {results}")
    
    # 执行会失败的异步任务
    print("\n执行会失败的异步任务:")
    result2 = await failing_async_task()
    print(f"失败任务的返回值: {result2}")


# 5. 实际应用场景示例
def demo_real_world_scenarios():
    """演示log_wraps装饰器在实际应用场景中的使用"""
    print("\n=== 5. 实际应用场景示例 ===")
    
    # 场景1: API服务日志记录
    @logging_wraps(log_args=True, log_result=True)
    def api_endpoint_handler(endpoint: str, request_data: dict[str, Any]) -> dict[str, Any]:
        """模拟API端点处理函数"""
        # 模拟处理时间
        time.sleep(0.1)
        
        # 模拟处理结果
        return {
            'status': 'success',
            'data': f'Processed {endpoint}',
            'received_data_size': len(str(request_data))
        }
    
    # 场景2: 数据库操作日志记录
    @logging_wraps(re_raise=False, default_return=None, log_traceback=True)
    def database_operation(query: str, params: list[Any] | None = None) -> list[dict[str, Any]] | None:
        """模拟数据库操作函数"""
        # 模拟数据库操作
        time.sleep(0.15)
        
        # 模拟某些查询会失败
        if 'fail' in query.lower():
            raise RuntimeError("Database query failed")
        
        # 模拟查询结果
        return [{'id': i, 'data': f'Result {i}'} for i in range(3)]
    
    # 场景3: 数据处理管道
    @logging_wraps(log_args=False, log_result=True)
    def process_data_pipeline(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """模拟数据处理管道"""
        # 模拟处理时间
        time.sleep(0.1)
        
        # 模拟数据转换
        processed = []
        for item in data:
            processed_item = {
                **item,
                'processed': True,
                'timestamp': time.time()
            }
            processed.append(processed_item)
        
        return processed
    
    # 运行示例
    print("\n--- API服务日志记录示例 ---")
    api_result = api_endpoint_handler(
        "/users/profile", 
        {'user_id': 123, 'fields': ['name', 'email']}
    )
    print(f"API结果: {api_result}")
    
    print("\n--- 数据库操作日志记录示例 ---")
    db_success = database_operation("SELECT * FROM users")
    print(f"数据库成功查询结果: {db_success}")
    
    db_failure = database_operation("SELECT * FROM fail_table")
    print(f"数据库失败查询返回值: {db_failure}")
    
    print("\n--- 数据处理管道示例 ---")
    raw_data = [
        {'id': 1, 'name': 'Item 1'},
        {'id': 2, 'name': 'Item 2'},
        {'id': 3, 'name': 'Item 3'}
    ]
    processed_data = process_data_pipeline(raw_data)
    print(f"处理后的数据数量: {len(processed_data)}")


# 6. 复杂对象日志记录示例
def demo_complex_object_logging():
    """演示log_wraps装饰器对复杂对象的日志记录"""
    print("\n=== 6. 复杂对象日志记录示例 ===")
    
    # 定义一个复杂对象类
    class DataProcessor:
        def __init__(self, name: str, version: str):
            self.name = name
            self.version = version
            
        def __str__(self):
            return f"DataProcessor(name={self.name}, version={self.version})"
        
        def __repr__(self):
            return self.__str__()
    
    # 使用logging_wraps装饰处理复杂对象的函数
    @logging_wraps
    def process_complex_data(processor: DataProcessor, data: list[dict[str, Any]]) -> dict[str, Any]:
        """处理包含复杂对象的函数"""
        time.sleep(0.1)
        
        # 模拟处理结果
        return {
            'processor': f"{processor.name} v{processor.version}",
            'processed_count': len(data),
            'timestamp': time.time()
        }
    
    # 创建复杂对象并执行函数
    processor = DataProcessor("AdvancedProcessor", "1.2.3")
    complex_data = [{'value': i, 'category': f'cat_{i % 3}'} for i in range(5)]
    
    result = process_complex_data(processor, complex_data)
    print(f"复杂对象处理结果: {result}")


# 主函数
async def main():
    """运行所有示例"""
    print("===== log.py 模块示例程序 =====")
    
    # 运行同步示例
    demo_basic_logging()
    demo_configuration_options()
    demo_exception_handling()
    demo_real_world_scenarios()
    demo_complex_object_logging()
    
    # 运行异步示例
    await demo_async_function_support()
    
    print("\n===== 所有示例运行完成 =====")


if __name__ == "__main__":
    # 如果是在__main__上下文中运行，执行主函数
    asyncio.run(main())