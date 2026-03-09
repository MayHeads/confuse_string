#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片锐化效果处理工具
使用Pillow库为图片添加可调节的锐化效果
"""

import os
import sys
from PIL import Image, ImageFilter, ImageEnhance
import argparse
from pathlib import Path

# ==================== 调试参数配置 ====================
# 方便调试时快速修改参数，无需修改代码内部
DEBUG_FOLDER_PATH = '/Users/jiangshanchen/TSComposs/TSComposs/Resource/Assets.xcassets'  # 要处理的文件夹路径
DEBUG_SHARPEN_STRENGTH = 200      # 锐化强度 (0.1-5.0)
DEBUG_SHARPEN_TYPE = 'unsharp_mask'  # 锐化类型 ('unsharp_mask', 'sharpen', 'detail', 'enhance')
DEBUG_PRESERVE_TRANSPARENCY = True  # 是否保持透明区域不变
DEBUG_BACKUP = False              # 是否创建备份文件
DEBUG_RECURSIVE = True            # 是否递归查找子文件夹
DEBUG_QUALITY = 95                # 输出图片质量 (1-100)
# =====================================================

class ImageSharpenProcessor:
    """图片锐化处理器"""
    
    def __init__(self, folder_path):
        """
        初始化图片锐化处理器
        
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
    
    def apply_sharpen(self, image_path, sharpen_strength=1.5, sharpen_type='unsharp_mask', 
                     preserve_transparency=True, backup=True):
        """
        对单张图片应用锐化效果
        
        Args:
            image_path (Path): 图片文件路径
            sharpen_strength (float): 锐化强度 (0.1-5.0)
            sharpen_type (str): 锐化类型 ('unsharp_mask', 'sharpen', 'detail', 'enhance')
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
                    
                    # 将RGB通道合并为RGB图像进行锐化处理
                    rgb_img = Image.merge('RGB', rgb_channels)
                    
                    # 应用锐化效果
                    sharpened_rgb = self._apply_sharpen_to_image(rgb_img, sharpen_strength, sharpen_type)
                    
                    # 将锐化后的RGB与原始Alpha通道合并
                    sharpened_channels = sharpened_rgb.split()
                    final_img = Image.merge('RGBA', sharpened_channels + (alpha_channel,))
                    
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
                    
                    # 应用锐化效果
                    final_img = self._apply_sharpen_to_image(img, sharpen_strength, sharpen_type)
                
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
    
    def _apply_sharpen_to_image(self, img, sharpen_strength, sharpen_type):
        """
        对图片应用锐化效果的核心方法
        
        Args:
            img (PIL.Image): 要处理的图片
            sharpen_strength (float): 锐化强度
            sharpen_type (str): 锐化类型
        
        Returns:
            PIL.Image: 锐化后的图片
        """
        if sharpen_type == 'unsharp_mask':
            # Unsharp Mask 锐化 - 最常用的锐化方法
            return self._unsharp_mask(img, sharpen_strength)
        elif sharpen_type == 'sharpen':
            # 基础锐化滤镜
            return self._basic_sharpen(img, sharpen_strength)
        elif sharpen_type == 'detail':
            # 细节增强锐化
            return self._detail_sharpen(img, sharpen_strength)
        elif sharpen_type == 'enhance':
            # 使用PIL的增强器
            return self._enhance_sharpen(img, sharpen_strength)
        else:
            print(f"警告：不支持的锐化类型 '{sharpen_type}'，使用Unsharp Mask")
            return self._unsharp_mask(img, sharpen_strength)
    
    def _unsharp_mask(self, img, strength):
        """Unsharp Mask 锐化算法（使用PIL实现）"""
        # 创建高斯模糊版本
        blurred = img.filter(ImageFilter.GaussianBlur(radius=1.0))
        
        # 使用PIL的ImageEnhance来实现Unsharp Mask效果
        # 先增强对比度来模拟锐化效果
        enhancer = ImageEnhance.Contrast(img)
        contrast_enhanced = enhancer.enhance(1.0 + (strength - 1.0) * 0.3)
        
        # 再增强锐度
        sharpness_enhancer = ImageEnhance.Sharpness(contrast_enhanced)
        sharpened = sharpness_enhancer.enhance(strength)
        
        return sharpened
    
    def _basic_sharpen(self, img, strength):
        """基础锐化滤镜"""
        # 使用PIL的内置锐化滤镜
        sharpened = img.filter(ImageFilter.SHARPEN)
        
        # 根据强度调整效果
        if strength > 1.0:
            # 多次应用锐化滤镜
            for _ in range(int(strength)):
                sharpened = sharpened.filter(ImageFilter.SHARPEN)
        
        return sharpened
    
    def _detail_sharpen(self, img, strength):
        """细节增强锐化"""
        # 使用边缘增强滤镜
        edge_enhanced = img.filter(ImageFilter.EDGE_ENHANCE)
        
        # 根据强度调整
        if strength > 1.0:
            for _ in range(int(strength)):
                edge_enhanced = edge_enhanced.filter(ImageFilter.EDGE_ENHANCE)
        
        return edge_enhanced
    
    def _enhance_sharpen(self, img, strength):
        """使用PIL增强器进行锐化"""
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(strength)
    
    def sharpen_all_images(self, sharpen_strength=1.5, sharpen_type='unsharp_mask', 
                          preserve_transparency=True, backup=True, recursive=True):
        """
        对文件夹中的所有图片执行锐化处理并直接替换原文件
        
        Args:
            sharpen_strength (float): 锐化强度 (0.1-5.0)
            sharpen_type (str): 锐化类型 ('unsharp_mask', 'sharpen', 'detail', 'enhance')
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
        print(f"锐化参数：类型={sharpen_type}, 强度={sharpen_strength}")
        print(f"备份模式：{'开启' if backup else '关闭'}")
        print(f"递归模式：{'开启' if recursive else '关闭'}")
        print(f"保持透明度：{'开启' if preserve_transparency else '关闭'}")
        
        success_count = 0
        
        for image_path in image_files:
            # 显示相对路径，更清晰地显示文件位置
            relative_path = image_path.relative_to(self.folder_path)
            print(f"正在处理: {relative_path}")
            
            # 应用锐化效果
            if self.apply_sharpen(image_path, sharpen_strength, sharpen_type, 
                                preserve_transparency, backup):
                print(f"  ✓ 已替换原文件: {relative_path}")
                success_count += 1
            else:
                print(f"  ✗ 处理失败")
        
        print(f"\n处理完成！成功处理 {success_count}/{len(image_files)} 张图片")
        
        if backup and success_count > 0:
            print(f"💡 提示：备份文件已保存，如需恢复原图，请将 .backup 文件重命名")
    
    @staticmethod
    def sharpen_folder_images(folder_path, sharpen_strength=1.5, sharpen_type='unsharp_mask',
                            preserve_transparency=True, backup=True, recursive=True):
        """
        静态方法：直接对指定文件夹中的图片执行锐化处理并替换
        
        Args:
            folder_path (str): 要处理的文件夹路径
            sharpen_strength (float): 锐化强度 (0.1-5.0)
            sharpen_type (str): 锐化类型 ('unsharp_mask', 'sharpen', 'detail', 'enhance')
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
        """
        # 创建一个处理器实例
        processor = ImageSharpenProcessor(folder_path)
        processor.sharpen_all_images(sharpen_strength, sharpen_type, 
                                   preserve_transparency, backup, recursive)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片锐化效果处理工具')
    parser.add_argument('folder_path', 
                       help='要处理的文件夹路径')
    parser.add_argument('--strength', '-s', type=float, default=1.5,
                       help='锐化强度 (0.1-5.0, 默认: 1.5)')
    parser.add_argument('--type', '-t', 
                       choices=['unsharp_mask', 'sharpen', 'detail', 'enhance'], 
                       default='unsharp_mask',
                       help='锐化类型 (默认: unsharp_mask)')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件（危险操作）')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归查找子文件夹中的图片（默认递归查找）')
    parser.add_argument('--no-preserve-transparency', action='store_true',
                       help='不保持透明区域不变（默认保持透明度）')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.strength < 0.1 or args.strength > 5.0:
        print("错误：锐化强度必须在 0.1-5.0 之间")
        return
    
    if not args.no_backup:
        print("⚠️ 警告：你选择了创建备份的替换模式，原文件将被修改！")
        confirm = input("确认继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
    
    try:
        # 使用静态方法直接处理指定文件夹
        ImageSharpenProcessor.sharpen_folder_images(
            args.folder_path,
            sharpen_strength=args.strength,
            sharpen_type=args.type,
            preserve_transparency=not args.no_preserve_transparency,
            backup=not args.no_backup,
            recursive=not args.no_recursive
        )
    except Exception as e:
        print(f"错误：{e}")

def sharpen_demo():
    """锐化效果演示"""
    print("=== 图片锐化效果处理工具 ===")
    print("使用调试参数进行演示...")
    
    print(f"将对文件夹 {DEBUG_FOLDER_PATH} 中的图片进行锐化处理并替换原文件...")
    print(f"调试参数：强度={DEBUG_SHARPEN_STRENGTH}, 类型={DEBUG_SHARPEN_TYPE}")
    print(f"备份模式：{'开启' if DEBUG_BACKUP else '关闭'}, 递归模式：{'开启' if DEBUG_RECURSIVE else '关闭'}")
    
    try:
        # 使用静态方法直接处理
        ImageSharpenProcessor.sharpen_folder_images(
            folder_path=DEBUG_FOLDER_PATH,
            sharpen_strength=DEBUG_SHARPEN_STRENGTH,
            sharpen_type=DEBUG_SHARPEN_TYPE,
            preserve_transparency=DEBUG_PRESERVE_TRANSPARENCY,
            backup=DEBUG_BACKUP,
            recursive=DEBUG_RECURSIVE
        )
        
        print("\n演示完成！")
        print("你可以使用以下命令进行自定义处理：")
        print("python image_sharpen_tool.py /path/to/folder --strength 2.0 --type unsharp_mask")
        print("python image_sharpen_tool.py /path/to/folder --no-backup --strength 3.0")
        
    except Exception as e:
        print(f"演示失败：{e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有命令行参数，运行演示
        sharpen_demo()
    else:
        # 有命令行参数，使用argparse处理
        main()
