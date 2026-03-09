import random
import os
import sys
import re

sys.path.append("./ios")
from log.random_strs import *
from handle_swift_class import file_util
from handle_oc_class import file_util as oc_file_util
from ios.log import random_strs
from ios.handle_oc_class import add_rubbish_native_code
from ios.log import log
from ios.handle_root  import parse_swift_file_2

new_add_ivar_map = {}

types = oc_file_util.oc_types

def generate_rubbish_ivar_reference_in_method(module_name):

    if module_name not in new_add_ivar_map.keys():
        return None

    content = ""
    
    ivar_list = new_add_ivar_map[module_name]
    for ivar_name in ivar_list:
        type,name = tuple(ivar_name.split(" "))
        print(type,name)
        if type == "int":
            content += "self.%s = %s;\n" % (name,random.randint(0,100))
        elif type == "NSString":
            content += "self.%s = @\"%s\";\n" % (name,get_single_word())
        elif type == "NSArray":
            string = f'@{random.randint(0,100)},@{random.randint(0,100)}'
            content += "self.%s = @[%s];\n" % (name,string)
        elif type == 'NSMutableArray':
            string = 'self.%s = [NSMutableArray array];\n' % name
            string += '[self.%s addObject:@(%s)];\n' % (name,random.randint(0,100))
            string += '[self.%s addObject:@(%s)];\n' % (name,random.randint(0,100))
            content += string
        elif type == "NSDictionary":
            string = f'@"{get_single_word()}":@"{random.randint(0,100)}"'
            content += "self.%s = @{%s};\n" % (name,string)
        elif type == "NSMutableDictionary":
            string = 'self.%s = [NSMutableDictionary dictionary];\n' % name
            string += 'self.%s[@"%s"] = @(%s);\n' % (name, get_single_word(), random.randint(0,100))
            content += string
        elif type == "BOOL":
            content += "self.%s = %s;\n" % (name,random.choice(["YES","NO"]))
        elif type == "float" or type == "double":
            content += "self.%s = %s;\n" % (name,random.random())
        elif type == "NSNumber":
            content += "self.%s = @(%s);\n" % (name,random.randint(0,100))
        else:
            content += "self.%s = %s;\n" % (name,"nil")
    

    return content

def record(content:str,new_ivar_content:str):
    pattern = re.compile(r"(?<=@interface)\s*(.*?)(?=\s*:\s*)")
    module_names = re.findall(pattern,content)
    if module_names is not None and len(module_names) > 0:

            # 定义匹配属性类型和名称的正则表达式
        pattern = re.compile(r"@property\s*\(\s*[^)]*\s*\)\s*([^;]+);\s*")

        # 使用正则表达式进行匹配
        matches = re.findall(pattern, new_ivar_content)

        # 提取属性类型和名称
        properties = []
        for match in matches:
            property_type, property_name = match.strip().split()
            properties.append((property_type, property_name.strip('*')))

        # 属性类型和名称
        ivars = []

        for property_type, property_name in properties:
            # print("Type:", property_type)
            # print("Name:", property_name)
            # print()
            ivars.append(f'{property_type} {property_name}')
            

        new_add_ivar_map[module_names[0]] = ivars
    

def insert_ivar_reference_code_in_method(content):

    objc_methods = []
    
    pattern = r'[-]\s?\(.*?\)\s?.*?{.*?}\s*(?=[-+]\s?\(.*?\)\s?|\s*@end)'

    module_name_pattern = re.compile(r"(?<=@implementation)\s*(.*?)(?=\s+)")
    module_name_re = re.compile(module_name_pattern)
    module_name = re.findall(module_name_re, content)
    if module_name is not None and len(module_name) > 0:
        module_name = module_name[0]
        
        # 使用正则表达式匹配方法块
        objc_methods = re.findall(pattern, content, re.DOTALL)

        for objc_method in objc_methods:

            #不处理switch case 代码段
            
            pattern = r"switch\s*\(.*\)\s*\{"
            match = re.search(pattern, objc_method)
            if match is not None:
                continue


            pattern = re.compile(r"\s*;\s*\n")

            # # 定义要插入的代码
            # # insert_code = " // Your code here\n"
            # insert_code = " %s\n" %(add_rubbish_native_code.generate_logic_rubbish_code())

            # # 使用正则表达式进行替换
            modified_content = re.sub(pattern, replace, objc_method)


            ivar_reference_code = generate_rubbish_ivar_reference_in_method(module_name)
            if ivar_reference_code is not None:
                pattern = r'[-]\s*\([\w\s\*]+\)\s*(.*?)\s*\{'
                modified_content = re.sub(pattern, r'\g<0>\n' + ivar_reference_code, modified_content)

                content = content.replace(objc_method, modified_content)

    return content
    



