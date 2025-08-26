import random
import sys
import os
import re
import string

sys.path.append("./ios")
from log.random_strs import *
from handle_oc_class import file_util as oc_file_util
from handle_swift_class import file_util
from ios.file_base import file_base
from ios.handle_oc_class import rubbish_code_template
from ios.config import config
from ios.log import log

oc_types = oc_file_util.oc_types

class PreviousMethod:
    method_name:str
    method_param_names:list
    method_param_types:list
    is_reset = True

    # def __init__(self, method_name, method_param_names, method_param_types):
    #     self.method_name = method_name
    #     self.method_param_names = method_param_names
    #     self.method_param_types = method_param_types

previous_method = PreviousMethod()
first_method = PreviousMethod()

left_space = "    "

#生成随机垃圾逻辑代码
def generate_logic_rubbish_code():
    type = random.choice(oc_types)
    text = ""
    if type == "int":
        text = '''%s R_LOCAL_IVAR_1 = %s;\nwhile (R_LOCAL_IVAR_1 >= %s) { break; }''' % (type,random.randint(1, 1000), random.randint(1, 1000))
        text = text.replace('R_LOCAL_IVAR_1',get_single_word())
    elif type == "float" or type == "double":
        text = '''%s R_LOCAL_IVAR_1 = %s;\nwhile (R_LOCAL_IVAR_1 >= %s) { break; }''' % (type,round(random.uniform(1, 1000),3), round(random.uniform(1, 1000),3))
        text = text.replace('R_LOCAL_IVAR_1',get_single_word())
    elif type == "BOOL":
        i = get_single_word()
        text = '''%s R_LOCAL_IVAR_1 = %s;
                    for (int %s = %s; %s < R_LOCAL_IVAR_1; %s++) { break; }
                ''' %('int',random.randint(0,100),i,random.randint(1, 1000),i,i)
        text = text.replace('R_LOCAL_IVAR_1',get_single_word())
    elif type == "NSString *":
        i = get_single_word()
        text = '''%s R_LOCAL_IVAR_1 = [NSString stringWithFormat:@"%s"];
                    for (int %s = 0; %s < R_LOCAL_IVAR_1.length; %s++) { break; }
                ''' %(type,get_single_word(),i,i,i)
        text = text.replace('R_LOCAL_IVAR_1',get_single_word())
    else:
        text = ""
    



    return text

    

#生成方法体
def generate_single_method(isLast:bool):
    #生成随机的参数个数
    num = random.randint(1, 5)
    #生成随机的参数名
    method_param_names = []
    param_names = []
    types = []
    method_name = f"{config.ADD_FILE_PREFIX.lower()}{camel_case_fun_name()}With"

    for i in range(num):
        method_param_names.append(config.ADD_FILE_PREFIX.lower() + lower_ivar_name())
        param_names.append(camel_case_fun_name())
        types.append(oc_types[random.randint(0,len(oc_types)-1)])

    method_content = f"- (void){method_name}"
    params_body = ""
    for i in range(num):
        params_body += f"{method_param_names[i]}:({types[i]}){param_names[i]} "

    #首字母大写
    params_body = params_body[0].upper() + params_body[1:]
    method_content += params_body + "{\n\n"

    #调用上一个方法
    call_previous_method_content = ""

    
    if previous_method.is_reset == False:
        call_previous_method_content = generate_call_method(
            previous_method.method_name,
            previous_method.method_param_types,
            previous_method.method_param_names)
    
    
    method_content += call_previous_method_content

    #方法体内容
    method_content += generate_single_body_content()

    #方法体最后
    method_content += "\n\n}"

    previous_method.method_name = method_name
    previous_method.method_param_names = method_param_names
    previous_method.method_param_types = types

    # if isLast is True:
    #     if previous_method.is_reset == True:
    previous_method.is_reset = False

    first_method.method_name = method_name
    first_method.method_param_names = method_param_names
    first_method.method_param_types = types


    return method_content

# 调用时随机生成的初始化参数
def generate_params_init(type):
    if type == "int":
        return f"{random.randint(0,10000)}"
    elif type == "double" or type == "float":
        return f"{random.uniform(0,10000)}"
    elif type == "BOOL":
        bool_list = ["YES","NO"]
        return f"{bool_list[random.randint(0,1)]}"
    elif type == "NSString *":
        return f"@\"{get_single_word()}\""
    elif type == "NSArray *" or type == "NSMutableArray *":
        content = ""
        index = 0
        count = random.randint(2, 5)
        for i in range(count):
            content += f"@\"{get_single_word()}\""
            if index != count - 1:
                content += ","
            index += 1
        return f"@[{content}]"
    elif type == "NSDictionary *" or type == "NSMutableDictionary *":
        content = ""
        index = 0
        count = random.randint(2, 5)
        for i in range(count):
            content += f"@\"{get_single_word()}\":@\"{get_single_word()}\""
            if index != count - 1:
                content += ","
            index += 1
        return f"@{{{content}}}"
    elif type == "NSNumber *":
        return f"@{random.randint(0,10000)}"
    else:
        return "nil"


