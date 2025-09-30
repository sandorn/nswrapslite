# !/usr/bin/env python3
"""
验证工具模块测试
"""

import os
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nswrapslite.validate import (
    TypedProperty,
    ensure_initialized,
    readonly,
    type_check_wrapper,
    typeassert,
    typed_property,
)


def test_typeassert_decorator():
    """测试typeassert装饰器"""

    @typeassert(x=int, y=str)
    def sample_function(x, y):
        return f'{x}: {y}'

    # 测试正确的参数类型
    result = sample_function(42, 'test')
    assert result == '42: test'

    # 测试错误的参数类型
    with pytest.raises(TypeError):
        sample_function('42', 'test')  # x应该是int类型

    with pytest.raises(TypeError):
        sample_function(42, 100)  # y应该是str类型


def test_type_check_wrapper():
    """测试type_check_wrapper装饰器"""

    # 定义一个带有类型注解的函数
    def sample_function(x: int, y: str) -> str:
        return f'{x}: {y}'

    # 应用类型检查装饰器
    checked_function = type_check_wrapper(sample_function)

    # 测试正确的参数类型
    result = checked_function(42, 'test')
    assert result == '42: test'

    # 测试错误的参数类型
    with pytest.raises(TypeError):
        checked_function('42', 'test')  # x应该是int类型

    with pytest.raises(TypeError):
        checked_function(42, 100)  # y应该是str类型


def test_typed_property():
    """测试TypedProperty类"""

    class TestClass:
        # 定义类型化属性
        integer_value = TypedProperty(int)
        string_value = TypedProperty(str)
        optional_value = TypedProperty((int, None))

    # 创建实例并测试类型检查
    instance = TestClass()

    # 测试正确的类型赋值
    instance.integer_value = 42
    assert instance.integer_value == 42

    instance.string_value = 'test'
    assert instance.string_value == 'test'

    instance.optional_value = 100
    assert instance.optional_value == 100

    instance.optional_value = None
    assert instance.optional_value is None

    # 测试错误的类型赋值
    with pytest.raises(TypeError):
        instance.integer_value = 'not an integer'  # 应该是int类型

    with pytest.raises(TypeError):
        instance.string_value = 123  # 应该是str类型


def test_typed_property_function():
    """测试typed_property函数"""

    class TestClass:
        # 使用函数定义类型化属性
        integer_value = typed_property(int)
        string_value = typed_property(str)

    # 创建实例并测试类型检查
    instance = TestClass()

    # 测试正确的类型赋值
    instance.integer_value = 42
    assert instance.integer_value == 42

    instance.string_value = 'test'
    assert instance.string_value == 'test'

    # 测试错误的类型赋值
    with pytest.raises(TypeError):
        instance.integer_value = 'not an integer'  # 应该是int类型


def test_ensure_initialized():
    """测试ensure_initialized装饰器"""

    class TestClass:
        def __init__(self):
            self.initialized = False

        @ensure_initialized
        def method1(self):
            return 'method1 called'

        def initialize(self):
            self.initialized = True

    # 创建实例但不初始化
    instance = TestClass()

    # 调用被装饰的方法应该抛出异常
    with pytest.raises(RuntimeError):
        instance.method1()

    # 初始化后再调用方法
    instance.initialize()
    result = instance.method1()
    assert result == 'method1 called'


def test_readonly():
    """测试readonly装饰器"""

    class TestClass:
        def __init__(self):
            self._value = 42

        @readonly
        def value(self):
            return self._value

    # 创建实例并测试只读属性
    instance = TestClass()
    assert instance.value == 42

    # 尝试修改只读属性应该抛出异常
    with pytest.raises(AttributeError):
        instance.value = 100


def test_combination_of_decorators():
    """测试多个装饰器的组合使用"""

    class TestClass:
        @readonly
        @typeassert(x=int)
        def calculate(self, x):
            return x * 2

    # 创建实例并测试
    instance = TestClass()

    # 测试正确的参数类型
    assert instance.calculate(5) == 10

    # 测试错误的参数类型
    with pytest.raises(TypeError):
        instance.calculate('5')

    # 测试只读属性
    with pytest.raises(AttributeError):
        instance.calculate = lambda x: x * 3
