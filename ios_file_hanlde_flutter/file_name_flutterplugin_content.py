# 替换文件内容的pkm 不能影响文件名的替换

import os
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from config import STRING_SUFFIX
from ios_string_generate.string_gen import get_random_class_name, get_random_method_name, init_word_lists

def collect_pkm_strings(flutter_plugin_path):
    """从flutter_plugin_path收集所有以_pkm结尾的字符串（在.swift、.h、.m文件中）"""
    pkm_strings = set()
    
    if not flutter_plugin_path or not os.path.exists(flutter_plugin_path):
        return pkm_strings
    
    # 支持的文件扩展名
    supported_extensions = ['.swift', '.h', '.m']
    
    for root, dirs, files in os.walk(flutter_plugin_path):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            # 只处理支持的文件类型
            if ext not in supported_extensions:
                continue
            
            try:
                # 尝试不同的编码方式读取文件
                encodings = ['utf-8', 'utf-16', 'ascii', 'latin1', 'gbk', 'gb2312']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                            content = f.read()
                        break
                    except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                        continue
                
                if content is None:
                    print(f"无法读取文件 {file_path}，尝试所有编码方式都失败")
                    continue
                
                # 使用正则表达式匹配以_pkm结尾的字符串（单词边界）
                pattern = r'\b\w+' + re.escape(STRING_SUFFIX) + r'\b'
                
                # 按行处理，忽略包含import或#import的行
                lines = content.split('\n')
                file_matches = set()
                
                for line_num, line in enumerate(lines, 1):
                    # 如果行包含 #import 或 import，跳过该行（不区分大小写）
                    # 这样可以匹配：#import "xxx.h" 或 import xxx 格式
                    line_lower = line.lower()
                    if '#import' in line_lower or 'import' in line_lower:
                        continue
                    
                    # 在该行中查找匹配的字符串
                    matches = re.findall(pattern, line)
                    if matches:
                        file_matches.update(matches)
                
                if file_matches:
                    pkm_strings.update(file_matches)
                    print(f"从文件 {file_path} 中找到 {len(file_matches)} 个匹配字符串（已忽略import行）")
                    
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    return pkm_strings

def create_replace_mapping(pkm_strings):
    """创建替换映射关系，根据首字母大小写选择类名或方法名"""
    replace_map = {}
    
    # 初始化词库
    if not init_word_lists():
        print("初始化词库失败，无法生成替换名称")
        return replace_map
    
    for string in pkm_strings:
        # 根据首字母大小写选择替换方法
        if string[0].isupper():
            # 首字母大写，使用类名生成器
            new_str = get_random_class_name()
        else:
            # 首字母小写，使用方法名生成器
            new_str = get_random_method_name()
        
        if new_str is None:
            print(f"警告: 无法为 {string} 生成替换名称")
            continue
        
        replace_map[string] = new_str
        print(f"替换映射: {string} -> {new_str}")
    
    return replace_map

def replace_strings_in_flutter_plugin_files(flutter_plugin_path, replace_map):
    """在flutter_plugin_path中的文件里替换_pkm相关字符串"""
    if not replace_map:
        print("没有映射关系，跳过文件内容替换")
        return
    
    if not flutter_plugin_path or not os.path.exists(flutter_plugin_path):
        print("flutter_plugin_path不存在，跳过文件内容替换")
        return
    
    # 支持的文件扩展名
    supported_extensions = ['.swift', '.h', '.m']
    
    replaced_count = 0
    processed_files = 0
    
    print(f"开始替换 {flutter_plugin_path} 中的文件内容...")
    
    for root, dirs, files in os.walk(flutter_plugin_path):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            # 只处理支持的文件类型
            if ext not in supported_extensions:
                continue
            
            processed_files += 1
            
            try:
                # 尝试不同的编码方式读取文件
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
                
                if content is None:
                    continue
                
                # 按行处理，忽略包含 #import 或 import 的行
                lines = content.split('\n')
                modified = False
                replacement_details = []
                new_lines = []
                
                for line in lines:
                    line_lower = line.lower()
                    # 如果行包含 #import 或 import，保持原样不替换
                    if '#import' in line_lower or 'import' in line_lower:
                        new_lines.append(line)
                        continue
                    
                    # 对该行进行替换
                    modified_line = line
                    for old_str, new_str in replace_map.items():
                        # 使用单词边界进行精准替换
                        pattern = r'\b' + re.escape(old_str) + r'\b'
                        new_line = re.sub(pattern, new_str, modified_line)
                        if new_line != modified_line:
                            count = len(re.findall(pattern, modified_line))
                            modified_line = new_line
                            modified = True
                            replacement_details.append(f"{old_str} -> {new_str} (替换 {count} 次)")
                    
                    new_lines.append(modified_line)
                
                # 如果修改过，重新组合内容
                if modified:
                    content = '\n'.join(new_lines)
                
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
                print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    print(f"\n替换完成统计:")
    print(f"  总共处理文件: {processed_files} 个")
    print(f"  更新文件: {replaced_count} 个")

