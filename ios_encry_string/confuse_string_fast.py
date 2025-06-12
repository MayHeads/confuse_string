#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import string
import random
import base64
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pbxproj import XcodeProject
import concurrent.futures
import threading
from typing import Dict, List, Tuple, Set
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info

# 配置
# project_path = "/Users/jiangshanchen/confuse_string/ConfuseDemo1/"
# target_name = "ConfuseDemo1"

project_path = ""
target_name = ""

IGNORE_DIRECTORY = [
    "Pods", "DerivedData", "build", ".git", "node_modules", 
    "Carthage", "fastlane", ".bundle" , "CloudWidget", "Products"
]

# 线程锁用于日志输出
print_lock = threading.Lock()

def safe_print(message: str):
    """线程安全的打印函数"""
    with print_lock:
        print(message)

def _add_swift_file_to_project(file_path, project_path):
    """添加Swift文件到Xcode项目"""
    try:
        pbxproj_path = None
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.pbxproj'):
                    pbxproj_path = os.path.join(root, file)
                    break
            if pbxproj_path:
                break
        
        if not pbxproj_path:
            safe_print("未找到.pbxproj文件")
            return
            
        project = XcodeProject.load(pbxproj_path)
        project.add_file(file_path)
        project.save()
        
    except Exception as e:
        safe_print(f"添加文件到项目时出错: {str(e)}")

class XcodeSwiftFileCreator:
    def __init__(self, project_path: str, aes_key: str, method_prefix: str):
        self.project_path = project_path
        self.aes_key = aes_key
        self.method_prefix = method_prefix

    def create_swift_file(self, file_name: str, target_name: str) -> bool:
        try:
            file_path = os.path.join(self.project_path, target_name, f'{file_name}.swift')
            swift_content = self._create_swift_template(file_name, self.aes_key, self.method_prefix)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(swift_content)
            
            _add_swift_file_to_project(file_path, self.project_path)
            return True
            
        except Exception as e:
            safe_print(f"创建文件时发生错误: {str(e)}")
            return False

    def _create_swift_template(self, file_name: str, aes_key: str, method_prefix: str) -> str:
        return f'''//
//  {file_name}
//
//  Created on {datetime.now().strftime("%Y/%m/%d")}
//

import Foundation
import CryptoSwift

extension String {{
    enum StringDecrypt {{
        static let key = "{aes_key}"
        static let iv = "{aes_key}"
    }}
    
    func {method_prefix}_decrypt() -> String{{
        var text: String?
        do {{
            let aes = try AES(key: StringDecrypt.key, iv: StringDecrypt.iv, padding: .pkcs5)
            let finiteCiphertext = try aes.decrypt(Array(base64: self))
            let backwardString = String(decoding: finiteCiphertext, as: UTF8.self)
            text = backwardString
        }} catch {{
        }}
        return text ?? ""
    }}

    func {method_prefix}_encrypt() -> String? {{
        var text = ""
        do {{
            let aes = try AES(key: StringDecrypt.key, iv: StringDecrypt.iv, padding: .pkcs5)
            let finiteCiphertext = try aes.encrypt(Array(self.utf8))
            text = finiteCiphertext.toBase64()
        }}
        catch {{
        }}
        return text
    }}
}}
'''

def is_ignore_file(file_path: str) -> bool:
    """检查文件是否应该被忽略"""
    path_parts = file_path.split("/")
    return any(directory in path_parts for directory in IGNORE_DIRECTORY)

def generate_aes_key(length: int = 16) -> str:
    """生成AES密钥"""
    try:
        uppercase_letters = string.ascii_uppercase
        digits = string.digits
        lowercase_letters = string.ascii_lowercase
        
        key = [
            random.choice(uppercase_letters),
            random.choice(digits),
            random.choice(lowercase_letters)
        ]
        
        remaining_length = length - len(key)
        all_chars = uppercase_letters + digits + lowercase_letters
        
        for _ in range(remaining_length):
            key.append(random.choice(all_chars))
        
        random.shuffle(key)
        return ''.join(key)
    
    except Exception as e:
        safe_print(f"生成密钥时发生错误: {str(e)}")
        return None

def rw_encrypt(key: str, plain_text: str) -> str:
    """加密字符串"""
    try:
        key_bytes = key.encode('utf-8') 
        iv = key_bytes
        
        data = plain_text.encode('utf-8')
        padded_data = pad(data, AES.block_size)
        
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(padded_data)
        
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception:
        return ""

