#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片自定义滤镜效果处理工具
使用Pillow库为图片添加可调节的自定义滤镜效果
"""

import os
import sys
from PIL import Image, ImageFilter, ImageEnhance
import argparse
from pathlib import Path

# ==================== 调试参数配置 ====================
# 方便调试时快速修改参数，无需修改代码内部
DEBUG_FOLDER_PATH = '/Users/jiangshanchen/TSComposs/TSComposs/Resource/Assets.xcassets'  # 要处理的文件夹路径
DEBUG_FILTER_TYPE = 'invert'        # 滤镜类型 ('red_black', 'sepia', 'vintage', 'high_contrast', 'invert', 'grayscale')
DEBUG_FILTER_STRENGTH = 1.5         # 滤镜强度 (0.1-3.0)
DEBUG_PRESERVE_TRANSPARENCY = True  # 是否保持透明区域不变
DEBUG_BACKUP = False                # 是否创建备份文件
DEBUG_RECURSIVE = True              # 是否递归查找子文件夹
DEBUG_QUALITY = 95                  # 输出图片质量 (1-100)
# =====================================================

class ImageFilterProcessor:
    """图片自定义滤镜处理器"""
    
    def __init__(self, folder_path):
        """
        初始化图片自定义滤镜处理器
        
        Args:
            folder_path (str): 要处理的文件夹路径
        """
        self.folder_path = Path(folder_path)
        
        # 支持的图片格式
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        
        # 确保文件夹存在
        if not self.folder_path.exists():
            raise FileNotFoundError(f"文件夹不存在: {self.folder_path}")
        if not self.folder_path.is_dir():
            raise NotADirectoryError(f"路径不是文件夹: {self.folder_path}")
    
    def get_image_files(self, recursive=True):
        """获取文件夹中的所有图片文件"""
        image_files = []
        
        if recursive:
            # 递归查找所有子文件夹中的图片
            for file_path in self.folder_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    image_files.append(file_path)
        else:
            # 只查找当前文件夹中的图片
            for file_path in self.folder_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    image_files.append(file_path)
        
        return image_files
    
    def apply_custom_filter(self, image_path, filter_type='red_black', filter_strength=1.0, 
                           preserve_transparency=True, backup=True):
        """
        对单张图片应用自定义滤镜效果
        
        Args:
            image_path (Path): 图片文件路径
            filter_type (str): 滤镜类型 ('red_black', 'sepia', 'vintage', 'high_contrast', 'invert', 'grayscale')
            filter_strength (float): 滤镜强度 (0.1-3.0)
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
        
        Returns:
            bool: 处理是否成功
        """
        try:
            # 创建备份文件（如果需要）
            backup_path = None
            if backup:
                backup_path = image_path.with_suffix(f'.backup{image_path.suffix}')
                try:
                    import shutil
                    shutil.copy2(image_path, backup_path)
                    print(f"  📁 已创建备份: {backup_path.name}")
                except Exception as e:
                    print(f"  ⚠️ 备份失败: {e}")
                    return False
            
            # 打开图片
            with Image.open(image_path) as img:
                # 保存原始模式
                original_mode = img.mode
                
                # 如果图片有透明通道且需要保持透明度
                if preserve_transparency and img.mode in ('RGBA', 'LA') or 'transparency' in img.info:
                    # 转换为RGBA模式以处理透明度
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # 分离RGB和Alpha通道
                    rgb_channels = img.split()[:3]  # R, G, B
                    alpha_channel = img.split()[3]  # Alpha
                    
                    # 将RGB通道合并为RGB图像进行滤镜处理
                    rgb_img = Image.merge('RGB', rgb_channels)
                    
                    # 应用自定义滤镜效果
                    filtered_rgb = self._apply_filter_to_image(rgb_img, filter_type, filter_strength)
                    
                    # 将滤镜后的RGB与原始Alpha通道合并
                    filtered_channels = filtered_rgb.split()
                    final_img = Image.merge('RGBA', filtered_channels + (alpha_channel,))
                    
                    # 如果原始模式不是RGBA，转换回原始模式
                    if original_mode != 'RGBA':
                        if original_mode == 'RGB':
                            final_img = final_img.convert('RGB')
                        elif original_mode == 'LA':
                            final_img = final_img.convert('LA')
                        else:
                            final_img = final_img.convert(original_mode)
                    
                else:
                    # 没有透明通道或不需要保持透明度，直接处理
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 应用自定义滤镜效果
                    final_img = self._apply_filter_to_image(img, filter_type, filter_strength)
                
                # 保存处理后的图片
                if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                    final_img.save(image_path, 'JPEG', quality=95, optimize=True)
                else:
                    final_img.save(image_path, optimize=True)
                
                return True
                
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            # 如果处理失败且创建了备份，尝试恢复备份
            if backup and backup_path and backup_path.exists():
                try:
                    import shutil
                    shutil.copy2(backup_path, image_path)
                    print(f"  🔄 已从备份恢复原文件")
                except Exception as restore_e:
                    print(f"  ❌ 恢复备份失败: {restore_e}")
            return False
    
    def _apply_filter_to_image(self, img, filter_type, filter_strength):
        """
        对图片应用自定义滤镜效果的核心方法
        
        Args:
            img (PIL.Image): 要处理的图片
            filter_type (str): 滤镜类型
            filter_strength (float): 滤镜强度
        
        Returns:
            PIL.Image: 滤镜处理后的图片
        """
        if filter_type == 'red_black':
            # 红黑滤镜
            return self._red_black_filter(img, filter_strength)
        elif filter_type == 'sepia':
            # 棕褐色滤镜
            return self._sepia_filter(img, filter_strength)
        elif filter_type == 'vintage':
            # 复古滤镜
            return self._vintage_filter(img, filter_strength)
        elif filter_type == 'high_contrast':
            # 高对比度滤镜
            return self._high_contrast_filter(img, filter_strength)
        elif filter_type == 'invert':
            # 反色滤镜
            return self._invert_filter(img, filter_strength)
        elif filter_type == 'grayscale':
            # 灰度滤镜
            return self._grayscale_filter(img, filter_strength)
        else:
            print(f"警告：不支持的滤镜类型 '{filter_type}'，使用红黑滤镜")
            return self._red_black_filter(img, filter_strength)
    
    def _red_black_filter(self, img, strength):
        """红黑滤镜效果"""
        # 转换为RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 获取像素数据
        pixels = img.load()
        width, height = img.size
        
        # 创建新图片
        filtered_img = Image.new('RGB', (width, height))
        filtered_pixels = filtered_img.load()
        
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                
                # 红黑滤镜算法：增强红色，减少绿色和蓝色
                # 计算红色强度
                red_intensity = r * strength
                # 减少绿色和蓝色
                green_reduced = g * (1.0 - strength * 0.5)
                blue_reduced = b * (1.0 - strength * 0.7)
                
                # 确保像素值在有效范围内
                new_r = min(255, int(red_intensity))
                new_g = max(0, min(255, int(green_reduced)))
                new_b = max(0, min(255, int(blue_reduced)))
                
                filtered_pixels[x, y] = (new_r, new_g, new_b)
        
        return filtered_img
    
    def _sepia_filter(self, img, strength):
        """棕褐色滤镜效果"""
        # 转换为RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 获取像素数据
        pixels = img.load()
        width, height = img.size
        
        # 创建新图片
        filtered_img = Image.new('RGB', (width, height))
        filtered_pixels = filtered_img.load()
        
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                
                # 棕褐色滤镜算法
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                # 应用强度
                new_r = min(255, int(tr * strength + r * (1 - strength)))
                new_g = min(255, int(tg * strength + g * (1 - strength)))
                new_b = min(255, int(tb * strength + b * (1 - strength)))
                
                filtered_pixels[x, y] = (new_r, new_g, new_b)
        
        return filtered_img
    
    def _vintage_filter(self, img, strength):
        """复古滤镜效果"""
        # 先应用棕褐色滤镜
        sepia_img = self._sepia_filter(img, strength * 0.7)
        
        # 降低对比度
        contrast_enhancer = ImageEnhance.Contrast(sepia_img)
        vintage_img = contrast_enhancer.enhance(0.8)
        
        # 降低亮度
        brightness_enhancer = ImageEnhance.Brightness(vintage_img)
        vintage_img = brightness_enhancer.enhance(0.9)
        
        return vintage_img
    
    def _high_contrast_filter(self, img, strength):
        """高对比度滤镜效果"""
        # 增强对比度
        contrast_enhancer = ImageEnhance.Contrast(img)
        high_contrast_img = contrast_enhancer.enhance(1.0 + strength)
        
        # 增强锐度
        sharpness_enhancer = ImageEnhance.Sharpness(high_contrast_img)
        high_contrast_img = sharpness_enhancer.enhance(1.0 + strength * 0.5)
        
        return high_contrast_img
    
    def _invert_filter(self, img, strength):
        """反色滤镜效果"""
        # 使用PIL的内置反色滤镜
        inverted = Image.eval(img, lambda x: 255 - x)
        
        # 根据强度混合原图和反色图
        if strength < 1.0:
            # 创建混合效果
            blend_img = Image.blend(img, inverted, strength)
            return blend_img
        else:
            return inverted
    
    def _grayscale_filter(self, img, strength):
        """灰度滤镜效果"""
        # 转换为灰度图
        grayscale = img.convert('L').convert('RGB')
        
        # 根据强度混合原图和灰度图
        if strength < 1.0:
            blend_img = Image.blend(img, grayscale, strength)
            return blend_img
        else:
            return grayscale
    
    def apply_all_filters(self, filter_type='red_black', filter_strength=1.0, 
                         preserve_transparency=True, backup=True, recursive=True):
        """
        对文件夹中的所有图片执行自定义滤镜处理并直接替换原文件
        
        Args:
            filter_type (str): 滤镜类型 ('red_black', 'sepia', 'vintage', 'high_contrast', 'invert', 'grayscale')
            filter_strength (float): 滤镜强度 (0.1-3.0)
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
        """
        # 获取所有图片文件
        image_files = self.get_image_files(recursive=recursive)
        
        if not image_files:
            print(f"在文件夹 {self.folder_path} 中没有找到可处理的图片文件")
            return
        
        print(f"在文件夹 {self.folder_path} 中找到 {len(image_files)} 张图片")
        print(f"自定义滤镜参数：类型={filter_type}, 强度={filter_strength}")
        print(f"备份模式：{'开启' if backup else '关闭'}")
        print(f"递归模式：{'开启' if recursive else '关闭'}")
        print(f"保持透明度：{'开启' if preserve_transparency else '关闭'}")
        
        success_count = 0
        
        for image_path in image_files:
            # 显示相对路径，更清晰地显示文件位置
            relative_path = image_path.relative_to(self.folder_path)
            print(f"正在处理: {relative_path}")
            
            # 应用自定义滤镜效果
            if self.apply_custom_filter(image_path, filter_type, filter_strength, 
                                      preserve_transparency, backup):
                print(f"  ✓ 已替换原文件: {relative_path}")
                success_count += 1
            else:
                print(f"  ✗ 处理失败")
        
        print(f"\n处理完成！成功处理 {success_count}/{len(image_files)} 张图片")
        
        if backup and success_count > 0:
            print(f"💡 提示：备份文件已保存，如需恢复原图，请将 .backup 文件重命名")
    
    @staticmethod
    def filter_folder_images(folder_path, filter_type='red_black', filter_strength=1.0,
                           preserve_transparency=True, backup=True, recursive=True):
        """
        静态方法：直接对指定文件夹中的图片执行自定义滤镜处理并替换
        
        Args:
            folder_path (str): 要处理的文件夹路径
            filter_type (str): 滤镜类型 ('red_black', 'sepia', 'vintage', 'high_contrast', 'invert', 'grayscale')
            filter_strength (float): 滤镜强度 (0.1-3.0)
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
        """
        # 创建一个处理器实例
        processor = ImageFilterProcessor(folder_path)
        processor.apply_all_filters(filter_type, filter_strength, 
                                  preserve_transparency, backup, recursive)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片自定义滤镜效果处理工具')
    parser.add_argument('folder_path', 
                       help='要处理的文件夹路径')
    parser.add_argument('--type', '-t', 
                       choices=['red_black', 'sepia', 'vintage', 'high_contrast', 'invert', 'grayscale'], 
                       default='red_black',
                       help='滤镜类型 (默认: red_black)')
    parser.add_argument('--strength', '-s', type=float, default=1.0,
                       help='滤镜强度 (0.1-3.0, 默认: 1.0)')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件（危险操作）')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归查找子文件夹中的图片（默认递归查找）')
    parser.add_argument('--no-preserve-transparency', action='store_true',
                       help='不保持透明区域不变（默认保持透明度）')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.strength < 0.1 or args.strength > 3.0:
        print("错误：滤镜强度必须在 0.1-3.0 之间")
        return
    
    if not args.no_backup:
        print("⚠️ 警告：你选择了创建备份的替换模式，原文件将被修改！")
        confirm = input("确认继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
    
    try:
        # 使用静态方法直接处理指定文件夹
        ImageFilterProcessor.filter_folder_images(
            args.folder_path,
            filter_type=args.type,
            filter_strength=args.strength,
            preserve_transparency=not args.no_preserve_transparency,
            backup=not args.no_backup,
            recursive=not args.no_recursive
        )
    except Exception as e:
        print(f"错误：{e}")

def filter_demo():
    """自定义滤镜效果演示"""
    print("=== 图片自定义滤镜效果处理工具 ===")
    print("使用调试参数进行演示...")
    
    print(f"将对文件夹 {DEBUG_FOLDER_PATH} 中的图片进行自定义滤镜处理并替换原文件...")
    print(f"调试参数：类型={DEBUG_FILTER_TYPE}, 强度={DEBUG_FILTER_STRENGTH}")
    print(f"备份模式：{'开启' if DEBUG_BACKUP else '关闭'}, 递归模式：{'开启' if DEBUG_RECURSIVE else '关闭'}")
    
    try:
        # 使用静态方法直接处理
        ImageFilterProcessor.filter_folder_images(
            folder_path=DEBUG_FOLDER_PATH,
            filter_type=DEBUG_FILTER_TYPE,
            filter_strength=DEBUG_FILTER_STRENGTH,
            preserve_transparency=DEBUG_PRESERVE_TRANSPARENCY,
            backup=DEBUG_BACKUP,
            recursive=DEBUG_RECURSIVE
        )
        
        print("\n演示完成！")
        print("你可以使用以下命令进行自定义处理：")
        print("python image_filter_tool.py /path/to/folder --type red_black --strength 2.0")
        print("python image_filter_tool.py /path/to/folder --type sepia --strength 1.5 --no-backup")
        
    except Exception as e:
        print(f"演示失败：{e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有命令行参数，运行演示
        filter_demo()
    else:
        # 有命令行参数，使用argparse处理
        main()
