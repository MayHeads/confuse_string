# 替换所有_pkm结尾的字符串 这个是针对Flutter项目的
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from config import STRING_SUFFIX
from ios_string_generate.string_gen import get_random_class_name, get_random_method_name, init_word_lists

def collect_suffix_strings(dart_files):
    """收集所有以指定后缀结尾的字符串"""
    suffix_strings = set()
    for file_path in dart_files:
        try:
            # 尝试不同的编码方式读取文件
            encodings = ['utf-8', 'utf-16', 'ascii', 'latin1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print(f"无法读取文件 {file_path}，尝试所有编码方式都失败")
                continue
                
            # 使用正则表达式匹配以指定后缀结尾的字符串
            pattern = r'\b\w+' + re.escape(STRING_SUFFIX) + r'\b'
            matches = re.findall(pattern, content)
            suffix_strings.update(matches)
            if matches:
                print(f"从文件 {file_path} 中找到 {len(matches)} 个匹配字符串")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    return suffix_strings

def write_strings_to_file(strings, file_path):
    """将字符串写入文件，每行一个"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for string in sorted(strings):
                f.write(f"{string}\n")
        print(f"成功写入 {len(strings)} 个字符串到文件 {file_path}")
    except Exception as e:
        print(f"写入文件 {file_path} 时出错: {str(e)}")

def replace_strings_in_files(file_list, replace_map):
    """替换文件中的字符串"""
    replaced_count = 0
    for file_path in file_list:
        try:
            # 尝试不同的编码方式读取文件
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
                print(f"无法读取文件 {file_path}，尝试所有编码方式都失败")
                continue
            
            # 替换所有匹配的字符串
            modified = False
            for old_str, new_str in replace_map.items():
                # 使用单词边界确保精确匹配
                new_content = re.sub(r'\b' + re.escape(old_str) + r'\b', new_str, content)
                if new_content != content:
                    modified = True
                    content = new_content
            
            if modified:
                # 使用相同的编码方式写回文件
                with open(file_path, 'w', encoding=used_encoding) as f:
                    f.write(content)
                replaced_count += 1
                print(f"成功更新文件 {file_path}")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    return replaced_count

def write_replace_log(replace_map, log_file):
    """写入替换日志"""
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("👉👉👉👉👉Flutter String Replace Map List👈👈👈👈👈\n\n\n")
            for old_str, new_str in sorted(replace_map.items()):
                f.write(f"{old_str} <-----------> {new_str}\n")
        print(f"成功写入替换日志到文件 {log_file}")
    except Exception as e:
        print(f"写入日志文件 {log_file} 时出错: {str(e)}")

def get_all_files_except_path(project_path, exclude_path):
    """获取项目路径下所有文件，但排除指定路径"""
    all_files = []
    
    if not exclude_path:
        # 如果没有排除路径，返回所有文件
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        return all_files
    
    # 标准化路径以便比较
    project_path_normalized = os.path.normpath(os.path.abspath(project_path))
    exclude_path_normalized = os.path.normpath(os.path.abspath(exclude_path))
    
    for root, dirs, files in os.walk(project_path):
        root_normalized = os.path.normpath(os.path.abspath(root))
        
        # 如果当前目录在排除路径内，跳过整个目录树
        if root_normalized.startswith(exclude_path_normalized):
            # 清空dirs列表，跳过所有子目录
            dirs[:] = []
            continue
        
        # 过滤掉会进入排除路径的目录
        dirs[:] = [d for d in dirs if not 
                   os.path.normpath(os.path.abspath(os.path.join(root, d))).startswith(exclude_path_normalized)]
        
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    
    return all_files

def find_matching_files(all_files, replace_map):
    """在所有文件中查找包含替换映射中旧字符串的文件"""
    matching_files = []
    
    for file_path in all_files:
        try:
            # 只处理文本文件（Swift, Dart, Objective-C等）
            if not any(file_path.endswith(ext) for ext in ['.swift', '.dart', '.m', '.h', '.mm', '.cpp', '.c']):
                continue
            
            encodings = ['utf-8', 'utf-16', 'ascii', 'latin1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            if content is None:
                continue
            
            # 检查文件中是否包含任何需要替换的字符串
            for old_str in replace_map.keys():
                if re.search(r'\b' + re.escape(old_str) + r'\b', content):
                    matching_files.append(file_path)
                    break
                    
        except Exception as e:
            # 忽略无法读取的文件
            continue
    
    return matching_files

def main_replace_fix_form_flutter():
    """主函数：处理Flutter项目的字符串替换"""
    project_info = get_project_info()
    if not project_info:
        print("无法获取项目信息，程序退出")
        sys.exit(1)
    
    project_path = project_info.project_path
    flutter_plugin_path = project_info.flutter_plugin_path
    flutter_plugin_dart_files = project_info.flutter_plugin_dart_files
    
    print(f"开始处理Flutter项目: {project_path}")
    
    # 检查是否有flutter_plugin_path
    if not flutter_plugin_path or not flutter_plugin_dart_files:
        print("未找到flutter_plugin_path或dart文件，跳过Flutter处理")
        # 创建空日志文件
        log_file = os.path.join(os.getcwd(), 'ios_log', 'replace_fix_form_flutter.txt')
        write_replace_log({}, log_file)
        return
    
    print(f"找到Flutter Plugin路径: {flutter_plugin_path}")
    print(f"找到 {len(flutter_plugin_dart_files)} 个Dart文件")
    
    # 初始化词库
    if not init_word_lists():
        print("初始化词库失败，程序退出")
        sys.exit(1)
    
    # 步骤1: 收集flutter_plugin_path中所有dart文件里以指定后缀结尾的字符串
    print("\n=== 步骤1: 收集Flutter Plugin中的字符串 ===")
    suffix_strings = collect_suffix_strings(flutter_plugin_dart_files)
    print(f"收集到 {len(suffix_strings)} 个需要替换的字符串")
    
    if not suffix_strings:
        print("未找到需要替换的字符串，创建空日志文件")
        log_file = os.path.join(os.getcwd(), 'ios_log', 'replace_fix_form_flutter.txt')
        write_replace_log({}, log_file)
        return
    
    # 步骤2: 写入到ios_replace_str_flutter.txt
    replace_str_file = os.path.join(os.getcwd(), 'ios_resource', 'ios_replace_str_flutter.txt')
    write_strings_to_file(suffix_strings, replace_str_file)
    
    # 步骤3: 创建替换映射
    print("\n=== 步骤2: 创建替换映射 ===")
    replace_map = {}
    for string in suffix_strings:
        # 根据首字母大小写选择替换方法
        if string[0].isupper():
            new_str = get_random_class_name()
        else:
            new_str = get_random_method_name()
            
        if new_str is None:
            print(f"警告: 无法为 {string} 生成替换名称")
            continue
            
        replace_map[string] = new_str
        print(f"替换映射: {string} -> {new_str}")
    
    if not replace_map:
        print("没有成功生成任何替换名称，创建空日志文件")
        log_file = os.path.join(os.getcwd(), 'ios_log', 'replace_fix_form_flutter.txt')
        write_replace_log({}, log_file)
        return
    
    # 步骤4: 替换flutter_plugin_path中的所有dart文件
    print("\n=== 步骤3: 替换Flutter Plugin中的Dart文件 ===")
    replaced_count = replace_strings_in_files(flutter_plugin_dart_files, replace_map)
    print(f"成功替换了 {replaced_count} 个Dart文件")
    
    # 步骤5: 写入替换日志
    print("\n=== 步骤4: 写入替换日志 ===")
    log_file = os.path.join(os.getcwd(), 'ios_log', 'replace_fix_form_flutter.txt')
    write_replace_log(replace_map, log_file)
    
    # 步骤6: 遍历project_path（排除flutter_plugin_path），找到所有匹配映射的文件并替换
    print("\n=== 步骤5: 替换项目其他文件中的匹配字符串 ===")
    all_files = get_all_files_except_path(project_path, flutter_plugin_path)
    print(f"扫描到 {len(all_files)} 个文件（已排除flutter_plugin_path）")
    
    # 查找包含替换映射中旧字符串的文件
    matching_files = find_matching_files(all_files, replace_map)
    print(f"找到 {len(matching_files)} 个包含匹配字符串的文件")
    
    if matching_files:
        replaced_count = replace_strings_in_files(matching_files, replace_map)
        print(f"成功替换了 {replaced_count} 个项目文件")
    else:
        print("未找到需要替换的项目文件")
    
    print(f"\n处理完成！共处理 {len(replace_map)} 个字符串映射。")
    print(f"Flutter Plugin文件: {len(flutter_plugin_dart_files)} 个")
    print(f"项目其他文件: {len(matching_files)} 个")

if __name__ == '__main__':
    main_replace_fix_form_flutter()

