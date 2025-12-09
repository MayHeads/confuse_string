import sys
import os
import random
import string
import re
import json
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 添加当前目录到路径，以便导入同目录下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from asset_change_name import entry_change_name
from gener_imageset import entry_gener_imageset
from image_meta_weh import entry_iamge_meta_change
from json_deal import process_all_contents_json

def z_asset_combin():
    # entry_iamge_meta_change()

    entry_change_name()
    entry_gener_imageset()
    process_all_contents_json()
if __name__=='__main__':
    z_asset_combin()



