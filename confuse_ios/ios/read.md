## env环境
1. 安装： brew install pyenv
2. 配置变量  1.  `echo 'eval "$(pyenv init --path)"' >> ~/.zshrc`  2. `source ~/.zshrc`
     
### 运行环境
cd 到当前bin目录下 
- 激活环境： source activate
- 取消环境： deactivate
- 安装插件库： `pip3 install -r requirements.txt`


## clang 解析oc
- 安装llvm： `brew install llvm`  同时就安装了clang
- 查看apple的libclang.dylib版本号：`otool -L /Library/Developer/CommandLineTools/usr/lib/libclang.dylib`   
- 查看clang的 version: `clang --version`
- 查看pip3插件的 version: `pip3 show clang`
- 安装兼容版本的clang: `pip3 install clang==14.0.0`  14.0.0 改成自己的版本号
- 查看 dylib的路径： `mdfind libclang.dylib`

导入
- import clang.cindex
- from clang.cindex import Config
- import os

### 
"""

def parse_objc_file(file_path):
    # "/Library/Developer/CommandLineTools/usr/lib/libclang.dylib"  # 或者是其它路径

    libclang_path = "/Library/Developer/CommandLineTools/usr/lib/libclang.dylib"
    # os.environ["DYLD_LIBRARY_PATH"] = libclang_path

    path = "/Library/Developer/CommandLineTools/usr/lib/"

    Config.set_library_path(path)
    index = clang.cindex.Index.create()
    translation_unit = index.parse(file_path)

    for cursor in translation_unit.cursor.walk_preorder():
        print(cursor.kind)
        if cursor.kind == clang.cindex.CursorKind.OBJC_CLASS_REF:
            class_name = cursor.spelling
            print("Class:", class_name)

        # if cursor.kind == clang.cindex.CursorKind.CLASS_DECL:
        #     class_name = cursor.spelling
        #     print("Class:", class_name)

        # if cursor.kind == clang.cindex.CursorKind.VAR_DECL:
        #     var_name = cursor.spelling
        #     print("Var:", var_name)

        # if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        #     func_name = cursor.spelling
        #     print("Func:", func_name)

        if cursor.kind == clang.cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL:
            func_name = cursor.spelling
            print("Func:", func_name)

        # if cursor.kind == clang.cindex.CursorKind.FIELD_DECL:
        #     var_name = cursor.spelling
        #     print("Var:", var_name)

        # if cursor.kind == clang.cindex.CursorKind.ENUM_DECL:
        #     enum_name = cursor.spelling
        #     print("Enum:", enum_name)
        # if cursor.kind == clang.cindex.CursorKind.OBJC_INTERFACE_DECL:
        #     class_name = cursor.spelling
        #     print("Class:", class_name)

        # if cursor.kind == clang.cindex.CursorKind.OBJC_METHOD_DECL:
        #     method_name = cursor.spelling
        #     print("Method:", method_name)




    if __name__ == "__main__":
        parse_objc_file(file_path=path2)
"""
