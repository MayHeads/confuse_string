import os
import sys
import importlib.util

# 处理相对导入和绝对导入
try:
    # 尝试相对导入（作为模块导入时）
    from .source_con_str_flutter import enc_string_process_flutter
except ImportError:
    # 如果相对导入失败，使用绝对导入（直接运行时）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_con_str_path = os.path.join(current_dir, 'source_con_str_flutter.py')
    spec = importlib.util.spec_from_file_location("source_con_str_flutter", source_con_str_path)
    source_con_str_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source_con_str_module)
    enc_string_process_flutter = source_con_str_module.enc_string_process_flutter


def z_enc_combin_flutter():
    enc_string_process_flutter()

if __name__ == '__main__':
    z_enc_combin_flutter()

