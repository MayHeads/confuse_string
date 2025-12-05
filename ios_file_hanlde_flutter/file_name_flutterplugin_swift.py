# 重命名文件名
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from ios_string_generate.string_gen import get_random_class_name, init_word_lists

from config import REPLACE_IGNORE_FILE_NAMES
# 更改.swift、.h、.m 文件名 【fluttersdkplugin中的目录结构】
# 需要忽略的文件名列表
IGNORE_FILE_NAMES = REPLACE_IGNORE_FILE_NAMES

def collect_ios_files(flutter_plugin_path):
    """从flutter_plugin_path收集所有以_pkm结尾的.swift、.h、.m文件"""
    ios_files = []
    
    if not flutter_plugin_path or not os.path.exists(flutter_plugin_path):
        return ios_files
    
    # 支持的文件扩展名
    supported_extensions = ['.swift', '.h', '.m']
    # 文件名必须以_pkm结尾
    STRING_SUFFIX = '_pkm'
    
    for root, dirs, files in os.walk(flutter_plugin_path):
        for file in files:
            file_path = os.path.join(root, file)
            # 获取文件名（不含扩展名）和扩展名
            file_name_without_ext, ext = os.path.splitext(file)
            
            # 检查文件扩展名和是否以_pkm结尾
            if ext in supported_extensions and file_name_without_ext.endswith(STRING_SUFFIX):
                ios_files.append(file_path)
    
    return ios_files

def rename_ios_files(ios_files):
    """重命名iOS文件（.swift、.h、.m，仅处理以_pkm结尾的文件）并记录映射关系
    注意：.h 和 .m 文件是成对出现的，会改成相同的名字
    """
    # 初始化词库
    init_word_lists()
    
    # 存储文件名映射关系
    name_mapping = {}
    
    # 创建日志目录
    log_dir = os.path.join(os.getcwd(), 'ios_log')
    os.makedirs(log_dir, exist_ok=True)
    
    STRING_SUFFIX = '_pkm'
    
    # 按文件名（不含扩展名）分组文件，以便识别成对的 .h 和 .m 文件
    file_groups = {}
    for file_path in ios_files:
        file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]
        file_ext = os.path.splitext(file_path)[1]
        
        # 检查是否在忽略列表中
        if file_name_without_ext in IGNORE_FILE_NAMES:
            print(f"忽略文件: {file_name_without_ext}")
            continue
        
        # 再次确认文件以_pkm结尾（双重检查）
        if not file_name_without_ext.endswith(STRING_SUFFIX):
            print(f"文件 {file_name_without_ext} 不以 {STRING_SUFFIX} 结尾，跳过")
            continue
        
        # 按文件名分组
        if file_name_without_ext not in file_groups:
            file_groups[file_name_without_ext] = {}
        file_groups[file_name_without_ext][file_ext] = file_path
    
    # 处理每个文件组
    for file_name_without_ext, ext_dict in file_groups.items():
        # 生成新的文件名（对于成对的 .h 和 .m，使用相同的新名字）
        new_name = get_random_class_name()
        if new_name is None:
            print(f"无法为文件 {file_name_without_ext} 生成新名称")
            continue
        
        # 处理该组中的所有文件
        for file_ext, file_path in ext_dict.items():
            dir_path = os.path.dirname(file_path)
            new_file_path = os.path.join(dir_path, f"{new_name}{file_ext}")
            
            try:
                # 重命名文件
                os.rename(file_path, new_file_path)
                # 对于成对的 .h 和 .m 文件，使用相同的映射关系
                if file_name_without_ext not in name_mapping:
                    name_mapping[file_name_without_ext] = new_name
                print(f"重命名文件: {file_name_without_ext}{file_ext} -> {new_name}{file_ext}")
            except Exception as e:
                print(f"重命名文件 {file_name_without_ext}{file_ext} 时出错: {str(e)}")
    
    # 写入映射关系到日志文件
    log_file = os.path.join(log_dir, 'file_name_flutterplugin_swift.txt')
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("👉👉👉👉👉Flutter Plugin iOS File Name Mapping List (Only _pkm files)👈👈👈👈👈\n\n\n")
            f.write("注意：.h 和 .m 文件是成对出现的，使用相同的新名字\n\n")
            for old_name, new_name in name_mapping.items():
                f.write(f"{old_name} -> {new_name}\n")
        print(f"文件名映射关系已写入: {log_file}")
    except Exception as e:
        print(f"写入映射关系时出错: {str(e)}")
    
    return name_mapping

