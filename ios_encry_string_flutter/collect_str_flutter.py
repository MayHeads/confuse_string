# 收集所有 Flutter Dart 文件中的静态字符串
# 1. 收集所有 Dart 文件中的静态字符串（单引号和双引号包裹，不包含特殊符号）
# 2. 保存到 ios_resource/ios_collection_str_flutter.txt 文件中

import os
import sys
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Set, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info

# 忽略规则列表
IGNORE_RULES = [
    r'^\s*$',  # 空字符串
    r'^-+$',   # 只包含连字符的字符串
    r'^[-\s]+$',  # 只包含连字符和空格的字符串
]

def should_ignore_string(s: str) -> bool:
    """
    检查字符串是否应该被忽略
    """
    # 检查是否匹配任何忽略规则
    for rule in IGNORE_RULES:
        if re.match(rule, s):
            return True
    return False

def is_static_string(s: str) -> bool:
    """
    检查字符串是否是静态字符串（不包含特殊符号）
    特殊符号包括：$、\、{}、()等
    """
    # 检查是否包含特殊符号
    special_chars = ['$', '\\', '{', '}', '(', ')', '%']
    for char in special_chars:
        if char in s:
            return False
    
    # 检查是否包含字符串插值（Flutter中的 ${} 或 $variable）
    if re.search(r'\$\{|\$[a-zA-Z_]', s):
        return False
    
    # 检查是否包含转义序列（除了基本的 \n, \t, \r）
    # 允许基本的转义序列，但不允许其他转义
    if re.search(r'\\(?!n|t|r|"|\')', s):
        return False
    
    return True

def is_import_export_statement_string(content: str, match_start: int, match_end: int) -> bool:
    """
    检查字符串是否在import或export语句中
    只要字符串前面是import或export，就不进行混淆
    例如: 
    - import 'package:ttfluttersdk_plugin/ttfluttersdk_plugin.dart';
    - export 'src/network/obs_net_manager.dart';
    - import 'some_path';
    - export "another_path";
    """
    # 获取匹配位置前200个字符（足够包含import/export语句）
    context_start = max(0, match_start - 200)
    context = content[context_start:match_end]
    
    # 检查是否在import或export语句中
    # 匹配 import '...' 或 import "..." 格式
    # 匹配 export '...' 或 export "..." 格式
    # 允许前后有空格、注释等
    import_export_pattern = r'(?:import|export)\s+[\'"][^\'"]*[\'"]'
    
    # 查找所有import/export语句
    for match in re.finditer(import_export_pattern, context, re.IGNORECASE):
        # 计算在原始内容中的位置
        statement_start = context_start + match.start()
        statement_end = context_start + match.end()
        
        # 检查当前字符串是否在import/export语句的范围内
        if statement_start <= match_start and match_end <= statement_end:
            return True
    
    return False

def is_static_string_declaration(content: str, match_start: int, match_end: int) -> bool:
    """
    检查字符串所在行是否包含 const 或 static String 相关声明
    规则：
    1. 如果行中包含 const，忽略该行的所有字符串
    2. 如果行中包含 static String，忽略该行的所有字符串
    例如:
    - static String name = 'test';
    - static const String version = "1.0.0";
    - const String path = 'some/path';
    - const apiKey = 'abc123';
    - final const value = 'test';
    """
    # 找到字符串所在行的开始位置
    line_start = content.rfind('\n', 0, match_start)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1  # 跳过换行符
    
    # 找到字符串所在行的结束位置
    line_end = content.find('\n', match_end)
    if line_end == -1:
        line_end = len(content)
    
    # 获取整行内容
    line_content = content[line_start:line_end]
    
    # 规则1: 如果行中包含 const，忽略该行的所有字符串
    # 使用单词边界确保匹配完整的 const 关键字
    if re.search(r'\bconst\b', line_content, re.IGNORECASE):
        return True
    
    # 规则2: 检查是否包含 static String（不区分大小写）
    static_pattern = r'static\s+String'
    if re.search(static_pattern, line_content, re.IGNORECASE):
        return True
    
    return False

