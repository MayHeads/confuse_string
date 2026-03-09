from enum import Enum


#类型
class ElementType(Enum):
    CLASS = 1
    ENUM = 2
    STRUCT = 3
    PROTOCOL = 4
    CATEGORY = 5

class FileObject:
    struct_list:list
    file_name:str

    def __init__(self, file_name):
        self.struct_list = []
        self.file_name = file_name
        

#代码块结构
class StructObject:
    type = ElementType.CLASS
    name:str
    file_belong:str
    method_list:list

    def __init__(self, type, name,file_belong):
        self.type = type
        self.name = name
        self.file_belong = file_belong
        self.method_list = []


#方法
class MethodElement:
    name:str
    start_offset:int
    end_offset:int

    def __init__(self, name, start_offset, end_offset):
        self.name = name
        self.start_offset = start_offset
        self.end_offset = end_offset
