# !/usr/bin/env python3
"""
NSWrapsLite 单例模式模块示例程序

本示例展示了 NSWrapsLite 库中所有单例模式实现方式的用法，包括:
1. SingletonMeta 元类实现
2. SingletonMixin 混入类实现
3. SingletonWraps 装饰器类实现
4. singleton 装饰器函数实现

每个示例都包含实例创建、实例管理和线程安全测试等场景。
"""

import os
import sys
import threading
import time
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nswrapslite.singleton import (
    SingletonMeta,
    SingletonMixin,
    SingletonWraps,
    singleton,
)


# ======================================================
# 示例 1: 使用 SingletonMeta 元类实现单例模式
# ======================================================
class DatabaseConnection(metaclass=SingletonMeta):
    """使用 SingletonMeta 元类实现的数据库连接类示例"""

    def __init__(self, connection_string: str = 'default'):
        """初始化数据库连接

        Args:
            connection_string: 数据库连接字符串
        """
        self.connection_string = connection_string
        print(f'初始化数据库连接: {connection_string}')
        # 模拟连接建立的耗时操作
        time.sleep(0.1)

    def execute_query(self, query: str) -> str:
        """执行数据库查询

        Args:
            query: 查询语句

        Returns:
            查询结果
        """
        return f'[{self.connection_string}] 执行查询: {query}'


