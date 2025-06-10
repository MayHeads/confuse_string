import sys
import os
import random
import string
import re
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info
from config import asset_prefix


def random_name(prefix="tl", length=6):
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

def refactor_assets(project_info, prefix="tl"):
    # 创建或清空日志文件
    with open("ios_log/assetlog.txt", "w", encoding="utf-8") as log_file:
        # 1. 遍历所有assets
        for assets_path in project_info.xcassets_paths:
            # 2. 找到所有.imageset
            imagesets = find_imagesets(assets_path)
            for imageset in imagesets:
                old_name = os.path.basename(imageset).replace('.imageset', '')
                new_name = random_name(prefix)
                new_imageset_path = rename_imageset(imageset, new_name)
                log_message = f"{old_name} ----> {new_name}\n"
                log_file.write(log_message)

                # 4. 替换所有swift文件
                def process_swift(swift_file):
                    replace_in_file(swift_file, old_name, new_name)
                with ThreadPoolExecutor() as executor:
                    executor.map(process_swift, project_info.swift_files)

if __name__ == "__main__":
    project_info = get_project_info()
    refactor_assets(project_info, prefix=asset_prefix)  # prefix可自定义