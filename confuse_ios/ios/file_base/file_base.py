import os
import glob
import sys
sys.path.append("./")
sys.path.append("./ios")
import config.config as config
from ios.modes.directory_model import DirectoryModel



#获取目录【工程下可能存在多个】
def get_all_folders():
    root_dir = config.ROOT_PROJECT_DIR

    # 获取iOS工程下面的文件夹列表
    subfolders = glob.glob(os.path.join(root_dir, "*"))

    # 过滤出文件夹
    subfolders = [folder for folder in subfolders if os.path.isdir(folder)]

    file_folders = []

    for subfolder in subfolders:
        subfolder_name = os.path.basename(subfolder).split('/')[-1]
        if subfolder_name == f"{config.PROJECT_SCHEME}.xcodeproj" or subfolder_name == f"{config.PROJECT_SCHEME}.xcworkspace":
            continue
        if subfolder_name in config.IGNORE_CODE_DIRECTORY:
            continue
        file_folders.append(subfolder)
    return file_folders


def get_files_in_directory(directory):
    files = []
    for file in glob.glob(os.path.join(directory, "**"), recursive=True):
        if os.path.isfile(file):
            files.append(file)
    return files


def get_all_files():
    file_folders = get_all_folders()
    files = []
    for folder in file_folders:
        files.extend(get_files_in_directory(folder))
    return files

#获取iOS 所有文件（.swift | .xib | .h | .m）
def get_all_files_suffix_with_swift_or_mh():
    files = get_all_files()
    file_paths = []
    for file in files:
        if file.endswith('.swift') or file.endswith('.xib') or file.endswith('.m') or file.endswith('.h') or file.endswith('.mm'):
            file_paths.append(file)
    return file_paths

#获取iOS 所有文件（.swift
def get_files_suffix_with_swift():
    files = get_all_files()
    file_paths = []
    for file in files:
        if file.endswith('.swift'):
            file_paths.append(file)
    return file_paths

## 获取oc文件
def get_files_suffix_withhm():
    files = get_all_files()
    #获取后缀为.h .m 的文件
    return [path for path in files if path.endswith(".h") or path.endswith(".m") or path.endswith(".mm")]

    ## 获取oc .m文件
def get_oc_files_suffix_withm():
    files = get_all_files()
    #获取后缀为.h .m 的文件
    return [path for path in files if path.endswith(".m") or path.endswith(".mm")]

#判断是否是oc桥接文件
def __is_oc_briding_file(file_path):
    return os.path.basename(file_path) == os.path.basename(DirectoryModel().bridge_header)
    
#混淆中忽略哪些文件
def is_ignore_confuse(file_path):
    #获取上一级目录名称
    file_path_list = file_path.split("/")
    file_path_list_len = len(file_path_list)
    if file_path_list_len < 2:
        return False
    # 1暂时忽略桥接文件
    # 2根据文件路径获取文件名称
    if __is_oc_briding_file(file_path):
        return True
    # 3忽略系统文件
    if file_path_list[file_path_list_len - 2] in config.IGNORE_CODE_DIRECTORY:
        return True
    return False

if __name__ == "__main__":
    flies = get_all_files_suffix_with_swift_or_mh()
    for file in flies:
        print(file + '\n')