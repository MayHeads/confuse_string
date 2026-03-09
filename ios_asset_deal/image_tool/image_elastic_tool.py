#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片弹性变形处理工具
使用Pillow库为图片添加可调节的弹性变形效果（非线性扭曲）
"""

import os
import sys
import math
from PIL import Image, ImageOps, ImageFilter
import argparse
from pathlib import Path

# ==================== 调试参数配置 ====================
# 方便调试时快速修改参数，无需修改代码内部
DEBUG_FOLDER_PATH = '/Users/jiangshanchen/TSComposs/TSComposs/Resource/Assets.xcassets'  # 要处理的文件夹路径
DEBUG_ELASTIC_STRENGTH = 0.8     # 弹性变形强度 (0.1-1.0, 数值越大变形越明显)
DEBUG_ELASTIC_TYPE = 'both'  # 弹性变形类型 ('horizontal', 'vertical', 'both', 'wave', 'spiral')
DEBUG_PRESERVE_TRANSPARENCY = True  # 是否保持透明区域不变
DEBUG_BACKUP = False               # 是否创建备份文件
DEBUG_RECURSIVE = True             # 是否递归查找子文件夹
DEBUG_QUALITY = 93                # 输出图片质量 (1-100)
DEBUG_INTERPOLATION = 'BILINEAR'    # 插值方法 ('NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS')
# =====================================================

class ImageElasticProcessor:
    """图片弹性变形处理器"""
    
    def __init__(self, folder_path):
        """
        初始化图片弹性变形处理器
        
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
    
    def apply_elastic_deformation(self, image_path, elastic_strength=0.3, elastic_type='horizontal', 
                                 preserve_transparency=True, backup=True, 
                                 interpolation='LANCZOS', quality=95):
        """
        对单张图片应用弹性变形效果
        
        Args:
            image_path (Path): 图片文件路径
            elastic_strength (float): 弹性变形强度 (0.1-1.0)
            elastic_type (str): 弹性变形类型 ('horizontal', 'vertical', 'both', 'wave', 'spiral')
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            interpolation (str): 插值方法
            quality (int): 输出图片质量 (1-100)
        
        Returns:
            bool: 处理是否成功
        """
        try:
            # 验证参数
            if not (0.1 <= elastic_strength <= 1.0):
                raise ValueError(f"elastic_strength 必须在 0.1-1.0 之间，当前值: {elastic_strength}")
            
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
                    
                    # 应用弹性变形
                    transformed_img = self._apply_elastic_deformation_to_image(
                        img, elastic_strength, elastic_type, interpolation
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
                    
                    # 应用弹性变形
                    transformed_img = self._apply_elastic_deformation_to_image(
                        img, elastic_strength, elastic_type, interpolation
                    )
                
                # 显示变换后的尺寸
                new_size = transformed_img.size
                print(f"  📏 变换后尺寸: {new_size[0]}x{new_size[1]}")
                print(f"  📊 弹性变形: 强度={elastic_strength:.2f}, 类型={elastic_type}")
                
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
    
    def _apply_elastic_deformation_to_image(self, img, elastic_strength, elastic_type, interpolation):
        """
        对图片应用弹性变形的核心方法
        
        Args:
            img (PIL.Image): 要处理的图片
            elastic_strength (float): 弹性变形强度
            elastic_type (str): 弹性变形类型
            interpolation (str): 插值方法
        
        Returns:
            PIL.Image: 变形后的图片
        """
        # 获取插值方法
        interp_method = self.interpolation_methods.get(interpolation, Image.LANCZOS)
        
        width, height = img.size
        
        # 根据变形类型应用不同的变形
        if elastic_type == 'horizontal':
            # 水平弹性变形（瘦身效果）
            transformed_img = self._horizontal_elastic_deformation(img, elastic_strength, interp_method)
        elif elastic_type == 'vertical':
            # 垂直弹性变形
            transformed_img = self._vertical_elastic_deformation(img, elastic_strength, interp_method)
        elif elastic_type == 'both':
            # 双向弹性变形
            transformed_img = self._bidirectional_elastic_deformation(img, elastic_strength, interp_method)
        elif elastic_type == 'wave':
            # 波浪形变形
            transformed_img = self._wave_deformation(img, elastic_strength, interp_method)
        elif elastic_type == 'spiral':
            # 螺旋形变形
            transformed_img = self._spiral_deformation(img, elastic_strength, interp_method)
        else:
            print(f"警告：不支持的弹性变形类型 '{elastic_type}'，使用水平变形")
            transformed_img = self._horizontal_elastic_deformation(img, elastic_strength, interp_method)
        
        return transformed_img
    
    def _horizontal_elastic_deformation(self, img, strength, interp_method):
        """水平弹性变形（瘦身效果）"""
        width, height = img.size
        
        # 计算新的宽度（水平压缩） - 增强强度影响
        compression_factor = 1 - strength * 0.5  # 增加压缩比例
        new_width = int(width * compression_factor)
        
        if new_width <= 0:
            new_width = 1
        
        # 使用resize进行水平压缩
        compressed_img = img.resize((new_width, height), interp_method)
        
        # 如果需要保持原始尺寸，可以添加背景填充
        if new_width < width:
            # 创建背景（使用图片边缘颜色）
            background = Image.new(img.mode, (width, height), img.getpixel((0, 0)))
            
            # 将压缩后的图片居中放置
            paste_x = (width - new_width) // 2
            background.paste(compressed_img, (paste_x, 0))
            return background
        
        return compressed_img
    
    def _vertical_elastic_deformation(self, img, strength, interp_method):
        """垂直弹性变形"""
        width, height = img.size
        
        # 计算新的高度（垂直压缩） - 增强强度影响
        compression_factor = 1 - strength * 0.5  # 增加压缩比例
        new_height = int(height * compression_factor)
        
        if new_height <= 0:
            new_height = 1
        
        # 使用resize进行垂直压缩
        compressed_img = img.resize((width, new_height), interp_method)
        
        # 如果需要保持原始尺寸，可以添加背景填充
        if new_height < height:
            # 创建背景（使用图片边缘颜色）
            background = Image.new(img.mode, (width, height), img.getpixel((0, 0)))
            
            # 将压缩后的图片居中放置
            paste_y = (height - new_height) // 2
            background.paste(compressed_img, (0, paste_y))
            return background
        
        return compressed_img
    
    def _bidirectional_elastic_deformation(self, img, strength, interp_method):
        """双向弹性变形"""
        # 先进行水平变形
        horizontal_img = self._horizontal_elastic_deformation(img, strength * 0.7, interp_method)
        # 再进行垂直变形
        final_img = self._vertical_elastic_deformation(horizontal_img, strength * 0.7, interp_method)
        
        return final_img
    
    def _wave_deformation(self, img, strength, interp_method):
        """波浪形变形"""
        width, height = img.size
        
        # 创建波浪效果 - 使用多次resize和轻微旋转来模拟
        wave_img = img.copy()
        
        # 应用波浪扭曲 - 增强强度影响
        wave_amplitude = int(strength * 20)  # 增加波浪幅度
        if wave_amplitude > 0:
            # 根据强度调整切片数量
            num_slices = max(10, int(20 * strength))  # 强度越大，切片越多
            slice_height = max(1, height // num_slices)
            
            for i in range(0, height, slice_height):
                end_y = min(i + slice_height, height)
                
                # 提取切片
                slice_img = wave_img.crop((0, i, width, end_y))
                
                # 计算波浪偏移 - 增强波浪效果
                wave_offset = int(wave_amplitude * math.sin(i * 0.2 * strength))  # 增加频率和强度
                
                # 创建新的切片位置
                new_x = max(0, min(width - slice_img.width, wave_offset))
                
                # 将切片粘贴到新位置
                if new_x != 0:
                    # 创建临时画布
                    temp_canvas = Image.new(wave_img.mode, (width, slice_img.height))
                    temp_canvas.paste(slice_img, (new_x, 0))
                    wave_img.paste(temp_canvas, (0, i))
        
        return wave_img
    
    def _spiral_deformation(self, img, strength, interp_method):
        """螺旋形变形"""
        width, height = img.size
        
        # 创建螺旋效果 - 使用旋转和缩放来模拟
        spiral_img = img.copy()
        
        # 应用螺旋扭曲 - 增强强度影响
        spiral_factor = strength * 2.0  # 增加强度倍数
        
        if spiral_factor > 0:
            # 将图片分成多个同心圆区域
            center_x, center_y = width // 2, height // 2
            max_radius = min(width, height) // 2
            
            # 根据强度调整环的数量
            num_rings = max(5, int(10 * strength))  # 强度越大，环数越多
            ring_width = max_radius // num_rings
            
            for ring in range(num_rings):
                inner_radius = ring * ring_width
                outer_radius = (ring + 1) * ring_width
                
                if inner_radius >= max_radius:
                    break
                
                # 计算这个环的旋转角度 - 增强角度计算
                rotation_angle = spiral_factor * ring * 10  # 增加角度倍数
                
                # 降低角度阈值，让更多旋转生效
                if abs(rotation_angle) > 0.5:  # 降低阈值
                    # 提取环形区域
                    ring_img = self._extract_ring(img, center_x, center_y, inner_radius, outer_radius)
                    
                    if ring_img:
                        # 旋转环形区域
                        rotated_ring = ring_img.rotate(rotation_angle, expand=False, fillcolor=(0, 0, 0, 0))
                        
                        # 将旋转后的环形区域粘贴回去
                        spiral_img.paste(rotated_ring, (center_x - outer_radius, center_y - outer_radius), rotated_ring)
        
        return spiral_img
    
    def _extract_ring(self, img, center_x, center_y, inner_radius, outer_radius):
        """提取环形区域"""
        width, height = img.size
        
        # 创建掩码
        mask = Image.new('L', (width, height), 0)
        
        # 绘制环形掩码
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        
        # 绘制外圆
        draw.ellipse([center_x - outer_radius, center_y - outer_radius, 
                     center_x + outer_radius, center_y + outer_radius], fill=255)
        
        # 绘制内圆（挖空）
        if inner_radius > 0:
            draw.ellipse([center_x - inner_radius, center_y - inner_radius, 
                         center_x + inner_radius, center_y + inner_radius], fill=0)
        
        # 应用掩码
        ring_img = img.copy()
        ring_img.putalpha(mask)
        
        return ring_img
    
    def elastic_deform_all_images(self, elastic_strength=0.3, elastic_type='horizontal', 
                                 preserve_transparency=True, backup=True, 
                                 recursive=True, interpolation='LANCZOS', quality=95):
        """
        对文件夹中的所有图片执行弹性变形处理并直接替换原文件
        
        Args:
            elastic_strength (float): 弹性变形强度 (0.1-1.0)
            elastic_type (str): 弹性变形类型 ('horizontal', 'vertical', 'both', 'wave', 'spiral')
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
        print(f"弹性变形参数：类型={elastic_type}, 强度={elastic_strength}")
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
            
            # 应用弹性变形
            if self.apply_elastic_deformation(image_path, elastic_strength, elastic_type, 
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
    def elastic_deform_folder_images(folder_path, elastic_strength=0.3, elastic_type='horizontal',
                                   preserve_transparency=True, backup=True, 
                                   recursive=True, interpolation='LANCZOS', quality=95):
        """
        静态方法：直接对指定文件夹中的图片执行弹性变形处理并替换
        
        Args:
            folder_path (str): 要处理的文件夹路径
            elastic_strength (float): 弹性变形强度 (0.1-1.0)
            elastic_type (str): 弹性变形类型 ('horizontal', 'vertical', 'both', 'wave', 'spiral')
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
            interpolation (str): 插值方法
            quality (int): 输出图片质量 (1-100)
        """
        # 创建一个处理器实例
        processor = ImageElasticProcessor(folder_path)
        processor.elastic_deform_all_images(elastic_strength, elastic_type, 
                                          preserve_transparency, backup, 
                                          recursive, interpolation, quality)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片弹性变形处理工具')
    parser.add_argument('folder_path', 
                       help='要处理的文件夹路径')
    parser.add_argument('--strength', '-s', type=float, default=DEBUG_ELASTIC_STRENGTH,
                       help=f'弹性变形强度 (0.1-1.0, 默认: {DEBUG_ELASTIC_STRENGTH})')
    parser.add_argument('--type', '-t', 
                       choices=['horizontal', 'vertical', 'both', 'wave', 'spiral'], 
                       default=DEBUG_ELASTIC_TYPE,
                       help=f'弹性变形类型 (默认: {DEBUG_ELASTIC_TYPE})')
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
    if not (0.1 <= args.strength <= 1.0):
        print("错误：弹性变形强度必须在 0.1-1.0 之间")
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
        ImageElasticProcessor.elastic_deform_folder_images(
            args.folder_path,
            elastic_strength=args.strength,
            elastic_type=args.type,
            preserve_transparency=not args.no_preserve_transparency,
            backup=not args.no_backup,
            recursive=not args.no_recursive,
            interpolation=args.interpolation,
            quality=args.quality
        )
    except Exception as e:
        print(f"错误：{e}")

def elastic_demo():
    """弹性变形效果演示"""
    print("=== 图片弹性变形处理工具 ===")
    print("使用调试参数进行演示...")
    
    print(f"将对文件夹 {DEBUG_FOLDER_PATH} 中的图片进行弹性变形处理并替换原文件...")
    print(f"调试参数：强度={DEBUG_ELASTIC_STRENGTH}, 类型={DEBUG_ELASTIC_TYPE}")
    print(f"插值方法：{DEBUG_INTERPOLATION}, 质量：{DEBUG_QUALITY}")
    
    try:
        # 使用静态方法直接处理
        ImageElasticProcessor.elastic_deform_folder_images(
            folder_path=DEBUG_FOLDER_PATH,
            elastic_strength=DEBUG_ELASTIC_STRENGTH,
            elastic_type=DEBUG_ELASTIC_TYPE,
            preserve_transparency=DEBUG_PRESERVE_TRANSPARENCY,
            backup=DEBUG_BACKUP,
            recursive=DEBUG_RECURSIVE,
            interpolation=DEBUG_INTERPOLATION,
            quality=DEBUG_QUALITY
        )
        
        print("\n演示完成！")
        print("你可以使用以下命令进行自定义处理：")
        print("python image_elastic_tool.py /path/to/folder --strength 0.5 --type horizontal")
        print("python image_elastic_tool.py /path/to/folder --no-backup --strength 0.7 --type wave")
        print("\n💡 提示：")
        print("- horizontal: 水平弹性变形（瘦身效果）")
        print("- vertical: 垂直弹性变形")
        print("- both: 双向弹性变形")
        print("- wave: 波浪形变形")
        print("- spiral: 螺旋形变形")
        
    except Exception as e:
        print(f"演示失败：{e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有命令行参数，运行演示
        elastic_demo()
    else:
        # 有命令行参数，使用argparse处理
        main()
