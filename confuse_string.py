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

########### 项目配置 ###########

#工程中pod：  添加 pod 'CryptoSwift'
#python环境： pip3 install pbxproj
#/Users/xmiles/Documents/Project/CloudTuiQing
project_path = "/Users/jiangshanchen/confuse_string/ConfuseDemo1"
target_name = "ConfuseDemo1"



# project_path = "/Users/jiangshanchen/CloudTuiQing"
# target_name = "CloudTuiQing"

IGNORE_DIRECTORY = [
    "Pods",
    "du.xcframework",
    "du.framework",
    "Flutter",
    "CloudWidget",
]

print(f'os.getcwd() = {os.getcwd()}')

########### 项目配置 ###########


def _add_swift_file_to_project(file_path, project_path):
    """将文件添加到Xcode项目中"""
    try:
        # 加载项目文件
        project = XcodeProject.load(os.path.join(project_path, f"{target_name}.xcodeproj/project.pbxproj"))
        
        # 添加文件到项目
        project.add_file(file_path, force=False)
        
        # 保存项目
        project.save()
        print(f"成功将文件添加到项目中: {file_path}")
        return True
    except Exception as e:
        print(f"添加文件到项目时出错: {str(e)}")
        return False


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
            print('--------------------------------')
            print(f'swift_content = {swift_content}')
            print('--------------------------------')

            # 创建文件
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(swift_content)

            # 将文件添加到项目中
            # self._add_file_to_project(file_name, target_name)

            _add_swift_file_to_project(file_path, project_path)

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


def extract_strings_from_swift_files(project_path: str) -> list:
    """
    从项目中所有Swift文件提取字符串字面量
    返回去重后的字符串列表
    """
    print("🔍 开始扫描项目中的Swift文件...")
    
    all_strings = set()  # 使用set自动去重
    processed_files = 0
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.swift'):
                file_path = os.path.join(root, file)
                
                # 跳过忽略的目录
                if is_ignore_file(file_path):
                    continue
                
                # 跳过可能的解密文件（避免提取已加密的字符串）
                if 'Decryptor' in file:
                    print(f"  跳过解密文件: {file}")
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        print(f"  正在处理文件: {file}")
                        
                        # 使用更强大的正则表达式匹配字符串字面量
                        # 匹配双引号包围的字符串，支持转义字符，处理复杂嵌套情况
                        string_pattern = r'"(?:[^"\\\\]|\\\\.)*"'
                        matches = list(re.finditer(string_pattern, content))
                        
                        print(f"    在 {file} 中找到 {len(matches)} 个字符串字面量")
                        
                        file_string_count = 0
                        # 更精确的字符串提取
                        for i, match in enumerate(matches):
                            full_match = match.group(0)  # 包含引号的完整匹配
                            string_content = full_match[1:-1]  # 去掉首尾引号
                            
                            # 显示上下文信息，帮助调试
                            start_pos = max(0, match.start() - 20)
                            end_pos = min(len(content), match.end() + 20)
                            context = content[start_pos:end_pos].replace('\n', '\\n')
                            
                            print(f"    [{i+1}] 找到字符串: \"{string_content}\"")
                            print(f"        上下文: ...{context}...")
                            
                            # 过滤条件检查，添加详细的调试信息
                            should_include = True
                            filter_reason = ""
                            
                            if len(string_content) == 0:
                                should_include = False
                                filter_reason = "空字符串"
                            elif len(string_content) >= 100:
                                should_include = False
                                filter_reason = "字符串太长"
                            elif (re.match(r'^[A-Za-z0-9+/]*={0,2}$', string_content) and 
                                  len(string_content) > 15 and 
                                  len(string_content) % 4 == 0 and
                                  '+' in string_content or '/' in string_content or '=' in string_content):
                                should_include = False
                                filter_reason = "可能是base64编码"
                            elif string_content.startswith('http'):
                                should_include = False
                                filter_reason = "URL链接"
                            elif string_content.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                                should_include = False
                                filter_reason = "图片文件名"
                            elif re.match(r'^#[0-9A-Fa-f]{6}$', string_content):
                                should_include = False
                                filter_reason = "颜色值"
                            elif re.match(r'^\d{4}-\d{2}-\d{2}', string_content):
                                should_include = False
                                filter_reason = "日期格式"
                            elif string_content in ['true', 'false', 'nil', 'null']:
                                should_include = False
                                filter_reason = "布尔值或空值"
                            
                            if should_include:
                                all_strings.add(string_content)
                                file_string_count += 1
                                print(f"        ✅ 添加到待混淆列表")
                            else:
                                print(f"        ❌ 过滤掉 (原因: {filter_reason})")
                                
                        print(f"    从 {file} 中提取了 {file_string_count} 个有效字符串")
                        processed_files += 1
                        
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {str(e)}")
                    continue
    
    # 转换为列表并排序
    string_list = sorted(list(all_strings))
    
    print(f"✅ 扫描完成! 从 {processed_files} 个Swift文件中提取到 {len(string_list)} 个唯一字符串")
    
    # 显示一些示例
    if string_list:
        print("📝 提取到的字符串示例:")
        for i, s in enumerate(string_list[:10]):  # 显示前10个
            print(f"  {i+1}. \"{s}\"")
        if len(string_list) > 10:
            print(f"  ... 还有 {len(string_list) - 10} 个字符串")
    
    return string_list


