# 通用函数：替换 readme_file 中的字符串
import os
import re
from project_scanner import get_project_info

def replace_strings_in_readme_file(replace_map):
    """
    替换 readme_file (README1.md) 中所有匹配的字符串
    Args:
        replace_map: 字符串映射字典 {old_str: new_str}
    Returns:
        bool: 是否成功替换
    """
    if not replace_map:
        return False
    
    project_info = get_project_info()
    if not project_info:
        return False
    
    readme_file = project_info.readme_file
    if not readme_file or not os.path.exists(readme_file):
        return False
    
    try:
        # 尝试不同的编码方式读取文件
        encodings = ['utf-8', 'utf-16', 'ascii', 'latin1', 'gbk', 'gb2312']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(readme_file, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                used_encoding = encoding
                break
            except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                continue
        
        if content is None:
            print(f"无法读取 readme_file: {readme_file}")
            return False
        
        # 替换所有匹配的字符串（不使用单词边界，因为 md 文件中可能有各种格式）
        modified = False
        replacement_details = []
        
        for old_str, new_str in replace_map.items():
            # 对于 md 文件，使用简单的字符串替换（不使用单词边界）
            if old_str in content:
                count = content.count(old_str)
                content = content.replace(old_str, new_str)
                modified = True
                replacement_details.append(f"{old_str} -> {new_str} (替换 {count} 次)")
        
        if modified:
            # 写回文件
            try:
                with open(readme_file, 'w', encoding=used_encoding, errors='ignore') as f:
                    f.write(content)
                print(f"✓ 已更新 readme_file: {readme_file}")
                for detail in replacement_details:
                    print(f"    {detail}")
                return True
            except Exception as e:
                print(f"✗ 写入 readme_file {readme_file} 时出错: {str(e)}")
                return False
        
        return False
        
    except Exception as e:
        print(f"处理 readme_file {readme_file} 时出错: {str(e)}")
        return False

