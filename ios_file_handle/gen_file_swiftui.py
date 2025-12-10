# 生成 SwiftUI 文件
# filepath: /Users/jiangshanchen/confuse_string/ios_file_name/gen_file_swiftui.py
import os
import random
import sys
import datetime
import shutil # Added for directory operations
import re # Added for camelCase conversion, though not strictly needed for the final approach

# 将项目根目录添加到sys.path，以便导入其他目录中的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEME_KEYWORDS, NUM_FILES

try:
    from ios_string_generate.string_gen import get_random_class_name, init_word_lists, get_random_method_name
except ImportError:
    print("错误：无法导入 'ios_string_generate.string_gen'。请确保该模块存在且路径正确。")
    print("当前sys.path:", sys.path)
    sys.exit(1)

# 使用相对路径
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ios_resource", "gen_file_swiftui")

# # 本地变量控制
# THEME_KEYWORDS = ["清理项目", "压缩文件", "网络监控", "任务管理"]  # 主题关键字列表
# NUM_FILES = 3  # 要生成的文件数量

# Helper function to convert PascalCase or other names to camelCase for Swift variable names
def to_camel_case(name_str):
    if not name_str:
        return "aProperty" # Fallback for empty input
    # Simple conversion: first letter lower, rest as is.
    # More robust conversion might handle spaces, underscores, etc. if needed.
    name_str = name_str.replace(" ", "").replace("_", "")
    if not name_str: # If it became empty after stripping
        return "anotherProperty"
    return name_str[0].lower() + name_str[1:]

def generate_random_string_value(prefix="", with_quotes=True):
    """生成随机字符串值"""
    random_suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))
    value = f"{prefix}_{random_suffix}" if prefix else random_suffix
    if with_quotes:
        return f"\"{value}\""
    return value

def generate_random_string_array(count=2):
    """生成随机字符串数组"""
    strings = [generate_random_string_value(with_quotes=True) for _ in range(count)]
    return "[" + ", ".join(strings) + "]"

def generate_dynamic_default_value(spec_type, spec_role):
    """根据类型和角色动态生成默认值"""
    if spec_type == "Double":
        return f"{random.uniform(0.1, 0.9):.2f}"
    elif spec_type == "Int":
        return f"{random.randint(0, 100)}"
    elif spec_type == "Bool":
        return random.choice(["true", "false"])
    elif spec_type == "[String]":
        # 生成2-4个随机字符串
        count = random.randint(2, 4)
        return generate_random_string_array(count)
    elif spec_type == "String":
        # 生成随机字符串
        return generate_random_string_value()
    elif "[ActiveConnection]" in spec_type:
        # 生成随机连接详情
        detail = generate_random_string_value()
        return f"[ActiveConnection(details: {detail})]"
    elif "[FileItem]" in spec_type:
        # 生成随机文件项
        name = generate_random_string_value()
        size = random.randint(100, 10000)
        return f"[FileItem(name: {name}, size: {size})]"
    elif "[TaskItem]" in spec_type:
        # 生成随机任务项
        title = generate_random_string_value()
        is_completed = random.choice(["true", "false"])
        return f"[TaskItem(title: {title}, isCompleted: {is_completed})]"
    else:
        # 自定义类型，返回默认初始化
        return f"{spec_type}()"