def should_include_string(string_content: str) -> Tuple[bool, str]:
    """快速过滤字符串，返回(是否包含, 过滤原因)"""
    if not string_content:
        return False, "空字符串"
    
    if len(string_content) >= 100:
        return False, "字符串太长"
    
    # 快速base64检测（优化版）
    if (len(string_content) > 15 and 
        len(string_content) % 4 == 0 and
        re.match(r'^[A-Za-z0-9+/]*={0,2}$', string_content) and
        ('+' in string_content or '/' in string_content or '=' in string_content)):
        return False, "可能是base64编码"
    
    # 快速URL检测
    if string_content.startswith(('http', 'ftp')):
        return False, "URL链接"
    
    # 快速文件扩展名检测
    if string_content.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf')):
        return False, "文件名"
    
    # 快速颜色值检测
    if len(string_content) == 7 and string_content.startswith('#'):
        return False, "颜色值"
    
    # 快速布尔值检测
    if string_content in {'true', 'false', 'nil', 'null', 'YES', 'NO'}:
        return False, "布尔值或空值"
    
    return True, ""

def extract_strings_from_file(file_path: str) -> Set[str]:
    """从单个文件提取字符串（用于并行处理）"""
    if is_ignore_file(file_path) or 'Decryptor' in os.path.basename(file_path):
        return set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 改进的正则表达式，排除多行字符串
        # 首先移除多行字符串内容，避免误匹配
        multiline_pattern = re.compile(r'""".*?"""', re.DOTALL)
        content_without_multiline = multiline_pattern.sub('', content)
        
        # 使用更精确的正则表达式匹配单行字符串
        string_pattern = re.compile(r'"(?:[^"\\\\]|\\\\.)*"')
        matches = string_pattern.findall(content_without_multiline)
        
        valid_strings = set()
        for match in matches:
            string_content = match[1:-1]  # 去掉引号
            should_include, _ = should_include_string(string_content)
            if should_include:
                valid_strings.add(string_content)
        
        return valid_strings
        
    except Exception as e:
        safe_print(f"读取文件 {file_path} 时出错: {str(e)}")
        return set()

