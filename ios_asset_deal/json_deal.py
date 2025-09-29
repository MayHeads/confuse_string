import os
import sys
import random
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from ios_string_generate.string_gen import get_random_method_name, get_random_snake_name


def asset_path():
    project_info = get_project_info()
    asset_path = project_info.xcassets_paths
    asset_one_path = asset_path[0]
    print(asset_one_path)
    return asset_one_path


def find_contents_json_files(root_path):
    """
    递归遍历文件夹，找到所有Contents.json文件
    """
    contents_files = []
    
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file == "Contents.json":
                file_path = os.path.join(root, file)
                contents_files.append(file_path)
    
    return contents_files


def update_author_in_json(json_file_path):
    """
    更新JSON文件中的author字段
    支持根级别的author字段和info.author字段
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        new_author = get_random_method_name()
        
        if not new_author:
            print(f"❌ 无法生成随机方法名，跳过 {json_file_path}")
            return False
        
        # 检查根级别的author字段
        if 'author' in data:
            old_author = data['author']
            data['author'] = new_author
            updated = True
            print(f"✅ 已更新根级别author: {old_author} -> {new_author}")
        
        # 检查info.author字段
        if 'info' in data and isinstance(data['info'], dict) and 'author' in data['info']:
            old_author = data['info']['author']
            data['info']['author'] = new_author
            updated = True
            print(f"✅ 已更新info.author: {old_author} -> {new_author}")
        
        if updated:
            # 写回文件
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 已更新文件: {json_file_path}")
            return True
        else:
            print(f"ℹ️  {json_file_path} 中没有找到author字段，跳过")
            return False
            
    except Exception as e:
        print(f"❌ 处理文件 {json_file_path} 时出错: {str(e)}")
        return False


def process_all_contents_json():
    """
    处理指定路径下所有的Contents.json文件
    """
    print(f"🔍 开始扫描路径: {asset_path}")

    asset_path = asset_path()

    
    # 查找所有Contents.json文件
    contents_files = find_contents_json_files(asset_path)
    
    if not contents_files:
        print("❌ 未找到任何Contents.json文件")
        return
    
    print(f"📁 找到 {len(contents_files)} 个Contents.json文件:")
    for file_path in contents_files:
        print(f"   - {file_path}")
    
    print("\n🔄 开始处理文件...")
    
    success_count = 0
    total_count = len(contents_files)
    
    for json_file in contents_files:
        if update_author_in_json(json_file):
            success_count += 1
    
    print(f"\n📊 处理完成:")
    print(f"   总文件数: {total_count}")
    print(f"   成功处理: {success_count}")
    print(f"   跳过/失败: {total_count - success_count}")


if __name__ == "__main__":
    process_all_contents_json()