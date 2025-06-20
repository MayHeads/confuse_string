# 替换所有_ckm结尾的字符串
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from config import STRING_SUFFIX
from ios_string_generate.string_gen import get_random_class_name, get_random_method_name, init_word_lists

# 目前用的ckm
def collect_ckm_strings(swift_files):
    """收集所有以指定后缀结尾的字符串"""
    ckm_strings = set()
    for file_path in swift_files:
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
            ckm_strings.update(matches)
            print(f"从文件 {file_path} 中找到 {len(matches)} 个匹配字符串")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    return ckm_strings

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

def replace_strings_in_files(swift_files, replace_map):
    """替换文件中的字符串"""
    for file_path in swift_files:
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
            
            # 替换所有匹配的字符串
            modified = False
            for old_str, new_str in replace_map.items():
                new_content = re.sub(r'\b' + re.escape(old_str) + r'\b', new_str, content)
                if new_content != content:
                    modified = True
                    content = new_content
            
            if modified:
                # 使用相同的编码方式写回文件
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
                print(f"成功更新文件 {file_path}")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")

def write_replace_log(replace_map, log_file):
    """写入替换日志"""
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("👉👉👉👉👉String Replace Map List👈👈👈👈👈\n\n\n")
            for old_str, new_str in replace_map.items():
                f.write(f"{old_str} <-----------> {new_str}\n")
        print(f"成功写入替换日志到文件 {log_file}")
    except Exception as e:
        print(f"写入日志文件 {log_file} 时出错: {str(e)}")

def main_replace_fix_form():
    project_info = get_project_info()
    project_path = project_info.project_path
    target_name = project_info.target_name
    swift_all_files = project_info.all_swift_files
    
    print(f"开始处理项目: {project_path}")
    print(f"找到 {len(swift_all_files)} 个Swift文件")
    
    # 初始化词库
    if not init_word_lists():
        print("初始化词库失败，程序退出")
        sys.exit(1)
    
    # 1. 收集所有_ckm结尾的字符串
    ckm_strings = collect_ckm_strings(swift_all_files)
    print(f"收集到 {len(ckm_strings)} 个需要替换的字符串")
    
    # if not ckm_strings:
    #     print("未找到需要替换的字符串，程序继续执行")
    #     # 创建空文件
    #     replace_str_file = os.path.join(os.getcwd(), 'ios_resource', 'ios_replace_str.txt')
    #     write_strings_to_file(set(), replace_str_file)
        
    #     log_file = os.path.join(os.getcwd(), 'ios_log', 'replace_fix_form.txt')
    #     write_replace_log({}, log_file)
    #     return
    
    # 2. 写入到ios_replace_str.txt
    replace_str_file = os.path.join(os.getcwd(), 'ios_resource', 'ios_replace_str.txt')
    write_strings_to_file(ckm_strings, replace_str_file)
    
    # 3. 创建替换映射
    replace_map = {}
    for string in ckm_strings:
        # 4. 根据首字母大小写选择替换方法
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
        print("没有成功生成任何替换名称，程序继续执行")
        # 创建空日志文件
        log_file = os.path.join(os.getcwd(), 'ios_log', 'replace_fix_form.txt')
        write_replace_log({}, log_file)
        return
    
    # 5. 替换文件中的字符串
    replace_strings_in_files(swift_all_files, replace_map)
    
    # 6. 写入替换日志
    log_file = os.path.join(os.getcwd(), 'ios_log', 'replace_fix_form.txt')
    write_replace_log(replace_map, log_file)
    
    print(f"处理完成！共处理 {len(replace_map)} 个字符串。")

if __name__=='__main__':
    main_replace_fix_form()
    
    
    
    


