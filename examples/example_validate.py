# !/usr/bin/env python3
"""
NSWrapsLite 验证工具模块示例程序

本示例展示了 NSWrapsLite 库中验证工具模块的所有功能用法，包括:
1. ensure_initialized - 确保变量已初始化装饰器
2. TypedProperty - 属性类型检查描述符
3. typeassert - 类属性类型检查装饰器
4. typed_property - 类型检查的property创建函数
5. readonly - 只读属性创建函数
6. type_check_wrapper - 简单参数类型检查装饰器

每个示例都包含基本用法、高级用法和实际应用场景。
"""
from __future__ import annotations

from typing import Any

from nswrapslite.validate import (
    TypedProperty,
    ensure_initialized,
    readonly,
    type_check_wrapper,
    typeassert,
    typed_property,
)


# ======================================================
# 示例 1: ensure_initialized 装饰器用法
# ======================================================
class DatabaseClient:
    """数据库客户端类（演示ensure_initialized装饰器）"""

    def __init__(self):
        """初始化数据库客户端（但不立即连接）"""
        self._connection = None  # 未初始化的连接

    def connect(self, connection_string: str) -> None:
        """建立数据库连接

        Args:
            connection_string: 数据库连接字符串
        """
        print(f'连接到数据库: {connection_string}')
        self._connection = f'Connected to {connection_string}'  # 初始化连接

    @ensure_initialized('_connection')
    def execute_query(self, query: str) -> str:
        """执行数据库查询（要求连接已初始化）

        Args:
            query: 查询语句

        Returns:
            查询结果

        Raises:
            RuntimeError: 当连接未初始化时
        """
        print(f'执行查询: {query}')
        return f'[{self._connection}] 查询结果: {query} 的数据'

    @ensure_initialized('_connection')
    def close(self) -> None:
        """关闭数据库连接（要求连接已初始化）"""
        print(f'关闭连接: {self._connection}')
        self._connection = None  # 重置连接


# ======================================================
# 示例 2: TypedProperty 描述符用法
# ======================================================
class Person:
    """人员类（演示TypedProperty描述符）"""

    # 使用TypedProperty定义属性
    name = TypedProperty('name', str)  # 字符串类型
    age = TypedProperty('age', int)  # 整数类型
    height = TypedProperty('height', (int, float), allow_none=True)  # 联合类型，允许None

    def __init__(self, name: str, age: int, height: int | float | None = None):
        """初始化人员对象

        Args:
            name: 姓名
            age: 年龄
            height: 身高（可选）
        """
        self.name = name
        self.age = age
        self.height = height

    def __str__(self) -> str:
        """字符串表示"""
        height_str = f'{self.height}cm' if self.height is not None else '未知'
        return f'Person(name={self.name}, age={self.age}, height={height_str})'


# ======================================================
# 示例 3: typeassert 装饰器用法
# ======================================================


# 基本用法
@typeassert(name=str, age=int)
class Employee:
    """员工类（演示typeassert基本用法）"""

    def __init__(self, name: str, age: int):
        """初始化员工对象

        Args:
            name: 姓名
            age: 年龄
        """
        self.name = name
        self.age = age

    def __str__(self) -> str:
        """字符串表示"""
        return f'Employee(name={self.name}, age={self.age})'


# 联合类型用法
@typeassert(name=str, salary=(int, float), department=str)
class Manager:
    """经理类（演示typeassert联合类型用法）"""

    def __init__(self, name: str, salary: int | float, department: str):
        """初始化经理对象

        Args:
            name: 姓名
            salary: 薪水（整数或浮点数）
            department: 部门
        """
        self.name = name
        self.salary = salary
        self.department = department

    def __str__(self) -> str:
        """字符串表示"""
        return f'Manager(name={self.name}, salary={self.salary}, department={self.department})'


# 高级用法（允许None值）
@typeassert(
    title=str,
    content={'type': str, 'allow_none': True},
    tags={'type': list, 'allow_none': True},
)
class Document:
    """文档类（演示typeassert高级用法）"""

    def __init__(self, title: str, content: str | None = None, tags: list[str] | None = None):
        """初始化文档对象

        Args:
            title: 标题
            content: 内容（可选）
            tags: 标签列表（可选）
        """
        self.title = title
        self.content = content
        self.tags = tags or []

    def __str__(self) -> str:
        """字符串表示"""
        content_preview = self.content[:20] + '...' if self.content else '无'
        return f'Document(title={self.title}, content={content_preview}, tags={self.tags})'


