
import re
# 定义一个函数，输入一个swift文件的路径，输出这个文件的所有函数名
def get_function_name(file_path):
    # 读取文件内容
    with open(file_path, "r") as file:
        file_content = file.read()

    # 匹配函数名
    pattern = r"func\s*(\w+)\s*\("
    function_names = re.findall(pattern, file_content)

    return function_names

# 定义一个函数，输入一个swift文件的路径
# 1. 获取所有的函数名
# 2. 获取函数名对应的函数体作用域第一个大括号的开始的行号和位置
# 3. 并且获取这个函数体作用域最后一个大括号的结束的行号和位置
# 4. 返回一个字典，key是函数名，value是一个元组，元组的第一个元素是开始的行号，第二个元素是开始的位置，第三个元素是结束的行号，第四个元素是结束的位置
def get_function_range(file_path):
    # 读取文件内容
    with open(file_path, "r") as file:
        file_content = file.read()

    # 匹配函数名
    pattern = r"func\s*(\w+)\s*\("
    function_names = re.findall(pattern, file_content)

    # 匹配函数体作用域
    pattern = r"func\s*\w+\s*\([^)]*\)\s*\{([^}]*)\}"
    function_scopes = re.findall(pattern, file_content, re.DOTALL)

    # 匹配函数体作用域的开始的行号和位置
    pattern = r"func\s*\w+\s*\([^)]*\)\s*\{([^}]*)\}"
    function_scope_starts = re.finditer(pattern, file_content, re.DOTALL)

    # 匹配函数体作用域的结束的行号和位置
    pattern = r"\{([^}]*)\}"
    function_scope_ends = re.finditer(pattern, file_content, re.DOTALL)

    # 将匹配到的内容放到字典中
    function_ranges = {}
    for index, function_name in enumerate(function_names):
        function_scope_start = next(function_scope_starts)
        function_scope_end = next(function_scope_ends)

        function_ranges[function_name] = (
            function_scope_start.start(),
            function_scope_start.end(),
            function_scope_end.start(),
            function_scope_end.end(),
        )

    return function_ranges






if __name__=='__main__':
    path = '/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/ViewController.swift'
    # x = get_function_name(path)
    # print(x)

    y = get_function_range(path)
    print(y)