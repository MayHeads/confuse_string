import sys
import os
import clang.cindex
from clang.cindex import Config

sys.path.append("./ios")
from parse_oc.element import *

proj_dir = '/Users/lindy/test_ios'

objc_methods = []
objc_class_names = []

def parse_objc_file_method(file_path):

    if not file_path.endswith('.m'):
        print('请传入.m文件的路径')
        return
    
    if Config.library_path is None:
        path = "/Library/Developer/CommandLineTools/usr/lib/"
        Config.set_library_path(path)
    

    index = clang.cindex.Index.create()
    tu = index.parse(file_path)
    # 定义系统类前缀
    system_class_prefixes = ['UI', 'NS']

    # 获取根节点
    root = tu.cursor

    method_list = []

    # 遍历子节点
    for child in root.get_children():
        # 判断子节点是否为类声明
        if child.kind == clang.cindex.CursorKind.OBJC_INTERFACE_DECL:
            # 获取类名
            class_name = child.displayname

            # 判断类名是否为系统类
            is_system_class = any(class_name.startswith(prefix) for prefix in system_class_prefixes)
            
            # 遍历类声明的子节点
            for method in child.get_children():
                if len(method.displayname) == 0:
                    continue
                # 判断子节点是否为实例方法声明
                if method.kind == clang.cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL or method.kind == clang.cindex.CursorKind.OBJC_CLASS_METHOD_DECL:
                    # 获取方法名
                    method_name = method.displayname
                    start_offset = method.extent.start.offset
                    end_offset = method.extent.end.offset

                    # 过滤系统方法和get/set方法
                    if not is_system_class and not method_name.startswith(('set', 'get', 'init')):
                        print("Instance or class method name:", method_name)
                        objc_methods.append(method_name)

                        method_element = MethodElement(method_name, start_offset, end_offset)
                        method_list.append(method_element)

    return method_list

 
def parse_objc_file(proj_dir = proj_dir):
    # 遍历目录下的所有文件和文件夹
    for root, dirs, files in os.walk(proj_dir):
        # 遍历文件
        for file in files:
            # 判断文件扩展名是否为.m
            if file.endswith('.m'):
                # 获取文件路径
                file_path = os.path.join(root, file)
                # 在这里执行你的操作，例如解析Objective-C代码、获取方法名等
                # 示例：打印文件路径
                print("🍺 ==> 开始解析 File path:", file_path)

                # file_object = FileObject()
                parse_objc_class(file_path=file_path)
                parse_objc_file_method(file_path=file_path)


def parse_objc_property(file_path):

    if not file_path.endswith('.m'):
        print('请传入.m文件的路径')
        return

    # 创建TranslationUnit
    index = clang.cindex.Index.create()
    tu = index.parse(file_path)

    # 获取根节点
    root = tu.cursor

    # 遍历子节点
    for child in root.get_children():
        # 判断子节点是否为类声明
        if child.kind == clang.cindex.CursorKind.OBJC_INTERFACE_DECL:
            # 遍历类声明的子节点
            for property in child.get_children():
                # 判断子节点是否为属性声明
                if property.kind == clang.cindex.CursorKind.OBJC_PROPERTY_DECL:
                    # 获取属性名
                    property_name = property.displayname
                    # 获取属性类型
                    property_type = property.type.spelling
                    # 打印属性名和类型
                    print("Property name:", property_name)
                    print("Property type:", property_type)


def parse_objc_class(file_path):
    if not file_path.endswith('.m'):
        print('请传入.m文件的路径')
        return
    
    if Config.library_path is None:
        path = "/Library/Developer/CommandLineTools/usr/lib/"
        Config.set_library_path(path)


    struct_list = []

    # 定义系统类的前缀
    system_class_prefixes = ['NS', 'UI', 'CG', 'OS', 'GDT', 'Turing']

    index = clang.cindex.Index.create()
    tu = index.parse(file_path)
    # 获取根节点
    root = tu.cursor
    # 遍历子节点
    for child in root.get_children():
        if len(child.displayname) == 0:
                    continue
        # 判断子节点是否为类声明
        if child.kind == clang.cindex.CursorKind.OBJC_INTERFACE_DECL:
            # 获取类名
            class_name = child.displayname
            offset = child.extent.start.offset
            bodyoffset = child.extent.end.offset
             # 判断类名是否为系统类
            is_system_class = any(class_name.startswith(prefix) for prefix in system_class_prefixes)
            if not is_system_class: 
                objc_class_names.append(class_name)
                print("Class name:", class_name, "offset:", offset, "bodyoffset", bodyoffset)

                struct_list.append(StructObject(class_name, offset, bodyoffset))



if __name__=='__main__':
    parse_objc_file()
