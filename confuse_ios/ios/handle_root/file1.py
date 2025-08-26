import re

# 定义一个函数，输入一个swift文件的路径，输出这个文件的所有函数名
# 生成函数
def get_function_name(file_path):
    # 读取文件内容
    with open(file_path, "r") as file:
        file_content = file.read()

    # 匹配函数名
    pattern = r"func\s*(\w+)\s*\("
    function_names = re.findall(pattern, file_content)

    return function_names

# 定义一个函数，输入一个swift文件的路径，输入一个字符串，输出这个字符串在这个文件中的位置
# 生成函数
def get_string_range(file_path, string):
    # 读取文件内容
    with open(file_path, "r") as file:
        file_content = file.read()

    # 匹配字符串
    escaped_string = re.escape(string)
    pattern = r"{}".format(escaped_string)
    string_range = re.search(pattern, file_content)
    span = string_range.span()
    print(f'字符串{string}在文件{file_path}中的位置是{span}')
    x, y = span
    print(f'字符串{string}在文件{file_path}中的位置是{x}和{y}')


    return string_range

# 定义一个函数，输入一个swift文件的路径，和一个位置，替换这个位置的字符串为新一个新的字符串
# 生成函数
def replace_string(file_path, string, new_string):
    # 读取文件内容
    with open(file_path, "r") as file:
        file_content = file.read()

    # 匹配字符串
    escaped_string = re.escape(string)
    pattern = r"{}".format(escaped_string)
    file_content = re.sub(pattern, new_string, file_content)

    # 将修改后的内容写回文件 （关闭一次）
    with open(file_path, "w") as file:
        file.write(file_content)

    return file_content


if __name__=='__main__':
    path = '/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/ViewController.swift'
    x = get_function_name(path)
    print(x)

    y = get_string_range(path, 'b_4_gray')
    print(y)

