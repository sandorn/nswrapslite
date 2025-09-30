# !/usr/bin/env python3
"""
验证测试文件是否存在并能被识别
"""

import importlib.util
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 获取tests目录下所有测试文件
test_dir = os.path.dirname(__file__)
test_files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]

print(f'找到 {len(test_files)} 个测试文件:')
for test_file in test_files:
    print(f'- {test_file}')

    # 尝试导入测试文件
    try:
        module_name = test_file[:-3]  # 移除.py后缀
        file_path = os.path.join(test_dir, test_file)

        # 创建模块规范
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            # 加载模块
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f'  ✓ 成功导入 {module_name}')

            # 查找测试函数
            test_functions = [func for func in dir(module) if func.startswith('test_')]
            if test_functions:
                print(f'  ✓ 找到 {len(test_functions)} 个测试函数')
            else:
                print('  ! 未找到测试函数')
        else:
            print('  ✗ 无法创建模块规范')
    except Exception as e:
        print(f'  ✗ 导入失败: {e!s}')

print('\n验证完成！')
