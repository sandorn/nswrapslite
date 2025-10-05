# !/usr/bin/env python3
"""
==============================================================
Description  : xt_wraps模块装饰器组合示例
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-01 13:30:00
Github       : https://github.com/sandorn

演示xt_wraps模块中多个装饰器的组合使用方法
==============================================================
"""
from __future__ import annotations

import asyncio
import time

from xtlog import mylog

from nswrapslite import cache_wrapper, exception_wraps, logging_wraps, singleton, timing_decorator
from nswrapslite.retry import retry_async_wraps, retry_wraps

# 配置日志级别
mylog.set_level('INFO')


# 示例1：基本API调用装饰器组合
def demo_api_calls():
    """演示API调用中常用的装饰器组合"""
    print("\n=== API调用装饰器组合示例 ===")
    
    # 模拟API请求函数
    @retry_wraps(max_retries=3, delay=1, exceptions=(ConnectionError, TimeoutError))
    @cache_wrapper(maxsize=20)  # 缓存示例
    @timing_decorator
    @logging_wraps(log_args=True, log_result=False)
    def api_get_data(endpoint: str, params: dict | None = None) -> dict:
        """模拟API GET请求"""
        print(f"实际发送请求到: {endpoint}")
        
        # 模拟网络延迟
        time.sleep(0.5)
        
        # 模拟某些端点可能失败
        if endpoint == "/api/fail" and not hasattr(api_get_data, "_succeeded_once"):
            api_get_data._succeeded_once = True
            raise ConnectionError("网络连接失败，模拟重试场景")
        
        # 返回模拟数据
        return {
            "endpoint": endpoint,
            "params": params,
            "data": [1, 2, 3],
            "timestamp": time.time()
        }
    
    # 测试API调用
    try:
        # 第一次调用 - 会执行实际请求
        start = time.time()
        result1 = api_get_data("/api/users", {"page": 1})
        print(f"第一次API调用耗时: {time.time() - start:.4f}秒")
        print(f"结果: {result1}")
        
        # 第二次调用相同参数 - 应该从缓存获取
        start = time.time()
        result2 = api_get_data("/api/users", {"page": 1})
        print(f"第二次API调用耗时: {time.time() - start:.4f}秒")
        print(f"结果: {result2}")
        
        # 测试失败并重试的场景
        start = time.time()
        result3 = api_get_data("/api/fail")
        print(f"失败重试API调用耗时: {time.time() - start:.4f}秒")
        print(f"结果: {result3}")
        
    except Exception as e:
        print(f"API调用出错: {e}")


# 示例2：数据库操作装饰器组合
def demo_database_operations():
    """演示数据库操作中常用的装饰器组合"""
    print("\n=== 数据库操作装饰器组合示例 ===")
    
    # 模拟数据库服务类
    @singleton
    class DatabaseService:
        """数据库服务单例类"""
        def __init__(self):
            self.connected = False
            print("初始化数据库服务")
            self.connect()
        
        def connect(self):
            """模拟数据库连接"""
            print("连接到数据库...")
            time.sleep(0.3)  # 模拟连接耗时
            self.connected = True
            print("数据库连接成功")
        
        @retry_wraps(max_retries=2, delay=0.5, exceptions=(RuntimeError,))
        @exception_wraps(default_return=None, log_traceback=True, re_raise=False)
        @logging_wraps(log_args=True, log_result=True)
        def execute_query(self, query: str, params: tuple | None = None) -> list:
            """执行数据库查询"""
            if not self.connected:
                raise ConnectionError("数据库未连接")
            
            print(f"执行查询: {query}, 参数: {params}")
            
            # 模拟查询执行
            time.sleep(0.2)
            
            # 模拟随机失败
            import random
            if random.random() < 0.3:
                raise RuntimeError("查询执行失败，模拟重试")
            
            # 返回模拟结果
            return [{"id": i, "name": f"Item {i}"} for i in range(1, 4)]
    
    # 使用数据库服务
    db = DatabaseService()
    db2 = DatabaseService()  # 应该是同一个实例
    print(f"是否是同一个数据库实例: {db is db2}")
    
    # 执行查询
    results = db.execute_query("SELECT * FROM items WHERE category = ?", ("electronics",))
    print(f"查询结果: {results}")
    
    # 测试异常处理
    results = db.execute_query("INVALID SQL SYNTAX")
    print(f"错误SQL查询结果: {results}")