# Define dynamic variable specifications: role, type, default Swift value, and placeholder for templates
# These cover the needs of the templates in get_view_suggestions
DYNAMIC_VAR_SPECS = [
    # 基础类型
    {"role": "progressValue", "type": "Double", "default_val": "0.65", "placeholder": "{{PROGRESS_VALUE_DOUBLE}}"},
    {"role": "cacheSizeMB", "type": "Double", "default_val": "128.5", "placeholder": "{{CACHE_SIZE_MB_DOUBLE}}"},
    {"role": "selectedFileCount", "type": "Int", "default_val": "0", "placeholder": "{{SELECTED_FILES_COUNT_INT}}"},
    {"role": "isEncryptionEnabled", "type": "Bool", "default_val": "false", "placeholder": "{{IS_ENCRYPTION_ENABLED_BOOL}}"},
    {"role": "isLoading", "type": "Bool", "default_val": "false", "placeholder": "{{IS_LOADING_BOOL}}"},
    
    # 数组类型
    {"role": "logFiles", "type": "[String]", "default_val": "[\"app.log\", \"error.log\"]", "placeholder": "{{LOG_FILES_ARRAY_STRING}}"},
    {"role": "formats", "type": "[String]", "default_val": "[\"ZIP\", \"TAR.GZ\", \"7Z\"]", "placeholder": "{{FORMATS_ARRAY_STRING}}"},
    {"role": "activeConnections", "type": "[ActiveConnection]", "default_val": "[ActiveConnection(details: \"Sample Connection 1\")]", "placeholder": "{{ACTIVE_CONNECTIONS_ARRAY_CUSTOM}}"},
    {"role": "fileList", "type": "[FileItem]", "default_val": "[FileItem(name: \"document.pdf\", size: 1024)]", "placeholder": "{{FILE_LIST_ARRAY_CUSTOM}}"},
    {"role": "taskList", "type": "[TaskItem]", "default_val": "[TaskItem(title: \"Task 1\", isCompleted: false)]", "placeholder": "{{TASK_LIST_ARRAY_CUSTOM}}"},
    
    # 字符串类型
    {"role": "compressionFormat", "type": "String", "default_val": "\"ZIP\"", "placeholder": "{{COMPRESSION_FORMAT_STRING}}"},
    {"role": "endpointUrl", "type": "String", "default_val": "\"https://api.example.com/data\"", "placeholder": "{{ENDPOINT_URL_STRING}}"},
    {"role": "currentFileName", "type": "String", "default_val": "\"document.pdf\"", "placeholder": "{{CURRENT_FILE_NAME_STRING}}"},
    {"role": "statusMessage", "type": "String", "default_val": "\"Processing...\"", "placeholder": "{{STATUS_MESSAGE_STRING}}"},
    {"role": "errorMessage", "type": "String", "default_val": "\"An error occurred\"", "placeholder": "{{ERROR_MESSAGE_STRING}}"},
    
    # 自定义类型
    {"role": "connectionStatus", "type": "ConnectionStatus", "default_val": "ConnectionStatus()", "placeholder": "{{CONNECTION_STATUS_CUSTOM}}"},
    {"role": "fileStatus", "type": "FileStatus", "default_val": "FileStatus()", "placeholder": "{{FILE_STATUS_CUSTOM}}"},
    {"role": "taskStatus", "type": "TaskStatus", "default_val": "TaskStatus()", "placeholder": "{{TASK_STATUS_CUSTOM}}"},
    {"role": "networkStatus", "type": "NetworkStatus", "default_val": "NetworkStatus()", "placeholder": "{{NETWORK_STATUS_CUSTOM}}"},
    {"role": "compressionStatus", "type": "CompressionStatus", "default_val": "CompressionStatus()", "placeholder": "{{COMPRESSION_STATUS_CUSTOM}}"},
]


def generate_random_image_name():
    """生成随机图片名称，优先从文件中读取"""
    # 先尝试从 gener_imageset.txt 文件中读取图片名称
    image_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "ios_log", "gener_imageset.txt")
    try:
        with open(image_file_path, 'r', encoding='utf-8') as f:
            image_names = [line.strip() for line in f if line.strip()]
            if image_names:
                return random.choice(image_names)
    except FileNotFoundError:
        pass  # 文件不存在，继续使用随机生成
    except Exception as e:
        print(f"读取图片名称文件时出错: {e}")
    
    # 如果文件不存在或文件为空，使用随机方法名生成
    random_name = get_random_method_name()
    if not random_name:
        # 如果生成失败，使用随机字符串
        random_suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=12))
        random_name = f"img{random_suffix}"
    return random_name

