import os


def sub_mkdir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path, "文件夹创建成功")
        return True
    else:
        print(path, "目录已经存在")
        return False


def find_workspace_dirs(path) -> str:
    workspace_dirs = list()
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith("xcworkspace"):
                workspace_dirs.append(os.path.join(root, dir))
    return workspace_dirs[0] if len(workspace_dirs) else ""


def find_provision_dirs(path) -> str:
    workspace_dirs = list()
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith("provisioning"):
                workspace_dirs.append(os.path.join(root, dir))
    return workspace_dirs[0] if len(workspace_dirs) else ""


def find_xcodeproj_dirs(path) -> str:
    workspace_dirs = list()
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir.endswith("xcodeproj"):
                workspace_dirs.append(os.path.join(root, dir))
    return workspace_dirs[0] if len(workspace_dirs) else ""


def find_workspace_files(path):
    workspace_files = []
    print(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".plist"):
                workspace_files.append(os.path.join(root, file))
    return workspace_files[0] if len(workspace_files) else ""


def get_folder_name(path):
    folder_name = os.path.basename(path)
    folder_name = os.path.splitext(folder_name)[0]
    return folder_name


if __name__ == "__main__":
    x = "/Users/jiangshanchen/Desktop/gitee/test_ios/TestPackage/Assets.xcassets/AA_log/AA_AA_logo-main.imageset"
    print(f"----{get_folder_name(x)}")
