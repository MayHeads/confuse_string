#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片仿射变换处理工具
使用Pillow库为图片添加可调节的仿射变换效果（缩放瘦身）
"""

import os
import sys
from PIL import Image, ImageOps
import argparse
from pathlib import Path

# ==================== 调试参数配置 ====================
# 方便调试时快速修改参数，无需修改代码内部
DEBUG_FOLDER_PATH = '/Users/jiangshanchen/TSComposs/TSComposs/Resource/Assets.xcassets'  # 要处理的文件夹路径
DEBUG_SCALE_X = 0.95         # X轴缩放比例 (0.1-2.0, 小于1为瘦身，大于1为拉伸)
DEBUG_SCALE_Y = 1.0          # Y轴缩放比例 (0.1-2.0, 小于1为瘦身，大于1为拉伸)
DEBUG_PRESERVE_TRANSPARENCY = True  # 是否保持透明区域不变
DEBUG_BACKUP = False          # 是否创建备份文件
DEBUG_RECURSIVE = True       # 是否递归查找子文件夹
DEBUG_QUALITY = 95           # 输出图片质量 (1-100)
DEBUG_INTERPOLATION = 'LANCZOS'  # 插值方法 ('NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS')
# =====================================================

class ImageAffineProcessor:
    """图片仿射变换处理器"""
    
    def __init__(self, folder_path):
        """
        初始化图片仿射变换处理器
        
        Args:
            folder_path (str): 要处理的文件夹路径
        """
        self.folder_path = Path(folder_path)
        
        # 支持的图片格式
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        
        # 插值方法映射
        self.interpolation_methods = {
            'NEAREST': Image.NEAREST,
            'BILINEAR': Image.BILINEAR,
            'BICUBIC': Image.BICUBIC,
            'LANCZOS': Image.LANCZOS
        }
        
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
    
    def apply_affine_transform(self, image_path, scale_x=0.8, scale_y=1.0, 
                              preserve_transparency=True, backup=True, 
                              interpolation='LANCZOS', quality=95):
        """
        对单张图片应用仿射变换（缩放瘦身）
        
        Args:
            image_path (Path): 图片文件路径
            scale_x (float): X轴缩放比例 (0.1-2.0, 小于1为瘦身，大于1为拉伸)
            scale_y (float): Y轴缩放比例 (0.1-2.0, 小于1为瘦身，大于1为拉伸)
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            interpolation (str): 插值方法
            quality (int): 输出图片质量 (1-100)
        
        Returns:
            bool: 处理是否成功
        """
        try:
            # 验证参数
            if not (0.1 <= scale_x <= 2.0):
                raise ValueError(f"scale_x 必须在 0.1-2.0 之间，当前值: {scale_x}")
            if not (0.1 <= scale_y <= 2.0):
                raise ValueError(f"scale_y 必须在 0.1-2.0 之间，当前值: {scale_y}")
            
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
                original_size = img.size
                
                print(f"  📏 原始尺寸: {original_size[0]}x{original_size[1]}")
                
                # 如果图片有透明通道且需要保持透明度
                if preserve_transparency and img.mode in ('RGBA', 'LA') or 'transparency' in img.info:
                    # 转换为RGBA模式以处理透明度
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # 应用仿射变换
                    transformed_img = self._apply_affine_transform_to_image(
                        img, scale_x, scale_y, interpolation
                    )
                    
                    # 如果原始模式不是RGBA，转换回原始模式
                    if original_mode != 'RGBA':
                        if original_mode == 'RGB':
                            transformed_img = transformed_img.convert('RGB')
                        elif original_mode == 'LA':
                            transformed_img = transformed_img.convert('LA')
                        else:
                            transformed_img = transformed_img.convert(original_mode)
                    
                else:
                    # 没有透明通道或不需要保持透明度，直接处理
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 应用仿射变换
                    transformed_img = self._apply_affine_transform_to_image(
                        img, scale_x, scale_y, interpolation
                    )
                
                # 显示变换后的尺寸
                new_size = transformed_img.size
                print(f"  📏 变换后尺寸: {new_size[0]}x{new_size[1]}")
                print(f"  📊 缩放比例: X={scale_x:.2f}, Y={scale_y:.2f}")
                
                # 保存处理后的图片
                if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                    transformed_img.save(image_path, 'JPEG', quality=quality, optimize=True)
                else:
                    transformed_img.save(image_path, optimize=True)
                
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
    
    def _apply_affine_transform_to_image(self, img, scale_x, scale_y, interpolation):
        """
        对图片应用仿射变换的核心方法
        
        Args:
            img (PIL.Image): 要处理的图片
            scale_x (float): X轴缩放比例
            scale_y (float): Y轴缩放比例
            interpolation (str): 插值方法
        
        Returns:
            PIL.Image: 变换后的图片
        """
        # 获取插值方法
        interp_method = self.interpolation_methods.get(interpolation, Image.LANCZOS)
        
        # 计算新的尺寸
        original_width, original_height = img.size
        new_width = int(original_width * scale_x)
        new_height = int(original_height * scale_y)
        
        # 使用PIL的resize方法实现仿射变换
        # 这里我们使用resize来实现缩放效果
        transformed_img = img.resize((new_width, new_height), interp_method)
        
        # 如果需要保持原始尺寸，可以添加背景填充
        # 这里我们直接返回变换后的尺寸，让用户看到瘦身效果
        
        return transformed_img
    
    def affine_transform_all_images(self, scale_x=0.8, scale_y=1.0, 
                                   preserve_transparency=True, backup=True, 
                                   recursive=True, interpolation='LANCZOS', quality=95):
        """
        对文件夹中的所有图片执行仿射变换处理并直接替换原文件
        
        Args:
            scale_x (float): X轴缩放比例 (0.1-2.0)
            scale_y (float): Y轴缩放比例 (0.1-2.0)
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
            interpolation (str): 插值方法
            quality (int): 输出图片质量 (1-100)
        """
        # 获取所有图片文件
        image_files = self.get_image_files(recursive=recursive)
        
        if not image_files:
            print(f"在文件夹 {self.folder_path} 中没有找到可处理的图片文件")
            return
        
        print(f"在文件夹 {self.folder_path} 中找到 {len(image_files)} 张图片")
        print(f"仿射变换参数：X轴缩放={scale_x}, Y轴缩放={scale_y}")
        print(f"插值方法：{interpolation}")
        print(f"输出质量：{quality}")
        print(f"备份模式：{'开启' if backup else '关闭'}")
        print(f"递归模式：{'开启' if recursive else '关闭'}")
        print(f"保持透明度：{'开启' if preserve_transparency else '关闭'}")
        
        success_count = 0
        
        for image_path in image_files:
            # 显示相对路径，更清晰地显示文件位置
            relative_path = image_path.relative_to(self.folder_path)
            print(f"正在处理: {relative_path}")
            
            # 应用仿射变换
            if self.apply_affine_transform(image_path, scale_x, scale_y, 
                                         preserve_transparency, backup, 
                                         interpolation, quality):
                print(f"  ✓ 已替换原文件: {relative_path}")
                success_count += 1
            else:
                print(f"  ✗ 处理失败")
        
        print(f"\n处理完成！成功处理 {success_count}/{len(image_files)} 张图片")
        
        if backup and success_count > 0:
            print(f"💡 提示：备份文件已保存，如需恢复原图，请将 .backup 文件重命名")
    
    @staticmethod
    def affine_transform_folder_images(folder_path, scale_x=0.8, scale_y=1.0,
                                      preserve_transparency=True, backup=True, 
                                      recursive=True, interpolation='LANCZOS', quality=95):
        """
        静态方法：直接对指定文件夹中的图片执行仿射变换处理并替换
        
        Args:
            folder_path (str): 要处理的文件夹路径
            scale_x (float): X轴缩放比例 (0.1-2.0)
            scale_y (float): Y轴缩放比例 (0.1-2.0)
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
            interpolation (str): 插值方法
            quality (int): 输出图片质量 (1-100)
        """
        # 创建一个处理器实例
        processor = ImageAffineProcessor(folder_path)
        processor.affine_transform_all_images(scale_x, scale_y, 
                                            preserve_transparency, backup, 
                                            recursive, interpolation, quality)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片仿射变换处理工具')
    parser.add_argument('folder_path', 
                       help='要处理的文件夹路径')
    parser.add_argument('--scale-x', '-x', type=float, default=DEBUG_SCALE_X,
                       help=f'X轴缩放比例 (0.1-2.0, 默认: {DEBUG_SCALE_X})')
    parser.add_argument('--scale-y', '-y', type=float, default=DEBUG_SCALE_Y,
                       help=f'Y轴缩放比例 (0.1-2.0, 默认: {DEBUG_SCALE_Y})')
    parser.add_argument('--interpolation', '-i', 
                       choices=['NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS'], 
                       default=DEBUG_INTERPOLATION,
                       help=f'插值方法 (默认: {DEBUG_INTERPOLATION})')
    parser.add_argument('--quality', '-q', type=int, default=DEBUG_QUALITY,
                       help=f'输出图片质量 (1-100, 默认: {DEBUG_QUALITY})')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件（危险操作）')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归查找子文件夹中的图片（默认递归查找）')
    parser.add_argument('--no-preserve-transparency', action='store_true',
                       help='不保持透明区域不变（默认保持透明度）')
    
    args = parser.parse_args()
    
    # 验证参数
    if not (0.1 <= args.scale_x <= 2.0):
        print("错误：X轴缩放比例必须在 0.1-2.0 之间")
        return
    if not (0.1 <= args.scale_y <= 2.0):
        print("错误：Y轴缩放比例必须在 0.1-2.0 之间")
        return
    if not (1 <= args.quality <= 100):
        print("错误：输出质量必须在 1-100 之间")
        return
    
    if not args.no_backup:
        print("⚠️ 警告：你选择了创建备份的替换模式，原文件将被修改！")
        confirm = input("确认继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
    
    try:
        # 使用静态方法直接处理指定文件夹
        ImageAffineProcessor.affine_transform_folder_images(
            args.folder_path,
            scale_x=args.scale_x,
            scale_y=args.scale_y,
            preserve_transparency=not args.no_preserve_transparency,
            backup=not args.no_backup,
            recursive=not args.no_recursive,
            interpolation=args.interpolation,
            quality=args.quality
        )
    except Exception as e:
        print(f"错误：{e}")

def affine_demo():
    """仿射变换效果演示"""
    print("=== 图片仿射变换处理工具 ===")
    print("使用调试参数进行演示...")
    
    print(f"将对文件夹 {DEBUG_FOLDER_PATH} 中的图片进行仿射变换处理并替换原文件...")
    print(f"调试参数：X轴缩放={DEBUG_SCALE_X}, Y轴缩放={DEBUG_SCALE_Y}")
    print(f"插值方法：{DEBUG_INTERPOLATION}, 质量：{DEBUG_QUALITY}")
    
    try:
        # 使用静态方法直接处理
        ImageAffineProcessor.affine_transform_folder_images(
            folder_path=DEBUG_FOLDER_PATH,
            scale_x=DEBUG_SCALE_X,
            scale_y=DEBUG_SCALE_Y,
            preserve_transparency=DEBUG_PRESERVE_TRANSPARENCY,
            backup=DEBUG_BACKUP,
            recursive=DEBUG_RECURSIVE,
            interpolation=DEBUG_INTERPOLATION,
            quality=DEBUG_QUALITY
        )
        
        print("\n演示完成！")
        print("你可以使用以下命令进行自定义处理：")
        print("python image_affine_tool.py /path/to/folder --scale-x 0.7 --scale-y 1.0")
        print("python image_affine_tool.py /path/to/folder --no-backup --scale-x 0.6 --scale-y 0.9")
        print("\n💡 提示：")
        print("- scale_x < 1.0: 水平瘦身效果")
        print("- scale_y < 1.0: 垂直瘦身效果")
        print("- scale_x > 1.0: 水平拉伸效果")
        print("- scale_y > 1.0: 垂直拉伸效果")
        
    except Exception as e:
        print(f"演示失败：{e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有命令行参数，运行演示
        affine_demo()
    else:
        # 有命令行参数，使用argparse处理
        main()
