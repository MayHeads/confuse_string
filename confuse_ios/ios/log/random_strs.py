import nltk
from nltk.corpus import wordnet
import random

# ========================================== 配置 ==========================================

# 有需要的自己添加
ignore_keywords = [
    "associatedtype", "class", "deinit", "enum", "extension", "func",
    "import", "init", "inout", "let", "operator", "precedencegroup",
    "protocol", "struct", "subscript", "typealias", "var", "fileprivate",
    "internal", "private", "public", "static", "defer", "if", "guard",
    "do", "repeat", "else", "for", "in", "while", "return", "break",
    "continue", "fallthrough", "switch", "case", "default", "where",
    "catch", "throw", "as", "Any", "false", "is", "nil", "super", "self",
    "Self", "true", "try", "throws", "case"
]

# 判断字符串是否用数字开头
def is_start_with_number(string):
    return string[0].isdigit()
# 判断
def contain_numer_str(items):
    for index in range(len(items)):
        if is_start_with_number(items[index]) or contain_ignore_keyword(items):
            return True
# 包含顶部的那个关键字
def contain_ignore_keyword(items):
    for index in range(len(items)):
        if items[index] in ignore_keywords:
            return True


def get_verbs():
    verbs = []
    for synset in wordnet.all_synsets(pos="v"):
        for lemma in synset.lemmas():
            verbs.append(lemma.name())
    return verbs


def get_nouns():
    nouns = []
    for synset in wordnet.all_synsets(pos="n"):
        for lemma in synset.lemmas():
            nouns.append(lemma.name())
    return nouns


def get_one_or_two_verb_words():
    datas = []
    with open("./ios/config/verbs.txt", "r") as file:
        words = file.readlines()
        random_words = random.sample(words, k=random.randint(1, 2))
        while contain_numer_str(random_words):
            random_words = random.sample(words, k=random.randint(1, 2))
        for word in random_words:
            datas.append(word.strip())
    return datas


def get_one_or_two_nonu_words():
    datas = []
    with open("./ios/config/nouns.txt", "r") as file:
        words = file.readlines()
        random_words = random.sample(words, k=random.randint(1, 2))
        while contain_numer_str(random_words):
            random_words = random.sample(words, k=random.randint(1, 2))
        for word in random_words:
            datas.append(word.strip())
    return datas


# 获取类名
def camel_case_class_name():
    x = get_one_or_two_nonu_words()
    y = get_one_or_two_verb_words()
    y = x[0].capitalize() + y[0].capitalize()
    return y


# 获取方法名
def camel_case_fun_name():
    x = get_one_or_two_nonu_words()
    y = get_one_or_two_verb_words()
    datas = x + y
    camel_case = "".join(
        word.capitalize() if i != 0 else word.lower() for i, word in enumerate(datas)
    )
    return camel_case


# 获取属性名
def lower_ivar_name():
    datas = []
    with open("./ios/config/nouns.txt", "r") as file:
        words = file.readlines()
        random_words = random.sample(words, k=random.randint(1, 1))
        for word in random_words:
            datas.append(word.strip())
    return decapitalize(datas[0])

def decapitalize(s, upper_rest = False):
  return ''.join([s[:1].lower(), (s[1:].upper() if upper_rest else s[1:])])


def get_single_word():
    datas = []
    with open("./ios/config/nouns.txt", "r") as file:
        words = file.readlines()
        random_words = random.sample(words, k=random.randint(1, 1))
        for word in random_words:
            datas.append(word.strip())
    return datas[0]

if __name__ == "__main__":
    print(get_one_or_two_nonu_words())