def get_view_suggestions(theme_keywords):
    """根据主题关键字提供SwiftUI视图元素的建议"""
    suggestions = []
    theme_str_lower = " ".join(theme_keywords).lower()

    # 为每个视图生成随机图片名称
    image_name_1 = generate_random_image_name()
    image_name_2 = generate_random_image_name()
    image_name_3 = generate_random_image_name()
    image_name_4 = generate_random_image_name()
    image_name_5 = generate_random_image_name()
    image_name_6 = generate_random_image_name()
    image_name_7 = generate_random_image_name()
    image_name_8 = generate_random_image_name()
    image_name_9 = generate_random_image_name()
    image_name_10 = generate_random_image_name()

    # 清理主题相关视图
    if "clean" in theme_str_lower or "清理" in theme_str_lower:
        suggestions.extend([
            ("CacheCleanerView", [
                "VStack(spacing: 20) {",
                f"    Image(\"{image_name_1}\")",
                "        .resizable()",
                "        .aspectRatio(contentMode: .fit)",
                "        .frame(height: 200)",
                "    ProgressView(value: {{PROGRESS_VALUE_DOUBLE}}, label: { Text(\"清理进度\") })",
                "    Text(\"缓存大小: \\({{CACHE_SIZE_MB_DOUBLE}}, specifier: \"%.2f\") MB\")",
                "    Button(\"清理缓存\") { /* 清理缓存逻辑 */ }",
                "    if {{IS_LOADING_BOOL}} {",
                "        ProgressView()",
                "    }",
                "}"
            ]),
            ("LogFileManagerView", [
                "VStack(spacing: 15) {",
                f"    Image(\"{image_name_2}\")",
                "        .resizable()",
                "        .frame(width: 60, height: 60)",
                "        .clipShape(Circle())",
                "    List {",
                "        ForEach({{LOG_FILES_ARRAY_STRING}}, id: \\.self) { logFile in",
                "            HStack {",
                "                Text(logFile)",
                "                Spacer()",
                "                Button(\"删除\") { /* 删除日志逻辑 */ }",
                "            }",
                "        }",
                "    }",
                "    Button(\"导出日志\") { /* 导出日志逻辑 */ }",
                "}"
            ])
        ])

    # 压缩主题相关视图
    if "compress" in theme_str_lower or "压缩" in theme_str_lower:
        suggestions.extend([
            ("FileCompressionView", [
                "VStack(spacing: 15) {",
                f"    Image(\"{image_name_3}\")",
                "        .resizable()",
                "        .aspectRatio(contentMode: .fill)",
                "        .frame(height: 150)",
                "        .clipped()",
                "    List {",
                "        ForEach({{FILE_LIST_ARRAY_CUSTOM}}) { file in",
                "            HStack {",
                f"                Image(\"{image_name_4}\")",
                "                    .resizable()",
                "                    .frame(width: 40, height: 40)",
                "                    .cornerRadius(8)",
                "                Text(file.name)",
                "                Spacer()",
                "                Text(\"\\(file.size) bytes\")",
                "            }",
                "        }",
                "    }",
                "    Picker(\"压缩格式\", selection: Binding(get: {{ { {{COMPRESSION_FORMAT_STRING}} } }, set: {{ { newValue in {{COMPRESSION_FORMAT_STRING}} = newValue } }}) {",
                "        ForEach({{FORMATS_ARRAY_STRING}}, id: \\.self) { format in",
                "            Text(format)",
                "        }",
                "    }",
                "    Toggle(\"加密压缩包\", isOn: Binding(get: {{ { {{IS_ENCRYPTION_ENABLED_BOOL}} } }, set: {{ { newValue in {{IS_ENCRYPTION_ENABLED_BOOL}} = newValue } }})",
                "    Button(\"开始压缩\") { /* 压缩逻辑 */ }",
                "}"
            ])
        ])

    # 网络主题相关视图
    if "network" in theme_str_lower or "网络" in theme_str_lower:
        suggestions.extend([
            ("NetworkMonitorView", [
                "VStack(spacing: 20) {",
                f"    Image(\"{image_name_5}\")",
                "        .resizable()",
                "        .aspectRatio(contentMode: .fit)",
                "        .frame(maxWidth: .infinity)",
                "    HStack {",
                "        Image(systemName: {{NETWORK_STATUS_CUSTOM}}.icon)",
                "        Text({{NETWORK_STATUS_CUSTOM}}.message)",
                "    }",
                "    .foregroundColor({{NETWORK_STATUS_CUSTOM}}.color)",
                "    List {",
                "        ForEach({{ACTIVE_CONNECTIONS_ARRAY_CUSTOM}}) { connection in",
                "            HStack {",
                f"                Image(\"{image_name_6}\")",
                "                    .resizable()",
                "                    .frame(width: 30, height: 30)",
                "                    .clipShape(Circle())",
                "                Text(connection.details)",
                "            }",
                "        }",
                "    }",
                "    if {{IS_LOADING_BOOL}} {",
                "        ProgressView()",
                "    }",
                "}"
            ])
        ])

    # 任务管理主题相关视图
    if "task" in theme_str_lower or "任务" in theme_str_lower:
        suggestions.extend([
            ("TaskManagerView", [
                "VStack(spacing: 15) {",
                f"    Image(\"{image_name_7}\")",
                "        .resizable()",
                "        .frame(width: 100, height: 100)",
                "    List {",
                "        ForEach({{TASK_LIST_ARRAY_CUSTOM}}) { task in",
                "            HStack {",
                f"                Image(\"{image_name_8}\")",
                "                    .resizable()",
                "                    .frame(width: 50, height: 50)",
                "                    .cornerRadius(10)",
                "                Toggle(task.title, isOn: Binding(get: {{ { task.isCompleted } }, set: {{ { newValue in task.isCompleted = newValue } }})",
                "                Spacer()",
                "                Text({{TASK_STATUS_CUSTOM}}.status)",
                "                    .foregroundColor({{TASK_STATUS_CUSTOM}}.color)",
                "            }",
                "        }",
                "    }",
                "    Button(\"添加任务\") { /* 添加任务逻辑 */ }",
                "}"
            ])
        ])

    # 如果没有匹配的主题，使用通用视图
    if not suggestions:
        suggestions.extend([
            ("GenericDetailView", [
                "VStack(spacing: 20) {",
                f"    Image(\"{image_name_9}\")",
                "        .resizable()",
                "        .aspectRatio(contentMode: .fit)",
                "        .frame(maxWidth: .infinity)",
                "    Text({{STATUS_MESSAGE_STRING}})",
                "    if {{IS_LOADING_BOOL}} {",
                "        ProgressView()",
                "    }",
                "    if !{{ERROR_MESSAGE_STRING}}.isEmpty {",
                "        Text({{ERROR_MESSAGE_STRING}})",
                "            .foregroundColor(.red)",
                "    }",
                f"    Image(\"{image_name_10}\")",
                "        .resizable()",
                "        .frame(height: 100)",
                "        .opacity(0.5)",
                "}"
            ])
        ])

    return suggestions