def load_name_mapping_from_log(log_file):
    """从映射日志文件中加载文件名映射关系"""
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
    except Exception as e:
        print(f"读取映射日志文件时出错: {str(e)}")
    
    return name_mapping

def replace_in_project_files(project_path, name_mapping):
    """在project_path中递归遍历所有文件内容，精准替换映射关系
    遍历所有文件（不限制文件类型，只跳过二进制文件），在文件内容中查找并替换所有匹配的旧文件名
    """
    if not name_mapping:
        print("没有映射关系，跳过文件内容替换")
        return
    
    # 忽略的文件夹列表（如果遇到这些目录，就跳过整个目录树，包括所有子目录和文件）
    ignore_folders = ['Framework']
    
    # 二进制文件扩展名列表（跳过这些文件）
    binary_extensions = [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
        '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
        '.xcarchive', '.framework', '.a', '.dylib', '.so',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        '.ttf', '.otf', '.woff', '.woff2',
        '.xcodeproj', '.xcworkspace',  # 这些是目录，但也要注意
    ]
    
    replaced_count = 0
    processed_files = 0
    skipped_files = 0
    
    print(f"开始递归遍历 {project_path} 下的所有文件...")
    
    for root, dirs, files in os.walk(project_path):
        # 检查当前路径是否包含忽略的文件夹
        should_skip_root = False
        for ignore_folder in ignore_folders:
            if ignore_folder in root:
                should_skip_root = True
                break
        
        # 如果当前路径包含忽略的文件夹，跳过整个目录树
        if should_skip_root:
            # 清空dirs列表，不进入任何子目录
            dirs[:] = []
            continue
        
        # 跳过一些不需要处理的目录
        dirs[:] = [d for d in dirs if d not in ['.git', 'build', 'DerivedData', 'Pods', '.dart_tool', 'node_modules', '.idea']]
        
        # 从dirs列表中移除忽略的文件夹，这样就不会进入这些目录
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        for file in files:
            file_path = os.path.join(root, file)
            processed_files += 1
            
            _, ext = os.path.splitext(file)
            
            # 跳过二进制文件
            if ext.lower() in binary_extensions:
                skipped_files += 1
                continue
            
            try:
                # 尝试读取文件（支持多种编码）
                encodings = ['utf-8', 'utf-16', 'ascii', 'latin1', 'gbk', 'gb2312']
                content = None
                used_encoding = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                            content = f.read()
                        used_encoding = encoding
                        break
                    except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                        continue
                
                # 如果无法读取文件内容，跳过
                if content is None:
                    skipped_files += 1
                    continue
                
                # 替换所有匹配的旧文件名（精准字符串替换）
                modified = False
                replacement_details = []
                
                for old_name, new_name in name_mapping.items():
                    # 检查旧文件名是否在内容中
                    if old_name in content:
                        # 统计替换次数
                        count = content.count(old_name)
                        content = content.replace(old_name, new_name)
                        modified = True
                        replacement_details.append(f"{old_name} -> {new_name} (替换 {count} 次)")
                
                if modified:
                    # 写回文件
                    try:
                        with open(file_path, 'w', encoding=used_encoding, errors='ignore') as f:
                            f.write(content)
                        replaced_count += 1
                        print(f"✓ 已更新文件: {file_path}")
                        for detail in replacement_details:
                            print(f"    {detail}")
                    except Exception as e:
                        print(f"✗ 写入文件 {file_path} 时出错: {str(e)}")
                        
            except Exception as e:
                skipped_files += 1
                # 不打印每个文件的错误，避免输出过多
                if processed_files % 100 == 0:
                    print(f"处理进度: 已处理 {processed_files} 个文件，跳过 {skipped_files} 个文件")
    
    print(f"\n替换完成统计:")
    print(f"  总共处理文件: {processed_files} 个")
    print(f"  跳过文件: {skipped_files} 个")
    print(f"  更新文件: {replaced_count} 个")

