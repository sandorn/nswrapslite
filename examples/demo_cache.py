# !/usr/bin/env python3

"""
nswrapslite/cache.py 模块示例程序

本示例展示了 cache.py 模块中 cache_wrapper 装饰器的使用方法，包括：
- 基本缓存功能
- 缓存大小控制
- 不可哈希参数处理
- 实际应用场景
"""
from __future__ import annotations

import time
from functools import lru_cache
from typing import Any

from xtlog import mylog

from nswrapslite.cache import cache_wrapper

# 配置日志级别
mylog.set_level('INFO')


def demo_basic_cache() -> None:
    """演示 cache_wrapper 的基本缓存功能"""
    print("\n=== 演示基本缓存功能 ===")
    
    # 使用 cache_wrapper 装饰器装饰一个耗时函数
    @cache_wrapper(maxsize=128)
    def expensive_computation(a: int, b: int) -> int:
        """模拟耗时计算"""
        print(f"执行耗时计算: {a} + {b}")
        time.sleep(0.5)  # 模拟耗时操作
        return a + b
    
    # 第一次调用，应该执行计算
    print("第一次调用:")
    mylog.info("开始第一次调用 expensive_computation")
    start_time = time.time()
    result1 = expensive_computation(10, 20)
    elapsed_time1 = time.time() - start_time
    print(f"结果: {result1}, 耗时: {elapsed_time1:.4f}秒")
    mylog.success(f"第一次调用完成，耗时: {elapsed_time1:.4f}秒")
    
    # 第二次调用相同参数，应该使用缓存结果
    print("\n第二次调用相同参数:")
    mylog.info("开始第二次调用 expensive_computation（应该命中缓存）")
    start_time = time.time()
    result2 = expensive_computation(10, 20)
    elapsed_time2 = time.time() - start_time
    print(f"结果: {result2}, 耗时: {elapsed_time2:.4f}秒")
    mylog.success(f"第二次调用完成，耗时: {elapsed_time2:.4f}秒（命中缓存）")
    
    # 验证两次结果相同
    print(f"\n两次结果是否相同: {result1 == result2}")
    print(f"缓存带来的性能提升: {elapsed_time1 / elapsed_time2:.2f}倍")
    
    # 调用不同参数，应该再次执行计算
    print("\n调用不同参数:")
    start_time = time.time()
    result3 = expensive_computation(20, 30)
    elapsed_time3 = time.time() - start_time
    print(f"结果: {result3}, 耗时: {elapsed_time3:.4f}秒")


def demo_cache_size_control() -> None:
    """演示 cache_wrapper 的缓存大小控制"""
    print("\n=== 演示缓存大小控制 ===")
    
    # 创建一个小缓存大小的装饰器
    @cache_wrapper(maxsize=3)  # 只缓存3个不同的调用结果
    def fibonacci(n: int) -> int:
        """计算斐波那契数列的第n个数（使用递归，便于观察缓存效果）"""
        print(f"计算斐波那契数: fibonacci({n})")
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    # 测试缓存大小限制
    print("\n第一次计算 fibonacci(5):")
    start_time = time.time()
    result = fibonacci(5)
    elapsed_time = time.time() - start_time
    print(f"结果: {result}, 耗时: {elapsed_time:.4f}秒")
    
    # 此时应该缓存了 fibonacci(0), fibonacci(1), fibonacci(2), fibonacci(3), fibonacci(4), fibonacci(5)
    # 但由于 maxsize=3，只有最近的3个结果会被缓存
    
    print("\n再次计算 fibonacci(5):")
    start_time = time.time()
    result = fibonacci(5)
    elapsed_time = time.time() - start_time
    print(f"结果: {result}, 耗时: {elapsed_time:.4f}秒")
    
    # 计算更大的数，观察缓存替换
    print("\n计算 fibonacci(6):")
    start_time = time.time()
    result = fibonacci(6)
    elapsed_time = time.time() - start_time
    print(f"结果: {result}, 耗时: {elapsed_time:.4f}秒")


