

#### TTRouSDk 通用脚本

import sys
import os
import re

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from ios_replace_fix_form.z_replce_indi import z_replace_fix_form
from ios_pod_ex.ios_pod_ex import change_pod_ex
from project_scanner import get_project_info

from ios_encry_string.z_enc_combin import z_enc_combin

from ios_file_handle.z_file_combin import z_replace_file, z_gen_process

from ios_asset_deal.z_asset_combin import z_asset_combin
from ios_asset_deal.gener_imageset import entry_gener_imageset

# # 替换pod名字
# NEW_POD_FILE_NAME = "YetRateSDK"
# # 生成处理文件 swiftUI文件
# THEME_KEYWORDS = ["心率", "统计"]  # 主题关键字列表
# # 要生成的文件数量
# NUM_FILES = 54  # 要生成的文件数量
# # 项目路径
# project_path = "/Users/jiangshanchen/TTRouSDK"


def execute_pod_install():
    print("执行pod install")

    project_info = get_project_info()
    project_path = project_info.project_path

    os.chdir(project_path)
    os.system("pod install --verbose")

    print("pod install 完成")
    # 回到原来的路径
    os.chdir(current_dir)


def update_config_files():
    """更新配置文件中的变量值"""
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # 1. 更新根目录的config.py
    root_config_path = os.path.join(project_root, "config.py")
    if os.path.exists(root_config_path):
        with open(root_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换NEW_POD_FILE_NAME
        content = re.sub(r'NEW_POD_FILE_NAME = "[^"]*"', f'NEW_POD_FILE_NAME = "{NEW_POD_FILE_NAME}"', content)
        
        # 替换THEME_KEYWORDS
        keywords_str = str(THEME_KEYWORDS)
        content = re.sub(r'THEME_KEYWORDS = \[[^\]]*\]', f'THEME_KEYWORDS = {keywords_str}', content)
        
        # 替换NUM_FILES
        content = re.sub(r'NUM_FILES = \d+', f'NUM_FILES = {NUM_FILES}', content)
        
        # 替换project_path
        content = re.sub(r'project_path = "[^"]*"', f'project_path = "{project_path}"', content)
        
        with open(root_config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已更新根目录config.py: {root_config_path}")
    
    # 2. 更新ios/config.py中的ROOT_PROJECT_DIR
    ios_config_path = os.path.join(project_root, "confuse_ios", "ios", "config", "config.py")
    if os.path.exists(ios_config_path):
        with open(ios_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换ROOT_PROJECT_DIR
        content = re.sub(r'ROOT_PROJECT_DIR = "[^"]*"', f'ROOT_PROJECT_DIR = "{project_path}"', content)
        
        with open(ios_config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已更新ios/config.py: {ios_config_path}")


def insert_action():
    project_root = os.path.dirname(os.path.dirname(current_dir))
    confuse_ios_path = os.path.join(project_root, "confuse_ios")
    os.chdir(confuse_ios_path)
    os.system("python3 ios/entry/entry.py")





if __name__ == '__main__':
    

    # z_asset_combin()
    entry_gener_imageset()



    # # 生成处理文件 swiftUI文件
    z_gen_process()

    # z_replace_fix_form()
    # z_replace_file()

    # z_enc_combin()

    # insert_action()





    # 执行pod install
    # execute_pod_install()




