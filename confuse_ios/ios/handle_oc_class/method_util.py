import os
import sys
import re

sys.path.append("./ios")
from handle_oc_class import parse_and_assemble_re
from log.random_strs import *
from handle_swift_class import file_util
from handle_oc_class import file_util as oc_file_util


def get_method():
    file_result = file_util.get_all_files()

    result = oc_file_util.get_files_endswithhm(file_result)

    for file_path in result:
        
        with open(file_path, 'r', encoding='utf-8') as f:
            objc_code = f.read()

        method_blocks = re.findall(r"[-+]\s*\(.*?\)\s*\w+\s*{([^}]*)}", objc_code, re.DOTALL)

        index = 0
        for definition in method_blocks:
            print(index)
            print(definition.strip())
            index += 1



if __name__=='__main__':
    get_method()