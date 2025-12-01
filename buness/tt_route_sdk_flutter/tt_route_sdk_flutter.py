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

from ios_encry_string_flutter.z_enc_combin_flutter import z_enc_combin_flutter
from ios_file_hanlde_flutter.z_file_combin_flutter import z_replace_file_flutter
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





if __name__ == '__main__':

    # 替换文件名
    z_replace_file_flutter()

    # 替换固定名字
    z_replace_fix_form_flutter()

    # 加密字符串
    z_enc_combin_flutter()


    # 替换pod名字  这个可以统一用flutter
    change_pod_ex()






