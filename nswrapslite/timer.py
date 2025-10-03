# !/usr/bin/env python3
"""
==============================================================
Description  : 计时工具模块 - 提供函数执行耗时自动记录功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-09-11 14:30:00
Github       : https://github.com/sandorn/nswrapslite

本模块提供以下核心功能：
- timer_wraps：自动记录函数执行耗时的装饰器
- timer：timer_wraps的简写别名
- timeit：支持同步和异步函数的计时装饰器

主要特性：
- 同时支持同步和异步函数，自动识别函数类型
- 毫秒级精度的执行时间记录
- 集成异常处理机制
- 详细的日志输出
- 支持无参和有参调用方式
- 保留原始函数的元数据（名称、文档等）
==============================================================
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import Any

from xtlog import mylog

from .utils import _get_function_location


def timer_wraps(fn: Callable[..., Any] | None = None) -> Callable[..., Any]:
    """自动记录函数执行耗时的装饰器

    核心功能：
    - 自动记录函数的执行时间并输出调试日志
    - 同时支持同步和异步函数，自动识别函数类型
    - 集成异常处理机制，确保计时准确性
    - 保留原始函数的元数据（名称、文档字符串、参数签名等）

    参数说明：
    - fn: 可选，要装饰的函数，用于支持无参调用方式

    返回值：
    - 装饰后的函数，执行时会自动记录耗时

    示例用法：
        >>> # 方式1: 直接装饰同步函数
        >>> @timer_wraps
        >>> def calculate_sum(a, b):
        >>> # 执行一些计算
        >>>     return a + b
        >>> # 方式2: 带括号装饰异步函数
        >>> @timer_wraps()
        >>> async def fetch_data(url):
        >>> # 模拟网络请求延迟
        >>>     await asyncio.sleep(1)
        >>>     return f"Data from {url}"
        >>> # 方式3: 与其他装饰器组合使用
        >>> @log_wraps
        >>> @timer_wraps
        >>> def complex_operation(data):
        >>> # 执行复杂操作
        >>>     return processed_data
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = perf_counter()
            try:
                result = func(*args, **kwargs)
                func_location = _get_function_location(func)
                mylog.info(f'{func_location}执行耗时: {perf_counter() - start_time:.4f}秒')
                return result
            except Exception as err:
                func_location = _get_function_location(func)
                mylog.error(f'{func_location}失败耗时: {perf_counter() - start_time:.4f}秒')
                raise err

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = perf_counter()
            try:
                result = await func(*args, **kwargs)
                func_location = _get_function_location(func)
                mylog.info(f'{func_location}执行耗时: {perf_counter() - start_time:.4f}秒')
                return result
            except Exception as err:
                func_location = _get_function_location(func)
                mylog.error(f'{func_location}失败耗时: {perf_counter() - start_time:.4f}秒')
                raise err

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator(fn) if fn else decorator


timer = timer_wraps


class TimerWrapt:
    """
    计时器工具类 - 同时支持装饰器和上下文管理器两种使用方式

    功能特性：
    - 作为装饰器统计函数执行时间
    - 作为上下文管理器统计代码块执行时间
    - 支持自定义日志消息
    - 保留原函数的元信息
    - 支持异常处理，确保计时准确性

    Example 1: 装饰器用法
        >>> @TimerWrapt
        >>> def process_data():
        >>>     time.sleep(0.5)
        >>>     return "Processed"
        >>> # 调用会输出: [TimerWrapt | Function:`process_data`] | <Time-Consuming 0.5003s>
        >>> result = process_data()

    Example 2: 上下文管理器用法
        >>> with TimerWrapt("数据处理"):
        >>>     time.sleep(0.3)
        >>> # 会输出: [TimerWrapt | 数据处理] | <Time-Consuming 0.3002s>

    Example 3: 带描述的上下文管理器
        >>> with TimerWrapt("复杂计算"):
        >>>     perform_complex_calculation()
    """

    def __init__(self, target: Any = None) -> None:
        """
        初始化计时器

        Args:
            target: 可以是函数(装饰器模式)或字符串描述(上下文模式)
        """
        if callable(target):
            self.func = target
            self.description = f'{target.__name__}'
            self.is_context = False
        else:
            self.func = None
            self.description = str(target) if target else 'TimerWrapt'
            self.is_context = True
        self.start_time: float = 0.0  # 初始化实例变量

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """装饰器模式：执行被装饰的函数并计时"""
        if self.is_context:
            # 允许无参调用作为上下文管理器
            return self

        if self.func is None:
            raise ValueError('TimerWrapt 装饰器模式下 func 不能为 None')

        start_time = perf_counter()
        try:
            result = self.func(*args, **kwargs)
            elapsed = perf_counter() - start_time
            func_location = _get_function_location(self.func)
            mylog.info(f'TimerWrapt {self.description} | {func_location}执行耗时:{elapsed:.4f}秒')
            return result
        except Exception as err:
            elapsed = perf_counter() - start_time
            func_location = _get_function_location(self.func)
            mylog.error(f'TimerWrapt {self.description} | {func_location}失败耗时:{elapsed:.4f}秒')
            raise err

    def __enter__(self) -> TimerWrapt:
        """上下文管理器模式：开始计时"""
        if not self.is_context:
            raise TypeError('TimerWrapt 必须用字符串初始化才能作为上下文管理器使用')
        self.start_time = perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """上下文管理器模式：结束计时并记录"""
        elapsed = perf_counter() - self.start_time
        if exc_type is not None:
            func_location = _get_function_location(self.__exit__)
            mylog.error(f'TimerWrapt {self.description} | {func_location}失败耗时:{elapsed:.4f}秒')
            return
        func_location = _get_function_location(self.__exit__)
        mylog.info(f'TimerWrapt {self.description} | {func_location}执行耗时:{elapsed:.4f}秒')

    async def __aenter__(self) -> TimerWrapt:
        """异步上下文管理器模式：开始计时"""
        if not self.is_context:
            raise TypeError('TimerWrapt 必须用字符串初始化才能作为上下文管理器使用')
        self.start_time = perf_counter()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """异步上下文管理器模式：结束计时并记录"""
        elapsed = perf_counter() - self.start_time
        if exc_type is not None:
            mylog.error(
                f' TimerWrapt {self.description} | 失败耗时:{elapsed:.4f}秒',
                callfrom=self.__aexit__,
            )
            return
        mylog.info(
            f' TimerWrapt {self.description} | 执行耗时:{elapsed:.4f}秒',
            callfrom=self.__aexit__,
        )


__all__ = [
    'TimerWrapt',
    'timer',
    'timer_wraps',
]