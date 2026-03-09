import os
import sys
import random
import requests
import json
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info
from ios_string_generate.string_gen import get_random_method_name, get_random_snake_name
from config import ASSET_IMAGE_CONFIG

# 配置参数
IMAGE_CONFIG = ASSET_IMAGE_CONFIG

def write_log(image_name):
    """
    将生成的图片名称写入日志文件
    """
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(root_dir, 'ios_log')
    
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志文件路径
    log_file = os.path.join(log_dir, 'gener_imageset.txt')
    
    # 写入日志，只记录图片名称
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{image_name}\n")


def download_image(image_name, folder_path, timeout=10):
    """
    从 picsum.photos 下载随机图片并保存为 PNG
    """
    # 随机生成图片尺寸
    width = random.randint(*IMAGE_CONFIG['width_range'])
    height = random.randint(*IMAGE_CONFIG['height_range'])
    
    # 随机生成模糊程度
    blur_amount = random.randint(*IMAGE_CONFIG['blur_range'])
    
    # 构建图片URL，添加模糊效果
    image_url = f"https://picsum.photos/{width}/{height}?blur={blur_amount}"
    
    try:
        # 下载图片，添加超时设置
        response = requests.get(image_url, timeout=timeout)
        response.raise_for_status()
        
        # 保存为PNG
        image_path = os.path.join(folder_path, f"{image_name}.png")
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        # 写入日志
        write_log(image_name)
        
        return True
    except requests.exceptions.Timeout:
        print(f"⚠️  下载图片超时: {image_name}")
        return False
    except Exception as e:
        print(f"⚠️  下载图片出错 {image_name}: {e}")
        return False


def create_contents_json(image_name, folder_path):
    """
    创建 Contents.json 文件
    """
    contents = {
        "images": [
            {
                "idiom": "universal",
                "scale": "1x"
            },
            {
                "idiom": "universal",
                "scale": "2x"
            },
            {
                "filename": f"{image_name}.png",
                "idiom": "universal",
                "scale": "3x"
            }
        ],
        "info": {
            "author": "xcode",
            "version": 1
        }
    }
    
    contents_path = os.path.join(folder_path, "Contents.json")
    with open(contents_path, 'w') as f:
        json.dump(contents, f, indent=2)


def create_imageset_folder(parent_folder):
    """
    在指定文件夹中创建 imageset 文件夹并下载图片
    """
    # 获取随机方法名
    method_name = get_random_method_name()
    if not method_name:
        return False
    
    # 创建 imageset 文件夹
    imageset_name = f"{method_name}.imageset"
    imageset_path = os.path.join(parent_folder, imageset_name)
    
    try:
        os.makedirs(imageset_path, exist_ok=True)
        
        # 下载图片（添加超时处理）
        if download_image(method_name, imageset_path, timeout=15):
            # 创建 Contents.json
            create_contents_json(method_name, imageset_path)
            return True
        else:
            # 如果下载失败，清理已创建的文件夹
            try:
                if os.path.exists(imageset_path):
                    shutil.rmtree(imageset_path)
            except:
                pass
    except Exception as e:
        print(f"  ⚠️  创建 imageset 文件夹出错: {e}")
        # 清理已创建的文件夹
        try:
            if os.path.exists(imageset_path):
                shutil.rmtree(imageset_path)
        except:
            pass
    
    return False


def get_valid_asset_folders(root_path):
    """
    获取可以在其中创建新 imageset 的有效文件夹
    返回 .xcassets 目录本身，以及已存在 imageset 的父目录
    """
    valid_folders = set()
    
    # 首先添加 .xcassets 目录本身（这是最常用的位置）
    if os.path.exists(root_path) and os.path.isdir(root_path):
        valid_folders.add(root_path)
    
    # 查找已存在的 imageset，将其父目录也加入有效文件夹列表
    # 这样可以在已有 imageset 的同一层级创建新的 imageset
    for root, dirs, files in os.walk(root_path):
        # 快速过滤隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # 检查当前目录是否是 imageset（包含 Contents.json 且以 .imageset 结尾）
        if 'Contents.json' in files:
            dir_name = os.path.basename(root)
            if dir_name.endswith('.imageset'):
                # 添加 imageset 的父目录
                parent_dir = os.path.dirname(root)
                if parent_dir and os.path.exists(parent_dir):
                    valid_folders.add(parent_dir)
    
    return list(valid_folders)


def count_existing_imagesets(root_path):
    """
    统计现有的 imageset 数量
    """
    count = 0
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if 'Contents.json' in files:
            dir_name = os.path.basename(root)
            if dir_name.endswith('.imageset'):
                count += 1
    return count

def create_single_imageset(subfolder_path):
    """
    创建单个 imageset（用于多线程）
    """
    return create_imageset_folder(subfolder_path)

