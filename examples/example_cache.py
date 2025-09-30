# !/usr/bin/env python3
"""
NSWrapsLite 缓存装饰器模块示例程序

本示例展示了 NSWrapsLite 库中缓存装饰器模块的功能用法,包括:
1. cache_wrapper 基本用法
2. 不同 maxsize 参数的影响
3. 缓存对耗时操作的性能提升
4. 缓存参数包含可变类型的处理
5. 缓存的统计信息
6. 缓存清除操作
7. 缓存的实际应用场景

每个示例都包含详细的注释和输出,帮助您理解如何在实际项目中使用缓存装饰器优化性能。
"""

import os
import sys
import time
from typing import Any, Dict, List, Tuple

from nswrapslite.cache import cache_wrapper

# ======================================================
# 示例 1: 基本的缓存装饰器用法
# ======================================================
print('\n=== 示例1: 基本的缓存装饰器用法 ===')


# 使用默认的maxsize=128
@cache_wrapper()
def fibonacci(n: int) -> int:
    """计算斐波那契数列（使用默认缓存大小）"""
    print(f'计算 fibonacci({n})')
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# 测试基本缓存功能
def test_basic_caching():
    """测试基本的缓存功能"""
    print('首次调用 fibonacci(10):')
    start_time = time.time()
    result1 = fibonacci(10)
    first_time = time.time() - start_time
    print(f'结果: {result1}, 耗时: {first_time:.6f}秒')

    print('\n再次调用 fibonacci(10) (应该使用缓存):')
    start_time = time.time()
    result2 = fibonacci(10)
    second_time = time.time() - start_time
    print(f'结果: {result2}, 耗时: {second_time:.6f}秒')

    print(f'\n性能提升: 第二次调用比第一次快了 {first_time / second_time:.1f} 倍')


# ======================================================
# 示例 2: 不同 maxsize 参数的影响
# ======================================================
print('\n=== 示例2: 不同 maxsize 参数的影响 ===')


# 小缓存大小
@cache_wrapper(maxsize=5)
def limited_fibonacci(n: int) -> int:
    """计算斐波那契数列（限制缓存大小为5）"""
    print(f'计算limited_fibonacci({n})')
    if n <= 1:
        return n
    return limited_fibonacci(n - 1) + limited_fibonacci(n - 2)


# 无限缓存大小
@cache_wrapper(maxsize=None)
def unlimited_cache_function(n: int) -> str:
    """使用无限缓存大小的函数"""
    print(f'执行 unlimited_cache_function({n})')
    return f'结果_{n}'


def test_different_maxsize():
    """测试不同 maxsize 参数的影响"""
    print('\n测试小缓存 (maxsize=5):')
    # 调用多次,应该会看到一些缓存未命中
    print('\n第一次计算limited_fibonacci(5)（未缓存）：')
    result = limited_fibonacci(5)
    print(f'limited_fibonacci(5) = {result}')

    print('\n第二次计算limited_fibonacci(5)（使用缓存）：')
    result = limited_fibonacci(5)
    print(f'limited_fibonacci(5) = {result}')

    print('\n计算多个值以达到缓存上限：')
    for i in range(10, 15):
        result = limited_fibonacci(i)
        print(f'limited_fibonacci({i}) = {result}')

    print('\n再次计算limited_fibonacci(5)（可能超出缓存限制）：')
    result = limited_fibonacci(5)
    print(f'limited_fibonacci(5) = {result}')

    print('\n测试无限缓存 (maxsize=None):')
    # 调用5次,全部缓存
    for i in range(5):
        unlimited_cache_function(i)

    # 再次调用所有参数,应该全部命中缓存
    print('\n再次调用所有参数 (应该全部命中缓存):')
    for i in range(5):
        unlimited_cache_function(i)


# ======================================================
# 示例 3: 缓存耗时操作的性能提升
# ======================================================
print('\n=== 示例3: 缓存耗时操作的性能提升 ===')


@cache_wrapper(maxsize=None)  # 无限制缓存
def expensive_operation(a: int, b: int) -> int:
    """模拟一个耗时操作（无限制缓存）"""
    print(f'执行耗时操作: a={a}, b={b}')
    # 模拟耗时操作
    time.sleep(0.5)
    return a * b + a + b


