import os
import glob
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ProjectInfo:
    """项目信息模型"""
    project_path: str
    swift_files: List[str]  # 过滤后的Swift文件
    xcodeproj_path: Optional[str]
    xcassets_paths: List[str]
    all_swift_files: List[str]  # 所有Swift文件（未过滤）
    
    def __str__(self):
        return f"""
项目路径: {self.project_path}
Swift文件数量: {len(self.swift_files)} (过滤后)
所有Swift文件数量: {len(self.all_swift_files)} (未过滤)
Xcode项目文件: {self.xcodeproj_path}
xcassets文件夹数量: {len(self.xcassets_paths)}
"""

def scan_project(project_path: str, 
                ignore_folders: List[str] = None, 
                ignore_swift_files: List[str] = None) -> ProjectInfo:
    """
    扫描项目路径，获取相关文件信息
    
    参数:
        project_path: 项目根路径
        ignore_folders: 要忽略的文件夹名称列表
        ignore_swift_files: 要忽略的特殊Swift文件名称列表
    
    返回:
        ProjectInfo: 包含项目文件信息的对象
    """
    # 默认忽略的文件夹
    if ignore_folders is None:
        ignore_folders = [
            'Pods',           # CocoaPods依赖
            'build',          # 构建目录
            'DerivedData',    # Xcode派生数据
            '.git',           # Git版本控制
            'node_modules',   # Node.js依赖
            'Carthage',       # Carthage依赖
            'fastlane',       # Fastlane配置
            '.swiftpm',       # Swift Package Manager
            'Tests',          # 测试文件夹
            'TestData',       # 测试数据
            'Documentation',  # 文档
        ]
    
    # 默认忽略的Swift文件
    if ignore_swift_files is None:
        ignore_swift_files = [
            'AppDelegate.swift',
            'SceneDelegate.swift',
            'main.swift',
            'ContentView.swift',
            'Bridging-Header.swift',
        ]
    
    if not os.path.exists(project_path):
        raise ValueError(f"项目路径不存在: {project_path}")
    
    # 1. 获取所有Swift文件（未过滤）
    all_swift_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.swift'):
                all_swift_files.append(os.path.join(root, file))
    
    # 2. 获取过滤后的Swift文件
    swift_files = []
    for root, dirs, files in os.walk(project_path):
        # 过滤掉忽略的文件夹
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        for file in files:
            if file.endswith('.swift'):
                # 检查是否是要忽略的特殊Swift文件
                if file not in ignore_swift_files:
                    swift_files.append(os.path.join(root, file))
    
    # 3. 获取xcodeproj文件路径（只取第一个）
    xcodeproj_pattern = os.path.join(project_path, '**/*.xcodeproj')
    xcodeproj_files = glob.glob(xcodeproj_pattern, recursive=True)
    xcodeproj_path = xcodeproj_files[0] if xcodeproj_files else None
    
    # 4. 获取xcassets文件夹路径
    xcassets_pattern = os.path.join(project_path, '**/*.xcassets')
    xcassets_paths = glob.glob(xcassets_pattern, recursive=True)
    
    return ProjectInfo(
        project_path=project_path,
        swift_files=swift_files,
        xcodeproj_path=xcodeproj_path,
        xcassets_paths=xcassets_paths,
        all_swift_files=all_swift_files
    )

def print_project_summary(project_info: ProjectInfo):
    """打印项目信息摘要"""
    print("=" * 60)
    print("项目扫描结果")
    print("=" * 60)
    print(project_info)
    
    if project_info.swift_files:
        print(f"\n过滤后的Swift文件列表 (前10个):")
        for i, swift_file in enumerate(project_info.swift_files[:10]):
            relative_path = os.path.relpath(swift_file, project_info.project_path)
            print(f"  {i+1}. {relative_path}")
        if len(project_info.swift_files) > 10:
            print(f"  ... 还有 {len(project_info.swift_files) - 10} 个文件")
    
    if project_info.all_swift_files:
        print(f"\n所有Swift文件列表 (前10个):")
        for i, swift_file in enumerate(project_info.all_swift_files[:10]):
            relative_path = os.path.relpath(swift_file, project_info.project_path)
            print(f"  {i+1}. {relative_path}")
        if len(project_info.all_swift_files) > 10:
            print(f"  ... 还有 {len(project_info.all_swift_files) - 10} 个文件")
    
    if project_info.xcodeproj_path:
        relative_proj = os.path.relpath(project_info.xcodeproj_path, project_info.project_path)
        print(f"\nXcode项目文件: {relative_proj}")
    
    if project_info.xcassets_paths:
        print(f"\nxcassets文件夹:")
        for i, xcassets_path in enumerate(project_info.xcassets_paths):
            relative_assets = os.path.relpath(xcassets_path, project_info.project_path)
            print(f"  {i+1}. {relative_assets}")

def scan_current_project():
    """
    扫描当前配置的项目路径
    返回项目信息对象
    """
    from config import project_path, custom_ignore_folders, custom_ignore_swift_files
    
    return scan_project(
        project_path, 
        ignore_folders=custom_ignore_folders,
        ignore_swift_files=custom_ignore_swift_files
    )

def get_project_info():
    """
    获取项目信息的简单方法
    返回项目信息对象，如果出错返回None
    """
    try:
        return scan_current_project()
    except Exception as e:
        print(f"扫描项目时出错: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    project_info = get_project_info()
    if project_info:
        print(project_info) 