#方法体内容(垃圾代码)
def generate_single_body_content():
    content = ""
    num = random.randint(3, 6)
    for i in range(num):
        type = oc_types[random.randint(0,len(oc_types)-1)]
        local_var_name = lower_ivar_name()

        
        if type == "int":
            content += f"{left_space}{type} {local_var_name} = {random.randint(0,10000)};\n"

            loop = f"{left_space}for (int i = 0; i < {random.randint(0,100)}; i++) " + "{\n"
            loop += f"{left_space}{left_space}{local_var_name} += {random.randint(1,100)};\n"
            loop += left_space + "}\n"
            
            content += loop

        elif type == "double" or type == "float":
            content += f"{left_space}{type} {local_var_name} = {random.uniform(0,10000)};\n"

            loop = f"{left_space}for (int i = 0; i < {random.randint(0,100)}; i++) " + "{\n"
            loop += f"{left_space}{left_space}{local_var_name} += {random.uniform(1,100)};\n"
            loop += left_space + "}\n"
            
            content += loop

        elif type == "bool":
            bool_list = ["YES","NO"]
            content += f"{left_space}{type} {local_var_name} = {bool_list[random.randint(0,1)]};\n"

        elif type == "NSString *":
            content += f"{left_space}{type}{local_var_name} = @\"{lower_ivar_name()}\";\n"

        elif type == "NSArray *":
            array_content = ""
            random_num = random.randint(2, 10)
            for i in range(random_num):
                array_content += "@" + f"\"{get_single_word()}\""
                if i != random_num-1:
                    array_content += ","
            content += f"{left_space}{type}{local_var_name} = @[{array_content}];\n"

            content += f"{left_space}NSUInteger {local_var_name}_count = {local_var_name}.count;\n"
            

        elif type == "NSDictionary *":
            
            dict_content = ""
            random_num = random.randint(2, 10)
            for i in range(random_num):
                dict_content += f"@\"{get_single_word()}\" : @\"{get_single_word()}\""
                if i != random_num-1:
                    dict_content += ","
            content += f"{left_space}{type}{local_var_name} = " + "@{" + dict_content + "}" + ";\n"

            content += f"{left_space}NSUInteger {local_var_name}_count = {local_var_name}.count;\n"
        
        elif type == "NSNumber *":
            content += f"{left_space}{type}{local_var_name} = @{random.randint(0,10000)};\n"

        elif type == "NSMutableArray *":
            content += f"{left_space}{type}{local_var_name} = [NSMutableArray array];\n"
            for i in range(random.randint(2, 10)):
                content += f"{left_space}[{local_var_name} addObject:@\"{get_single_word()}\"];\n"

            content += f"{left_space}NSUInteger {local_var_name}_count = {local_var_name}.count;\n"

        elif type == "NSMutableDictionary *":
            content += f"{left_space}{type}{local_var_name} = [NSMutableDictionary dictionary];\n"
            for i in range(random.randint(2, 10)):
                content += f"{left_space}[{local_var_name} setObject:@\"{get_single_word()}\" forKey:@\"{get_single_word()}\"];\n"                

            content += f"{left_space}NSUInteger {local_var_name}_count = {local_var_name}.count;\n"



    return content


#生成垃圾方法
def generate_method():
    
    num = random.randint(2, 5)
    total_method_content = ""
    for i in range(num):
        total_method_content += generate_single_method(isLast=(i==num-1)) + "\n"

    return total_method_content

def extract_objc_methods(inner_content):
    objc_methods = []
    
    # 正则表达式模式匹配Objective-C方法
    pattern = r'[-]\s*\([\w\s\*]+\)\s*([\w:]+)\s*'

    matches = re.findall(pattern, inner_content)
    for match in matches:
        # 去除方法中的空格和换行符
        method = match.replace(' ', '').replace('\n', '')
        objc_methods.append(method)

    return objc_methods

# 在第一个方法中插入调用《垃圾方法》
def insert_call_code_in_first_method(content, method_name, code):

    # # 在方法名后插入代码
    pattern = r'[-]\s*\([\w\s\*]+\)\s*' + re.escape(method_name) + r'(.*?)\s*\{'
    modified_content = re.sub(pattern, r'\g<0>\n' + code, content)
    return modified_content

  


