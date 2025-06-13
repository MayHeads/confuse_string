import sys
import os
import random
import string
import re
import json
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info
from config import asset_prefix
from ios_string_generate.string_gen import init_word_lists, get_random_snake_name


def random_name(prefix="tl", length=6):
    # 确保词库已初始化
    if not init_word_lists():
        # 如果初始化失败，使用原来的随机生成方式作为后备
        return prefix + '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    # 使用string_gen中的下划线命名生成器
    snake_name = get_random_snake_name()
    if snake_name:
        return prefix + '_' + snake_name
    
    # 如果生成失败，使用原来的随机生成方式作为后备
    return prefix + '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def find_imagesets(assets_path):
    result = []
    for root, dirs, files in os.walk(assets_path):
        for d in dirs:
            if d.endswith('.imageset'):
                result.append(os.path.join(root, d))
    return result

def rename_imageset(imageset_path, new_name):
    parent = os.path.dirname(imageset_path)
    new_path = os.path.join(parent, new_name + ".imageset")
    os.rename(imageset_path, new_path)
    return new_path

def replace_in_file(file_path, old, new):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    content_new = re.sub(rf"\b{old}\b", new, content)
    # 驼峰替换
    camel_old = ''.join([w.capitalize() for w in old.split('_')])
    camel_new = ''.join([w.capitalize() for w in new.split('_')])
    content_new = re.sub(rf"\b{camel_old}\b", camel_new, content_new)
    if content != content_new:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_new)

def process_imageset_pngs(imageset_path, new_name, log_file):
    # 获取所有PNG文件
    png_files = []
    for file in os.listdir(imageset_path):
        if file.endswith('.png'):
            png_files.append(file)
    
    if not png_files:
        return
    
    # 获取基础名称（不包含@2x, @3x等后缀）
    base_name = png_files[0].split('@')[0].replace('.png', '')
    
    # 写入日志
    log_message = f"{base_name} ----> {new_name}\n"
    log_file.write(log_message)
    
    # 重命名所有PNG文件
    for png_file in png_files:
        old_path = os.path.join(imageset_path, png_file)
        # 保持原有的@2x, @3x等后缀
        suffix = png_file[len(base_name):]
        new_png_name = f"{new_name}{suffix}"
        new_path = os.path.join(imageset_path, new_png_name)
        os.rename(old_path, new_path)
    
    # 更新Contents.json
    contents_path = os.path.join(imageset_path, 'Contents.json')
    if os.path.exists(contents_path):
        with open(contents_path, 'r', encoding='utf-8') as f:
            contents = json.load(f)
        
        # 更新images数组中的filename
        if 'images' in contents:
            for image in contents['images']:
                if 'filename' in image:
                    old_filename = image['filename']
                    if old_filename:
                        # 保持原有的@2x, @3x等后缀
                        suffix = old_filename[len(base_name):]
                        image['filename'] = f"{new_name}{suffix}"
        
        # 写回文件
        with open(contents_path, 'w', encoding='utf-8') as f:
            json.dump(contents, f, indent=2)

def refactor_assets(project_info, prefix="tl"):
    # 创建或清空日志文件
    with open("ios_log/asset_change_name.txt", "w", encoding="utf-8") as asset_log_file, \
         open("ios_log/imagename.txt", "w", encoding="utf-8") as image_log_file:
        # 1. 遍历所有assets
        for assets_path in project_info.xcassets_paths:
            # 2. 找到所有.imageset
            imagesets = find_imagesets(assets_path)
            for imageset in imagesets:
                old_name = os.path.basename(imageset).replace('.imageset', '')
                new_name = random_name(prefix)
                new_imageset_path = rename_imageset(imageset, new_name)
                log_message = f"{old_name} ----> {new_name}\n"
                asset_log_file.write(log_message)

                # 处理imageset中的PNG文件和Contents.json
                process_imageset_pngs(new_imageset_path, new_name, image_log_file)

                # 4. 替换所有swift文件
                def process_swift(swift_file):
                    replace_in_file(swift_file, old_name, new_name)
                with ThreadPoolExecutor() as executor:
                    executor.map(process_swift, project_info.swift_files)
def entry_change_name():
    project_info = get_project_info()
    refactor_assets(project_info, prefix=asset_prefix)  # prefix可自定义


if __name__ == "__main__":
    entry_change_name()