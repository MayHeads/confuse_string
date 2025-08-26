
import os
import sys

sys.path.append("./")
from ios.handle_swift_class.file_util import get_all_files
from ios.config import config
from ios.modes.directory_model import DirectoryModel


oc_types = ["int","double","float","BOOL","NSNumber *","NSString *", "NSArray *", "NSDictionary *", "NSMutableArray *", "NSMutableDictionary *"]

#判断是否是oc桥接文件
def __is_oc_briding_file(file_path):
    return os.path.basename(file_path) == os.path.basename(DirectoryModel().bridge_header)

#混淆中忽略哪些文件
def is_ignore_confuse_oc(file_path):
    # #获取上一级目录名称
    # file_path_list = file_path.split("/")
    # file_path_list_len = len(file_path_list)
    # if file_path_list_len < 2:
    #     return False
    # # 1暂时忽略桥接文件
    # # 2根据文件路径获取文件名称
    # if __is_oc_briding_file(file_path):
    #     return True
    # # 3忽略系统文件
    # if file_path_list[file_path_list_len - 2] in config.IGNORE_CODE_DIRECTORY:
    #     return True
    # return False
    is_exit = False
    for ignore_directory in config.IGNORE_CODE_DIRECTORY:
        file_floder_list = file_path.split("/")
        if ignore_directory in file_floder_list:
            is_exit = True
            break
    return is_exit

## 获取oc文件
def get_files_endswithhm(fileList = []):
    #获取后缀为.h .m 的文件
    return [path for path in fileList if path.endswith(".h") or path.endswith(".m") or path.endswith(".mm")]

## 直接获取oc文件（不带路径）
def get_directly_files_endswithhm():
    result = get_all_files()
    # 1暂时忽略桥接文件
    # 2根据文件路径获取文件名称
    result = [os.path.basename(path) for path in result if not __is_oc_briding_file(path)]

    return get_files_endswithhm(result)

### 获取oc文件（带路径）
def get_all_file_paths():
    file_result = get_all_files()
    result = get_files_endswithhm(file_result)
    return result


if __name__ == "__main__":
    print(get_all_file_paths())