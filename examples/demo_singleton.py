# !/usr/bin/env python3
"""
==============================================================
Description  : 单例模式工具模块示例程序
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-09-29 10:00:00

本示例程序演示xt_wraps.singleton模块的以下功能：
- SingletonMeta：线程安全的单例元类实现
- SingletonMixin：线程安全的单例混入类实现
- SingletonWraps：增强型单例类装饰器实现
- singleton：基于SingletonWraps的简单单例装饰器函数
- 多线程环境下的线程安全性
- 单例实例的管理功能（重置、检查、获取等）
- 实际应用场景（配置管理、数据库连接池等）
==============================================================
"""
from __future__ import annotations

import threading
import time
from typing import Any

from xtlog import mylog

# 导入单例模式工具模块和日志模块
from nswrapslite.singleton import SingletonMeta, SingletonMixin, SingletonWraps, singleton

# 配置日志级别
mylog.set_level('INFO')


# ============================ 基本用法示例 ============================

# 示例1: 使用SingletonMeta元类实现单例
class DatabaseConnection(metaclass=SingletonMeta):
    """数据库连接类 - 使用SingletonMeta实现单例"""
    def __init__(self, connection_string: str):
        print(f"初始化数据库连接: {connection_string}")
        self.connection_string = connection_string
        self.connected = False
        # 模拟连接过程
        time.sleep(0.1)
        self.connected = True
        print(f"数据库连接已建立: {connection_string}")

    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """执行数据库查询"""
        if not self.connected:
            raise RuntimeError("数据库未连接")
        print(f"在{self.connection_string}上执行查询: {query}")
        return [{"result": f"来自{self.connection_string}的结果"}]


# 示例2: 使用SingletonMixin混入类实现单例
class ConfigService(SingletonMixin):
    """配置服务类 - 使用SingletonMixin实现单例"""
    def __init__(self, config_file: str | None = None):
        print(f"加载配置文件: {config_file or '默认配置'}")
        # 模拟配置加载
        time.sleep(0.1)
        self.config = {
            "app_name": "MyApp",
            "version": "1.0",
            "debug": False
        }
        if config_file:
            self.config["config_file"] = config_file
        print("配置加载完成")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)

    def update_setting(self, key: str, value: Any) -> None:
        """更新配置项"""
        self.config[key] = value


# 示例3: 使用SingletonWraps装饰器类实现单例
@SingletonWraps
class CacheManager:
    """缓存管理器类 - 使用SingletonWraps实现单例"""
    def __init__(self, max_size: int = 100):
        print(f"初始化缓存管理器，最大大小: {max_size}")
        # 模拟初始化过程
        time.sleep(0.1)
        self.cache: dict[Any, Any] = {}
        self.max_size = max_size
        print("缓存管理器初始化完成")

    def set(self, key: Any, value: Any) -> None:
        """设置缓存项"""
        if len(self.cache) >= self.max_size:
            # 简单的LRU策略，移除第一个项
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value

    def get(self, key: Any, default: Any = None) -> Any:
        """获取缓存项"""
        return self.cache.get(key, default)


# 示例4: 使用singleton装饰器函数实现单例
@singleton
class AppLogger:
    """应用日志记录器类 - 使用singleton装饰器实现单例"""
    def __init__(self, log_level: str = "INFO"):
        print(f"初始化日志记录器，日志级别: {log_level}")
        # 模拟初始化过程
        time.sleep(0.1)
        self.log_level = log_level
        self.logs: list[str] = []
        print("日志记录器初始化完成")

    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        log_levels = {"DEBUG": 1, "INFO": 2, "WARNING": 3, "ERROR": 4}
        current_level = log_levels.get(self.log_level, 2)
        message_level = log_levels.get(level, 2)
        
        if message_level >= current_level:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}"
            self.logs.append(log_entry)
            print(log_entry)

    def get_logs(self) -> list[str]:
        """获取所有日志"""
        return self.logs


# ============================ 多线程安全性示例 ============================

