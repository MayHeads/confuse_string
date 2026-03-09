#### TTRouSDk 通用脚本

import sys
import os
import re

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# ==================== 需要同步的变量 ====================
# 修改下面的变量值后，运行脚本会自动同步到 config.py 和 ios/config.py

# 替换pod名字
NEW_POD_FILE_NAME = "MCCleanSDK"
# 生成处理文件 swiftUI文件
THEME_KEYWORDS = ["来电秀", "铃声", "图片", "视频", "结果"]
# 要生成的文件数量
NUM_FILES = 50
# 项目路径 (同时会同步到 ios/config.py 的 ROOT_PROJECT_DIR)
# project_path = "/Users/jiangshanchen/TTCleanerSDK"
project_path = '/Users/jiangshanchen/Desktop/pencial/LaiShow/laishow_app/ios'
# 是否是pod混淆模式
IS_POD_CONFUSE_MODE = False

ORIGIN_POD_FILE_NAME = "MyFirstLibrary"

# 忽略文件夹
custom_ignore_folders = ['Pods', 'build', 'DerivedData', '.git', 'Tests', 'UnitTests', 'UITests', '1234']
# asset 前缀
asset_prefix = "xyk"

# ==================== 同步变量列表 ====================
# 添加新变量时，只需要：1. 在上面定义变量  2. 在下面列表中添加变量名
SYNC_TO_ROOT_CONFIG = [
    'NEW_POD_FILE_NAME',
    'THEME_KEYWORDS',
    'NUM_FILES',
    'project_path',
    'IS_POD_CONFUSE_MODE',
    'custom_ignore_folders',
    'asset_prefix',
    'ORIGIN_POD_FILE_NAME',
]

# 同步到 ios/config.py 的映射 (本地变量名 -> 目标变量名)
SYNC_TO_IOS_CONFIG = {
    'project_path': 'ROOT_PROJECT_DIR',
}


def execute_pod_install():
    print("执行pod install")

    from project_scanner import get_project_info
    project_info = get_project_info()
    proj_path = project_info.project_path

    os.chdir(proj_path)
    os.system("pod install --verbose")

    print("pod install 完成")
    # 回到原来的路径
    os.chdir(current_dir)


def _replace_variable_in_content(content, var_name, var_value):
    """替换配置文件中的变量值（只替换非注释行）"""
    value_str = repr(var_value) if isinstance(var_value, str) else str(var_value)
    
    # 根据值类型选择匹配模式
    if isinstance(var_value, str):
        # 字符串类型: var = "value" 或 var = 'value'
        pattern = rf'^(?!#)(.*){var_name}\s*=\s*["\'][^"\']*["\']'
        replacement = rf'\1{var_name} = {value_str}'
    elif isinstance(var_value, bool):
        # 布尔类型: var = True/False
        pattern = rf'^(?!#)(.*){var_name}\s*=\s*(True|False)'
        replacement = rf'\1{var_name} = {value_str}'
    elif isinstance(var_value, (int, float)):
        # 数字类型: var = 123
        pattern = rf'^(?!#)(.*){var_name}\s*=\s*[\d.]+'
        replacement = rf'\1{var_name} = {value_str}'
    elif isinstance(var_value, (list, tuple)):
        # 列表/元组类型: var = [...] (单行或多行)
        # 先尝试匹配单行 (优先，因为更安全)
        pattern_single = rf'^(?!#)(.*){var_name}\s*=\s*\[[^\]\n]*\]'
        if re.search(pattern_single, content, flags=re.MULTILINE):
            return re.sub(pattern_single, rf'\1{var_name} = {value_str}', content, flags=re.MULTILINE)
        # 再尝试匹配多行 (从变量名开始到独立的])
        pattern_multiline = rf'(^(?!#).*{var_name}\s*=\s*\[)[^\]]*(\n[^\]]*)*\n\]'
        if re.search(pattern_multiline, content, flags=re.MULTILINE):
            return re.sub(pattern_multiline, rf'\1{value_str[1:]}', content, flags=re.MULTILINE)
        # 最后兜底
        pattern = rf'^(?!#)(.*){var_name}\s*=\s*\[.*?\]'
        replacement = rf'\1{var_name} = {value_str}'
    elif isinstance(var_value, dict):
        # 字典类型
        pattern = rf'^(?!#)(.*){var_name}\s*=\s*\{{.*?\}}'
        replacement = rf'\1{var_name} = {value_str}'
    else:
        # 其他类型
        pattern = rf'^(?!#)(.*){var_name}\s*=\s*\S+'
        replacement = rf'\1{var_name} = {value_str}'
    
    return re.sub(pattern, replacement, content, flags=re.MULTILINE)


def update_config_files():
    """更新配置文件中的变量值"""
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # 获取当前模块的全局变量
    current_globals = globals()
    
    # 1. 更新根目录的config.py
    root_config_path = os.path.join(project_root, "config.py")
    if os.path.exists(root_config_path):
        with open(root_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 遍历需要同步的变量
        for var_name in SYNC_TO_ROOT_CONFIG:
            if var_name in current_globals:
                var_value = current_globals[var_name]
                content = _replace_variable_in_content(content, var_name, var_value)
                print(f"  - 同步 {var_name} = {repr(var_value)}")
        
        with open(root_config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已更新根目录config.py: {root_config_path}")
    else:
        print(f"根目录config.py不存在: {root_config_path}")
    
    # 2. 更新ios/config.py
    ios_config_path = os.path.join(project_root, "confuse_ios", "ios", "config", "config.py")
    if os.path.exists(ios_config_path):
        with open(ios_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 遍历需要同步到ios config的变量
        for local_var, target_var in SYNC_TO_IOS_CONFIG.items():
            if local_var in current_globals:
                var_value = current_globals[local_var]
                content = _replace_variable_in_content(content, target_var, var_value)
                print(f"  - 同步 {local_var} -> {target_var} = {repr(var_value)}")
        
        with open(ios_config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已更新ios/config.py: {ios_config_path}")
    else:
        print(f"ios/config.py不存在: {ios_config_path}")


def insert_action():
    project_root = os.path.dirname(os.path.dirname(current_dir))
    confuse_ios_path = os.path.join(project_root, "confuse_ios")
    os.chdir(confuse_ios_path)
    os.system("python3 ios/entry/entry.py")





if __name__ == '__main__':
    
    # 先更新配置文件（必须在import依赖config的模块之前）
    update_config_files()




    # 测试修改是否正常修改
    # exit()

    # 延迟导入（因为这些模块依赖config.py，必须在update_config_files之后导入）
    from ios_replace_fix_form.z_replce_indi import z_replace_fix_form
    from ios_pod_ex.ios_pod_ex import change_pod_ex
    from project_scanner import get_project_info
    from ios_encry_string.z_enc_combin import z_enc_combin
    from ios_file_handle.z_file_combin import z_replace_file, z_gen_process

    z_gen_process()
    execute_pod_install()

    exit()


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

    insert_action()

    # 执行pod install
    execute_pod_install()




