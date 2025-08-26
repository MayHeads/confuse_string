import os
import sys
sys.path.append("./ios")
from handle_swift_class import file_util
from handle_oc_class import file_util as oc_file_util
import re
from ios.file_base import file_base

file_object_map = {}
file_object_list = []

project_enum_list = []

class OCFileClassObject:
    path:str
    class_list:list

    def __init__(self, path, class_list):
        self.class_list = class_list
        self.path = path


#枚举对象
class OCEnumObject:
    name:str
    members:list

    def __init__(self, name, members):
        self.members = members
        self.name = name


class OCStructObject:
    path:str
    struct_list:list

    def __init__(self, path, struct_list):
        self.struct_list = struct_list
        self.path = path


class OCFileObject:
    path:str
    class_object_list:list


def add_enum_list(enum_name,enum_members):
    enum_member_list = enum_members.split(',')
    enum_member_list = [member.strip() for member in enum_member_list]
    enum_member_list = [member for member in enum_member_list if member.strip() != '']

    obj = OCEnumObject(name=enum_name, members=enum_member_list)

    project_enum_list.append(obj)


# 获取所有类名(文件名称)
def get_class_in_file(file_path):
    # 读取文件内容 (只打开一次)
    with open(file_path, "r") as file:
        file_content = file.read()
        # 匹配所有类名
        class_name_list = re.findall(r'@interface\s+(.*?)\s*:', file_content)

        struct_or_enum_list = []
        # 枚举，结构体定义
        if 'struct' in file_content:
            pass
            #1
            # pattern = r'typedef\s+struct\s*\{[\s\S]*?\}\s*([\w\d_]+)\s*;'
            # result_0 = re.findall(pattern, file_content)

            # struct_or_enum_list += result_0
            
            # #2
            # pattern = r'^[\s\S]*?struct\s+([^=]*?)\s*{'
            # result_1 = re.findall(pattern, file_content)  
            # struct_or_enum_list += result_1

            
        if 'enum' in file_content:
            #1
            # pattern = r'typedef\s+enum\s*:\s*[\w\d_]+\s*\{[\s\S]*?\}\s*([\w\d_]+)\s*;'
            # result_0 = re.findall(pattern, file_content)
            # struct_or_enum_list += result_0

            #2
            # pattern = r'enum\s+([^:].*?)\s*\{'
            # result_1 = re.findall(pattern, file_content)
            # struct_or_enum_list += result_1

            #1
            pattern = r'typedef\s+enum\s*:\s*[\w\d_]+\s*\{([\s\S]*?)\}\s*([\w\d_]+)\s*;'
            
            match = re.search(pattern, file_content)

            if match:
                enum_members = match.group(1)
                enum_name = match.group(2)
                add_enum_list(enum_members=enum_members, enum_name=enum_name)
                # print(f'enum_name===={enum_name}')
                struct_or_enum_list.append(enum_name)
                

            #2
            pattern = r'enum\s+([^:].*?)\s*\{([\s\S]*?)\}\s*;'
            match2 = re.search(pattern, file_content)

            if match2:
                enum_members = match2.group(2)
                enum_name = match2.group(1)
              
                add_enum_list(enum_members=enum_members, enum_name=enum_name)
                # print(f'enum_name===={enum_name}')
                struct_or_enum_list.append(enum_name)

         
        if 'NS_ENUM' in file_content:
            #1
            # pattern = r'typedef\s*NS_ENUM\s*\(\s*\w*,\s*(.*?)\)\s*\{'
            # structs = re.findall(pattern, file_content)
            # struct_or_enum_list += structs

            pattern = r'typedef\s*NS_ENUM\s*\(\s*\w*,\s*(.*?)\)\s*\{([\s\S]*?)\}\s*;'
            match = re.search(pattern, file_content)

            if match:
                enum_members = match.group(2)
                enum_name = match.group(1)
              
                add_enum_list(enum_members=enum_members, enum_name=enum_name)
                # print(f'enum_name===={enum_name}')
                struct_or_enum_list.append(enum_name)

        struct_or_enum_list = [s for s in struct_or_enum_list if s != ""]
        class_name_list += struct_or_enum_list
           
    return class_name_list
    

def get_obj_classes_and_flie(file_path):
    class_list = get_class_in_file(file_path)
    if len(class_list) != 0:
        file_object = OCFileClassObject(file_path, class_list)
        return file_object

def obj_to_map(file_path):
    obj = get_obj_classes_and_flie(file_path)
    if obj is None:
        return
    #判断file_object_map 是否已经存在obj.path 
    if obj.path not in file_object_map:
        file_object_map[obj.path] = obj.class_list
    else:
        file_object_map[obj.path].extend(obj.class_list)
    
    file_object_list.append(obj)


def get_file_object_map():
    global project_enum_list

    # file_result = file_util.get_all_files()
    file_result = file_base.get_all_files_suffix_with_swift_or_mh()

    result = oc_file_util.get_files_endswithhm(file_result)

    for file_path in result:
        #忽略文件
        if (oc_file_util.is_ignore_confuse_oc(file_path) == True):
            continue
        obj_to_map(file_path)    

    return file_object_map


if __name__ == '__main__':
    get_file_object_map()  
    
    # for obj in project_enum_list:
    #     print(obj.name)
    #     for i in obj.members:
    #         print(i)