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

def extract_strings_from_content(content: str) -> Set[str]:
    """
    从内容中提取所有字符串
    """
    strings = set()
    
    # 匹配所有字符串字面量，包括字符串插值中的字符串
    pattern = r'(?<!\\)"(?:[^"\\]|\\.)*"'
    
    def process_string(s: str):
        # 移除引号
        s = s[1:-1]
        
        # 处理转义字符
        s = s.replace('\\"', '"')
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        s = s.replace('\\\\', '\\')
        
        # 提取字符串插值中的字符串
        # 匹配形如 \(xc)https\("1234tdcaciton") 中的 "1234tdcaciton"
        interpolation_pattern = r'\\\([^)]*\\"([^"]*)\\"[^)]*\)'
        for match in re.finditer(interpolation_pattern, s):
            inner_str = match.group(1)
            if not should_ignore_string(inner_str):
                strings.add(inner_str)
        
        # 如果字符串本身不是空的且不包含字符串插值，也添加它
        if not should_ignore_string(s) and '\\(' not in s:
            strings.add(s)
    
    # 处理所有匹配的字符串
    for match in re.finditer(pattern, content):
        process_string(match.group(0))
    
    # 过滤掉无效的字符串
    strings = {s for s in strings if s and not any(c in s for c in '(),')}
    
    return strings

def extract_strings_from_file(file_path: str) -> Set[str]:
    """
    从单个文件中提取字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return set()

    # 移除多行字符串
    content = re.sub(r'"""(?:[^"]|"[^"]|""[^"])*"""', '', content)
    
    return extract_strings_from_content(content)

def collect_strings(swift_files: List[str]) -> Set[str]:
    """
    并行收集所有Swift文件中的字符串
    """
    all_strings = set()
    
    # 使用线程池并行处理文件
    with ThreadPoolExecutor() as executor:
        # 提交所有文件处理任务
        future_to_file = {executor.submit(extract_strings_from_file, file): file 
                         for file in swift_files}
        
        # 收集结果
        for future in future_to_file:
            try:
                strings = future.result()
                all_strings.update(strings)
            except Exception as e:
                file = future_to_file[future]
                print(f"Error processing file {file}: {e}")
    
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
            # 确保字符串是有效的UTF-8编码且不包含无效字符
            try:
                s.encode('utf-8')
                if s and not any(c in s for c in '(),'):
                    f.write(f"{s}\n")
            except UnicodeEncodeError:
                print(f"Warning: Skipping string with invalid UTF-8 encoding: {s}")

def main():
    # 获取项目信息
    project_info = get_project_info()
    
    # 获取所有Swift文件
    swift_files = project_info.swift_files
    print("Processing files:", swift_files)
    
    # 收集字符串
    print("Collecting strings from Swift files...")
    strings = collect_strings(swift_files)
    
    # 保存到文件
    output_file = "ios_resource/ios_collection_str.txt"
    save_strings_to_file(strings, output_file)
    
    print(f"Collected {len(strings)} unique strings")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()