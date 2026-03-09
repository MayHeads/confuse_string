import re
import random
import os
import sys

sys.path.append("./")
from ios.file_base import file_base
from ios.config import config
from ios.log import random_strs
from ios.log import log
from ios.file_base import file_base

oc_ivar_list = []
oc_ivar_set = set()

oc_local_ivar_list = []
oc_local_ivar_set = set()

oc_method_list = []
oc_method_set = set()

swift_ivar_set = set()
swift_method_set = set()

total_code_name_set = set()

modify_map = {}

# 提取oc 属性
def extract_objc_ivar(file_content):
    content = file_content
    
    extract_objc_global_ivar(content)

    # pattern = r'@property\s*\(.*?\)\s*(.*?)\s*(\w+)\s*;'
    pattern = r'@property\s*\(.*?\)\s*(.*?)\s*(\w+)\s*;'
    x = re.findall(pattern, content)
    for item in x:
        # print(f'====={item}')
    
        oc_ivar_set.add(item[1])
        if item not in oc_ivar_list:
            oc_ivar_list.append(item)

# 提取@interface 中的成员变量  
# "@interface MyClass : NSObject { int myVariable; }"
def extract_objc_global_ivar(file_content):
    pattern = re.compile(r'@interface.*?@end', re.DOTALL)
    x = pattern.findall(file_content)
    for item in x:
        pattern = re.compile(r'{.*?}', re.DOTALL)
        fangluohao_x = pattern.findall(item)
        for fangluohao_item in fangluohao_x:
            # print(fangluohao_item)
            # 正则表达式模式
            block_pattern = r"\b(\w+)\b\s*;"

            # 使用正则表达式捕获成员变量
            matches = re.findall(block_pattern, fangluohao_item)

            # 打印捕获到的成员变量
            for match in matches:
                oc_local_ivar_list.append(match)
                oc_local_ivar_set.add(match)

            

# 提取oc 方法
def collect_method(file_path,file_content):
    
    content = file_content
    path = file_path

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

    total_result = []
    for s in result + result2:
        name = s[1]
        total_result.append(name)
        
    return total_result


def breakdown_method(method_name):
    if ':' in method_name:

        pattern = r"\b\w+:\("

        matches = re.findall(pattern, method_name)

        method_names = [match.strip(":(") for match in matches]

        names = []
        for name in method_names:
            names.append(name)

        return names
    else:
        return [method_name]

def extract_objc_method(file_path,file_content):
    result = collect_method(file_path=file_path,file_content=file_content)
    for i in result:
        # print(i)
        breakdown_result = breakdown_method(i)
        for j in breakdown_result:
            oc_method_list.append(j)
            oc_method_set.add(j)


#收集
def collect():
    files = file_base.get_all_files_suffix_with_swift_or_mh()
    for file in files:
        file_path_tmp = file
        with open(file, 'r',encoding='utf-8') as file:
            content = file.read()
        if file_path_tmp.endswith('.swift'):
            extract_swift_ivar(content)
            extract_swift_method(content)
        else:
            extract_objc_ivar(content)
            extract_objc_method(file_path=file_path_tmp,file_content=content)
    
    global total_code_name_set
    total_code_name_set = oc_ivar_set | oc_method_set | oc_local_ivar_set | swift_ivar_set | swift_method_set
            
#映射修改
def mapping():
    _set_tmp = total_code_name_set.copy()
    for i_str in _set_tmp:
        #判断前缀
        if i_str.startswith(config.ORIGIN_SYMBOL_PREFIX):
            if i_str not in modify_map.keys():
                new_name = config.ADD_FILE_PREFIX.lower() + random_strs.lower_ivar_name()
                modify_map[i_str] = new_name
                # print(f"{i_str} ====替换为 {new_name}")
                
                log.logger.info(f"{i_str} ====替换为 {new_name}")
        else:
            continue

# setter 方法修改
def setter_method_modity():
    file_reslut = file_base.get_all_files_suffix_with_swift_or_mh()
    for i in oc_ivar_set:
        setter_method = 'set%s'%(i.capitalize())
        new_setter_method = 'set%s'%(modify_map[i].capitalize())
        
        for file in file_reslut:
            with open(file, 'r',encoding='utf-8') as file:
                content = file.read()
            if setter_method in content:
                content = content.replace(setter_method,new_setter_method)
        
            with open(file, 'w',encoding='utf-8') as file:
                file.write(content)

#提取swift 属性
def extract_swift_ivar(file_content):
    
    #只提取带有类型声明的属性或变量
    # pattern = r"(?<=var|let)\s+(\w+)\s*:"

    #提取全部属性或变量
    pattern = r"(?<=var|let)\s+(\w+)\s*(?=:|=)"
    
    matches = re.findall(pattern, file_content)
    for i in matches:
        swift_ivar_set.add(i)

#提取swift 方法
def extract_swift_method(file_content):

    pattern = r"(?<=func)\s+(\w+)\s*(?=\()"

    matches = re.findall(pattern, file_content)
    for i in matches:
        swift_method_set.add(i)

def start():

    log.logger.info(f"\n\n开始混淆带前缀为{config.ORIGIN_SYMBOL_PREFIX}的属性或者方法")

    global oc_ivar_set
    global oc_ivar_list

    global oc_local_ivar_set
    global oc_local_ivar_list
    
    global oc_method_set
    global oc_method_list

    global swift_ivar_set
    global swift_method_set

    global modify_map

    collect()
    mapping()

    file_result = file_base.get_all_files_suffix_with_swift_or_mh()
    for file in file_result:
        file_path_tmp = file
        
        # print(f"正在修改 {file}")
        log.logger.info(f"正在处理{file}")
        with open(file, 'r',encoding='utf-8') as file:
            content = file.read()

        for i_str in modify_map.keys():
            content = content.replace(i_str,modify_map[i_str])

        for i in oc_ivar_set:
            iiiii:str = i
            if i in modify_map.keys():
                new_ooooo = modify_map[i]
                if new_ooooo is not None:
                    new_ooooo:str = new_ooooo
                    setter_method = 'set%s'%(iiiii.capitalize())
                    new_setter_method = 'set%s'%(new_ooooo.capitalize())
                    if setter_method in content:
                        content = content.replace(setter_method,new_setter_method)
        
        with open(file_path_tmp, 'w',encoding='utf-8') as file:
            file.write(content)




    


    

if __name__=='__main__':
    log.clear()
    log.logger.info(f"开始混淆带前缀为{config.ORIGIN_SYMBOL_PREFIX}的属性或者方法")
    start()


