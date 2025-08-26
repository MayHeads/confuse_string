from random import random
import subprocess
import os
from enum import Enum
import subprocess
import json
import nltk
import re
import sys
import time
sys.path.append("./")

from ios.handle_root import random_code_function

# ========================================== 配置 ==========================================
ignore_fun_key_words = [
    'init',
    'dealloc',
    'convenience',
    'description',
    'debugDescription',
    'encodeWithCoder',
    'initWithCoder',
    'class',
    'hash',
    'isEqual',
    'isEqualToString',
    'isEqualToString',
    'setup',
    'awakeFromNib',
    'case', 
    'guard',
    'if',

]



# file_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/SwiftParse/CapModel.swift"
# file_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/SwiftParse/CapModel.swift"
# file_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/SwiftParse/CapModel.swift"
# file_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/SwiftParse/CapModel.swift"
# file_path = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/SwiftParse/Note1.swift"

# file_path = "/Users/jiangshanchen/charge_ios/FrogPhoto/FrogPhoto/AppDelegate.swift"
file_path = "/Users/jiangshanchen/charge_ios/FrogPhoto/FrogPhoto/Inner/Camera/Debug/DemoVC.swift"

def is_ignore_fun_key_words(string):
    for item in ignore_fun_key_words:
        if string.find(item) != -1:
            return True
    return False

def deleteCommentCode(path):
    content = ''
    with open(path, 'r') as file:
        content = file.read()
    # print(content)
    # print('------------------')

    # 删除单行注释
    content = re.sub(r'\s+//.*', '', content)

    # 删除/// 注释
    content = re.sub(r'\s+///.*', '', content)

    # 删除 pragma mark - name
    content = re.sub(r'#\s*pragma .*', '', content)

    # 删除多行注释
    content = re.sub(r'/\*(.|\n)*?\*/', '', content)

    with open(path, 'w') as file:
        file.write(content)
# from ios.handle_root.custom_obj_in_file import *
# from custom_obj_in_file import *
# ========================================== 解析swift Model ==========================================
class KindType(Enum):
    CLASS = 1
    ENUM = 2
    STUCT = 3
    PROTOCOL = 4
    EXTENSION = 5


class ObjectStruct:
    """类, 枚举， 结构体， 扩展"""
    structType: KindType = KindType.CLASS
    name: str
    inheritedtypes: list
    methods: list
    instances: list
    staticinstances: list
    staticmethods: list

    def __init__(self, type, name):
        self.structType = type
        self.name = name
        self.inheritedtypes = []
        self.methods = []
        self.instances = []
        self.staticinstances = []
        self.staticmethods = []

class InstaceStruce:
    accessibility: str
    kind: str
    length: int
    name: str
    namelength: int
    nameofset: int
    offset: int
    typename: str

    def __init__(self,accessibility, kind, length, name, namelength, nameofset, offset, setter_accessibility, typename):
        self.accessibility = accessibility
        self.kind = kind
        self.length = length
        self.name = name
        self.namelength = namelength
        self.nameofset = nameofset
        self.offset = offset
        self.setter_accessibility = setter_accessibility
        self.typename = typename
    def __repr__(self):
        return f"""
----------------> instance:({self.name}) \n
    accessibility: {self.accessibility}\n
    kind: {self.kind}\n
    length: {self.length}\n
    name: {self.name}\n
    namelength: {self.namelength}\n
    nameofset: {self.nameofset}\n
    offset: {self.offset}\n
    typename: {self.typename}\n

"""

class MethodStruce:
    accessibility: str
    bodylength: str
    bodyoffset: str
    kind: str
    length: int
    name: str
    namelength: int
    nameofset: int
    offset: int
    arguments: list

    def __init__(self,accessibility, bodylength, bodyoffset, kind, length, name, namelength, nameofset, offset):
        self.accessibility = accessibility
        self.kind = kind
        self.length = length
        self.name = name
        self.namelength = namelength
        self.nameofset = nameofset
        self.offset = offset
        self.bodylength = bodylength
        self.bodyoffset = bodyoffset
        self.arguments = []

    def __repr__(self):
        return f"""
----------------> Method:({self.name}) \n
    accessibility: {self.accessibility}\n
    bodylength: {self.bodylength}\n
    bodyoffset: {self.bodyoffset}\n
    kind: {self.kind}\n
    length: {self.length}\n
    name: {self.name}\n
    namelength: {self.namelength}\n
    nameofset: {self.nameofset}\n
    offset: {self.offset}\n
"""
    
class ArgumentStruct:

    kind: str
    length: int
    name: str
    namelength: int
    nameofset: int
    offset: int
    typename: str

    def __init__(self, kind, length, name, namelength, nameofset, offset, typename):
        self.kind = kind
        self.length = length
        self.name = name
        self.namelength = namelength
        self.nameofset = nameofset
        self.offset = offset
        self.typename = typename

    def __repr__(self):
        return f"""
----------------> Argument:({self.name}) \n
    kind: {self.kind}\n
    length: {self.length}\n
    name: {self.name}\n
    namelength: {self.namelength}\n
    nameofset: {self.nameofset}\n
    offset: {self.offset}\n
    offset: {self.typename}\n
"""

