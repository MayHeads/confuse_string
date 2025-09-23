#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片轮廓增强效果处理工具
使用Pillow库为图片添加可调节的轮廓增强效果
"""

import os
import sys
from PIL import Image, ImageFilter, ImageEnhance
import argparse
from pathlib import Path

# ==================== 调试参数配置 ====================
# 方便调试时快速修改参数，无需修改代码内部
DEBUG_FOLDER_PATH = '/Users/jiangshanchen/TSComposs/TSComposs/Resource/Assets.xcassets'  # 要处理的文件夹路径
DEBUG_CONTOUR_STRENGTH = 3.0      # 轮廓增强强度 (0.1-5.0)
DEBUG_CONTOUR_TYPE = 'enhance'    # 轮廓增强类型 ('edge_enhance', 'edge_enhance_more', 'find_edges', 'emboss', 'contour', 'enhance')
DEBUG_PRESERVE_TRANSPARENCY = True  # 是否保持透明区域不变
DEBUG_BACKUP = False              # 是否创建备份文件
DEBUG_RECURSIVE = True            # 是否递归查找子文件夹
DEBUG_QUALITY = 95                # 输出图片质量 (1-100)
# =====================================================

class ImageContourProcessor:
    """图片轮廓增强处理器"""
    
    def __init__(self, folder_path):
        """
        初始化图片轮廓增强处理器
        
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
    
    def apply_contour_enhancement(self, image_path, contour_strength=1.5, contour_type='edge_enhance', 
                                 preserve_transparency=True, backup=True):
        """
        对单张图片应用轮廓增强效果
        
        Args:
            image_path (Path): 图片文件路径
            contour_strength (float): 轮廓增强强度 (0.1-5.0)
            contour_type (str): 轮廓增强类型 ('edge_enhance', 'edge_enhance_more', 'find_edges', 'emboss', 'contour')
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
                    
                    # 将RGB通道合并为RGB图像进行轮廓增强处理
                    rgb_img = Image.merge('RGB', rgb_channels)
                    
                    # 应用轮廓增强效果
                    enhanced_rgb = self._apply_contour_to_image(rgb_img, contour_strength, contour_type)
                    
                    # 将增强后的RGB与原始Alpha通道合并
                    enhanced_channels = enhanced_rgb.split()
                    final_img = Image.merge('RGBA', enhanced_channels + (alpha_channel,))
                    
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
                    
                    # 应用轮廓增强效果
                    final_img = self._apply_contour_to_image(img, contour_strength, contour_type)
                
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
    
    def _apply_contour_to_image(self, img, contour_strength, contour_type):
        """
        对图片应用轮廓增强效果的核心方法
        
        Args:
            img (PIL.Image): 要处理的图片
            contour_strength (float): 轮廓增强强度
            contour_type (str): 轮廓增强类型
        
        Returns:
            PIL.Image: 轮廓增强后的图片
        """
        if contour_type == 'edge_enhance':
            # 边缘增强
            return self._edge_enhance(img, contour_strength)
        elif contour_type == 'edge_enhance_more':
            # 强边缘增强
            return self._edge_enhance_more(img, contour_strength)
        elif contour_type == 'find_edges':
            # 查找边缘
            return self._find_edges(img, contour_strength)
        elif contour_type == 'emboss':
            # 浮雕效果
            return self._emboss(img, contour_strength)
        elif contour_type == 'contour':
            # 轮廓效果
            return self._contour(img, contour_strength)
        elif contour_type == 'enhance':
            # 使用PIL的增强器
            return self._enhance_contour(img, contour_strength)
        else:
            print(f"警告：不支持的轮廓增强类型 '{contour_type}'，使用边缘增强")
            return self._edge_enhance(img, contour_strength)
    
    def _edge_enhance(self, img, strength):
        """边缘增强"""
        # 使用PIL的内置边缘增强滤镜
        enhanced = img.filter(ImageFilter.EDGE_ENHANCE)
        
        # 根据强度调整效果
        if strength > 1.0:
            # 多次应用边缘增强滤镜
            for _ in range(int(strength)):
                enhanced = enhanced.filter(ImageFilter.EDGE_ENHANCE)
        
        return enhanced
    
    def _edge_enhance_more(self, img, strength):
        """强边缘增强"""
        # 使用PIL的内置强边缘增强滤镜
        enhanced = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # 根据强度调整效果
        if strength > 1.0:
            for _ in range(int(strength)):
                enhanced = enhanced.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        return enhanced
    
    def _find_edges(self, img, strength):
        """查找边缘"""
        # 使用PIL的内置边缘检测滤镜
        edges = img.filter(ImageFilter.FIND_EDGES)
        
        # 根据强度调整效果
        if strength > 1.0:
            # 增强对比度来模拟强度调整
            enhancer = ImageEnhance.Contrast(edges)
            edges = enhancer.enhance(strength)
        
        return edges
    
    def _emboss(self, img, strength):
        """浮雕效果"""
        # 使用PIL的内置浮雕滤镜
        embossed = img.filter(ImageFilter.EMBOSS)
        
        # 根据强度调整效果
        if strength > 1.0:
            # 增强对比度来模拟强度调整
            enhancer = ImageEnhance.Contrast(embossed)
            embossed = enhancer.enhance(strength)
        
        return embossed
    
    def _contour(self, img, strength):
        """轮廓效果"""
        # 使用PIL的内置轮廓滤镜
        contoured = img.filter(ImageFilter.CONTOUR)
        
        # 根据强度调整效果
        if strength > 1.0:
            # 增强对比度来模拟强度调整
            enhancer = ImageEnhance.Contrast(contoured)
            contoured = enhancer.enhance(strength)
        
        return contoured
    
    def _enhance_contour(self, img, strength):
        """使用PIL增强器进行轮廓增强"""
        # 先应用边缘增强
        edge_enhanced = img.filter(ImageFilter.EDGE_ENHANCE)
        
        # 再增强对比度
        contrast_enhancer = ImageEnhance.Contrast(edge_enhanced)
        enhanced = contrast_enhancer.enhance(strength)
        
        return enhanced
    
    def enhance_all_images(self, contour_strength=1.5, contour_type='edge_enhance', 
                          preserve_transparency=True, backup=True, recursive=True):
        """
        对文件夹中的所有图片执行轮廓增强处理并直接替换原文件
        
        Args:
            contour_strength (float): 轮廓增强强度 (0.1-5.0)
            contour_type (str): 轮廓增强类型 ('edge_enhance', 'edge_enhance_more', 'find_edges', 'emboss', 'contour', 'enhance')
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
        print(f"轮廓增强参数：类型={contour_type}, 强度={contour_strength}")
        print(f"备份模式：{'开启' if backup else '关闭'}")
        print(f"递归模式：{'开启' if recursive else '关闭'}")
        print(f"保持透明度：{'开启' if preserve_transparency else '关闭'}")
        
        success_count = 0
        
        for image_path in image_files:
            # 显示相对路径，更清晰地显示文件位置
            relative_path = image_path.relative_to(self.folder_path)
            print(f"正在处理: {relative_path}")
            
            # 应用轮廓增强效果
            if self.apply_contour_enhancement(image_path, contour_strength, contour_type, 
                                            preserve_transparency, backup):
                print(f"  ✓ 已替换原文件: {relative_path}")
                success_count += 1
            else:
                print(f"  ✗ 处理失败")
        
        print(f"\n处理完成！成功处理 {success_count}/{len(image_files)} 张图片")
        
        if backup and success_count > 0:
            print(f"💡 提示：备份文件已保存，如需恢复原图，请将 .backup 文件重命名")
    
    @staticmethod
    def enhance_folder_images(folder_path, contour_strength=1.5, contour_type='edge_enhance',
                            preserve_transparency=True, backup=True, recursive=True):
        """
        静态方法：直接对指定文件夹中的图片执行轮廓增强处理并替换
        
        Args:
            folder_path (str): 要处理的文件夹路径
            contour_strength (float): 轮廓增强强度 (0.1-5.0)
            contour_type (str): 轮廓增强类型 ('edge_enhance', 'edge_enhance_more', 'find_edges', 'emboss', 'contour', 'enhance')
            preserve_transparency (bool): 是否保持透明区域不变
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹中的图片
        """
        # 创建一个处理器实例
        processor = ImageContourProcessor(folder_path)
        processor.enhance_all_images(contour_strength, contour_type, 
                                   preserve_transparency, backup, recursive)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片轮廓增强效果处理工具')
    parser.add_argument('folder_path', 
                       help='要处理的文件夹路径')
    parser.add_argument('--strength', '-s', type=float, default=1.5,
                       help='轮廓增强强度 (0.1-5.0, 默认: 1.5)')
    parser.add_argument('--type', '-t', 
                       choices=['edge_enhance', 'edge_enhance_more', 'find_edges', 'emboss', 'contour', 'enhance'], 
                       default='edge_enhance',
                       help='轮廓增强类型 (默认: edge_enhance)')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件（危险操作）')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归查找子文件夹中的图片（默认递归查找）')
    parser.add_argument('--no-preserve-transparency', action='store_true',
                       help='不保持透明区域不变（默认保持透明度）')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.strength < 0.1 or args.strength > 5.0:
        print("错误：轮廓增强强度必须在 0.1-5.0 之间")
        return
    
    if not args.no_backup:
        print("⚠️ 警告：你选择了创建备份的替换模式，原文件将被修改！")
        confirm = input("确认继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
    
    try:
        # 使用静态方法直接处理指定文件夹
        ImageContourProcessor.enhance_folder_images(
            args.folder_path,
            contour_strength=args.strength,
            contour_type=args.type,
            preserve_transparency=not args.no_preserve_transparency,
            backup=not args.no_backup,
            recursive=not args.no_recursive
        )
    except Exception as e:
        print(f"错误：{e}")

def contour_demo():
    """轮廓增强效果演示"""
    print("=== 图片轮廓增强效果处理工具 ===")
    print("使用调试参数进行演示...")
    
    print(f"将对文件夹 {DEBUG_FOLDER_PATH} 中的图片进行轮廓增强处理并替换原文件...")
    print(f"调试参数：强度={DEBUG_CONTOUR_STRENGTH}, 类型={DEBUG_CONTOUR_TYPE}")
    print(f"备份模式：{'开启' if DEBUG_BACKUP else '关闭'}, 递归模式：{'开启' if DEBUG_RECURSIVE else '关闭'}")
    
    try:
        # 使用静态方法直接处理
        ImageContourProcessor.enhance_folder_images(
            folder_path=DEBUG_FOLDER_PATH,
            contour_strength=DEBUG_CONTOUR_STRENGTH,
            contour_type=DEBUG_CONTOUR_TYPE,
            preserve_transparency=DEBUG_PRESERVE_TRANSPARENCY,
            backup=DEBUG_BACKUP,
            recursive=DEBUG_RECURSIVE
        )
        
        print("\n演示完成！")
        print("你可以使用以下命令进行自定义处理：")
        print("python image_contour_tool.py /path/to/folder --strength 2.0 --type edge_enhance")
        print("python image_contour_tool.py /path/to/folder --no-backup --strength 3.0 --type emboss")
        
    except Exception as e:
        print(f"演示失败：{e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有命令行参数，运行演示
        contour_demo()
    else:
        # 有命令行参数，使用argparse处理
        main()
