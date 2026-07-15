# -*- coding: utf-8 -*-
"""OpenShelf - Windows 本地 AI 编程助手。"""
import os as _os
_os.write(2, b"[OpenShelf] Starting...\n")
import sys, asyncio, time, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

_os.write(2, b"[OpenShelf] Importing PyQt6...\n")
from PyQt6.QtWidgets import QMessageBox

_os.write(2, b"[OpenShelf] Importing core modules...\n")
from src.core.app import OpenShelfApp
from src.core.storage import Database
from src.core.engine import AgentLoop
from src.core.query import QueryEngine
from src.tools.registry import ToolRegistry
from src.tools.bash_tool import BashTool
from src.tools.powershell_tool import PowerShellTool
from src.tools.file_read import FileReadTool
from src.tools.file_write import FileWriteTool
from src.tools.file_edit import FileEditTool
from src.tools.glob_tool import GlobTool
from src.tools.grep_tool import GrepTool
from src.tools.web_fetch import WebFetchTool
from src.tools.web_search import WebSearchTool
from src.tools.task_tools import TaskCreateTool, TaskListTool, TaskGetTool
from src.tools.mcp_tool import MCPTool

_os.write(2, b"[OpenShelf] Importing API...\n")
from src.api.registry import ProviderRegistry

_os.write(2, b"[OpenShelf] Importing utils...\n")
from src.utils.crypto import SecureStorage
from src.skills.manager import SkillManager
from src.mcp.server_manager import MCPServerManager
from src.permissions.manager import PermissionManager

_os.write(2, b"[OpenShelf] Importing UI...\n")
from src.ui.main_window import MainWindow
_os.write(2, b"[OpenShelf] All imports done\n")


def register_tools(registry, mcp_manager=None):
    registry.register_many([
        BashTool(), PowerShellTool(), FileReadTool(), FileWriteTool(),
        FileEditTool(), GlobTool(), GrepTool(), WebFetchTool(),
        WebSearchTool(), TaskCreateTool(), TaskListTool(), TaskGetTool(),
        MCPTool(mcp_manager=mcp_manager),
    ])


def initialize_services(storage, async_loop):
    db = Database()
    db.initialize()
    registry = ToolRegistry()
    mcp_mgr = MCPServerManager(db)
    register_tools(registry, mcp_mgr)
    skill_mgr = SkillManager()
    try:
        skill_mgr.load_from_dir(Path(__file__).parent / "resources" / "default_skills")
    except Exception as e:
        _os.write(2, f"Skill load warning: {e}\n".encode())
    providers = ProviderRegistry.from_settings(storage)
    provider = providers.get_default()
    if provider is None:
        from src.api.deepseek import DeepSeekProvider
        provider = DeepSeekProvider(api_key="", base_url="https://api.deepseek.com/v1")
    agent = AgentLoop(provider, registry)
    db.create_conversation(agent.conversation_id, title="新对话")
    sp = "你是 OpenShelf，一个 Windows 本地 AI 编程助手。用中文回复用户。"
    try:
        si = skill_mgr._registry.get_instructions()
    except Exception:
        si = []
    agent.set_system_prompt(sp, si)
    if hasattr(provider, "set_fixed_prefix"):
        from src.api.base import ChatMessage
        provider.set_fixed_prefix([ChatMessage(role="system", content=agent.system_prompt)])
    qe = QueryEngine(agent, db)
    return agent, qe, mcp_mgr, skill_mgr, providers


def main():
    _os.write(2, b"[OpenShelf] main() entered\n")
    try:
        app_controller = OpenShelfApp()
        qt_app = app_controller.initialize()
        _os.write(2, b"[OpenShelf] QApplication created\n")

        if app_controller.is_duplicate():
            QMessageBox.warning(None, "OpenShelf", "OpenShelf 已在运行中。")
            return 0

        storage = SecureStorage()
        async_loop = None
        waited = 0
        while async_loop is None and waited < 5:
            async_loop = app_controller.get_async_loop()
            if async_loop is None:
                time.sleep(0.2)
                waited += 0.2

        if async_loop is None:
            QMessageBox.critical(None, "错误", "异步引擎启动失败。")
            return 1

        _os.write(2, b"[OpenShelf] Initializing services...\n")
        agent, qe, mcp_mgr, skill_mgr, providers = initialize_services(storage, async_loop)
        _os.write(2, b"[OpenShelf] Creating window...\n")

        window = MainWindow(app_controller)
        window.set_async_loop(async_loop)
        window.set_agent_loop(agent)
        window.show()
        _os.write(2, b"[OpenShelf] Auto-loading last conversation...\n")
        window.autoload_conversation()
        _os.write(2, b"[OpenShelf] Window shown, entering event loop\n")

        exit_code = app_controller.run()
        _os.write(2, f"[OpenShelf] Exit code: {exit_code}\n".encode())

        try:
            future = asyncio.run_coroutine_threadsafe(app_controller.cleanup(), async_loop)
            future.result(timeout=5)
        except Exception:
            pass
        Database().close()
        return exit_code

    except Exception as e:
        _os.write(2, f"[OpenShelf] FATAL: {e}\n".encode())
        traceback.print_exc(file=sys.stderr)
        try:
            QMessageBox.critical(None, "OpenShelf 启动失败", str(e))
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())