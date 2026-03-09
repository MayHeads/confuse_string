from ios.handle_swift_class import file_util
from ios.handle_root.parse_swift_file import parse_swift_file

#### 获取所有结构

class CollectAllModule:

    struct_module = []

    def __init__(self):
        ## 1、获取所有文件
        result = file_util.get_all_files()
        ## 2、获取.swift 文件
        swift_result = file_util.get_files_endswithSwift(result)

        for item_path in swift_result:

            if (file_util.ignore_swift_file(item_path) == True):
                continue

            item_result = parse_swift_file(item_path)
            for item in item_result:
                self.struct_module.append(item)
            


if __name__ == "__main__":
    module = CollectAllModule()
    print('=================================')
    print(module.struct_module)
    pass