#生成调用方法
def generate_call_method(method_name:str,method_param_types:list,method_param_names:list):
    call_previous_method_content = ""

    
    call_previous_method_content += f"{left_space}[self {method_name}"
    for i in range(len(method_param_types)):
        param_name = method_param_names[i]
        if i == 0:
            param_name = param_name[0].upper() + param_name[1:]
        
        type = method_param_types[i]
        last_space = "" if i == len(method_param_types)- 1 else " "
        if i == len(method_param_types)- 1:
            last_space = ""
        else:
            last_space = " "
        
        call_previous_method_content += f"{param_name}:{generate_params_init(type=type)}{last_space}"
    call_previous_method_content += "];\n"

    return call_previous_method_content



def generate_junk_code_by_level():
    
    junk_code = ""
    a = lower_ivar_name()
    b = lower_ivar_name()

    junk_code += f"{left_space}int {a} = {random.randint(0,10000)};\n\n"
    junk_code += f"{left_space}int {b} = {random.randint(0,10000)};\n\n"
    junk_code += f"{left_space}{a} = {a} + {b};\n"
    #OC 判断
    junk_code += f"{left_space}if ({a} > 10000) " + '{\n'
    junk_code += f"{left_space}{left_space}{b} = {random.randint(0,10000)};\n"
    junk_code += left_space + '}\n'

    return junk_code

# 生成随机的变量名
def generate_random_variable_name():
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(5))

# 生成随机的Objective-C类型
def generate_random_type():
    types = ['int', 'double']
    return random.choice(types)

# 生成随机的垃圾代码
def generate_garbage_code():
    code = ''

    # 生成随机的变量声明和赋值语句
    variable_name_list = []
    num_statements = random.randint(5, 10)
    for _ in range(num_statements):
        variable_name = generate_random_variable_name()
        variable_type = generate_random_type()
        code += f'{variable_type} {variable_name} = {random.randint(0, 100)};\n'
        variable_name_list.append(variable_name)

    # 生成随机的逻辑运算和条件语句
    num_operations = random.randint(1, 3)
    for _ in range(num_operations):
        operand1 = random.choice(variable_name_list)
        operand2 = random.choice(variable_name_list)
        operator = random.choice(['+', '-', '*',])
        result = generate_random_variable_name()
        code += f'{variable_type} {result} = {operand1} {operator} {operand2};\n'

        # 生成随机的条件语句（if）
        if_statement = f'if ({result} > 0) {{\n'
        if_statement += f'\t// 垃圾代码\n{operand1} = {random.randint(0, 100)};\n'
        if_statement += '} else {\n'
        if_statement += f'\t// 垃圾代码\n{operand2} = {random.randint(0, 100)};\n'
        if_statement += '}\n'
        code += if_statement

    # 生成随机的循环语句（while）
    num_loops = random.randint(1, 2)
    for _ in range(num_loops):
        loop_variable = random.choice(variable_name_list)
        loop_condition = random.choice(variable_name_list)
        loop_c_sign = random.choice(['<', '>'])
        code += f'while ({loop_variable} {loop_c_sign} {loop_condition}) {{\n'
        code += '\t// 垃圾代码\nbreak;\n'
        code += '}\n'

    return code


#开始执行
def start():
    log.logger.info("\n\nOC-开始插入垃圾代码")

    # file_result = file_util.get_all_files()
    file_result = file_base.get_all_files_suffix_with_swift_or_mh()

    result = oc_file_util.get_files_endswithhm(file_result)

    for file_path in result:

        #忽略文件
        if (oc_file_util.is_ignore_confuse_oc(file_path) == True):
            continue
        
        handle_file(file_path)
        
        

def handle_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    print(f"<OC-AddRubbishNativeCode> ==== 正在处理文件{file_path}\n")
    log.logger.info(f"<OC-AddRubbishNativeCode> ==== 正在处理文件{file_path}")

    # 在@interface和@end之间插入@property声明
    pattern = re.compile(r'@implementation.*?@end', re.DOTALL)
    x = pattern.findall(content)
    for s in x:

        previous_method.is_reset = True

        method_list_content = generate_method()
        new_content = s.replace('@end', f'\n{method_list_content}\n\n@end')

        ## 在第一个方法中插入并调用《垃圾方法》
        methods = extract_objc_methods(s)
        if len(methods) > 0:
            method_name = methods[0]

            global first_method
            call_code = generate_call_method(first_method.method_name, first_method.method_param_types, first_method.method_param_names)
            new_content = insert_call_code_in_first_method(new_content, method_name, call_code)

        ### 关闭方法（方法 开始插入代码）
        ### 在原方法体中插入生成的垃圾代码，进一步增强代码差异
            # for method in methods:
            #     # rubbish_code = f'/**\n你来写方法中的垃圾代码吧\n*/\n'
            #     rubbish_code = generate_garbage_code()
            #     new_content = insert_call_code_in_first_method(new_content, method, rubbish_code)
        ##

        content = content.replace(s, new_content)

    with open(file_path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    start()

    # file_path = "/Users/lindy/test_ios/TestPackage/OC/LZSCesuGongju.m"
    # handle_file(file_path=file_path)
    