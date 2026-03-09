import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append("./")
from ios.modes.directory_model import DirectoryModel
from ios.utils.replace_util import *
import config.config as config
from ios.modes.directory_model import DirectoryModel
from ios.handle_swift_class import file_util

import handle_root.file_module_area as module_area

import add_rubbish_swift_code.rubbish_swift_code as rubbish_util


def should_ignore_file(file_path):
    """检查文件路径是否应该被忽略"""
    for ignore_dir in config.IGNORE_CODE_DIRECTORY:
        if ignore_dir in file_path:
            print(f"忽略文件（包含忽略目录 {ignore_dir}）: {file_path}")
            return True
    return False


def _insert_rubbish_ivar_for_file(file_path):
    module_names = module_area.get_class_or_struct_module_area_in_file(file_path)

    for name in module_names:
        result = module_area.get_module_area_info(file_path, name)
        if result is None:
            continue

        print(
            f"<InsertRubbishIvar> ==== 正在处理文件{file_path}\n"
        )

        bodyoffset = result["bodyoffset"]
        insert_offset = bodyoffset

        r_file = open(file_path, "r")
        file_content = r_file.read().encode("utf-8")

        rubbish_property = rubbish_util.generate_swift_property().encode("utf-8")

        new_file_content = (
            file_content[:insert_offset]
            + '\n'.encode('utf-8')
            + rubbish_property
            + '\n'.encode('utf-8')
            + file_content[insert_offset:]
        )
        new_file_content = new_file_content.decode("utf-8")

        w_file = open(file_path, "w")
        w_file.write(new_file_content)

        r_file.close()
        w_file.close()


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
    swift_result = [file_path for file_path in swift_result if not should_ignore_file(file_path)]
    if not swift_result:
        return

    max_workers = min(len(swift_result), max(1, min(8, os.cpu_count() or 4)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_insert_rubbish_ivar_for_file, file_path): file_path
            for file_path in swift_result
        }
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f"Swift 垃圾属性插入失败: {file_path}\n原因: {exc}")



if __name__ == "__main__":
    handle_insert_rubbish_ivar()
