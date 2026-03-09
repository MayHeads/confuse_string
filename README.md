# iOS String Obfuscation Tool

一个用于 iOS 项目字符串混淆的工具，支持 Swift 和 Objective-C 代码。

## 功能特点

- 自动扫描项目中的字符串
- 使用 AES 加密算法进行字符串混淆
- 支持 Swift 和 Objective-C 代码
- 自动生成解密方法
- 支持自定义忽略规则
- 生成混淆映射日志

## 使用方法

1. 确保已安装 Python 3.x 和必要的依赖：
```bash
python3 -m pip install -r requirements.txt
```

如果你需要运行 `confuse_ios` 里的 Swift / OC 插入和解析逻辑，还需要额外准备系统工具：

- Xcode Command Line Tools
- `sourcekitten`
- `libclang`（`clang` Python 包只提供绑定，底层动态库需要系统安装）

另外，`nltk` 相关脚本会使用 `wordnet` 语料；首次使用时如果缺失，需要执行：

```bash
python3 -m nltk.downloader wordnet omw-1.4
```

2. 运行字符串收集：
```bash
python3 ios_encry_string/collect_str.py
```

3. 运行混淆工具：
```bash
python3 ios_encry_string/source_con_str.py
```

## 配置说明

在 `config.py` 中可以配置：
- 需要忽略的文件夹
- 需要忽略的 Swift 文件
- 需要忽略的固定文本
- 需要忽略的格式化字符串

## 输出文件

- `ios_resource/ios_collection_str.txt`: 收集到的字符串列表
- `ios_log/native_con_str.txt`: 字符串混淆映射关系
- 项目目录下会生成解密器文件（如：`String+xxDecryptor.swift`）

## 注意事项

1. 使用前请备份项目
2. 确保项目路径配置正确
3. 建议在开发环境测试后再应用到生产环境 
