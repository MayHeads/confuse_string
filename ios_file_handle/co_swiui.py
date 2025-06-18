# 1. 收集 gen_file_swiftui 文件夹中的 Swift 文件名
# 2. 替换图片名称

import os
import sys
import random
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_random_image_name():
    """从 gener_imageset.txt 中随机获取一个图片名称"""
    # 使用正确的相对路径，包含 ios_log 目录
    image_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "ios_log", "gener_imageset.txt")
    try:
        with open(image_file_path, 'r', encoding='utf-8') as f:
            image_names = [line.strip() for line in f if line.strip()]
            if image_names:
                print(f"找到图片名称列表: {image_names}")
                return random.choice(image_names)
    except FileNotFoundError:
        print(f"未找到图片名称文件: {image_file_path}")
    
    # 如果没有文件或文件为空，生成随机名称
    random_name = f"image_{random.randint(1000, 9999)}"
    print(f"生成随机图片名称: {random_name}")
    return random_name

def collect_swift_files():
    """收集 gen_file_swiftui 文件夹中的 Swift 文件名"""
    swift_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "ios_resource", "gen_file_swiftui")
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "ios_log", "co_swiui_name.txt")
    
    # 获取所有 .swift 文件，并去掉后缀
    swift_files = [f[:-6] for f in os.listdir(swift_dir) if f.endswith('.swift')]
    
    # 写入文件名到输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for file_name in swift_files:
            f.write(f"{file_name}\n")
    
    # 返回带后缀的文件名列表（用于后续处理）和目录
    return [f + '.swift' for f in swift_files], swift_dir

def replace_image_names(swift_files, swift_dir):
    """替换 Swift 文件中的图片名称"""
    image_pattern = r'Image\("([^"]+)"\)'
    
    for file_name in swift_files:
        file_path = os.path.join(swift_dir, file_name)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换所有图片名称
        def replace_match(match):
            return f'Image("{get_random_image_name()}")'
        
        new_content = re.sub(image_pattern, replace_match, content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

def collect_swiftui_name():
    # 1. 收集 Swift 文件名
    swift_files, swift_dir = collect_swift_files()
    print(f"已收集 {len(swift_files)} 个 Swift 文件名到 co_swiui_name.txt")
    
    # 2. 替换图片名称
    replace_image_names(swift_files, swift_dir)
    print("已完成图片名称替换")

if __name__ == "__main__":
    collect_swiftui_name()



