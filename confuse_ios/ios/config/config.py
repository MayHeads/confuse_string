""" 项目路径，调试的话，设置成自己的路径
"""


# ROOT_PROJECT_DIR = "/Users/jiangshanchen/TTRouSDK"

ROOT_PROJECT_DIR = '/Users/jiangshanchen/Desktop/Code/flutter_ttk/ttfluttersdk'

# ROOT_PROJECT_DIR = "/Users/jiangshanchen/TTRouSDK"



# 项目Scheme，用来匹配workspace，资源代码的位置
PROJECT_SCHEME = "ttfluttersdk"
# PROJECT_SCHEME = "IncomingCall"
# PROJECT_SCHEME = "Fingertip"
# PROJECT_SCHEME = "qianyan" 

# 目录前缀
ADD_DIRECTORY_PREFIX = "TT_"
# 文件前缀
ADD_FILE_PREFIX = "QY_"

#需要修改的代码前缀
ORIGIN_SYMBOL_PREFIX = "qy_"

# 混淆等级 1 - 20, 混淆的等级越高，混淆的时间越长, 最好1 - 3
CONFUSE_LEVEL = 2

# 要忽略的文件目录
IGNORE_CODE_DIRECTORY = [
    "main.m",
    "Assets.xcassets",
    "Base.lproj",
    "PetWidget",
    "Frameworks",
    "Products",
    "Pods",
    "provisioning",
    f"{PROJECT_SCHEME}Tests",
    f"{PROJECT_SCHEME}UITests",
    "FingertipWidget",
    # "OC_Ignore",
    "WWidgets",
    "ZFPlayer",
    "Mustang",
    "iflyMSC",
    "Pods",
    "KSBannerView",
    "KSArchiveTools",
    "KSLoadingView",
    "KSURLRequest",
    "KSNetworking",
    "SVProgressHUD",
    "XBExpandButton",
    "LocalPods",
    "cocos2d_libs.xcworkspace",
    "qianyan.xcodeproj",
    "Others",
    "mac",
    # "SDK",
    "Demo",
    # 新增：忽略 Pod 库相关目录
    "MyFirstLibrary",
    "KSCompossSDK",
    "TTRouSDK.debug.dylib",
    # 忽略第三方库目录
    "ThirdParty",
    "External",
    "Vendor",
    # "LocalLib",  # 忽略混淆sdk的时候需要删除掉这个
    'AAT',
    'AAB',
]
# 忽略assert不操作的目录
IGNORE_ASSERT_DEFAULT_DIRECTORY = [".colorset", ".appiconset", ".imageset"]

# 需要混淆字符串的文件
CONFUSE_STR_FILES = [
    # "FlutterCommonTool",
    # "ViewController",
    # "RequestApi",
]

# 忽略混淆的类名前缀
IGNORE_CLASS_PREFIXES = [
    'GDT',           # 广点通相关类
    'Turing',        # 图灵相关类
    'NS',            # 系统类
    'UI',            # 系统类
    'CG',            # 系统类
    'OS',            # 系统类
    'MyFirstLibrary', # Pod 库类
    'KSCompossSDK'   # 新的 Pod 库类
]