def generate_swiftui_view_content(view_name, theme_keywords):
    """生成SwiftUI视图文件的内容"""
    # 随机选择3-5个不同的属性
    selected_specs = random.sample(DYNAMIC_VAR_SPECS, random.randint(3, 5))
    
    # 确保包含必要的属性
    required_specs = []
    required_roles = ["logFiles", "fileList", "taskList", "formats", "activeConnections"]
    for spec in DYNAMIC_VAR_SPECS:
        if spec["role"] in required_roles:
            required_specs.append(spec)
    
    # 合并必需属性和随机属性，使用角色名来去重
    all_specs = []
    used_roles = set()
    
    # 首先添加必需属性
    for spec in required_specs:
        if spec["role"] not in used_roles:
            all_specs.append(spec)
            used_roles.add(spec["role"])
    
    # 然后添加随机属性
    for spec in selected_specs:
        if spec["role"] not in used_roles:
            all_specs.append(spec)
            used_roles.add(spec["role"])
    
    state_var_declarations = []
    placeholder_to_swift_name_map = {}
    used_swift_names = set()

    for spec in all_specs:
        # 使用随机方法名作为变量名，而不是固定的 role
        swift_var_name = get_random_method_name()
        if not swift_var_name:
            # 如果生成失败，使用 role 作为后备
            swift_var_name = to_camel_case(spec["role"])
        
        # 确保唯一性
        original_swift_var_name = swift_var_name
        counter = 1
        while swift_var_name in used_swift_names:
            swift_var_name = f"{original_swift_var_name}{counter}"
            counter += 1
        used_swift_names.add(swift_var_name)

        # 动态生成默认值（字符串值随机生成）
        dynamic_default_val = generate_dynamic_default_value(spec['type'], spec['role'])
        
        placeholder_to_swift_name_map[spec["placeholder"]] = swift_var_name
        state_var_declarations.append(
            f"    @State private var {swift_var_name}: {spec['type']} = {dynamic_default_val}"
        )

    state_vars_string = "\n".join(state_var_declarations)
    suggestions = get_view_suggestions(theme_keywords)
    
    if not suggestions:
        suggestions = [("GenericView", ["Text(\"No specific view for this theme\")"])]
    
    suggestion_tuple = random.choice(suggestions)
    chosen_suggestion_elements_templates = suggestion_tuple[1]

    # 处理模板中的占位符
    processed_body_elements = []
    for elem_template in chosen_suggestion_elements_templates:
        elem_processed = elem_template
        
        # 首先处理所有可能的占位符
        for placeholder, swift_name in placeholder_to_swift_name_map.items():
            # 处理 Binding 的情况
            if "Binding(get: {{ { " in elem_processed and placeholder in elem_processed:
                elem_processed = elem_processed.replace(
                    f"Binding(get: {{ {{ {placeholder} }} }}, set: {{ {{ newValue in {placeholder} = newValue }} }})",
                    f"${swift_name}"
                )
            else:
                # 处理普通占位符
                elem_processed = elem_processed.replace(placeholder, swift_name)
        
        # 处理任务列表中的绑定
        if "task.isCompleted" in elem_processed:
            elem_processed = elem_processed.replace(
                "Binding(get: {{ { task.isCompleted } }, set: {{ { newValue in task.isCompleted = newValue } }})",
                "$task.isCompleted"
            )
        
        # 确保所有占位符都被替换
        for placeholder in ["{{FILE_LIST_ARRAY_CUSTOM}}", "{{TASK_LIST_ARRAY_CUSTOM}}", 
                          "{{LOG_FILES_ARRAY_STRING}}", "{{FORMATS_ARRAY_STRING}}",
                          "{{ACTIVE_CONNECTIONS_ARRAY_CUSTOM}}", "{{PROGRESS_VALUE_DOUBLE}}",
                          "{{CACHE_SIZE_MB_DOUBLE}}", "{{IS_LOADING_BOOL}}", "{{COMPRESSION_FORMAT_STRING}}",
                          "{{IS_ENCRYPTION_ENABLED_BOOL}}", "{{NETWORK_STATUS_CUSTOM}}", "{{TASK_STATUS_CUSTOM}}",
                          "{{STATUS_MESSAGE_STRING}}", "{{ERROR_MESSAGE_STRING}}"]:
            if placeholder in elem_processed:
                # 如果这个占位符没有被映射，生成一个随机的变量名
                if placeholder not in placeholder_to_swift_name_map:
                    # 使用随机方法名作为变量名
                    default_name = get_random_method_name()
                    if not default_name:
                        default_name = to_camel_case(placeholder.strip("{{}}").lower())
                    
                    # 确保唯一性
                    original_default_name = default_name
                    counter = 1
                    while default_name in used_swift_names:
                        default_name = f"{original_default_name}{counter}"
                        counter += 1
                    
                    used_swift_names.add(default_name)
                    placeholder_type = get_type_for_placeholder(placeholder)
                    dynamic_default_val = generate_dynamic_default_value(placeholder_type, placeholder)
                    state_var_declarations.append(
                        f"    @State private var {default_name}: {placeholder_type} = {dynamic_default_val}"
                    )
                    placeholder_to_swift_name_map[placeholder] = default_name
                
                # 使用映射的变量名替换占位符
                elem_processed = elem_processed.replace(placeholder, placeholder_to_swift_name_map[placeholder])
        
        processed_body_elements.append(elem_processed)

    # 更新 state_vars_string，包含所有变量声明
    state_vars_string = "\n".join(state_var_declarations)
    
    body_content = "\n                ".join(processed_body_elements)
    current_date = datetime.date.today().strftime('%Y-%m-%d')

    # 根据使用的属性类型生成所需的数据结构
    used_types = set()
    for spec in all_specs:
        if "[" in spec["type"] and "]" in spec["type"]:
            used_types.add(spec["type"].strip("[]"))
        elif spec["type"] not in ["String", "Int", "Double", "Bool"]:
            used_types.add(spec["type"])

    # 生成所需的数据结构
    supporting_structs = []
    
    # 添加所有可能需要的类型定义
    type_definitions = {
        "ActiveConnection": """
    // MARK: - Supporting Types
    private struct ActiveConnection: Identifiable {
        let id = UUID()
        var details: String
    }""",
        "FileItem": """
    private struct FileItem: Identifiable {
        let id = UUID()
        var name: String
        var size: Int
    }""",
        "TaskItem": """
    private struct TaskItem: Identifiable {
        let id = UUID()
        var title: String
        var isCompleted: Bool
    }""",
        "ConnectionStatus": """
    private struct ConnectionStatus {
        var icon: String = "wifi.slash"
        var message: String = "Unknown"
        var color: Color = .gray
    }""",
        "FileStatus": """
    private struct FileStatus {
        var status: String = "Ready"
        var color: Color = .blue
    }""",
        "TaskStatus": """
    private struct TaskStatus {
        var status: String = "Pending"
        var color: Color = .orange
    }""",
        "NetworkStatus": """
    private struct NetworkStatus {
        var icon: String = "wifi.slash"
        var message: String = "Disconnected"
        var color: Color = .red
    }""",
        "CompressionStatus": """
    private struct CompressionStatus {
        var status: String = "Idle"
        var progress: Double = 0.0
        var color: Color = .blue
    }"""
    }

    # 检查模板中使用的所有类型
    template_content = "\n".join(chosen_suggestion_elements_templates)
    for type_name, definition in type_definitions.items():
        if type_name in template_content or type_name in used_types:
            supporting_structs.append(definition)

    supporting_structs_string = "\n".join(supporting_structs)

    content = f"""
import SwiftUI

// Theme: {', '.join(theme_keywords)}
// Generated on: {current_date}

public struct {view_name}: View {{
{state_vars_string}

    public init() {{
        // Default initializer
    }}

    public var body: some View {{
        ScrollView {{
            VStack(alignment: .leading, spacing: 15) {{
                {body_content}
                
                Spacer()
                Text("Generated for theme: {', '.join(theme_keywords)}")
                    .font(.caption)
                    .foregroundColor(.gray)
            }}
            .padding()
        }}
        .navigationTitle("{view_name.replace("View", "")}")
    }}
{supporting_structs_string}
}}

// Preview provider
public struct {view_name}_Previews: PreviewProvider {{
    public static var previews: some View {{
        NavigationView {{
            {view_name}()
        }}
    }}
}}
"""
    return content

