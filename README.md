# 🦖 大将怪兽摧毁 - Desktop Monster Deleter

这是一个充满趣味的 Windows 桌面交互应用！当你想删除电脑上的文件时，不再是单调的系统提示，而是可以召唤出一只强悍的“大将怪兽”，让他迈着嚣张的步伐走到文件跟前，一脚将文件连同垃圾桶一起踢爆粉碎！

## ✨ 核心亮点

- 🎯 **狙击级精准锁定**：高级半透明磨砂 UI 与红色十字狙击光标，给你沉浸式的瞄准体验。
- 🦖 **生动的怪兽动效**：包括出场、行走、指点、踢爆、飞离等全套精心设计的逐帧动画（支持完美绿幕抠图）。
- 💥 **硬核视听震撼**：全程伴随专属 BGM、怪兽语音以及爆破音效，删除文件也能成为一种享受。
- 🖱️ **智能右键菜单集成**：程序只需运行一次，即可自动在 Windows 右键菜单中注册“召唤大将怪兽摧毁”选项。
- 🚀 **指哪打哪**：在任意文件夹或桌面右击文件并召唤怪兽，它都能精确获取鼠标的绝对物理坐标，实现精准打击。

## 📦 如何使用（无需安装环境）

如果你拿到了打包好的 `MonsterDeleter.exe`，只需要两步：

1. **注册右键菜单**：双击运行一次 `MonsterDeleter.exe`，程序会注册“召唤大将怪兽摧毁”并显示成功提示。
2. **享受摧毁**：在桌面上或任意文件夹中，右键点击你想删除的文件，选择 **“召唤大将怪兽摧毁”**。屏幕变暗后，使用红色准星选择爆炸出现的位置，再核对文件名并确认。任何时候都可以按 `Esc` 取消。

> ⚠️ **注意**：程序实际使用了 `send2trash`（安全移至回收站）而不是彻底粉碎，所以如果你后悔了，还可以从回收站把文件捞回来。

## 🛠️ 开发者指南 (Developer Guide)

如果你想通过源码运行或自己修改代码，请确保你的系统上安装了 Python 3。

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果需要运行测试、打包程序或使用 `scripts/` 中的图片处理工具，请安装开发依赖：

```bash
pip install -r requirements-dev.txt
```

### 2. 本地运行测试

```bash
# 开启手动狙击模式
python main.py

# 指定删除某个特定文件 (替换成你的文件路径)
python main.py "C:\path\to\your\file.txt"
```

运行自动测试：

```bash
python -m pytest -q
```

`tests/` 中的 Windows UI 自动化脚本也可以单独运行；相关可选依赖缺失时，pytest 会跳过这些诊断脚本。

图片处理脚本默认读取仓库的 `assets/`，也可以传入其他目录：

```bash
python scripts/batch_bg_remove.py "D:\path\to\sprites"
python scripts/batch_rembg.py "D:\path\to\sprites"
python scripts/batch_rembg_slice.py "D:\path\to\sprites"
python scripts/process_image.py "D:\path\to\input.png" "D:\path\to\output.png"
```

### 3. 一键打包发布 (PyInstaller)

使用以下命令可将 Python 源码与所有的图片 (`assets/`)、音频等依赖一键打包成单文件的 `.exe` 程序：

```bash
pyinstaller --noconfirm --onefile --windowed --name MonsterDeleter --add-data "assets;assets" --hidden-import send2trash main.py
```
> **提示**: 生成的独立程序会在 `dist/MonsterDeleter.exe`。程序会在运行时自动将 `assets` 目录解压到临时路径 (`sys._MEIPASS`) 并完美加载。

## 📂 项目结构
```
MonsterDeleter/
│
├── main.py                  # 核心主程序逻辑 (UI渲染、动画播放、注册表写入)
├── register_menu.py         # (遗留/参考) 原版菜单注册脚本
├── requirements.txt         # 运行所需依赖
├── assets/                  # 资源目录 (打包时嵌入 exe)
│   ├── 音频/                # bgm, 音效等
│   └── *_transparent.png    # 优化后的高压缩比透明背景序列帧
├── scripts/                 # 工具脚本目录 (绿幕抠图、切片等)
└── tests/                   # 开发过程中的测试用例
```

## 📜 许可
本项目仅供娱乐与学习使用。
