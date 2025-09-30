#!/usr/bin/env python3
"""
直接运行单个测试文件中的测试函数
"""

import argparse
import asyncio
import importlib.util
import inspect
import os
import sys
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_single_test_file(file_path):
    """运行单个测试文件中的所有测试函数"""

    # 获取文件名和模块名
    file_name = os.path.basename(file_path)
    module_name = file_name[:-3]  # 移除.py后缀

    try:
        # 导入测试模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module

            # 尝试导入pytest，如果失败则模拟pytest.raises
            try:
                import pytest

                module.__dict__['pytest'] = pytest
            except ImportError:
                # 模拟pytest.raises
                class MockRaises:
                    def __init__(self, expected_exception, match=None):
                        self.expected_exception = expected_exception
                        self.match = match

                    def __enter__(self):
                        return self

                    def __exit__(self, exc_type, exc_val, exc_tb):
                        if exc_type is None:
                            raise AssertionError(f'DID NOT RAISE {self.expected_exception!r}')
                        return issubclass(exc_type, self.expected_exception)

                class MockPytest:
                    @staticmethod
                    def raises(expected_exception, match=None):
                        return MockRaises(expected_exception, match)

                module.__dict__['pytest'] = MockPytest()

            # 执行模块
            spec.loader.exec_module(module)

            # 查找测试函数
            test_functions = [getattr(module, func_name) for func_name in dir(module) if func_name.startswith('test_') and callable(getattr(module, func_name))]

            if not test_functions:
                return False

            len(test_functions)
            passed_tests = 0
            failed_tests = 0

            # 运行每个测试函数
            for test_func in test_functions:
                func_name = test_func.__name__

                try:
                    # 检查函数是否为协程函数
                    if inspect.iscoroutinefunction(test_func):
                        # 使用事件循环运行异步函数
                        asyncio.run(test_func())
                    else:
                        # 直接运行同步函数
                        test_func()
                    passed_tests += 1
                except Exception:
                    # 显示简短的堆栈跟踪
                    tb_lines = traceback.format_exc().split('\n')
                    for line in tb_lines:
                        if module_name in line and func_name in line:
                            break
                    failed_tests += 1

            # 输出结果摘要

            return failed_tests == 0
        return False
    except Exception:
        return False


if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='直接运行单个测试文件')
    parser.add_argument('test_file', help='测试文件路径')

    # 解析命令行参数
    args = parser.parse_args()
    test_file_path = args.test_file

    # 确保文件路径是绝对路径
    if not os.path.isabs(test_file_path):
        test_file_path = os.path.join(os.getcwd(), test_file_path)

    # 检查文件是否存在
    if not os.path.exists(test_file_path):
        sys.exit(1)

    # 运行测试
    success = run_single_test_file(test_file_path)

    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)
