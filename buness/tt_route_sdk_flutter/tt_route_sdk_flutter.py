#### TTRouSDk 通用脚本

import sys
import os
import re

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from ios_replace_fix_form_flutter.z_replace_fix_form_flutter import z_replace_fix_form_flutter
from ios_pod_ex.ios_pod_ex import change_pod_ex
from project_scanner import get_project_info

from ios_encry_string_flutter.z_enc_combin_flutter import z_enc_combin_flutter, z_enc_combin_flutter_swift
from ios_file_hanlde_flutter.z_file_combin_flutter import z_replace_file_flutter, z_replace_file_flutter_plugin_swift, z_replace_pkm_strings_in_flutter_plugin
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



if __name__ == '__main__':

    # 替换文件名 flutter文件
    z_replace_file_flutter()

    # 替换固定名字 flutter文件
    z_replace_fix_form_flutter()

    # 替换文件名 flutter plugin文件 swift文件
    z_replace_file_flutter_plugin_swift()


    # 替换文件内容 flutter plugin文件 swift文件
    z_replace_pkm_strings_in_flutter_plugin()

    # 加密字符串 flutter文件
    z_enc_combin_flutter()

    # 加密字符串 flutter plugin文件 swift文件
    z_enc_combin_flutter_swift()


    # 替换pod名字  这个可以统一用flutter
    change_pod_ex()

    # 执行clean.py文件
    execute_clean_py()






