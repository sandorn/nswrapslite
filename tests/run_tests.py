# !/usr/bin/env python3
"""
运行所有测试的脚本
"""

import asyncio
import importlib.util
import inspect
import os
import sys
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class SimpleTestFramework:
    """简单的测试框架，支持同步和异步测试"""

    @staticmethod
    def run_test(test_func):
        """运行单个测试函数，处理同步和异步函数"""

        # 检查函数是否为异步函数
        if inspect.iscoroutinefunction(test_func):
            # 运行异步测试函数
            try:
                loop = asyncio.get_event_loop()
                # 如果事件循环已关闭，创建新的
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                loop.run_until_complete(test_func())
                return True, None
            except Exception as e:
                return False, e
        else:
            # 运行同步测试函数
            try:
                test_func()
                return True, None
            except Exception as e:
                return False, e


class MockPytest:
    """模拟pytest的一些基本功能"""

    class MockRaises:
        def __init__(self, expected_exception):
            self.expected_exception = expected_exception
            self.exception_occurred = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                # 没有异常抛出，应该失败
                raise AssertionError(f'DID NOT RAISE {self.expected_exception!r}')
            if not issubclass(exc_type, self.expected_exception):
                # 抛出了异常，但不是预期的异常类型
                return False  # 让异常继续传播

            self.exception_occurred = True
            return True  # 捕获异常

    @staticmethod
    def raises(expected_exception):
        return MockPytest.MockRaises(expected_exception)


# 将模拟的pytest添加到sys.modules中，以便测试可以导入它
sys.modules['pytest'] = MockPytest()


def run_all_tests():
    """手动运行所有测试文件中的测试函数"""
    # 获取tests目录
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')

    # 查找所有测试文件
    test_files = [f for f in os.listdir(tests_dir) if f.startswith('test_') and f.endswith('.py')]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    # 遍历每个测试文件
    for test_file in test_files:
        file_path = os.path.join(tests_dir, test_file)
        module_name = test_file[:-3]  # 移除.py后缀

        try:
            # 导入测试模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module

                # 在执行模块前，添加mock的pytest到模块命名空间
                module.__dict__['pytest'] = MockPytest()

                spec.loader.exec_module(module)

                # 查找测试函数
                test_functions = [getattr(module, func_name) for func_name in dir(module) if func_name.startswith('test_') and callable(getattr(module, func_name))]

                len(test_functions)
                file_passed = 0
                file_failed = 0

                # 运行每个测试函数
                for test_func in test_functions:
                    total_tests += 1

                    success, _error = SimpleTestFramework.run_test(test_func)
                    if success:
                        passed_tests += 1
                        file_passed += 1
                    else:
                        tb_lines = traceback.format_exc().split('\n')
                        # 找到有用的堆栈跟踪行
                        for line in tb_lines:
                            if 'test_' in line and file_path in line:
                                break
                        failed_tests += 1
                        file_failed += 1

            else:
                failed_tests += 1
        except Exception:
            failed_tests += 1

    # 输出总结果

    return failed_tests == 0


if __name__ == '__main__':
    # 运行所有测试
    success = run_all_tests()

    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)
