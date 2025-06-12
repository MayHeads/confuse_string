


project_path = "/Users/jiangshanchen/confuse_string/ConfuseDemo1"


# project_path = "/Users/jiangshanchen/CSQingLi"

# 忽略文件夹
custom_ignore_folders = [
    'Pods', 'build', 'DerivedData', '.git', 
    'Tests', 'UnitTests', 'UITests'
]

### 忽略swif文件
custom_ignore_swift_files = [
    'AppDelegate.swift',
    'SceneDelegate.swift', 
    'main.swift'
]


### asset 浅醉
asset_prefix = "duc"


##### 字符串混淆  配置
# 固定文本忽略列表
ig_fix_text = [
    '.mp4',
    '.zip',
    '/',
    '.',
    ','
    
]

# 格式化字符串忽略列表（包含%的字符串）
ig_format_text = [
    '%.',
    '%d',
    '%s',
    '%f'
]