# ======================================================
# 示例 2: 使用 SingletonMixin 混入类实现单例模式
# ======================================================
class ConfigManager(SingletonMixin):
    """使用 SingletonMixin 混入类实现的配置管理类示例"""

    def __init__(self, config_file: str = 'default.ini'):
        """初始化配置管理器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.settings: dict[str, str] = {}
        print(f'加载配置文件: {config_file}')
        # 模拟配置加载的耗时操作
        time.sleep(0.1)
        self.settings['initialized'] = 'True'
        self.settings['config_file'] = config_file

    def get_setting(self, key: str) -> str | None:
        """获取配置项

        Args:
            key: 配置项键名

        Returns:
            配置项值，如果不存在则返回 None
        """
        return self.settings.get(key)

    def set_setting(self, key: str, value: str) -> None:
        """设置配置项

        Args:
            key: 配置项键名
            value: 配置项值
        """
        self.settings[key] = value


# ======================================================
# 示例 3: 使用 SingletonWraps 装饰器类实现单例模式
# ======================================================
@SingletonWraps
class LoggerService:
    """使用 SingletonWraps 装饰器类实现的日志服务类示例"""

    def __init__(self, log_level: str = 'INFO'):
        """初始化日志服务

        Args:
            log_level: 日志级别
        """
        self.log_level = log_level
        self.logs: list[str] = []
        print(f'初始化日志服务，级别: {log_level}')
        # 模拟日志服务初始化的耗时操作
        time.sleep(0.1)

    def log(self, message: str, level: str = 'INFO') -> None:
        """记录日志

        Args:
            message: 日志消息
            level: 日志级别
        """
        if self._should_log(level):
            log_entry = f'[{time.strftime("%H:%M:%S")}] [{level}] {message}'
            self.logs.append(log_entry)
            print(log_entry)

    def _should_log(self, level: str) -> bool:
        """判断日志级别是否应该被记录

        Args:
            level: 日志级别

        Returns:
            是否应该记录该级别的日志
        """
        levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3}
        current_level = levels.get(self.log_level, 1)
        message_level = levels.get(level, 1)
        return message_level >= current_level


# ======================================================
# 示例 4: 使用 singleton 装饰器函数实现单例模式
# ======================================================
@singleton
class CacheManager:
    """使用 singleton 装饰器函数实现的缓存管理类示例"""

    def __init__(self, max_size: int = 100):
        """初始化缓存管理器

        Args:
            max_size: 缓存最大容量
        """
        self.max_size = max_size
        self.cache: dict[Any, Any] = {}
        print(f'初始化缓存管理器，最大容量: {max_size}')
        # 模拟缓存初始化的耗时操作
        time.sleep(0.1)

    def set(self, key: Any, value: Any) -> None:
        """设置缓存项

        Args:
            key: 缓存键
            value: 缓存值
        """
        if len(self.cache) >= self.max_size:
            # 简单的缓存淘汰策略：移除第一个项
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value

    def get(self, key: Any) -> Any | None:
        """获取缓存项

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在则返回 None
        """
        return self.cache.get(key)


# ======================================================
# 线程安全测试函数
# ======================================================
def test_thread_safety(singleton_class: type, *args: Any, **kwargs: Any) -> None:
    """测试单例类的线程安全性

    Args:
        singleton_class: 要测试的单例类
        *args: 创建实例时的位置参数
        **kwargs: 创建实例时的关键字参数
    """
    instances: list[Any] = []

    def create_instance():
        """创建单例实例并添加到列表中"""
        instance = singleton_class(*args, **kwargs)
        instances.append(instance)

    # 创建多个线程同时实例化单例类
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=create_instance)
        threads.append(thread)

    # 启动所有线程
    for thread in threads:
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 验证所有线程获取的是同一个实例
    first_instance = instances[0]
    all_same = all(instance is first_instance for instance in instances)

    # 获取类名，处理 SingletonWraps 装饰器的情况
    class_name = getattr(singleton_class, '__name__', str(singleton_class))
    # SingletonWraps 装饰器将原始类存储在 _cls 属性中
    if hasattr(singleton_class, '_cls') and hasattr(singleton_class._cls, '__name__'):
        class_name = singleton_class._cls.__name__

    print(f'线程安全测试 [{class_name}] - 所有线程获取同一实例: {all_same}')


# ======================================================
# 主函数 - 演示所有单例实现的用法
# ======================================================
def main() -> None:
    """主函数，演示所有单例实现的用法"""
    print('=' * 80)
    print('NSWrapsLite 单例模式模块示例程序')
    print('=' * 80)

    # 重置所有可能存在的单例实例
    print('\n[初始化] 重置可能存在的单例实例...')
    if hasattr(DatabaseConnection, 'reset_instance'):
        DatabaseConnection.reset_instance()
    if hasattr(ConfigManager, 'reset_instance'):
        ConfigManager.reset_instance()
    if hasattr(LoggerService, 'reset_instance'):
        LoggerService.reset_instance()
    if hasattr(CacheManager, 'reset_instance'):
        CacheManager.reset_instance()

    # 1. 演示 SingletonMeta 元类的用法
    print('\n' + '-' * 80)
    print('1. SingletonMeta 元类示例')
    print('-' * 80)

    # 创建实例
    db1 = DatabaseConnection('mysql://localhost:3306/db1')
    db2 = DatabaseConnection('mysql://localhost:3306/db2')  # 这个参数会被忽略

    # 验证是否为同一实例
    print(f'db1 和 db2 是同一实例: {db1 is db2}')
    print(f'db1 连接字符串: {db1.connection_string}')
    print(f'db2 连接字符串: {db2.connection_string}')  # 应该与 db1 相同

    # 使用实例方法
    print(db1.execute_query('SELECT * FROM users'))

    # 实例管理功能
    print(f'是否存在实例: {DatabaseConnection.has_instance()}')
    print(f'获取实例: {DatabaseConnection.get_instance()}')

    # 重置实例
    DatabaseConnection.reset_instance()
    print(f'重置后是否存在实例: {DatabaseConnection.has_instance()}')

    # 重置后创建新实例
    db3 = DatabaseConnection('mysql://localhost:3306/db3')
    print(f'新实例连接字符串: {db3.connection_string}')

    # 线程安全测试
    test_thread_safety(DatabaseConnection, 'mysql://localhost:3306/test')

    # 2. 演示 SingletonMixin 混入类的用法
    print('\n' + '-' * 80)
    print('2. SingletonMixin 混入类示例')
    print('-' * 80)

    # 创建实例
    config1 = ConfigManager('app.config')
    config2 = ConfigManager('user.config')  # 这个参数会被忽略

    # 验证是否为同一实例
    print(f'config1 和 config2 是同一实例: {config1 is config2}')
    print(f'config1 配置文件: {config1.config_file}')
    print(f'config2 配置文件: {config2.config_file}')  # 应该与 config1 相同

    # 使用实例方法
    config1.set_setting('app_name', 'MyApplication')
    print(f'应用名称: {config2.get_setting("app_name")}')  # 通过 config2 访问 config1 设置的值

    # 实例管理功能
    print(f'是否存在实例: {ConfigManager.has_instance()}')
    print(f'获取实例: {ConfigManager.get_instance()}')

    # 重置实例
    ConfigManager.reset_instance()
    print(f'重置后是否存在实例: {ConfigManager.has_instance()}')

    # 线程安全测试
    test_thread_safety(ConfigManager, 'test.config')

    # 3. 演示 SingletonWraps 装饰器类的用法
    print('\n' + '-' * 80)
    print('3. SingletonWraps 装饰器类示例')
    print('-' * 80)

    # 创建实例
    logger1 = LoggerService('DEBUG')
    logger2 = LoggerService('ERROR')  # 这个参数会被忽略

    # 验证是否为同一实例
    print(f'logger1 和 logger2 是同一实例: {logger1 is logger2}')
    print(f'logger1 日志级别: {logger1.log_level}')

    # 使用实例方法
    logger1.log('这是一条信息日志')
    logger2.log('这是一条调试日志', 'DEBUG')  # 通过 logger2 调用

    # 实例管理功能
    print(f'是否存在实例: {LoggerService.has_instance()}')
    print(f'获取实例: {LoggerService.get_instance()}')

    # 重新初始化实例
    print('\n重新初始化实例...')
    logger3 = LoggerService('WARNING', reinit=True)
    print(f'重新初始化后日志级别: {logger3.log_level}')

    # 重置实例
    LoggerService.reset_instance()
    print(f'重置后是否存在实例: {LoggerService.has_instance()}')

    # 线程安全测试
    test_thread_safety(LoggerService, 'INFO')

    # 4. 演示 singleton 装饰器函数的用法
    print('\n' + '-' * 80)
    print('4. singleton 装饰器函数示例')
    print('-' * 80)

    # 创建实例
    cache1 = CacheManager(200)
    cache2 = CacheManager(500)  # 这个参数会被忽略

    # 验证是否为同一实例
    print(f'cache1 和 cache2 是同一实例: {cache1 is cache2}')
    print(f'cache1 最大容量: {cache1.max_size}')

    # 使用实例方法
    cache1.set('key1', 'value1')
    print(f'从 cache2 获取 key1: {cache2.get("key1")}')  # 通过 cache2 访问 cache1 设置的值

    # 实例管理功能
    print(f'是否存在实例: {CacheManager.has_instance()}')
    print(f'获取实例: {CacheManager.get_instance()}')

    # 重新初始化实例
    print('\n重新初始化实例...')
    cache3 = CacheManager(1000, reinit=True)
    print(f'重新初始化后最大容量: {cache3.max_size}')

    # 重置实例
    CacheManager.reset_instance()
    print(f'重置后是否存在实例: {CacheManager.has_instance()}')

    # 线程安全测试
    test_thread_safety(CacheManager, 500)

    print('\n' + '=' * 80)
    print('NSWrapsLite 单例模式模块示例程序 演示完毕')
    print('=' * 80)


if __name__ == '__main__':
    main()