def demo_unhashable_params() -> None:
    """演示 cache_wrapper 对不可哈希参数的处理"""
    print("\n=== 演示不可哈希参数处理 ===")
    
    @cache_wrapper(maxsize=128)
    def process_data(data_id: int, config: dict[str, Any]) -> dict[str, Any]:
        """处理数据，其中 config 是一个字典（不可哈希）"""
        print(f"处理数据: {data_id} 配置: {config}")
        time.sleep(0.3)  # 模拟耗时操作
        return {"result": data_id * 10, "processed_at": time.time()}
    
    # 第一次调用，即使有不可哈希参数，也会执行函数
    print("\n第一次调用:")
    start_time = time.time()
    result1 = process_data(1, {"mode": "fast", "precision": "low"})
    elapsed_time1 = time.time() - start_time
    print(f"结果: {result1}, 耗时: {elapsed_time1:.4f}秒")
    
    # 第二次调用相同参数，由于有不可哈希参数，应该再次执行函数
    print("\n第二次调用相同参数（含不可哈希参数）:")
    start_time = time.time()
    result2 = process_data(1, {"mode": "fast", "precision": "low"})
    elapsed_time2 = time.time() - start_time
    print(f"结果: {result2}, 耗时: {elapsed_time2:.4f}秒")
    
    # 验证两次结果虽然值相同，但返回的是不同对象
    print(f"\n两次结果对象是否相同: {result1 is result2}")
    print(f"两次结果内容是否相同: {result1 == result2}")
    
    # 演示部分参数可哈希的情况
    @cache_wrapper(maxsize=128)
    def mixed_params(a: int, b: list[int]) -> int:
        """混合可哈希和不可哈希参数"""
        print(f"处理混合参数: a={a}, b={b}")
        time.sleep(0.2)  # 模拟耗时操作
        return a + sum(b)
    
    # 即使第一个参数相同，由于第二个参数不可哈希，每次都会执行函数
    print("\n混合参数测试 - 第一次:")
    mixed_params(5, [1, 2, 3])
    
    print("\n混合参数测试 - 第二次（相同参数）:")
    mixed_params(5, [1, 2, 3])


def demo_real_world_application() -> None:
    """演示 cache_wrapper 在实际应用中的使用场景"""
    print("\n=== 演示实际应用场景 ===")
    
    # 场景1: 数据库查询缓存
    class Database:
        def __init__(self):
            # 模拟数据库
            self.users = {
                1: {"id": 1, "name": "张三", "age": 30, "department": "开发部"},
                2: {"id": 2, "name": "李四", "age": 28, "department": "市场部"},
                3: {"id": 3, "name": "王五", "age": 35, "department": "管理层"}
            }
            self.products = {
                101: {"id": 101, "name": "产品A", "price": 199.99},
                102: {"id": 102, "name": "产品B", "price": 299.99},
                103: {"id": 103, "name": "产品C", "price": 399.99}
            }
        
        @cache_wrapper(maxsize=50)
        def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
            """根据ID查询用户信息（模拟数据库查询）"""
            print(f"执行数据库查询: SELECT * FROM users WHERE id = {user_id}")
            time.sleep(0.4)  # 模拟数据库查询延迟
            return self.users.get(user_id)
        
        @cache_wrapper(maxsize=100)
        def search_products(self, min_price: float = 0, max_price: float = float('inf')) -> list[dict[str, Any]]:
            """根据价格范围搜索产品（模拟数据库查询）"""
            print(f"执行数据库查询: SELECT * FROM products WHERE price BETWEEN {min_price} AND {max_price}")
            time.sleep(0.6)  # 模拟数据库查询延迟
            return [
                product for product in self.products.values()
                if min_price <= product["price"] <= max_price
            ]
    
    # 场景2: API调用缓存
    @cache_wrapper(maxsize=30)
    def fetch_weather(city: str, date: str) -> dict[str, Any]:
        """模拟获取天气信息的API调用"""
        print(f"调用天气API: city={city}, date={date}")
        time.sleep(0.7)  # 模拟网络延迟
        # 模拟返回的数据
        weather_data = {
            "北京": {"2023-10-01": {"temperature": 22, "condition": "晴朗"},
                    "2023-10-02": {"temperature": 20, "condition": "多云"}},
            "上海": {"2023-10-01": {"temperature": 25, "condition": "小雨"},
                    "2023-10-02": {"temperature": 23, "condition": "阴"}},
            "广州": {"2023-10-01": {"temperature": 28, "condition": "雷阵雨"},
                    "2023-10-02": {"temperature": 27, "condition": "多云"}}
        }
        return weather_data.get(city, {}).get(date, {"error": "未找到天气数据"})
    
    # 测试数据库查询缓存
    print("\n测试数据库查询缓存:")
    db = Database()
    
    # 第一次查询用户
    print("\n第一次查询用户ID=1:")
    start_time = time.time()
    user1 = db.get_user_by_id(1)
    elapsed_time1 = time.time() - start_time
    print(f"结果: {user1}, 耗时: {elapsed_time1:.4f}秒")
    
    # 第二次查询同一个用户，应该使用缓存
    print("\n第二次查询用户ID=1:")
    start_time = time.time()
    user1_cache = db.get_user_by_id(1)
    elapsed_time2 = time.time() - start_time
    print(f"结果: {user1_cache}, 耗时: {elapsed_time2:.4f}秒")
    
    # 查询产品
    print("\n第一次查询价格在200-400之间的产品:")
    start_time = time.time()
    products = db.search_products(200, 400)
    elapsed_time3 = time.time() - start_time
    print(f"结果: {products}, 耗时: {elapsed_time3:.4f}秒")
    
    # 再次查询相同价格范围的产品，应该使用缓存
    print("\n第二次查询相同价格范围的产品:")
    start_time = time.time()
    products_cache = db.search_products(200, 400)
    elapsed_time4 = time.time() - start_time
    print(f"结果: {products_cache}, 耗时: {elapsed_time4:.4f}秒")
    
    # 测试API调用缓存
    print("\n测试API调用缓存:")
    
    # 第一次调用天气API
    print("\n第一次调用天气API获取北京10月1日天气:")
    start_time = time.time()
    weather1 = fetch_weather("北京", "2023-10-01")
    elapsed_time5 = time.time() - start_time
    print(f"结果: {weather1}, 耗时: {elapsed_time5:.4f}秒")
    
    # 第二次调用相同参数的天气API，应该使用缓存
    print("\n第二次调用相同参数的天气API:")
    start_time = time.time()
    weather1_cache = fetch_weather("北京", "2023-10-01")
    elapsed_time6 = time.time() - start_time
    print(f"结果: {weather1_cache}, 耗时: {elapsed_time6:.4f}秒")
    
    # 调用不同城市的天气API
    print("\n调用上海的天气API:")
    start_time = time.time()
    weather2 = fetch_weather("上海", "2023-10-01")
    elapsed_time7 = time.time() - start_time
    print(f"结果: {weather2}, 耗时: {elapsed_time7:.4f}秒")


