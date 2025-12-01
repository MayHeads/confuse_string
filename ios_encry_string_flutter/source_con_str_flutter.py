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
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info
from config import CONFUSE_KEY

# 处理相对导入和绝对导入
try:
    # 尝试相对导入（作为模块导入时）
    from .collect_str_flutter import main_collect_str_flutter
except ImportError:
    # 如果相对导入失败，使用绝对导入（直接运行时）
    import importlib.util
    current_dir = os.path.dirname(os.path.abspath(__file__))
    collect_str_path = os.path.join(current_dir, 'collect_str_flutter.py')
    spec = importlib.util.spec_from_file_location("collect_str_flutter", collect_str_path)
    collect_str_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collect_str_module)
    main_collect_str_flutter = collect_str_module.main_collect_str_flutter

def generate_random_aes_key(length=16):
    """生成随机的AES密钥"""
    # 使用数字和大写字母生成密钥
    characters = string.digits + string.ascii_uppercase
    return ''.join(random.choice(characters) for _ in range(length))

# 生成随机的AES密钥，每次运行都不同
LOCAL_AES_KEY = generate_random_aes_key(16)
print(f"生成随机AES密钥: {LOCAL_AES_KEY}")

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
    collection_file = f'{os.getcwd()}/ios_resource/ios_collection_str_flutter.txt'
    
    if not os.path.exists(collection_file):
        print(f"字符串收集文件不存在: {collection_file}")
        return data_map
    
    # 清空日志文件
    log_file = f'{os.getcwd()}/ios_log/native_con_str_flutter.txt'
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("👉👉👉👉👉Flutter String Obfuscation Map List👈👈👈👈👈\n\n\n")

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
    local_map_file = os.path.join(project_path, 'ios_log', 'native_con_str_flutter.txt')
    os.makedirs(os.path.dirname(local_map_file), exist_ok=True)
    with open(local_map_file, 'w', encoding='utf-8') as f:
        f.write("👉👉👉👉👉Flutter String Obfuscation Map List👈👈👈👈👈\n\n\n")
        for string in strings:
            f.write(string + '\n')
            
    return data_map

def create_flutter_decryptor_file(flutter_plugin_path: str, aes_key: str, method_prefix: str) -> str:
    """
    创建Flutter解密器文件
    Args:
        flutter_plugin_path: Flutter Plugin路径
        aes_key: AES密钥
        method_prefix: 方法前缀
    Returns:
        创建的文件路径
    """
    # 确保lib目录存在
    lib_dir = os.path.join(flutter_plugin_path, 'lib')
    os.makedirs(lib_dir, exist_ok=True)
    
    # 生成文件名
    file_name = f'string_decryptor_{method_prefix}.dart'
    file_path = os.path.join(lib_dir, file_name)
    
    # 检查文件是否已存在
    if os.path.exists(file_path):
        print(f"文件 {file_name} 已存在，将覆盖")
    
    # 创建Dart文件内容
    # 使用 encrypt 包（需要在 pubspec.yaml 中添加依赖）
    dart_content = f'''//
//  {file_name}
//
//  Created on {datetime.now().strftime("%Y/%m/%d")}
//  String Decryptor for Flutter
//
//  Note: This file requires 'encrypt' package in pubspec.yaml:
//    dependencies:
//      encrypt: ^5.0.0

import 'dart:convert';
import 'package:encrypt/encrypt.dart';

class StringDecryptor{method_prefix.capitalize()} {{
  static final String _keyStr = "{aes_key}";
  static final String _ivStr = "{aes_key}";
  
  static Key get _key => Key(utf8.encode(_keyStr));
  static IV get _iv => IV(utf8.encode(_ivStr));
  
  /// 解密字符串
  static String decrypt(String encryptedText) {{
    try {{
      // Base64解码
      final encrypted = Encrypted(base64Decode(encryptedText));
      
      // 创建AES解密器
      final encrypter = Encrypter(AES(_key, mode: AESMode.cbc));
      
      // 解密
      final decrypted = encrypter.decrypt(encrypted, iv: _iv);
      
      return decrypted;
    }} catch (e) {{
      return "";
    }}
  }}
  
  /// 加密字符串（用于测试）
  static String encrypt(String plainText) {{
    try {{
      // 创建AES加密器
      final encrypter = Encrypter(AES(_key, mode: AESMode.cbc));
      
      // 加密
      final encrypted = encrypter.encrypt(plainText, iv: _iv);
      
      // Base64编码
      return encrypted.base64;
    }} catch (e) {{
      return "";
    }}
  }}
}}

extension StringDecryptExtension on String {{
  /// 解密字符串扩展方法
  String {method_prefix}_decrypt() {{
    return StringDecryptor{method_prefix.capitalize()}.decrypt(this);
  }}
}}
'''
    
    # 创建文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(dart_content)
    
    print(f"成功创建Flutter解密器文件: {file_path}")
    return file_path

