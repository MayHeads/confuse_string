# 重命名Flutter Dart文件名
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from ios_string_generate.string_gen import get_random_class_name, init_word_lists
from config import REPLACE_IGNORE_FILE_NAMES, STRING_SUFFIX
# 更改.dart 文件名 【fluttersdk中的目录结构】
# 需要忽略的文件名列表
IGNORE_FILE_NAMES = REPLACE_IGNORE_FILE_NAMES

def rename_dart_files(dart_files):
    """重命名Dart文件并记录映射关系"""
    # 初始化词库
    init_word_lists()
    
    # 存储文件名映射关系
    name_mapping = {}
    
    # 创建日志目录
    log_dir = os.path.join(os.getcwd(), 'ios_log')
    os.makedirs(log_dir, exist_ok=True)
    
    # 处理每个Dart文件
    for file_path in dart_files:
        # 获取文件名（不含扩展名）
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 检查是否在忽略列表中
        if file_name in IGNORE_FILE_NAMES:
            print(f"忽略文件: {file_name}")
            continue
        
        # 只重命名以 _pkm 结尾的文件名
        if not file_name.endswith(STRING_SUFFIX):
            # 不是以 _pkm 结尾的文件，跳过
            continue
        
        # 以 _pkm 结尾的文件名，需要重命名
        print(f"检测到以 {STRING_SUFFIX} 结尾的文件名: {file_name}")
            
        # 生成新的文件名
        new_name = get_random_class_name()
        if new_name is None:
            print(f"无法为文件 {file_name} 生成新名称")
            continue
            
        # 构建新文件路径
        dir_path = os.path.dirname(file_path)
        new_file_path = os.path.join(dir_path, f"{new_name}.dart")
        
        try:
            # 重命名文件
            os.rename(file_path, new_file_path)
            name_mapping[file_name] = new_name
            print(f"重命名文件: {file_name} -> {new_name}")
        except Exception as e:
            print(f"重命名文件 {file_name} 时出错: {str(e)}")
    
    # 写入映射关系到日志文件
    log_file = os.path.join(log_dir, 'file_name_flutter.txt')
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("👉👉👉👉👉Flutter File Name Mapping List👈👈👈👈👈\n\n\n")
            for old_name, new_name in name_mapping.items():
                f.write(f"{old_name} -> {new_name}\n")
        print(f"文件名映射关系已写入: {log_file}")
    except Exception as e:
        print(f"写入映射关系时出错: {str(e)}")
    
    return name_mapping

def load_name_mapping_from_log(log_file):
    """
    从映射日志文件中加载文件名映射关系
    格式: old_name -> new_name
    """
    name_mapping = {}
    
    if not os.path.exists(log_file):
        print(f"映射日志文件不存在: {log_file}")
        return name_mapping
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和标题行
                if not line or '👉' in line or '👈' in line:
                    continue
                
                # 解析映射关系: old_name -> new_name
                if ' -> ' in line:
                    parts = line.split(' -> ', 1)
                    if len(parts) == 2:
                        old_name = parts[0].strip()
                        new_name = parts[1].strip()
                        if old_name and new_name:
                            name_mapping[old_name] = new_name
                            print(f"加载映射: {old_name} -> {new_name}")
    except Exception as e:
        print(f"读取映射日志文件时出错: {str(e)}")
    
    return name_mapping

def update_file_references(dart_files, name_mapping):
    """
    更新所有Dart文件中对旧文件名的引用
    逐行检查，如果一行中包含旧文件名，就替换为新文件名
    """
    updated_count = 0
    
    if not name_mapping:
        print("没有映射关系，跳过引用更新")
        return updated_count
    
    for file_path in dart_files:
        try:
            # 读取文件
            encodings = ['utf-8', 'utf-16', 'ascii', 'latin1']
            lines = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    used_encoding = encoding
                    break
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            if lines is None:
                print(f"无法读取文件 {file_path}")
                continue
            
            # 逐行检查并替换
            modified = False
            new_lines = []
            
            for line in lines:
                original_line = line
                # 对每一行，检查是否包含旧文件名，如果包含就直接替换
                for old_name, new_name in name_mapping.items():
                    # 简单替换：如果行中包含旧文件名，就直接替换为新文件名
                    if old_name in line:
                        line = line.replace(old_name, new_name)
                        if line != original_line:
                            modified = True
                            print(f"  替换: {old_name} -> {new_name} (在文件 {os.path.basename(file_path)} 中)")
                            original_line = line  # 更新原始行，避免重复替换
                
                new_lines.append(line)
            
            if modified:
                # 写回文件
                with open(file_path, 'w', encoding=used_encoding) as f:
                    f.writelines(new_lines)
                updated_count += 1
                print(f"已更新文件引用: {file_path}")
            
        except Exception as e:
            print(f"更新文件 {file_path} 时出错: {str(e)}")
    
    return updated_count

def rename_dart_file():
    """重命名Flutter Dart文件的主函数"""
    project_info = get_project_info()
    if not project_info:
        print("无法获取项目信息，程序退出")
        return
    
    flutter_plugin_path = project_info.flutter_plugin_path
    flutter_plugin_dart_files = project_info.flutter_plugin_dart_files
    
    # 检查是否有flutter_plugin_path
    if not flutter_plugin_path or not flutter_plugin_dart_files:
        print("未找到flutter_plugin_path或dart文件，跳过Flutter文件重命名")
        # 创建空日志文件
        log_dir = os.path.join(os.getcwd(), 'ios_log')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'file_name_flutter.txt')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("👉👉👉👉👉Flutter File Name Mapping List👈👈👈👈👈\n\n\n")
        return
    
    print(f"开始重命名Flutter Dart文件...")
    print(f"Flutter Plugin路径: {flutter_plugin_path}")
    print(f"找到 {len(flutter_plugin_dart_files)} 个Dart文件")
    
    # 步骤1: 重命名文件
    name_mapping = rename_dart_files(flutter_plugin_dart_files)
    print(f"总共重命名了 {len(name_mapping)} 个文件")
    
    if not name_mapping:
        print("没有文件需要重命名，跳过引用更新")
        return
    
    # 步骤2: 从映射日志文件中加载映射关系
    log_file = os.path.join(os.getcwd(), 'ios_log', 'file_name_flutter.txt')
    print(f"\n从映射日志文件加载映射关系: {log_file}")
    loaded_mapping = load_name_mapping_from_log(log_file)
    
    if not loaded_mapping:
        print("无法从日志文件加载映射关系，使用内存中的映射")
        loaded_mapping = name_mapping
    
    # 步骤3: 重新扫描flutter_plugin_path，获取最新的文件列表
    print(f"\n重新扫描flutter_plugin_path获取最新的文件列表...")
    updated_project_info = get_project_info()
    if not updated_project_info:
        print("无法重新获取项目信息，使用原始文件列表")
        updated_dart_files = flutter_plugin_dart_files
    else:
        updated_dart_files = updated_project_info.flutter_plugin_dart_files
        print(f"重新扫描后找到 {len(updated_dart_files)} 个Dart文件")
    
    # 步骤4: 更新所有Dart文件中对旧文件名的引用
    print(f"\n开始更新文件引用...")
    print(f"将遍历 {len(updated_dart_files)} 个Dart文件")
    updated_count = update_file_references(updated_dart_files, loaded_mapping)
    print(f"总共更新了 {updated_count} 个文件的引用")


if __name__ == '__main__':
    rename_dart_file()

