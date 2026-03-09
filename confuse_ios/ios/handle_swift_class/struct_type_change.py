import json
import re
import sys
import os
sys.path.append("./")
from ios.handle_swift_class.collect_all_module import CollectAllModule
from ios.log.random_strs import camel_case_class_name
from ios.log.random_strs import camel_case_fun_name
from ios.handle_swift_class import file_util
from ios.handle_root.parse_swift_file import BaseStructKind
from ios.config.config import *
from lxml import etree
from ios.handle_oc_class import file_util as oc_file_util
from ios.config import config
from ios.log import log
from ios.modes.directory_model import DirectoryModel


swift_struct_modules = CollectAllModule().struct_module

fileName = "confuse-reflection-data.json"

confused_map = {}

def get_all_modules():
    return swift_struct_modules


def write_to_file(jsonObject):
    file = open(fileName, "w")
    json.dump(jsonObject, file)
    file.close()

#修改文件内一级模块名称（class，protocal,enum...）
def change_struct_name():
    print("------")
    log.logger.info("类名映射=========================================\n\n")
    for model_obj in swift_struct_modules:
        
        name = model_obj.name

        ## 类型
        type = "class"
        if (model_obj.structType == BaseStructKind.CLASS):
            type = "class"
        elif (model_obj.structType == BaseStructKind.ENUM):
            type = "enum"
        elif (model_obj.structType == BaseStructKind.STUCT):
            type = "struct"
        elif (model_obj.structType == BaseStructKind.PROTOCOL):
            type = "protocol" 
        else:
            type = "extension"

        
        if (name in confused_map.keys()):
            item_map = confused_map[name]
            if type not in item_map["type"]:
                item_map["type"] = item_map["type"] + '/' + type

            confused_map[name] = item_map   
            
        else:
            if type == "extension":
                continue

            item_map = {}
            ## 混淆后的名称
            item_map["confuseName"] = config.ADD_FILE_PREFIX + camel_case_class_name()

            item_map["type"] = type

            confused_map[name] = item_map

            log.logger.info(f"\t{name} ====替换为 {item_map['confuseName']}")

        # print(confused_map)    
        write_to_file(confused_map)


def replace_struct_name_in_file_when_handle_oc_file(content,origin_name,replace_name):

    
    file_content = content
     # 替换类名的声明
    pattern_declaration = re.compile(r'\b' + re.escape(origin_name) + r'\b')
    modified_content_declaration = pattern_declaration.sub(replace_name, file_content)

    # 替换类名的引用
    pattern_reference = re.compile(r'\b' + re.escape(origin_name) + r'(?=[^A-Za-z0-9_])')
    modified_content_reference = pattern_reference.sub(replace_name, modified_content_declaration)

    return modified_content_reference

