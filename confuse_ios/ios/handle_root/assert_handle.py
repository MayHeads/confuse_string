import fnmatch
import json
import os
import sys
import re

from pprint import pprint

sys.path.append("./")
from ios.modes.directory_model import DirectoryModel
from ios.utils.replace_util import *
from ios.utils.path_util import *
from ios.file_base import file_base
import config.config as config



replace_image_name = []

""" 修改assert下只有文件的名字
"""


def modify_assert_folder_only(directory):
    origins = []
    replaces = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)

        is_contian = False
        for item in config.IGNORE_ASSERT_DEFAULT_DIRECTORY:
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

            os.rename(path, new_path)
            print(f"Renamed Assert Folder: {path} -> {new_path}")

            # 递归处理子目录
            modify_assert_folder_only(new_path)


def modify_imagesert_foler_only(directory):
    for name in os.listdir(directory):
        path = os.path.join(directory, name)

        if os.path.isdir(path):
            if ".imageset" in path:
                new_name = config.ADD_DIRECTORY_PREFIX + name
                new_path = os.path.join(directory, new_name)

                os.rename(path, new_path)
                print(f"Renamed Assert Folder: {path} -> {new_path}")
                name1 = get_folder_name(path)
                name2 = get_folder_name(new_path)
                replace_image_name.append((name1, name2))
                print(f"oldname", name1, "newname", name2)
                _inner_pic_handle(new_path, name1, name2)
                ## 规则信息添加

                path = new_path
            # 递归处理子目录
            modify_imagesert_foler_only(path)


def _inner_pic_handle(path, old_name, new_name):
    # file_name = get_folder_name(path)
    # print(f"<file_name> {file_name} {path}")

    png = path + f"/{old_name}.png"
    two_png = path + f"/{old_name}@2x.png"
    three_png = path + f"/{old_name}@3x.png"

    is_contain_one_x_png = False
    is_contain_two_x_png = False
    is_contain_three_x_png = False

    if os.path.isfile(png) and os.path.exists(png):
        is_contain_one_x_png = True
        new_png = path + f"/{new_name}.png"
        os.rename(png, new_png)

    if os.path.isfile(two_png) and os.path.exists(two_png):
        is_contain_two_x_png = True
        new_two_png = path + f"/{new_name}@2x.png"
        os.rename(two_png, new_two_png)

    if os.path.isfile(three_png) and os.path.exists(three_png):
        is_contain_three_x_png = True
        new_three_png = path + f"/{new_name}@3x.png"
        os.rename(three_png, new_three_png)

    content_json = path + "/Contents.json"

    # 处理contejson
    if os.path.exists(content_json):
        with open(content_json, "r") as file:
            json_data = json.load(file)
            if is_contain_one_x_png:
                json_data["images"][0]["filename"] = f"{new_name}.png"
            if is_contain_two_x_png:
                json_data["images"][1]["filename"] = f"{new_name}@2x.png"
            if is_contain_three_x_png:
                json_data["images"][2]["filename"] = f"{new_name}@3x.png"
        with open(content_json, "w") as file:
            json.dump(json_data, file, indent=4)


def replace_main_project_image_name():
    # 存储匹配的文件路径
    matches = []
    # 遍历根目录及其子目录下的所有文件和文件夹
    for root_dir, dirnames, filenames in os.walk(DirectoryModel().code):
        for filename in filenames:
            if fnmatch.fnmatch(filename, "*.swift") or fnmatch.fnmatch(filename, "*.m"):
                file_path = os.path.join(root_dir, filename)
                matches.append(file_path)
                for item in replace_image_name:
                    old_name, new_name = item
                    r_new_name = new_name.lower()
                    print(
                        f"<changeName> old_name: {old_name} new_name: {new_name} file_path: {file_path} \n"
                    )
                    with open(file_path, "r") as file:
                        file_content = file.read()

                        # 匹配R.image
                        comment_pattern = r"R.image.({})\(\)".format(old_name)
                        file_content = re.sub(
                            comment_pattern,
                            r"R.image.{}()".format(r_new_name),
                            file_content,
                        )

                        # 匹配UIimage
                        # comment_pattern = r"UIImage(named: ({}))".format(f'"{"b_4_gray"}"')
                        # pattern = r'UIImage\(named:\s*"({})"\)'.format("b_4_gray")
                        # file_content = re.sub(
                        #     pattern, r'UIImage(named: "{}")'.format(replace_string), file_content
                        # )

                        # 精确匹配字符串
                        pattern = r'"({})"'.format(old_name)
                        file_content = re.sub(
                            pattern, r'"{}"'.format(new_name), file_content
                        )
                        # 将修改后的内容写回文件 （关闭一次）
                    with open(file_path, "w") as file:
                        file.write(file_content)

