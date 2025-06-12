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
from pbxproj import XcodeProject
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info
from config import custom_ignore_folders, custom_ignore_swift_files, ig_fix_text, ig_format_text
from collect_str import main_collect_str_all




project_info = get_project_info()



## 项目路径
project_path = project_info.project_path
## 替换为你的目标名称（通常与项目名相同）
target_name = project_info.target_name

IGNORE_DIRECTORY = custom_ignore_folders

class XcodeSwiftFileCreator:
    def __init__(self, project_path: str, aes_key: str,method_prefix:str):
        self.project_path = project_path
        self.pbxproj_path = self._find_pbxproj()
        self.aes_key = aes_key
        self.method_prefix = method_prefix
        
    def _find_pbxproj(self) -> str:
        """查找项目的.pbxproj文件"""
        for root, dirs, files in os.walk(self.project_path):
            for dir in dirs:
                if dir.endswith('.xcodeproj'):
                    return os.path.join(root, dir, 'project.pbxproj')
        raise FileNotFoundError("找不到.xcodeproj文件")

    

    def create_swift_file(self, file_name: str, target_name: str) -> bool:
        try:
            # 确保文件名有.swift后缀
            if not file_name.endswith('.swift'):
                file_name = f"{file_name}.swift"

            # 确定文件路径
            file_dir = os.path.join(self.project_path, target_name)
            file_path = os.path.join(file_dir, file_name)

            # 检查文件是否已存在
            if os.path.exists(file_path):
                print(f"文件 {file_name} 已存在!")
                return False

            # 创建Swift文件内容
            swift_content = self._create_swift_template(file_name,aes_key=self.aes_key,method_prefix=self.method_prefix)
            
            # 创建文件
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(swift_content)

            # 将文件添加到项目中
            # self._add_file_to_project(file_name, target_name)

            self._add_swift_file_to_project(file_path, target_name)

            print(f"成功创建并添加Swift文件: {file_path}")
            return True

        except Exception as e:
            print(f"创建文件时发生错误: {str(e)}")
            return False

    def _create_swift_template(self, file_name: str,aes_key: str,method_prefix: str) -> str:
        """创建Swift文件模板"""
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
    def _add_swift_file_to_project(self,file_path, target_name):
        # 打开 .xcodeproj 文件
        project = XcodeProject.load(self.pbxproj_path)

        # 获取相对路径
        relative_path = os.path.relpath(file_path, self.project_path)
        
        # 添加文件到项目
        project.add_file(relative_path, force=False)

        # set a Other Linker Flags
        project.add_other_ldflags('-ObjC')

        # save the project, otherwise your changes won't be picked up by Xcode
        project.save()


#是否是忽略文件
def is_ignore_file(file_path):
    is_exit = False
    for directory in IGNORE_DIRECTORY:
        file_floder_list = file_path.split("/")
        if directory in file_floder_list:
            is_exit = True
            break
    return is_exit    

def rw_decrypt(key:str, encrypted_text: str) -> str:
    try:

        key = key.encode('utf-8') 
        iv = key   
        
        # Base64解码
        cipher_text = base64.b64decode(encrypted_text)
        
        # 创建AES解密器
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # 解密并移除填充
        decrypted_data = unpad(cipher.decrypt(cipher_text), AES.block_size)
        
        # 转换为字符串
        result = decrypted_data.decode('utf-8')
        
        return result
    except Exception as e:
        return ""

def generate_aes_key(length: int = 16) -> str:
    """
    生成指定长度的AES密钥
    格式：大写字母 + 数字 + 小写字母的组合
    """
    try:
        # 定义字符集
        uppercase_letters = string.ascii_uppercase  # A-Z
        digits = string.digits                     # 0-9
        lowercase_letters = string.ascii_lowercase  # a-z
        
        # 确保每种字符至少出现一次
        key = [
            random.choice(uppercase_letters),  # 至少一个大写字母
            random.choice(digits),            # 至少一个数字
            random.choice(lowercase_letters)   # 至少一个小写字母
        ]
        
        # 剩余长度随机填充
        remaining_length = length - len(key)
        all_chars = uppercase_letters + digits + lowercase_letters
        
        # 生成剩余字符
        for _ in range(remaining_length):
            key.append(random.choice(all_chars))
        
        # 打乱顺序
        random.shuffle(key)
        
        # 合并成字符串
        return ''.join(key)
    
    except Exception as e:
        print(f"生成密钥时发生错误: {str(e)}")
        return None