def replace_struct_name_in_file():
    ##swift 文件
    swift_flies = file_util.get_directly_files_endswithSwift()

    oc_files = oc_file_util.get_all_file_paths()

    pro_files = swift_flies + oc_files

    for file_path in pro_files:
        # 读取文件内容 (只打开一次)
        with open(file_path, "r") as file:
            file_content = file.read()

        for key, value in confused_map.items():
            origin_name = key
            inner_map = value
            replace_name = inner_map["confuseName"]

            # print(origin_name + "=====>" + replace_name)
            print(
                f"<changeSwiftFileChangeStructName> old_name: {origin_name} new_name: {replace_name } file_path: {file_path}\n"
            )

            if file_path.endswith(".h") or file_path.endswith(".m"):

                file_content =  replace_struct_name_in_file_when_handle_oc_file(content=file_content,origin_name=origin_name,replace_name=replace_name)

            else:

                # 使用正则表达式匹配类名
                pattern = r'\bclass\s+' + origin_name + r'\b'
                file_content = re.sub(pattern, 'class ' + replace_name, file_content)

                # 使用正则表达式匹配类名的引用位置
                pattern = r'\b' + origin_name + r'\b'
                file_content = re.sub(pattern, replace_name, file_content)
                
                # type_name = inner_map["type"]
                # ###如果存在‘/’ 可以优先考虑class（extension --> class）
                # if ("/" in type_name):
                #     type_name = "class"    


                # ###替换 class 、struct、enum、protocal 名称
                # comment_pattern = r"({})\s*({})\s*:".format(type_name,origin_name)
                # file_content = re.sub(comment_pattern, f"{type_name} {replace_name}:", file_content)

                
                # comment_pattern_1 = r"({})\s*({})\s*".format(type_name,origin_name)
                # file_content = re.sub(comment_pattern_1, f"{type_name} {replace_name} ", file_content)

                # comment_pattern_struct = r"({})\s*({})\s*".format("struct",origin_name)
                # file_content = re.sub(comment_pattern_struct, f"struct {replace_name} ", file_content)

                # ###替换extension 名称
                # if type_name == 'class':
                #     comment_pattern_extension = r"({})\s*({})\s*".format('extension',origin_name)
                #     file_content = re.sub(comment_pattern_extension, f"extension {replace_name} ", file_content)
                    
                # ###左括号
                # comment_pattern_left_parentheses = r"\s+({})\s*({})".format(origin_name,'\(')
                # file_content = re.sub(comment_pattern_left_parentheses, f" {replace_name}" + "(", file_content)

                # ###  <,CSubSubGroupDataSource>
                # comment_pattern_pro = r",\s*({})\s*".format(origin_name,)
                # file_content = re.sub(comment_pattern_pro, f",{replace_name}", file_content)    
    
                
                # # 替换 文件中引用的

                # comment_pattern_refence = r":\s*({})\s*".format(origin_name)
                # file_content = re.sub(comment_pattern_refence, f":{replace_name}", file_content)

                # comment_pattern_end = r":\s*({})\s*=".format(origin_name)
                # file_content = re.sub(comment_pattern_end, f":{replace_name} =", file_content)


        ##将修改后的内容写回文件 （关闭一次）
        with open(file_path, "w") as file:
            file.write(file_content)



def replace_struct_name_and_reference():
    
    confuse_json_file_path = 'confuse-reflection-data.json'
    # 以只读模式打开JSON文件
    with open(confuse_json_file_path, 'r') as file:
        # 使用json.load()加载JSON文件内容并保存到变量data中
        confuse_data_map = json.load(file)

    target_json_file_path = 'ivar_confuse-reflection-data.json'
    with open(target_json_file_path, 'r') as file:
        # 使用json.load()加载JSON文件内容并保存到变量data中
        target_data_map = json.load(file)

    
    for key, value in target_data_map.items():
        objs = value.get("objs")
        ##文件路径
        file_path = value.get("filePath")
        if objs is None:
            continue
         
        with open(file_path, "r") as file:
            file_content = file.read()

        for element in objs:
            name = element.get("name")
            nameoffset = element.get("nameoffset")
            offset = element.get("offset")
            typename = element.get("typename")

            if name:

                pass
            else:
                pass


# 修改main.Storyboard 文件
def _modifyAndUpdateMainStoryboard():

    # 指定Storyboard文件路径
    storyboard_file = DirectoryModel().main_storyboard

    #判断工程中是否存在该文件
    if not os.path.exists(storyboard_file):
        print("main.Storyboard 文件不存在")
        return

    tree = etree.parse(storyboard_file)
    root = tree.getroot()

    # 遍历Storyboard中的所有元素
    for element in root.iter():
        # 在这里进行你想要的操作
        # 例如，修改元素的属性
        if element.tag == "viewController":
            # 修改viewController元素的属性
            value = element.attrib["customClass"]

            confuse_data_map = {}
            with open(fileName, 'r') as file:
                # 使用json.load()加载JSON文件内容并保存到变量data中
                confuse_data_map = json.load(file)
                if value is not None:
                    if value in confuse_data_map:
                        element.attrib["customClass"] = confuse_data_map[value]["confuseName"]
    
    # 将修改后的内容写回到文件
    tree.write(storyboard_file)


 ### 修改模块名称 example:
 # class A {} ====> class B {}
def handle_change_module_name():
    log.logger.info("\n\n<SwiftModifyStructName>----开始修改类名")
    get_all_modules()
    change_struct_name()
    replace_struct_name_in_file()
    _modifyAndUpdateMainStoryboard()
    
 


if (__name__ == "__main__"):
    handle_change_module_name()
    _modifyAndUpdateMainStoryboard()