def get_type_for_placeholder(placeholder):
    """根据占位符返回对应的类型"""
    type_map = {
        "{{FILE_LIST_ARRAY_CUSTOM}}": "[FileItem]",
        "{{TASK_LIST_ARRAY_CUSTOM}}": "[TaskItem]",
        "{{LOG_FILES_ARRAY_STRING}}": "[String]",
        "{{FORMATS_ARRAY_STRING}}": "[String]",
        "{{ACTIVE_CONNECTIONS_ARRAY_CUSTOM}}": "[ActiveConnection]",
        "{{PROGRESS_VALUE_DOUBLE}}": "Double",
        "{{CACHE_SIZE_MB_DOUBLE}}": "Double",
        "{{IS_LOADING_BOOL}}": "Bool",
        "{{COMPRESSION_FORMAT_STRING}}": "String",
        "{{IS_ENCRYPTION_ENABLED_BOOL}}": "Bool",
        "{{NETWORK_STATUS_CUSTOM}}": "NetworkStatus",
        "{{TASK_STATUS_CUSTOM}}": "TaskStatus",
        "{{STATUS_MESSAGE_STRING}}": "String",
        "{{ERROR_MESSAGE_STRING}}": "String"
    }
    return type_map.get(placeholder, "String")

def get_default_value_for_placeholder(placeholder):
    """根据占位符返回对应的默认值（动态生成随机值）"""
    type_map = {
        "{{FILE_LIST_ARRAY_CUSTOM}}": "[FileItem]",
        "{{TASK_LIST_ARRAY_CUSTOM}}": "[TaskItem]",
        "{{LOG_FILES_ARRAY_STRING}}": "[String]",
        "{{FORMATS_ARRAY_STRING}}": "[String]",
        "{{ACTIVE_CONNECTIONS_ARRAY_CUSTOM}}": "[ActiveConnection]",
        "{{PROGRESS_VALUE_DOUBLE}}": "Double",
        "{{CACHE_SIZE_MB_DOUBLE}}": "Double",
        "{{IS_LOADING_BOOL}}": "Bool",
        "{{COMPRESSION_FORMAT_STRING}}": "String",
        "{{IS_ENCRYPTION_ENABLED_BOOL}}": "Bool",
        "{{NETWORK_STATUS_CUSTOM}}": "NetworkStatus",
        "{{TASK_STATUS_CUSTOM}}": "TaskStatus",
        "{{STATUS_MESSAGE_STRING}}": "String",
        "{{ERROR_MESSAGE_STRING}}": "String"
    }
    
    spec_type = type_map.get(placeholder, "String")
    return generate_dynamic_default_value(spec_type, placeholder)

