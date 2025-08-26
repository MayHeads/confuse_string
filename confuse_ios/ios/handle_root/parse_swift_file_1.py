import subprocess
import os
import sys
import chardet
sys.path.append("./")
from enum import Enum
import subprocess
import json
from ios.handle_root import random_code_function


file_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/VC/LoginController.swift"


def parse_swift_file(file_path):
    # 调用 sourcekitten 命令并获取输出
    command = f"sourcekitten structure --file {file_path}"
    output = subprocess.check_output(command, shell=True)
    # 解析 JSON 输出
    structure = json.loads(output.decode())
    print(json.dumps(structure, indent=2))

    # 获取顶级结构元素（类、结构体、协议等）
    top_level_structure = structure.get("key.substructure", [])
    print(json.dumps(top_level_structure, indent=2))
    offset = structure.get("key.offset", int)
    length = structure.get("key.length", int)
    print(f'lenght:{length},offset:{offset}')

if __name__=='__main__':
    # parse_swift_file(file_path)
    x1 = random_code_function.c_generate_code_random_method()
    x2 = random_code_function.c_generate_code_random_method()
    x3 = random_code_function.c_generate_code_random_method()
    # print(x1,x2,x3)
    append_str = "\n" + x1 + x2 + x3
    print(append_str)

    content = ""
    with open(file_path, "r") as file:
        content = file.read()
    with open(file_path, "a") as file:
        file.write(append_str)
    



