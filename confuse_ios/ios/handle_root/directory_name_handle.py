import os
import sys
import pprint
import glob

sys.path.append("./")
from ios.modes.directory_model import DirectoryModel
from ios.utils.replace_util import *
import config.config as config


def add_prefix_to_files(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        new_filepath = os.path.join(directory, "AA_" + filename)

        # if os.path.isdir(filepath):
        #     # 递归处理子目录
        #     add_prefix_to_files(filepath)

        # # 给文件和文件夹添加前缀
        # os.rename(filepath, new_filepath)
        print(f"Renamed: {filepath} -> {new_filepath}")

def add_prefix_to_all_directories():
    origins = []
    replaces = []

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

    for file_folder in file_folders:
        add_prefix_to_directories(file_folder)


def add_prefix_to_directories(directory):
    origins = []
    replaces = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)

        # 忽略规则 Assets.xcassets 和 Base.lproj
        is_contian = False
        for item in config.IGNORE_CODE_DIRECTORY:
            if item in path:
                is_contian = True
                break
        if is_contian:
            continue

        if os.path.isdir(path):
            new_name = config.ADD_DIRECTORY_PREFIX + name
            new_path = os.path.join(directory, new_name)

            origins.append(name)
            replaces.append(new_name)
            replace_strings_in_pbxproj_upgrate_file(
                DirectoryModel().pbxproject, [name], [new_name]
            )

            os.rename(path, new_path)
            print(f"Renamed: {path} -> {new_path}")

            # 递归处理子目录
            add_prefix_to_directories(new_path)

    """路径下不包含某些字符串
    """


def is_name_not_in_path(path, name):
    path_str = str(path)
    return name not in path_str


"""
替换目录文件 pbxproj_file文件字符串<重点： 只针对更改目录修改>
"""


def replace_strings_in_pbxproj_upgrate_file(file_path, origin_strings, replace_strings):
    if len(origin_strings) != len(replace_strings):
        print("目录结构匹配数量有问题")
        raise ValueError

    # 读取文件内容 (只打开一次)
    with open(file_path, "r") as file:
        file_content = file.read()

    for index, element in enumerate(origin_strings):
        origin_string = element
        replace_string = replace_strings[index]

        # 替换 /* xxx */ 格式的字符串
        escaped_string = re.escape(origin_string)
        comment_pattern = r"/\*\s*({})\s*\*/".format(escaped_string)
        file_content = re.sub(comment_pattern, f"/* {replace_string} */", file_content)

        # 替换 path = xxx; 格式的字符串
        line_pattern = r"path\s*=\s*({});".format(escaped_string)
        file_content = re.sub(line_pattern, f"path = {replace_string};", file_content)

        # 替换 path = xxx; 格式的字符串
        line_pattern_deep = r"path\s*=\s*\"({})\";".format(escaped_string)
        file_content = re.sub(
            line_pattern_deep, f"path = \"{replace_string}\";", file_content
        )

    # 将修改后的内容写回文件 （关闭一次）
    with open(file_path, "w") as file:
        file.write(file_content)


## 但测试 没有实际意义
def replace_str(file_path, origin_strings, replace_strings):
    if len(origin_strings) != len(replace_strings):
        print("目录结构匹配数量有问题")
        raise ValueError

    # 读取文件内容 (只打开一次)
    with open(file_path, "r") as file:
        file_content = file.read()

        for index, element in enumerate(origin_strings):
            origin_string = element
            replace_string = replace_strings[index]

            # 替换 /* xxx */ 格式的字符串
            escaped_string = re.escape(origin_string)

            comment_pattern = r"/\*\s*({})\s*\*/".format(escaped_string)
            file_content = re.sub(
                comment_pattern, f"/* {replace_string} */", file_content
            )

            # 替换 path = xxx; 格式的字符串
            line_pattern = r"path\s*=\s*\"({})\";".format(escaped_string)

            file_content = re.sub(
                line_pattern, f"path = {replace_string};", file_content
            )

    # 将修改后的内容写回文件 （关闭一次）
    with open(file_path, "w") as file:
        file.write(file_content)


def c_add_prefix_to_directories():
    # x = DirectoryModel().code
    # add_prefix_to_directories(x)
    add_prefix_to_all_directories()


if __name__ == "__main__":
    # x = DirectoryModel().code
    # add_prefix_to_directories(x)

    add_prefix_to_all_directories()

    # path = "/Users/jiangshanchen/step_ios/PetTravel/PetTravel/AD_SECTION"
    # add_prefix_to_directories(path)