def write_replace_log(replace_map, log_file):
    """将替换映射关系写入日志文件"""
    try:
        # 确保目录存在
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("👉👉👉👉👉Flutter Plugin Content Replace Map List (Only _pkm strings)👈👈👈👈👈\n\n\n")
            for old_str, new_str in sorted(replace_map.items()):
                f.write(f"{old_str} <-----------> {new_str}\n")
        print(f"替换映射关系已写入: {log_file}")
    except Exception as e:
        print(f"写入日志文件 {log_file} 时出错: {str(e)}")

def load_replace_mapping_from_log(log_file):
    """从映射日志文件中加载文件内容映射关系"""
    replace_map = {}
    
    if not os.path.exists(log_file):
        print(f"映射日志文件不存在: {log_file}")
        return replace_map
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和标题行
                if not line or '👉' in line or '👈' in line:
                    continue
                
                # 解析映射关系: old_str <-----------> new_str
                if ' <-----------> ' in line:
                    parts = line.split(' <-----------> ', 1)
                    if len(parts) == 2:
                        old_str = parts[0].strip()
                        new_str = parts[1].strip()
                        if old_str and new_str:
                            replace_map[old_str] = new_str
    except Exception as e:
        print(f"读取映射日志文件时出错: {str(e)}")
    
    return replace_map

