# 1. 清空 content_path 目录下的文件夹
# 2. 复制 ios_resource 目录下的 gen_file_swiftui 和 single_swifui_view 文件夹到 content_path
import os
import shutil
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from project_scanner import get_project_info
from config import IS_POD_CONFUSE_MODE

def find_classes_directory(project_path):
    """查找项目中的Classes目录，返回第一个找到的路径"""
    classes_paths = []
    
    for root, dirs, files in os.walk(project_path):
        for dir_name in dirs:
            if dir_name == 'Classes':
                classes_path = os.path.join(root, dir_name)
                classes_paths.append(classes_path)
                print(f"找到Classes目录: {classes_path}")
    
    # 返回第一个找到的Classes目录
    if classes_paths:
        return classes_paths[0]
    
    return None

def clear_directory(directory):
    """清空目录中的所有内容"""
    if os.path.exists(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"已清空目录: {directory}")

def copy_folders_to_content_path():
    """
    复制 ios_resource 目录下的 gen_file_swiftui 和 single_swifui_view 文件夹到 content_path
    """
    # 获取项目信息
    project_info = get_project_info()
    if not project_info:
        print("无法获取项目信息")
        return
    
    # 源文件夹路径
    source_folders = [
        "gen_file_swiftui",
        "single_swifui_view"
    ]
    
    # 根据IS_POD_CONFUSE_MODE决定目标路径
    if IS_POD_CONFUSE_MODE:
        # Pod混淆模式：查找Classes目录
        classes_path = find_classes_directory(project_info.project_path)
        if classes_path:
            target_path = classes_path
            print(f"Pod混淆模式：复制到Classes目录: {target_path}")
        else:
            # 如果没找到Classes目录，使用原来的逻辑
            target_path = project_info.content_path
            print(f"未找到Classes目录，使用默认路径: {target_path}")
    else:
        # 非Pod混淆模式：使用原来的逻辑
        target_path = project_info.content_path
        print(f"非Pod混淆模式：使用默认路径: {target_path}")
    
    # 确保目标路径存在
    os.makedirs(target_path, exist_ok=True)
    
    # 获取 ios_resource 目录的路径
    ios_resource_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ios_resource")
    
    # 先检查并删除目标路径下的文件夹
    for folder in source_folders:
        target_folder_path = os.path.join(target_path, folder)
        if os.path.exists(target_folder_path):
            print(f"删除已存在的目标文件夹: {target_folder_path}")
            shutil.rmtree(target_folder_path)
    
    # 复制每个文件夹
    for folder in source_folders:
        source_path = os.path.join(ios_resource_path, folder)
        target_folder_path = os.path.join(target_path, folder)
        
        try:
            # 复制文件夹
            shutil.copytree(source_path, target_folder_path)
            print(f"成功复制 {folder} 到 {target_folder_path}")
            
        except Exception as e:
            print(f"复制 {folder} 时出错: {str(e)}")

if __name__ == "__main__":
    copy_folders_to_content_path()
