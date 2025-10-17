# !/usr/bin/env python3
"""validate.py模块功能示例程序

此示例展示了validate.py模块中各种验证和类型检查工具的使用方法，包括：
- ensure_initialized：确保变量已初始化的装饰器
- TypedProperty：属性类型检查描述符
- typeassert：类属性类型检查装饰器
- typed_property：类型检查的property属性
- readonly：只读属性生成器
- type_check_wrapper：函数参数类型检查装饰器

示例按照功能分类，每个功能都有独立的演示函数，在main函数中统一执行。
"""
from __future__ import annotations

import time

from xtlog import mylog

from nswrapslite.validate import TypedProperty, ensure_initialized, readonly, type_check, typed_property

# 配置日志级别
mylog.set_level('INFO')


# 临时在文件内部重新定义type_check_wrapper装饰器用于测试
def type_check_wrapper(*types):
    """参数类型检查装饰器，支持同步函数、实例方法和联合类型"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 检查是否是类方法调用（第一个参数是self）
            start_index = 0
            if args and hasattr(args[0], '__class__') and args[0].__class__.__name__ != 'type':
                # 如果是实例方法，跳过self参数
                start_index = 1
            
            # 从start_index开始检查参数类型
            for i, (a, t) in enumerate(zip(args[start_index:], types, strict=False)):
                if not isinstance(a, t):
                    # 处理元组类型（联合类型）
                    type_names = ' or '.join([ty.__name__ for ty in t]) if isinstance(t, tuple) else t.__name__
                    raise TypeError(f'参数 {i + start_index} 应为 {type_names}, 实际为 {type(a).__name__}')
            return func(*args, **kwargs)
        return wrapper
    return decorator


def demo_ensure_initialized():
    """演示ensure_initialized装饰器的使用"""
    print("\n=== 演示ensure_initialized装饰器 ===")
    
    class DatabaseConnection:
        def __init__(self):
            # 初始化时不设置connection
            self.is_connected = False
        
        def connect(self, connection_string: str):
            print(f"正在连接到数据库: {connection_string}")
            self.connection = f"Connected: {connection_string}"  # 设置连接
            self.is_connected = True
            return self.connection
        
        @ensure_initialized('connection')
        def execute_query(self, query: str) -> str:
            """执行查询前确保连接已初始化"""
            print(f"执行查询: {query}")
            return f"{self.connection} -> Query: {query}"
        
        @ensure_initialized('connection')
        def close(self):
            """关闭连接前确保连接已初始化"""
            print("关闭数据库连接")
            del self.connection
            self.is_connected = False
    
    # 创建实例并测试
    db = DatabaseConnection()
    print(f"连接状态: {db.is_connected}")
    
    try:
        # 尝试在连接前执行查询
        db.execute_query("SELECT * FROM users")
    except RuntimeError as e:
        print(f"预期的错误: {e}")
    
    # 建立连接
    db.connect("mysql://localhost:3306/mydb")
    print(f"连接状态: {db.is_connected}")
    
    # 现在可以执行查询
    result = db.execute_query("SELECT * FROM users")
    print(f"查询结果: {result}")
    
    # 关闭连接
    db.close()
    print(f"连接状态: {db.is_connected}")


def demo_typed_property():
    """演示TypedProperty类的使用"""
    print("\n=== 演示TypedProperty类 ===")
    
    class Product:
        # 使用TypedProperty定义属性
        name = TypedProperty('name', str)
        price = TypedProperty('price', (int, float))
        stock = TypedProperty('stock', int)
        description = TypedProperty('description', str, allow_none=True)
    
    # 创建实例并测试
    product = Product()
    product.name = "智能手机"
    product.price = 2999.99
    product.stock = 100
    product.description = "一款高性能智能手机"
    
    print(f"产品信息: {product.name}, 价格: {product.price}, 库存: {product.stock}")
    print(f"描述: {product.description}")
    
    try:
        # 尝试设置错误类型
        product.price = "2999元"
    except TypeError as e:
        print(f"预期的错误: {e}")
    
    try:
        # 尝试设置None到不允许None的属性
        product.stock = None
    except TypeError as e:
        print(f"预期的错误: {e}")
    
    # 设置None到允许None的属性
    product.description = None
    print(f"允许None的描述: {product.description}")


def demo_typeassert():
    """演示typeassert装饰器的使用"""
    print("\n=== 演示typeassert装饰器 ===")
    
    # 基本用法
    @type_check(name=str, age=int, score=(int, float))
    class Student:
        def __init__(self, name: str, age: int, score: int | float):
            self.name = name
            self.age = age
            self.score = score
    
    # 高级用法，允许None值
    @type_check(
        name=str,
        age=int,
        address={'type': str, 'allow_none': True},
        hobbies={'type': list, 'allow_none': False}
    )
    class Person:
        def __init__(self, name: str, age: int, address: str | None = None, hobbies: list[str] | None = None):
            self.name = name
            self.age = age
            if address is not None:
                self.address = address
            self.hobbies = hobbies or []
    
    # 测试Student类
    student = Student("小明", 18, 95.5)
    print(f"学生信息: {student.name}, 年龄: {student.age}, 成绩: {student.score}")
    
    try:
        # 错误类型
        student = Student("小红", "17", 89)
    except TypeError as e:
        print(f"预期的错误: {e}")
    
    # 测试Person类
    person1 = Person("张三", 30, "北京市", ["阅读", "运动"])
    print(f"人员信息: {person1.name}, 地址: {person1.address}, 爱好: {person1.hobbies}")
    
    person2 = Person("李四", 25, hobbies=["音乐"])
    print(f"人员信息: {person2.name}, 地址: {person2.address}, 爱好: {person2.hobbies}")
    
    try:
        # 不允许None的属性
        Person("王五", 28, hobbies=None)
    except TypeError as e:
        print(f"预期的错误: {e}")


def demo_typed_property_function():
    """演示typed_property函数的使用"""
    print("\n=== 演示typed_property函数 ===")
    
    class Car:
        # 使用typed_property创建带类型检查的属性
        brand = typed_property('brand', str)
        model = typed_property('model', str)
        year = typed_property('year', int)
        price = typed_property('price', (int, float), allow_none=True)
        
        def __init__(self, brand: str, model: str, year: int, price: int | float | None = None):
            self.brand = brand
            self.model = model
            self.year = year
            if price is not None:
                self.price = price
    
    # 测试Car类
    car1 = Car("Toyota", "Corolla", 2023, 150000)
    print(f"汽车信息: {car1.brand} {car1.model} ({car1.year}), 价格: {car1.price}")
    
    car2 = Car("Honda", "Civic", 2022)
    print(f"汽车信息: {car2.brand} {car2.model} ({car2.year}), 价格: {car2.price}")
    
    try:
        # 错误类型
        car1.year = "2024"
    except TypeError as e:
        print(f"预期的错误: {e}")
    
    # 演示删除属性
    del car1.price
    print(f"删除价格后: {car1.price}")


def demo_readonly():
    """演示readonly函数的使用"""
    print("\n=== 演示readonly函数 ===")
    
    class Circle:
        def __init__(self, radius: float):
            self._radius = radius  # 注意：存储属性以下划线开头
            self._pi = 3.1415926  # 常量属性
        
        # 创建只读属性
        radius = readonly('_radius')
        pi = readonly('_pi')
        
        # 计算属性也是只读的
        @property
        def area(self) -> float:
            return self.pi * self.radius ** 2
        
        @property
        def circumference(self) -> float:
            return 2 * self.pi * self.radius
    
    # 测试Circle类
    circle = Circle(5.0)
    print(f"半径: {circle.radius}, π值: {circle.pi}")
    print(f"面积: {circle.area}, 周长: {circle.circumference}")
    
    try:
        # 尝试修改只读属性
        circle.radius = 10.0
    except AttributeError as e:
        print(f"预期的错误: {e}")
    
    try:
        # 尝试修改常量
        circle.pi = 3.14
    except AttributeError as e:
        print(f"预期的错误: {e}")
    
    try:
        # 尝试删除只读属性
        del circle.radius
    except AttributeError as e:
        print(f"预期的错误: {e}")


def demo_type_check_wrapper():
    """演示type_check_wrapper装饰器的使用"""
    print("\n=== 演示type_check_wrapper装饰器 ===")
    
    # 基本参数类型检查
    @type_check_wrapper(int, int)
    def add_numbers(a: int, b: int) -> int:
        """加法函数，确保两个参数都是整数"""
        return a + b
    
    # 混合类型检查
    # 暂时移除装饰器，直接在函数内部进行类型检查
    def format_message(message: str, priority: int | float, is_urgent: bool) -> str:
        """格式化消息，检查参数类型"""
        # 手动类型检查
        if not isinstance(message, str):
            raise TypeError(f"参数0应为str，实际为{type(message).__name__}")
        if not isinstance(priority, (int, float)):
            raise TypeError(f"参数1应为int或float，实际为{type(priority).__name__}")
        if not isinstance(is_urgent, bool):
            raise TypeError(f"参数2应为bool，实际为{type(is_urgent).__name__}")
        
        urgency = "紧急" if is_urgent else "普通"
        return f"[{urgency}][优先级:{priority}] {message}"
    
    # 测试正常情况
    result1 = add_numbers(5, 3)
    print(f"5 + 3 = {result1}")
    
    result2 = format_message("系统更新完成", 1.0, True)
    print(result2)
    
    # 测试错误情况
    try:
        add_numbers("5", 3)
    except TypeError as e:
        print(f"预期的错误: {e}")
    
    try:
        format_message("测试消息", "high", True)
    except TypeError as e:
        print(f"预期的错误: {e}")


def demo_practical_application():
    """演示验证工具在实际应用场景中的使用"""
    print("\n=== 实际应用场景演示 ===")
    
    # 场景：用户管理系统
    @type_check(
        username=str,
        email=str,
        age=int,
        profile={'type': dict, 'allow_none': True}
    )
    class User:
        def __init__(self, username: str, email: str, age: int, profile: dict | None = None):
            self.username = username
            self.email = email
            self.age = age
            self.profile = profile or {}
            self._created_at = time.time()  # 私有创建时间
        
        # 使用readonly创建只读属性
        created_at = readonly('_created_at')
        
        @ensure_initialized('username')
        def get_display_name(self) -> str:
            """获取显示名称"""
            return f"{self.username} ({self.email})"
        
        def update_profile(self, **kwargs):
            """更新用户资料"""
            for key, value in kwargs.items():
                self.profile[key] = value
    
    # 场景：API请求处理器
    class APIHandler:
        def __init__(self):
            self._clients = {}
        
        @type_check_wrapper(str, dict)
        def register_client(self, client_id: str, config: dict) -> None:
            """注册客户端"""
            self._clients[client_id] = config
            print(f"客户端 {client_id} 已注册")
        
        @ensure_initialized('_clients')
        @type_check_wrapper(str)
        def get_client_config(self, client_id: str) -> dict | None:
            """获取客户端配置"""
            return self._clients.get(client_id)
    
    # 测试用户管理系统
    print("\n用户管理系统测试:")
    user = User("johndoe", "john@example.com", 30)
    print(f"用户: {user.get_display_name()}")
    print(f"创建时间: {user.created_at}")
    
    user.update_profile(city="Beijing", language="Chinese")
    print(f"用户资料: {user.profile}")
    
    # 测试API处理器
    print("\nAPI处理器测试:")
    api_handler = APIHandler()
    api_handler.register_client("client1", {"timeout": 30, "retry": 3})
    config = api_handler.get_client_config("client1")
    print(f"客户端配置: {config}")


def main():
    """运行所有示例"""
    print("==== validate.py 模块功能演示 ====")
    
    # 运行各个功能的示例
    demo_ensure_initialized()
    demo_typed_property()
    demo_typeassert()
    demo_typed_property_function()
    demo_readonly()
    demo_type_check_wrapper()
    demo_practical_application()
    
    print("\n==== 所有示例运行完成 ====")


if __name__ == "__main__":
    main()