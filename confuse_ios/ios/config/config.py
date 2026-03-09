"""兼容配置桥接。

confuse_ios 历史上读取的是这个文件，现在统一转发到仓库根目录 config.py。
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_root_config():
    root_config_path = Path(__file__).resolve().parents[3] / "config.py"
    spec = importlib.util.spec_from_file_location("_confuse_root_config", root_config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载根配置文件: {root_config_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ROOT = _load_root_config()

ROOT_PROJECT_DIR = _ROOT.project_path
PROJECT_SCHEME = _ROOT.PROJECT_SCHEME
ADD_DIRECTORY_PREFIX = _ROOT.ADD_DIRECTORY_PREFIX
ADD_FILE_PREFIX = _ROOT.ADD_FILE_PREFIX
ORIGIN_SYMBOL_PREFIX = _ROOT.ORIGIN_SYMBOL_PREFIX
CONFUSE_LEVEL = _ROOT.CONFUSE_LEVEL
IGNORE_CODE_DIRECTORY = _ROOT.IGNORE_CODE_DIRECTORY
IGNORE_ASSERT_DEFAULT_DIRECTORY = _ROOT.IGNORE_ASSERT_DEFAULT_DIRECTORY
CONFUSE_STR_FILES = _ROOT.CONFUSE_STR_FILES
