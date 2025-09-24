#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理工具合并执行器
整合所有图像处理工具，统一配置管理
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径，以便导入其他工具
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入所有图像处理工具
from image_sharpen_tool import sharpen_demo
from image_blur_tool import simple_blur_demo
from image_affine_tool import affine_demo
from image_contour_tool import contour_demo
from image_filter_tool import filter_demo
from image_elastic_tool import elastic_demo

# ==================== 统一配置参数 ====================
# 通用配置参数（所有工具共用）
COMMON_FOLDER_PATH = '/Users/jiangshanchen/TSComposs/TSComposs/Resource/Assets.xcassets'  # 要处理的文件夹路径
COMMON_PRESERVE_TRANSPARENCY = True  # 是否保持透明区域不变
COMMON_BACKUP = False                # 是否创建备份文件
COMMON_RECURSIVE = True              # 是否递归查找子文件夹
COMMON_QUALITY = 95                  # 输出图片质量 (1-100)

# 仿射变换工具配置
SCALE_X = 0.95                       # X轴缩放比例 (0.1-2.0, 小于1为瘦身，大于1为拉伸)  最好是0.9 - 0.99 不要进行参数太小
SCALE_Y = 1.0                        # Y轴缩放比例 (0.1-2.0, 小于1为瘦身，大于1为拉伸)
INTERPOLATION = 'BICUBIC'            # 插值方法 ('NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS')


# 滤镜工具配置
FILTER_TYPE = 'sepia'               # 滤镜类型 ('red_black', 'sepia', 'vintage', 'high_contrast', 'invert', 'grayscale')  invert不好用
FILTER_STRENGTH = 3.0                # 滤镜强度 (0.1-3.0)   这个参数生效

# 模糊工具配置
BLUR_RADIUS = 2.5                      # 模糊半径 (1-20, 数值越大越模糊)  1.5-3   5太大了
BLUR_TYPE = 'gaussian'               # 模糊类型 ('gaussian', 'box', 'median')

# 弹性变形工具配置
ELASTIC_STRENGTH = 0.8               # 弹性变形强度 (0.1-1.0, 数值越大变形越明显)
ELASTIC_TYPE = 'wave'                # 弹性变形类型 ('horizontal', 'vertical', 'both', 'wave', 'spiral')


# 锐化工具配置
SHARPEN_STRENGTH = 200               # 锐化强度 (0.1-5.0)
SHARPEN_TYPE = 'unsharp_mask'        # 锐化类型 ('unsharp_mask', 'sharpen', 'detail', 'enhance')



# 轮廓增强工具配置
CONTOUR_STRENGTH = 3.0               # 轮廓增强强度 (0.1-5.0)
CONTOUR_TYPE = 'enhance'             # 轮廓增强类型 ('edge_enhance', 'edge_enhance_more', 'find_edges', 'emboss', 'contour', 'enhance')




# =====================================================

def update_tool_configs():
    """更新所有工具的配置参数"""
    
    # 更新锐化工具配置
    import image_sharpen_tool
    image_sharpen_tool.DEBUG_FOLDER_PATH = COMMON_FOLDER_PATH
    image_sharpen_tool.DEBUG_SHARPEN_STRENGTH = SHARPEN_STRENGTH
    image_sharpen_tool.DEBUG_SHARPEN_TYPE = SHARPEN_TYPE
    image_sharpen_tool.DEBUG_PRESERVE_TRANSPARENCY = COMMON_PRESERVE_TRANSPARENCY
    image_sharpen_tool.DEBUG_BACKUP = COMMON_BACKUP
    image_sharpen_tool.DEBUG_RECURSIVE = COMMON_RECURSIVE
    image_sharpen_tool.DEBUG_QUALITY = COMMON_QUALITY
    
    # 更新模糊工具配置
    import image_blur_tool
    image_blur_tool.DEBUG_FOLDER_PATH = COMMON_FOLDER_PATH
    image_blur_tool.DEBUG_ORIGIN_FOLDER = COMMON_FOLDER_PATH  # 模糊工具需要的额外变量
    image_blur_tool.DEBUG_OUTPUT_FOLDER = COMMON_FOLDER_PATH  # 模糊工具需要的额外变量
    image_blur_tool.DEBUG_BLUR_RADIUS = BLUR_RADIUS
    image_blur_tool.DEBUG_BLUR_TYPE = BLUR_TYPE
    image_blur_tool.DEBUG_QUALITY = COMMON_QUALITY
    image_blur_tool.DEBUG_PRESERVE_TRANSPARENCY = COMMON_PRESERVE_TRANSPARENCY
    image_blur_tool.DEBUG_BACKUP = COMMON_BACKUP
    image_blur_tool.DEBUG_RECURSIVE = COMMON_RECURSIVE
    
    # 更新仿射变换工具配置
    import image_affine_tool
    image_affine_tool.DEBUG_FOLDER_PATH = COMMON_FOLDER_PATH
    image_affine_tool.DEBUG_SCALE_X = SCALE_X
    image_affine_tool.DEBUG_SCALE_Y = SCALE_Y
    image_affine_tool.DEBUG_PRESERVE_TRANSPARENCY = COMMON_PRESERVE_TRANSPARENCY
    image_affine_tool.DEBUG_BACKUP = COMMON_BACKUP
    image_affine_tool.DEBUG_RECURSIVE = COMMON_RECURSIVE
    image_affine_tool.DEBUG_QUALITY = COMMON_QUALITY
    image_affine_tool.DEBUG_INTERPOLATION = INTERPOLATION
    
    # 更新轮廓增强工具配置
    import image_contour_tool
    image_contour_tool.DEBUG_FOLDER_PATH = COMMON_FOLDER_PATH
    image_contour_tool.DEBUG_CONTOUR_STRENGTH = CONTOUR_STRENGTH
    image_contour_tool.DEBUG_CONTOUR_TYPE = CONTOUR_TYPE
    image_contour_tool.DEBUG_PRESERVE_TRANSPARENCY = COMMON_PRESERVE_TRANSPARENCY
    image_contour_tool.DEBUG_BACKUP = COMMON_BACKUP
    image_contour_tool.DEBUG_RECURSIVE = COMMON_RECURSIVE
    image_contour_tool.DEBUG_QUALITY = COMMON_QUALITY
    
    # 更新滤镜工具配置
    import image_filter_tool
    image_filter_tool.DEBUG_FOLDER_PATH = COMMON_FOLDER_PATH
    image_filter_tool.DEBUG_FILTER_TYPE = FILTER_TYPE
    image_filter_tool.DEBUG_FILTER_STRENGTH = FILTER_STRENGTH
    image_filter_tool.DEBUG_PRESERVE_TRANSPARENCY = COMMON_PRESERVE_TRANSPARENCY
    image_filter_tool.DEBUG_BACKUP = COMMON_BACKUP
    image_filter_tool.DEBUG_RECURSIVE = COMMON_RECURSIVE
    image_filter_tool.DEBUG_QUALITY = COMMON_QUALITY
    
    # 更新弹性变形工具配置
    import image_elastic_tool
    image_elastic_tool.DEBUG_FOLDER_PATH = COMMON_FOLDER_PATH
    image_elastic_tool.DEBUG_ELASTIC_STRENGTH = ELASTIC_STRENGTH
    image_elastic_tool.DEBUG_ELASTIC_TYPE = ELASTIC_TYPE
    image_elastic_tool.DEBUG_PRESERVE_TRANSPARENCY = COMMON_PRESERVE_TRANSPARENCY
    image_elastic_tool.DEBUG_BACKUP = COMMON_BACKUP
    image_elastic_tool.DEBUG_RECURSIVE = COMMON_RECURSIVE
    image_elastic_tool.DEBUG_QUALITY = COMMON_QUALITY
    image_elastic_tool.DEBUG_INTERPOLATION = INTERPOLATION

