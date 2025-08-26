#### TTRouSDk 通用脚本

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from ios_replace_fix_form.z_replce_indi import z_replace_fix_form
from ios_pod_ex.ios_pod_ex import change_pod_ex
from project_scanner import get_project_info

from ios_encry_string.z_enc_combin import z_enc_combin

from ios_file_handle.z_file_combin import z_replace_file, z_gen_process



def execute_pod_install():
    print("执行pod install")

    project_info = get_project_info()
    project_path = project_info.project_path

    os.chdir(project_path)
    os.system("pod install --verbose")

    print("pod install 完成")
    # 回到原来的路径
    os.chdir(current_dir)





if __name__ == '__main__':

    # 替换pod名字
    change_pod_ex()

    # 替换固定名字
    z_replace_fix_form()

    # 加密字符串
    z_enc_combin()

    # 替换文件名
    z_replace_file()

    # 生成处理文件 swiftUI文件
    z_gen_process()

    # 执行pod install
    execute_pod_install()