# ========================================== 插入代码 model ==========================================

class OffsetType(Enum):
    INVOKE = 1
    INSERT = 2


class InsertOperation:
    name: str
    offset: int
    type: OffsetType
    invoke_code: str
    insert_code: str
    def __init__(self, name, offset, type, invoke_code, insert_code):
        self.name = name
        self.offset = offset
        self.type = type
        self.invoke_code = invoke_code
        self.insert_code = insert_code
    
    def insertBottomFunctionCode(self, index) -> (str, str):
        code = random_code_function.c_generate_code_random_method()
        # partern = re.compile(r"func\s+([a-zA-Z0-9_]+)\s*\(\s*\)\s*\{")
        partern = re.compile(r"func\s+([a-zA-Z0-9_]+)\s*\(\s*\)\s*\{")
        result = partern.search(code)
        invoke_name = '\n      ' + result.group(1) + '()'
        self.insert_code = code
        self.invoke_code = invoke_name
        if index % 2 == 0:
            self.invoke_code += InsertOperation.insertInnerFunctionCode()
        
        return (code, invoke_name)
    
    def insertInnerFunctionCode() -> str:
        code = random_code_function.c_generate_code_random_method()
        partern = re.compile(r"func\s+([a-zA-Z0-9_]+)\s*\(\s*\)\s*\{")
        result = partern.search(code)
        invoke_name = '\n       ' + result.group(1) + '()'
        all_insert = code + '\n' + invoke_name
        return (all_insert)
    
     


# ========================================== 转化 ==========================================

def as_list(obj):
    return obj if obj is not None else []

def as_method(obj) -> MethodStruce:
    return obj if obj is not None else MethodStruce()

def as_instance(obj) -> InstaceStruce:
    return obj if obj is not None else InstaceStruce()

def as_object_struct(obj) -> ObjectStruct:
    return obj if obj is not None else ObjectStruct()

def as_insert_operation(obj) -> InsertOperation:
    return obj if obj is not None else InsertOperation()

def get_instace_struct(k) -> InstaceStruce:
    accessibility = k.get("key.accessibility")
    kind = k.get("key.kind")
    length = k.get("key.length")
    name = k.get("key.name")
    namelength = k.get("key.namelength")
    nameoffset = k.get("key.nameoffset")
    offset = k.get("key.offset")
    setter_accessibility = k.get("key.setter_accessibility")
    typename = k.get("key.typename")
    instance = InstaceStruce(
        accessibility=accessibility,
        kind=kind,
        length=length,
        name=name,
        namelength=namelength,
        nameofset=nameoffset,
        offset=offset,
        setter_accessibility=setter_accessibility,
        typename=typename)
    return instance

def get_method_struct(k) -> MethodStruce:
    accessibility = k.get("key.accessibility")
    bodylength = k.get("key.bodylength")
    bodyoffset = k.get("key.bodyoffset")
    kind = k.get("key.kind")
    length = k.get("key.length")
    name = k.get("key.name")
    namelength = k.get("key.namelength")
    nameoffset = k.get("key.nameoffset")
    offset = k.get("key.offset")

    method = MethodStruce(
        accessibility=accessibility,
        bodylength=bodylength,
        bodyoffset=bodyoffset,
        kind=kind,
        length=length,
        name=name,
        namelength=namelength,
        nameofset=nameoffset,
        offset=offset
        )
    return method

def get_argument_struct(a) -> ArgumentStruct:
    kind = a.get("key.kind")
    if kind == "source.lang.swift.decl.var.parameter":
        length = a.get("key.length")
        name = a.get("key.name")
        namelength = a.get("key.namelength")
        nameoffset = a.get("key.nameoffset")
        offset = a.get("key.offset")
        typename = a.get("key.typename")
        argument = ArgumentStruct(
            kind=kind,
            length=length,
            name=name,
            namelength=namelength,
            nameofset=nameoffset,
            offset=offset,
            typename=typename
        )
    return argument

def get_insertaction(method: MethodStruce, type: OffsetType) -> InsertOperation:
    bodyoffset = method.bodyoffset
    endoffset = method.bodyoffset + method.bodylength
    offset = 0
    if type == OffsetType.INVOKE:
        offset = bodyoffset
    else:
        offset = endoffset

    z = InsertOperation(
        name=method.name,
        offset=offset,
        type=type,
        invoke_code="",
        insert_code=""
    )
    if type == OffsetType.INSERT:
        z.insertBottomFunctionCode(index=21)
    return z
        # z.insertBottomFunctionCode(index=random.randint(0, 10))

    

def split_string(string, splits):
    string = string.encode('utf-8')
    result = []
    start = 0
    for end in splits:
        result.append(string[start:end])
        start = end
    result.append(string[start:])
    return result

