

# flutter改项目名字

1. 修改config.py中的 project_path, ROOT_PROJECT_DIR, PROJECT_SCHEME
2. 修改ios_pod_ex.py中的 change_pod_ex_with_params 中的 old_name, new_name
    1. old_name 一般都是Runner  
    2. new_name 就是新的项目名字
3. 执行python ios_pod_ex.py
4. 在 project_path对应的flutter项目下执行 python3 clean.py
5. 在xcode的工程中 添加对应的Runner的 scheme
6. 在flutter入口的 的地方也给一起修改了 需要把报错修改掉
7. 直接运行，当然 注意Runner 和 WorkSpace中的位置
