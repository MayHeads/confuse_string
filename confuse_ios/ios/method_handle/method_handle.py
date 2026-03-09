import re
import sys
import os

sys.path.append("./")
from ios.file_base import file_base


def collect_method():
    oc_files = file_base.get_files_suffix_withhm()

    total_result = []
    for path in oc_files:

        with open(path, 'r') as file:
            content = file.read()

        pattern1 = re.compile(r'//.*') # 这个是为了查找到项目文件里面的注释代码，好比//abc 
        # .*? 尽可能少的匹配
        pattern2 = re.compile(r'/\**.*?\*/', re.S) # 这个是为了找到项目里面的注释代码：/* *ABC* */ 这里 .*? 是为了懒匹配
        if path.endswith(".h"):
            pattern3 = re.compile(r'(-|\+)\s*\(\w+\s*\**\)(.*?);', re.S) # 这是为了找到.h文件夹的方法名
        else:
            pattern3 = re.compile(r'(-|\+)\s*\(\w+\s*\**\)(.*?){', re.S)# 这是为了找到.m文件夹的方法名
        out = re.sub(pattern1, '', content)
        out = re.sub(pattern2, '', out)
        result2 = re.findall(pattern2, out)
        result = re.findall(pattern3, out)

        for s in result + result2:
            name = s[1]
            total_result.append(name)
            

    return total_result


def breakdown_method(method_name):
    pattern = r"\b\w+:\("

    matches = re.findall(pattern, method_name)

    method_names = [match.strip(":(") for match in matches]

    names = []
    for name in method_names:
        names.append(name)

    return names

if __name__=='__main__':
    result = collect_method()
    for i in result:
        print(i)
        breakdown_result = breakdown_method(i)
        # print(breakdown_result)