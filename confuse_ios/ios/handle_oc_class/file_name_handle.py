import os
import sys
import re

sys.path.append("./")

from ios.handle_oc_class  import file_util as oc_file_util
from ios.handle_swift_class import file_util as file_util
from ios.log.random_strs import camel_case_class_name
from ios.config import config
from ios.modes.directory_model import DirectoryModel
from ios.log import log
from ios.handle_root  import parse_swift_file_2

x = DirectoryModel()

file_name_map = {}

## 获取上一级目录
def __get_parent_dir(file_path):
    return os.path.dirname(file_path)
    

## 重命名
def __rename_oc_file(file_path):
    #上一级目录
    parent_dir = __get_parent_dir(file_path)
  
    if (oc_file_util.is_ignore_confuse_oc(file_path) == True):
        return


    file_name = file_util.get_file_name(file_path)

    #获取文件名称(没有.h 和.m 后缀)
    file_name_without_type = os.path.splitext(file_name)[0]

    print(file_name_without_type)

    #生成/获取新文件名
    new_file_name_without_type = ''
    if (file_name_map.get(file_name_without_type) != None):
        new_file_name_without_type = file_name_map.get(file_name_without_type)
    else:
        new_file_name_without_type =  config.ADD_FILE_PREFIX + camel_case_class_name()
        file_name_map[file_name_without_type] = new_file_name_without_type

    #当前旧文件名
    old_file_path = parent_dir + f'/{file_name}'

    #需要更换成的新的文件名    
    new_file_path = ''

    #判断文件是否.h 还是.m 文件
    if (file_name.endswith(".h")):
        new_file_path = parent_dir + f'/{new_file_name_without_type}.h'
    elif (file_name.endswith(".m") or file_name.endswith(".mm")):
        if file_name.endswith(".m"):
            new_file_path = parent_dir + f'/{new_file_name_without_type}.m'
        else:
            new_file_path = parent_dir + f'/{new_file_name_without_type}.mm'
    else:
        pass

    #开始更换

    print(
        f"<changeOCFileName> old_name: {file_name} new_name: {file_util.get_file_name(new_file_path)}\n"
    )
    log.logger.info(f"<changeOCFileName> old_name: {file_name} ====替换为 new_name: {file_util.get_file_name(new_file_path)}\n")

    os.rename(old_file_path,new_file_path)


## 更新 pbxproj 文件
def __update_pbxproj_file():
    pbxproj_path = x.pbxproject

    with open(pbxproj_path, "r") as file:
        content = file.read()

    for old_file_name, new_file_name in file_name_map.items():
        
        ##必须空格
        # content = content.replace(f' {old_file_name}',f' {new_file_name}')
        # pattern_declaration = re.compile(r'\b' + re.escape(old_file_name) + r'\b')
        # content = pattern_declaration.sub(new_file_name, content)

        # pattern_declaration = r'(?<=[\s"])({})(?=.+[hm])'.format(re.escape(old_file_name))
        # content = re.sub(pattern_declaration, new_file_name, content)

        old_file_name_pattern = re.escape(old_file_name)

        pattern_declaration = r'({}.h)'.format(old_file_name_pattern)
        content = re.sub(pattern_declaration, f'{new_file_name}.h' , content)

        pattern_declaration = r'({}.m)'.format(old_file_name_pattern)
        content = re.sub(pattern_declaration, f'{new_file_name}.m' , content)

        # pattern_declaration = r'"({}.h)'.format(old_file_name_pattern)
        # content = re.sub(pattern_declaration, f'"{new_file_name}.h', content)

        # pattern_declaration = r'"({}.m)'.format(old_file_name_pattern)
        # content = re.sub(pattern_declaration, f'"{new_file_name}.m', content)




        with open(pbxproj_path, "w") as file:
            file.write(content)

#更新头文件导入
def __update_m_file_header_import(file_path):
    log.logger.info(f"修改后更新头文件导入 {file_path}")
    with open(file_path, "r") as file:
        content = file.read()

    for old_file_name, new_file_name in file_name_map.items():
        # pattern = re.compile(r'\b' + re.escape(old_file_name) + r'\b')
        # content = re.sub(pattern, new_file_name, content)


        # pattern = r"#import\s+\"({}).h\"".format(old_file_name)
        # content = re.sub(pattern, f"#import \"{new_file_name}.h\"", content)

        
        part = r'#import "{}.h"'.format(old_file_name)
        part = re.escape(part)
        content = re.sub(part, r'#import "{}.h"'.format(new_file_name),content )

     ##将修改后的内容写回文件 （关闭一次）
    with open(file_path, "w") as file:
        file.write(content)

# 外部调用方法
def change_file_name():
    log.logger.info("\n\n<OCHandleFileName>--开始修改文件名称")

    file_result = file_util.get_all_files()
    result = oc_file_util.get_files_endswithhm(file_result)
    for file_path in result:
        __rename_oc_file(file_path)

    __update_pbxproj_file()

    new_oc_file_result = oc_file_util.get_files_endswithhm(file_util.get_all_files())
    for file_path in new_oc_file_result:
        #删除注释
        parse_swift_file_2.deleteCommentCode(file_path)
        __update_m_file_header_import(file_path)

if __name__ == "__main__":
    change_file_name()


    # string = "789353B829F4101C000EE56D /* ZFIJKPlayerManager+add.m */"
    # pattern = r"(?<=\s)({})(?=.+[hm]+)".format(re.escape("ZFIJKPlayerManager+add"))
    # # pattern = re.escape(pattern)
    # x = re.search(pattern, string)
    # pattern_declaration = re.compile(re.escape(pattern))

