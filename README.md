# OpenShelf — Windows 本地 AI 编程助手

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-orange.svg)]()

纯 Python 实现的 Windows 桌面端 AI 编程助手。100% 本地优先，零云端依赖，完全开源。

> 基于 Claude Code 内部 MAP 架构逆向工程，彻底去 Anthropic 化。

## 功能

| 模块 | 说明 |
|------|------|
| 🤖 多模型后端 | DeepSeek / OpenAI / Ollama / Groq 一键切换 |
| 💾 本地优先 | 代码、对话、密钥永不上传，零遥测 |
| ⚡ 前缀缓存 | DeepSeek 固定前缀策略，KV 缓存命中率 ~100% |
| 🔗 MCP 协议 | 纯 Python 自实现，stdio + HTTP 传输 |
| 🖱️ 桌面操控 | pyautogui 驱动，沙箱化执行 + 录制回放 |
| 🧠 本地 RAG | chromadb + sentence-transformers 向量检索 |
| 📐 CAD 集成 | Python 代码 → STEP/STL/GLB 3D 模型 |
| 🛠️ 技能系统 | .md/.yaml 技能文件，支持链式调用 |
| ✏️ 代码编辑 | 流式对话 + Diff 预览 + 一键撤销 |
| 🖥️ 终端 | 多标签页 + 命令补全 + 错误自动修复 |

## 架构

```
openshelf/
├── main.py              # 入口文件
├── requirements.txt     # 依赖清单
├── src/
│   ├── core/            # 核心引擎：AgentLoop、QueryEngine、SQLite
│   ├── api/             # 模型抽象层：DeepSeek、OpenAI 兼容接口
│   ├── tools/           # 13 个内置工具：bash/powershell/file/grep/web
│   ├── mcp/             # MCP 客户端：stdio/HTTP 传输，服务器管理
│   ├── skills/          # 技能加载、注册、链式调用
│   ├── computer_use/    # 桌面操控：截图、点击、键盘、录制回放
│   ├── rag/             # 向量检索：chromadb 索引、watchdog 自动重索引
│   ├── terminal/        # 终端模拟：pty 驱动、错误分析、命令补全
│   ├── permissions/     # 权限系统：ASK/ALLOW/DENY 规则引擎
│   ├── plugins/         # 插件系统：热加载 Python 模块
│   ├── ui/              # PyQt6 界面：主窗口、设置、主题
│   └── utils/           # 工具函数：加密、Markdown、文件操作
└── resources/           # 主题 QSS、技能 Markdown、图标
```

## 快速开始

### 环境要求
- Windows 10/11
- Python 3.11+
- [FFmpeg](https://ffmpeg.org/)（视频渲染必需）

### 安装

```powershell
git clone https://github.com/xxwkf752tf-sudo/OpenShelf.git
cd OpenShelf
pip install -r requirements.txt
python main.py
```

### 配置 API Key

启动后点击 **工具 → API 配置**，填入 [DeepSeek API Key](https://platform.deepseek.com/)（推荐），或 OpenAI / Ollama 接口。

## 关键设计决策

- **QThread 隔离异步引擎**：asyncio 事件循环运行在独立线程，避免阻塞 PyQt6 主线程
- **固定前缀缓存**：系统提示词 + 技能指令固定为 `messages[0]`，确保 DeepSeek KV 缓存 100% 命中
- **线程安全 UI**：`queue.Queue` + `QTimer` 轮询机制，异步线程通过消息队列更新界面
- **本地加密存储**：API Key 优先使用 Windows Credential Manager，回退 AES-256-GCM 文件加密

## 已验证能力

| 能力 | 状态 | 说明 |
|------|------|------|
| Python → STEP 3D 模型 | ✅ | gen_box.py 生成 box.step (16KB), gear_50mm_20teeth.step (29MB) |
| STEP → STL 导出 | ✅ | `step --stl` 一键转换 |
| 桌面截图操控 | ✅ | pyautogui 沙箱化执行 |
| 对话持久化 | ✅ | SQLite 自动保存/加载 |
| 技能链式调用 | ✅ | Markdown 技能文件 + chain_to |
| MCP 服务器管理 | ✅ | stdio/HTTP 协议客户端 |

## 开发

```powershell
# 安装开发依赖
pip install black ruff

# 代码格式化
black src/
ruff check src/

# 打包为 .exe
pyinstaller openshelf.spec
```

## 许可

MIT License

## 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — GUI 框架
- [DeepSeek](https://www.deepseek.com/) — 推荐模型后端
- [Claude Code](https://claude.ai/) — 架构参考
