import os
import sys
import re
import random
import string
import concurrent.futures
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info

def generate_random_id():
    """生成24位的随机ID，由数字和大写字母组成"""
    chars = string.digits + string.ascii_uppercase
    return ''.join(random.choices(chars, k=24))

def process_pbx_file(pbx_path):
    """处理pbx文件，替换所有24位的ID"""
    # 读取文件内容
    with open(pbx_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配24位的ID
    pattern = r'[A-F0-9]{24}'
    matches = set(re.findall(pattern, content))
    
    if not matches:
        print("未找到需要替换的ID")
        return
    
    print(f"找到 {len(matches)} 个需要替换的ID")
    
    # 创建ID映射关系
    id_mapping = {old_id: generate_random_id() for old_id in matches}
    
    # 使用线程池进行替换
    def replace_ids(chunk):
        for old_id, new_id in id_mapping.items():
            chunk = chunk.replace(old_id, new_id)
        return chunk
    
    # 将文件内容分成多个块
    chunk_size = 1024 * 1024  # 1MB
    chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
    
    # 使用线程池处理替换
    with concurrent.futures.ThreadPoolExecutor() as executor:
        new_chunks = list(executor.map(replace_ids, chunks))
    
    # 合并处理后的内容
    new_content = ''.join(new_chunks)
    
    # 写入映射关系到日志文件
    log_dir = os.path.join(os.getcwd(), 'ios_log')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'pbx_id_mapping.txt')
    
    with open(log_file, 'w', encoding='utf-8') as f:
        for old_id, new_id in id_mapping.items():
            f.write(f"{old_id} -> {new_id}\n")
    
    # 备份原文件
    backup_path = pbx_path + '.backup'
    if not os.path.exists(backup_path):
        os.rename(pbx_path, backup_path)
    
    # 写入新内容
    with open(pbx_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"ID替换完成，映射关系已保存到: {log_file}")
    print(f"原文件已备份到: {backup_path}")

if __name__ == '__main__':
    project_info = get_project_info()
    pbx_path = project_info.xcodeproj_path
    
    pbx_file_name = pbx_path + '/project.pbxproj'
    # 检查文件是否已经处理过
    # if os.path.exists(pbx_file_name + '.backup'):
    #     print("文件已经处理过，请检查备份文件")
    #     sys.exit(1)
    
    # 处理pbx文件
    process_pbx_file(pbx_file_name)

