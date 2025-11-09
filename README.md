# 剪贴板自动收集工具

一个使用 Rust + Tauri + React + Ant Design 构建的现代化剪贴板历史管理工具。

## 功能特性

- 🎯 **自动监听剪贴板** - 实时捕获剪贴板内容变化
- 📝 **历史记录管理** - 保存所有剪贴板历史记录
- 🔍 **快速搜索** - 支持关键词搜索历史记录
- 📋 **一键复制** - 快速复制历史记录到剪贴板
- 💾 **导出功能** - 将历史记录导出为文本文件
- 🎨 **现代化UI** - 使用 Ant Design 组件库
- 🔔 **系统托盘** - 最小化到系统托盘，随时访问
- ⚡ **高性能** - Rust 后端保证高效运行
- 🖥️ **跨平台** - 支持 Windows、macOS、Linux

## 技术栈

### 后端
- **Rust** - 高性能系统编程语言
- **Tauri** - 轻量级桌面应用框架
- **clipboard-win** - Windows 剪贴板监听

### 前端
- **React 18** - 现代化前端框架
- **TypeScript** - 类型安全
- **Ant Design 5** - 企业级 UI 组件库
- **Vite** - 快速构建工具

## 安装依赖

### 前置要求

1. **Node.js** (v16 或更高版本)
2. **Rust** (最新稳定版)
   - 访问 https://rustup.rs/ 安装 Rust
3. **系统依赖** (Windows)
   - Visual Studio Build Tools 或 Visual Studio 2019+

### 安装步骤

1. 克隆或下载项目到本地

2. 安装前端依赖：
```bash
npm install
```

3. 安装 Tauri CLI（如果还没安装）：
```bash
npm install -g @tauri-apps/cli
```

## 开发

启动开发服务器：

```bash
npm run tauri:dev
```

这将同时启动 Vite 开发服务器和 Tauri 应用。

## 构建

构建生产版本：

```bash
npm run tauri:build
```

构建产物将在 `src-tauri/target/release/bundle/` 目录下。

## 使用说明

### 基本操作

1. **启动应用** - 双击运行程序
2. **监听剪贴板** - 默认自动开启监听，可通过右上角开关控制
3. **查看历史** - 左侧列表显示所有历史记录
4. **搜索记录** - 使用搜索框快速查找
5. **复制内容** - 点击记录后点击"复制"按钮
6. **清空历史** - 点击"清空"按钮清除所有记录
7. **导出记录** - 点击"导出"按钮保存为文本文件

### 系统托盘

- **左键单击** - 显示/隐藏主窗口
- **右键菜单**：
  - 显示主窗口
  - 开启/关闭监听
  - 退出程序

### 快捷键

- 点击列表项查看详细内容
- 双击托盘图标显示主窗口

## 项目结构

```
clipboard-data/
├── src/                    # React 前端源码
│   ├── App.tsx            # 主应用组件
│   ├── main.tsx           # 入口文件
│   └── styles.css         # 全局样式
├── src-tauri/             # Tauri 后端
│   ├── src/
│   │   └── main.rs        # Rust 主程序
│   ├── Cargo.toml         # Rust 依赖配置
│   ├── tauri.conf.json    # Tauri 配置
│   └── build.rs           # 构建脚本
├── index.html             # HTML 入口
├── package.json           # Node.js 依赖
├── tsconfig.json          # TypeScript 配置
├── vite.config.ts         # Vite 配置
└── README.md              # 项目说明

```

## 配置说明

### 存储位置

历史记录保存在应用运行目录下的 `clipboard_history.json` 文件中。

### 监听频率

默认每 500ms 检查一次剪贴板变化，可在 `src/App.tsx` 中修改。

## 常见问题

### Q: 为什么监听不工作？
A: 确保监听开关已开启，并且应用有足够的系统权限。

### Q: 如何修改窗口大小？
A: 在 `src-tauri/tauri.conf.json` 中修改 `windows` 配置。

### Q: 历史记录保存在哪里？
A: 默认保存在应用运行目录的 `clipboard_history.json` 文件中。

### Q: 如何自定义 UI 样式？
A: 修改 `src/App.tsx` 中的 Ant Design 组件样式，或在 `src/styles.css` 中添加全局样式。

## 从 Python 版本迁移

原 Python 版本使用 PySide6 构建，新版本使用 Rust + Tauri 重构，具有以下优势：

- ✅ 更小的安装包体积（约 10MB vs 100MB+）
- ✅ 更快的启动速度
- ✅ 更低的内存占用
- ✅ 更现代的 UI 界面
- ✅ 更好的跨平台支持

历史数据兼容：新版本可以直接读取旧版本的 `clipboard_history.json` 文件。

## 开发计划

- [ ] 添加快捷键支持
- [ ] 支持图片剪贴板
- [ ] 云同步功能
- [ ] 分类标签功能
- [ ] 收藏功能
- [ ] 主题切换

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请提交 Issue。