# 未缓存的耗时函数
def non_cached_expensive_operation(x: int, y: int) -> dict[str, int]:
    """模拟耗时的操作（无缓存版本）"""
    print(f'执行未缓存的耗时操作: x={x}, y={y}')
    time.sleep(0.2)  # 模拟耗时操作
    return {'sum': x + y, 'product': x * y}


# 缓存的耗时函数
@cache_wrapper()
def cached_version_expensive_operation(x: int, y: int) -> dict[str, int]:
    """使用缓存的耗时操作"""
    print(f'执行缓存的耗时操作: x={x}, y={y}')
    time.sleep(0.2)  # 模拟耗时操作
    return {'sum': x + y, 'product': x * y}


def test_performance_improvement():
    """测试缓存对耗时操作的性能提升"""
    print('\n第一次执行耗时操作（未缓存）：')
    start_time = time.time()
    result = expensive_operation(100, 200)
    elapsed_time = time.time() - start_time
    print(f'结果: {result}')
    print(f'执行耗时: {elapsed_time:.4f} 秒')

    print('\n第二次执行耗时操作（使用缓存）：')
    start_time = time.time()
    result = expensive_operation(100, 200)
    elapsed_time = time.time() - start_time
    print(f'结果: {result}')
    print(f'执行耗时: {elapsed_time:.4f} 秒')

    print('\n执行不同参数的耗时操作：')
    start_time = time.time()
    result = expensive_operation(100, 201)
    elapsed_time = time.time() - start_time
    print(f'结果: {result}')
    print(f'执行耗时: {elapsed_time:.4f} 秒')

    # 更直观的性能对比
    print('\n缓存与非缓存版本性能对比:')
    start_time = time.time()
    for _ in range(3):
        non_cached_expensive_operation(10, 20)
    uncached_time = time.time() - start_time
    print(f'执行3次未缓存操作耗时: {uncached_time:.3f}秒')

    start_time = time.time()
    for _ in range(3):
        cached_version_expensive_operation(10, 20)
    cached_time = time.time() - start_time
    print(f'执行3次缓存操作耗时: {cached_time:.3f}秒')

    print(f'性能提升: 缓存版本比未缓存版本快了 {uncached_time / cached_time:.1f} 倍')


# ======================================================
# 示例 4: 缓存参数处理
# ======================================================
print('\n=== 示例4: 缓存参数处理 ===')


@cache_wrapper()
def with_kwargs(a: int, b: int, c: str = 'default') -> str:
    """测试带默认参数的函数缓存"""
    print(f'执行带默认参数的函数: a={a}, b={b}, c={c}')
    return f'{c}: {a + b}'


# 注意：lru_cache 不支持可变类型作为参数
# 但是我们可以通过转换可变类型为不可变类型来处理
@cache_wrapper()
def process_data(items: tuple[int, ...], options: dict[str, str]) -> int:
    """处理数据的函数（使用不可变类型作为参数）"""
    print(f'处理数据: items={items}, options={options}')
    time.sleep(0.1)  # 模拟处理时间
    return sum(items) + len(options)


def test_variable_parameters():
    """测试缓存参数处理"""
    print('\n第一次调用带默认参数的函数：')
    result = with_kwargs(1, 2)
    print(f'结果: {result}')

    print('\n第二次调用相同参数的函数（使用缓存）：')
    result = with_kwargs(1, 2)
    print(f'结果: {result}')

    print('\n使用不同的默认参数调用：')
    result = with_kwargs(1, 2, c='custom')
    print(f'结果: {result}')

    print('\n再次使用自定义参数调用（使用缓存）：')
    result = with_kwargs(1, 2, c='custom')
    print(f'结果: {result}')

    # 使用元组（不可变类型）作为参数
    print('\n使用不可变类型作为参数:')
    process_data(items=(1, 2, 3), options={'mode': 'fast'})  # 首次调用,不命中缓存
    process_data(items=(1, 2, 3), options={'mode': 'fast'})  # 应该命中缓存

    # 使用列表（可变类型）的情况
    # 我们需要先将列表转换为元组
    print('\n使用可变类型转换为不可变类型:')
    data_list = [4, 5, 6]
    options_dict = {'mode': 'detailed'}

    # 正确的做法：将可变类型转换为不可变类型
    process_data(items=tuple(data_list), options=options_dict)  # 首次调用,不命中缓存
    process_data(items=tuple(data_list), options=options_dict)  # 应该命中缓存

    # 但要注意,字典仍然是可变类型
    # 如果我们修改字典内容,缓存会认为是不同的参数
    print('\n修改字典内容后:')
    options_dict['mode'] = 'new_mode'
    process_data(items=tuple(data_list), options=options_dict)  # 新的缓存条目


