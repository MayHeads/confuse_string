import sys
import re
import random
import string
import time

sys.path.append("./")

from ios.config import config
from ios.modes.directory_model import DirectoryModel


#翻新文件uuid 
def renovate_uuids():

    def randString():
        x = 24
        random.seed(time.time())
        string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        letterRunes = [char for char in string]
        b = [random.choice(letterRunes) for _ in range(x)]
        return ''.join(b).upper()

    def scan():
        with open(DirectoryModel().pbxproject, 'r') as f:
            content = f.read()
            pattern = re.compile(r'[0-9A-Z]{24}')
            matches = pattern.findall(content)
            #matches 转set
            total = set(matches)
            
            return total
            
    
        
    replace = {}
    uuids = scan()

    with open(DirectoryModel().pbxproject, 'r') as f:
        content = f.read()

    for uuid in uuids:
        new_uuid:str
        if uuid in replace.keys():
            new_uuid = replace[uuid]
        else:
            new_uuid = randString()
            replace[uuid] = new_uuid
        
        content = content.replace(uuid, new_uuid)
    
    with open(DirectoryModel().pbxproject, 'w') as f:
        f.write(content)
        

#修改target name
def modify_target_name():
    pass


if __name__ == "__main__":
    renovate_uuids()



