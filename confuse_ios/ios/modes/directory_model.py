import sys
import os

sys.path.append("./ios")
import config.config as config

sys.path.append("../../")


p = os.path.abspath("../../")


PATH1 = "1234"
root = config.ROOT_PROJECT_DIR
scheme = config.PROJECT_SCHEME

def search_directories(target_dir_name):
    root_dir = config.ROOT_PROJECT_DIR
    result = []
    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name == target_dir_name:
                result.append(os.path.join(root, dir_name))
    if len(result)  == 0:
        print(f'{target_dir_name} 路径为空')
        return ''
    return result[0] 

def search_files(part_file_name):
    root_dir = config.ROOT_PROJECT_DIR
    result = []
    for root, dirs, files in os.walk(root_dir):
        for file_name in files:
            if part_file_name in file_name:
                result.append(os.path.join(root, file_name))
    if len(result)  == 0:
        print(f'{part_file_name} 路径为空')
        return ''
    return result[0]



class DirectoryModel:
    """
    路径path
    """

        # self.xcworkspace = '/Users/jiangshanchen/charge_ios/归档/qianyan.xcworkspace'
        # self.code = '/Users/jiangshanchen/charge_ios/归档/qianyan/qianyan/Business'
        # self.xcassets = '/Users/jiangshanchen/charge_ios/归档/qianyan/qianyan/Others/Assets.xcassets'
        # self.pbxproject = '/Users/jiangshanchen/charge_ios/归档/qianyan/qianyan.xcodeproj/project.pbxproj'

    xcworkspace: str
    code: str
    xcassets: str
    pbxproject: str
    bridge_header: str
    main_storyboard: str
    # project_path = "YourProject.xcodeproj/project.pbxproj"

    def __init__(self):
        self.code = root + '/' + scheme
        s_work_space = scheme + '.xcworkspace'
        s_asset = 'Assets.xcassets'
        s_xcproject = scheme + '.xcodeproj'
        self.xcworkspace = search_directories(target_dir_name=s_work_space)
        self.xcassets = search_directories(target_dir_name=s_asset)
        self.pbxproject = search_directories(target_dir_name=s_xcproject) + '/project.pbxproj'
        self.bridge_header = search_files(part_file_name='Bridging-Header')
        self.main_storyboard = search_files(part_file_name='Main.storyboard')


    def __repr__(self):
        return f"workspace: {self.xcworkspace}\n code: {self.code} \n assets: {self.xcassets} \n pbxproject: {self.pbxproject}\n bridge_header: {self.bridge_header}\n bridge_header: {self.main_storyboard}"


if __name__ == "__main__":
    x = DirectoryModel()
    print(x)