def rename_swift_file_flutterplugin_swift():
    """重命名Flutter Plugin中的iOS文件（.swift、.h、.m，仅处理以_pkm结尾的文件）"""
    project_info = get_project_info()
    if not project_info:
        print("无法获取项目信息，程序退出")
        return
    
    # 项目目录路径
    project_path = project_info.project_path
    
    # flutter_plugin_path 目录路径
    flutter_plugin_path = project_info.flutter_plugin_path
    
    # 检查是否有flutter_plugin_path
    if not flutter_plugin_path:
        print("未找到flutter_plugin_path，跳过iOS文件重命名")
        return
    
    print(f"开始处理Flutter Plugin中的iOS文件（仅处理以_pkm结尾的文件）...")
    print(f"Flutter Plugin路径: {flutter_plugin_path}")
    print(f"项目路径: {project_path}")
    
    # 步骤1: 从flutter_plugin_path收集所有以_pkm结尾的.swift、.h、.m文件
    print(f"\n=== 步骤1: 收集以_pkm结尾的iOS文件 ===")
    ios_files = collect_ios_files(flutter_plugin_path)
    print(f"找到 {len(ios_files)} 个以_pkm结尾的iOS文件（.swift、.h、.m）")
    
    if not ios_files:
        print("未找到符合条件的iOS文件，跳过重命名")
        return
    
    # 步骤2: 重命名文件并生成映射关系
    print(f"\n=== 步骤2: 重命名iOS文件 ===")
    name_mapping = rename_ios_files(ios_files)
    print(f"总共重命名了 {len(name_mapping)} 个文件")
    
    if not name_mapping:
        print("没有文件需要重命名，跳过文件内容替换")
        return
    
    # 步骤3: 重新获取project_path（重新扫描项目，包含刚才重命名后的文件）
    print(f"\n=== 步骤3: 重新扫描项目路径 ===")
    print(f"重新扫描项目以获取最新的 project_path（包含重命名后的文件）")
    
    # 重新获取项目信息
    re_scanned_project_info = get_project_info()
    if re_scanned_project_info:
        updated_project_path = re_scanned_project_info.project_path
        print(f"重新扫描后的项目路径: {updated_project_path}")
    else:
        print("重新扫描失败，使用原始项目路径")
        updated_project_path = project_path
    
    # 从映射日志文件中加载映射关系
    log_file = os.path.join(os.getcwd(), 'ios_log', 'file_name_flutterplugin_swift.txt')
    print(f"映射日志文件: {log_file}")
    loaded_mapping = load_name_mapping_from_log(log_file)
    
    if not loaded_mapping:
        print("无法从日志文件加载映射关系，使用内存中的映射")
        loaded_mapping = name_mapping
    
    print(f"\n加载了 {len(loaded_mapping)} 个映射关系:")
    for old_name, new_name in loaded_mapping.items():
        print(f"  {old_name} -> {new_name}")
    
    # 步骤4: 在project_path中递归遍历所有文件内容，精准替换映射关系
    print(f"\n=== 步骤4: 替换项目文件中的引用 ===")
    print(f"将递归遍历 {updated_project_path} 中的所有文件内容（不限制文件类型）")
    print(f"查找并替换所有匹配的旧文件名（xxxx_pkm -> new_name）")
    replace_in_project_files(updated_project_path, loaded_mapping)
    
    print(f"\n处理完成！")


if __name__ == '__main__':
    rename_swift_file_flutterplugin_swift()