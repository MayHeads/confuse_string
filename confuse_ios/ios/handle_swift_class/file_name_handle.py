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
from ios.handle_swift_class import file_util
from ios.log.random_strs import camel_case_class_name
from ios.log.log import *

x = DirectoryModel()


""" 修改文件名称(仅.swift文件)
"""

## swift 文件转换map 
swift_file_convert_map = {}
swift_file_name_convert_map = {}

###
__swift_file_new_prefix = config.ADD_FILE_PREFIX


import os

## 获取后缀名 .xib .swift
def get_file_name_and_extension(filename):
    name, extension = os.path.splitext(filename)
    return (name, extension)


## 获取上一级目录
def __get_parent_dir(file_path):
    return os.path.dirname(file_path)
    

## 重命名
def __rename_swift_file(file_path):
    #上一级目录
    parent_dir = __get_parent_dir(file_path)
  
    if (file_util.ignore_swift_file(file_path) == True):
        return

    file_name = file_util.get_file_name(file_path)

    if file_name == 'main.swift' or file_name == 'AppDelegate.swift':
        return

    #当前旧文件名
    old_file_path = parent_dir + f'/{file_name}'
    #需要更换成的新的文件名  
      
    ## 获取名称，后缀名
    name,extension = get_file_name_and_extension(file_name)

    new_name = ""
    if name in swift_file_name_convert_map.keys():
        new_name = swift_file_name_convert_map[name]
    else: 
        new_name = camel_case_class_name()

    new_file_name_with_prefix = new_name + extension
    new_file_name= f'{__swift_file_new_prefix}{new_file_name_with_prefix}'
    new_file_path = parent_dir + '/' + new_file_name

    print(
        f"<changeSwiftFileName> old_name: {file_name} new_name: {new_file_name}\n"
    )
    logger.info(f"<changeSwiftFileName> old_name: {file_name} ====替换为 new_name: {new_file_name}\n")

    os.rename(old_file_path,new_file_path)

    swift_file_convert_map[file_name] = new_file_name
    swift_file_name_convert_map[name] = new_name

## 更新 pbxproj 文件
def __update_pbxproj_file():
    pbxproj_path = x.pbxproject

    with open(pbxproj_path, "r") as file:
        content = file.read()

    for old_file_name, new_file_name in swift_file_convert_map.items():

        # comment_pattern = r"\s+({}).".format(old_file_name)
        # content = re.sub(comment_pattern, f"{new_file_name}.", content)
        
        ##必须空格
        content = content.replace(f' {old_file_name}',f' {new_file_name}')
        content = content.replace(f'\"{old_file_name}\"',f' {new_file_name}')

        with open(pbxproj_path, "w") as file:
            file.write(content)

## 外部调用
def rename_files():
    logger.info("\n\n<SwiftHandleFileName>--开始修改文件名称")
    ## 1、获取所有文件
    result = file_util.get_all_files()
    ## 2、获取.swift 文件
    swift_result = file_util.get_files_endswithSwift(result)
    ## 3、修改.swift 文件名
    for path in swift_result:
        __rename_swift_file(path)
    ## 4、替换 pbxproj 文件
    __update_pbxproj_file()

    # print(swift_result)


if __name__ == "__main__":
    rename_files()