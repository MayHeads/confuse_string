#### TTRouSDk 通用脚本

import sys
import os
import re
import importlib.util

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from ios_replace_fix_form_flutter.z_replace_fix_form_flutter import z_replace_fix_form_flutter
from ios_pod_ex.ios_pod_ex import change_pod_ex
from project_scanner import get_project_info

from ios_encry_string_flutter.z_enc_combin_flutter import z_enc_combin_flutter, z_enc_combin_flutter_swift
from ios_file_hanlde_flutter.z_file_combin_flutter import z_replace_file_flutter, z_replace_file_flutter_plugin_swift, z_replace_pkm_strings_in_flutter_plugin

# 导入 readme_replace_helper（同目录下）
try:
    from .readme_replace_helper import replace_strings_in_readme_file
except ImportError:
    # 如果相对导入失败，使用绝对导入
    readme_helper_path = os.path.join(current_dir, 'readme_replace_helper.py')
    import importlib.util
    spec = importlib.util.spec_from_file_location("readme_replace_helper", readme_helper_path)
    readme_helper_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(readme_helper_module)
    replace_strings_in_readme_file = readme_helper_module.replace_strings_in_readme_file
# # 替换pod名字
# NEW_POD_FILE_NAME = "MMPtkSDK"
# # 生成处理文件 swiftUI文件
# THEME_KEYWORDS = ["地图显示 导航"]  # 主题关键字列表
# # 要生成的文件数量
# NUM_FILES = 40  # 要生成的文件数量
# # 项目路径
# project_path = "/Users/jiangshanchen/TTRouSDK"







def insert_action():
    project_root = os.path.dirname(os.path.dirname(current_dir))
    confuse_ios_path = os.path.join(project_root, "confuse_ios")
    os.chdir(confuse_ios_path)
    os.system("python3 ios/entry/entry.py")


def execute_clean_py():
    project_info = get_project_info()
    flutter_clenpy = project_info.flutter_clenpy
    if flutter_clenpy:
        # flutter_clenpy 是文件路径，需要获取其所在目录
        clean_py_dir = os.path.dirname(flutter_clenpy)
        clean_py_file = os.path.basename(flutter_clenpy)
        
        # 切换到 clean.py 文件所在的目录
        os.chdir(clean_py_dir)
        # 执行 clean.py 文件
        os.system(f"python3 {clean_py_file}")
        print(f"已执行 clean.py: {flutter_clenpy}")
    else:
        print("未找到 clean.py 文件，跳过执行")

def load_mapping_from_log(log_file):
    """从日志文件中加载映射关系"""
    mapping = {}
    if not os.path.exists(log_file):
        return mapping
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和标题行
                if not line or '👉' in line or '👈' in line:
                    continue
                
                # 解析映射关系: old_str -> new_str 或 old_str <-----------> new_str
                if ' -> ' in line:
                    parts = line.split(' -> ', 1)
                    if len(parts) == 2:
                        old_str = parts[0].strip()
                        new_str = parts[1].strip()
                        if old_str and new_str:
                            mapping[old_str] = new_str
                elif ' <-----------> ' in line:
                    parts = line.split(' <-----------> ', 1)
                    if len(parts) == 2:
                        old_str = parts[0].strip()
                        new_str = parts[1].strip()
                        if old_str and new_str:
                            mapping[old_str] = new_str
    except Exception as e:
        print(f"读取映射日志文件 {log_file} 时出错: {str(e)}")
    
    return mapping



if __name__ == '__main__':

    # 替换文件名 flutter文件
    z_replace_file_flutter()
    # 处理 readme_file
    log_file = os.path.join(project_root, 'ios_log', 'file_name_flutter.txt')
    mapping = load_mapping_from_log(log_file)
    if mapping:
        print(f"\n=== 替换 readme_file 中的文件名映射 ===")
        replace_strings_in_readme_file(mapping)

    # 替换固定名字 flutter文件
    z_replace_fix_form_flutter()
    # 处理 readme_file
    log_file = os.path.join(project_root, 'ios_log', 'replace_fix_form_flutter.txt')
    mapping = load_mapping_from_log(log_file)
    if mapping:
        print(f"\n=== 替换 readme_file 中的固定名字映射 ===")
        replace_strings_in_readme_file(mapping)

    # 替换文件名 flutter plugin文件 swift文件
    z_replace_file_flutter_plugin_swift()
    # 处理 readme_file
    log_file = os.path.join(project_root, 'ios_log', 'file_name_flutterplugin_swift.txt')
    mapping = load_mapping_from_log(log_file)
    if mapping:
        print(f"\n=== 替换 readme_file 中的文件名映射 ===")
        replace_strings_in_readme_file(mapping)

    # 替换文件内容 flutter plugin文件 swift文件
    z_replace_pkm_strings_in_flutter_plugin()
    # 处理 readme_file
    log_file = os.path.join(project_root, 'ios_log', 'file_name_flutterplugin_content.txt')
    mapping = load_mapping_from_log(log_file)
    if mapping:
        print(f"\n=== 替换 readme_file 中的内容映射 ===")
        replace_strings_in_readme_file(mapping)

    # 加密字符串 flutter文件
    z_enc_combin_flutter()


    # 加密字符串 flutter plugin文件 swift文件
    z_enc_combin_flutter_swift()

    # 插入垃圾代码
    insert_action()



    # 替换pod名字  这个可以统一用flutter
    change_pod_ex()

    # 执行clean.py文件
    execute_clean_py()








