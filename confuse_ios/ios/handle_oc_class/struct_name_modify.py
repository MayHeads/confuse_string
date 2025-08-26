
import os
import sys
import re

sys.path.append("./ios")
from handle_oc_class import parse_and_assemble_re
from log.random_strs import *
from handle_swift_class import file_util
from handle_oc_class import file_util as oc_file_util

from ios.handle_root  import parse_swift_file_2
from ios.file_base import file_base
from ios.config import config
from ios.log import log

modify_map = {}

modify_enums_map = {}

_project_enum_list = []

def __log():
    print("类名映射=========================================\n\n")
    log.logger.info("类名映射=========================================\n\n")
    for key in modify_map.keys():
        for obj in modify_map[key].keys():
            print(f"\t{obj} -> {modify_map[key][obj]}")
            log.logger.info(f"\t{obj} ====替换为 {modify_map[key][obj]}")

    print("枚举映射=========================================\n\n")
    log.logger.info("枚举映射=========================================\n\n")
    for key in modify_enums_map.keys():
            print(f"枚举名{key}")
            log.logger.info(f"枚举名{key}")
            map = modify_enums_map[key]
            for e in map.keys():
                print(f'{e} ====替换为 {map[e]}')
                log.logger.info(f'{e} ====替换为 {map[e]}')


def mirror_name():
    files_map = parse_and_assemble_re.get_file_object_map()
    _project_enum_list = parse_and_assemble_re.project_enum_list

    if files_map is None:
        return
    for key in files_map.keys():
        
        child_map = {}
        
        for obj in files_map[key]:
            child_map[obj] = config.ADD_FILE_PREFIX + camel_case_class_name()

        modify_map[key] = child_map


    #处理枚举
    if len(_project_enum_list) > 0:
        

        for ele in _project_enum_list:

            confuse_member_map = {}
            origin_name = ele.name

            for child_map in modify_map.values():
                for ori_key in child_map.keys():
                    if ori_key == ele.name:
                        confuse_name = child_map[ori_key]
                    
                        for member in ele.members:
                            
                            new_member = member
                            if "=" in member:
                                new_member = member.split("=")[0].replace(" ", "")
                            
                            # print(f'===={new_member}')
                            
                            if new_member.startswith(origin_name):
                                pattern = r"^" + re.escape(origin_name)
                                result = re.sub(pattern, "", new_member)

                                confuse_member = confuse_name + result
                                confuse_member_map[new_member] = confuse_member
                            else:
                                confuse_member = get_single_word().capitalize()
                                confuse_member_map[new_member] = confuse_member
                        
                        modify_enums_map[confuse_name] = confuse_member_map
        
        # for key in modify_enums_map.keys():
        #     print("======")
        #     print(key)
        #     map = modify_enums_map[key]
        #     for e in map.keys():
        #         print(e, map[e])


    __log()
    

def handle_modify():
    #1.0
    # file_result = file_util.get_all_files()
    # result = oc_file_util.get_files_endswithhm(file_result)
    # result_swift = file_util.get_directly_files_endswithSwift()
    # result = result + result_swift

    #2.0
    result = file_base.get_all_files_suffix_with_swift_or_mh()

    for file_path in result:
        log.logger.info(f"<OCModifyStructName>-处理文件: {file_path}")

        #忽略文件
        if (oc_file_util.is_ignore_confuse_oc(file_path) == True):
            continue
        #删除注释
        # parse_swift_file_2.deleteCommentCode(file_path)

        with open(file_path, "r") as f:
            content = f.read()
            for obj in modify_map.keys():
                child_map = modify_map[obj]

                for key in child_map.keys():
                    # print(f'{key}=======>{child_map[key]}')

                    #oc 文件
                    # pattern = r"(?<=[\s[(\s)])({})(?=[\s.:*;])".format(key)
                    # 枚举，结构体
                    pattern = r"(?<=[\s[(\s),])({})(?=[\s.:*;),{{])".format(key)
                    content = re.sub(pattern, f"{child_map[key]}", content) 

                    #swift 文件
                    pattern2 = r"(?<=[:\s=\s<\s])({})(?=[?\s=(.\s>])".format(key)
                    content = re.sub(pattern2, f"{child_map[key]}", content) 

                    

            #枚举成员     
            for key in modify_enums_map.keys():
                map = modify_enums_map[key]
                for e in map.keys():
                    
                    content = re.sub(e, f"{map[e]}", content)    

                
        with open(file_path, "w") as f:
            f.write(content)
            
            # print(f"{file_path} 类名修改完成=========================================")

#先删除注释吧，避免运行报错
def deleteCommentCode():
    result = file_base.get_all_files_suffix_with_swift_or_mh()

    for file_path in result:

        #忽略文件
        if (oc_file_util.is_ignore_confuse_oc(file_path) == True):
            continue
        #删除注释
        parse_swift_file_2.deleteCommentCode(file_path)

## 外部调用
def start():
    log.logger.info("\n\n<OCModifyStructName>----开始修改类名")
    deleteCommentCode()
    mirror_name()
    handle_modify()
    print(f"类名修改完成=========================================")



if __name__ == "__main__":
    start()