#工程全替换
def replace_main_project_image_name_all():
    # 存储匹配的文件路径
    matches = file_base.get_all_files_suffix_with_swift_or_mh()
    for file_path in matches:
        for item in replace_image_name:
            old_name, new_name = item
            r_new_name = new_name.lower()
            print(
                f"<changeName> old_name: {old_name} new_name: {new_name} file_path: {file_path} \n"
            )
            with open(file_path, "r") as file:
                file_content = file.read()

                # 匹配R.image
                comment_pattern = r"R.image.({})\(\)".format(old_name)
                file_content = re.sub(
                    comment_pattern,
                    r"R.image.{}()".format(r_new_name),
                    file_content,
                )

                # 匹配UIimage
                # comment_pattern = r"UIImage(named: ({}))".format(f'"{"b_4_gray"}"')
                # pattern = r'UIImage\(named:\s*"({})"\)'.format("b_4_gray")
                # file_content = re.sub(
                #     pattern, r'UIImage(named: "{}")'.format(replace_string), file_content
                # )

                # 精确匹配字符串
                pattern = r'"({})"'.format(old_name)
                file_content = re.sub(
                    pattern, r'"{}"'.format(new_name), file_content
                )
                # 将修改后的内容写回文件 （关闭一次）
            with open(file_path, "w") as file:
                file.write(file_content)


def c_modifier_assert_folder_and_filename():
    # 获取`Assets.xcassets`的路径
    x = DirectoryModel().xcassets

    # 修改资源新建的文件夹 
    modify_assert_folder_only(x)  

    # 修改通用资源后缀`imageset`的资源
    modify_imagesert_foler_only(x) 

    # 修改项目中的引用图片的位置
    # 1.0
    # replace_main_project_image_name()
    #2.0
    replace_main_project_image_name_all()


if __name__ == "__main__":

    # 获取`Assets.xcassets`的路径
    x = DirectoryModel().xcassets

    # 修改资源新建的文件夹 
    modify_assert_folder_only(x)  

    # 修改通用资源后缀`imageset`的资源
    modify_imagesert_foler_only(x) 

    # 修改项目中的引用图片的位置
    replace_main_project_image_name()

    #     file_path = "./ios/text/demo_text.txt"
    # replace_image_name = [("logoMain", "new_logoMain"), ("pan", "new_pan")]
    # for item in replace_image_name:
    #     old_name, new_name = item
    #     with open(file_path, "r") as file:
    #         file_content = file.read()

    #         # 匹配R.image
    #         comment_pattern = r"R.image.({})\(\)".format(old_name)
    #         file_content = re.sub(
    #             comment_pattern, f"R.image.{new_name}()", file_content
    #         )

    #         # 匹配UIimage
    #         # comment_pattern = r"UIImage(named: ({}))".format(f'"{"b_4_gray"}"')
    #         # pattern = r'UIImage\(named:\s*"({})"\)'.format("b_4_gray")
    #         # file_content = re.sub(
    #         #     pattern, r'UIImage(named: "{}")'.format(replace_string), file_content
    #         # )

    #         # 精确匹配字符串
    #         pattern = r'"({})"'.format(old_name)
    #         file_content = re.sub(pattern, r'"{}"'.format(new_name), file_content)
    #         # 将修改后的内容写回文件 （关闭一次）
    #     with open(file_path, "w") as file:
    #         file.write(file_content)
