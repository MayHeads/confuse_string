# 重命名文件名
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from ios_string_generate.string_gen import get_random_class_name, init_word_lists

from config import REPLACE_IGNORE_FILE_NAMES

# 需要忽略的文件名列表
IGNORE_FILE_NAMES = REPLACE_IGNORE_FILE_NAMES

def rename_swift_files(swift_files):
    """重命名Swift文件并记录映射关系"""
    # 初始化词库
    init_word_lists()
    
    # 存储文件名映射关系
    name_mapping = {}
    
    # 创建日志目录
    log_dir = os.path.join(os.getcwd(), 'ios_log')
    os.makedirs(log_dir, exist_ok=True)
    
    # 处理每个Swift文件
    for file_path in swift_files:
        # 获取文件名（不含扩展名）
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 检查是否在忽略列表中
        if file_name in IGNORE_FILE_NAMES:
            print(f"忽略文件: {file_name}")
            continue
            
        # 生成新的文件名
        new_name = get_random_class_name()
        if new_name is None:
            print(f"无法为文件 {file_name} 生成新名称")
            continue
            
        # 构建新文件路径
        dir_path = os.path.dirname(file_path)
        new_file_path = os.path.join(dir_path, f"{new_name}.swift")
        
        try:
            # 重命名文件
            os.rename(file_path, new_file_path)
            name_mapping[file_name] = new_name
            print(f"重命名文件: {file_name} -> {new_name}")
        except Exception as e:
            print(f"重命名文件 {file_name} 时出错: {str(e)}")
    
    # 写入映射关系到日志文件
    log_file = os.path.join(log_dir, 'file_name.txt')
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            for old_name, new_name in name_mapping.items():
                f.write(f"{old_name} -> {new_name}\n")
        print(f"文件名映射关系已写入: {log_file}")
    except Exception as e:
        print(f"写入映射关系时出错: {str(e)}")
    
    return name_mapping

def rename_swift_file():
    project_info = get_project_info()
    swift_all_files = project_info.all_swift_files
    
    # 重命名文件
    name_mapping = rename_swift_files(swift_all_files)
    print(f"总共重命名了 {len(name_mapping)} 个文件")


if __name__ == '__main__':
    rename_swift_file()