def generate_swiftui_files(theme_keywords, num_files):
    """根据主题生成指定数量的SwiftUI文件, 覆盖旧文件。"""
    try:
        init_word_lists() 
    except Exception as e:
        print(f"错误：初始化词汇列表失败: {e}")
        return

    # Clear and recreate the output directory
    if os.path.exists(OUTPUT_DIR):
        try:
            shutil.rmtree(OUTPUT_DIR)
            print(f"已清除旧的输出目录: {OUTPUT_DIR}")
        except OSError as e:
            print(f"错误: 清除目录 {OUTPUT_DIR} 失败: {e}")
            return
            
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"SwiftUI文件将生成在: {OUTPUT_DIR}")
    except OSError as e:
        print(f"错误: 创建目录 {OUTPUT_DIR} 失败: {e}")
        return

    generated_files_count = 0
    generated_names = set() 

    for i in range(num_files):
        view_name = None
        attempts = 0
        max_attempts = 20 

        while attempts < max_attempts:
            base_name = get_random_class_name()
            if not base_name:
                base_name = f"FallbackGen{i}{random.randint(1000,9999)}"
            
            potential_view_name = base_name if base_name.endswith("View") else base_name + "View"
            
            if potential_view_name not in generated_names:
                view_name = potential_view_name
                break
            attempts += 1
        
        if not view_name:
            print(f"警告: 无法为文件 {i+1} 生成唯一视图名称 (尝试次数: {max_attempts})。跳过此文件。")
            continue

        generated_names.add(view_name)
        file_path = os.path.join(OUTPUT_DIR, f"{view_name}.swift")

        if os.path.exists(file_path):
            print(f"警告: 文件 {file_path} 已存在 (可能来自之前的运行)。跳过此文件。")
            continue
            
        content = generate_swiftui_view_content(view_name, theme_keywords)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已生成SwiftUI文件: {file_path}")
            generated_files_count += 1
        except IOError as e:
            print(f"错误: 写入文件 {file_path} 失败: {e}")
        except Exception as e:
            print(f"未知错误在处理文件 {file_path}: {e}")


    print(f"\n成功生成 {generated_files_count} / {num_files} 个请求的SwiftUI文件。")

def gen_file_swiftui():
    print("SwiftUI 文件生成器")
    print("--------------------")
    print(f"使用主题关键字: {', '.join(THEME_KEYWORDS)}")
    print(f"生成文件数量: {NUM_FILES}")
    
    if not THEME_KEYWORDS:
        print("未提供主题关键字。正在退出。")
    else:
        generate_swiftui_files(THEME_KEYWORDS, NUM_FILES)
    

if __name__ == "__main__":
    gen_file_swiftui()