def test_thread_safety():
    """测试单例在多线程环境下的线程安全性"""
    print("\n===== 测试多线程安全性 ======")
    
    # 重置所有单例实例，确保测试的纯净性
    DatabaseConnection.reset_instance()
    
    # 创建多个线程同时获取单例实例
    def thread_function(thread_id: int):
        print(f"线程 {thread_id} 尝试获取数据库连接实例")
        db = DatabaseConnection(f"mysql://localhost:3306/db_thread_{thread_id}")
        print(f"线程 {thread_id} 获取到的实例ID: {id(db)}")
        result = db.execute_query(f"SELECT * FROM table WHERE thread_id = {thread_id}")
        print(f"线程 {thread_id} 查询结果: {result}")
    
    # 创建10个线程
    threads = []
    for i in range(10):
        thread = threading.Thread(target=thread_function, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 验证所有线程获取的是同一个实例
    db_final = DatabaseConnection("mysql://localhost:3306/final")
    print(f"最终实例连接字符串: {db_final.connection_string}")
    print("多线程测试完成，所有线程获取的是同一个实例")


# ============================ 实例管理功能示例 ============================

def test_instance_management():
    """测试单例的实例管理功能"""
    print("\n===== 测试实例管理功能 ======")
    
    # 测试SingletonMeta的实例管理
    print("\n测试SingletonMeta实例管理:")
    print(f"数据库连接实例是否存在: {DatabaseConnection.has_instance()}")
    db = DatabaseConnection("mysql://localhost:3306/test")
    print(f"数据库连接实例是否存在: {DatabaseConnection.has_instance()}")
    print(f"获取数据库连接实例: {DatabaseConnection.get_instance()}")
    print(f"当前实例ID: {id(db)}")
    DatabaseConnection.reset_instance()
    print(f"重置后，数据库连接实例是否存在: {DatabaseConnection.has_instance()}")
    db_new = DatabaseConnection("mysql://localhost:3306/new")
    print(f"新实例ID: {id(db_new)}")
    print(f"两次获取的实例是否相同: {db is db_new}")
    
    # 测试SingletonWraps的实例管理和reinit功能
    print("\n测试SingletonWraps实例管理和reinit功能:")
    cache1 = CacheManager(200)
    print(f"缓存最大大小: {cache1.max_size}")
    print(f"缓存实例是否存在: {CacheManager.has_instance()}")
    
    # 测试重新初始化
    print("\n测试重新初始化功能:")
    cache2 = CacheManager(300, reinit=True)
    print(f"重新初始化后缓存最大大小: {cache2.max_size}")
    print(f"重新初始化后的实例是否与原实例相同: {cache1 is cache2}")


# ============================ 实际应用场景示例 ============================

def test_practical_scenarios():
    """测试单例在实际应用场景中的使用"""
    print("\n===== 测试实际应用场景 ======")
    
    # 场景1: 全局配置管理
    print("\n场景1: 全局配置管理")
    config = ConfigService("app_config.json")
    print(f"应用名称: {config.get_setting('app_name')}")
    print(f"配置文件: {config.get_setting('config_file')}")
    config.update_setting("debug", True)
    print(f"调试模式: {config.get_setting('debug')}")
    
    # 验证在不同模块中获取的是同一个配置实例
    another_config = ConfigService("different_config.json")
    print(f"不同引用获取的配置是否相同: {config is another_config}")
    print(f"通过不同引用访问的调试模式: {another_config.get_setting('debug')}")
    
    # 场景2: 全局日志记录器
    print("\n场景2: 全局日志记录器")
    logger = AppLogger("INFO")
    logger.log("应用启动")
    logger.log("这是一条调试信息", "DEBUG")  # 由于日志级别为INFO，这条不会显示
    logger.log("这是一条警告信息", "WARNING")
    
    # 在不同地方使用同一个日志记录器
    another_logger = AppLogger("DEBUG")  # 由于是单例，日志级别不会改变
    another_logger.log("这是通过另一个引用记录的信息")
    another_logger.log("这是另一条调试信息", "DEBUG")  # 由于原日志级别为INFO，这条不会显示
    
    print(f"\n所有记录的日志 ({len(logger.get_logs())}条):")
    for log in logger.get_logs():
        print(f"  {log}")
    
    # 场景3: 数据库连接池（简化版）
    print("\n场景3: 数据库连接池")
    # 假设有多个组件需要访问数据库

    class UserService:
        def get_user(self, user_id: int) -> dict[str, Any]:
            db = DatabaseConnection("mysql://localhost:3306/users")
            result = db.execute_query(f"SELECT * FROM users WHERE id = {user_id}")
            return result[0] if result else {}
    
    class ProductService:
        def get_product(self, product_id: int) -> dict[str, Any]:
            db = DatabaseConnection("mysql://localhost:3306/products")
            result = db.execute_query(f"SELECT * FROM products WHERE id = {product_id}")
            return result[0] if result else {}
    
    user_service = UserService()
    product_service = ProductService()
    
    # 两个服务共享同一个数据库连接实例
    user = user_service.get_user(1)
    product = product_service.get_product(100)
    
    print(f"用户数据: {user}")
    print(f"产品数据: {product}")


# ============================ 性能对比示例 ============================

def test_performance():
    """测试单例与普通类的性能对比"""
    print("\n===== 测试性能对比 ======")
    
    # 定义一个普通类作为对比
    class RegularDatabaseConnection:
        """普通的数据库连接类（非单例）"""
        def __init__(self, connection_string: str):
            self.connection_string = connection_string
            # 模拟连接开销
            time.sleep(0.01)
    
    # 测试获取单例实例的时间
    def test_singleton_performance():
        # 确保有实例存在
        DatabaseConnection("mysql://localhost:3306/test")
        
        start_time = time.time()
        for _ in range(1000):
            DatabaseConnection("mysql://localhost:3306/test")
        singleton_time = time.time() - start_time
        print(f"获取单例实例1000次耗时: {singleton_time:.6f}秒")
    
    # 测试创建普通实例的时间
    def test_regular_performance():
        start_time = time.time()
        for _ in range(1000):
            RegularDatabaseConnection("mysql://localhost:3306/test")
        regular_time = time.time() - start_time
        print(f"创建普通实例1000次耗时: {regular_time:.6f}秒")
        
    # 运行性能测试
    test_singleton_performance()
    test_regular_performance()


# ============================ 主函数 ============================

def main():
    """主函数，运行所有示例"""
    print("=====================================================")
    print("          xt_wraps.singleton 模块示例程序")
    print("=====================================================")
    
    # 运行所有测试示例
    try:
        # 1. 测试基本用法
        print("\n===== 测试基本用法 ======")
        db1 = DatabaseConnection("mysql://localhost:3306/db1")
        db2 = DatabaseConnection("mysql://localhost:3306/db2")
        print(f"数据库连接是同一个实例: {db1 is db2}")
        print(f"连接字符串: {db1.connection_string}")
        
        # 2. 测试线程安全性
        test_thread_safety()
        
        # 3. 测试实例管理功能
        test_instance_management()
        
        # 4. 测试实际应用场景
        test_practical_scenarios()
        
        # 5. 测试性能对比
        test_performance()
        
    except Exception as e:
        print(f"示例程序执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n=====================================================")
        print("             示例程序执行完毕")
        print("=====================================================")


if __name__ == "__main__":
    main()