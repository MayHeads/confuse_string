"""统一项目配置。

这是整个仓库唯一的配置源：
- 根目录脚本直接读取这里
- confuse_ios/ios/config/config.py 会桥接到这里

如无特殊说明，优先修改这个文件，不要再分别维护两套配置。
"""

# ==================== 目标项目 ====================

project_path = '/Users/jiangshanchen/TTRouSDK'
ROOT_PROJECT_DIR = '/Users/jiangshanchen/TTRouSDK'
PROJECT_SCHEME = 'ttfluttersdk'

# ==================== 扫描/过滤配置 ====================

custom_ignore_folders = ['Pods', 'build', 'DerivedData', '.git', 'Tests', 'UnitTests', 'UITests', '1234']
custom_ignore_swift_files = []

# ==================== Asset 配置 ====================

asset_prefix = 'xyk'
ASSET_IMAGE_CONFIG = {'width_range': (100, 200),
 'height_range': (200, 300),
 'blur_range': (1, 5),
 'imageset_count_range': (2, 3)}

# ==================== 字符串混淆配置 ====================

ig_fix_text = ['.mp4', '.zip', '/', '.', ',']
ig_format_text = ['%.', '%d', '%s', '%f']
STRING_SUFFIX = '_pkm'
CONFUSE_KEY = '0C32C2KT2FE79YKC'
IS_POD_CONFUSE_MODE = True

# ==================== 文件/命名替换配置 ====================

REPLACE_IGNORE_FILE_NAMES = {
    'AppDelegate',
    'Assets',
    'Info',
    'Main',
    'SceneDelegate',
    'ViewController',
}
THEME_KEYWORDS = ['来电秀', '铃声', '图片', '视频', '结果']
NUM_FILES = 50
ORIGIN_POD_FILE_NAME = 'MyFirstLibrary'
NEW_POD_FILE_NAME = 'CCVIdeoSDK'

# ==================== confuse_ios 相关配置 ====================

ADD_DIRECTORY_PREFIX = 'TT_'
ADD_FILE_PREFIX = 'QY_'
ORIGIN_SYMBOL_PREFIX = 'qy_'
CONFUSE_LEVEL = 2
IGNORE_CODE_DIRECTORY = ['main.m',
 'Assets.xcassets',
 'Base.lproj',
 'PetWidget',
 'Frameworks',
 'Products',
 'Pods',
 'provisioning',
 'ttfluttersdkTests',
 'ttfluttersdkUITests',
 'FingertipWidget',
 'WWidgets',
 'ZFPlayer',
 'Mustang',
 'iflyMSC',
 'Pods',
 'KSBannerView',
 'KSArchiveTools',
 'KSLoadingView',
 'KSURLRequest',
 'KSNetworking',
 'SVProgressHUD',
 'XBExpandButton',
 'LocalPods',
 'cocos2d_libs.xcworkspace',
 'qianyan.xcodeproj',
 'Others',
 'mac',
 'Demo',
 'MyFirstLibrary',
 'KSCompossSDK',
 'TTRouSDK.debug.dylib',
 'ThirdParty',
 'External',
 'Vendor',
 'AAT',
 'AAB']
IGNORE_ASSERT_DEFAULT_DIRECTORY = ['.colorset', '.appiconset', '.imageset']
CONFUSE_STR_FILES = []
IGNORE_CLASS_PREFIXES = ['GDT', 'Turing', 'NS', 'UI', 'CG', 'OS', 'MyFirstLibrary', 'KSCompossSDK']
