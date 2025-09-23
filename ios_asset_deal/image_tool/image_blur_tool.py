#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片模糊效果处理工具
使用Pillow库为图片添加可调节的模糊效果
"""

import os
import sys
from PIL import Image, ImageFilter
import argparse
from pathlib import Path

# ==================== 调试参数配置 ====================
# 方便调试时快速修改参数，无需修改代码内部
 # 输出图片文件夹路径
DEBUG_FOLDER_PATH = '/Users/jiangshanchen/TSComposs/TSComposs/Resource/Assets.xcassets'  # 要处理的文件夹路径
DEBUG_BLUR_RADIUS = 3           # 模糊半径 (1-20, 数值越大越模糊)
DEBUG_BLUR_TYPE = 'gaussian'    # 模糊类型 ('gaussian', 'box', 'median')
DEBUG_QUALITY = 95              # 输出图片质量 (1-100)
DEBUG_PRESERVE_TRANSPARENCY = True  # 是否保持透明区域不变
DEBUG_BACKUP = False            # 是否创建备份文件
DEBUG_RECURSIVE = True          # 是否递归查找子文件夹
# =====================================================

class ImageBlurProcessor:
    """图片模糊处理器"""
    
    def __init__(self, origin_folder, output_folder):
        """
        初始化图片模糊处理器
        
        Args:
            origin_folder (str): 原始图片文件夹路径
            output_folder (str): 输出图片文件夹路径
        """
        self.origin_folder = Path(origin_folder)
        self.output_folder = Path(output_folder)
        
        # 支持的图片格式
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        
        # 确保输出文件夹存在
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def get_image_files(self, recursive=True):
        """获取原始文件夹中的所有图片文件"""
        image_files = []
        if not self.origin_folder.exists():
            print(f"错误：原始图片文件夹不存在: {self.origin_folder}")
            return image_files
        
        if recursive:
            # 递归查找所有子文件夹中的图片
            for file_path in self.origin_folder.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    image_files.append(file_path)
        else:
            # 只查找当前文件夹中的图片
            for file_path in self.origin_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    image_files.append(file_path)
        
        return image_files
    
    def apply_blur(self, image_path, blur_radius=2, blur_type='gaussian', preserve_transparency=True):
        """
        对单张图片应用模糊效果
        
        Args:
            image_path (Path): 图片文件路径
            blur_radius (int): 模糊半径，数值越大越模糊
            blur_type (str): 模糊类型 ('gaussian', 'box', 'median')
            preserve_transparency (bool): 是否保持透明区域不变
        
        Returns:
            PIL.Image: 处理后的图片对象
        """
        try:
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
                    
                    # 将RGB通道合并为RGB图像进行模糊处理
                    rgb_img = Image.merge('RGB', rgb_channels)
                    
                    # 根据模糊类型应用不同的模糊效果
                    if blur_type == 'gaussian':
                        blurred_rgb = rgb_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                    elif blur_type == 'box':
                        blurred_rgb = rgb_img.filter(ImageFilter.BoxBlur(radius=blur_radius))
                    elif blur_type == 'median':
                        blurred_rgb = rgb_img.filter(ImageFilter.MedianFilter(size=blur_radius))
                    else:
                        print(f"警告：不支持的模糊类型 '{blur_type}'，使用高斯模糊")
                        blurred_rgb = rgb_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                    
                    # 将模糊后的RGB与原始Alpha通道合并
                    blurred_channels = blurred_rgb.split()
                    final_img = Image.merge('RGBA', blurred_channels + (alpha_channel,))
                    
                    # 如果原始模式不是RGBA，转换回原始模式
                    if original_mode != 'RGBA':
                        if original_mode == 'RGB':
                            final_img = final_img.convert('RGB')
                        elif original_mode == 'LA':
                            final_img = final_img.convert('LA')
                        else:
                            final_img = final_img.convert(original_mode)
                    
                    return final_img
                
                else:
                    # 没有透明通道或不需要保持透明度，直接处理
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 根据模糊类型应用不同的模糊效果
                    if blur_type == 'gaussian':
                        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                    elif blur_type == 'box':
                        blurred_img = img.filter(ImageFilter.BoxBlur(radius=blur_radius))
                    elif blur_type == 'median':
                        blurred_img = img.filter(ImageFilter.MedianFilter(size=blur_radius))
                    else:
                        print(f"警告：不支持的模糊类型 '{blur_type}'，使用高斯模糊")
                        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                    
                    return blurred_img
                
        except Exception as e:
            print(f"错误：处理图片 {image_path} 时出错: {e}")
            return None
    
    def process_all_images(self, blur_radius=2, blur_type='gaussian', quality=95, recursive=True, preserve_transparency=True):
        """
        处理原始文件夹中的所有图片
        
        Args:
            blur_radius (int): 模糊半径，数值越大越模糊 (1-20)
            blur_type (str): 模糊类型 ('gaussian', 'box', 'median')
            quality (int): 输出图片质量 (1-100)
            recursive (bool): 是否递归查找子文件夹中的图片
            preserve_transparency (bool): 是否保持透明区域不变
        """
        # 获取所有图片文件
        image_files = self.get_image_files(recursive=recursive)
        
        if not image_files:
            print("没有找到可处理的图片文件")
            return
        
        print(f"找到 {len(image_files)} 张图片，开始处理...")
        print(f"模糊参数：类型={blur_type}, 半径={blur_radius}, 质量={quality}")
        print(f"递归模式：{'开启' if recursive else '关闭'}")
        print(f"保持透明度：{'开启' if preserve_transparency else '关闭'}")
        
        success_count = 0
        
        for image_path in image_files:
            # 显示相对路径，更清晰地显示文件位置
            relative_path = image_path.relative_to(self.origin_folder)
            print(f"正在处理: {relative_path}")
            
            # 应用模糊效果
            blurred_img = self.apply_blur(image_path, blur_radius, blur_type, preserve_transparency)
            
            if blurred_img is not None:
                # 保持原有的文件夹结构
                relative_output_path = self.output_folder / relative_path
                relative_output_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    # 保存处理后的图片
                    if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                        blurred_img.save(relative_output_path, 'JPEG', quality=quality, optimize=True)
                    else:
                        blurred_img.save(relative_output_path, optimize=True)
                    
                    print(f"  ✓ 已保存到: {relative_output_path}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ✗ 保存失败: {e}")
            else:
                print(f"  ✗ 处理失败")
        
        print(f"\n处理完成！成功处理 {success_count}/{len(image_files)} 张图片")
    
    def blur_and_replace_images(self, folder_path, blur_radius=2, blur_type='gaussian', quality=95, backup=True, recursive=True, preserve_transparency=True):
        """
        对指定文件夹中的所有图片执行模糊处理并直接替换原文件
        
        Args:
            folder_path (str): 要处理的文件夹路径
            blur_radius (int): 模糊半径，数值越大越模糊 (1-20)
            blur_type (str): 模糊类型 ('gaussian', 'box', 'median')
            quality (int): 输出图片质量 (1-100)
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
            preserve_transparency (bool): 是否保持透明区域不变
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            print(f"错误：文件夹不存在: {folder_path}")
            return
        
        if not folder_path.is_dir():
            print(f"错误：路径不是文件夹: {folder_path}")
            return
        
        # 获取文件夹中的所有图片文件（支持递归）
        image_files = []
        if recursive:
            for file_path in folder_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    image_files.append(file_path)
        else:
            for file_path in folder_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    image_files.append(file_path)
        
        if not image_files:
            print(f"在文件夹 {folder_path} 中没有找到可处理的图片文件")
            return
        
        print(f"在文件夹 {folder_path} 中找到 {len(image_files)} 张图片")
        print(f"模糊参数：类型={blur_type}, 半径={blur_radius}, 质量={quality}")
        print(f"备份模式：{'开启' if backup else '关闭'}")
        print(f"递归模式：{'开启' if recursive else '关闭'}")
        print(f"保持透明度：{'开启' if preserve_transparency else '关闭'}")
        
        success_count = 0
        
        for image_path in image_files:
            # 显示相对路径，更清晰地显示文件位置
            relative_path = image_path.relative_to(folder_path)
            print(f"正在处理: {relative_path}")
            
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
                    continue
            
            # 应用模糊效果
            blurred_img = self.apply_blur(image_path, blur_radius, blur_type, preserve_transparency)
            
            if blurred_img is not None:
                try:
                    # 直接替换原文件
                    if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                        blurred_img.save(image_path, 'JPEG', quality=quality, optimize=True)
                    else:
                        blurred_img.save(image_path, optimize=True)
                    
                    print(f"  ✓ 已替换原文件: {relative_path}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ✗ 替换失败: {e}")
                    # 如果替换失败且创建了备份，尝试恢复备份
                    if backup and backup_path and backup_path.exists():
                        try:
                            import shutil
                            shutil.copy2(backup_path, image_path)
                            print(f"  🔄 已从备份恢复原文件")
                        except Exception as restore_e:
                            print(f"  ❌ 恢复备份失败: {restore_e}")
            else:
                print(f"  ✗ 处理失败")
        
        print(f"\n处理完成！成功处理 {success_count}/{len(image_files)} 张图片")
        
        if backup and success_count > 0:
            print(f"💡 提示：备份文件已保存，如需恢复原图，请将 .backup 文件重命名")
    
    @staticmethod
    def blur_folder_images(folder_path, blur_radius=2, blur_type='gaussian', quality=95, backup=True, recursive=True, preserve_transparency=True):
        """
        静态方法：直接对指定文件夹中的图片执行模糊处理并替换
        
        Args:
            folder_path (str): 要处理的文件夹路径
            blur_radius (int): 模糊半径，数值越大越模糊 (1-20)
            blur_type (str): 模糊类型 ('gaussian', 'box', 'median')
            quality (int): 输出图片质量 (1-100)
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
            preserve_transparency (bool): 是否保持透明区域不变
        """
        # 创建一个临时的处理器实例
        temp_processor = ImageBlurProcessor(folder_path, folder_path)
        temp_processor.blur_and_replace_images(folder_path, blur_radius, blur_type, quality, backup, recursive, preserve_transparency)
    
    def preview_blur_effects(self, image_path, blur_radii=[1, 3, 5, 10]):
        """
        预览不同模糊半径的效果
        
        Args:
            image_path (Path): 图片文件路径
            blur_radii (list): 要预览的模糊半径列表
        """
        if not image_path.exists():
            print(f"错误：图片文件不存在: {image_path}")
            return
        
        print(f"预览图片: {image_path.name}")
        print("不同模糊半径的效果预览：")
        
        for radius in blur_radii:
            blurred_img = self.apply_blur(image_path, radius, 'gaussian')
            if blurred_img is not None:
                # 生成预览文件名
                preview_name = f"preview_blur_{radius}_{image_path.name}"
                preview_path = self.output_folder / preview_name
                
                try:
                    blurred_img.save(preview_path, optimize=True)
                    print(f"  半径 {radius}: 已保存预览到 {preview_name}")
                except Exception as e:
                    print(f"  半径 {radius}: 保存预览失败 - {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片模糊效果处理工具')
    parser.add_argument('--origin', '-o', 
                       default='/Users/jiangshanchen/confuse_string/ios_log/origin_image_file',
                       help='原始图片文件夹路径')
    parser.add_argument('--output', '-out',
                       default='/Users/jiangshanchen/confuse_string/ios_log/output_image_file', 
                       help='输出图片文件夹路径')
    parser.add_argument('--radius', '-r', type=int, default=2,
                       help='模糊半径 (1-20, 默认: 2)')
    parser.add_argument('--type', '-t', choices=['gaussian', 'box', 'median'], 
                       default='gaussian',
                       help='模糊类型 (默认: gaussian)')
    parser.add_argument('--quality', '-q', type=int, default=95,
                       help='输出图片质量 (1-100, 默认: 95)')
    parser.add_argument('--preview', '-p', action='store_true',
                       help='预览不同模糊半径的效果')
    parser.add_argument('--replace', action='store_true',
                       help='直接替换原文件（会创建备份）')
    parser.add_argument('--no-backup', action='store_true',
                       help='替换模式时不创建备份（危险操作）')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归查找子文件夹中的图片（默认递归查找）')
    parser.add_argument('--no-preserve-transparency', action='store_true',
                       help='不保持透明区域不变（默认保持透明度）')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.radius < 1 or args.radius > 20:
        print("错误：模糊半径必须在 1-20 之间")
        return
    
    if args.quality < 1 or args.quality > 100:
        print("错误：图片质量必须在 1-100 之间")
        return
    
    if args.replace:
        # 替换模式
        if args.no_backup:
            print("⚠️ 警告：你选择了不创建备份的替换模式，原文件将被永久修改！")
            confirm = input("确认继续吗？(y/N): ")
            if confirm.lower() != 'y':
                print("操作已取消")
                return
        
        # 使用静态方法直接处理指定文件夹
        ImageBlurProcessor.blur_folder_images(
            args.origin, 
            args.radius, 
            args.type, 
            args.quality, 
            backup=not args.no_backup,
            recursive=not args.no_recursive,
            preserve_transparency=not args.no_preserve_transparency
        )
    else:
        # 创建处理器
        processor = ImageBlurProcessor(args.origin, args.output)
        
        if args.preview:
            # 预览模式
            image_files = processor.get_image_files()
            if image_files:
                processor.preview_blur_effects(image_files[0])
            else:
                print("没有找到可预览的图片文件")
        else:
            # 正常处理模式
            processor.process_all_images(args.radius, args.type, args.quality, recursive=not args.no_recursive, preserve_transparency=not args.no_preserve_transparency)

def simple_blur_demo():
    """简单的模糊效果演示"""
    print("=== 图片模糊效果处理工具 ===")
    print("使用调试参数进行演示...")
    
    print(f"原始文件夹: {DEBUG_ORIGIN_FOLDER}")
    print(f"输出文件夹: {DEBUG_OUTPUT_FOLDER}")
    print(f"模糊参数：类型={DEBUG_BLUR_TYPE}, 半径={DEBUG_BLUR_RADIUS}, 质量={DEBUG_QUALITY}")
    
    # 创建处理器
    processor = ImageBlurProcessor(DEBUG_ORIGIN_FOLDER, DEBUG_OUTPUT_FOLDER)
    
    # 处理所有图片，使用调试参数
    processor.process_all_images(blur_radius=DEBUG_BLUR_RADIUS, blur_type=DEBUG_BLUR_TYPE, quality=DEBUG_QUALITY)
    
    print("\n演示完成！")
    print("你可以使用以下命令进行自定义处理：")
    print("python image_blur_tool.py --radius 5 --type gaussian")
    print("python image_blur_tool.py --preview  # 预览不同模糊效果")
    print("python image_blur_tool.py --replace  # 直接替换原文件（会创建备份）")
    print("python image_blur_tool.py --replace --no-backup  # 直接替换原文件（不创建备份，危险）")

def blur_folder_example():
    """演示如何直接对文件夹中的图片进行模糊处理并替换"""
    print("=== 文件夹图片模糊替换演示 ===")
    
    print(f"将对文件夹 {DEBUG_FOLDER_PATH} 中的图片进行模糊处理并替换原文件...")
    print(f"调试参数：模糊半径={DEBUG_BLUR_RADIUS}, 类型={DEBUG_BLUR_TYPE}, 质量={DEBUG_QUALITY}")
    print(f"备份模式：{'开启' if DEBUG_BACKUP else '关闭'}, 递归模式：{'开启' if DEBUG_RECURSIVE else '关闭'}")
    
    # 使用静态方法直接处理
    ImageBlurProcessor.blur_folder_images(
        folder_path=DEBUG_FOLDER_PATH,
        blur_radius=DEBUG_BLUR_RADIUS,
        blur_type=DEBUG_BLUR_TYPE,
        quality=DEBUG_QUALITY,
        backup=DEBUG_BACKUP,
        preserve_transparency=DEBUG_PRESERVE_TRANSPARENCY,
        recursive=DEBUG_RECURSIVE
    )
    
    print("\n文件夹处理完成！")
    print("💡 提示：原文件已被替换，备份文件以 .backup 扩展名保存")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有命令行参数，运行演示
        # simple_blur_demo()

        blur_folder_example()
    else:
        # 有命令行参数，使用argparse处理
        main()
