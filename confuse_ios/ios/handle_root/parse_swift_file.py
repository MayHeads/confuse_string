import subprocess
import os
from enum import Enum
import subprocess
import json
import nltk
import re
# from ios.handle_root.custom_obj_in_file import *
# from custom_obj_in_file import *


file_path = "/Users/lindy/python/python_test/IOSConfuse/IOSConfuse/AA_CGroup/AA_CSubGroup/CSubGroupModel.swift"

file_info_data_name = "swift_file_parse_data.json"

file_info_data_map = {}

def write_to_file(file_path,objs):
    map = {}

    # 使用正则表达式k获取文件名
    file_name = re.findall(r'/([^/]+)\.swift', file_path)[0]

    map["fileName"] = file_name
    map["filePath"] = file_path

    obj_list = []
    for obj in objs:
        obj_list.append(obj.to_map())

    map["objs"] = obj_list

    file_info_data_map[file_name] = map

    file = open(file_info_data_name, "w")
    json.dump(file_info_data_map, file)
    file.close()


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

    # e = CoustomObjInFile()
    # objs = e.get_custom_objs(top_level_structure)
    # write_to_file(file_path,objs)

    results = []
    # 提取类信息
    for element in top_level_structure:
        if element.get("key.kind") == "source.lang.swift.decl.class":
            data1 = collect_class(element=element)
            results.append(data1)

        if element.get("key.kind") == "source.lang.swift.decl.enum":
            data2 = collect_enum(element=element)
            results.append(data2)

        if element.get("key.kind") == "source.lang.swift.decl.struct":
            data3 = collect_struct(element=element)
            results.append(data3)

        if element.get("key.kind") == "source.lang.swift.decl.protocol":
            data4 = collect_protocol(element=element)
            results.append(data4)

        if element.get("key.kind") == "source.lang.swift.decl.extension":
            data5 = collect_extension(element=element)
            results.append(data5)
    return results
    print(results)

    # if element.get("key.kind") == "source.lang.swift.decl.enum":
    #     pass


"""  1.0收集类相关信息
"""


def collect_class(element):
    class_name = element.get("key.name")
    inheritedtypes = element.get("key.inheritedtypes")

    model = KeySubstucture(type=BaseStructKind.CLASS, name=class_name)
    model.inheritedtypes = inheritedtypes

    # 提取属性信息
    t_properties = []
    properties = element.get("key.substructure", [])
    for property in properties:
        if property.get("key.kind") == "source.lang.swift.decl.var.instance":
            property_name = property.get("key.name")
            print(f"Property Name: {property_name}")
            t_properties.append(property_name)
    model.vars = t_properties

    # 提取方法信息
    t_methods = []
    methods = element.get("key.substructure", [])
    for method in methods:
        if method.get("key.kind") == "source.lang.swift.decl.function.method.instance":
            method_name = method.get("key.name")
            t_methods.append(method_name)
    model.methods = t_methods
    return model


""" 2.0收集枚举相关信息
"""


def collect_enum(element):
    enum_name = element.get("key.name")
    inheritedtypes = element.get("key.inheritedtypes")

    model = KeySubstucture(type=BaseStructKind.ENUM, name=enum_name)
    model.inheritedtypes = inheritedtypes

    # 提取属性信息
    t_cases = []
    cases = element.get("key.substructure", [])
    for case in cases:
        if case.get("key.kind") == "source.lang.swift.decl.enumcase":
            for item in case.get("key.substructure"):
                case_name = item.get("key.name")
                print(f"Property Name: {case_name}")
                t_cases.append(case_name)
    model.vars = t_cases

    # 提取方法信息
    t_methods = []
    methods = element.get("key.substructure", [])
    for method in methods:
        if method.get("key.kind") == "source.lang.swift.decl.function.method.instance":
            method_name = method.get("key.name")
            t_methods.append(method_name)
    model.methods = t_methods
    return model


""" 3.0收集结构体
"""


def collect_struct(element):
    struct_name = element.get("key.name")
    inheritedtypes = element.get("key.inheritedtypes")

    model = KeySubstucture(type=BaseStructKind.STUCT, name=struct_name)
    model.inheritedtypes = inheritedtypes

    # 提取属性信息
    t_cases = []
    cases = element.get("key.substructure", [])
    for struct in cases:
        if struct.get("key.kind") == "source.lang.swift.decl.var.instance":
            struct_name = struct.get("key.name")
            print(f"Property Name: {struct_name}")
            t_cases.append(struct_name)
    model.vars = t_cases

    # 提取方法信息
    t_methods = []
    methods = element.get("key.substructure", [])
    for method in methods:
        if method.get("key.kind") == "source.lang.swift.decl.function.method.instance":
            method_name = method.get("key.name")
            t_methods.append(method_name)
    model.methods = t_methods
    return model


""" 4.0收集Protocol
"""


def collect_protocol(element):
    pro_name = element.get("key.name")
    inheritedtypes = element.get("key.inheritedtypes")

    model = KeySubstucture(type=BaseStructKind.PROTOCOL, name=pro_name)
    model.inheritedtypes = inheritedtypes

    # 提取属性信息
    t_cases = []
    cases = element.get("key.substructure", [])
    for struct in cases:
        if struct.get("key.kind") == "source.lang.swift.decl.var.instance":
            struct_name = struct.get("key.name")
            print(f"Property Name: {struct_name}")
            t_cases.append(struct_name)
    model.vars = t_cases

    # 提取方法信息
    t_methods = []
    methods = element.get("key.substructure", [])
    for method in methods:
        if method.get("key.kind") == "source.lang.swift.decl.function.method.instance":
            method_name = method.get("key.name")
            t_methods.append(method_name)
    model.methods = t_methods
    return model


""" 5.0收集Extension
"""


def collect_extension(element):
    ex_name = element.get("key.name")
    inheritedtypes = element.get("key.inheritedtypes")

    model = KeySubstucture(type=BaseStructKind.EXTENSION, name=ex_name)
    model.inheritedtypes = inheritedtypes

    # 提取属性信息
    t_cases = []
    cases = element.get("key.substructure", [])
    for struct in cases:
        if struct.get("key.kind") == "source.lang.swift.decl.var.instance":
            struct_name = struct.get("key.name")
            print(f"Property Name: {struct_name}")
            t_cases.append(struct_name)
    model.vars = t_cases

    # 提取方法信息
    t_methods = []
    methods = element.get("key.substructure", [])
    for method in methods:
        if method.get("key.kind") == "source.lang.swift.decl.function.method.instance":
            method_name = method.get("key.name")
            t_methods.append(method_name)
    model.methods = t_methods
    return model


class BaseStructKind(Enum):
    CLASS = 1
    ENUM = 2
    STUCT = 3
    PROTOCOL = 4
    EXTENSION = 5


class KeySubstucture:
    """类, 枚举， 结构体， 扩展"""

    structType: BaseStructKind = BaseStructKind.CLASS
    name: str
    inheritedtypes: list = []
    methods: list = []
    vars: list = []

    def __init__(self, type, name):
        self.structType = type
        self.name = name


if __name__ == "__main__":
    x = parse_swift_file(file_path)
    # print(x)
