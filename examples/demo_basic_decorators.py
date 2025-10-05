# !/usr/bin/env python3
"""
==============================================================
Description  : nswrapslite模块基础功能示例
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-01 13:00:00
Github       : https://github.com/sandorn

演示nswrapslite模块中的基本装饰器使用方法
==============================================================
"""
from __future__ import annotations

import asyncio
import time

from xtlog import mylog

from nswrapslite.retry import retry_wraps as retry
from nswrapslite.singleton import singleton
from nswrapslite.wrapped import timing_decorator

# 配置日志级别
mylog.set_level('INFO')


# 演示计时装饰器
def demo_timer():
    """演示计时装饰器的使用"""
    print("\n=== 计时装饰器示例 ===")
    
    @timing_decorator
    def slow_function(duration: float) -> str:
        """一个慢函数示例"""
        time.sleep(duration)
        return f"Slept for {duration} seconds"
    
    @timing_decorator
    async def async_slow_function(duration: float) -> str:
        """异步慢函数示例"""
        await asyncio.sleep(duration)
        return f"Async slept for {duration} seconds"
    
    # 测试同步函数
    result = slow_function(0.5)
    print(f"结果11111: {result}")
    
    # 测试异步函数
    async def run_async():
        result = await async_slow_function(0.3)
        print(f"异步结果: {result}")
    
    asyncio.run(run_async())


# 演示单例模式装饰器
def demo_singleton():
    """演示单例模式装饰器的使用"""
    print("\n=== 单例模式装饰器示例 ===")
    
    @singleton
    class DatabaseConnection:
        """数据库连接类示例"""
        def __init__(self, connection_string: str = "default"):
            self.connection_string = connection_string
            self.connected = False
            print(f"创建连接: {connection_string}")
        
        def connect(self):
            """模拟连接操作"""
            self.connected = True
            print(f"已连接到: {self.connection_string}")
        
        def disconnect(self):
            """模拟断开连接操作"""
            self.connected = False
            print("已断开连接")
    
    # 创建多个实例，但实际上应该是同一个对象
    conn1 = DatabaseConnection("db://localhost:3306")
    conn2 = DatabaseConnection("db://different:3306")  # 注意这里的参数会被忽略
    
    # 验证是否是同一个实例
    print(f"conn1 和 conn2 是否是同一个实例: {conn1 is conn2}")
    print(f"conn1连接字符串: {conn1.connection_string}")
    print(f"conn2连接字符串: {conn2.connection_string}")
    
    # 测试方法调用
    conn1.connect()
    print(f"conn1连接状态: {conn1.connected}")
    print(f"conn2连接状态: {conn2.connected}")


# 演示重试装饰器
def demo_retry():
    """演示重试装饰器的使用"""
    print("\n=== 重试装饰器示例 ===")
    
    # 失败计数器
    fail_counter = [0]
    
    @retry(max_retries=3, delay=0.2, exceptions=(ValueError,))
    def unstable_operation(success_after: int = 2) -> str:
        """不稳定的操作，在指定次数后才会成功"""
        fail_counter[0] += 1
        print(f"操作尝试 #{fail_counter[0]}")
        if fail_counter[0] <= success_after:
            raise ValueError("操作失败，需要重试")
        return "操作成功！"
    
    try:
        result = unstable_operation()
        print(f"最终结果: {result}")
    except Exception as e:
        print(f"所有重试都失败了: {e}")
    
    # 重置计数器
    fail_counter[0] = 0
    
    # 测试异步重试
    @retry(max_retries=2, delay=0.1, exceptions=(ValueError,))
    async def async_unstable_operation() -> str:
        """异步不稳定操作"""
        fail_counter[0] += 1
        print(f"异步操作尝试 #{fail_counter[0]}")
        if fail_counter[0] <= 1:
            raise ValueError("异步操作失败")
        return "异步操作成功！"
    
    async def run_async_retry():
        try:
            result = await async_unstable_operation()
            print(f"异步最终结果: {result}")
        except Exception as e:
            print(f"异步所有重试都失败了: {e}")
    
    asyncio.run(run_async_retry())


# 主函数，运行所有示例
def main():
    """运行所有装饰器示例"""
    print("==== xt_wraps 基础装饰器示例 ====")
    
    demo_timer()
    demo_singleton()
    demo_retry()
    
    print("\n==== 所有示例运行完毕 ====")


if __name__ == "__main__":
    main()