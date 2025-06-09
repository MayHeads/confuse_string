from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import numpy as np
import random
import hashlib
import os
from skimage import color, segmentation, measure
import cv2
import matplotlib.pyplot as plt

def modify_image(input_path, output_path, text_color=None, object_color_shift=None, add_icon=None):
    """
    修改图片使其视觉和谐但不同于原图
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        text_color: 要修改的文字颜色 (RGB元组)
        object_color_shift: 物体颜色偏移量 (Hue偏移)
        add_icon: 要添加的小图标路径
    """
    # 1. 读取原始图片
    original = Image.open(input_path)
    img = original.copy()
    
    # 2. 计算原始MD5
    original_md5 = hashlib.md5(open(input_path, 'rb').read()).hexdigest()
    
    # 3. 颜色调整策略
    # 转换到HSV空间进行颜色操作
    hsv_img = img.convert('HSV')
    h, s, v = hsv_img.split()
    h_array = np.array(h)
    
    # 3.1 文字颜色修改（如果指定了文字颜色）
    if text_color:
        # 转换为HSV空间的目标颜色
        target_hsv = color.rgb2hsv(np.array([text_color]) / 255.0)[0]
        target_h = int(target_hsv[0] * 255)
        
        # 检测文字区域（简化版，实际应用可用OCR）
        # 这里使用边缘检测作为示例
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # 查找轮廓（假设文字区域是密集的小轮廓）
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 创建文字区域掩码
        text_mask = np.zeros_like(gray)
        for cnt in contours:
            if 50 < cv2.contourArea(cnt) < 5000:  # 过滤太大太小的区域
                cv2.drawContours(text_mask, [cnt], -1, 255, -1)
        
        # 应用颜色修改
        for y in range(h_array.shape[0]):
            for x in range(h_array.shape[1]):
                if text_mask[y, x] > 128:
                    h_array[y, x] = target_h
    
    # 3.2 物体颜色偏移
    if object_color_shift:
        # 使用超像素分割找到物体区域
        segments = segmentation.slic(
            np.array(img), 
            n_segments=100, 
            compactness=10
        )
        
        # 随机选择几个区域修改颜色
        num_regions = np.max(segments) + 1
        regions_to_modify = random.sample(range(num_regions), min(5, num_regions))
        
        for region_id in regions_to_modify:
            mask = (segments == region_id)
            # 应用Hue偏移
            h_array[mask] = (h_array[mask] + int(object_color_shift * 255)) % 256
    
    # 4. 合并修改后的通道
    modified_h = Image.fromarray(h_array)
    modified_hsv = Image.merge('HSV', (modified_h, s, v))
    img = modified_hsv.convert('RGB')
    
    # 5. 添加小图标
    if add_icon and os.path.exists(add_icon):
        icon = Image.open(add_icon)
        # 调整图标大小（固定2x2像素）
        icon_size = (2, 2)
        icon = icon.resize(icon_size, Image.LANCZOS)
        
        # 检查原图是否有透明度
        has_transparency = original.mode in ('RGBA', 'LA') or 'transparency' in original.info
        
        if has_transparency:
            # 如果有透明度，转换为RGBA来检测
            temp_img = original.convert('RGBA')
            
            # 找到一个不透明的位置
            max_attempts = 100
            position = None
            
            for attempt in range(max_attempts):
                x = random.randint(20, img.width - icon.width - 20)
                y = random.randint(20, img.height - icon.height - 20)
                
                # 检查这个位置的alpha值
                pixel = temp_img.getpixel((x, y))
                if len(pixel) == 4 and pixel[3] > 200:  # alpha值足够高（不透明）
                    position = (x, y)
                    break
            
            # 如果找不到合适位置，使用中心区域
            if position is None:
                position = (img.width//2, img.height//2)
        else:
            # 没有透明度的图片，正常随机位置
            margin = 20
            position = (
                random.randint(margin, img.width - icon.width - margin),
                random.randint(margin, img.height - icon.height - margin)
            )
        
        # 创建半透明蒙版（随机透明度）
        alpha = random.uniform(0.3, 0.7)
        mask = Image.new('L', icon.size, int(255 * alpha))
        
        img.paste(icon, position, mask)
    
    # 6. 应用细微全局变化（使图片和谐但有区别）
    # 6.1 轻微色彩调整
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(random.uniform(0.95, 1.05))
    
    # 6.2 轻微亮度调整
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.98, 1.02))
    
    # 6.3 添加微小噪点（几乎不可见）
    # 保持原图的透明度信息
    if original.mode in ('RGBA', 'LA') or 'transparency' in original.info:
        # 对于有透明度的图片，只在不透明区域添加噪点
        original_rgba = original.convert('RGBA')
        img_rgba = img.convert('RGBA')
        np_img = np.array(img_rgba)
        original_alpha = np.array(original_rgba)[:,:,3]
        
        # 只在不透明区域添加噪点
        noise = np.random.normal(0, 1.5, np_img.shape).astype(np.uint8)
        
        # 创建掩码，只在alpha > 200的区域应用噪点
        alpha_mask = original_alpha > 200
        for i in range(3):  # RGB通道
            np_img[:,:,i] = np.where(alpha_mask, 
                                   np.clip(np_img[:,:,i] + noise[:,:,i], 0, 255),
                                   np_img[:,:,i])
        
        # 保持原始alpha通道
        np_img[:,:,3] = original_alpha
        img = Image.fromarray(np_img, 'RGBA')
        
        # 如果原图是RGB模式，转换回RGB
        if original.mode == 'RGB':
            img = img.convert('RGB')
    else:
        # 普通RGB图片的噪点处理
        np_img = np.array(img)
        noise = np.random.normal(0, 1.5, np_img.shape).astype(np.uint8)
        np_img = np.clip(np_img + noise, 0, 255)
        img = Image.fromarray(np_img)
    
    # 7. 保存结果
    img.save(output_path)
    
    # 8. 计算新MD5
    new_md5 = hashlib.md5(open(output_path, 'rb').read()).hexdigest()
    
    print(f"原始MD5: {original_md5}")
    print(f"新MD5: {new_md5}")
    print(f"修改后的图片已保存至: {output_path}")
    
    # 返回修改前后的图片用于比较
    return original, img

# 使用示例
if __name__ == "__main__":
    input_image = "/Users/jiangshanchen/confuse_string/inputImage/tag_scaning_bg@3x.png"
    output_image = "/Users/jiangshanchen/confuse_string/outputImage/modified_example.png"
    
    # 修改参数（可选）：
    # text_color - 要修改的文字颜色 (R, G, B)
    # object_color_shift - 物体颜色偏移量 (0-1.0)
    # add_icon - 要添加的小图标路径
    
    original, modified = modify_image(
        input_image,
        output_image,
        text_color=(50, 100, 200),  # 蓝色文字
        object_color_shift=0.1,      # 10% 色调偏移
        add_icon="/Users/jiangshanchen/confuse_string/icoImage/Ellipse 95@3x.png"    # 添加小图标
    )
    
    # 显示结果对比
    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.imshow(original)
    plt.title("Original Image")
    plt.axis('off')
    
    plt.subplot(122)
    plt.imshow(modified)
    plt.title("Modified Image")
    plt.axis('off')
    
    plt.show()