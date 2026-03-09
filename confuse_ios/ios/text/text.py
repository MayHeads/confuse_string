import os
import sys

sys.path.append("./")
from pbxproj import XcodeProject
from ios.modes.directory_model import DirectoryModel


# 加载项目文件

x = DirectoryModel()


# project_path = x.pbxproject
# project = XcodeProject.load(project_path)

# # 获取目标文件夹的引用 ID
# folder_name = "TestPackage"
# target_folder_id = None

# for obj in project.objects.get_objects_in_section("PBXGroup"):
#     if "TestPackage" in obj and obj["TestPackage"] == folder_name:
#         target_folder_id = obj["id"]
#         break

# # 如果找到目标文件夹，则更新其名称
# if target_folder_id:
#     new_folder_name = "AA_ViewController"
#     project.get_obj(target_folder_id)["name"] = new_folder_name

#     # 保存修改后的项目文件
#     project.save()

#     print(f"成功将文件夹 '{folder_name}' 重命名为 '{new_folder_name}'")
# else:
#     print(f"未找到文件夹 '{folder_name}'")


# project_path = x.pbxproject
# folder_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/ViewController"
# new_name = "AA_ViewController"


# def update_folder_name(project_file, folder_path, new_name):
#     # 加载项目文件
#     project = XcodeProject.load(project_file)

# 查找目标文件夹
# target_group = None

# root_group = project.get_or_create_group("")
# project.

# for group in root_group.groups:
#     if group.path == folder_path:
#         target_group = group
#         break
# for group_id in project.objects.get_keys_in_section("PBXGroup"):
#     group = project.objects[group_id]
#     if "path" in group and group["path"] == folder_path:
#         target_group = group
#         break
#     target_group = project.get_or_create_group(folder_path, make_relative=True)

#     # 更新目标文件夹的名称
#     if target_group:
#         target_group.name = new_name

#         # 保存修改
#         project.save()

#         print(f"成功将文件夹 '{folder_path}' 重命名为 '{new_name}'")
#     else:
#         print(f"未找到文件夹 '{folder_path}'")


# update_folder_name(project_path, folder_path, new_name)


import re


def replace_strings_in_file(file_path, strings_to_replaces, replacements):
    if len(strings_to_replaces) != len(replacements):
        print("要更改的目录不想等，请重新排查代码")
        raise ValueError

    strings_to_replaces_trans = []
    for item in strings_to_replaces:
        strings_to_replaces_trans.append([item])

        # 读取文件内容
    with open(file_path, "r") as file:
        file_content = file.read()

    # 替换 /* xxx */ 注释块中的字符串
    pattern = r"/\*([^*]|(\*[^/]))*\*/"
    # pattern = r"/\*\s*(.*?)\s*\*/"

    matches = re.finditer(pattern, file_content)

    for index, element in enumerate(replacements):
        strings_to_replace = strings_to_replaces_trans[index]
        replacement = element
        for match in matches:
            if any(string in match.group() for string in strings_to_replace):
                file_content = file_content.replace(match.group(), replacement)

        # 替换 path = xxx; 格式的字符串
        pattern = r"path\s*=\s*(.*?);"
        matches = re.finditer(pattern, file_content)
        for match in matches:
            if any(string in match.group(0) for string in strings_to_replace):
                file_content = file_content.replace(
                    match.group(1), f"path = {replacement};"
                )

        # 将修改后的内容写回文件
        with open(file_path, "w") as file:
            file.write(file_content)


# 示例用法
file_path = "./ios/check/demo_text.txt"
strings_to_replaces = [
    "ViewController",
    "ViewController1",
]
replacements = ["/* rx1 */", "/* rx3 */"]

replace_strings_in_file(file_path, strings_to_replaces, replacements)
