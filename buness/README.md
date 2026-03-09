# buness 用法

这次重构的目标是两件事：

1. 保留你现在的旧用法，不需要重新记命令。
2. 把配置收口到根目录的 [config.py](/Users/jiangshanchen/confuse_string/config.py)。

## 你现在怎么用

旧脚本路径全部保留，下面这些命令还能继续用：

```bash
python3 buness/tt_clean_sdk/tt_clean_sdk.py
python3 buness/tt_compass_sdk/tt_compass.py
python3 buness/tt_rate_tracker/tt_rate_tracker.py
python3 buness/tt_route_sdk/tt_route_sdk.py
python3 buness/tt_route_sdk_flutter/tt_route_sdk_flutter.py
python3 buness/tt_single_lji_souce/tt_single_laji_souce.py
python3 buness/tt_video_re/tt_video_re.py
```

这些脚本现在只是“兼容入口”，内部会走统一 runner。

## 新入口

如果你想统一查看和执行 profile，可以直接用：

```bash
python3 -m buness.cli list
python3 -m buness.cli show tt_route_sdk
python3 -m buness.cli run tt_route_sdk
```

## 配置怎么改

现在只改一个文件：

- [config.py](/Users/jiangshanchen/confuse_string/config.py)

`confuse_ios/ios/config/config.py` 已经改成桥接层，不再单独维护。

常改的配置：

- `project_path`: 当前目标工程路径
- `PROJECT_SCHEME`: `confuse_ios` 里主工程目录名
- `NEW_POD_FILE_NAME`: 新 Pod 名
- `ORIGIN_POD_FILE_NAME`: 原 Pod 名
- `THEME_KEYWORDS`: 生成 SwiftUI 文件主题
- `NUM_FILES`: 生成文件数量
- `IS_POD_CONFUSE_MODE`: 是否走 Pod 混淆模式
- `custom_ignore_folders`: 项目扫描忽略目录

## 每个 profile 当前会做什么

### `tt_clean_sdk`

执行顺序：

1. `change_pod_ex`
2. `z_replace_fix_form`
3. `z_enc_combin`
4. `z_replace_file`
5. `z_gen_process`
6. `insert_action`
7. `pod install`

### `tt_compass_sdk`

保持你当前脚本行为，只执行：

1. `z_gen_process`

### `tt_rate_tracker`

保持你当前脚本行为，只执行：

1. `insert_action`

### `tt_route_sdk`

会先把 profile 里的覆盖项同步进 [config.py](/Users/jiangshanchen/confuse_string/config.py)，再执行：

1. `change_pod_ex`
2. `z_replace_fix_form`
3. `z_enc_combin`
4. `z_replace_file`
5. `z_gen_process`
6. `insert_action`
7. `pod install`

### `tt_route_sdk_flutter`

执行顺序：

1. Dart 文件重命名
2. README 映射同步
3. Flutter 固定词替换
4. README 映射同步
5. Flutter plugin Swift 文件重命名
6. README 映射同步
7. Flutter plugin 内容替换
8. README 映射同步
9. Flutter 字符串加密
10. Flutter plugin Swift 字符串加密
11. `insert_action`
12. `change_pod_ex`
13. 执行 `clean.py`

### `tt_single_lji_souce`

保持你当前脚本行为，只执行：

1. `entry_gener_imageset`
2. `z_gen_process`

### `tt_video_re`

会先把 profile 里的覆盖项同步进 [config.py](/Users/jiangshanchen/confuse_string/config.py)，再执行：

1. 等待 1 秒
2. `z_replace_fix_form`
3. `z_replace_file`
4. `insert_action`

## profile 配置放哪

如果你以后还想继续保留“每个脚本一套默认参数”的习惯，就改：

- [buness/profiles.py](/Users/jiangshanchen/confuse_string/buness/profiles.py)

里面的 `overrides` 是 profile 自带覆盖项，执行脚本时会先写回 [config.py](/Users/jiangshanchen/confuse_string/config.py)。

适合放在 `overrides` 里的值：

- `project_path`
- `PROJECT_SCHEME`
- `NEW_POD_FILE_NAME`
- `ORIGIN_POD_FILE_NAME`
- `THEME_KEYWORDS`
- `NUM_FILES`
- `IS_POD_CONFUSE_MODE`

## 建议的日常用法

如果只是切一个项目跑现有流程：

1. 先改 [config.py](/Users/jiangshanchen/confuse_string/config.py)
2. 再执行原来的 `buness/.../*.py`

如果是固定项目、固定流程：

1. 改 [buness/profiles.py](/Users/jiangshanchen/confuse_string/buness/profiles.py) 对应 profile 的 `overrides`
2. 直接跑对应脚本



## 常用命令

### 运行原生sdk混淆
python3 -m buness.cli run tt_route_sdk

### 运行flutter sdk混淆
python3 -m buness.cli run tt_route_sdk_flutter
