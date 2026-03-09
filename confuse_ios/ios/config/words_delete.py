import os
import re
def deleteNumber(filepath):
    content = ""
    with open(filepath, 'r') as file:
        content = file.read()
        content = re.sub(r'\d+', '', content)
        content = re.sub(r'\b\d+\b', '', content)

    with open(filepath, 'w') as file:
        file.write(content)

    with open(filepath, "r") as f:
        lines = f.readlines()
        index = 0
        while index < len(lines):
            if lines[index].strip() == "":
                # 删除空行
                del lines[index]
                # 向上缩进
                if index > 0:
                    lines[index-1] = lines[index-1].rstrip() + "\n"
            else:
                index += 1
        with open(filepath, "w") as f:
            f.writelines(lines)


def delete_one_word(filepath,word):
    content = ""
    with open(filepath, 'r') as file:
        content = file.read()
        content = re.sub(r'({})'.format(word), '', content)

    with open(filepath, 'w') as file:
        file.write(content)

    with open(filepath, "r") as f:
        lines = f.readlines()
        index = 0
        while index < len(lines):
            if lines[index].strip() == "":
                # 删除空行
                del lines[index]
                # 向上缩进
                if index > 0:
                    lines[index-1] = lines[index-1].rstrip() + "\n"
            else:
                index += 1
        with open(filepath, "w") as f:
            f.writelines(lines)


if __name__=='__main__':
    current_path = os.path.abspath(__file__)

    parent_directory = os.path.dirname(current_path)
    print(parent_directory)
    nouns_file = os.path.join(parent_directory, 'nouns.txt')
    verbs_file = os.path.join(parent_directory, 'verbs.txt')

    # deleteNumber(nouns_file)
    # deleteNumber(verbs_file)

    delete_one_word(nouns_file,'do')
    delete_one_word(verbs_file,'do')


    #
