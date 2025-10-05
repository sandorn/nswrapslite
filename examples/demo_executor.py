# !/usr/bin/env python3

"""
xt_wraps/executor.py 模块示例程序

本示例展示了 executor.py 模块中异步执行器功能的使用方法，包括：
- executor_wraps：异步执行同步函数，支持后台执行模式
- run_executor_wraps：同步运行异步函数，无需await
- future_wraps：将同步函数包装为返回Future对象的函数
- future_wraps_result：等待Future完成并返回结果，含超时处理
- 实际应用场景：IO操作加速、多任务并行处理、耗时操作优化等
"""
from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from xtlog import mylog

# 导入 executor 模块中的函数
from nswrapslite.executor import async_executor, await_future_with_timeout, syncify, to_future

# 配置日志级别
mylog.set_level('INFO')


def demo_basic_executor_wraps() -> None:
    """演示 executor_wraps 装饰器的基本使用"""
    print("\n=== 演示 executor_wraps 装饰器的基本使用 ===")
    
    # 示例1: 基本用法 - 将同步函数转换为异步函数
    print("\n示例1: 基本用法 - 将同步函数转换为异步函数")

    @async_executor
    def sync_sleep(seconds: float) -> str:
        """模拟耗时的同步操作"""
        time.sleep(seconds)
        return f"睡眠了 {seconds} 秒"
    
    async def test_basic_executor():
        # 现在可以使用 await 调用同步函数
        start_time = time.time()
        result = await sync_sleep(0.5)
        elapsed = time.time() - start_time
        print(f"同步函数转换为异步函数结果: {result}, 耗时: {elapsed:.2f}秒")
    
    asyncio.run(test_basic_executor())
    
    # 示例2: 后台执行模式
    print("\n示例2: 后台执行模式")

    @async_executor(background=True)
    def background_task(seconds: float) -> str:
        """在后台执行的任务"""
        time.sleep(seconds)
        return f"后台任务完成，耗时 {seconds} 秒"
    
    async def test_background_executor():
        # 立即返回 Future 对象，不阻塞主线程
        start_time = time.time()
        future = background_task(1.0)
        print("后台任务已启动，无需等待即可继续执行其他操作")
        
        # 可以在稍后获取结果
        await asyncio.sleep(0.1)  # 执行其他操作
        print("执行其他操作...")
        
        # 等待并获取结果
        result = await future
        elapsed = time.time() - start_time
        print(f"后台任务结果: {result}, 总耗时: {elapsed:.2f}秒")
    
    asyncio.run(test_background_executor())
    
    # 示例3: 自定义执行器
    print("\n示例3: 自定义执行器")
    # 创建自定义线程池执行器
    custom_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="CustomExecutor")
    
    @async_executor(executor=custom_executor)
    def task_with_custom_executor(seconds: float) -> str:
        """使用自定义执行器的任务"""
        time.sleep(seconds)
        return f"使用自定义执行器完成任务，耗时 {seconds} 秒"
    
    async def test_custom_executor():
        result = await task_with_custom_executor(0.5)
        print(f"自定义执行器结果: {result}")
        # 记得关闭自定义执行器
        custom_executor.shutdown()
    
    asyncio.run(test_custom_executor())


def demo_run_executor_wraps() -> None:
    """演示 run_executor_wraps 装饰器的使用"""
    print("\n=== 演示 run_executor_wraps 装饰器的使用 ===")
    
    # 示例1: 将异步函数转换为同步函数调用
    print("\n示例1: 将异步函数转换为同步函数调用")

    async def async_sleep(seconds: float) -> str:
        """模拟异步操作"""
        await asyncio.sleep(seconds)
        return f"异步睡眠了 {seconds} 秒"
    
    # 使用装饰器转换为同步函数
    sync_version = syncify(async_sleep)
    
    # 直接调用，无需await
    start_time = time.time()
    result = sync_version(0.5)
    elapsed = time.time() - start_time
    print(f"异步函数转换为同步函数调用结果: {result}, 耗时: {elapsed:.2f}秒")
    
    # 示例2: 直接装饰异步函数
    print("\n示例2: 直接装饰异步函数")

    @syncify
    async def decorated_async_task(seconds: float) -> str:
        """直接装饰的异步任务"""
        await asyncio.sleep(seconds)
        return f"装饰后的异步任务完成，耗时 {seconds} 秒"
    
    # 直接调用，无需await
    result = decorated_async_task(0.6)
    print(f"装饰后的异步函数调用结果: {result}")
    
    # 示例3: 在已运行的事件循环中使用
    print("\n示例3: 在已运行的事件循环中使用")

    @syncify
    async def task_in_running_loop(seconds: float) -> str:
        """在已运行的事件循环中执行的任务"""
        await asyncio.sleep(seconds)
        return f"在已运行的事件循环中完成任务，耗时 {seconds} 秒"
    
    # 模拟已运行的事件循环环境
    async def run_event_loop():
        # 在事件循环中调用同步函数版本的异步函数
        result = task_in_running_loop(0.7)
        print(f"在运行中的事件循环中调用结果: {result}")
    
    asyncio.run(run_event_loop())