def extract_strings_from_swift_files(project_path: str) -> List[str]:
    """并行提取项目中所有Swift文件的字符串"""
    safe_print("🔍 开始扫描项目中的Swift文件...")
    
    # 收集所有Swift文件
    swift_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.swift'):
                file_path = os.path.join(root, file)
                swift_files.append(file_path)
    
    safe_print(f"找到 {len(swift_files)} 个Swift文件")
    
    # 并行处理文件
    all_strings = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_file = {executor.submit(extract_strings_from_file, file_path): file_path 
                         for file_path in swift_files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                file_strings = future.result()
                all_strings.update(file_strings)
            except Exception as e:
                safe_print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    string_list = sorted(list(all_strings))
    safe_print(f"✅ 扫描完成! 提取到 {len(string_list)} 个唯一字符串")
    
    return string_list

def create_compiled_patterns(data_map: Dict[str, str], method_prefix: str) -> List[Tuple[re.Pattern, str, str]]:
    """预编译所有正则表达式模式"""
    patterns = []
    # 按长度排序，长字符串优先
    sorted_items = sorted(data_map.items(), key=lambda x: len(x[0]), reverse=True)
    
    for de_str, en_str in sorted_items:
        escaped_de_str = re.escape(de_str)
        pattern = re.compile(f'"{escaped_de_str}"(?!\\.\\w+_decrypt\\(\\))')
        replacement = f'"{en_str}".{method_prefix}_decrypt()'
        patterns.append((pattern, replacement, de_str))
    
    return patterns

def load_predefined_strings(file_path: str = 'ios_resource/ios_collection_str.txt') -> Set[str]:
    """加载预定义的字符串列表"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        safe_print(f"❌ 找不到预定义字符串文件: {file_path}")
        return set()

def process_file_content(file_path: str, patterns: List[Tuple[re.Pattern, str, str]], 
                        decryptor_file_name: str, predefined_strings: Set[str]) -> bool:
    """处理单个文件的字符串替换"""
    if is_ignore_file(file_path) or os.path.basename(file_path) == decryptor_file_name:
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 检查是否已经包含解密方法，如果是则跳过整个文件
        if re.search(r'\.\w+_decrypt\(\)', content):
            return False
        
        # 按行处理，避免跨行替换问题
        lines = content.split('\n')
        processed_lines = []
        replacements_made = 0
        
        for line in lines:
            # 跳过多行字符串的开始和结束行
            if '"""' in line:
                processed_lines.append(line)
                continue
            
            # 跳过字符串插值复杂的行（包含 \( 的行）
            if '\\(' in line:
                processed_lines.append(line)
                continue
                
            processed_line = line
            
            # 使用预定义的字符串列表进行匹配和替换
            for pattern, replacement, original_str in patterns:
                if original_str in predefined_strings and pattern.search(processed_line):
                    new_line = pattern.sub(replacement, processed_line)
                    if new_line != processed_line:
                        processed_line = new_line
                        replacements_made += 1
            
            processed_lines.append(processed_line)
        
        content = '\n'.join(processed_lines)
        
        # 只有当内容改变时才写入
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            safe_print(f"  📝 更新文件: {os.path.basename(file_path)} (替换了 {replacements_made} 个字符串)")
            return True
        
        return False
        
    except Exception as e:
        safe_print(f"处理文件 {file_path} 时出错: {str(e)}")
        return False

def process_files_parallel(project_path: str, patterns: List[Tuple[re.Pattern, str, str]], 
                          decryptor_file_name: str, predefined_strings: Set[str]):
    """并行处理所有文件的字符串替换"""
    # 收集所有需要处理的Swift文件
    swift_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.swift'):
                file_path = os.path.join(root, file)
                swift_files.append(file_path)
    
    safe_print(f"开始处理 {len(swift_files)} 个Swift文件...")
    
    # 并行处理文件
    updated_files = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_file = {executor.submit(process_file_content, file_path, patterns, decryptor_file_name, predefined_strings): file_path 
                         for file_path in swift_files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                was_updated = future.result()
                if was_updated:
                    updated_files += 1
            except Exception as e:
                safe_print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    safe_print(f"✅ 处理完成! 更新了 {updated_files} 个文件")

def start_confuse_string():
    """主函数"""
    safe_print("🚀 开始高性能字符串混淆...")
    
    # 生成随机方法前缀和密钥
    random_method_prefix = ''.join(random.choices(string.ascii_letters, k=2)).lower()
    aes_key = generate_aes_key()
    
    safe_print(f"🔑 使用密钥: {aes_key}")
    safe_print(f"🔧 使用方法前缀: {random_method_prefix}")
    
    # 加载预定义的字符串列表
    predefined_strings = load_predefined_strings('ios_resource/ios_collection_str.txt')
    safe_print(f"📚 加载了 {len(predefined_strings)} 个预定义字符串")
    
    # 提取字符串
    extracted_strings = extract_strings_from_swift_files(project_path)
    
    if not extracted_strings:
        safe_print("❌ 没有找到可以混淆的字符串，程序退出")
        return
    
    safe_print(f"🔐 开始加密 {len(extracted_strings)} 个字符串...")
    
    # 批量加密字符串
    data_map = {}
    for string_content in extracted_strings:
        if string_content in predefined_strings:  # 只加密预定义的字符串
            encrypted = rw_encrypt(aes_key, string_content)
            if encrypted:
                data_map[string_content] = encrypted
    
    safe_print(f"✅ 成功加密 {len(data_map)} 个字符串")
    
    # 创建解密文件
    creator = XcodeSwiftFileCreator(project_path, aes_key=aes_key, method_prefix=random_method_prefix)
    file_name = f'String+{random_method_prefix}Decryptor'
    decryptor_file_name = f'{file_name}.swift'
    creator.create_swift_file(file_name, target_name)
    
    # 写入映射关系到native_con_str.txt
    log_content = ""
    for original, encrypted in data_map.items():
        log_content += f"{original} ----> {encrypted}\n"
    
    # 写入到native_con_str.txt
    with open('ios_log/native_con_str.txt', 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    # 预编译正则表达式模式
    safe_print("🔧 预编译正则表达式模式...")
    patterns = create_compiled_patterns(data_map, random_method_prefix)
    
    # 并行处理文件替换
    safe_print("🔄 开始字符串替换...")
    process_files_parallel(project_path, patterns, decryptor_file_name, predefined_strings)
    
    safe_print("🎉 字符串混淆完成!")

if __name__ == '__main__':

    project_info = get_project_info()
    
    # 获取所有Swift文件
    swift_files = project_info.swift_files
    project_path = project_info.project_path
    target_name = project_info.target_name
    print("Processing files:", swift_files)


    start_confuse_string() 