def create_subfolder_with_imagesets(parent_folder, num_imagesets, folder_name):
    """
    在父文件夹中创建子文件夹，并在其中创建指定数量的 imageset（使用多线程）
    """
    subfolder_path = os.path.join(parent_folder, folder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    
    # 使用线程池并行创建 imageset
    max_workers = min(10, num_imagesets)  # 最多10个线程
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(create_single_imageset, subfolder_path) for _ in range(num_imagesets)]
        
        # 获取结果并显示进度
        completed = 0
        for future in as_completed(futures):
            completed += 1
            try:
                if future.result():
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"  ⚠️  创建 imageset 时出错: {e}")
            
            # 显示进度
            print(f"  📥 [{folder_name}] 进度: {completed}/{num_imagesets} (成功: {success_count}, 失败: {failed_count})", end='\r')
    
    # 清除进度行并显示结果
    print(f"  ✅ [{folder_name}] 完成: {success_count}/{num_imagesets} 个 imageset 创建成功")
    
    return success_count

def process_folder(folder):
    """
    处理单个文件夹
    """
    num_imagesets = random.randint(*IMAGE_CONFIG['imageset_count_range'])
    success_count = 0
    
    for _ in range(num_imagesets):
        if create_imageset_folder(folder):
            success_count += 1
    
    return success_count


def asset_path():
    project_info = get_project_info()
    asset_path = project_info.xcassets_paths
    asset_one_path = asset_path[0]
    print(asset_one_path)
    return asset_one_path


def entry_gener_imageset():
    asset_root_path = asset_path()
    print("asset_root_path:---->")
    print(asset_root_path)
    
    # 统计现有的 imageset 数量
    existing_count = count_existing_imagesets(asset_root_path)
    print(f"📊 现有 imageset 数量: {existing_count}")
    
    # 如果图片数量少于10个，生成50-60个随机照片并拆分到不同文件夹
    if existing_count < 10:
        print(f"⚠️  图片数量较少（{existing_count}个），将生成50-60个新的 imageset 并拆分到不同文件夹")
        
        # 生成50-60个随机数量
        total_to_generate = random.randint(50, 60)
        print(f"🎯 目标生成数量: {total_to_generate} 个 imageset")
        
        # 创建多个子文件夹来分散 imageset（每个文件夹10-15个）
        imagesets_per_folder = random.randint(10, 15)
        num_folders = (total_to_generate + imagesets_per_folder - 1) // imagesets_per_folder  # 向上取整
        
        print(f"📁 将创建 {num_folders} 个子文件夹，每个文件夹约 {imagesets_per_folder} 个 imageset")
        print(f"🚀 使用多线程并行处理，加速生成...\n")
        
        # 准备所有文件夹任务
        folder_tasks = []
        remaining = total_to_generate
        
        for i in range(num_folders):
            # 生成子文件夹名称
            folder_name = get_random_method_name()
            if not folder_name:
                folder_name = f"AssetGroup{i+1}"
            
            # 计算这个文件夹要创建的 imageset 数量
            current_batch = min(imagesets_per_folder, remaining)
            folder_tasks.append((folder_name, current_batch))
            remaining -= current_batch
            
            if remaining <= 0:
                break
        
        # 使用线程池并行处理多个文件夹
        total_success = 0
        max_folder_workers = min(5, len(folder_tasks))  # 最多5个文件夹并行
        
        with ThreadPoolExecutor(max_workers=max_folder_workers) as executor:
            # 提交所有文件夹任务
            future_to_folder = {
                executor.submit(create_subfolder_with_imagesets, asset_root_path, num_imagesets, folder_name): (folder_name, num_imagesets)
                for folder_name, num_imagesets in folder_tasks
            }
            
            # 获取结果
            for future in as_completed(future_to_folder):
                folder_name, num_imagesets = future_to_folder[future]
                try:
                    success_count = future.result()
                    total_success += success_count
                except Exception as e:
                    print(f"  ❌ 处理文件夹 {folder_name} 时出错: {e}")
        
        print(f"\n✅ 总共创建了 {total_success} 个 imageset")
    else:
        # 原有逻辑：使用现有文件夹
        print(f"ℹ️  图片数量充足（{existing_count}个），使用原有逻辑")
        valid_folders = get_valid_asset_folders(asset_root_path)
        print("Valid asset folders:")
        for folder in valid_folders:
            print(folder)
        
        # 使用线程池并行处理文件夹
        total_success = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 提交所有任务
            future_to_folder = {executor.submit(process_folder, folder): folder for folder in valid_folders}
            
            # 获取结果
            for future in as_completed(future_to_folder):
                folder = future_to_folder[future]
                try:
                    success_count = future.result()
                    total_success += success_count
                    print(f"Processed {folder}: {success_count} imagesets created")
                except Exception as e:
                    print(f"Error processing {folder}: {e}")
        
        print(f"\nTotal imagesets created: {total_success}")


if __name__ == '__main__':
    entry_gener_imageset()
