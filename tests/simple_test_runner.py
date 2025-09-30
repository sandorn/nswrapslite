# !/usr/bin/env python3
"""
简单的测试运行器，不依赖外部测试框架
"""

import asyncio
import importlib.util
import inspect
import os
import sys
import time
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class SimpleTestRunner:
    """简单的测试运行器，支持同步和异步测试函数"""

    @staticmethod
    def run_test(test_func):
        """运行单个测试函数，处理同步和异步函数"""
        start_time = time.time()

        try:
            # 检查函数是否为异步函数
            if inspect.iscoroutinefunction(test_func):
                # 运行异步测试函数
                loop = asyncio.get_event_loop()
                # 如果事件循环已关闭，创建新的
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                loop.run_until_complete(test_func())
            else:
                # 运行同步测试函数
                test_func()

            elapsed = time.time() - start_time
            return True, None, elapsed
        except Exception as e:
            elapsed = time.time() - start_time
            return False, e, elapsed

    @staticmethod
    def run_all_tests(test_dir='tests'):
        """运行指定目录下的所有测试文件"""
        # 获取tests目录的绝对路径
        tests_dir = os.path.join(os.path.dirname(__file__), test_dir)

        # 检查目录是否存在
        if not os.path.exists(tests_dir):
            return False

        # 查找所有测试文件
        test_files = [f for f in os.listdir(tests_dir) if f.startswith('test_') and f.endswith('.py')]

        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        total_time = 0

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
                    spec.loader.exec_module(module)

                    # 查找测试函数
                    test_functions = [getattr(module, func_name) for func_name in dir(module) if func_name.startswith('test_') and callable(getattr(module, func_name))]

                    len(test_functions)
                    file_passed = 0
                    file_failed = 0
                    file_time = 0

                    # 运行每个测试函数
                    for test_func in test_functions:
                        total_tests += 1

                        success, _error, elapsed = SimpleTestRunner.run_test(test_func)
                        file_time += elapsed
                        total_time += elapsed

                        if success:
                            passed_tests += 1
                            file_passed += 1
                        else:
                            # 获取有用的堆栈信息
                            tb = traceback.format_exc().split('\n')
                            for line in tb:
                                if module_name in line and 'test_' in line:
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
    success = SimpleTestRunner.run_all_tests()

    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)