if __name__ == '__main__':


    data_map = {}

    random_method_prefix = ''.join(random.choices(string.ascii_letters + string.ascii_letters, k=2)).lower()
    file_name = f'String+{random_method_prefix}Decryptor'

    aes_key = generate_aes_key() 
    
    # 清空日志文件
    with open(f'{os.getcwd()}/confuse_string_log.txt', 'r+') as log_file:
        log_file.truncate(0)

    # 从项目Swift文件中提取字符串，而不是读取strings.txt
    print("🚀 开始从项目中提取字符串...")
    extracted_strings = extract_strings_from_swift_files(project_path)
    
    if not extracted_strings:
        print("❌ 没有找到可以混淆的字符串，程序退出")
        exit(1)

    print(f"🔐 开始加密 {len(extracted_strings)} 个字符串...")
    
    strings = []
    for line in extracted_strings:
        en_str = rw_encrypt(aes_key, line)
        de_str = rw_decrypt(aes_key, en_str)

        if line == de_str:
            print(f"{de_str} <-----> {en_str}")
            strings.append(f"{de_str} <-----------> {en_str}")
            data_map[de_str] = en_str

    #映射日志
    with open(f'{os.getcwd()}/confuse_string_log.txt', 'r+') as f: 
        f.write("👉👉👉👉👉string Obfuscation Map List👈👈👈👈👈" + '\n\n\n')
        for string in strings:
            f.write(string + '\n')

    local_map_file = project_path + 'confuse_string' + '/confuse_string_log.txt'
    os.makedirs(os.path.dirname(local_map_file), exist_ok=True)
    with open(local_map_file, 'w', encoding='utf-8') as f:
        f.write("👉👉👉👉👉string Obfuscation Map List👈👈👈👈👈" + '\n\n\n')
        for string in strings:
            f.write(string + '\n')

    #新建swift 文件
    creator = XcodeSwiftFileCreator(project_path,aes_key=aes_key,method_prefix=random_method_prefix)
    decryptor_file_name = f'String+{random_method_prefix}Decryptor.swift'
    creator.create_swift_file(file_name, target_name)

    
    
    #替换
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.swift', '.m', '.h')):  
                
                file_path = os.path.join(root, file)

                if is_ignore_file(file_path):
                    continue

                # 跳过新创建的解密文件，避免对解密文件本身进行混淆
                if file == decryptor_file_name:
                    print(f"跳过解密文件: {file}")
                    continue

                print(f"正在读取文件 {file_path}...")

                ##方法
                if file.endswith(('.m', '.h')):
                    #oc 类暂未实现
                    continue
                elif file.endswith('.swift'):
                    with open(file_path, 'r+') as f:
                        content = f.read()
                        original_content = content  # 保存原始内容用于比较
                        
                        # 按行处理，跳过已经包含解密方法的行
                        lines = content.split('\n')
                        processed_lines = []
                        
                        for line in lines:
                            # 如果这行已经包含解密方法调用，直接跳过
                            if re.search(r'\.[a-zA-Z_]+_decrypt\(\)', line):
                                processed_lines.append(line)
                                continue
                                
                            # 处理当前行
                            processed_line = line
                            for de_str, en_str in data_map.items():
                                # 转义特殊字符，避免正则表达式错误
                                escaped_de_str = re.escape(de_str)
                                
                                # 改进的正则表达式：匹配双引号字符串，但排除已经有解密方法调用的情况
                                # 负向后行断言确保字符串后面没有跟解密方法
                                # 同时确保引号前后的字符保持原样（包括逗号、括号等）
                                pattern1 = f'("{escaped_de_str}")(?!\\.\\w+_decrypt\\(\\))'
                                replacement1 = f'"{en_str}".{random_method_prefix}_decrypt()'
                                
                                # 更严格的部分匹配：确保不匹配已经加密的字符串
                                # 使用负向前行断言和负向后行断言
                                pattern2 = f'(?<!\\\\)"([^"]*{escaped_de_str}[^"]*)"(?!\\.\\w+_decrypt\\(\\))'
                                
                                # 先尝试精确匹配
                                matches = list(re.finditer(pattern1, processed_line))
                                if matches:
                                    # 从后往前替换，避免索引变化影响
                                    for match in reversed(matches):
                                        start, end = match.span()
                                        # 保持引号外的字符不变
                                        processed_line = processed_line[:start] + replacement1 + processed_line[end:]
                                    print(f"  ✅ 在 {file} 中找到并替换了: {de_str}")
                                
                                # 如果精确匹配没找到，尝试部分匹配（字符串包含目标文本）
                                elif re.search(pattern2, processed_line):
                                    def replace_partial(match):
                                        full_string = match.group(1)
                                        if de_str in full_string:
                                            # 检查这个完整字符串是否已经是加密过的（通常加密字符串是base64格式）
                                            # 如果字符串看起来像base64且长度较长，跳过处理
                                            if len(full_string) > 20 and re.match(r'^[A-Za-z0-9+/]*={0,2}$', full_string):
                                                return match.group(0)  # 不处理，返回原字符串
                                            
                                            # 只替换包含目标字符串的完整字符串
                                            encrypted_full = rw_encrypt(aes_key, full_string)
                                            return f'"{encrypted_full}".{random_method_prefix}_decrypt()'
                                        return match.group(0)
                                    
                                    processed_line = re.sub(pattern2, replace_partial, processed_line)
                                    print(f"  ✅ 在 {file} 中找到并部分替换了包含: {de_str}")
                            
                            processed_lines.append(processed_line)
                        
                        # 重新组合内容
                        content = '\n'.join(processed_lines)
                        
                        # 只有当内容真的改变了才写入文件
                        if content != original_content:
                            print(f"  📝 更新文件: {file}")
                        else:
                            print(f"  ⏭️  跳过文件（无匹配）: {file}")

                    with open(file_path, 'w') as f:
                        f.write(content)

                        
                    
