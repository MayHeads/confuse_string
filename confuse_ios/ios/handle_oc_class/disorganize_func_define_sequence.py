


import random
import re
import sys
import os

sys.path.append("./ios")
from handle_oc_class import parse_and_assemble_re
from log.random_strs import *
from handle_swift_class import file_util
from handle_oc_class import file_util as oc_file_util
from ios.handle_oc_class import add_rubbish_native_code
from ios.log import log

#打乱函数定义顺序

def shuffle_methods_in_file(file_path,new_method_list):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = r''

# 打乱方法列表
def shuffle_method_body_list(method_blocks):
    random.shuffle(method_blocks)

# 获取方法块 方法名 + 参数名称 + {....code....}
def extract_method_blocks_from_oc_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = re.compile(r'@implementation.*?@end', re.DOTALL)
    x = pattern.findall(content)
    for child_content in x:

        new_content = child_content

        # 定义方法块的正则表达式模式
        # pattern = r'[-+]\s?\(.*?\)\s?.*?{.*?}\s*(?=[-+]\s?)'
        pattern = r'[-+]\s?\(.*?\)\s?.*?{.*?}\s*(?=[-+]\s?\(.*?\)\s?|\s*@end)'
        

        # # 使用正则表达式匹配方法块
        method_blocks = re.findall(pattern, child_content, re.DOTALL)
        origin_method_blocks = re.findall(pattern, child_content, re.DOTALL)

        random.shuffle(method_blocks)

        
        #抹掉方法块
        for method_block in origin_method_blocks:
            new_content = new_content.replace(method_block, "")

        #回写原来方法（顺序已打乱）
        
        for method_block in method_blocks:
            new_content = new_content.replace("\n@end", "\n" + method_block + "\n@end")
    
        content = content.replace(child_content, new_content)

    #将替换后的内容写入文件
    with open(file_path, 'w') as file:
        file.write(content)


    

# 获取方法名称
def get_all_fuction_name(path):
    with open(path, 'r') as file:
        content = file.read()

    pattern1 = re.compile(r'//.*') # 这个是为了查找到项目文件里面的注释代码，好比//abc 
    # .*? 尽可能少的匹配
    pattern2 = re.compile(r'/\**.*?\*/', re.S) # 这个是为了找到项目里面的注释代码：/* *ABC* */ 这里 .*? 是为了懒匹配
    if path.endswith(".h"):
        pattern3 = re.compile(r'(-|\+)\s*\(\w+\s*\**\)(.*?);', re.S) # 这是为了找到.h文件夹的方法名
    else:
        pattern3 = re.compile(r'(-|\+)\s*\(\w+\s*\**\)(.*?){', re.S)# 这是为了找到.m文件夹的方法名
    out = re.sub(pattern1, '', content)
    out = re.sub(pattern2, '', out)
    result2 = re.findall(pattern2, out)
    result = re.findall(pattern3, out)

    print(result)


#开始
def start():

    log.logger.info(f"\n\n开始打乱OC方法顺序")

    file_result = file_util.get_all_files()

    result = oc_file_util.get_files_endswithhm(file_result)

    for file_path in result:
        print(f"<OC-DisorganizeFunctionDefine> ==== 正在处理文件{file_path}\n")
        log.logger.info(f"<OC-DisorganizeFunctionDefine> ==== 正在处理文件{file_path}")
        extract_method_blocks_from_oc_file(file_path)



if __name__ == '__main__':
    # 示例：从Objective-C文件中提取方法定义并打乱顺序
    # file_path = "/Users/lindy/test_ios/TestPackage/OC_Ignore/FlutterCommonTool.m"
    file_path = "/Users/lindy/test_ios/TestPackage/OC/LZSCesuGongju.m"
    # # get_all_fuction_name(file_path)    

    # add_rubbish_native_code.handle_file(file_path)
    # methods = extract_method_blocks_from_oc_file(file_path)

    
    start()
    





 

