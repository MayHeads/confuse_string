import os
import sys

# 添加当前目录到路径，以便导入同目录下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加项目根目录到路径
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 导入同目录下的模块
from file_name_flutter import rename_dart_file
from file_name_flutterplugin_swift import rename_swift_file_flutterplugin_swift
from file_name_flutterplugin_content import replace_pkm_strings_in_flutter_plugin

# 重命名Flutter Dart文件
def z_replace_file_flutter():
    """重命名Flutter Dart文件"""
    rename_dart_file()

# 重命名Flutter Plugin .swift文件
def z_replace_file_flutter_plugin_swift():
    """重命名Flutter Plugin文件"""
    rename_swift_file_flutterplugin_swift()

# 替换Flutter Plugin .swift文件内容中的_pkm字符串
def z_replace_pkm_strings_in_flutter_plugin():
    """重命名Flutter Plugin文件内容"""
    replace_pkm_strings_in_flutter_plugin()


if __name__ == '__main__':
    z_replace_file_flutter()
    z_replace_file_flutter_plugin_swift()
    z_replace_pkm_strings_in_flutter_plugin()