def demo_future_wraps() -> None:
    """演示 future_wraps 装饰器的使用"""
    print("\n=== 演示 future_wraps 装饰器的使用 ===")
    
    # 示例1: 基本用法 - 将同步函数包装为返回Future的函数
    print("\n示例1: 基本用法 - 将同步函数包装为返回Future的函数")

    @to_future
    def create_future_task(seconds: float) -> str:
        """返回Future对象的任务"""
        time.sleep(seconds)
        return f"Future任务完成，耗时 {seconds} 秒"
    
    async def test_future_wraps():
        # 调用返回Future对象的函数
        future = create_future_task(0.5)
        # 检查返回类型
        print(f"返回类型: {type(future).__name__}")
        # 等待Future完成并获取结果
        result = await future
        print(f"Future结果: {result}")
    
    asyncio.run(test_future_wraps())
    
    # 示例2: 使用自定义执行器
    print("\n示例2: 使用自定义执行器")
    custom_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="FutureExecutor")
    
    @to_future(executor=custom_executor)
    def future_with_custom_executor(seconds: float) -> str:
        """使用自定义执行器的Future任务"""
        time.sleep(seconds)
        return f"使用自定义执行器的Future任务完成，耗时 {seconds} 秒"
    
    async def test_custom_executor_future():
        future = future_with_custom_executor(0.6)
        result = await future
        print(f"自定义执行器的Future结果: {result}")
        custom_executor.shutdown()
    
    asyncio.run(test_custom_executor_future())


def demo_future_wraps_result() -> None:
    """演示 future_wraps_result 函数的使用"""
    print("\n=== 演示 future_wraps_result 函数的使用 ===")
    
    # 示例1: 基本用法 - 等待Future完成并获取结果
    print("\n示例1: 基本用法 - 等待Future完成并获取结果")

    async def test_basic_future_result():
        # 创建一个简单的Future对象
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        # 创建一个任务来设置Future的结果
        async def set_future_result():
            await asyncio.sleep(0.5)
            future.set_result("Future已完成")
        
        # 启动设置结果的任务
        loop.create_task(set_future_result())
        
        # 等待Future完成并获取结果
        result = await await_future_with_timeout(future)
        print(f"Future结果: {result}")
    
    asyncio.run(test_basic_future_result())
    
    # 示例2: 超时处理
    print("\n示例2: 超时处理")

    async def test_timeout():
        # 创建一个永远不会完成的Future
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        try:
            # 设置较短的超时时间
            result = await await_future_with_timeout(future, timeout=1.0)
            print(f"Future结果: {result}")
        except TimeoutError:
            print("Future等待超时，已自动取消")
        except Exception as e:
            print(f"发生其他异常: {type(e).__name__}: {e}")
    
    asyncio.run(test_timeout())
    
    # 示例3: 处理已完成的Future
    print("\n示例3: 处理已完成的Future")

    async def test_completed_future():
        # 创建一个已完成的Future
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        future.set_result("已完成的Future结果")
        
        # 处理已完成的Future
        result = await await_future_with_timeout(future)
        print(f"已完成的Future结果: {result}")
    
    asyncio.run(test_completed_future())
    
    # 示例4: 处理失败的Future
    print("\n示例4: 处理失败的Future")

    async def test_failed_future():
        # 创建一个失败的Future
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        future.set_exception(ValueError("Future执行失败"))
        
        try:
            # 处理失败的Future
            result = await await_future_with_timeout(future)
            print(f"Future结果: {result}")
        except ValueError as e:
            print(f"捕获到Future中的异常: {e}")
    
    asyncio.run(test_failed_future())


def demo_parallel_execution() -> None:
    """演示使用executor进行并行执行"""
    print("\n=== 演示使用executor进行并行执行 ===")
    
    # 定义一个耗时的任务
    @async_executor
    def process_item(item_id: int, delay: float) -> dict[str, Any]:
        """处理单个项目的耗时任务"""
        time.sleep(delay)
        return {
            "item_id": item_id,
            "result": item_id * 2,
            "processed_at": time.time()
        }
    
    async def test_parallel_execution():
        # 准备要处理的项目
        items = [(i, 0.3) for i in range(10)]  # 10个项目，每个耗时0.3秒
        
        # 串行执行
        print("\n串行执行:")
        start_time = time.time()
        serial_results = []
        for item_id, delay in items:
            result = await process_item(item_id, delay)
            serial_results.append(result)
        serial_time = time.time() - start_time
        print(f"串行执行完成，总耗时: {serial_time:.2f}秒")
        
        # 并行执行 - 使用asyncio.gather
        print("\n并行执行:")
        start_time = time.time()
        # 创建所有任务
        tasks = [process_item(item_id, delay) for item_id, delay in items]
        # 等待所有任务完成
        parallel_results = await asyncio.gather(*tasks)
        parallel_time = time.time() - start_time
        print(f"并行执行完成，总耗时: {parallel_time:.2f}秒")
        
        # 计算性能提升
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        print(f"并行执行相比串行执行提升了 {speedup:.2f}倍速度")
        
        # 验证结果一致性
        assert len(serial_results) == len(parallel_results)
        print("结果一致性验证通过")
    
    asyncio.run(test_parallel_execution())