def rw_encrypt(key:str, plain_text: str) -> str:
    try:
        
        # key = b'8TWKJHW080iEABVC'  # 替换为实际的密钥
        # iv = b'8TWKJHW080iEABVC'    # 替换为实际的IV
        
        key = key.encode('utf-8') 
        iv = key   
        
        # 将字符串转换为字节并添加填充
        data = plain_text.encode('utf-8')
        padded_data = pad(data, AES.block_size)
        
        # 创建AES加密器
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # 加密数据
        encrypted_data = cipher.encrypt(padded_data)
        
        # 转换为base64编码的字符串
        result = base64.b64encode(encrypted_data).decode('utf-8')
        
        return result
    except Exception as e:
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
    
    #读取本文件目录下的另外一个文件
    with open(f'{os.getcwd()}/ios_log/native_con_str.txt', 'r+') as log_file:
        log_file.truncate(0)

    with open(f'{os.getcwd()}/ios_resource/ios_collection_str.txt', 'r') as f:
        lines = f.readlines()

        strings = []
        for i in range(len(lines)):
            line = lines[i].strip()
            en_str = rw_encrypt(aes_key,line)
            de_str = rw_decrypt(aes_key,en_str)
    
            if line == de_str:
                print(f"{de_str} <-----> {en_str}")
                strings.append(f"{de_str} <-----------> {en_str}")
                data_map[de_str] = en_str
            
    #映射日志
    with open(f'{os.getcwd()}/ios_log/native_con_str.txt', 'r+') as f: 
        f.write("👉👉👉👉👉string Obfuscation Map List👈👈👈👈👈" + '\n\n\n')
        for string in strings:
            f.write(string + '\n')

    local_map_file = project_path + '/ios_log/native_con_str.txt'
    os.makedirs(os.path.dirname(local_map_file), exist_ok=True)
    with open(local_map_file, 'w', encoding='utf-8') as f:
        f.write("👉👉👉👉👉string Obfuscation Map List👈👈👈👈👈" + '\n\n\n')
        for string in strings:
            f.write(string + '\n')
            
    return data_map

def start_string_obfuscation():
    """开始字符串混淆流程"""
    random_method_prefix = ''.join(random.choices(string.ascii_letters + string.ascii_letters, k=2)).lower()
    file_name = f'String+{random_method_prefix}Decryptor'
    aes_key = generate_aes_key() 

    # 处理字符串加密并获取映射关系
    data_map = process_strings_and_write_mapping(aes_key, project_path)

    #新建swift 文件
    creator = XcodeSwiftFileCreator(project_path,aes_key=aes_key,method_prefix=random_method_prefix)
    creator.create_swift_file(file_name, target_name)

    #替换
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.swift', '.m', '.h')):  
                
                file_path = os.path.join(root, file)

                if is_ignore_file(file_path):
                    continue

                print(f"正在读取文件 {file_path}...")

                ##方法
                if file.endswith(('.m', '.h')):
                    #oc 类暂未实现
                    continue
                elif file.endswith('.swift'):
                    with open(file_path, 'r+') as f:
                        content = f.read()
                        for de_str, en_str in data_map.items():
                            # content = content.replace(de_str, en_str)
                            content = re.sub(f'"{de_str}"', f'"{en_str}".{random_method_prefix}_decrypt()', content)

                    with open(file_path, 'w') as f:
                        f.write(content)

if __name__ == '__main__':
    main_collect_str_all()
    start_string_obfuscation()

                        
                    
