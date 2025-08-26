# 生成单个 SwiftUI 文件
import os
import sys
import random
import string
from datetime import datetime
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ios_string_generate.string_gen import get_random_class_name, init_word_lists
except ImportError:
    print("错误：无法导入 'ios_string_generate.string_gen'。请确保该模块存在且路径正确。")
    sys.exit(1)

def generate_random_name(length=15):
    """生成随机文件名"""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def read_view_names():
    """读取 co_swiui_name.txt 中的视图名称"""
    view_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 "ios_log", "co_swiui_name.txt")
    try:
        with open(view_file_path, 'r', encoding='utf-8') as f:
            view_names = [line.strip() for line in f if line.strip()]
            print("\n读取到的视图名称:")
            for i, name in enumerate(view_names, 1):
                print(f"{i}. {name}")
            print(f"\n总共读取到 {len(view_names)} 个视图名称")
            return view_names
    except FileNotFoundError:
        print(f"错误：未找到视图名称文件: {view_file_path}")
        return []

def generate_combined_view(view_names):
    """生成组合视图的 Swift 代码"""
    # 生成随机类名
    try:
        init_word_lists()
        base_name = get_random_class_name()
        if not base_name:
            base_name = generate_random_name()
    except Exception as e:
        print(f"警告：生成类名失败，使用随机名称: {e}")
        base_name = generate_random_name()
    
    view_name = base_name if base_name.endswith("View") else base_name + "View"
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    print("\n开始生成组合视图，包含以下视图:")
    for i, name in enumerate(view_names, 1):
        print(f"{i}. {name}")
    
    # 生成视图代码
    content = f"""import SwiftUI

// Generated on: {current_date}
// Combined Views: {', '.join(view_names)}

struct {view_name}: View {{
    var body: some View {{
        ScrollView {{
            VStack(spacing: 30) {{
"""
    
    # 添加每个视图
    for view in view_names:
        content += f"""
                // {view}
                VStack {{
                    Text("{view}")
                        .font(.headline)
                        .padding(.bottom, 5)
                    {view}()
                }}
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(10)
"""
    
    # 添加文件结尾
    content += f"""
            }}
            .padding()
        }}
        .navigationTitle("Combined Views")
    }}
}}

// Preview provider
struct {view_name}_Previews: PreviewProvider {{
    static var previews: some View {{
        NavigationView {{
            {view_name}()
        }}
    }}
}}
"""
    
    return view_name, content

def single_swifui():
    # 1. 读取视图名称
    view_names = read_view_names()
    if not view_names:
        print("没有找到视图名称，退出程序")
        return
    
    # 2. 生成组合视图
    view_name, content = generate_combined_view(view_names)
    
    # 3. 保存到文件
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "ios_resource", "single_swifui_view")
    
    # 清空输出目录
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"已清空目录: {output_dir}")
    else:
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"{view_name}.swift")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n已生成组合视图文件: {output_file}")
        print(f"文件包含 {len(view_names)} 个视图组件")
        print("注意：文件已生成到临时目录，后续会通过move_view.py复制到项目中的正确位置")
    except Exception as e:
        print(f"错误：写入文件失败: {e}")

if __name__ == "__main__":
    single_swifui()