def demo_comparison_with_standard_lru_cache() -> None:
    """比较 cache_wrapper 与标准 lru_cache 的区别"""
    print("\n=== 比较 cache_wrapper 与标准 lru_cache ===")
    
    # 使用标准 lru_cache
    @lru_cache(maxsize=128)
    def standard_cached_function(a: int, b: dict[str, Any]) -> int:
        """使用标准 lru_cache 的函数"""
        print(f"执行标准缓存函数: {a}, {b}")
        time.sleep(0.2)
        return a + sum(b.values())
    
    # 使用 cache_wrapper
    @cache_wrapper(maxsize=128)
    def our_cached_function(a: int, b: dict[str, Any]) -> int:
        """使用 cache_wrapper 的函数"""
        print(f"执行自定义缓存函数: {a}, {b}")
        time.sleep(0.2)
        return a + sum(b.values())
    
    # 测试标准 lru_cache 处理不可哈希参数
    print("\n测试标准 lru_cache 处理不可哈希参数:")
    try:
        # 这会引发 TypeError，因为字典是不可哈希的
        standard_cached_function(5, {"x": 10, "y": 20})
    except TypeError as e:
        print(f"标准 lru_cache 错误: {e}")
    
    # 测试 cache_wrapper 处理不可哈希参数
    print("\n测试 cache_wrapper 处理不可哈希参数:")
    # 这应该能正常执行，即使有不可哈希参数
    result = our_cached_function(5, {"x": 10, "y": 20})
    print(f"自定义缓存函数结果: {result}")
    
    # 再次调用我们的缓存函数，验证不可哈希参数的处理
    print("\n再次调用自定义缓存函数（相同参数）:")
    result2 = our_cached_function(5, {"x": 10, "y": 20})
    print(f"结果: {result2}")
    print("两次调用都执行了函数体，因为有不可哈希参数")


def main() -> None:
    """主函数，运行所有示例"""
    print("=== xt_wraps/cache.py 模块示例程序 ===")
    
    # 运行各个示例
    demo_basic_cache()
    demo_cache_size_control()
    demo_unhashable_params()
    demo_real_world_application()
    demo_comparison_with_standard_lru_cache()
    
    print("\n=== 所有示例运行完毕 ===")


if __name__ == "__main__":
    main()