# ========================================== 解析代码 ==========================================
def parse_swift_file(file_path):
    # 调用 sourcekitten 命令并获取输出
    command = f"sourcekitten structure --file {file_path}"
    output = subprocess.check_output(command, shell=True)
    # 解析 JSON 输出
    # print(output)
    z = json.loads(output.decode())
    y = json.dumps(z, indent=2)
    print(f"<output>:------>\n {y}")

    all_length = z["key.length"]
    all_offset = z["key.offset"]
    number_objects = z ["key.substructure"]
    print(all_length,all_offset,number_objects)

    if len(number_objects) == 1:
        print("只有一个类，协议，或者，结构体")
    else:
        print("有多个类，协议，或者，结构体")

    objects = []
    for item in number_objects:
        # 解析对象类型
        kindtype = KindType.CLASS
        if item.get("key.kind") == "source.lang.swift.decl.class":
            kindtype = KindType.CLASS
        elif item.get("key.kind") == "source.lang.swift.decl.enum":
            kindtype = KindType.ENUM
        elif item.get("key.kind") == "source.lang.swift.decl.struct":
            kindtype = KindType.STUCT
        elif item.get("key.kind") == "source.lang.swift.decl.protocol":
            kindtype = KindType.PROTOCOL
        elif item.get("key.kind") == "source.lang.swift.decl.extension":
            kindtype = KindType.EXTENSION
        name = item.get("key.name")
        print(kindtype,name)
        data = ObjectStruct(type=kindtype,name=name)
        substructure = as_list(item.get("key.substructure"))
        for k in substructure:
            main_kind = k.get("key.kind")
            if main_kind == "source.lang.swift.decl.var.instance":
                instance = get_instace_struct(k)
                data.instances.append(instance)

            if main_kind == "source.lang.swift.decl.var.static":
                instance = get_instace_struct(k)
                data.staticinstances.append(instance)
            
            if main_kind == "source.lang.swift.decl.function.method.instance":
                method = get_method_struct(k)
                # for a in as_list(k.get("key.substructure")):
                #     argument = get_argument_struct(a)
                #     method.arguments.append(argument)
                data.methods.append(method)
            
            if main_kind == "source.lang.swift.decl.function.method.static":
                method = get_method_struct(k)
                # for a in as_list(k.get("key.substructure")):
                #     argument = get_argument_struct(a)
                #     method.arguments.append(argument)
                data.staticmethods.append(method)
            
        objects.append(data)

    print("----------------> 解析完成 <----------------")
    # x = as_object_struct(objects[2])
    # print(f"类名：----------{x.name}")
    # print(x.methods)
    # print(x.staticmethods)
    return objects

# ========================================== 修改方法插入 ==========================================
def modfife_method(path):
    # 删除注释

    # 注释这个修改删除
    # deleteCommentCode(path)

    file_path = path
    content = ''
    modi_conten = b""
    positions = []
    inserts = []
    invokes = []
    all_offsets = []
    x = parse_swift_file(file_path)

    with open(file_path, "r") as f:
        content = f.read()

    for k in x:
        item = as_object_struct(k)
        
        for M in as_list(item.methods):
            method = as_method(M)
            if method.bodylength is None:
                continue
            if method.bodyoffset is None:
                continue

            invoke = get_insertaction(method, OffsetType.INVOKE)
            insert = get_insertaction(method, OffsetType.INSERT)
            invokes.append(invoke)
            invokes.append(insert)
            all_offsets.append(method.bodyoffset)
            all_offsets.append(method.offset + method.length)

            # 代码结束位置
            # position = method.offset + method.length

            # 方法体开始位置
            position = method.bodyoffset
            print(f'offset: {position} name: {method.name}')
            positions.append(position)
    
    split_part = split_string(content, all_offsets)

    l = len(as_list(invokes))
    for index, item in enumerate(as_list(split_part)):
        modi_conten += item
        if index == len(split_part) - 1:
            break
        x =  as_insert_operation(invokes[index])
        if index % 2 == 0 and index < l - 1:
            print(f'======name: {x.name}')
            if is_ignore_fun_key_words(x.name) == False:
                next_item = as_insert_operation(invokes[index + 1])
                modi_conten += (next_item.invoke_code).encode('utf-8')
        if index % 2 == 1:
            modi_conten += (x.insert_code).encode('utf-8')
        modi_conten += b"\n"

    # print(modi_conten)
    decode_str = modi_conten.decode('utf-8')
    with open(file_path, "w") as f:
        f.write(decode_str)
    
    

# 测试效果
def parse(file_path):
    command = f'sourcekitten structure --file "{file_path}"'
    output = subprocess.check_output(command, shell=True)
    z = json.loads(output.decode())
    y = json.dumps(z, indent=2)
    print(f"<output>:------>\n {y}")




if __name__ == "__main__":
    modfife_method(path=file_path)






    # content = ''
    # with open(file_path, 'r') as file:
    #     content = file.read()
    # byte_length = len(content.encode('utf-8'))
    # # print(byte_length)
    # # parse(file_path=file_path)
    # byte_string = content.encode('utf-8')
    # offset = 583
    # offset_byte_string = byte_string[0:offset]
    # offset_string = offset_byte_string.decode('utf-8')
    # print(offset_string)


    # print(content[0:604])




    

    