def replace_in_project_files(project_path, replace_map):
    """在project_path中递归遍历所有文件内容，精准替换映射关系"""
    if not replace_map:
        print("没有映射关系，跳过文件内容替换")
        return
    
    # 忽略的文件夹列表（如果遇到这些目录，就跳过整个目录树）
    ignore_folders = ['Framework', 'Pods', '.git', 'build', 'DerivedData', '.dart_tool', 'node_modules', '.idea']
    
    # 二进制文件扩展名列表（跳过这些文件）
    binary_extensions = [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
        '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
        '.xcarchive', '.framework', '.a', '.dylib', '.so',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        '.ttf', '.otf', '.woff', '.woff2',
        '.xcodeproj', '.xcworkspace',
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
            dirs[:] = []
            continue
        
        # 从dirs列表中移除忽略的文件夹
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        for file in files:
            file_path = os.path.join(root, file)
            processed_files += 1
            
            _, ext = os.path.splitext(file)
            
            # 跳过二进制文件
            if ext.lower() in binary_extensions:
                skipped_files += 1
                continue
            
            # 跳过.podspec文件和.dart文件
            if ext.lower() == '.podspec' or ext.lower() == '.dart':
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
                
                # 按行处理，忽略包含 #import 或 import 的行
                lines = content.split('\n')
                modified = False
                replacement_details = []
                new_lines = []
                
                for line in lines:
                    line_lower = line.lower()
                    # 如果行包含 #import 或 import，保持原样不替换
                    if '#import' in line_lower or 'import' in line_lower:
                        new_lines.append(line)
                        continue
                    
                    # 对该行进行替换
                    modified_line = line
                    for old_str, new_str in replace_map.items():
                        # 使用单词边界进行精准替换
                        pattern = r'\b' + re.escape(old_str) + r'\b'
                        new_line = re.sub(pattern, new_str, modified_line)
                        if new_line != modified_line:
                            count = len(re.findall(pattern, modified_line))
                            modified_line = new_line
                            modified = True
                            replacement_details.append(f"{old_str} -> {new_str} (替换 {count} 次)")
                    
                    new_lines.append(modified_line)
                
                # 如果修改过，重新组合内容
                if modified:
                    content = '\n'.join(new_lines)
                
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

def replace_pkm_strings_in_flutter_plugin():
    """替换Flutter Plugin中的_pkm相关字符串"""
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
        print("未找到flutter_plugin_path，跳过_pkm字符串替换")
        return
    
    print(f"开始处理Flutter Plugin中的_pkm字符串替换...")
    print(f"Flutter Plugin路径: {flutter_plugin_path}")
    print(f"项目路径: {project_path}")
    
    # 步骤1: 从flutter_plugin_path收集所有以_pkm结尾的字符串
    print(f"\n=== 步骤1: 收集以_pkm结尾的字符串 ===")
    pkm_strings = collect_pkm_strings(flutter_plugin_path)
    print(f"找到 {len(pkm_strings)} 个需要替换的字符串")
    
    if not pkm_strings:
        print("未找到需要替换的字符串，跳过替换")
        # 创建空日志文件
        log_file = os.path.join(os.getcwd(), 'ios_log', 'file_name_flutterplugin_content.txt')
        write_replace_log({}, log_file)
        return
    
    # 步骤2: 创建替换映射关系
    print(f"\n=== 步骤2: 创建替换映射关系 ===")
    replace_map = create_replace_mapping(pkm_strings)
    print(f"总共创建了 {len(replace_map)} 个映射关系")
    
    if not replace_map:
        print("没有成功生成任何替换映射，程序继续执行")
        # 创建空日志文件
        log_file = os.path.join(os.getcwd(), 'ios_log', 'file_name_flutterplugin_content.txt')
        write_replace_log({}, log_file)
        return
    
    # 步骤3: 在flutter_plugin_path中的文件里替换字符串
    print(f"\n=== 步骤3: 替换Flutter Plugin文件中的字符串 ===")
    replace_strings_in_flutter_plugin_files(flutter_plugin_path, replace_map)
    
    # 步骤4: 将映射关系写入日志文件
    print(f"\n=== 步骤4: 写入映射关系到日志文件 ===")
    log_file = os.path.join(os.getcwd(), 'ios_log', 'file_name_flutterplugin_content.txt')
    write_replace_log(replace_map, log_file)
    
    # 步骤5: 从日志文件加载映射关系（用于后续在project_path中替换）
    print(f"\n=== 步骤5: 从日志文件加载映射关系 ===")
    loaded_mapping = load_replace_mapping_from_log(log_file)
    
    if not loaded_mapping:
        print("无法从日志文件加载映射关系，使用内存中的映射")
        loaded_mapping = replace_map
    
    print(f"加载了 {len(loaded_mapping)} 个映射关系:")
    for old_str, new_str in list(loaded_mapping.items())[:10]:  # 只显示前10个
        print(f"  {old_str} -> {new_str}")
    if len(loaded_mapping) > 10:
        print(f"  ... 还有 {len(loaded_mapping) - 10} 个映射关系")
    
    # 步骤6: 在project_path中递归遍历所有文件内容，精准替换映射关系
    print(f"\n=== 步骤6: 替换项目文件中的引用 ===")
    print(f"将递归遍历 {project_path} 中的所有文件内容（不限制文件类型）")
    print(f"查找并替换所有匹配的_pkm字符串")
    replace_in_project_files(project_path, loaded_mapping)
    
    print(f"\n处理完成！")

if __name__ == '__main__':
    replace_pkm_strings_in_flutter_plugin()
