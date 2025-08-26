import ast
from pycparser import c_parser, c_ast




import clang.cindex
from clang.cindex import Config
import os


path2 = (
    "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/OC/OCMainViewController.m"
)
path = '/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/OC/Person.h'

def parse_objc_file(file_path):
    # "/Library/Developer/CommandLineTools/usr/lib/libclang.dylib"  # 或者是其它路径

    libclang_path = "/Library/Developer/CommandLineTools/usr/lib/libclang.dylib"
    # os.environ["DYLD_LIBRARY_PATH"] = libclang_path

    path = "/Library/Developer/CommandLineTools/usr/lib/"

    Config.set_library_path(path)
    index = clang.cindex.Index.create()
    translation_unit = index.parse(file_path)

    for cursor in translation_unit.cursor.walk_preorder():

        # print(cursor.kind)
        if cursor.kind == clang.cindex.CursorKind.OBJC_CLASS_REF:
            class_name = cursor.spelling
            print("Class:", class_name)


        if cursor.kind == clang.cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL:
            func_name = cursor.spelling
            offset = cursor.extent.start.offset
            bodyoffset = cursor.extent.end.offset
            
            print("Func:", func_name, offset, bodyoffset)




if __name__ == "__main__":
    parse_objc_file(file_path=path2)


