# !/usr/bin/env python3
"""
单例模式工具模块测试
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nswrapslite.singleton import (
    SingletonMeta,
    SingletonMixin,
    SingletonWraps,
    singleton,
)


def test_singleton_meta():
    """测试SingletonMeta元类"""

    class TestClass(metaclass=SingletonMeta):
        def __init__(self, value=None):
            self.value = value

    # 创建两个实例，应该是同一个对象
    instance1 = TestClass(42)
    instance2 = TestClass(100)  # 这个值不会生效，因为实例已经存在

    assert instance1 is instance2
    assert instance1.value == 42  # 值保持第一个实例的值

    # 重置实例
    TestClass.reset_instance()

    # 重新创建实例，应该是新的对象
    instance3 = TestClass(200)
    assert instance1 is not instance3
    assert instance3.value == 200


def test_singleton_mixin():
    """测试SingletonMixin混入类"""

    class TestClass(SingletonMixin):
        def __init__(self, value=None):
            self.value = value

    # 创建两个实例，应该是同一个对象
    instance1 = TestClass(42)
    instance2 = TestClass(100)  # 这个值不会生效，因为实例已经存在

    assert instance1 is instance2
    assert instance1.value == 42  # 值保持第一个实例的值

    # 重置实例
    TestClass.reset_instance()

    # 重新创建实例，应该是新的对象
    instance3 = TestClass(200)
    assert instance1 is not instance3
    assert instance3.value == 200


def test_singleton_wraps():
    """测试SingletonWraps装饰器"""

    @SingletonWraps
    class TestClass:
        def __init__(self, value=None):
            self.value = value

    # 创建两个实例，应该是同一个对象
    instance1 = TestClass(42)
    instance2 = TestClass(100)  # 这个值不会生效，因为实例已经存在

    assert instance1 is instance2
    assert instance1.value == 42  # 值保持第一个实例的值

    # 重置实例
    TestClass.reset_instance()

    # 重新创建实例，应该是新的对象
    instance3 = TestClass(200)
    assert instance1 is not instance3
    assert instance3.value == 200


def test_singleton_decorator():
    """测试singleton装饰器"""

    @singleton
    class TestClass:
        def __init__(self, value=None):
            self.value = value

    # 创建两个实例，应该是同一个对象
    instance1 = TestClass(42)
    instance2 = TestClass(100)  # 这个值不会生效，因为实例已经存在

    assert instance1 is instance2
    assert instance1.value == 42  # 值保持第一个实例的值


def test_singleton_different_classes():
    """测试不同类的单例独立性"""

    @singleton
    class ClassA:
        pass

    @singleton
    class ClassB:
        pass

    # 不同类的实例应该是不同的对象
    instance_a = ClassA()
    instance_b = ClassB()

    assert instance_a is not instance_b


def test_singleton_thread_safety():
    """简单测试单例的线程安全性"""
    import threading
    import time

    @singleton
    class ThreadSafeClass:
        def __init__(self):
            # 模拟耗时初始化
            time.sleep(0.01)

    instances = []

    def create_instance():
        instances.append(ThreadSafeClass())

    # 创建多个线程同时实例化类
    threads = [threading.Thread(target=create_instance) for _ in range(10)]

    # 启动所有线程
    for thread in threads:
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 验证所有线程获取的是同一个实例
    first_instance = instances[0]
    for instance in instances[1:]:
        assert instance is first_instance
