# NSWrapsLite

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://badge.fury.io/py/nswrapslite.svg)](https://pypi.org/project/nswrapslite/)

## 项目简介

NSWrapsLite 是一个功能强大的 Python 装饰器工具库，提供一系列实用的装饰器和工具函数，用于简化日常开发工作。

## 功能特性

### 核心功能
- **统一装饰器接口**：简化同步/异步函数的装饰器实现
- **日志记录装饰器**：提供函数调用的详细日志
- **函数执行计时器**：监控同步/异步函数的执行时间
- **自动重试机制**：优化网络请求和不稳定操作的成功率
- **线程池执行器包装器**：简化异步执行同步函数
- **单例模式实现**：提供多种单例装饰器和混入类
- **缓存装饰器**：提供函数结果缓存功能
- **类型检查和验证装饰器**：确保函数参数和返回值类型正确

### 设计特点
- **统一的 API 设计**：简化装饰器使用体验
- **自动识别并适配**：同步和异步函数无缝切换
- **完整的异常捕获和处理机制**：提高代码健壮性
- **符合现代 Python 类型注解规范**：增强代码可读性和IDE支持
- **支持多种组合使用场景**：灵活应对不同需求
- **线程安全的单例实现**：确保多线程环境下的安全性
- **完整的类型提示支持**：提高开发效率和代码质量

## 安装方法

使用 pip 安装 NSWrapsLite：

```bash
pip install nswrapslite
```

## 使用示例

### 1. 日志装饰器

```python
from nswrapslite import log_wraps

@log_wraps
def add_numbers(a: int, b: int) -> int:
    return a + b

# 调用函数，会自动记录函数调用信息
result = add_numbers(5, 3)
```

### 2. 计时装饰器

```python
from nswrapslite import timer_wraps

@timer_wraps
def slow_function():
    import time
    time.sleep(1)  # 模拟耗时操作
    return "完成"

# 调用函数，会自动记录执行时间
result = slow_function()
```

### 3. 异常处理装饰器

```python
from nswrapslite import exc_wraps

@exc_wraps(re_raise=False, default_return=0)
def divide(a: int, b: int) -> float:
    return a / b

# 安全调用，即使除零也不会崩溃
result = divide(10, 0)  # 返回 0
```

### 4. 重试装饰器

```python
from nswrapslite import retry_wraps

@retry_wraps(max_retries=3, delay=1)
def unstable_operation():
    # 模拟不稳定操作，可能会失败
    import random
    if random.random() < 0.7:
        raise ConnectionError("连接失败")
    return "操作成功"

# 调用函数，会自动重试失败的操作
result = unstable_operation()
```

### 5. 单例模式

```python
from nswrapslite import singleton

@singleton
def get_database_connection():
    # 模拟数据库连接初始化
    print("初始化数据库连接...")
    return {"connection": "active"}

# 多次调用返回相同实例
conn1 = get_database_connection()
conn2 = get_database_connection()
assert conn1 is conn2
```

### 6. 缓存装饰器

```python
from nswrapslite import cache_wrapper

@cache_wrapper(ttl=60)  # 缓存60秒
def expensive_computation(x: int, y: int) -> int:
    # 模拟耗时计算
    print(f"执行计算: {x} + {y}")
    return x + y

# 首次调用会执行计算并缓存结果
result1 = expensive_computation(10, 20)
# 再次调用会直接返回缓存结果，不执行计算
result2 = expensive_computation(10, 20)
```

## 更多示例

请查看 [examples](examples/) 目录下的示例文件，了解更多使用方法：

- `example_log.py`: 演示如何使用日志装饰器和日志记录器
- `example_exception.py`: 演示如何使用异常处理功能
- `example_retry.py`: 演示如何使用重试机制
- `example_cache.py`: 演示如何使用缓存功能
- `example_timer.py`: 演示如何使用计时器功能
- `example_singleton.py`: 演示如何使用单例模式
- `example_validate.py`: 演示如何使用数据验证功能
- `example_wrapper.py`: 演示如何使用函数包装器

## 开发要求

- Python 3.13+
- 依赖项见 [requirements.txt](requirements.txt)

## 贡献指南

欢迎提交问题和改进建议！如果您想为项目贡献代码，请遵循以下步骤：

1. Fork 项目仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 作者

**sandorn**
- GitHub: [@sandorn](https://github.com/sandorn)
- Email: sandorn@live.cn