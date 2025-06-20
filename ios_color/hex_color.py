import os
import sys
import re
import random
import colorsys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_scanner import get_project_info


def extract_hex_colors(swift_files):
    """
    从Swift文件中提取16进制颜色代码
    例如: #808080, #FFFFFF 等格式
    
    参数:
        swift_files: Swift文件路径列表
    
    返回:
        set: 不重复的16进制颜色代码集合
    """
    # 16进制颜色代码的正则表达式模式 (#开头,后跟6位16进制字符)
    hex_color_pattern = r'#[0-9A-Fa-f]{6}\b'
    hex_colors = set()
    
    for swift_file in swift_files:
        try:
            with open(swift_file, 'r', encoding='utf-8') as file:
                content = file.read()
                # 查找所有16进制颜色代码
                matches = re.findall(hex_color_pattern, content)
                # 添加到结果集合
                hex_colors.update(matches)
        except Exception as e:
            print(f"处理文件 {swift_file} 时出错: {e}")
    
    return hex_colors


def save_hex_colors_to_file(hex_colors, output_file):
    """
    将16进制颜色代码保存到文本文件中
    
    参数:
        hex_colors: 16进制颜色代码集合
        output_file: 输出文件路径
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 按字母顺序排序颜色代码
    sorted_colors = sorted(list(hex_colors))
    
    # 写入文件，每行一个颜色代码
    with open(output_file, 'w', encoding='utf-8') as file:
        for color in sorted_colors:
            file.write(f"{color}\n")
    
    # 同时写入到hex_color_map.txt，格式为"原始颜色 --- 随机生成颜色"
    map_file = os.path.join(os.path.dirname(output_file), 'hex_color_map.txt')
    with open(map_file, 'w', encoding='utf-8') as file:
        for color in sorted_colors:
            # 生成映射颜色
            mapped_color = generate_mapped_color(color)
            # 写入文件
            file.write(f"{color} --- {mapped_color}\n")
    
    print(f"找到 {len(sorted_colors)} 个16进制颜色代码")
    print(f"- 原始列表已保存至: {output_file}")
    print(f"- 颜色映射已保存至: {map_file}")


def is_grayscale(hex_color):
    """
    判断一个颜色是否是灰色（R=G=B或非常接近）
    
    参数:
        hex_color: 16进制颜色代码，如 #808080
        
    返回:
        bool: 是否为灰色
    """
    # 提取RGB值
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    
    # 判断RGB值是否接近（灰度容差）
    tolerance = 10
    return (abs(r - g) <= tolerance and 
            abs(r - b) <= tolerance and 
            abs(g - b) <= tolerance)


def is_light_color(hex_color):
    """
    判断颜色是浅色还是深色
    
    参数:
        hex_color: 16进制颜色代码
        
    返回:
        bool: 如果是浅色返回True，深色返回False
    """
    # 提取RGB值
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    
    # 计算亮度 (简化版本)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    # 亮度阈值
    return brightness > 127


def generate_similar_grayscale(hex_color):
    """
    生成一个与给定灰度颜色相似但不同的灰度颜色
    
    参数:
        hex_color: 16进制灰度颜色代码
    
    返回:
        str: 新的灰度颜色代码
    """
    # 提取灰度值 (取R值，因为灰度RGB值相近)
    gray_value = int(hex_color[1:3], 16)
    
    # 决定是变亮还是变暗
    if is_light_color(hex_color):
        # 如果是浅色，变暗一点
        new_gray = max(0, gray_value - random.randint(30, 70))
    else:
        # 如果是深色，变亮一点
        new_gray = min(255, gray_value + random.randint(30, 70))
    
    # 转回16进制格式
    new_hex = f"#{new_gray:02x}{new_gray:02x}{new_gray:02x}"
    return new_hex


def generate_different_color(hex_color):
    """
    为给定颜色生成一个不同色系的颜色
    
    参数:
        hex_color: 16进制颜色代码
    
    返回:
        str: 新的颜色代码
    """
    # 提取RGB值
    r = int(hex_color[1:3], 16) / 255.0
    g = int(hex_color[3:5], 16) / 255.0
    b = int(hex_color[5:7], 16) / 255.0
    
    # 转换为HSV (色调、饱和度、明度)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # 改变色调 (0-1范围内)
    h = (h + random.uniform(0.2, 0.8)) % 1.0
    
    # 稍微调整饱和度和明度，但保持在合理范围内
    s = min(1.0, max(0.3, s + random.uniform(-0.2, 0.2)))
    v = min(1.0, max(0.3, v + random.uniform(-0.2, 0.2)))
    
    # 转回RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    # 转为16进制
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def generate_mapped_color(hex_color):
    """
    为给定颜色生成一个对应的映射颜色
    
    参数:
        hex_color: 原始16进制颜色代码
        
    返回:
        str: 映射后的16进制颜色代码
    """
    # 检查是否是灰度
    if is_grayscale(hex_color):
        return generate_similar_grayscale(hex_color)
    else:
        return generate_different_color(hex_color)
    

def color_hanlde():
    # 获取项目信息
    project_info = get_project_info()
    all_swift_files = project_info.all_swift_files
    print(f"Total Swift files: {len(all_swift_files)}")
    
    # 输出文件路径
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               'ios_log', 'hex_color.txt')
    
    # 提取16进制颜色代码
    hex_colors = extract_hex_colors(all_swift_files)
    
    # 保存结果到文件
    save_hex_colors_to_file(hex_colors, output_file)
  


def replace_colors():
    """
    读取颜色映射文件，并替换所有Swift文件中的颜色值
    使用多线程提高处理效率
    """
    # 获取项目信息
    project_info = get_project_info()
    all_swift_files = project_info.all_swift_files
    print(f"准备处理 {len(all_swift_files)} 个Swift文件")
    
    # 读取颜色映射文件
    map_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'ios_log', 'hex_color_map.txt')
    
    # 解析颜色映射
    color_map = {}
    try:
        with open(map_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if ' --- ' in line:
                    parts = line.split(' --- ')
                    if len(parts) == 2:
                        original_color = parts[0].strip()
                        mapped_color = parts[1].strip()
                        color_map[original_color] = mapped_color
        
        print(f"读取到 {len(color_map)} 个颜色映射关系")
        
        if not color_map:
            print("没有找到颜色映射数据，请先运行color_hanlde()方法生成映射")
            return
        
    except Exception as e:
        print(f"读取颜色映射文件时出错: {e}")
        return
    
    # 定义替换函数
    def replace_colors_in_file(swift_file):
        try:
            # 读取文件内容
            with open(swift_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 跟踪是否有修改
            modified = False
            
            # 替换颜色值
            for original_color, mapped_color in color_map.items():
                if original_color in content:
                    content = content.replace(original_color, mapped_color)
                    modified = True
            
            # 如果有修改，写回文件
            if modified:
                with open(swift_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                return swift_file
            
            return None
            
        except Exception as e:
            print(f"处理文件 {swift_file} 时出错: {e}")
            return None
    
    # 使用多线程处理文件
    import concurrent.futures
    import threading
    
    # 创建一个锁，用于同步输出
    print_lock = threading.Lock()
    
    # 计数器
    replaced_files = []
    
    # 使用线程池执行任务
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, os.cpu_count() * 2)) as executor:
        # 提交所有任务
        future_to_file = {executor.submit(replace_colors_in_file, file): file for file in all_swift_files}
        
        # 处理结果
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                if result:
                    replaced_files.append(result)
                    with print_lock:
                        print(f"已替换颜色: {os.path.basename(result)}")
            except Exception as e:
                with print_lock:
                    print(f"处理 {os.path.basename(file)} 时出错: {e}")
    
    print(f"\n处理完成: 替换了 {len(replaced_files)} 个文件中的颜色值")
    print(f"原始文件数量: {len(all_swift_files)}")
    
    return replaced_files

def z_color_combin():
    color_hanlde()
    replace_colors()


if __name__=='__main__':
    z_color_combin()
    # # 提取项目中的颜色代码并生成映射
    # color_hanlde()
    
    # # 询问用户是否要替换颜色
    # user_input = input("\n是否要替换Swift文件中的颜色代码? (y/n): ")
    # if user_input.lower() in ['y', 'yes']:
    #     # 替换所有颜色
    #     replace_colors()
    # else:
    #     print("跳过颜色替换操作")