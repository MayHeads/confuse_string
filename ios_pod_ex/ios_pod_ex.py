# 替换本地pod中相关的sdk名字

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info

from config import ORIGIN_POD_FILE_NAME, NEW_POD_FILE_NAME

fix_phase = ORIGIN_POD_FILE_NAME
new_phase = NEW_POD_FILE_NAME


def rename_directories(project_path):
    """递归重命名包含目标字符串的目录"""
    renamed_dirs_count = 0
    
    # 从最深层的目录开始处理，避免路径变化影响遍历
    for root, dirs, files in os.walk(project_path, topdown=False):
        for dir_name in dirs:
            old_dir_path = os.path.join(root, dir_name)
            
            # 检查目录名是否需要替换
            if fix_phase in dir_name:
                new_dir_name = dir_name.replace(fix_phase, new_phase)
                new_dir_path = os.path.join(root, new_dir_name)
                
                try:
                    os.rename(old_dir_path, new_dir_path)
                    print(f"重命名目录: {old_dir_path} -> {new_dir_path}")
                    renamed_dirs_count += 1
                except Exception as e:
                    print(f"重命名目录失败 {old_dir_path}: {str(e)}")
    
    return renamed_dirs_count


def change_pod_ex():
    delete_empty_folders()
    
    project_info = get_project_info()
    project_path = project_info.project_path
    
    print(f"开始替换项目中的 {fix_phase} 为 {new_phase}")
    print(f"项目路径: {project_path}")
    
    # 首先处理目录名的替换
    print("\n=== 处理目录名替换 ===")
    renamed_dirs_count = rename_directories(project_path)
    print(f"重命名目录数量: {renamed_dirs_count}")
    
    # 统计替换的文件数量
    replaced_files_count = 0
    total_replacements = 0
    
    print("\n=== 处理文件名和内容替换 ===")
    # 遍历项目中的所有文件
    for root, dirs, files in os.walk(project_path):
        # 跳过一些不需要处理的目录
        dirs[:] = [d for d in dirs if d not in ['.git', 'build', 'DerivedData', 'Pods']]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 处理文件名中的替换
            old_file_name = file
            new_file_name = file.replace(fix_phase, new_phase)
            
            # 如果文件名需要替换
            if old_file_name != new_file_name:
                new_file_path = os.path.join(root, new_file_name)
                try:
                    os.rename(file_path, new_file_path)
                    print(f"重命名文件: {file_path} -> {new_file_path}")
                    file_path = new_file_path
                    replaced_files_count += 1
                except Exception as e:
                    print(f"重命名文件失败 {file_path}: {str(e)}")
            
            # 处理文件内容中的替换
            try:
                # 尝试读取文件内容
                encodings = ['utf-8', 'utf-16', 'ascii', 'latin1']
                content = None
                used_encoding = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        used_encoding = encoding
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    print(f"无法读取文件 {file_path}，跳过")
                    continue
                
                # 检查是否需要替换
                if fix_phase in content:
                    # 替换内容
                    new_content = content.replace(fix_phase, new_phase)
                    
                    # 写回文件
                    with open(file_path, 'w', encoding=used_encoding) as f:
                        f.write(new_content)
                    
                    # 统计替换次数
                    replacements = content.count(fix_phase)
                    total_replacements += replacements
                    
                    print(f"更新文件内容: {file_path} (替换了 {replacements} 处)")
                    replaced_files_count += 1
                    
            except Exception as e:
                print(f"处理文件内容失败 {file_path}: {str(e)}")
    
    print(f"\n=== 替换完成！===")
    print(f"重命名目录数量: {renamed_dirs_count}")
    print(f"处理的文件数量: {replaced_files_count}")
    print(f"总替换次数: {total_replacements}")

def delete_empty_folders():
    project_info = get_project_info()
    project_path = project_info.project_path

    print(f"开始清理空目录: {project_path}")

    # 递归删除空目录的通用函数
    def recursive_delete_empty_dirs(root_path, deleted_count=[0]):
        """递归删除空目录，如果子目录都为空，则删除当前目录"""
        if not os.path.exists(root_path):
            return False

        try:
            # 获取目录内容
            items = os.listdir(root_path)
            has_non_empty_subdir = False

            # 递归处理所有子目录
            for item in items:
                item_path = os.path.join(root_path, item)
                if os.path.isdir(item_path):
                    # 递归删除子目录中的空目录
                    if recursive_delete_empty_dirs(item_path, deleted_count):
                        has_non_empty_subdir = True

            # 重新检查当前目录是否为空
            remaining_items = os.listdir(root_path)

            # 如果目录为空（没有任何文件或子目录），则删除它
            if not remaining_items:
                try:
                    parent_dir = os.path.dirname(root_path)
                    os.rmdir(root_path)
                    deleted_count[0] += 1
                    print(f"删除空目录: {root_path}")
                    return False  # 返回False表示这个目录被删除了
                except OSError as e:
                    print(f"无法删除目录 {root_path}: {e}")
                    return True  # 返回True表示删除失败，目录仍然存在
            else:
                return True  # 目录不为空，返回True

        except OSError as e:
            print(f"无法访问目录 {root_path}: {e}")
            return True

    # 统计删除的目录数量
    deleted_count = [0]

    # 从项目根目录开始递归删除空目录
    recursive_delete_empty_dirs(project_path, deleted_count)

    print(f"空目录清理完成，共删除 {deleted_count[0]} 个空目录")

if __name__ == '__main__':

    print(f"开始替换项目中的 {fix_phase} 为 {new_phase}")
    # change_pod_ex()
    delete_empty_folders()
    print(f"替换完成")