# ======================================================
# 示例 4: typed_property 函数用法
# ======================================================
class Product:
    """产品类（演示typed_property函数）"""

    # 使用typed_property定义属性
    product_id = typed_property('product_id', int)
    name = typed_property('name', str)
    price = typed_property('price', (int, float))
    description = typed_property('description', str, allow_none=True)

    def __init__(
        self,
        product_id: int,
        name: str,
        price: int | float,
        description: str | None = None,
    ):
        """初始化产品对象

        Args:
            product_id: 产品ID
            name: 产品名称
            price: 产品价格
            description: 产品描述（可选）
        """
        self.product_id = product_id
        self.name = name
        self.price = price
        self.description = description

    def __str__(self) -> str:
        """字符串表示"""
        desc_preview = self.description[:20] + '...' if self.description else '无'
        return f'Product(id={self.product_id}, name={self.name}, price=${self.price:.2f}, desc={desc_preview})'


# ======================================================
# 示例 5: readonly 函数用法
# ======================================================
class Circle:
    """圆形类（演示readonly函数）"""

    def __init__(self, radius: float):
        """初始化圆形对象

        Args:
            radius: 半径
        """
        self._radius = radius  # 私有存储属性
        self._area = 3.14159 * radius * radius  # 计算并存储面积

    # 定义只读属性
    radius = readonly('_radius')  # 半径作为只读属性
    area = readonly('_area')  # 面积作为只读属性

    def __str__(self) -> str:
        """字符串表示"""
        return f'Circle(radius={self.radius}, area={self.area:.2f})'


# ======================================================
# 示例 6: type_check_wrapper 装饰器用法
# ======================================================


# 基本类型检查
@type_check_wrapper(str, int)
def greet(name: str, age: int) -> str:
    """问候函数（演示基本参数类型检查）

    Args:
        name: 姓名
        age: 年龄

    Returns:
        问候消息

    Raises:
        TypeError: 当参数类型不正确时
    """
    return f'Hello, {name}! You are {age} years old.'


# 联合类型检查
@type_check_wrapper((int, float), (int, float))
def calculate_area(length: int | float, width: int | float) -> float:
    """计算矩形面积（演示联合类型参数检查）

    Args:
        length: 长度
        width: 宽度

    Returns:
        矩形面积

    Raises:
        TypeError: 当参数类型不正确时
    """
    return length * width


# 复杂类型检查
@type_check_wrapper(str, list)
def process_data(filename: str, data: list[dict[str, Any]]) -> dict[str, Any]:
    """处理数据（演示复杂类型参数检查）

    Args:
        filename: 文件名
        data: 数据列表

    Returns:
        处理结果统计

    Raises:
        TypeError: 当参数类型不正确时
    """
    print(f'处理文件: {filename}')
    print(f'数据条目数: {len(data)}')

    # 简单的处理统计
    return {'filename': filename, 'count': len(data), 'processed_at': '2023-10-01'}


# ======================================================
# 综合示例: 组合多个验证功能
# ======================================================
class APIResponse:
    """API响应类（综合示例，组合多个验证功能）"""

    # 使用typed_property定义类型检查属性
    status_code = typed_property('status_code', int)
    data = typed_property('data', (dict, list), allow_none=True)
    error = typed_property('error', str, allow_none=True)

    def __init__(
        self,
        status_code: int,
        data: dict[str, Any] | list[Any] | None = None,
        error: str | None = None,
    ):
        """初始化API响应对象

        Args:
            status_code: HTTP状态码
            data: 响应数据（可选）
            error: 错误信息（可选）
        """
        self.status_code = status_code
        self.data = data
        self.error = error
        self._parsed = False  # 未初始化的解析状态

    @ensure_initialized('_parsed')
    def get_parsed_data(self) -> dict[str, Any] | list[Any] | None:
        """获取解析后的数据（要求已解析）

        Returns:
            解析后的数据

        Raises:
            RuntimeError: 当数据未解析时
        """
        return self.data

    def parse(self) -> None:
        """解析响应数据"""
        print(f'解析响应数据，状态码: {self.status_code}')
        self._parsed = True  # 标记为已解析

    def __str__(self) -> str:
        """字符串表示"""
        if self.error:
            return f'APIResponse(status={self.status_code}, error={self.error})'
        return f'APIResponse(status={self.status_code}, data_available={self.data is not None})'


