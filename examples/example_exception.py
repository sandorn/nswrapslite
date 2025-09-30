# !/usr/bin/env python3
"""
NSWrapsLite 异常处理模块示例程序

本示例展示了 NSWrapsLite 库中异常处理模块的所有功能用法，包括:
1. handle_exception - 统一的异常处理函数
2. exc_wraps - 通用异常处理装饰器（支持同步和异步函数）

每个示例都包含基本用法和高级配置选项，展示如何捕获、记录和处理异常。
"""

import asyncio
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nswrapslite.exception import exc_wraps, handle_exception

# 配置日志，以便更好地查看异常处理的输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ======================================================
# 示例 1: handle_exception 统一异常处理函数
# ======================================================
print('\n=== 示例1: handle_exception 统一异常处理函数 ===')


# 方式1: 基本用法，捕获异常但不重新抛出
def basic_exception_handling():
    """基本异常处理示例"""
    try:
        result = 10 / 0
    except Exception as e:
        # 记录异常但不中断程序，返回默认值
        result = handle_exception(
            e,
            re_raise=False,
            default_return=0,
            log_traceback=True,  # 记录完整堆栈信息
        )
    print(f'basic_exception_handling 结果: {result}')


# 方式2: 带自定义消息的异常处理
def custom_message_handling():
    """带自定义消息的异常处理示例"""
    try:
        data = [1, 2, 3]
        data[5]  # 索引越界
    except Exception as e:
        result = handle_exception(
            e,
            re_raise=False,
            default_return='错误发生',
            custom_message='数据访问错误: 索引超出范围',
        )
    print(f'custom_message_handling 结果: {result}')


# 方式3: 重新抛出异常
def re_raise_exception():
    """重新抛出异常示例"""
    try:
        # 尝试执行可能失败的操作
        time.sleep(0.1)
        raise ValueError('测试重新抛出异常')
    except Exception as e:
        try:
            # 记录异常并重新抛出
            handle_exception(
                e,
                re_raise=True,  # 重新抛出异常
                log_traceback=True,
            )
        except Exception as re_raised_e:
            print(f're_raise_exception 捕获到重新抛出的异常: {type(re_raised_e).__name__}')


# ======================================================
# 示例 2: exc_wraps 通用异常处理装饰器
# ======================================================
print('\n=== 示例2: exc_wraps 通用异常处理装饰器 ===')


# 方式1: 基本用法，直接装饰同步函数（捕获所有异常并重新抛出）
@exc_wraps
def divide_numbers(a: int, b: int) -> float:
    """除法函数（演示基本异常处理装饰器）"""
    return a / b


# 方式2: 带参数装饰同步函数（不重新抛出，设置默认返回值）
@exc_wraps(re_raise=False, default_return=0)
def safe_divide(a: int, b: int) -> float:
    """安全除法函数（演示自定义异常处理行为）"""
    return a / b


# 方式3: 只捕获特定类型的异常
@exc_wraps(
    allowed_exceptions=(ValueError, TypeError),  # 只捕获这两种异常
    re_raise=False,
    default_return='输入无效',
    custom_message='数据验证失败',
)
def validate_input(value: Any) -> str:
    """输入验证函数（演示特定异常捕获）"""
    if not isinstance(value, int):
        raise TypeError('必须是整数')
    if value < 0:
        raise ValueError('必须是非负数')
    return f'验证通过: {value}'


# 方式4: 异步函数异常处理
@exc_wraps(
    re_raise=False,
    default_return=None,
    log_traceback=False,  # 不记录完整堆栈
)
async def async_process_data(data: list[int]) -> dict[str, Any] | None:
    """异步处理数据（演示异步函数异常处理）"""
    if not data:
        raise ValueError('数据不能为空')
    await asyncio.sleep(0.2)  # 模拟异步操作
    return {'sum': sum(data), 'count': len(data), 'average': sum(data) / len(data)}


# 方式5: 不记录堆栈信息
@exc_wraps(
    re_raise=False,
    default_return='操作失败',
    log_traceback=False,  # 不记录堆栈信息
)
def fast_operation(value: int) -> str:
    """快速操作（演示不记录堆栈信息）"""
    if value % 2 != 0:
        raise ValueError('值必须是偶数')
    return f'操作成功: {value}'


# ======================================================
# 示例 3: 高级用法和实际应用场景
# ======================================================
print('\n=== 示例3: 高级用法和实际应用场景 ===')