def insert_new_ivar_reference_per_method(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    
    pattern = re.compile(r'@implementation.*?@end', re.DOTALL)
    x = pattern.findall(content)
    for s in x:
        content = content.replace(s,insert_ivar_reference_code_in_method(s))
   
   

    with open(file_path, "w") as f:
        f.write(content)

# 属性类型
def ivar_type():
    inx = random.randint(0,len(types)-1)
    return types[inx]

# 生成属性（单行）
def generate_ivars():
    type = ivar_type()

    spacer = ""

    #修饰符    
    modifier = "assign"

    #判断前缀
    if "NS" in type:
        if type == "NSString *":
            modifier = "copy"
        else:
            modifier = "strong"
    else:
        modifier = "assign"
        spacer = " "

    #名称
    name = lower_ivar_name()

    text = f"@property(nonatomic,{modifier}){type}{spacer}{name};"
    return text

# 生成属性内容（多行）
def generate_rubbish_ivar():
    inx = random.randint(4,10)
    text = ""
    for i in range(inx):
        text = text + generate_ivars() + "\n"

    return text







def start():
    
    log.logger.info("\n\nOC--开始垃圾属性")

    file_result = file_util.get_all_files()

    result = oc_file_util.get_files_endswithhm(file_result)

    for file_path in result:

        #删除注释
        parse_swift_file_2.deleteCommentCode(file_path)


        #忽略文件
        if (oc_file_util.is_ignore_confuse_oc(file_path) == True):
            continue

        with open(file_path, "r") as f:
            content = f.read()
            
        # 在@interface和@end之间插入@property声明
        pattern = re.compile(r'@interface.*?@end', re.DOTALL)
        re.findall(pattern, content)
        match = re.search(pattern, content)
        x = pattern.findall(content)
        # match = pattern.search(content)
        if match:
            print(
                f"<OC-InsertRubbishIvar> ==== 正在处理文件{file_path}\n"
            )
            log.logger.info(f"<OC-InsertRubbishIvar> ==== 正在处理文件{file_path}\n")

            for s in x:
                new_propertys = generate_rubbish_ivar()
                new_content = s.replace('@end', f'\n{new_propertys}\n\n@end')
                content = content.replace(s, new_content)
                record(s,new_propertys)

            with open(file_path, "w") as f:
                f.write(content)

        else:
            print(f'warning: @interface and @end not found in the file.{file_path}')


    for file_path in result:
        insert_new_ivar_reference_per_method(file_path)


# 定义替换函数
def replace(match):
    index = match.start() // 2
    insert_code = " %s\n" %(add_rubbish_native_code.generate_logic_rubbish_code())
    return match.group() + insert_code

if __name__ == '__main__':
    start()

    # content = '''
    # self.libyanFightingGroup = @[@56,@47];
    # self.
    # plication = 96;
    # self.inaction = @(21);
    # [self bbbbbbb];
    # for (int i = 0; i < 100; i++) {
        
    # }
    # self.epipremnum = 24;
    # '''
    # # 定义正则表达式模式
    # # pattern = r"(?<!for\s*\(.*;.*;.*\));"
    # pattern = r";\s*\n"
    # # 定义正则表达式模式
    # pattern = r";\s*\n"

    # # 定义要插入的代码
    

    
    # # 使用正则表达式进行替换
    
    
    # # 使用正则表达式进行替换
    # result = re.sub(pattern, replace, content)

    # print(result)