# ======================================================
# 示例 5: 缓存的统计信息
# ======================================================
print('\n=== 示例5: 缓存的统计信息 ===')


@cache_wrapper(maxsize=5)
def stats_function(n: int) -> int:
    """用于统计的缓存函数"""
    print(f'计算 stats_function({n})')
    return n * n


def test_cache_statistics():
    """测试缓存的统计信息"""
    print('\n调用stats_function多次,触发缓存:')
    for i in range(3):
        stats_function(i)  # 首次调用,不命中缓存

    for i in range(3):
        stats_function(i)  # 再次调用,命中缓存

    # 触发缓存淘汰
    for i in range(3, 8):
        stats_function(i)  # 添加新的缓存条目,淘汰旧条目

    # 查看缓存统计信息
    # 注意：我们需要访问原始的lru_cache装饰的函数
    cached_func = None
    for attr in dir(stats_function):
        if attr.startswith('_wrapped'):
            cached_func = getattr(stats_function, attr)
            break

    if cached_func and hasattr(cached_func, 'cache_info'):
        print(f'\n缓存统计信息: {cached_func.cache_info()}')
        # 解释统计信息
        hits = cached_func.cache_info().hits
        misses = cached_func.cache_info().misses
        maxsize = cached_func.cache_info().maxsize
        current_size = cached_func.cache_info().currsize

        print(f'  命中次数: {hits}')
        print(f'  未命中次数: {misses}')
        print(f'  最大缓存大小: {maxsize}')
        print(f'  当前缓存大小: {current_size}')

        if hits + misses > 0:
            hit_rate = hits / (hits + misses) * 100
            print(f'  缓存命中率: {hit_rate:.1f}%')


# ======================================================
# 示例 6: 缓存清除操作
# ======================================================
print('\n=== 示例6: 缓存清除操作 ===')


@cache_wrapper()
def clearable_cache_function(n: int) -> str:
    """可清除缓存的函数"""
    print(f'执行 clearable_cache_function({n})')
    return f'结果_{n}'


def test_cache_clear():
    """测试缓存清除操作"""
    print('\n首次调用函数:')
    clearable_cache_function(1)
    clearable_cache_function(2)

    print('\n再次调用函数（应该命中缓存）:')
    clearable_cache_function(1)
    clearable_cache_function(2)

    # 清除缓存
    print('\n清除缓存后再次调用:')
    # 获取原始的缓存函数并清除缓存
    cached_func = None
    for attr in dir(clearable_cache_function):
        if attr.startswith('_wrapped'):
            cached_func = getattr(clearable_cache_function, attr)
            break

    if cached_func and hasattr(cached_func, 'cache_clear'):
        cached_func.cache_clear()
        print('缓存已清除')

        # 再次调用,应该重新执行函数体
        clearable_cache_function(1)
        clearable_cache_function(2)


# ======================================================
# 示例 7: 缓存的实际应用场景
# ======================================================
print('\n=== 示例7: 缓存的实际应用场景 ===')


# 场景1: 数据库查询缓存
@cache_wrapper(maxsize=100)
def get_user_profile(user_id: int) -> dict[str, str]:
    """模拟从数据库获取用户配置文件"""
    print(f'从数据库查询用户 {user_id} 的配置文件')
    time.sleep(0.1)  # 模拟数据库查询时间
    # 模拟返回用户数据
    return {
        'id': user_id,
        'name': f'用户{user_id}',
        'email': f'user{user_id}@example.com',
        'role': 'user' if user_id < 10 else 'admin',
    }