def extract_strings_from_content(content: str) -> Set[str]:
    """
    从内容中提取所有静态字符串（单引号和双引号）
    排除import和export语句中的路径字符串
    """
    strings = set()
    
    # 匹配单引号字符串 '...'
    single_quote_pattern = r"(?<!\\)'(?:[^'\\]|\\.)*'"
    
    # 匹配双引号字符串 "..."
    double_quote_pattern = r'(?<!\\)"(?:[^"\\]|\\.)*"'
    
    def process_string(match, quote_type: str):
        match_start = match.start()
        match_end = match.end()
        
        # 检查是否在import或export语句中
        if is_import_export_statement_string(content, match_start, match_end):
            return  # 跳过import/export语句中的路径字符串
        
        # 检查是否在static String或static const String声明中
        if is_static_string_declaration(content, match_start, match_end):
            return  # 跳过static String声明中的字符串
        
        s = match.group(0)
        # 移除引号
        s = s[1:-1]
        
        # 处理基本转义字符
        s = s.replace("\\'", "'")
        s = s.replace('\\"', '"')
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        s = s.replace('\\r', '\r')
        s = s.replace('\\\\', '\\')
        
        # 检查是否是静态字符串
        if is_static_string(s) and not should_ignore_string(s):
            strings.add(s)
    
    # 处理所有匹配的单引号字符串
    for match in re.finditer(single_quote_pattern, content):
        process_string(match, 'single')
    
    # 处理所有匹配的双引号字符串
    for match in re.finditer(double_quote_pattern, content):
        process_string(match, 'double')
    
    return strings

def extract_strings_from_file(file_path: str) -> Set[str]:
    """
    从单个文件中提取字符串
    """
    try:
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
            print(f"无法读取文件 {file_path}，尝试所有编码方式都失败")
            return set()
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return set()

    # 移除多行字符串（Flutter中的三引号字符串）
    content = re.sub(r"'''(?:[^']|'[^']|''[^'])*'''", '', content)
    content = re.sub(r'"""(?:[^"]|"[^"]|""[^"])*"""', '', content)
    
    return extract_strings_from_content(content)

def collect_strings(dart_files: List[str]) -> Set[str]:
    """
    并行收集所有Dart文件中的字符串
    """
    all_strings = set()
    
    if not dart_files:
        print("没有找到Dart文件")
        return all_strings
    
    # 使用线程池并行处理文件
    with ThreadPoolExecutor() as executor:
        # 提交所有文件处理任务
        future_to_file = {executor.submit(extract_strings_from_file, file): file 
                         for file in dart_files}
        
        # 收集结果
        for future in future_to_file:
            try:
                strings = future.result()
                all_strings.update(strings)
            except Exception as e:
                file = future_to_file[future]
                print(f"处理文件 {file} 时出错: {e}")
    
    return all_strings

def save_strings_to_file(strings: Set[str], output_file: str):
    """
    将收集到的字符串保存到文件
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 按字母顺序排序并写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for s in sorted(strings):
            # 确保字符串是有效的UTF-8编码
            try:
                s.encode('utf-8')
                if s:
                    f.write(f"{s}\n")
            except UnicodeEncodeError:
                print(f"警告: 跳过无效UTF-8编码的字符串: {s}")

def main_collect_str_flutter():
    """主函数：收集Flutter项目中的静态字符串"""
    # 获取项目信息
    project_info = get_project_info()
    if not project_info:
        print("无法获取项目信息，程序退出")
        return
    
    flutter_plugin_path = project_info.flutter_plugin_path
    flutter_plugin_dart_files = project_info.flutter_plugin_dart_files
    
    # 检查是否有flutter_plugin_path
    if not flutter_plugin_path or not flutter_plugin_dart_files:
        print("未找到flutter_plugin_path或dart文件，跳过Flutter字符串收集")
        # 创建空文件
        output_file = "ios_resource/ios_collection_str_flutter.txt"
        save_strings_to_file(set(), output_file)
        return
    
    print(f"开始收集Flutter Plugin中的字符串: {flutter_plugin_path}")
    print(f"找到 {len(flutter_plugin_dart_files)} 个Dart文件")
    
    # 收集字符串
    print("正在收集Dart文件中的静态字符串...")
    strings = collect_strings(flutter_plugin_dart_files)
    
    # 保存到文件
    output_file = "ios_resource/ios_collection_str_flutter.txt"
    save_strings_to_file(strings, output_file)
    
    print(f"收集到 {len(strings)} 个唯一的静态字符串")
    print(f"结果已保存到 {output_file}")

if __name__ == "__main__":
    main_collect_str_flutter()

