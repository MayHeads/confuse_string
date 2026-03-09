#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swift文件恢复工具
将混淆的注释格式恢复为原始字符串格式
"""

import os
import re
import sys
from pathlib import Path

# ==================== 调试参数配置 ====================
# 方便调试时快速修改参数，无需修改代码内部
DEBUG_FOLDER_PATH = '/Users/jiangshanchen/TSComposs'  # 要处理的文件夹路径

DEBUG_BACKUP = False              # 是否创建备份文件
DEBUG_RECURSIVE = True           # 是否递归查找子文件夹
# =====================================================

class SwiftRecoverProcessor:
    """Swift文件恢复处理器"""
    
    def __init__(self, folder_path, backup=True, recursive=True):
        """
        初始化恢复处理器
        
        Args:
            folder_path (str): 要处理的文件夹路径
            backup (bool): 是否创建备份文件
            recursive (bool): 是否递归查找子文件夹
        """
        self.folder_path = Path(folder_path)
        self.backup = backup
        self.recursive = recursive
        self.processed_files = 0
        self.recovered_patterns = 0
        
    def clean_backup_files(self):
        """清理所有备份文件"""
        print("🧹 开始清理备份文件...")
        
        backup_files = []
        if self.recursive:
            # 递归查找所有备份文件
            pattern = "**/*.swift.backup"
            backup_files = list(self.folder_path.glob(pattern))
        else:
            # 只查找当前目录的备份文件
            backup_files = list(self.folder_path.glob("*.swift.backup"))
        
        if backup_files:
            print(f"📁 找到 {len(backup_files)} 个备份文件")
            for backup_file in backup_files:
                try:
                    backup_file.unlink()  # 删除文件
                    print(f"  🗑️  已删除: {backup_file.relative_to(self.folder_path)}")
                except Exception as e:
                    print(f"  ❌ 删除失败: {backup_file.name} - {e}")
            print(f"✅ 备份文件清理完成，删除了 {len(backup_files)} 个文件")
        else:
            print("ℹ️  未找到备份文件")
        print()
    
    def find_swift_files(self):
        """查找所有Swift文件"""
        swift_files = []
        
        if self.recursive:
            # 递归查找所有Swift文件
            pattern = "**/*.swift"
            swift_files = list(self.folder_path.glob(pattern))
        else:
            # 只查找当前目录的Swift文件
            swift_files = list(self.folder_path.glob("*.swift"))
        
        return swift_files
    
    def create_backup(self, file_path):
        """创建备份文件"""
        if self.backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            if not backup_path.exists():
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"  📁 已创建备份: {backup_path.name}")
    
    def recover_swift_content(self, content):
        """
        恢复Swift文件内容
        
        Args:
            content (str): 文件内容
            
        Returns:
            tuple: (恢复后的内容, 恢复的模式数量)
        """
        recovered_content = content
        pattern_count = 0
        
     
        pattern = r'/\*([^*]+)\*/"([^"]+)"\.[a-zA-Z_][a-zA-Z0-9_]*\(\)'
        
        def replace_pattern(match):
            nonlocal pattern_count
            pattern_count += 1
            
            # 提取注释内容和加密字符串
            comment_content = match.group(1).strip()
            encrypted_string = match.group(2)
            
            # 恢复为原始字符串格式
            recovered = f'"{comment_content}"'
            
            print(f"    🔄 恢复模式 {pattern_count}:")
            print(f"       原始: {match.group(0)}")
            print(f"       恢复: {recovered}")
            
            return recovered
        
        # 执行替换
        recovered_content = re.sub(pattern, replace_pattern, recovered_content)
        
        return recovered_content, pattern_count
    
    def process_file(self, file_path):
        """处理单个Swift文件"""
        try:
            print(f"📄 处理文件: {file_path.relative_to(self.folder_path)}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 创建备份
            self.create_backup(file_path)
            
            # 恢复内容
            recovered_content, pattern_count = self.recover_swift_content(original_content)
            
            if pattern_count > 0:
                # 写入恢复后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(recovered_content)
                
                print(f"  ✅ 成功恢复 {pattern_count} 个模式")
                self.recovered_patterns += pattern_count
            else:
                print(f"  ℹ️  未找到需要恢复的模式")
            
            self.processed_files += 1
            
        except Exception as e:
            print(f"  ❌ 处理文件时出错: {e}")
    
    def process_all_files(self):
        """处理所有Swift文件"""
        # 首先清理备份文件
        self.clean_backup_files()
        
        print("🔍 开始查找Swift文件...")
        
        swift_files = self.find_swift_files()
        
        if not swift_files:
            print("❌ 未找到任何Swift文件")
            return
        
        print(f"📁 找到 {len(swift_files)} 个Swift文件")
        print("=" * 60)
        
        for file_path in swift_files:
            self.process_file(file_path)
            print()
        
        print("=" * 60)
        print(f"🎉 处理完成！")
        print(f"📊 统计信息:")
        print(f"   - 处理文件数: {self.processed_files}")
        print(f"   - 恢复模式数: {self.recovered_patterns}")
        
        if self.backup:
            print(f"💾 备份文件已创建，扩展名为 .backup")

def recover_demo():
    """Swift文件恢复演示"""
    print("=== Swift文件恢复工具 ===")
    print("使用调试参数进行演示...")
    
    print(f"目标文件夹: {DEBUG_FOLDER_PATH}")
    print(f"备份模式: {'开启' if DEBUG_BACKUP else '关闭'}")
    print(f"递归模式: {'开启' if DEBUG_RECURSIVE else '关闭'}")
    print()
    
    # 检查文件夹是否存在
    if not os.path.exists(DEBUG_FOLDER_PATH):
        print(f"❌ 文件夹不存在: {DEBUG_FOLDER_PATH}")
        return
    
    # 创建处理器
    processor = SwiftRecoverProcessor(
        folder_path=DEBUG_FOLDER_PATH,
        backup=DEBUG_BACKUP,
        recursive=DEBUG_RECURSIVE
    )
    
    # 处理所有文件
    processor.process_all_files()

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        folder_path = sys.argv[1]
        backup = '--no-backup' not in sys.argv
        recursive = '--no-recursive' not in sys.argv
        
        processor = SwiftRecoverProcessor(folder_path, backup, recursive)
        processor.process_all_files()
    else:
        # 演示模式
        recover_demo()

if __name__ == "__main__":
    main()