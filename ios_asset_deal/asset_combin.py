import sys
import os
import random
import string
import re
import json
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asset_change_name import entry_change_name
from gener_imageset import entry_gener_imageset
from image_meta_weh import entry_iamge_meta_change


if __name__=='__main__':
    entry_iamge_meta_change()
    entry_change_name()
    entry_gener_imageset()