def replace_strings_in_dart_files(dart_files: List[str], data_map: dict, method_prefix: str, decryptor_file_name: str, package_name: str):
    """
    替换Dart文件中的字符串
    Args:
        dart_files: Dart文件列表
        data_map: 字符串映射字典
        method_prefix: 方法前缀
        decryptor_file_name: 解密器文件名（不含路径，用于导入）
        package_name: Flutter包名
    """
    replaced_count = 0
    
    # 计算导入路径（使用package:格式）
    # 格式: import 'package:包名/string_decryptor_sq.dart';
    import_path = decryptor_file_name.replace('.dart', '')
    import_statement = f"import 'package:{package_name}/{import_path}.dart';"
    
    for file_path in dart_files:
        try:
            # 读取文件
            encodings = ['utf-8', 'utf-16', 'ascii', 'latin1']
            content = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    used_encoding = encoding
                    break
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            if content is None:
                print(f"无法读取文件 {file_path}")
                continue
            
            # 替换所有匹配的字符串
            modified = False
            for de_str, en_str in data_map.items():
                # 替换单引号字符串
                single_pattern = f"'{re.escape(de_str)}'"
                single_replacement = f"/*{de_str}*/'{en_str}'.{method_prefix}_decrypt()"
                new_content = re.sub(single_pattern, single_replacement, content)
                if new_content != content:
                    modified = True
                    content = new_content
                
                # 替换双引号字符串
                double_pattern = f'"{re.escape(de_str)}"'
                double_replacement = f'/*{de_str}*/"{en_str}".{method_prefix}_decrypt()'
                new_content = re.sub(double_pattern, double_replacement, content)
                if new_content != content:
                    modified = True
                    content = new_content
            
            if modified:
                # 检查是否需要添加导入语句
                # 检查是否已经有导入语句（检查完整的导入路径）
                if import_statement not in content and f"package:{package_name}/{import_path}" not in content:
                    # 查找最后一个import语句的位置
                    import_pattern = r'^import\s+[\'"][^\'"]+[\'"]\s*;'
                    imports = list(re.finditer(import_pattern, content, re.MULTILINE))
                    
                    if imports:
                        # 在最后一个import语句后添加
                        last_import = imports[-1]
                        insert_pos = last_import.end()
                        content = content[:insert_pos] + '\n' + import_statement + content[insert_pos:]
                    else:
                        # 如果没有import语句，在文件开头添加
                        content = import_statement + '\n\n' + content
                
                # 写回文件
                with open(file_path, 'w', encoding=used_encoding) as f:
                    f.write(content)
                replaced_count += 1
                print(f"成功更新文件 {file_path}")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    return replaced_count

def start_string_obfuscation_flutter():
    """开始Flutter字符串混淆流程"""
    project_info = get_project_info()
    if not project_info:
        print("无法获取项目信息，程序退出")
        return
    
    flutter_plugin_path = project_info.flutter_plugin_path
    flutter_plugin_dart_files = project_info.flutter_plugin_dart_files
    
    # 检查是否有flutter_plugin_path
    if not flutter_plugin_path or not flutter_plugin_dart_files:
        print("未找到flutter_plugin_path或dart文件，跳过Flutter字符串混淆")
        return
    
    project_path = project_info.project_path
    random_method_prefix = ''.join(random.choices(string.ascii_letters, k=2)).lower()
    aes_key = LOCAL_AES_KEY

    print(f"开始Flutter字符串混淆流程...")
    print(f"Flutter Plugin路径: {flutter_plugin_path}")
    print(f"Dart文件数量: {len(flutter_plugin_dart_files)}")
    print(f"方法前缀: {random_method_prefix}")

    # 处理字符串加密并获取映射关系
    data_map = process_strings_and_write_mapping(aes_key, project_path)
    
    if not data_map:
        print("没有找到需要加密的字符串")
        return

    print(f"成功创建 {len(data_map)} 个字符串映射")

    # 创建Flutter解密器文件（放到lib目录下）
    decryptor_file = create_flutter_decryptor_file(flutter_plugin_path, aes_key, random_method_prefix)
    print(f"解密器文件已创建: {decryptor_file}")
    
    # 获取解密器文件名（用于导入）
    decryptor_file_name = os.path.basename(decryptor_file)
    
    # 从flutter_plugin_path中提取包名（路径的最后一级目录名）
    package_name = os.path.basename(os.path.normpath(flutter_plugin_path))
    print(f"包名: {package_name}")

    # 替换Dart文件中的字符串
    print(f"\n开始替换Dart文件中的字符串...")
    replaced_count = replace_strings_in_dart_files(flutter_plugin_dart_files, data_map, random_method_prefix, decryptor_file_name, package_name)
    print(f"成功替换了 {replaced_count} 个Dart文件")

def enc_string_process_flutter():
    """Flutter字符串加密处理主流程"""
    # 1. 收集字符串
    main_collect_str_flutter()
    
    # 2. 加密并替换
    start_string_obfuscation_flutter()

if __name__ == '__main__':
    enc_string_process_flutter()