# ======================================================
# 主函数 - 演示所有验证功能
# ======================================================
def main() -> None:
    """主函数，演示所有验证工具的用法"""
    print('=' * 80)
    print('NSWrapsLite 验证工具模块示例程序')
    print('=' * 80)

    # 1. 演示 ensure_initialized 装饰器
    print('\n' + '-' * 80)
    print('1. ensure_initialized 装饰器示例')
    print('-' * 80)

    db = DatabaseClient()
    print('尝试在未连接时执行查询...')
    try:
        db.execute_query('SELECT * FROM users')
    except RuntimeError as e:
        print(f'预期的错误: {e}')

    # 正确使用方式
    db.connect('mysql://localhost:3306/mydb')
    result = db.execute_query('SELECT * FROM users')
    print(f'查询结果: {result}')
    db.close()

    # 2. 演示 TypedProperty 描述符
    print('\n' + '-' * 80)
    print('2. TypedProperty 描述符示例')
    print('-' * 80)

    person = Person('Alice', 30, 165.5)
    print(f'创建的Person对象: {person}')

    # 修改属性
    person.name = 'Bob'
    person.age = 31
    print(f'修改后的Person对象: {person}')

    # 尝试设置错误类型
    print('尝试设置错误类型的age属性...')
    try:
        person.age = 'thirty-one'  # 应该抛出TypeError
    except TypeError as e:
        print(f'预期的错误: {e}')

    # 允许None值的属性
    person.height = None
    print(f'设置height为None后的Person对象: {person}')

    # 3. 演示 typeassert 装饰器
    print('\n' + '-' * 80)
    print('3. typeassert 装饰器示例')
    print('-' * 80)

    # 基本用法
    emp = Employee('Charlie', 28)
    print(f'创建的Employee对象: {emp}')

    # 尝试设置错误类型
    print('尝试设置错误类型的age属性...')
    try:
        emp.age = 'twenty-eight'  # 应该抛出TypeError
    except TypeError as e:
        print(f'预期的错误: {e}')

    # 联合类型用法
    mgr = Manager('David', 85000.50, 'Engineering')
    print(f'创建的Manager对象: {mgr}')

    # 高级用法（允许None值）
    doc = Document('Project Plan', 'This is a detailed project plan...', ['project', 'plan'])
    print(f'创建的Document对象: {doc}')

    # 设置None值
    doc.content = None
    print(f'设置content为None后的Document对象: {doc}')

    # 4. 演示 typed_property 函数
    print('\n' + '-' * 80)
    print('4. typed_property 函数示例')
    print('-' * 80)

    product = Product(101, 'Smartphone', 699.99, 'Latest model with great features')
    print(f'创建的Product对象: {product}')

    # 修改属性
    product.price = 649.99
    print(f'修改价格后的Product对象: {product}')

    # 尝试设置错误类型
    print('尝试设置错误类型的price属性...')
    try:
        product.price = 'six hundred forty-nine'  # 应该抛出TypeError
    except TypeError as e:
        print(f'预期的错误: {e}')

    # 5. 演示 readonly 函数
    print('\n' + '-' * 80)
    print('5. readonly 函数示例')
    print('-' * 80)

    circle = Circle(5.0)
    print(f'创建的Circle对象: {circle}')
    print(f'半径: {circle.radius}')
    print(f'面积: {circle.area}')

    # 尝试修改只读属性
    print('尝试修改只读属性radius...')
    try:
        circle.radius = 10.0  # 应该抛出AttributeError
    except AttributeError as e:
        print(f'预期的错误: {e}')

    # 6. 演示 type_check_wrapper 装饰器
    print('\n' + '-' * 80)
    print('6. type_check_wrapper 装饰器示例')
    print('-' * 80)

    # 基本类型检查
    greeting = greet('Eve', 25)
    print(f'greet函数结果: {greeting}')

    # 尝试传入错误类型
    print('尝试传入错误类型的参数...')
    try:
        greet('Frank', 'twenty-five')  # 应该抛出TypeError
    except TypeError as e:
        print(f'预期的错误: {e}')

    # 联合类型检查
    area1 = calculate_area(5, 3)
    area2 = calculate_area(4.5, 2.5)
    print(f'calculate_area函数结果 (整数参数): {area1}')
    print(f'calculate_area函数结果 (浮点数参数): {area2}')

    # 复杂类型检查
    data = [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}]
    stats = process_data('items.json', data)
    print(f'process_data函数结果: {stats}')

    # 7. 演示综合示例
    print('\n' + '-' * 80)
    print('7. 综合示例: 组合多个验证功能')
    print('-' * 80)

    response = APIResponse(200, {'users': [{'id': 1, 'name': 'Alice'}]})
    print(f'创建的APIResponse对象: {response}')

    # 尝试在未解析时获取数据
    print('尝试在未解析时获取数据...')
    try:
        response.get_parsed_data()
    except RuntimeError as e:
        print(f'预期的错误: {e}')

    # 正确使用方式
    response.parse()
    parsed_data = response.get_parsed_data()
    print(f'解析后的数据: {parsed_data}')

    print('\n' + '=' * 80)
    print('NSWrapsLite 验证工具模块示例程序 演示完毕')
    print('=' * 80)


if __name__ == '__main__':
    main()