# 场景2: API调用缓存
@cache_wrapper(maxsize=50)
def call_external_api(endpoint: str, params: dict[str, str]) -> dict[str, Any]:
    """模拟调用外部API"""
    print(f'调用外部API: {endpoint} 带参数: {params}')
    time.sleep(0.2)  # 模拟网络延迟
    # 模拟API返回结果
    return {
        'status': 'success',
        'data': f'从{endpoint}获取的数据',
        'timestamp': time.time(),
    }


# 场景3: 计算密集型操作缓存
@cache_wrapper(maxsize=200)
def complex_calculation(x: float, y: float, precision: int = 3) -> list[float]:
    """模拟计算密集型操作"""
    print(f'执行复杂计算: {x}, {y}, 精度: {precision}')
    time.sleep(0.3)  # 模拟计算时间
    # 模拟复杂计算结果
    result = []
    for i in range(precision):
        result.append(x * y + i)
    return result


def test_practical_scenarios():
    """测试缓存的实际应用场景"""
    print('\n场景1: 数据库查询缓存:')
    start_time = time.time()
    # 第一次查询,从数据库获取
    get_user_profile(1)
    # 第二次查询,从缓存获取
    get_user_profile(1)
    db_time = time.time() - start_time
    print(f'两次查询耗时: {db_time:.3f}秒')

    print('\n场景2: API调用缓存:')
    start_time = time.time()
    # 第一次调用,实际发起请求
    call_external_api('/users', {'id': '1'})
    # 第二次调用,从缓存获取
    call_external_api('/users', {'id': '1'})
    api_time = time.time() - start_time
    print(f'两次API调用耗时: {api_time:.3f}秒')

    print('\n场景3: 计算密集型操作缓存:')
    start_time = time.time()
    # 第一次计算,实际执行计算
    complex_calculation(3.14, 2.71)
    # 第二次计算,从缓存获取
    complex_calculation(3.14, 2.71)
    calc_time = time.time() - start_time
    print(f'两次计算耗时: {calc_time:.3f}秒')


# ======================================================
# 主函数 - 演示所有缓存功能
# ======================================================
def main() -> None:
    """主函数,演示所有缓存工具的用法"""
    print('=' * 80)
    print('NSWrapsLite 缓存装饰器模块示例程序')
    print('=' * 80)

    # 1. 基本的缓存装饰器用法
    print('\n' + '-' * 80)
    print('1. 基本的缓存装饰器用法')
    print('-' * 80)
    test_basic_caching()

    # 2. 不同 maxsize 参数的影响
    print('\n' + '-' * 80)
    print('2. 不同 maxsize 参数的影响')
    print('-' * 80)
    test_different_maxsize()

    # 3. 缓存耗时操作的性能提升
    print('\n' + '-' * 80)
    print('3. 缓存耗时操作的性能提升')
    print('-' * 80)
    test_performance_improvement()

    # 4. 缓存参数处理
    print('\n' + '-' * 80)
    print('4. 缓存参数处理')
    print('-' * 80)
    test_variable_parameters()

    # 5. 缓存的统计信息
    print('\n' + '-' * 80)
    print('5. 缓存的统计信息')
    print('-' * 80)
    test_cache_statistics()

    # 6. 缓存清除操作
    print('\n' + '-' * 80)
    print('6. 缓存清除操作')
    print('-' * 80)
    test_cache_clear()

    # 7. 缓存的实际应用场景
    print('\n' + '-' * 80)
    print('7. 缓存的实际应用场景')
    print('-' * 80)
    test_practical_scenarios()

    print('\n' + '=' * 80)
    print('NSWrapsLite 缓存装饰器模块示例程序 演示完毕')
    print('=' * 80)

    # 总结使用缓存的最佳实践
    print('\n缓存装饰器使用最佳实践:')
    print('1. 对计算密集型、IO密集型或重复调用的函数使用缓存')
    print('2. 合理设置maxsize参数,避免内存占用过大')
    print('3. 注意缓存键的可哈希性,避免使用可变类型作为参数')
    print('4. 定期监控缓存统计信息,评估缓存效果')
    print('5. 在数据更新时记得清除相关缓存')
    print('6. 对于随时间变化的结果,考虑使用其他缓存策略')


if __name__ == '__main__':
    main()
