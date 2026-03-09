# 对 Flutter Plugin 中的 Swift 文件进行字符串加密
# 1. 遍历 flutter_plugin_path 下的 Swift 文件
# 2. 收集字符串并加密
# 3. 生成解密器文件到 flutter_plugin_path/ios/Classes 目录
# 4. 替换 Swift 文件中的字符串

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
import base64
import uuid
from datetime import datetime
import re
import os
import random
import string
import sys
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info
from config import custom_ignore_folders, ig_fix_text, ig_format_text

def generate_random_aes_key(length=16):
    """生成随机的AES密钥"""
    # 使用数字和大写字母生成密钥
    characters = string.digits + string.ascii_uppercase
    return ''.join(random.choice(characters) for _ in range(length))

# 生成随机的AES密钥，每次运行都不同
LOCAL_AES_KEY = generate_random_aes_key(16)
print(f"生成随机AES密钥: {LOCAL_AES_KEY}")

# 忽略规则列表
IGNORE_RULES = [
    r'^\s*$',  # 空字符串
    r'^-+$',   # 只包含连字符的字符串
    r'^[-\s]+$',  # 只包含连字符和空格的字符串
]

def should_ignore_string(s: str) -> bool:
    """检查字符串是否应该被忽略"""
    # 检查是否匹配任何忽略规则
    for rule in IGNORE_RULES:
        if re.match(rule, s):
            return True
    
    # 检查是否在固定文本忽略列表中
    if s in ig_fix_text:
        return True
    
    # 检查是否是格式化字符串
    for format_str in ig_format_text:
        if format_str in s:
            return True
    
    return False

def is_ignore_file(file_path: str) -> bool:
    """检查文件是否应该被忽略"""
    for directory in custom_ignore_folders:
        file_folder_list = file_path.split("/")
        if directory in file_folder_list:
            return True
    return False

def extract_strings_from_content(content: str) -> Set[str]:
    """从内容中提取所有字符串"""
    strings = set()
    
    # 匹配所有字符串字面量
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
    """从单个文件中提取字符串"""
    try:
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
            return set()
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return set()

    # 移除多行字符串
    content = re.sub(r'"""(?:[^"]|"[^"]|""[^"])*"""', '', content)
    
    return extract_strings_from_content(content)

def collect_strings_from_swift_files(swift_files: List[str]) -> Set[str]:
    """并行收集所有Swift文件中的字符串"""
    all_strings = set()
    
    if not swift_files:
        print("没有找到Swift文件")
        return all_strings
    
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
                print(f"处理文件 {file} 时出错: {e}")
    
    return all_strings

