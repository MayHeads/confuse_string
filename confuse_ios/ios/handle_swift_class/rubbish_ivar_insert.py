import os
import sys

sys.path.append("./")
from ios.modes.directory_model import DirectoryModel
from ios.utils.replace_util import *
import config.config as config
from ios.modes.directory_model import DirectoryModel
from ios.handle_swift_class import file_util

import handle_root.file_module_area as module_area

import add_rubbish_swift_code.rubbish_swift_code as rubbish_util

###插入垃圾属性 example:
### class A {
###   var name: String = "hello" 
### }

### class A {
### var dadadad:bool = false
### var asa:String = "false"

###   var name: String = "hello"
### }

def handle_insert_rubbish_ivar():
     ## 1、获取所有文件
    result = file_util.get_all_files()
    ## 2、获取.swift 文件
    swift_result = file_util.get_files_endswithSwift(result)
    ## 3、插入垃圾属性
    for file_path in swift_result:
        
        ## 4 获取结构
        module_names = module_area.get_class_or_struct_module_area_in_file(file_path)

        for name in module_names:
            
            result = module_area.get_module_area_info(file_path,name)
            
            if result is None:
                continue

            print(
                f"<InsertRubbishIvar> ==== 正在处理文件{file_path}\n"
            )

            # print(result['kind'],result["bodyoffset"],name)            
            bodyoffset = result["bodyoffset"]
            insert_offset = bodyoffset
            

            r_file = open(file_path, "r")
            file_content = r_file.read().encode("utf-8")

            rubbish_property = rubbish_util.generate_swift_property().encode("utf-8")
        
            new_file_content = file_content[:insert_offset] + '\n'.encode('utf-8') + rubbish_property + '\n'.encode('utf-8') +file_content[insert_offset:]
            new_file_content = new_file_content.decode("utf-8")
        
            w_file = open(file_path, "w")
            w_file.write(new_file_content)

            r_file.close()
            w_file.close()



if __name__ == "__main__":
    handle_insert_rubbish_ivar()