import os
import sys
import re
import shutil
import importlib
import random
from pbxproj import XcodeProject
sys.path.append("./")

from ios.config import config
from ios.file_base import file_base
from ios.log import random_strs
from ios.config import config
from ios.modes.directory_model import DirectoryModel

ord_key = hex(random.randint(0, 255))


decryptConstString_method_code_oc = '''//字符串混淆解密函数
+ (NSString *)decryptConstString:(char *)string{
    char* origin_string = string;
    while(*string) {
        *string ^= 0xAA;
        string++;
    }
    
    return [NSString stringWithUTF8String:origin_string];
}
'''

decryptConstString_method_name = 'decryptConstString'
decryptConstString_method_code_swift = '''//字符串混淆解密函数
func %s(_ inputBytes: [UInt8]) -> String {
    
    let newByteArray = inputBytes.map { $0 ^ %s }
    
    let byteArray: [UInt8] = newByteArray
    let data = Data(byteArray)
    let str222 = String(data: data, encoding: .utf8)

    assert(str222 != nil,"解析失败☹️，请手动恢复字符串")
    if let convertedString = str222 {
        return convertedString
    } else {
        return ""
    }
}
''' % (decryptConstString_method_name,ord_key)

# OC 
# def replace(match):
#     string = match.group(2)
#     replaced_string = '((char []) {' + ', '.join(["%i" % ((ord(c) ^ 0xAA) if c != '\0' else 0) for c in list(string)]) + '})'
#     return ' ' + replaced_string + f'\n//{match.group(1)}"{match.group(2)}" \n'

# swift
def replace(match):
    string = match.group(2)
    if contains_chinese(string) == True:
        return " " + f'"{string}"'

    replaced_string = f'{decryptConstString_method_name}(' '[' + ', '.join(["%i" % ((ord(c) ^ int(ord_key,16)) if c != '\0' else 0) for c in list(string)]) + '])'
    return ' ' + replaced_string + f'\n//{match.group(1)}"{match.group(2)}" \n'

# def replace(match):
#     string = match.group(2)
#     byte_array = list(string.encode())
#     return ' ' + f'{byte_array}' + f'\n//{match.group(1)}"{match.group(2)}" \n'


# def new_create_file_to_decrypt():
#     # 创建并写入Objective-C头文件
#     header_file_content = '''
#     #import <Foundation/Foundation.h>

#     @interface MyClass : NSObject

#     - (void)myMethod;

#     @end
#     '''

#     header_file_path = f'{config.ROOT_PROJECT_DIR}/{config.PROJECT_SCHEME}/'+'MyClass.h'
#     with open(header_file_path, 'w') as header_file:
#         header_file.write(header_file_content)

#     print(f"Objective-C头文件已创建：{header_file_path}")

#     # 创建并写入Objective-C实现文件
#     implementation_file_content = '''
#     #import "MyClass.h"

#     @implementation MyClass

#     - (void)myMethod {
#         NSLog(@"Hello, World!");
#     }

#     @end
#     '''

#     implementation_file_path = f'{config.ROOT_PROJECT_DIR}/{config.PROJECT_SCHEME}/'+'MyClass.m'
#     with open(implementation_file_path, 'w') as implementation_file:
#         implementation_file.write(implementation_file_content)

#     print(f"Objective-C实现文件已创建：{implementation_file_path}")

#     model = DirectoryModel()
#     project = XcodeProject.load(model.pbxproject)

#     # file_options = FileOptions(create_build_files=True)

#     # project.add_file('MyClass.h',tree=TreeType.GROUP,force=True,)
#     # project.add_file('MyClass.m',tree=TreeType.GROUP,force=True,)
#     # project.save()

#     project_directory = config.ROOT_PROJECT_DIR

#     # 获取主工程组
#     main_group = project.get_or_create_group('Main Group')

#     # 添加文件到主工程组
#     file_reference = main_group.add_file(implementation_file_path, force=False, create_build_files=True)

#     # 获取文件的相对路径
#     file_relative_path = os.path.relpath(implementation_file_path, project_directory)

#     # 将文件引用添加到工程目录
#     project.add_file_reference(file_reference, file_relative_path)

#     project.save()



def collect_and_replace():
    # result = file_base.get_all_files_suffix_with_swift_or_mh()
    result = file_base.get_files_suffix_with_swift()
    for file_path in result:
        
        if len(config.CONFUSE_STR_FILES) == 0:
            #忽略文件
            if (file_base.is_ignore_confuse(file_path) == True):
                continue
        else:
            # 获取文件名
            file_name = os.path.basename(file_path).split('.')[0]
            if file_name not in config.CONFUSE_STR_FILES:
                continue
            
        print(file_path)
        with open(file_path, 'r+', encoding='utf-8') as f:
            content = f.read()
        pattern = re.compile(r'(?<==)\s*(@{0,1}\s*)"(.*?)"')
        content = re.sub(pattern, replace, content)
        with open(file_path, 'w+', encoding='utf-8') as f:
            f.write(content)


    if len(result) > 0:
        with open(result[0], 'a', encoding='utf-8') as f:
            f.write(f'\n\n{decryptConstString_method_code_swift}')
        

def contains_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fff]')  # 匹配中文字符的正则表达式
    return bool(pattern.search(text))


def start():
    collect_and_replace()
    pass


if __name__ == "__main__":
    

    collect_and_replace()
    # print(ord_key)

    