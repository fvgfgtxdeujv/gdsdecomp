# Godot RE Tools

[English](README.md) | 简体中文

## 简介

![代码截图](images/screenshot.png)

本模块包含以下功能：

- 完整项目恢复
- PCK 归档提取器 / 创建器
- GDScript 批量反编译器
- 资源文本 <-> 二进制批量转换器

完整项目恢复会执行以下操作：

- 从 APK、PCK 或内嵌 PCK 的 EXE 文件中加载项目资源
- 反编译所有 GDScript 脚本
- 还原原始项目文件
- 将所有导入资源转换回原始导入格式
- 将所有被自动转换的二进制资源转换回原始文本格式
- 重建插件配置文件

本模块支持反编译 Godot 4.x、3.x 和 2.x 项目。

## 安装

从这里获取最新发布版本：https://github.com/GDRETools/gdsdecomp/releases

在 Windows 上，你也可以通过 [Scoop](https://scoop.sh) 安装：

```
scoop bucket add games
scoop install gdsdecomp
```

## 用法

### 图形界面

- 要在 GUI 中执行完整项目恢复，请从 "RE Tools" 菜单中选择 "Recover project..."：
  ![菜单截图](images/recovery_gui.png)
- 或者，直接把 PCK/EXE 拖放到应用程序窗口上。

### 命令行

#### 用法：

```bash
gdre_tools --headless <主命令> [选项]
```
```
主命令：
--recover=<GAME_PCK/EXE/APK/DIR>              对指定的 PCK、APK、EXE 或已解包的项目目录执行完整项目恢复。
--extract=<GAME_PCK/EXE/APK>                  提取指定的 PCK、APK 或 EXE。
--list-files=<GAME_PCK/EXE/APK>               列出指定 PCK、APK 或 EXE 中的所有文件后退出（可重复）
--compile=<GD_FILE>                           将 GDScript 文件编译为字节码（可重复并可使用通配符，需要 --bytecode）
--decompile=<GDC_FILE>                        将 GDC 文件反编译为文本（可重复并可使用通配符）
--pck-create=<PCK_DIR>                        从指定目录创建 PCK 文件（需要 --pck-version 和 --pck-engine-version）
--pck-patch=<GAME_PCK/EXE>                    用指定文件修补 PCK 文件
--list-bytecode-versions                      列出所有可用的字节码版本
--dump-bytecode-versions=<DIR>                将所有可用的字节码定义以 JSON 格式转储到指定目录
--txt-to-bin=<FILE>                           将文本格式的场景或资源文件转换为二进制格式（可重复）
--bin-to-txt=<FILE>                           将二进制场景或资源文件转换为文本格式（可重复）
--patch-translations=<CSV_FILE>=<SRC_PATH>    用指定的 CSV 文件和源路径修补翻译
                                                （例如 "/path/to/translation.csv=res://translations/translation.csv"）（可重复）
--godot-version                               打印 Godot 引擎版本后退出
--godot-help                                  打印 Godot 引擎的帮助信息后退出
--help, --gdre-help                           打印本帮助信息后退出
--version, --gdre-version                     打印本 GDRE tools 版本后退出

恢复/提取选项：

--key=<KEY>                          项目加密时使用的密钥，为 64 字符的十六进制字符串，
                                         例如：'000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F'
--output=<DIR>                       输出目录，默认为 <NAME_extracted>；若已指定项目目录则默认为项目目录
--scripts-only                       仅提取/恢复脚本
--include=<GLOB>                     包含匹配通配符模式的文件（可重复，见下方说明）
--exclude=<GLOB>                     排除匹配通配符模式的文件（可重复，见下方说明）
--ignore-checksum-errors             提取/恢复时忽略 MD5 校验和错误
--skip-checksum-check                提取/恢复时跳过 MD5 校验和检查
--csharp-assembly=<PATH>             C# 项目的 C# 程序集可选路径；未指定时从 PCK 路径自动检测
--force-bytecode-version=<VERSION>   强制使用指定的字节码版本。可以是提交哈希（如 'f3f05dc'）或版本字符串（如 '4.3.0'）
--load-custom-bytecode=<JSON_FILE>   从指定的 JSON 文件加载自定义字节码定义文件，并在本次恢复会话中使用
--translation-hint=<FILE>            加载翻译键提示文件（.csv、.txt、.po、.mo），并在翻译恢复期间使用
--skip-loading-resource-strings      翻译恢复期间跳过从所有资源加载资源字符串

反编译/编译选项：
--bytecode=<COMMIT_OR_VERSION>          字节码修订版的提交哈希（如 'f3f05dc'），或引擎版本（如 '4.3.0'）
--load-custom-bytecode=<JSON_FILE>      从指定的 JSON 文件加载自定义字节码定义文件，并在本次会话中使用
--output=<DIR>                          编译文件的输出目录。
                                          - 未指定时，编译文件输出到原位置
                                          （例如 '<PROJ_DIR>/main.gd' -> '<PROJ_DIR>/main.gdc'）

创建 PCK 选项：
--output=<OUTPUT_PCK/EXE>                要创建的 PCK 输出文件
--pck-version=<VERSION>                  要创建的 PCK 文件格式版本（0, 1, 2）
--pck-engine-version=<ENGINE_VERSION>    要为其创建 PCK 的引擎版本（x.y.z）
--embed=<EXE_TO_EMBED>                   要将 PCK 内嵌进的可执行文件
--key=<KEY>                              用于加密 PCK 的 64 字符十六进制字符串

修补 PCK 选项：
--output=<OUTPUT_PCK/EXE>                要创建的 PCK 输出文件
--patch-file=<SRC_FILE>=<DEST_FILE>      用于修补 PCK 的文件（例如 "/path/to/file.gd=res://file.gd"）（可重复）
--include=<GLOB>                         仅包含原始 PCK 中匹配通配符模式的文件（可重复）
--exclude=<GLOB>                         排除原始 PCK 中匹配通配符模式的文件（可重复）
--embed=<EXE_TO_EMBED>                   要将修补后 PCK 内嵌进的可执行文件
--key=<KEY>                              用于解密/加密 PCK 的 64 字符十六进制字符串

修补翻译选项：
（注意：可与 --pck-patch 及其选项组合使用）
--pck=<GAME_PCK>                        包含源翻译的 PCK 文件（与 --pck-patch 组合使用时可省略）
--output=<OUTPUT_DIR>                   保存修补后翻译的输出目录（与 --pck-patch 组合使用时可省略）
--locales=<LOCALES>                     要修补的语言区域（逗号分隔，默认仅为新添加的语言区域）
```

#### Include/Exclude 通配符说明：

- 可使用 `**` 指定递归模式
  - 示例：`res://**/*.gdc` 匹配 `res://main.gdc`、`res://scripts/script.gdc` 等。
- 通配符应以 `res://` 或 `user://` 为根
  - 示例：`res://*.gdc` 匹配项目根目录下的所有 .gdc 文件，但不匹配子目录中的文件。
- 未指定根时，通配符将以 `res://` 为根
  - 示例：`addons/plugin/main.gdc` 等价于 `res://addons/plugin/main.gdc`
- 特殊情况：如果通配符包含星号但不包含目录，则假定其为递归模式。
  - 示例：`*.gdc` 等价于 `res://**/*.gdc`
- Include/Exclude 通配符只匹配项目 PCK/目录中实际存在的文件，不匹配不存在的资源源文件。
  - 示例：
    - 项目包含文件 `res://main.gdc`。`res://main.gd` 是 `res://main.gdc` 的源文件，但不在项目 PCK 中。
      - 使用 include 通配符 `res://main.gd` 执行项目恢复不会恢复 `res://main.gd`。
      - 使用 include 通配符 `res://main.gdc` 执行项目恢复则会恢复 `res://main.gd`

编辑项目时，请使用与原始游戏编译时相同的 Godot 工具版本；恢复日志会说明检测到的版本。

## 限制

以下资源的转换尚未实现支持：

- 2.x 模型（`dae`、`fbx`、`glb` 等）
- GDNative 或 GDExtension 脚本

## 从源码编译

将本仓库克隆到 Godot 的 `modules` 子文件夹下并命名为 `gdsdecomp`。
按照 https://docs.godotengine.org/en/latest/development/compiling/index.html 重新编译 Godot 引擎。

你还需要 [rustup](https://rustup.rs) 和 [dotnet 10 sdk](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)。

为了便于开发环境搭建，我们在 `.vscode` 目录中提供了 vscode 的启动、构建和设置模板。阅读上方的 Godot 编译说明并搭建好构建环境后：将这些模板放入 Godot 目录（不是 gdsdecomp）的 `.vscode` 文件夹中，去掉每个文件名的 ".template" 后缀，然后从 Godot 目录启动 vscode。

请确保先构建 editor 版本，并至少启动一次编辑器来编辑 `standalone` 目录中的项目，以便在运行前完成资源导入。

### 注意：

在 SCons 配置阶段，本模块会自动将 `modules/gdsdecomp/patches/` 下的补丁应用到 Godot 核心文件（目前只有 `main/main.cpp`，用于将 `gdre::modify_cli_args` 挂钩到 CLI 解析流程）。该操作是幂等的：补丁应用后重新运行 `scons` 不会重复操作。如果你移除了本模块或想恢复原文件，请手动在受影响文件上执行 `git checkout -- main/main.cpp` 还原。

### 环境要求

[我们的 godot 分支](https://github.com/nikitalita/godot) @ 分支 `gdre-wb-f964fa714f5`

- 已放弃对 3.x 构建的支持，不再推送新功能
  - 但 Godot RE Tools 仍保留反编译 3.x 和 2.x 项目的能力。

### Standalone

假设你使用 `scons platform=linuxbsd target=template_debug` 编译，

```bash
$ bin/godot.linuxbsd.template_debug.x86_64.llvm --headless --path=modules/gdsdecomp/standalone --recover=<pck/apk/exe>
```

## 许可证

本模块的源代码基于 MIT 许可证授权。
