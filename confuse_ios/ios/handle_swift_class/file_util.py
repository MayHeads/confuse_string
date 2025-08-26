import os
import random
import string
import re
import sys

sys.path.append("./")
from ios.modes.directory_model import DirectoryModel
from ios.utils.replace_util import *
import config.config as config
from ios.modes.directory_model import DirectoryModel
from ios.file_base import file_base

x = DirectoryModel()

""" 获取文件util(仅.swift文件)
"""

## assetsXcassets
__assetsXcassets_dir_name = 'Assets.xcassets'


## 获取工程下的所有文件
def get_all_files():

    # root_dir = config.ROOT_PROJECT_DIR + '/' + config.PROJECT_SCHEME
    # for root,dirs,files in os.walk(root_dir):
    #     if __assetsXcassets_dir_name not in root:
    #         for file in files:
    #             result.append(os.path.join(root,file))
    #     else:
    #         # Assets
    #         # print(f"Assets={root}")
    #         pass

    # return result

    result = file_base.get_all_files_suffix_with_swift_or_mh()
    return result

## 获取swift文件
def get_files_endswithSwift(fileList = []):
    return [path for path in fileList if path.endswith(".swift") or path.endswith(".xib")]


## 直接获取swift文件
def get_directly_files_endswithSwift():
    result = get_all_files()
    return get_files_endswithSwift(result)


def ignore_swift_file(file_path):
    #文件名称
    file_name = os.path.basename(file_path).split('/')[-1]

    if 'AppDelegate.swift' in file_name:
        return True
    if 'SceneDelegate.swift' in file_name:
        return True
    return False
def get_file_name(file_path):
    #文件名称
    file_name = os.path.basename(file_path).split('/')[-1]
    return file_name


if __name__ == "__main__":
    result = get_all_files()
    print(get_files_endswithSwift(result))