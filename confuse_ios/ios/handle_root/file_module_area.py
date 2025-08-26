import os
import subprocess
import json
import sys
import random

sys.path.append("./ios")
import log.random_strs as random_util
import add_rubbish_swift_code.rubbish_swift_code as rubbish_util

file_path = "/Users/lindy/Desktop/xmiles_project/python_ios_test/IOSConfuse/IOSConfuse/CGroup/CSubGroup/CSubSubGroup/CSubSubGroupModel.swift"

### 获取class 和 结构体
def get_class_or_struct_module_area_in_file(file_path):
    module_names = []
    result = get_all_module_area_in_file(file_path)
    for map in result:
        if map["type"] == "class" or map["type"] == "struct":
            module_names.append(map['name'])
    return module_names


### 获取一个文件中的所有module名称。
def get_all_module_area_in_file(file_path):
     # 调用 sourcekitten 命令并获取输出
    command = f"sourcekitten structure --file {file_path}"
    output = subprocess.check_output(command, shell=True)
    # 解析 JSON 输出
    structure = json.loads(output.decode())

    # 获取顶级结构元素（类、结构体、协议等）
    top_level_structure = structure.get("key.substructure", [])

    # print(json.dumps(top_level_structure, indent=2))


    module_names = []
    
    for element in top_level_structure:
        s_type = swift_type(element.get(key("kind")))
        s_name = element.get(key("name"))

        module_names.append({"type":s_type,"name":s_name})
    return module_names

### 根据解析的结构，获取一个swift类型
def swift_type(json_name):
    kind = ''

    if json_name == "source.lang.swift.decl.class":
        kind = "class"
    if json_name == "source.lang.swift.decl.extension":
        kind = "extension"
    if json_name == "source.lang.swift.decl.struct":
        kind = "struct"
    if json_name == "source.lang.swift.decl.protocol":
        kind = "protocol"
    if json_name == "source.lang.swift.decl.function.free":
        kind = "function"

    return kind

def get_module_area_info(file_path,module_name):
    # 调用 sourcekitten 命令并获取输出
    command = f"sourcekitten structure --file {file_path}"
    output = subprocess.check_output(command, shell=True)
    # 解析 JSON 输出
    structure = json.loads(output.decode())

    # 获取顶级结构元素（类、结构体、协议等）
    top_level_structure = structure.get("key.substructure", [])
    
    # print(json.dumps(top_level_structure, indent=2))


    top_map = {}
    for element in top_level_structure:
        name = element.get(key("name"))
        # bodylength = element.get(key("bodylength"))
        bodyoffset = element.get(key("bodyoffset"))
        nameoffset = element.get(key("nameoffset"))
        offset = element.get(key("offset"))
        typename = element.get(key("typename"))
        kind = element.get(key("kind"))

        if element.get(key("kind")) == "source.lang.swift.decl.class":
            kind = "class"
        if element.get(key("kind")) == "source.lang.swift.decl.extension":
            kind = "extension"
        if element.get(key("kind")) == "source.lang.swift.decl.struct":
            kind = "struct"
        if element.get(key("kind")) == "source.lang.swift.decl.protocol":
            kind = "protocol"
        if element.get(key("kind")) == "source.lang.swift.decl.function.free":
            kind = "function"

        if kind != "extension":
            item_map = {}
            item_map["name"] = name
            item_map["nameoffset"] = nameoffset
            item_map["typename"] = typename
            item_map["bodyoffset"] = bodyoffset


            item_map["kind"] = kind

            top_map[name] = item_map

        
    if module_name in top_map:
        return top_map[module_name]
    else:
        return None



def key(child_key):
    return f"key.{child_key}"


if __name__=="__main__":
    get_all_module_area_in_file(file_path)
    pass
        

    