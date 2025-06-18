
project_path = "/Users/jiangshanchen/confuse_string/ConfuseDemo1"


# project_path = "/Users/jiangshanchen/CSQingLi"

# 忽略文件夹  <忽略的swift文件夹>
custom_ignore_folders = [
    'Pods', 'build', 'DerivedData', '.git', 
    'Tests', 'UnitTests', 'UITests'
]

### 忽略swif文件  <忽略的swift文件>
custom_ignore_swift_files = [
    'AppDelegate.swift',
    'SceneDelegate.swift', 
    'main.swift'
]


### asset 浅醉 <asset 前缀>
asset_prefix = "duc"


ASSET_IMAGE_CONFIG = {
    'width_range': (100, 200),      # 图片宽度范围
    'height_range': (200, 300),     # 图片高度范围
    'blur_range': (1, 5),           # 模糊程度范围
    'imageset_count_range': (2, 3)  # 每个文件夹生成的imageset数量范围
}

##### 字符串混淆  配置 <字符串混淆忽略>
# 固定文本忽略列表
ig_fix_text = [
    '.mp4',
    '.zip',
    '/',
    '.',
    ','
    
]

# 格式化字符串忽略列表（包含%的字符串） <字符串混淆忽略>
ig_format_text = [
    '%.',
    '%d',
    '%s',
    '%f'
]


#  替换类名和方法前缀 <替换类名和方法前缀>
STRING_SUFFIX = '_ckm'


# 需要忽略的文件名列表  <替换文件名>
REPLACE_IGNORE_FILE_NAMES = {
    'AppDelegate',
    'SceneDelegate',
    'ViewController',
    'Main',
    'Info',
    'Assets',
}

# 生成swif文件的主题和数量
THEME_KEYWORDS = ["壁纸系列"]  # 主题关键字列表
NUM_FILES = 100  # 要生成的文件数量