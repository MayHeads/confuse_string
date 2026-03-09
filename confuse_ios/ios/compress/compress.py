import random
import subprocess
import sys
import os
from PIL import Image
sys.path.append("./")
from ios.modes.directory_model import DirectoryModel



xx = os.path.abspath("./")
sys.path.append("./")
import ios.config as config

# from PIL import Image
import hashlib


""" 1. 搜索出assert文件的路径，对路径下的png进行压缩
"""


def search_assets_xcassets_directory():
    directory = config.ROOT_PROJECT_DIR
    for root, dirs, files in os.walk(directory):
        if os.path.basename(root) == "Assets.xcassets":
            return os.path.abspath(root)
    return None


""" 2. 压缩该路径下以png结尾的图片
"""


def compress_png_images_main(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".png"):
                image_path = os.path.join(root, file)
                image = Image.open(image_path)
                # compress_quality = random.randint(70, 90)
                compress_quality = random.uniform(30.00000, 40.0000)
                print(f"<compress> {compress_quality}")
                image.save(image_path, optimize=True, quality=compress_quality)
                # 计算压缩后的 PNG 文件的 MD5 值
                with open(image_path, "rb") as f:
                    content = f.read()
                    md5 = hashlib.md5(content).hexdigest()
                    print(f"<compress>{file}: {md5}")


""" 3. 压缩该路径下以png结尾的图片 使每次的md5都不一样
"""


def compress_png_images_md5(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".png"):
                image_path = os.path.join(root, file)

                # 使用 pngquant 进行无损压缩
                compress_command = f"pngquant --ext=.png --force {image_path}"
                subprocess.run(compress_command, shell=True)

                # 计算压缩后的 PNG 文件的 MD5 值
                with open(image_path, "rb") as f:
                    content = f.read()
                    md5 = hashlib.md5(content).hexdigest()
                    print(f"{file}: {md5}")


""" 4. 直接修改md5
"""


def change_md5(directory):
    # directory = "/Users/jiangshanchen/step_ios/PetTravel/PetTravel/Assets.xcassets"
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".png"):
                image_path = os.path.join(root, file)

                # 使用 pngquant 进行无损压缩
                compress_command = f"echo bomb >> {image_path}"
                subprocess.run(compress_command, shell=True)

                # 计算压缩后的 PNG 文件的 MD5 值
                with open(image_path, "rb") as f:
                    content = f.read()
                    md5 = hashlib.md5(content).hexdigest()
                    print(f"{file}: {md5}")
                    
def c_compress_md5_change():
    x = DirectoryModel().xcassets
    compress_png_images_main(x)
    change_md5(x)

if __name__ == "__main__":
    # # 获取`Assets.xcassets`的路径
    # x = DirectoryModel().xcassets
    # print(x)

    # # 压缩图片
    # compress_png_images_main(x)

    # # # 修改md5
    # change_md5(x)
    c_compress_md5_change()
