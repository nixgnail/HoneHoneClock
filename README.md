# 人体时钟 (HoneHone Clock)

一款基于PyQt6开发的创意桌面时钟应用，通过拟人化的人体造型和流畅的动画效果，将抽象的时间概念转化为直观生动的视觉体验。

## 功能特性

- 🤟🏻 **透明窗口设计**：完美融入桌面环境
- 💗 **拟人化时间显示**：采用生动的人体造型表示数字
- 🎨 **主题切换**：支持默认、黑色、白色、红色、蓝色五种主题
- 🖱️ **鼠标缩放**：通过滚轮调整窗口大小
- 📌 **始终置顶**：可选择将窗口固定在所有窗口之上
- 🖥️ **分屏适配**：支持多显示器环境
- 🌙 **深色主题兼容**：完美适配Windows深色主题

## 安装和配置

### 环境要求

- Python 3.6+ 
- Windows 10/11

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python honehone_clock.py
```

## 使用说明

### 基本操作

- **查看时间**：应用会自动显示当前时间，数字以人体造型动画呈现
- **拖动窗口**：使用鼠标左键拖动窗口到任意位置
- **缩放窗口**：使用鼠标滚轮缩放窗口大小（10%-200%）

### 右键菜单功能

- **主题切换**：选择不同的界面主题
- **始终置顶**：切换窗口是否始终显示在最上层
- **关于**：查看应用版本和开发者信息
- **退出**：关闭应用程序

## 项目结构

```
├── honehone_clock.py      # 主应用程序文件
├── config.json            # 配置文件，包含动画帧数据
├── requirements.txt       # 依赖包列表
├── README.md             # 项目说明文档
├── version_info.txt      # Windows文件版本信息
├── attest/               # 应用资源目录
│   └── logo.ico         # 应用图标
├── split_characters/    # 字符分割图片
└── theme/               # 主题图片
    ├── default.png
    ├── black.png
    ├── white.png
    ├── red.png
    └── blue.png
```

## 开发说明

### 自定义打包

如需自定义打包应用程序，可以使用PyInstaller：

1. 生成spec文件：
```bash
pyinstaller --onefile --windowed --icon=attest/logo.ico --add-data "config.json;." --add-data "theme;theme" --add-data "attest;attest" honehone_clock.py
```

2. 编辑spec文件（可选）

3. 打包应用：
```bash
pyinstaller honehone_clock.spec
```

### 资源文件说明

- **sprite sheet**：主题图片（theme/*.png）包含所有数字的动画帧
- **config.json**：定义了每个数字动画帧的位置和大小信息
- **logo.ico**：应用程序图标，用于EXE文件和窗口标题栏

## 许可证

© 2025 AI & Liangxin. 保留所有权利。

## 联系方式

- 电话/微信：13700228563
