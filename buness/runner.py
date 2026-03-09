from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import time
from pathlib import Path
from pprint import pformat

from buness.profiles import PROFILES, BunessProfile


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.py"
CONFUSE_IOS_PATH = REPO_ROOT / "confuse_ios"
IOS_LOG_PATH = REPO_ROOT / "ios_log"

CONFIG_FIELD_ORDER = [
    "project_path",
    "ROOT_PROJECT_DIR",
    "PROJECT_SCHEME",
    "custom_ignore_folders",
    "custom_ignore_swift_files",
    "asset_prefix",
    "ASSET_IMAGE_CONFIG",
    "ig_fix_text",
    "ig_format_text",
    "STRING_SUFFIX",
    "CONFUSE_KEY",
    "IS_POD_CONFUSE_MODE",
    "REPLACE_IGNORE_FILE_NAMES",
    "THEME_KEYWORDS",
    "NUM_FILES",
    "ORIGIN_POD_FILE_NAME",
    "NEW_POD_FILE_NAME",
    "ADD_DIRECTORY_PREFIX",
    "ADD_FILE_PREFIX",
    "ORIGIN_SYMBOL_PREFIX",
    "CONFUSE_LEVEL",
    "IGNORE_CODE_DIRECTORY",
    "IGNORE_ASSERT_DEFAULT_DIRECTORY",
    "CONFUSE_STR_FILES",
    "IGNORE_CLASS_PREFIXES",
]

DEFAULT_CONFIG_VALUES = {
    "project_path": "/Users/jiangshanchen/Desktop/pencial/LaiShow/laishow_app/ios",
    "ROOT_PROJECT_DIR": "/Users/jiangshanchen/Desktop/pencial/LaiShow/laishow_app/ios",
    "PROJECT_SCHEME": "ttfluttersdk",
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
    "custom_ignore_swift_files": [],
    "asset_prefix": "xyk",
    "ASSET_IMAGE_CONFIG": {
        "width_range": (100, 200),
        "height_range": (200, 300),
        "blur_range": (1, 5),
        "imageset_count_range": (2, 3),
    },
    "ig_fix_text": [".mp4", ".zip", "/", ".", ","],
    "ig_format_text": ["%.", "%d", "%s", "%f"],
    "STRING_SUFFIX": "_pkm",
    "CONFUSE_KEY": "0C32C2KT2FE79YKC",
    "IS_POD_CONFUSE_MODE": False,
    "REPLACE_IGNORE_FILE_NAMES": {
        "AppDelegate",
        "Assets",
        "Info",
        "Main",
        "SceneDelegate",
        "ViewController",
    },
    "THEME_KEYWORDS": ["来电秀", "铃声", "图片", "视频", "结果"],
    "NUM_FILES": 50,
    "ORIGIN_POD_FILE_NAME": "MyFirstLibrary",
    "NEW_POD_FILE_NAME": "MCCleanSDK",
    "ADD_DIRECTORY_PREFIX": "TT_",
    "ADD_FILE_PREFIX": "QY_",
    "ORIGIN_SYMBOL_PREFIX": "qy_",
    "CONFUSE_LEVEL": 2,
    "IGNORE_CODE_DIRECTORY": [
        "main.m",
        "Assets.xcassets",
        "Base.lproj",
        "PetWidget",
        "Frameworks",
        "Products",
        "Pods",
        "provisioning",
        "ttfluttersdkTests",
        "ttfluttersdkUITests",
        "FingertipWidget",
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
        "Demo",
        "MyFirstLibrary",
        "KSCompossSDK",
        "TTRouSDK.debug.dylib",
        "ThirdParty",
        "External",
        "Vendor",
        "AAT",
        "AAB",
    ],
    "IGNORE_ASSERT_DEFAULT_DIRECTORY": [".colorset", ".appiconset", ".imageset"],
    "CONFUSE_STR_FILES": [],
    "IGNORE_CLASS_PREFIXES": [
        "GDT",
        "Turing",
        "NS",
        "UI",
        "CG",
        "OS",
        "MyFirstLibrary",
        "KSCompossSDK",
    ],
}