# 方式1: 在数据库操作中的应用
def mock_database_operation(operation: str) -> bool:
    """模拟数据库操作（演示在数据库操作中的异常处理）"""
    try:
        # 模拟数据库连接和操作
        print(f'执行数据库操作: {operation}')
        if operation.lower() == 'delete':
            raise RuntimeError('删除操作被拒绝')
        time.sleep(0.1)  # 模拟操作延迟
        return True
    except Exception as e:
        # 数据库操作失败时的处理
        result = handle_exception(
            e,
            re_raise=False,
            default_return=False,
            custom_message=f"数据库操作'{operation}'执行失败",
            log_traceback=True,
        )
        # 这里可以添加事务回滚等逻辑
        print(f'数据库操作回滚: {operation}')
        return result


# 方式2: 在API调用中的应用
@exc_wraps(
    re_raise=False,
    default_return={'status': 'error', 'message': '请求失败'},
    custom_message='API调用异常',
)
def call_external_api(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """调用外部API（演示在API调用中的异常处理）"""
    # 模拟API调用
    print(f'调用外部API: {endpoint} 带参数: {params}')
    if endpoint == '/error':
        raise ConnectionError('API连接超时')
    if 'invalid' in params:
        raise ValueError('参数无效')
    time.sleep(0.2)  # 模拟网络延迟
    return {'status': 'success', 'data': f'来自{endpoint}的数据'}


# 方式3: 结合日志级别动态调整异常处理
@exc_wraps(re_raise=True)
def process_sensitive_data(data: dict[str, Any]) -> dict[str, Any]:
    """处理敏感数据（演示结合日志级别的异常处理）"""
    try:
        # 实际应用中可能需要检查数据完整性和安全性
        if 'secret' not in data:
            raise KeyError('缺少必要的敏感信息')
        # 处理数据
        return {'processed': True, 'result': '数据已处理'}
    except Exception as e:
        # 动态决定是否记录详细堆栈，根据不同环境调整
        is_debug_mode = True  # 实际应用中可以从配置中读取
        return handle_exception(
            e,
            re_raise=True,  # 在生产环境可能设置为False
            log_traceback=is_debug_mode,
        )


# 方式4: 异步函数的高级异常处理
@exc_wraps(
    allowed_exceptions=(TimeoutError, ConnectionError),
    re_raise=False,
    default_return='请求失败，已重试',
    custom_message='网络请求异常',
)
async def async_api_request(url: str, retries: int = 3) -> str:
    """异步API请求（演示带重试机制的异常处理）"""
    for attempt in range(retries):
        try:
            print(f'尝试请求 {url} (第{attempt + 1}/{retries}次)')
            await asyncio.sleep(0.1)  # 模拟网络延迟
            if 'fail' in url:
                raise ConnectionError('连接失败')
            return f'成功获取 {url} 的数据'
        except allowed_exceptions:
            if attempt == retries - 1:
                raise  # 最后一次重试失败时，让exc_wraps处理
            print(f'请求失败，{retries - attempt - 1}次重试剩余')
            await asyncio.sleep(0.2)  # 重试间隔
    return '请求失败'  # 这一行通常不会执行


# ======================================================
# 示例 4: 异常处理的最佳实践组合
# ======================================================
print('\n=== 示例4: 异常处理的最佳实践组合 ===')


# 实践1: 异常链保留
@exc_wraps(re_raise=True)
def chained_exception():
    """异常链保留示例"""
    try:
        # 内层异常
        try:
            10 / 0
        except ZeroDivisionError as e:
            # 包装并重新抛出，保留原始异常链
            raise RuntimeError('计算过程出错') from e
    except Exception as e:
        # 使用handle_exception记录并重新抛出，保留完整的异常链
        handle_exception(e, re_raise=True)


# 实践2: 分层异常处理
class DatabaseError(Exception):
    """数据库错误基类"""

    pass


class ConnectionDatabaseError(DatabaseError):
    """数据库连接错误"""

    pass


class QueryDatabaseError(DatabaseError):
    """数据库查询错误"""

    pass


@exc_wraps(re_raise=True)
def complex_database_operation():
    """复杂数据库操作（演示分层异常处理）"""
    try:
        # 模拟连接数据库
        if True:  # 模拟连接失败条件
            raise ConnectionDatabaseError('无法连接到数据库')
        # 模拟查询操作
        time.sleep(0.1)
        # 模拟查询错误
        # raise QueryDatabaseError("查询执行失败")
    except DatabaseError as e:
        # 根据不同类型的数据库错误进行不同处理
        if isinstance(e, ConnectionDatabaseError):
            print('正在尝试重新连接...')
            # 这里可以添加重连逻辑
        elif isinstance(e, QueryDatabaseError):
            print('查询错误，检查SQL语句...')
            # 这里可以添加查询重试或修复逻辑
        # 记录并重新抛出
        handle_exception(e, re_raise=True)


# ======================================================
# 主函数 - 演示所有异常处理功能
# ======================================================
async def main() -> None:
    """主函数，演示所有异常处理工具的用法"""
    print('=' * 80)
    print('NSWrapsLite 异常处理模块示例程序')
    print('=' * 80)

    # 1. 演示 handle_exception 统一异常处理函数
    print('\n' + '-' * 80)
    print('1. handle_exception 统一异常处理函数示例')
    print('-' * 80)

    # 测试基本用法
    basic_exception_handling()

    # 测试自定义消息
    custom_message_handling()

    # 测试重新抛出异常
    re_raise_exception()

    # 2. 演示 exc_wraps 通用异常处理装饰器
    print('\n' + '-' * 80)
    print('2. exc_wraps 通用异常处理装饰器示例')
    print('-' * 80)

    # 测试基本装饰器（会抛出异常）
    try:
        result1 = divide_numbers(10, 0)
        print(f'divide_numbers 结果: {result1}')
    except Exception as e:
        print(f'divide_numbers 捕获到预期异常: {type(e).__name__}')

    # 测试安全除法（不会抛出异常）
    result2 = safe_divide(10, 0)
    print(f'safe_divide(10, 0) 结果: {result2} (预期的默认返回值)')

    # 测试输入验证
    result3 = validate_input(42)
    print(f'validate_input(42) 结果: {result3}')

    result4 = validate_input('not a number')
    print(f"validate_input('not a number') 结果: {result4} (预期的默认返回值)")

    # 测试异步函数异常处理
    async_result1 = await async_process_data([1, 2, 3, 4, 5])
    print(f'async_process_data(valid) 结果: {async_result1}')

    async_result2 = await async_process_data([])
    print(f'async_process_data(empty) 结果: {async_result2} (预期的默认返回值)')

    # 测试不记录堆栈信息
    fast_result1 = fast_operation(4)
    print(f'fast_operation(4) 结果: {fast_result1}')

    fast_result2 = fast_operation(5)
    print(f'fast_operation(5) 结果: {fast_result2} (预期的默认返回值)')

    # 3. 演示高级用法和实际应用场景
    print('\n' + '-' * 80)
    print('3. 高级用法和实际应用场景示例')
    print('-' * 80)

    # 测试数据库操作异常处理
    db_result1 = mock_database_operation('SELECT')
    print(f'mock_database_operation(SELECT) 结果: {db_result1}')

    db_result2 = mock_database_operation('DELETE')
    print(f'mock_database_operation(DELETE) 结果: {db_result2}')

    # 测试API调用异常处理
    api_result1 = call_external_api('/users', {'id': 1})
    print(f'call_external_api(/users) 结果: {api_result1}')

    api_result2 = call_external_api('/error', {'id': 1})
    print(f'call_external_api(/error) 结果: {api_result2}')

    # 测试带重试的异步API请求
    try:
        retry_result1 = await async_api_request('https://api.example.com/success')
        print(f'async_api_request(success) 结果: {retry_result1}')

        retry_result2 = await async_api_request('https://api.example.com/fail')
        print(f'async_api_request(fail) 结果: {retry_result2}')
    except Exception as e:
        print(f'async_api_request 捕获到预期异常: {type(e).__name__}')

    # 4. 演示异常处理的最佳实践组合
    print('\n' + '-' * 80)
    print('4. 异常处理的最佳实践组合示例')
    print('-' * 80)

    # 测试异常链保留
    try:
        chained_exception()
    except Exception as e:
        print(f'chained_exception 捕获到预期异常: {type(e).__name__}')
        # 打印完整的异常链
        print(f'异常链: {e.__cause__}')

    # 测试分层异常处理
    try:
        complex_database_operation()
    except Exception as e:
        print(f'complex_database_operation 捕获到预期异常: {type(e).__name__}')

    print('\n' + '=' * 80)
    print('NSWrapsLite 异常处理模块示例程序 演示完毕')
    print('=' * 80)


if __name__ == '__main__':
    asyncio.run(main())
