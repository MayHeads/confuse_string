import random
import re
import os
import time
from collections import OrderedDict

# iOS 关键字列表
IOS_KEYWORDS = {
    'class', 'struct', 'enum', 'protocol', 'extension', 'import', 'public', 'private', 'internal',
    'fileprivate', 'open', 'final', 'override', 'required', 'convenience', 'init', 'deinit', 'subscript',
    'self', 'super', 'Self', 'Type', 'Protocol', 'Any', 'AnyObject', 'nil', 'true', 'false',
    'guard', 'if', 'else', 'switch', 'case', 'default', 'for', 'while', 'repeat', 'do', 'break',
    'continue', 'return', 'throw', 'throws', 'rethrows', 'try', 'catch', 'as', 'is', 'in', 'where',
    'var', 'let', 'func', 'typealias', 'associatedtype', 'mutating', 'nonmutating', 'lazy', 'weak',
    'unowned', 'optional', 'required', 'convenience', 'override', 'final', 'open', 'public', 'internal',
    'fileprivate', 'private', 'static', 'class', 'mutating', 'nonmutating', 'prefix', 'postfix',
    'infix', 'precedencegroup', 'indirect', 'convenience', 'required', 'override', 'final', 'open',
    'public', 'internal', 'fileprivate', 'private', 'static', 'class', 'mutating', 'nonmutating',
    'prefix', 'postfix', 'infix', 'precedencegroup', 'indirect'
}

# 全局变量存储词库
NOUNS = []
VERBS = []

# 缓存最近生成的字符串，使用OrderedDict保持插入顺序
# 格式: {string: timestamp}
RECENT_STRINGS = OrderedDict()
CACHE_DURATION = 300  # 5分钟的缓存时间（秒）

def load_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
        return []

def contains_numbers(text):
    return bool(re.search(r'\d', text))

def is_valid_name(name):
    # 检查是否包含数字
    if contains_numbers(name):
        return False
    
    # 检查是否是iOS关键字
    if name.lower() in IOS_KEYWORDS:
        return False
    
    # 检查是否以数字开头
    if name[0].isdigit():
        return False
    
    return True

def generate_camel_case(words):
    return ''.join(word.capitalize() for word in words)

def clean_old_cache():
    """
    清理过期的缓存（超过5分钟的）
    """
    current_time = time.time()
    expired_keys = []
    
    for string, timestamp in RECENT_STRINGS.items():
        if current_time - timestamp > CACHE_DURATION:
            expired_keys.append(string)
    
    for key in expired_keys:
        del RECENT_STRINGS[key]

def is_string_recently_used(string):
    """
    检查字符串是否在最近5分钟内被使用过
    """
    clean_old_cache()
    return string in RECENT_STRINGS

def add_to_cache(string):
    """
    将字符串添加到缓存中
    """
    RECENT_STRINGS[string] = time.time()
    # 如果缓存太大，删除最旧的项
    if len(RECENT_STRINGS) > 1000:  # 设置一个合理的最大缓存大小
        RECENT_STRINGS.popitem(last=False)

def get_random_class_name():
    """
    生成一个随机的类名（驼峰命名）
    限制最大长度为40个字符
    """
    if not NOUNS:
        return None
    
    max_attempts = 20  # 增加最大尝试次数
    attempts = 0
    
    while attempts < max_attempts:
        # 随机选择2-3个名词
        num_words = random.randint(2, 3)
        selected_words = random.sample(NOUNS, num_words)
        class_name = generate_camel_case(selected_words)
        
        # 检查类名是否有效且长度不超过40
        if is_valid_name(class_name) and len(class_name) <= 40:
            # 检查是否最近使用过
            if not is_string_recently_used(class_name):
                add_to_cache(class_name)
                return class_name
        
        attempts += 1
    
    return None

def get_random_method_name():
    """
    生成一个随机的方法名（首字母小写的驼峰命名）
    """
    if not VERBS or not NOUNS:
        return None
    
    max_attempts = 20
    attempts = 0
    
    while attempts < max_attempts:
        # 随机选择1-2个动词和1-2个名词
        num_verbs = random.randint(1, 2)
        num_nouns = random.randint(1, 2)
        
        selected_verbs = random.sample(VERBS, num_verbs)
        selected_nouns = random.sample(NOUNS, num_nouns)
        
        # 第一个单词小写，其余单词首字母大写
        method_name = selected_verbs[0].lower()
        if len(selected_verbs) > 1:
            method_name += generate_camel_case(selected_verbs[1:])
        method_name += generate_camel_case(selected_nouns)
        
        # 检查方法名是否有效
        if is_valid_name(method_name):
            # 检查是否最近使用过
            if not is_string_recently_used(method_name):
                add_to_cache(method_name)
                return method_name
        
        attempts += 1
    
    return None

def get_random_snake_name():
    """
    生成一个随机的下划线命名
    """
    if not VERBS or not NOUNS:
        return None
    
    max_attempts = 20
    attempts = 0
    
    while attempts < max_attempts:
        # 随机选择1-2个动词和1-2个名词
        num_verbs = random.randint(1, 2)
        num_nouns = random.randint(1, 2)
        
        selected_verbs = random.sample(VERBS, num_verbs)
        selected_nouns = random.sample(NOUNS, num_nouns)
        
        # 所有单词小写并用下划线连接
        words = [verb.lower() for verb in selected_verbs] + [noun.lower() for noun in selected_nouns]
        snake_name = '_'.join(words)
        
        # 检查蛇形命名是否有效
        if is_valid_name(snake_name):
            # 检查是否最近使用过
            if not is_string_recently_used(snake_name):
                add_to_cache(snake_name)
                return snake_name
        
        attempts += 1
    
    return None

def init_word_lists():
    """
    初始化词库
    """
    global NOUNS, VERBS
    # 获取当前文件所在目录的父目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 构建词库文件的完整路径
    nouns_path = os.path.join(base_dir, 'ios_resource', 'nouns.txt')
    verbs_path = os.path.join(base_dir, 'ios_resource', 'verbs.txt')
    
    # 加载词库
    NOUNS = load_words(nouns_path)
    VERBS = load_words(verbs_path)
    
    if not NOUNS or not VERBS:
        print("Error: Required word files not found or empty")
        return False
    return True

def main():
    if not init_word_lists():
        return
    
    # 生成示例
    print("Generated Class Names:")
    for _ in range(5):
        print(get_random_class_name())
    
    print("\nGenerated Method Names:")
    for _ in range(5):
        print(get_random_method_name())
    
    print("\nGenerated Snake Case Names:")
    for _ in range(5):
        print(get_random_snake_name())

if __name__ == "__main__":
    main()