def demo_real_world_application() -> None:
    """演示executor在实际应用场景中的使用"""
    print("\n=== 演示executor在实际应用场景中的使用 ===")
    
    # 场景1: 数据库操作优化
    class DatabaseOperation:
        @async_executor
        def fetch_data(self, query: str, timeout: float = 5.0) -> list[dict[str, Any]]:
            """模拟数据库查询操作"""
            # 模拟数据库查询耗时
            time.sleep(0.8)
            print(f"执行数据库查询: {query}")
            # 模拟返回查询结果
            if "users" in query.lower():
                return [
                    {"id": 1, "name": "张三", "age": 30},
                    {"id": 2, "name": "李四", "age": 25},
                    {"id": 3, "name": "王五", "age": 35}
                ]
            if "products" in query.lower():
                return [
                    {"id": 101, "name": "产品A", "price": 199.99},
                    {"id": 102, "name": "产品B", "price": 299.99}
                ]
            return []
        
        @async_executor
        def save_data(self, table: str, data: dict[str, Any]) -> bool:
            """模拟数据库保存操作"""
            # 模拟数据库保存耗时
            time.sleep(0.5)
            print(f"保存数据到表 {table}: {data}")
            return True
    
    # 场景2: 网络请求处理
    class NetworkService:
        @async_executor
        def fetch_url(self, url: str, timeout: float = 10.0) -> dict[str, Any]:
            """模拟网络请求"""
            # 模拟网络延迟和请求处理
            time.sleep(1.2)
            print(f"请求URL: {url}")
            # 模拟返回结果
            return {
                "status": 200,
                "url": url,
                "content_length": len(url) * 10,
                "response_time": time.time()
            }
        
        @syncify
        async def process_batch_requests(self, urls: list[str]) -> list[dict[str, Any]]:
            """批量处理网络请求"""
            # 并行处理所有请求
            tasks = [self.fetch_url(url) for url in urls]
            return await asyncio.gather(*tasks)
    
    # 测试实际应用场景
    async def test_real_world_application():
        # 初始化服务
        db = DatabaseOperation()
        network = NetworkService()
        
        # 测试1: 并行执行数据库操作
        print("\n测试1: 并行执行数据库操作")
        start_time = time.time()
        # 并行执行两个数据库查询
        users_future = db.fetch_data("SELECT * FROM users")
        products_future = db.fetch_data("SELECT * FROM products")
        
        # 同时等待两个查询结果
        users, products = await asyncio.gather(users_future, products_future)
        
        print(f"用户数据: {users}")
        print(f"产品数据: {products}")
        print(f"数据库操作总耗时: {time.time() - start_time:.2f}秒")
        
        # 测试2: 混合操作（数据库+网络）
        print("\n测试2: 混合操作（数据库+网络）")
        start_time = time.time()
        
        # 同时执行数据库保存和网络请求
        save_task = db.save_data("logs", {"message": "系统启动", "level": "info"})
        fetch_task = network.fetch_url("https://api.example.com/data")
        
        # 等待两个操作完成
        save_result, fetch_result = await asyncio.gather(save_task, fetch_task)
        
        print(f"保存结果: {save_result}")
        print(f"网络请求结果: {fetch_result}")
        print(f"混合操作总耗时: {time.time() - start_time:.2f}秒")
        
        # 测试3: 使用run_executor_wraps处理批量网络请求
        print("\n测试3: 使用run_executor_wraps处理批量网络请求")
        # 注意：这里直接调用异步函数的同步版本，无需await
        urls = [
            "https://api.example.com/users",
            "https://api.example.com/products",
            "https://api.example.com/orders"
        ]
        
        batch_results = network.process_batch_requests(urls)
        print(f"批量请求结果数: {len(batch_results)}")
        for i, result in enumerate(batch_results):
            print(f"请求{i + 1}结果: URL={result['url']}, 状态码={result['status']}")
    
    asyncio.run(test_real_world_application())


def main() -> None:
    """主函数，运行所有示例"""
    print("=== xt_wraps/executor.py 模块示例程序 ===")
    
    # 运行各个功能的示例
    demo_basic_executor_wraps()
    demo_run_executor_wraps()
    demo_future_wraps()
    demo_future_wraps_result()
    demo_parallel_execution()
    demo_real_world_application()
    
    print("\n=== 所有示例运行完毕 ===")


if __name__ == "__main__":
    main()