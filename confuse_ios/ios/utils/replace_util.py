import re

"""
替换目录文件 pbxproj_file文件字符串<重点： 只针对更改目录修改>
"""


def replace_strings_in_pbxproj_file(file_path, strings_to_replace, replacement):
    # 读取文件内容
    with open(file_path, "r") as file:
        file_content = file.read()

    # 替换 /* xxx */ 注释块中的字符串
    pattern = r"/\*([^*]|(\*[^/]))*\*/"
    matches = re.finditer(pattern, file_content)
    for match in matches:
        if any(string in match.group() for string in strings_to_replace):
            file_content = file_content.replace(match.group(), replacement)

    # 替换 path = xxx; 格式的字符串
    pattern = r"path\s*=\s*(.*?);"
    matches = re.finditer(pattern, file_content)
    for match in matches:
        if any(string in match.group(0) for string in strings_to_replace):
            file_content = file_content.replace(
                match.group(0), f"path = {replacement};"
            )

    # 将修改后的内容写回文件
    with open(file_path, "w") as file:
        file.write(file_content)


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
        comment_pattern = r"/\*\s*({})\s*\*/".format(origin_string)
        file_content = re.sub(comment_pattern, f"/* {replace_string} */", file_content)

        # 替换 path = xxx; 格式的字符串
        line_pattern = r"path\s*=\s*({});".format(origin_string)
        file_content = re.sub(line_pattern, f"path = {replace_string};", file_content)

    # 将修改后的内容写回文件 （关闭一次）
    with open(file_path, "w") as file:
        file.write(file_content)


if __name__ == "__main__":
    file_path = "./ios/check/demo_text.txt"
    origins = [
        "ViewController",
        "ViewController1",
    ]
    replaces = ["1", "2"]

    replace_strings_in_pbxproj_upgrate_file(file_path, origins, replaces)