# 示例3：异步工作流装饰器组合
def demo_async_workflows():
    """演示异步工作流中常用的装饰器组合"""
    print("\n=== 异步工作流装饰器组合示例 ===")
    
    # 注意：当前版本的cache_wrapper不支持异步函数
    @retry_async_wraps(max_retries=2, delay=0.5)
    @timing_decorator
    @logging_wraps(log_args=True, log_result=True)
    async def async_fetch_data(source: str, timeout: float = 2.0) -> dict:
        """异步获取数据"""
        print(f"异步从{source}获取数据")
        
        # 模拟异步操作
        await asyncio.sleep(0.8)
        
        # 模拟随机失败
        import random
        if random.random() < 0.3 and not hasattr(async_fetch_data, f"_succeeded_{source}"):
            setattr(async_fetch_data, f"_succeeded_{source}", True)
            raise TimeoutError(f"从{source}获取数据超时")
        
        # 返回模拟数据
        return {
            "source": source,
            "data": [f"{source}_item_{i}" for i in range(1, 4)],
            "timestamp": time.time()
        }
    
    # 异步处理函数，组合多个数据源
    @exception_wraps(default_return={"error": "处理失败"}, log_traceback=True, re_raise=False)
    @logging_wraps(log_args=True, log_result=True)
    async def process_async_workflow():
        """处理异步工作流"""
        # 并发获取多个数据源
        results = await asyncio.gather(
            async_fetch_data("source1"),
            async_fetch_data("source2"),
            async_fetch_data("source3"),
            return_exceptions=True  # 即使部分任务失败也继续执行
        )
        
        # 处理结果
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_count = len([r for r in results if isinstance(r, Exception)])
        
        return {
            "success_count": len(successful_results),
            "failed_count": failed_count,
            "results": successful_results
        }
    
    # 运行异步工作流
    async def run_workflow():
        result = await process_async_workflow()
        print(f"工作流结果: {result}")
        
        # 测试缓存 - 再次调用相同的数据源应该从缓存获取
        start = time.time()
        await async_fetch_data("source1")
        print(f"缓存调用耗时: {time.time() - start:.4f}秒")
    
    asyncio.run(run_workflow())


# 示例4：自定义业务逻辑装饰器组合
def demo_custom_business_logic():
    """演示自定义业务逻辑中的装饰器组合"""
    print("\n=== 自定义业务逻辑装饰器组合示例 ===")
    
    # 模拟用户验证装饰器
    def user_authenticated(func):
        """自定义用户认证装饰器"""
        def wrapper(user_id: int, *args, **kwargs):
            print(f"验证用户 {user_id} 的权限")
            # 模拟简单的用户验证逻辑
            if user_id <= 0:
                raise PermissionError("无效的用户ID")
            return func(user_id, *args, **kwargs)
        return wrapper
    
    # 组合自定义装饰器和nswrapslite装饰器
    @exception_wraps(default_return="操作未完成", log_traceback=True, re_raise=False)
    @user_authenticated  # 自定义装饰器
    @logging_wraps(log_args=True, log_result=True)
    @timing_decorator
    def process_user_order(user_id: int, order_id: str, items: list) -> str:
        """处理用户订单"""
        print(f"处理用户 {user_id} 的订单 {order_id}")
        
        # 模拟处理逻辑
        time.sleep(0.4)
        
        # 模拟某些订单可能失败
        if order_id.startswith("fail"):
            raise ValueError("订单处理失败")
        
        total_items = len(items)
        return f"用户 {user_id} 的订单 {order_id} 已处理，共 {total_items} 件商品"
    
    # 测试订单处理
    result1 = process_user_order(123, "order123", ["item1", "item2", "item3"])
    print(f"订单处理结果: {result1}")
    
    # 测试验证失败
    result2 = process_user_order(-1, "order456", ["item4"])
    print(f"无效用户订单处理结果: {result2}")
    
    # 测试订单失败
    result3 = process_user_order(456, "fail_order", ["item5"])
    print(f"失败订单处理结果: {result3}")


# 主函数，运行所有装饰器组合示例
def main():
    """运行所有装饰器组合示例"""
    print("==== xt_wraps 装饰器组合示例 ====")
    
    demo_api_calls()
    demo_database_operations()
    demo_async_workflows()
    demo_custom_business_logic()
    
    print("\n==== 所有装饰器组合示例运行完毕 ====")


if __name__ == "__main__":
    main()