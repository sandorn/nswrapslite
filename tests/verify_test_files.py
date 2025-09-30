# !/usr/bin/env python3
"""
验证测试文件是否存在的脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def verify_test_files():
    """验证tests目录下的测试文件是否存在"""
    # 获取tests目录
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')

    # 检查tests目录是否存在
    if not os.path.exists(tests_dir):
        return False

    # 期望的测试文件列表
    expected_files = [
        '__init__.py',
        'conftest.py',
        'test_exception.py',
        'test_executor.py',
        'test_log.py',
        'test_singleton.py',
        'test_timer.py',
        'test_validate.py',
        'test_cache.py',
        'test_retry.py',
        'test_wrapper.py',
    ]

    # 检查每个文件是否存在
    missing_files = []
    for file_name in expected_files:
        file_path = os.path.join(tests_dir, file_name)
        if not os.path.exists(file_path):
            missing_files.append(file_name)

    # 输出结果
    if missing_files:
        for file_name in missing_files:
            pass
        return False

    # 显示每个文件的大小
    total_size = 0
    for file_name in sorted(expected_files):
        file_path = os.path.join(tests_dir, file_name)
        file_size = os.path.getsize(file_path)
        total_size += file_size

    return True


if __name__ == '__main__':
    success = verify_test_files()
    sys.exit(0 if success else 1)
