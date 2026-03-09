from collect_all_module import CollectAllModule
from ios.log.random_strs import camel_case_class_name
from ios.log.random_strs import camel_case_fun_name
from ios.log.random_strs import lower_ivar_name
import json
import os


import file_util
from ios.handle_root.parse_swift_file import BaseStructKind


fileName = "ivar_confuse-reflection-data.json"

ivar_confused_map = {}

###常量、变量 混淆

def get_all_modules():
    return CollectAllModule().struct_module


def write_to_file(jsonObject):
    file = open(fileName, "w")
    json.dump(jsonObject, file)
    file.close()


### 修改属性名称
def change_ivar():
    swift_struct_modules = get_all_modules()

    for model_obj in swift_struct_modules:
        
        name = model_obj.name
        ##不能是class 或者 extension   
        if (model_obj.structType not in [BaseStructKind.CLASS, BaseStructKind.EXTENSION]):
            continue

        ## 类型
        # type = "class"
        # if (model_obj.structType == BaseStructKind.CLASS):
        #     type = "class"
        # else:
        #     type = "extension"

        if (name in ivar_confused_map.keys()):
            item_map = ivar_confused_map[name]

            for ivar_name in model_obj.vars:
                item_map[ivar_name] = lower_ivar_name()

            ivar_confused_map[name] = item_map   
            
        else:
            item_map = {}

            for ivar_name in model_obj.vars:
                item_map[ivar_name] = lower_ivar_name()

            ivar_confused_map[name] = item_map 

        # print(ivar_confused_map)    
        write_to_file(ivar_confused_map)

        

if __name__ == "__main__":
    change_ivar()