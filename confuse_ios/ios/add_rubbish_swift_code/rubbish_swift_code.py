
import sys
import os
import random

sys.path.append("./")
# import log.random_strs as random_util
from ios.log import random_strs

_typeList = ["Int", "String", "Bool", "Double","Int?", "String?", "Bool?", "Double?"]

def generate_swift_property():
    count = random.randint(1, 5)
    new_str = ""
    for i in range(0,count):
        
        type_name = random.choice(_typeList)
        if "int" in type_name:
            random_number = random.randint(1, 10000)
            new_str += '\n' + 'var' + ' ' + random_strs.lower_ivar_name() + ':' + type_name + ' = ' + f'{random_number}'
        elif 'String' in type_name:
            random_str = random_strs.lower_ivar_name()
            new_str += '\n' + 'var' + ' ' + random_strs.lower_ivar_name() + ':' + type_name + ' = ' + f'"{random_str}"'

        elif 'Bool' in type_name:
            random_bool = random.choice(['true', "false"])
            new_str += '\n' + 'var' + ' ' + random_strs.lower_ivar_name() + ':' + type_name + ' = ' + f'{random_bool}'

        elif 'Double' in type_name:
            random_number = random.uniform(1, 10000)
            new_str += '\n' + 'var' + ' ' + random_strs.lower_ivar_name() + ':' + type_name + ' = ' + f'{random_number}'
            

        

        if i == count - 1:
            new_str += '\n'

    return new_str


if __name__ == "__main__":
    print(generate_swift_property())