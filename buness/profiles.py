from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BunessProfile:
    name: str
    description: str
    steps: list[str]
    overrides: dict[str, object] = field(default_factory=dict)


PROFILES = {
    "tt_clean_sdk": BunessProfile(
        name="tt_clean_sdk",
        description="原始清理 SDK 流程：Pod 替换、固定文本替换、字符串加密、文件处理、垃圾代码、pod install。",
        steps=[
            "change_pod_ex",
            "z_replace_fix_form",
            "z_enc_combin",
            "z_replace_file",
            "z_gen_process",
            "insert_action",
            "execute_pod_install",
        ],
    ),
    "tt_compass_sdk": BunessProfile(
        name="tt_compass_sdk",
        description="保持当前行为，只执行 SwiftUI 生成流程。",
        steps=["z_gen_process"],
    ),
    "tt_rate_tracker": BunessProfile(
        name="tt_rate_tracker",
        description="保持当前行为，只执行 confuse_ios 垃圾代码插入。",
        steps=["insert_action"],
    ),
    "tt_route_sdk": BunessProfile(
        name="tt_route_sdk",
        description="Route SDK 全流程，包含配置覆盖、Pod 替换、字符串和文件处理、垃圾代码、pod install。",
        overrides={
            "NEW_POD_FILE_NAME": "CCVIdeoSDK",
            "THEME_KEYWORDS": ["来电秀", "铃声", "图片", "视频", "结果"],
            "NUM_FILES": 50,
            "project_path": "/Users/jiangshanchen/TTRouSDK",
            "ROOT_PROJECT_DIR": "/Users/jiangshanchen/TTRouSDK",
            "IS_POD_CONFUSE_MODE": True,
            "ORIGIN_POD_FILE_NAME": "MyFirstLibrary",
            "custom_ignore_folders": [
                "Pods",
                "build",
                "DerivedData",
                ".git",
                "Tests",
                "UnitTests",
                "UITests",
                "1234",
            ],
            "asset_prefix": "xyk",
        },
        steps=[
            "change_pod_ex",
            "z_replace_fix_form",
            "z_enc_combin",
            "z_replace_file",
            "z_gen_process",
            "insert_action",
            "execute_pod_install",
        ],
    ),
    "tt_route_sdk_flutter": BunessProfile(
        name="tt_route_sdk_flutter",
        description="Flutter Route SDK 流程，含 Dart/Plugin 重命名、README 映射同步、字符串加密、垃圾代码、Pod 和 clean.py。",
        overrides={
            "NEW_POD_FILE_NAME": "flutter_base_sdk",
            "THEME_KEYWORDS": ["来电秀", "铃声", "图片", "视频", "结果"],
            "NUM_FILES": 100,
            "project_path": "/Users/jiangshanchen/Desktop/Code/flutter_ttk/ttfluttersdk",
            "ROOT_PROJECT_DIR": "/Users/jiangshanchen/Desktop/Code/flutter_ttk/ttfluttersdk",
            "IS_POD_CONFUSE_MODE": False,
            "ORIGIN_POD_FILE_NAME": "ttfluttersdk_plugin",
            "custom_ignore_folders": [
                "Pods",
                "build",
                "DerivedData",
                ".git",
                "Tests",
                "UnitTests",
                "UITests",
                "1234",
            ],
            "asset_prefix": "xyk",
        },
        steps=[
            "z_replace_file_flutter",
            "replace_readme:file_name_flutter.txt",
            "z_replace_fix_form_flutter",
            "replace_readme:replace_fix_form_flutter.txt",
            "z_replace_file_flutter_plugin_swift",
            "replace_readme:file_name_flutterplugin_swift.txt",
            "z_replace_pkm_strings_in_flutter_plugin",
            "replace_readme:file_name_flutterplugin_content.txt",
            "z_enc_combin_flutter",
            "z_enc_combin_flutter_swift",
            "insert_action",
            "change_pod_ex",
            "execute_clean_py",
        ],
    ),
    "tt_single_lji_souce": BunessProfile(
        name="tt_single_lji_souce",
        description="保持当前行为：只生成 imageset 和 SwiftUI 文件。名称沿用历史拼写。",
        steps=[
            "entry_gener_imageset",
            "z_gen_process",
        ],
    ),
    "tt_video_re": BunessProfile(
        name="tt_video_re",
        description="视频资源项目流程：覆盖配置后执行固定文本替换、文件替换和垃圾代码插入。",
        overrides={
            "NEW_POD_FILE_NAME": "TSComSDK",
            "THEME_KEYWORDS": ["支持 缠绕"],
            "NUM_FILES": 5,
            "project_path": "/Users/jiangshanchen/TTVideoRe",
            "ROOT_PROJECT_DIR": "/Users/jiangshanchen/TTVideoRe",
        },
        steps=[
            "sleep:1",
            "z_replace_fix_form",
            "z_replace_file",
            "insert_action",
        ],
    ),
}
