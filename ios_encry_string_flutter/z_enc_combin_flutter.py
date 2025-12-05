import os
import sys

# 添加当前目录到路径，以便导入同目录下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加项目根目录到路径
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 导入同目录下的模块
try:
    # 尝试相对导入（作为模块导入时）
    from .source_con_str_flutter import enc_string_process_flutter
    from .source_con_str_flutter_swift import enc_string_process_flutter_swift
except ImportError:
    # 如果相对导入失败，使用直接导入（直接运行时）
    from source_con_str_flutter import enc_string_process_flutter
    from source_con_str_flutter_swift import enc_string_process_flutter_swift

def z_enc_combin_flutter():
    enc_string_process_flutter()

def z_enc_combin_flutter_swift():
    enc_string_process_flutter_swift()

if __name__ == '__main__':
    z_enc_combin_flutter()
    z_enc_combin_flutter_swift()