def _load_root_config_module():
    spec = importlib.util.spec_from_file_location("_buness_root_config", CONFIG_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载配置文件: {CONFIG_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_root_config_values() -> dict[str, object]:
    try:
        module = _load_root_config_module()
    except Exception as exc:
        print(f"警告: 读取 config.py 失败，使用默认配置重建。原因: {exc}")
        return dict(DEFAULT_CONFIG_VALUES)

    values = {}
    for key in CONFIG_FIELD_ORDER:
        values[key] = getattr(module, key)
    return values


def _render_value(value: object) -> str:
    if isinstance(value, set):
        if not value:
            return "set()"
        items = "\n".join(f"    {item!r}," for item in sorted(value))
        return "{\n" + items + "\n}"
    return pformat(value, width=88, sort_dicts=False)


def _render_config(values: dict[str, object]) -> str:
    content = [
        '"""统一项目配置。',
        "",
        "这是整个仓库唯一的配置源：",
        "- 根目录脚本直接读取这里",
        "- confuse_ios/ios/config/config.py 会桥接到这里",
        "",
        "如无特殊说明，优先修改这个文件，不要再分别维护两套配置。",
        '"""',
        "",
        "# ==================== 目标项目 ====================",
        "",
        f"project_path = {_render_value(values['project_path'])}",
        f"ROOT_PROJECT_DIR = {_render_value(values['ROOT_PROJECT_DIR'])}",
        f"PROJECT_SCHEME = {_render_value(values['PROJECT_SCHEME'])}",
        "",
        "# ==================== 扫描/过滤配置 ====================",
        "",
        f"custom_ignore_folders = {_render_value(values['custom_ignore_folders'])}",
        f"custom_ignore_swift_files = {_render_value(values['custom_ignore_swift_files'])}",
        "",
        "# ==================== Asset 配置 ====================",
        "",
        f"asset_prefix = {_render_value(values['asset_prefix'])}",
        f"ASSET_IMAGE_CONFIG = {_render_value(values['ASSET_IMAGE_CONFIG'])}",
        "",
        "# ==================== 字符串混淆配置 ====================",
        "",
        f"ig_fix_text = {_render_value(values['ig_fix_text'])}",
        f"ig_format_text = {_render_value(values['ig_format_text'])}",
        f"STRING_SUFFIX = {_render_value(values['STRING_SUFFIX'])}",
        f"CONFUSE_KEY = {_render_value(values['CONFUSE_KEY'])}",
        f"IS_POD_CONFUSE_MODE = {_render_value(values['IS_POD_CONFUSE_MODE'])}",
        "",
        "# ==================== 文件/命名替换配置 ====================",
        "",
        f"REPLACE_IGNORE_FILE_NAMES = {_render_value(values['REPLACE_IGNORE_FILE_NAMES'])}",
        f"THEME_KEYWORDS = {_render_value(values['THEME_KEYWORDS'])}",
        f"NUM_FILES = {_render_value(values['NUM_FILES'])}",
        f"ORIGIN_POD_FILE_NAME = {_render_value(values['ORIGIN_POD_FILE_NAME'])}",
        f"NEW_POD_FILE_NAME = {_render_value(values['NEW_POD_FILE_NAME'])}",
        "",
        "# ==================== confuse_ios 相关配置 ====================",
        "",
        f"ADD_DIRECTORY_PREFIX = {_render_value(values['ADD_DIRECTORY_PREFIX'])}",
        f"ADD_FILE_PREFIX = {_render_value(values['ADD_FILE_PREFIX'])}",
        f"ORIGIN_SYMBOL_PREFIX = {_render_value(values['ORIGIN_SYMBOL_PREFIX'])}",
        f"CONFUSE_LEVEL = {_render_value(values['CONFUSE_LEVEL'])}",
        f"IGNORE_CODE_DIRECTORY = {_render_value(values['IGNORE_CODE_DIRECTORY'])}",
        (
            "IGNORE_ASSERT_DEFAULT_DIRECTORY = "
            f"{_render_value(values['IGNORE_ASSERT_DEFAULT_DIRECTORY'])}"
        ),
        f"CONFUSE_STR_FILES = {_render_value(values['CONFUSE_STR_FILES'])}",
        f"IGNORE_CLASS_PREFIXES = {_render_value(values['IGNORE_CLASS_PREFIXES'])}",
        "",
    ]
    return "\n".join(content)


def sync_root_config(overrides: dict[str, object] | None = None) -> dict[str, object]:
    values = _load_root_config_values()
    overrides = overrides or {}

    values.update(overrides)
    values["ROOT_PROJECT_DIR"] = values["project_path"]

    CONFIG_PATH.write_text(_render_config(values), encoding="utf-8")
    importlib.invalidate_caches()
    sys.modules.pop("config", None)
    return values


def _project_info():
    from project_scanner import get_project_info

    return get_project_info()


def _run_pod_install() -> None:
    project_info = _project_info()
    print(f"执行 pod install: {project_info.project_path}")
    subprocess.run(
        ["pod", "install", "--verbose"],
        cwd=project_info.project_path,
        check=True,
    )


def _run_confuse_ios_entry() -> None:
    print(f"执行 confuse_ios: {CONFUSE_IOS_PATH}")
    subprocess.run(
        [sys.executable, "ios/entry/entry.py"],
        cwd=CONFUSE_IOS_PATH,
        check=True,
    )


def _execute_clean_py() -> None:
    project_info = _project_info()
    flutter_clean_py = project_info.flutter_clenpy
    if not flutter_clean_py:
        print("未找到 clean.py 文件，跳过执行")
        return

    clean_path = Path(flutter_clean_py)
    print(f"执行 clean.py: {clean_path}")
    subprocess.run(
        [sys.executable, clean_path.name],
        cwd=clean_path.parent,
        check=True,
    )


def _load_mapping_from_log(log_name: str) -> dict[str, str]:
    mapping = {}
    log_file = IOS_LOG_PATH / log_name
    if not log_file.exists():
        print(f"未找到日志文件，跳过 README 替换: {log_file}")
        return mapping

    with log_file.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or "👉" in line or "👈" in line:
                continue
            if " -> " in line:
                old_value, new_value = line.split(" -> ", 1)
            elif " <-----------> " in line:
                old_value, new_value = line.split(" <-----------> ", 1)
            else:
                continue

            old_value = old_value.strip()
            new_value = new_value.strip()
            if old_value and new_value:
                mapping[old_value] = new_value
    return mapping


def _replace_readme_from_log(log_name: str) -> None:
    from buness.tt_route_sdk_flutter.readme_replace_helper import (
        replace_strings_in_readme_file,
    )

    mapping = _load_mapping_from_log(log_name)
    if not mapping:
        print(f"日志中没有可替换的映射，跳过: {log_name}")
        return

    print(f"同步 README 映射: {log_name}")
    replace_strings_in_readme_file(mapping)


def _run_step(step: str) -> None:
    if step.startswith("sleep:"):
        seconds = float(step.split(":", 1)[1])
        print(f"等待 {seconds} 秒")
        time.sleep(seconds)
        return

    if step.startswith("replace_readme:"):
        _replace_readme_from_log(step.split(":", 1)[1])
        return

    if step == "change_pod_ex":
        from ios_pod_ex.ios_pod_ex import change_pod_ex

        change_pod_ex()
        return

    if step == "z_replace_fix_form":
        from ios_replace_fix_form.z_replce_indi import z_replace_fix_form

        z_replace_fix_form()
        return

    if step == "z_enc_combin":
        from ios_encry_string.z_enc_combin import z_enc_combin

        z_enc_combin()
        return

    if step == "z_replace_file":
        from ios_file_handle.z_file_combin import z_replace_file

        z_replace_file()
        return

    if step == "z_gen_process":
        from ios_file_handle.z_file_combin import z_gen_process

        z_gen_process()
        return

    if step == "z_pbx_combin_all":
        from ios_pbx.z_pbx import z_pbx_combin_all

        z_pbx_combin_all()
        return

    if step == "z_asset_combin":
        from ios_asset_deal.z_asset_combin import z_asset_combin

        z_asset_combin()
        return

    if step == "entry_gener_imageset":
        from ios_asset_deal.gener_imageset import entry_gener_imageset

        entry_gener_imageset()
        return

    if step == "z_replace_file_flutter":
        from ios_file_hanlde_flutter.z_file_combin_flutter import z_replace_file_flutter

        z_replace_file_flutter()
        return

    if step == "z_replace_file_flutter_plugin_swift":
        from ios_file_hanlde_flutter.z_file_combin_flutter import (
            z_replace_file_flutter_plugin_swift,
        )

        z_replace_file_flutter_plugin_swift()
        return

    if step == "z_replace_pkm_strings_in_flutter_plugin":
        from ios_file_hanlde_flutter.z_file_combin_flutter import (
            z_replace_pkm_strings_in_flutter_plugin,
        )

        z_replace_pkm_strings_in_flutter_plugin()
        return

    if step == "z_replace_fix_form_flutter":
        from ios_replace_fix_form_flutter.z_replace_fix_form_flutter import (
            z_replace_fix_form_flutter,
        )

        z_replace_fix_form_flutter()
        return

    if step == "z_enc_combin_flutter":
        from ios_encry_string_flutter.z_enc_combin_flutter import z_enc_combin_flutter

        z_enc_combin_flutter()
        return

    if step == "z_enc_combin_flutter_swift":
        from ios_encry_string_flutter.z_enc_combin_flutter import (
            z_enc_combin_flutter_swift,
        )

        z_enc_combin_flutter_swift()
        return

    if step == "insert_action":
        _run_confuse_ios_entry()
        return

    if step == "execute_pod_install":
        _run_pod_install()
        return

    if step == "execute_clean_py":
        _execute_clean_py()
        return

    raise ValueError(f"未知步骤: {step}")


def list_profiles() -> list[BunessProfile]:
    return [PROFILES[key] for key in sorted(PROFILES)]


def run_profile(profile_name: str) -> None:
    if profile_name not in PROFILES:
        raise KeyError(f"未知 buness profile: {profile_name}")

    profile = PROFILES[profile_name]
    print(f"运行 buness profile: {profile.name}")
    print(f"说明: {profile.description}")

    if profile.overrides:
        print("同步配置覆盖:")
        for key, value in profile.overrides.items():
            print(f"  - {key} = {value!r}")
    sync_root_config(profile.overrides)

    for step in profile.steps:
        print(f"\n>>> 执行步骤: {step}")
        _run_step(step)
