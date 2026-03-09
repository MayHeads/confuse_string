import os
import sys
import time
sys.path.append("./")
from ios.compress import compress

from ios.config import config
from ios.log import log
from ios.handle_swift_class import rubbish_ivar_insert,file_name_handle,struct_type_change
from ios.handle_root import assert_handle,directory_name_handle, add_code
from ios.handle_oc_class import file_name_handle as oc_file_name_handle
from ios.handle_oc_class import  struct_name_modify,insert_rubbish_ivar, add_rubbish_native_code
from ios.handle_oc_class import  disorganize_func_define_sequence
from ios.replace_code_handle import modify


if __name__=='__main__':
    ###  SWIFT

    # ========================================== 资源和文件 ==========================================
    # ========================================== 文件名 ==========================================
    # ========================================== 代码 ==========================================
    start_time = time.time()
    
    # 清空日志
    log.clear()
    log.logger.info(f'混淆项目路径：{config.ROOT_PROJECT_DIR}\n\n')

    # 1. 压缩图片修改md5
    # compress.c_compress_md5_change()

    # # 2. 修改asset资源文件夹下的图片名称，工程中的名字
    # assert_handle.c_modifier_assert_folder_and_filename()

    # # 3. 修改代码位置主工程目录下的文件夹名称
    # directory_name_handle.c_add_prefix_to_directories()

    # # 4. 插入代码x
    add_code.c_add_random_code()

    # # 5. 修改 swift 文件名
    # file_name_handle.rename_files()

    # # 6. 修改 swift 文件块中class struct 
    # struct_type_change.handle_change_module_name()
    
    # # 7. 插入垃圾代码--属性
    rubbish_ivar_insert.handle_insert_rubbish_ivar()


    ### OC
    # 8. 修改 oc 文件名
    # oc_file_name_handle.change_file_name()

    # 9. 修改 模块名字
    # struct_name_modify.start()

    # 10. 插入垃圾属性
    # insert_rubbish_ivar.start()

    # 11. 插入垃圾代码
    # add_rubbish_native_code.start()

    # 12. 打乱函数定义顺序
    # disorganize_func_define_sequence.start()

    # 13. 修改带有前缀的方法属性
    # modify.start()

    end_time = time.time()
    print(f"总耗时耗时：{end_time - start_time}")

    log.logger.info(f'\n\n\n混淆项目完成，总用时{end_time - start_time}')