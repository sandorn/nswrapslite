# !/usr/bin/env python3
"""
==============================================================
Description  : nswraps - 功能强大的Python装饰器工具库
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-08-28 10:53:57
LastEditTime : 2025-09-27 01:00:00
Github       : https://github.com/sandorn/nswraps

nswraps是一个功能强大的Python装饰器工具库，提供以下核心功能：

核心功能:
- 统一的装饰器接口，简化同步/异步函数的装饰器实现
- 日志记录装饰器，提供函数调用的详细日志
- 函数执行计时器，监控同步/异步函数的执行时间
- 自动重试机制，优化网络请求和不稳定操作的成功率
- 线程池执行器包装器，简化异步执行同步函数
- 单例模式实现，提供多种单例装饰器和混入类
- 缓存装饰器，提供函数结果缓存功能
- 类型检查和验证装饰器

主要特性:
- 统一的API设计，简化装饰器使用体验
- 自动识别并适配同步和异步函数
- 完整的异常捕获和处理机制
- 符合现代Python类型注解规范
- 支持多种组合使用场景
- 线程安全的单例实现
- 完整的类型提示支持
==============================================================
"""

from __future__ import annotations

from .cache import cache_wrapper
from .exception import exc_wraps
from .executor import executor_wraps, future_wraps, run_executor_wraps
from .log import log_wraps
from .retry import retry_wraps
from .singleton import SingletonMeta, SingletonMixin, SingletonWraps, singleton
from .timer import TimerWrapt, timer, timer_wraps
from .validate import (
    TypedProperty,
    ensure_initialized,
    readonly,
    type_check_wrapper,
    typeassert,
    typed_property,
)
from .wrapper import decorator_factory, exc_wrapper, log_wrapper, timer_wrapper

__version__ = '0.0.8'
__author__ = 'sandorn'
__email__ = 'sandorn@live.cn'

__all__ = [
    'SingletonMeta',
    'SingletonMixin',
    'SingletonWraps',
    'TimerWrapt',
    'TypedProperty',
    'cache_wrapper',
    'decorator_factory',
    'ensure_initialized',
    'exc_wrapper',
    'exc_wraps',
    'executor_wraps',
    'future_wraps',
    'log_wrapper',
    'log_wraps',
    'readonly',
    'retry_wraps',
    'run_executor_wraps',
    'singleton',
    'timer',
    'timer_wrapper',
    'timer_wraps',
    'type_check_wrapper',
    'typeassert',
    'typed_property',
]
