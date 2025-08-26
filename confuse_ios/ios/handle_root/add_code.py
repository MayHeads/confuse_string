import subprocess
import os
import sys
import chardet
sys.path.append("./")
from enum import Enum
import subprocess
import json
import fnmatch
from ios.handle_root import random_code_function
from ios.handle_root import parse_swift_file_2
from ios.modes.directory_model import DirectoryModel
import config.config as config
from ios.file_base import file_base


def c_add_random_code():
    for i in range(config.CONFUSE_LEVEL):
        print(f"混淆次数---> {i}")
        #1.0
        # items = find_swift_files(DirectoryModel().code)
        #2.0
        items = find_swift_files_all()
        for item in items:
            parse_swift_file_2.modfife_method(item)
        # add_random_code(item)


def add_random_code(file_path):
    x1 = random_code_function.c_generate_code_random_method()
    x2 = random_code_function.c_generate_code_random_method()
    x3 = random_code_function.c_generate_code_random_method()
    # print(x1,x2,x3)
    append_str = "\n" + x1 + x2 + x3
    print(append_str)

    # content = ""
    # with open(file_path, "r") as file:
    #     content = file.read()
    with open(file_path, "a") as file:
        file.write(append_str)

def find_swift_files(directory):
    swift_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, '*.swift'):
                file_path = os.path.join(root, file)
                swift_files.append(file_path)

    return swift_files

#获取swift 后缀的文件
def find_swift_files_all():
    swift_files = file_base.get_files_suffix_with_swift()

    return swift_files



if __name__=='__main__':
    c_add_random_code()

 



# import sourcekit
# import subprocess
# import json
# import sys
# sys.path.append("./ios")


# diag_stage = 'key.diagnostic_stage'
# length = 'key.length'
# offset = 'key.offset'
# substructure = 'key.substructure'

# access = 'key.accessibility'
# body_length = 'key.bodylength'
# body_offset = 'key.bodyoffset'
# kind = 'key.kind'

# name = 'key.name'
# name_length = 'key.namelength'
# name_offset = 'key.nameoffset'



# file_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/Mode/MyClass.swift"


# # 调用 sourcekitten 命令并获取输出
# command = f"sourcekitten structure --file {file_path}"
# output = subprocess.check_output(command, shell=True)
# # 解析 JSON 输出
# data = json.loads(output.decode())
# print(json.dumps(data, indent=2))







# # 第一层整体的开始位置和结束位置，对于整个文件来说
# top_insert = data[length] + data[offset]

# # 读取文件中第一个类的明细
# firstGrade = data[substructure][0]
# class_offset = firstGrade[offset]
# class_length = firstGrade[length]

# current_insert = class_offset + class_length
# current_endinsert = class_offset + class_length  + 5 + 2


# # 获取方法声明的信息
# first_method = firstGrade[substructure][0]
# method_offset1 = first_method[offset]
# method_length1 = first_method[length]

# insertion_offset1 = class_offset + method_offset1 + method_length1 - 2  

# content = ""
# with open(file_path, "r") as file:
#     content = file.read()
# with open(file_path, "w") as file:
#     content = (
#         content[:current_insert] +  "\n//*****\n" + content[current_endinsert:]
#     )
#     file.write(content)

 


# # 在方法中插入代码
# code_to_insert = """
# var name = 10
# if name > 20 {
#     print("name > 20")
# }
# else {
#     print("name <= 20")
# }
# """
# content = ""
# with open(file_path, "r") as file:
#     content = file.read()


# with open(file_path, "w") as file:
#     content = (
#         content[:insertion_offset1] + code_to_insert + "\n" + content[insertion_offset1:]
        
#     )
#     content = (
#         content[:insertion_offset2] + code_to_insert + "\n" + content[insertion_offset2:]
        
#     )
#     content = (
#         content[:insertion_offset3] + code_to_insert + "\n" + content[insertion_offset3:]
        
#     )

#     file.write(content)

# if __name__=='__main__':
#     pass
    

# 在原始代码中插入新的代码
# modified_code = (
#     swift_code[:insertion_offset]
#     + code_to_insert
#     + "\n"
#     + swift_code[insertion_offset:]
# )

# print(modified_code)