def run_sharpen():
    """执行锐化处理"""
    print("🔍 开始执行锐化处理...")
    update_tool_configs()
    sharpen_demo()
    print("✅ 锐化处理完成！\n")

def run_blur():
    """执行模糊处理"""
    print("🌫️ 开始执行模糊处理...")
    update_tool_configs()
    simple_blur_demo()
    print("✅ 模糊处理完成！\n")

def run_affine():
    """执行仿射变换处理"""
    print("📐 开始执行仿射变换处理...")
    update_tool_configs()
    affine_demo()
    print("✅ 仿射变换处理完成！\n")

def run_contour():
    """执行轮廓增强处理"""
    print("🎨 开始执行轮廓增强处理...")
    update_tool_configs()
    contour_demo()
    print("✅ 轮廓增强处理完成！\n")

def run_filter():
    """执行滤镜处理"""
    print("🎭 开始执行滤镜处理...")
    update_tool_configs()
    filter_demo()
    print("✅ 滤镜处理完成！\n")

def run_elastic():
    """执行弹性变形处理"""
    print("🌀 开始执行弹性变形处理...")
    update_tool_configs()
    elastic_demo()
    print("✅ 弹性变形处理完成！\n")

def run_all():
    """执行所有图像处理"""
    print("🚀 开始执行所有图像处理...")
    print("=" * 60)
    
    run_sharpen()
    run_blur()
    run_affine()
    run_contour()
    run_filter()
    run_elastic()
    
    print("=" * 60)
    print("🎉 所有图像处理完成！")

def custom_combin_run():
    """执行自定义组合处理"""
    print("🚀 开始执行自定义组合处理...")
    print("=" * 60)

    run_affine()
    run_filter()

    run_blur()
    run_elastic()


    
    
 

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🖼️  图像处理工具合并执行器")
    print("=" * 60)
    print("请选择要执行的处理类型：")
    print("1. 锐化处理 (Sharpen)")
    print("2. 模糊处理 (Blur)")
    print("3. 仿射变换 (Affine Transform)")
    print("4. 轮廓增强 (Contour Enhancement)")
    print("5. 滤镜处理 (Filter)")
    print("6. 弹性变形 (Elastic Deformation)")
    print("7. 执行所有处理 (Run All)")
    print("0. 退出")
    print("=" * 60)

def main():


    custom_combin_run()
    exit()

    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        tool_name = sys.argv[1].lower()
        
        if tool_name == 'sharpen':
            run_sharpen()
        elif tool_name == 'blur':
            run_blur()
        elif tool_name == 'affine':
            run_affine()
        elif tool_name == 'contour':
            run_contour()
        elif tool_name == 'filter':
            run_filter()
        elif tool_name == 'elastic':
            run_elastic()
        elif tool_name == 'all':
            run_all()
        else:
            print(f"❌ 未知的工具类型: {tool_name}")
            print("支持的类型: sharpen, blur, affine, contour, filter, elastic, all")
    else:
        # 交互模式
        while True:
            show_menu()
            try:
                choice = input("请输入选择 (0-7): ").strip()
                
                if choice == '0':
                    print("👋 再见！")
                    break
                elif choice == '1':
                    run_sharpen()
                elif choice == '2':
                    run_blur()
                elif choice == '3':
                    run_affine()
                elif choice == '4':
                    run_contour()
                elif choice == '5':
                    run_filter()
                elif choice == '6':
                    run_elastic()
                elif choice == '7':
                    run_all()
                else:
                    print("❌ 无效选择，请输入 0-7 之间的数字")
                    
            except KeyboardInterrupt:
                print("\n👋 用户取消，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
