# from concurrent.futures import ThreadPoolExecutor
# import os
# import time
# import string
# import sys
# from pprint import pprint
# import re

# sys.path.append("./")
# # from ios.config import config as Config
# from ios.config import config

# if __name__ == "__main__":
#     # pattern = r"path"
#     file_path = "./ios/text/demo_text.txt"

#     print("\*")
#     # path\s*=\s*(ViewController);
#     # path = xxx;
#     line_pattern = r"path\s*=\s*({});".format("ViewController")

#     # /\*\s*(ViewController)\s*\*/
#     # /* xxx */
#     comment_pattern = r"/\*\s*({})\s*\*/".format("ViewController")

#     print(line_pattern, comment_pattern, end="\n")

#     with open(file_path, "r") as file:
#         file_content = file.read()
#         # print(file_content)

#         line_pattern = r"\*\*\s*({})\s\*\*".format("name")
#         file_content = re.sub(line_pattern, f"** {'TTT'} **", file_content)
#         print(file_content)

#     print(
#         re.sub(
#             r"def\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(\s*\):",
#             r"static PyObject*\npy_\1(void)\n{",
#             "def myfunc(name, branch, cast):",
#         )
#     )
import os
import sys

sys.path.append("./")
from ios.config import config as Config
from ios.handle_root.assert_handle import *

if __name__ == "__main__":
    x = DirectoryModel().xcassets
    modify_assert_folder_only(x)
    modify_imagesert_foler_only(x)
    print("result - const", replace_image_name)
