from file_name import rename_swift_file
from gen_file_swiftui import gen_file_swiftui
from co_swiui import collect_swiftui_name
from single_swifui import single_swifui
from move_view import copy_folders_to_content_path

def z_replace_file():
    rename_swift_file()

def z_gen_process():
    gen_file_swiftui()
    collect_swiftui_name()
    single_swifui()
    copy_folders_to_content_path()


if __name__ == '__main__':
    z_gen_process()