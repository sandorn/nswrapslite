# !/usr/bin/env python3
"""
xt_wraps.timer模块示例程序
本示例演示如何使用timer模块中的计时功能
包括：timer_wraps装饰器、TimerWrapt类作为装饰器和上下文管理器的使用
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

from xtlog import mylog

from nswrapslite.timer import TimerWrapt, timer, timer_wraps

# 配置日志级别
mylog.set_level('INFO')


def demo_basic_timer_wraps():
    """演示基本的timer_wraps装饰器功能"""
    print("\n=== 演示基本的timer_wraps装饰器功能 ===")
    
    # 方式1: 直接装饰同步函数
    @timer_wraps
    def calculate_sum(a: int, b: int) -> int:
        """计算两个数的和"""
        time.sleep(0.1)  # 模拟耗时操作
        return a + b
    
    # 方式2: 带括号装饰函数
    @timer_wraps()
    def complex_calculation(data: list[int]) -> tuple[int, float]:
        """执行复杂计算，返回总和和平均值"""
        time.sleep(0.2)  # 模拟耗时操作
        total = sum(data)
        avg = total / len(data) if data else 0
        return total, avg
    
    # 方式3: 使用别名timer
    @timer
    def fibonacci(n: int) -> int:
        """计算斐波那契数列的第n个数"""
        time.sleep(0.05)  # 模拟耗时操作
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    # 测试函数
    print("计算两个数的和:")
    result1 = calculate_sum(3, 5)
    print(f"结果: {result1}")
    
    print("\n执行复杂计算:")
    data = [1, 2, 3, 4, 5]
    total, avg = complex_calculation(data)
    print(f"数据: {data}")
    print(f"总和: {total}, 平均值: {avg}")
    
    print("\n计算斐波那契数列:")
    # 注意：这里使用小数值避免过多的递归调用
    fib_result = fibonacci(5)
    print(f"斐波那契数列第5个数: {fib_result}")


def demo_async_timer_wraps():
    """演示timer_wraps装饰器对异步函数的支持"""
    print("\n=== 演示timer_wraps装饰器对异步函数的支持 ===")
    
    # 装饰异步函数
    @timer_wraps
    async def fetch_data(url: str, delay: float = 0.3) -> dict[str, Any]:
        """模拟异步获取数据"""
        await asyncio.sleep(delay)  # 模拟网络延迟
        return {
            "url": url,
            "data": f"从{url}获取的数据",
            "timestamp": time.time(),
            "delay": delay
        }
    
    # 装饰异步函数（使用别名timer）
    @timer
    async def process_data_async(items: list[str], process_time: float = 0.1) -> list[dict[str, Any]]:
        """异步处理多个数据项"""
        results = []
        for item in items:
            await asyncio.sleep(process_time)  # 模拟处理时间
            results.append({
                "item": item,
                "processed": True,
                "timestamp": time.time()
            })
        return results
    
    # 测试异步函数
    async def test_async_functions():
        print("异步获取数据:")
        data = await fetch_data("https://api.example.com/users")
        print(f"获取结果: {data}")
        
        print("\n异步处理多个数据项:")
        items = ["item1", "item2", "item3"]
        processed_items = await process_data_async(items)
        print(f"处理的项目数: {len(processed_items)}")
    
    # 运行异步测试
    asyncio.run(test_async_functions())


def demo_timer_with_exceptions():
    """演示异常情况下的计时器功能"""
    print("\n=== 演示异常情况下的计时器功能 ===")
    
    # 会抛出异常的同步函数
    @timer_wraps
    def unstable_operation(param: int) -> None:
        """不稳定的操作，可能会抛出异常"""
        time.sleep(0.15)  # 模拟操作耗时
        if param < 0:
            raise ValueError("参数不能为负数")
        if param > 10:
            raise OverflowError("参数过大")
        print(f"成功处理参数: {param}")
    
    # 会抛出异常的异步函数
    @timer
    async def async_unstable_operation(param: int) -> None:
        """不稳定的异步操作，可能会抛出异常"""
        await asyncio.sleep(0.2)  # 模拟异步操作耗时
        if param % 2 == 0:
            raise ConnectionError(f"异步操作失败，参数{param}是偶数")
        print(f"成功处理异步参数: {param}")
    
    # 测试同步函数异常
    print("测试同步函数异常:")
    try:
        unstable_operation(-5)
    except ValueError as e:
        print(f"捕获到预期异常: {e}")
    
    try:
        unstable_operation(15)
    except OverflowError as e:
        print(f"捕获到预期异常: {e}")
    
    # 正常情况
    unstable_operation(5)
    
    # 测试异步函数异常
    async def test_async_exceptions():
        print("\n测试异步函数异常:")
        try:
            await async_unstable_operation(4)
        except ConnectionError as e:
            print(f"捕获到预期异步异常: {e}")
        
        # 正常情况
        await async_unstable_operation(3)
    
    # 运行异步测试
    asyncio.run(test_async_exceptions())


def demo_timer_wrapt_as_decorator():
    """演示TimerWrapt类作为装饰器使用"""
    print("\n=== 演示TimerWrapt类作为装饰器使用 ===")
    
    # 使用TimerWrapt装饰同步函数
    @TimerWrapt
    def data_processing_task(data: list[int]) -> dict[str, Any]:
        """处理数据的任务"""
        time.sleep(0.1)
        return {
            "count": len(data),
            "sum": sum(data),
            "min": min(data),
            "max": max(data)
        }
    
    # 使用TimerWrapt装饰异步函数
    @TimerWrapt
    async def async_data_analysis(data: dict[str, Any]) -> dict[str, Any]:
        """异步数据分析任务"""
        await asyncio.sleep(0.2)
        return {
            "keys": list(data.keys()),
            "values": list(data.values()),
            "size": len(data),
            "analysis_time": time.time()
        }
    
    # 测试同步函数
    print("测试TimerWrapt装饰的同步函数:")
    data = [10, 20, 30, 40, 50]
    result = data_processing_task(data)
    print(f"数据: {data}")
    print(f"处理结果: {result}")
    
    # 测试异步函数
    async def test_async_decorator():
        print("\n测试TimerWrapt装饰的异步函数:")
        data_dict = {"a": 1, "b": 2, "c": 3, "d": 4}
        analysis_result = await async_data_analysis(data_dict)
        print(f"分析结果: {analysis_result}")
    
    # 运行异步测试
    asyncio.run(test_async_decorator())


def demo_timer_wrapt_as_context_manager():
    """演示TimerWrapt类作为上下文管理器使用"""
    print("\n=== 演示TimerWrapt类作为上下文管理器使用 ===")
    
    # 基本上下文管理器用法
    print("基本上下文管理器用法:")
    with TimerWrapt("数据处理块"):
        # 模拟数据处理
        time.sleep(0.2)
        data = [i * 2 for i in range(10)]
        print(f"处理后的数据: {data}")
    
    # 带描述的上下文管理器
    print("\n带描述的上下文管理器:")
    with TimerWrapt("复杂计算操作"):
        # 模拟复杂计算
        total = 0
        for i in range(100000):
            total += i
        print(f"计算结果: {total}")
    
    # 异常情况下的上下文管理器
    print("\n异常情况下的上下文管理器:")
    try:
        with TimerWrapt("可能抛出异常的操作"):
            time.sleep(0.1)
            # 故意抛出异常
            raise RuntimeError("测试异常情况下的计时器")
    except RuntimeError as e:
        print(f"捕获到预期异常: {e}")
    
    # 异步上下文管理器
    async def test_async_context_manager():
        print("\n异步上下文管理器:")
        async with TimerWrapt("异步数据处理"):
            # 模拟异步操作
            await asyncio.sleep(0.3)
            await asyncio.gather(
                asyncio.sleep(0.1),
                asyncio.sleep(0.2)
            )
            print("异步操作完成")
        
        # 异步上下文管理器异常情况
        print("\n异步上下文管理器异常情况:")
        try:
            async with TimerWrapt("可能失败的异步操作"):
                await asyncio.sleep(0.1)
                # 故意抛出异步异常
                raise ConnectionError("测试异步异常")
        except ConnectionError as e:
            print(f"捕获到预期异步异常: {e}")
    
    # 运行异步上下文管理器测试
    asyncio.run(test_async_context_manager())


def demo_timer_combinations():
    """演示计时器装饰器与其他装饰器的组合使用"""
    print("\n=== 演示计时器装饰器与其他装饰器的组合使用 ===")
    
    # 导入其他装饰器（如果可用）
    try:
        from xt_wraps.exception import exc_wraps
        from xt_wraps.log import log_wraps
        
        # 组合多个装饰器
        @log_wraps
        @timer_wraps
        @exc_wraps(default_return={"status": "error", "message": "操作失败"})
        def combined_operation(param: int) -> dict[str, Any]:
            """组合了日志、计时和异常处理的操作"""
            time.sleep(0.15)
            if param < 0:
                raise ValueError("参数不能为负数")
            return {
                "status": "success",
                "result": param * 2,
                "timestamp": time.time()
            }
        
        # 异步函数组合装饰器
        @log_wraps
        @timer
        @exc_wraps(default_return={"status": "error", "async": True})
        async def async_combined_operation(param: str) -> dict[str, Any]:
            """异步组合装饰器操作"""
            await asyncio.sleep(0.2)
            if len(param) < 3:
                raise ValueError("参数长度必须大于等于3")
            return {
                "status": "success",
                "processed": param.upper(),
                "length": len(param),
                "timestamp": time.time()
            }
        
        # 测试同步函数组合装饰器
        print("\n测试同步函数组合装饰器:")
        # 正常情况
        result1 = combined_operation(5)
        print(f"正常情况结果: {result1}")
        
        # 异常情况
        result2 = combined_operation(-3)
        print(f"异常情况结果: {result2}")
        
        # 测试异步函数组合装饰器
        async def test_async_combined():
            print("\n测试异步函数组合装饰器:")
            # 正常情况
            result3 = await async_combined_operation("test")
            print(f"正常情况结果: {result3}")
            
            # 异常情况
            result4 = await async_combined_operation("ab")
            print(f"异常情况结果: {result4}")
        
        # 运行异步测试
        asyncio.run(test_async_combined())
        
    except ImportError as e:
        print(f"\n警告: 无法导入其他装饰器模块 ({e})")
        print("请确保xt_wraps.log和xt_wraps.exception模块可用")


def demo_practical_applications():
    """演示计时器在实际应用场景中的使用"""
    print("\n=== 演示计时器在实际应用场景中的使用 ===")
    
    # 场景1: 性能监控
    print("\n场景1: 性能监控")
    
    @timer_wraps
    def database_query(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """模拟数据库查询"""
        # 模拟数据库查询耗时
        time.sleep(random.uniform(0.1, 0.5))
        
        # 模拟返回结果
        return [
            {"id": 1, "name": "用户1", "value": 100},
            {"id": 2, "name": "用户2", "value": 200}
        ]
    
    # 场景2: 性能比较
    print("\n场景2: 性能比较")
    
    @timer
    def sort_method_1(data: list[int]) -> list[int]:
        """使用内置sort方法"""
        data_copy = data.copy()
        data_copy.sort()
        return data_copy
    
    @timer
    def sort_method_2(data: list[int]) -> list[int]:
        """使用sorted函数"""
        return sorted(data)
    
    # 场景3: 异步API调用性能监控
    print("\n场景3: 异步API调用性能监控")
    
    @timer_wraps
    async def api_call_chain(urls: list[str]) -> list[dict[str, Any]]:
        """异步调用多个API"""
        results = []
        for url in urls:
            # 模拟API调用
            result = await fetch_api_data(url)
            results.append(result)
        return results
    
    async def fetch_api_data(url: str) -> dict[str, Any]:
        """模拟获取API数据"""
        await asyncio.sleep(random.uniform(0.2, 0.8))
        return {
            "url": url,
            "status": 200,
            "data": f"来自{url}的数据",
            "timestamp": time.time()
        }
    
    # 场景4: 复杂业务流程性能分析
    print("\n场景4: 复杂业务流程性能分析")
    
    class OrderProcessor:
        def __init__(self):
            """初始化订单处理器"""
            pass
        
        @TimerWrapt("验证订单")
        def validate_order(self, order: dict[str, Any]) -> bool:
            """验证订单"""
            time.sleep(0.1)
            # 简单验证逻辑
            return order.get('items') and len(order['items']) > 0
        
        @TimerWrapt("计算价格")
        def calculate_price(self, order: dict[str, Any]) -> float:
            """计算订单总价"""
            time.sleep(0.15)
            total = 0.0
            for item in order.get('items', []):
                total += item.get('price', 0) * item.get('quantity', 0)
            return total
        
        @TimerWrapt("处理支付")
        def process_payment(self, amount: float) -> dict[str, str]:
            """处理支付"""
            time.sleep(0.2)
            return {
                "status": "success",
                "transaction_id": f"txn_{int(time.time())}",
                "amount": amount
            }
        
        @timer_wraps
        def complete_order(self, order: dict[str, Any]) -> dict[str, Any]:
            """完成整个订单处理流程"""
            # 使用上下文管理器监控各个阶段
            with TimerWrapt("订单处理总流程"):
                # 验证订单
                if not self.validate_order(order):
                    raise ValueError("订单无效")
                
                # 计算价格
                total_price = self.calculate_price(order)
                order['total_price'] = total_price
                
                # 处理支付
                payment_result = self.process_payment(total_price)
                order['payment_status'] = payment_result['status']
                order['transaction_id'] = payment_result['transaction_id']
                
                # 返回最终订单
                return order
    
    # 运行实际应用场景测试
    import random  # 导入random模块用于性能比较
    
    # 场景1测试
    print("\n运行数据库查询性能监控:")
    db_result = database_query("SELECT * FROM users WHERE active = true")
    print(f"查询结果数量: {len(db_result)}")
    
    # 场景2测试
    print("\n运行排序方法性能比较:")
    test_data = [random.randint(1, 1000) for _ in range(10000)]
    
    result1 = sort_method_1(test_data)
    result2 = sort_method_2(test_data)
    
    print(f"排序结果一致性: {result1 == result2}")
    
    # 场景3测试
    async def test_api_chain():
        print("\n运行异步API调用链性能监控:")
        urls = [
            "https://api.example.com/users",
            "https://api.example.com/products",
            "https://api.example.com/orders"
        ]
        api_results = await api_call_chain(urls)
        print(f"API调用成功数量: {len(api_results)}")
    
    asyncio.run(test_api_chain())
    
    # 场景4测试
    print("\n运行订单处理流程性能分析:")
    processor = OrderProcessor()
    
    order = {
        "id": "order_123",
        "customer_id": "cust_456",
        "items": [
            {"id": "item_1", "name": "商品1", "price": 99.99, "quantity": 2},
            {"id": "item_2", "name": "商品2", "price": 49.99, "quantity": 1}
        ]
    }
    
    try:
        completed_order = processor.complete_order(order)
        print(f"订单处理完成，交易ID: {completed_order['transaction_id']}")
        print(f"订单总价: {completed_order['total_price']}")
    except Exception as e:
        print(f"订单处理失败: {e}")


def main():
    """主函数，运行所有演示"""
    print("===== xt_wraps.timer模块示例程序 =====")
    
    # 基本功能演示
    demo_basic_timer_wraps()
    demo_async_timer_wraps()
    demo_timer_with_exceptions()
    
    # TimerWrapt类的使用
    demo_timer_wrapt_as_decorator()
    demo_timer_wrapt_as_context_manager()
    
    # 高级功能
    demo_timer_combinations()
    
    # 实际应用场景
    demo_practical_applications()
    
    print("\n===== 示例程序运行完毕 =====")


if __name__ == "__main__":
    main()