def save_strings_to_file(strings: Set[str], output_file: str):
    """将收集到的字符串保存到文件"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for s in sorted(strings):
            try:
                f.write(f"{s}\n")
            except UnicodeEncodeError:
                print(f"警告: 跳过无效UTF-8编码的字符串: {s}")

def rw_decrypt(key: str, encrypted_text: str) -> str:
    """解密字符串"""
    try:
        key_bytes = key.encode('utf-8') 
        iv = key_bytes   
        
        # Base64解码
        cipher_text = base64.b64decode(encrypted_text)
        
        # 创建AES解密器
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        
        # 解密并移除填充
        decrypted_data = unpad(cipher.decrypt(cipher_text), AES.block_size)
        
        # 转换为字符串
        result = decrypted_data.decode('utf-8')
        
        return result
    except Exception as e:
        print(f"解密错误: {e}")
        return ""

def rw_encrypt(key: str, plain_text: str) -> str:
    """加密字符串"""
    try:
        key_bytes = key.encode('utf-8') 
        iv = key_bytes   
        
        # 将字符串转换为字节并添加填充
        data = plain_text.encode('utf-8')
        padded_data = pad(data, AES.block_size)
        
        # 创建AES加密器
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        
        # 加密数据
        encrypted_data = cipher.encrypt(padded_data)
        
        # 转换为base64编码的字符串
        result = base64.b64encode(encrypted_data).decode('utf-8')
        
        return result
    except Exception as e:
        print(f"加密错误: {e}")
        return ""

def process_strings_and_write_mapping(aes_key: str, project_path: str) -> dict:
    """
    处理字符串加密并写入映射关系
    Args:
        aes_key: AES加密密钥
        project_path: 项目路径
    Returns:
        dict: 加密后的字符串映射关系
    """
    data_map = {}
    
    # 读取收集到的字符串文件
    collection_file = f'{os.getcwd()}/ios_resource/ios_collection_str_flutter_swift.txt'
    
    if not os.path.exists(collection_file):
        print(f"字符串收集文件不存在: {collection_file}")
        return data_map
    
    # 清空日志文件
    log_file = f'{os.getcwd()}/ios_log/native_con_str_flutter_swift.txt'
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("👉👉👉👉👉Flutter Swift String Obfuscation Map List👈👈👈👈👈\n\n\n")

    strings = []
    with open(collection_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        for i in range(len(lines)):
            line = lines[i].strip()
            if not line:
                continue
                
            en_str = rw_encrypt(aes_key, line)
            de_str = rw_decrypt(aes_key, en_str)
    
            if line == de_str:
                print(f"{de_str} <-----> {en_str}")
                strings.append(f"{de_str} <-----------> {en_str}")
                data_map[de_str] = en_str
    
    # 写入映射日志
    with open(log_file, 'a', encoding='utf-8') as f:
        for string in strings:
            f.write(string + '\n')

    # 也在项目目录下保存一份日志
    local_map_file = os.path.join(project_path, 'ios_log', 'native_con_str_flutter_swift.txt')
    os.makedirs(os.path.dirname(local_map_file), exist_ok=True)
    with open(local_map_file, 'w', encoding='utf-8') as f:
        f.write("👉👉👉👉👉Flutter Swift String Obfuscation Map List👈👈👈👈👈\n\n\n")
        for string in strings:
            f.write(string + '\n')
            
    return data_map

def create_swift_decryptor_file(flutter_plugin_path: str, aes_key: str, method_prefix: str) -> str:
    """
    创建Swift解密器文件到 flutter_plugin_path/ios/Classes 目录
    Args:
        flutter_plugin_path: Flutter Plugin路径
        aes_key: AES密钥
        method_prefix: 方法前缀
    Returns:
        创建的文件路径
    """
    # 确保 ios/Classes 目录存在
    classes_dir = os.path.join(flutter_plugin_path, 'ios', 'Classes')
    os.makedirs(classes_dir, exist_ok=True)
    
    # 生成文件名
    file_name = f'String+{method_prefix}Decryptor.swift'
    file_path = os.path.join(classes_dir, file_name)
    
    # 检查文件是否已存在
    if os.path.exists(file_path):
        print(f"文件 {file_name} 已存在，将覆盖")
    
    # 创建Swift文件内容
    swift_content = f'''//
//  {file_name}
//
//  Created on {datetime.now().strftime("%Y/%m/%d")}
//

import Foundation
import CryptoSwift

extension String {{
    public enum StringDecrypt {{
        static let key = "{aes_key}"
        static let iv = "{aes_key}"
    }}
    
    public func {method_prefix}_decrypt() -> String{{
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

    public func {method_prefix}_encrypt() -> String? {{
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
    
    # 创建文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(swift_content)
    
    print(f"成功创建Swift解密器文件: {file_path}")
    return file_path

def collect_swift_files_from_flutter_plugin(flutter_plugin_path: str) -> List[str]:
    """从 flutter_plugin_path 收集所有 Swift 文件"""
    swift_files = []
    
    if not flutter_plugin_path or not os.path.exists(flutter_plugin_path):
        return swift_files
    
    for root, dirs, files in os.walk(flutter_plugin_path):
        # 跳过忽略的文件夹
        dirs[:] = [d for d in dirs if d not in custom_ignore_folders]
        
        for file in files:
            if file.endswith('.swift'):
                file_path = os.path.join(root, file)
                if not is_ignore_file(file_path):
                    swift_files.append(file_path)
    
    return swift_files

def replace_strings_in_swift_files(swift_files: List[str], data_map: dict, method_prefix: str):
    """
    替换Swift文件中的字符串
    Args:
        swift_files: Swift文件列表
        data_map: 字符串映射字典
        method_prefix: 方法前缀
    """
    replaced_count = 0
    
    for file_path in swift_files:
        if is_ignore_file(file_path):
            continue
        
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
                print(f"无法读取文件 {file_path}")
                continue
            
            print(f"正在处理文件 {file_path}...")
            
            # 替换所有匹配的字符串
            modified = False
            for de_str, en_str in data_map.items():
                # 使用 re.escape 转义特殊字符，并添加原始字符串注释
                escaped_str = re.escape(de_str)
                pattern = f'"{escaped_str}"'
                replacement = f'/*{de_str}*/"{en_str}".{method_prefix}_decrypt()'
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    modified = True
            
            if modified:
                # 写回文件
                with open(file_path, 'w', encoding=used_encoding, errors='ignore') as f:
                    f.write(content)
                replaced_count += 1
                print(f"✓ 已更新文件: {file_path}")
                
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    print(f"\n替换完成统计: 更新了 {replaced_count} 个文件")

def start_string_obfuscation_flutter_swift():
    """开始Flutter Swift字符串混淆流程"""
    project_info = get_project_info()
    if not project_info:
        print("无法获取项目信息，程序退出")
        return
    
    flutter_plugin_path = project_info.flutter_plugin_path
    
    # 检查是否有flutter_plugin_path
    if not flutter_plugin_path:
        print("未找到flutter_plugin_path，跳过Swift字符串加密")
        return
    
    print(f"开始处理Flutter Plugin中的Swift文件字符串加密...")
    print(f"Flutter Plugin路径: {flutter_plugin_path}")
    
    # 步骤1: 收集 flutter_plugin_path 下的所有 Swift 文件
    print(f"\n=== 步骤1: 收集Swift文件 ===")
    swift_files = collect_swift_files_from_flutter_plugin(flutter_plugin_path)
    print(f"找到 {len(swift_files)} 个Swift文件")
    
    if not swift_files:
        print("未找到Swift文件，跳过字符串加密")
        return
    
    # 步骤2: 收集字符串
    print(f"\n=== 步骤2: 收集字符串 ===")
    strings = collect_strings_from_swift_files(swift_files)
    print(f"收集到 {len(strings)} 个唯一的字符串")
    
    # 保存收集到的字符串
    output_file = "ios_resource/ios_collection_str_flutter_swift.txt"
    save_strings_to_file(strings, output_file)
    print(f"字符串已保存到: {output_file}")
    
    if not strings:
        print("未收集到字符串，跳过加密处理")
        return
    
    # 步骤3: 生成随机方法前缀和AES密钥
    random_method_prefix = ''.join(random.choices(string.ascii_letters, k=2)).lower()
    aes_key = LOCAL_AES_KEY
    
    # 步骤4: 处理字符串加密并获取映射关系
    print(f"\n=== 步骤3: 加密字符串 ===")
    data_map = process_strings_and_write_mapping(aes_key, project_info.project_path)
    print(f"创建了 {len(data_map)} 个字符串映射关系")
    
    if not data_map:
        print("没有成功生成任何字符串映射，跳过后续处理")
        return
    
    # 步骤5: 创建Swift解密器文件
    print(f"\n=== 步骤4: 创建Swift解密器文件 ===")
    file_name = f'String+{random_method_prefix}Decryptor'
    decryptor_path = create_swift_decryptor_file(flutter_plugin_path, aes_key, random_method_prefix)
    print(f"解密器文件已创建: {decryptor_path}")
    
    # 步骤6: 替换Swift文件中的字符串
    print(f"\n=== 步骤5: 替换Swift文件中的字符串 ===")
    replace_strings_in_swift_files(swift_files, data_map, random_method_prefix)
    
    print(f"\n处理完成！")

def enc_string_process_flutter_swift():
    """完整的字符串加密处理流程"""
    start_string_obfuscation_flutter_swift()

if __name__ == '__main__':
    enc_string_process_flutter_swift()

