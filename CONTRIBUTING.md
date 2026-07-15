# Contributing to OpenShelf

感谢你为 OpenShelf 社区贡献力量！

## 开始之前

- 检查 [open issues](https://github.com/xxwkf752tf-sudo/OpenShelf/issues) 避免重复工作
- 检查 [open PRs](https://github.com/xxwkf752tf-sudo/OpenShelf/pulls) 确认没有冲突中的改动
- 阅读 [DeepSeek API 文档](https://api-docs.deepseek.com/) —— 模型配置必须基于最新 API

## 项目结构

```
src/
├── core/       # 核心引擎 (AgentLoop, QueryEngine, ContextManager, SQLite)
├── api/        # 模型抽象层 (DeepSeek, OpenAI compat)
├── tools/      # 内置工具 (bash, file_read/write/edit, grep, web_fetch)
├── mcp/        # MCP 协议客户端 (stdio/HTTP)
├── skills/     # 技能系统 (loader, manager, registry)
├── ui/         # PyQt6 界面 (main_window, settings, theme)
└── utils/      # 工具函数 (crypto, markdown, fs_operations)
```

## 技术栈

- **Python 3.11+**：核心语言
- **PyQt6**：桌面 GUI
- **aiohttp**：异步 HTTP 客户端
- **SQLite**：对话持久化
- **DeepSeek API**（默认）/ OpenAI 兼容接口

## 提交流程

### 1. Fork 并 Clone

```powershell
git clone https://github.com/YOUR_USERNAME/OpenShelf.git
cd OpenShelf
git remote add upstream https://github.com/xxwkf752tf-sudo/OpenShelf.git
```

### 2. 创建分支

```powershell
git checkout -b feat/your-feature-name
```

分支命名规则：`feat/xxx`（新功能）、`fix/xxx`（修复）、`docs/xxx`（文档）、`refactor/xxx`（重构）。

### 3. 开发

```powershell
pip install -r requirements.txt
python main.py
```

### 4. 提交

提交信息格式：
```
feat(tools): 添加 web_search 工具
fix(engine): 修复流式工具调用为空的问题  
docs(readme): 更新安装说明
```

### 5. Push 并创建 PR

```powershell
git push origin feat/your-feature-name
```

在 GitHub 上创建 Pull Request，描述改动内容和测试方法。

## 检查清单

PR 提交前确认：

- [ ] 代码通过 Python 语法检查 (`python -c "import py_compile; py_compile.compile('src/...', doraise=True)"`)
- [ ] 新增功能有对应的工具注册
- [ ] 中文界面文字完整（菜单、按钮、提示）
- [ ] 不破坏现有工具调用流程
- [ ] 不引入新的外部依赖（除非必要且已在 `requirements.txt` 中声明）
- [ ] 模型名称使用最新版本 (`deepseek-chat`)

## 特别注意

### 模型配置

OpenShelf 默认使用 DeepSeek 作为模型后端。配置项必须反映最新 API：

```
✅ model: "deepseek-chat"
✅ base_url: "https://api.deepseek.com/v1"  
✅ 固定前缀缓存：系统提示词固定为 messages[0]
```

### 线程安全

OpenShelf 使用 QThread 隔离异步引擎。所有 UI 更新必须通过 `queue.Queue` + `QTimer` 机制派发到 Qt 主线程，禁止在异步线程中直接操作 Widget。

### 工具开发

添加新工具需要：
1. 继承 `src.tools.base.Tool` 基类
2. 实现 `async def execute(self, **kwargs) -> dict`
3. 在 `main.py` 的 `register_tools()` 中注册

### API Key 安全

永远不要在代码中硬编码 API Key。使用 `src.utils.crypto.SecureStorage` 存取，优先级：Windows Credential Manager → AES-256-GCM 文件加密。

## 审核流程

维护者将检查：

- [ ] 语法正确性
- [ ] 线程安全（UI 更新机制）
- [ ] 工具调用流程不被破坏
- [ ] 中文本地化完整
- [ ] 依赖变更合理
- [ ] 提交历史清晰

感谢贡献！
