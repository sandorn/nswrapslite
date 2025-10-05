# !/usr/bin/env python3

"""
xt_wraps/exception.py 模块示例程序

本示例展示了 exception.py 模块中异常处理功能的使用方法，包括：
- _handle_exception 函数的基本使用
- exc_wraps 装饰器的不同配置选项
- 同步和异步函数的异常处理
- 自定义异常处理函数
- 允许特定异常类型的处理
- 实际应用场景示例
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

from xtlog import mylog

# 导入 exception 模块中的函数
from nswrapslite.exception import _handle_exception, exception_wraps

# 配置日志级别
mylog.set_level('INFO')


def demo_basic_exception_handling() -> None:
    """演示 _handle_exception 函数的基本使用"""
    print("\n=== 演示 _handle_exception 函数的基本使用 ===")
    
    # 示例1: 捕获异常但不重新抛出
    print("\n示例1: 捕获异常但不重新抛出")
    try:
        result = 10 / 0
    except Exception as e:
        result = _handle_exception(e, re_raise=False, default_return=0)
        print(f"捕获异常后的返回值: {result}")
    
    # 示例2: 捕获异常并重新抛出
    print("\n示例2: 捕获异常并重新抛出")
    try:
        try:
            result = 10 / 0
        except Exception as e:
            _handle_exception(e, re_raise=True)
    except Exception as e:
        print(f"成功捕获重新抛出的异常: {type(e).__name__}: {e}")
    
    # 示例3: 使用自定义消息
    print("\n示例3: 使用自定义消息")
    try:
        result = 10 / 0
    except Exception as e:
        _handle_exception(
            e, 
            re_raise=False, 
            default_return=None, 
            custom_message="除法运算失败"
        )
    
    # 示例4: 不记录堆栈信息
    print("\n示例4: 不记录堆栈信息")
    try:
        result = 10 / 0
    except Exception as e:
        _handle_exception(
            e, 
            re_raise=False, 
            default_return=0, 
            log_traceback=False, 
            custom_message="简化的异常处理"
        )


def demo_exc_wraps_decorator() -> None:
    """演示 exc_wraps 装饰器的基本使用"""
    print("\n=== 演示 exc_wraps 装饰器的基本使用 ===")
    
    # 示例1: 基本用法，默认重新抛出异常
    print("\n示例1: 基本用法，默认重新抛出异常")

    @exception_wraps()
    def divide1(a: int, b: int) -> float:
        """除法函数"""
        return a / b
    
    try:
        result = divide1(10, 0)
    except Exception as e:
        print(f"捕获到默认重新抛出的异常: {type(e).__name__}: {e}")
    
    # 示例2: 捕获异常但不重新抛出，返回默认值
    print("\n示例2: 捕获异常但不重新抛出，返回默认值")

    @exception_wraps(re_raise=False, default_return=0)
    def divide2(a: int, b: int) -> float:
        """安全的除法函数"""
        return a / b
    
    result = divide2(10, 0)
    print(f"除法结果 (异常情况下返回默认值): {result}")
    
    # 示例3: 使用自定义错误消息
    print("\n示例3: 使用自定义错误消息")

    @exception_wraps(re_raise=False, default_return=0, custom_message="执行除法操作时发生错误")
    def divide3(a: int, b: int) -> float:
        """带有自定义错误消息的除法函数"""
        return a / b
    
    result = divide3(10, 0)
    print(f"除法结果: {result}")
    
    # 示例4: 不记录堆栈信息
    print("\n示例4: 不记录堆栈信息")

    @exception_wraps(re_raise=False, default_return=0, log_traceback=False)
    def divide4(a: int, b: int) -> float:
        """不记录堆栈信息的除法函数"""
        return a / b
    
    result = divide4(10, 0)
    print(f"除法结果: {result}")


def demo_custom_exception_handler() -> None:
    """演示自定义异常处理函数"""
    print("\n=== 演示自定义异常处理函数 ===")
    
    # 定义自定义异常处理函数
    def custom_handler(exc: Exception) -> dict[str, Any]:
        """自定义异常处理函数"""
        # 记录异常信息到字典
        error_info = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "timestamp": time.time(),
            "handled": True
        }
        
        # 根据异常类型进行不同处理
        if isinstance(exc, ZeroDivisionError):
            error_info["suggestion"] = "除数不能为零"
        elif isinstance(exc, ValueError):
            error_info["suggestion"] = "请检查输入值是否正确"
        else:
            error_info["suggestion"] = "请联系系统管理员"
        
        # 返回处理后的信息
        return error_info
    
    # 使用自定义异常处理函数的装饰器
    @exception_wraps(re_raise=False, handler=custom_handler)
    def process_data(value: int, divisor: int) -> float:
        """处理数据的函数"""
        if value < 0:
            raise ValueError("输入值不能为负数")
        return value / divisor
    
    # 测试1: 除零异常
    print("\n测试1: 除零异常")
    result1 = process_data(10, 0)
    print(f"异常处理结果: {result1}")
    
    # 测试2: 数值异常
    print("\n测试2: 数值异常")
    result2 = process_data(-5, 2)
    print(f"异常处理结果: {result2}")
    
    # 测试3: 正常情况
    print("\n测试3: 正常情况")
    result3 = process_data(10, 2)
    print(f"正常处理结果: {result3}")


def demo_specific_exception_types() -> None:
    """演示允许特定异常类型的处理"""
    print("\n=== 演示允许特定异常类型的处理 ===")
    
    # 只捕获特定类型的异常
    @exception_wraps(
        re_raise=False, 
        default_return=None, 
        allowed_exceptions=(ZeroDivisionError, ValueError),
        custom_message="处理允许的异常类型"
    )
    def process_with_specific_exceptions(value: Any, divisor: Any) -> Any:
        """只处理特定异常类型的函数"""
        # 转换为整数
        int_value = int(value)
        int_divisor = int(divisor)
        # 执行除法
        return int_value / int_divisor
    
    # 测试1: 除零异常 (被捕获)
    print("\n测试1: 除零异常 (被捕获)")
    result1 = process_with_specific_exceptions(10, 0)
    print(f"结果: {result1}")
    
    # 测试2: 数值转换异常 (被捕获)
    print("\n测试2: 数值转换异常 (被捕获)")
    result2 = process_with_specific_exceptions("abc", 2)
    print(f"结果: {result2}")
    
    # 测试3: 其他类型的异常 (不会被捕获，会抛出)
    print("\n测试3: 其他类型的异常 (不会被捕获，会抛出)")
    try:
        # 创建一个列表，然后尝试访问超出范围的索引
        data = [1, 2, 3]
        process_with_specific_exceptions(data[5], 2)  # 这会引发 IndexError
    except IndexError as e:
        print(f"捕获到未被允许的异常: {type(e).__name__}: {e}")


async def demo_async_exception_handling() -> None:
    """演示异步函数的异常处理"""
    print("\n=== 演示异步函数的异常处理 ===")
    
    # 异步函数使用 exception_wraps 装饰器
    @exception_wraps(re_raise=False, default_return="异步操作失败")
    async def async_operation(value: int, delay: float) -> str:
        """模拟异步操作"""
        print(f"开始异步操作，延迟 {delay} 秒")
        await asyncio.sleep(delay)
        if value < 0:
            raise ValueError("异步操作中的值不能为负数")
        return f"异步操作成功，结果: {value * 2}"
    
    # 测试1: 正常的异步操作
    print("\n测试1: 正常的异步操作")
    result1 = await async_operation(10, 0.5)
    print(f"异步操作结果: {result1}")
    
    # 测试2: 异步操作中的异常
    print("\n测试2: 异步操作中的异常")
    result2 = await async_operation(-5, 0.3)
    print(f"异步操作结果: {result2}")
    
    # 测试3: 异步函数中重新抛出异常
    @exception_wraps(re_raise=True, custom_message="重要的异步操作失败")
    async def critical_async_operation(value: int) -> str:
        """重要的异步操作，失败时重新抛出异常"""
        await asyncio.sleep(0.2)
        if value == 0:
            raise RuntimeError("关键操作中值不能为零")
        return f"关键异步操作成功: {value}"
    
    print("\n测试3: 异步函数中重新抛出异常")
    try:
        await critical_async_operation(0)
    except RuntimeError as e:
        print(f"捕获到重新抛出的异步异常: {type(e).__name__}: {e}")


def demo_real_world_application() -> None:
    """演示异常处理在实际应用中的使用场景"""
    print("\n=== 演示异常处理在实际应用中的使用场景 ===")
    
    # 场景1: 数据库操作中的异常处理
    class Database:
        def __init__(self):
            # 模拟数据库连接状态
            self.connected = False
        
        def connect(self) -> bool:
            """模拟数据库连接"""
            # 随机模拟连接失败
            import random
            if random.random() < 0.3:  # 30% 的概率连接失败
                raise ConnectionError("数据库连接失败")
            self.connected = True
            return True
        
        def query(self, sql: str) -> list[dict[str, Any]]:
            """模拟数据库查询"""
            if not self.connected:
                raise RuntimeError("数据库未连接")
            # 模拟查询结果
            if "users" in sql.lower():
                return [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}]
            if "products" in sql.lower():
                return [{"id": 101, "name": "产品A"}, {"id": 102, "name": "产品B"}]
            raise ValueError(f"不支持的查询: {sql}")
    
    # 使用装饰器处理数据库操作异常
    @exception_wraps(
        re_raise=False, 
        default_return=[], 
        custom_message="数据库查询操作失败",
        allowed_exceptions=(ConnectionError, RuntimeError, ValueError)
    )
    def safe_db_query(db: Database, sql: str) -> list[dict[str, Any]]:
        """安全的数据库查询函数"""
        if not db.connected:
            db.connect()
        return db.query(sql)
    
    # 测试数据库操作
    print("\n测试数据库操作:")
    db = Database()
    
    # 测试1: 查询用户表
    print("\n测试1: 查询用户表")
    users = safe_db_query(db, "SELECT * FROM users")
    print(f"查询结果: {users}")
    
    # 测试2: 查询不存在的表
    print("\n测试2: 查询不存在的表")
    invalid = safe_db_query(db, "SELECT * FROM non_existent_table")
    print(f"查询结果: {invalid}")
    
    # 场景2: API请求处理
    @exception_wraps(
        re_raise=False, 
        handler=lambda exc: {"error": str(exc), "status": 500}, 
        custom_message="API请求处理失败"
    )
    def handle_api_request(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """处理API请求"""
        # 模拟API请求处理
        if endpoint not in ["/users", "/products", "/orders"]:
            raise ValueError(f"无效的API端点: {endpoint}")
        
        # 检查必要参数
        if "id" in params and not isinstance(params["id"], int):
            raise TypeError("参数'id'必须是整数")
        
        # 模拟返回数据
        return {
            "success": True,
            "data": {
                "endpoint": endpoint,
                "params": params,
                "timestamp": time.time()
            },
            "status": 200
        }
    
    # 测试API请求处理
    print("\n测试API请求处理:")
    
    # 测试1: 有效的API请求
    print("\n测试1: 有效的API请求")
    api_result1 = handle_api_request("/users", {"id": 1})
    print(f"API响应: {api_result1}")
    
    # 测试2: 无效的API端点
    print("\n测试2: 无效的API端点")
    api_result2 = handle_api_request("/invalid", {"id": 1})
    print(f"API响应: {api_result2}")
    
    # 测试3: 参数类型错误
    print("\n测试3: 参数类型错误")
    api_result3 = handle_api_request("/products", {"id": "invalid"})
    print(f"API响应: {api_result3}")


def main() -> None:
    """主函数，运行所有示例"""
    print("=== xt_wraps/exception.py 模块示例程序 ===")
    
    # 运行同步示例
    demo_basic_exception_handling()
    demo_exc_wraps_decorator()
    demo_custom_exception_handler()
    demo_specific_exception_types()
    demo_real_world_application()
    
    # 运行异步示例
    print("\n运行异步示例...")
    asyncio.run(demo_async_exception_handling())
    
    print("\n=== 所有示例运行完毕 ===")


if __name__ == "__main__":
    main()