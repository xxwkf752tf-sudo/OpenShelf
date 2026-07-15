# -*- coding: utf-8 -*-
"""主窗口 - 中文界面。导出、自动保存、自动加载。"""
import os as _os
_os.write(2, b"[main_window] importing PyQt6...\n")
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QStatusBar, QLabel, QPushButton, QMessageBox, QFileDialog, QTextBrowser, QPlainTextEdit, QListWidget)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QAction
import asyncio, uuid, queue, json, os
from pathlib import Path
from datetime import datetime
from src.ui.theme import ThemeManager
from src.utils.markdown import MarkdownRenderer
_os.write(2, b"[main_window] imports done\n")

AUTOSAVE_FILE = "autosave.json"


class MainWindow(QMainWindow):

    def __init__(self, app_controller=None):
        super().__init__()
        self._app = app_controller
        self._agent_loop = None
        self._async_loop = None
        self._cancel_requested = False
        self._stream_buf = ""
        self._msg_queue = queue.Queue()
        self._autosave_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "OpenShelf"
        self._autosave_dir.mkdir(parents=True, exist_ok=True)
        self.setWindowTitle("OpenShelf - 本地 AI 编程助手")
        self.setMinimumSize(QSize(1200, 800))
        self.resize(QSize(1400, 900))
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_statusbar()
        self._apply_theme()
        self._poll_timer = QTimer()
        self._poll_timer.timeout.connect(self._poll_messages)
        self._poll_timer.start(100)

    def set_async_loop(self, loop):
        self._async_loop = loop

    def set_agent_loop(self, agent_loop):
        self._agent_loop = agent_loop

    def _poll_messages(self):
        try:
            while True:
                msg = self._msg_queue.get_nowait()
                if msg[0] == "chat":
                    self._append_chat(msg[1], msg[2])
                elif msg[0] == "chat_stream":
                    self._stream_buf += msg[1]
                elif msg[0] == "status":
                    self.status_label.setText(msg[1])
                elif msg[0] == "button_text":
                    self.send_btn.setText(msg[1])
                    self.send_btn.setEnabled(True)
                elif msg[0] == "button":
                    self.send_btn.setEnabled(msg[1])
        except queue.Empty:
            if self._stream_buf:
                buf = self._stream_buf
                self._stream_buf = ""
                escaped = buf.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                self.chat_view.append('<div style="margin:4px 0; color: #a6e3a1; font-style:italic;">' + escaped + '</div>')

    def _append_chat(self, role, content):
        try:
            html = MarkdownRenderer.to_html(content)
            colors = {"user": "#89b4fa", "assistant": "#a6e3a1", "tool": "#f9e2af", "error": "#f38ba8", "system": "#94e2d5"}
            c = colors.get(role, "#cdd6f4")
            labels = {"user": "你", "assistant": "助手", "tool": "工具", "error": "错误", "system": "系统"}
            label = labels.get(role, role)
            self.chat_view.append('<div style="margin:8px 0;"><span style="color:' + c + ';font-weight:bold;">' + label + ':</span><div style="margin:4px 0;">' + html + '</div></div>')
        except Exception:
            self.chat_view.append("<div><b>" + role + ":</b> " + str(content) + "</div>")

    def _setup_menubar(self):
        mb = self.menuBar()
        fm = mb.addMenu("文件(&F)")
        fm.addAction("新建对话", self._new_conversation)
        fm.addAction("打开项目...", self._open_project)
        fm.addAction("导出对话...", self._export_conversation)
        fm.addAction("设置...", self._open_settings)
        fm.addSeparator()
        fm.addAction("退出", self.close)
        vm = mb.addMenu("视图(&V)")
        vm.addAction("切换主题", self._toggle_theme)
        tm = mb.addMenu("工具(&T)")
        tm.addAction("API 配置", self._open_api_config)
        tm.addAction("MCP 服务器...")
        hm = mb.addMenu("帮助(&H)")
        hm.addAction("关于 OpenShelf", self._show_about)

    def _setup_toolbar(self):
        tb = QToolBar("主工具栏")
        tb.setMovable(False)
        tb.addAction("新建对话", self._new_conversation)
        tb.addAction("导出", self._export_conversation)
        tb.addAction("设置", self._open_settings)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

    def _setup_central_widget(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        ft = QWidget()
        ftl = QVBoxLayout(ft)
        ftl.addWidget(QLabel("项目文件"))
        self.file_list = QListWidget()
        ftl.addWidget(self.file_list)
        splitter.addWidget(ft)
        center = QSplitter(Qt.Orientation.Vertical)
        cw = QWidget()
        cl = QVBoxLayout(cw)
        cl.setContentsMargins(4, 4, 4, 4)
        self.chat_view = QTextBrowser()
        self.chat_view.setOpenExternalLinks(True)
        self.chat_view.setReadOnly(True)
        cl.addWidget(self.chat_view, stretch=4)
        iw = QWidget()
        il = QHBoxLayout(iw)
        il.setContentsMargins(0, 0, 0, 0)
        self.chat_input = QPlainTextEdit()
        self.chat_input.setPlaceholderText("在此输入问题... (Ctrl+Enter 发送)")
        self.chat_input.setMaximumHeight(120)
        self.chat_input.setMinimumHeight(40)
        il.addWidget(self.chat_input)
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedWidth(80)
        self.send_btn.clicked.connect(self._on_send_click)
        il.addWidget(self.send_btn)
        cl.addWidget(iw, stretch=0)
        center.addWidget(cw)
        tw = QWidget()
        tl = QVBoxLayout(tw)
        tl.setContentsMargins(4, 4, 4, 4)
        tl.addWidget(QLabel("AI 终端（只读）"))
        self.terminal_view = QPlainTextEdit()
        self.terminal_view.setReadOnly(True)
        self.terminal_view.setPlaceholderText("AI 执行的命令和输出将在此处显示...")
        tl.addWidget(self.terminal_view)
        center.addWidget(tw)
        center.setSizes([600, 200])
        splitter.addWidget(center)
        splitter.setSizes([250, 950])
        layout.addWidget(splitter)
        self.setCentralWidget(central)

    def _setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.status_label = QLabel("就绪")
        self.token_label = QLabel("Token: -- | 缓存: --")
        self.model_label = QLabel("模型: --")
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.token_label)
        self.status_bar.addPermanentWidget(self.model_label)
        self.setStatusBar(self.status_bar)

    def _apply_theme(self):
        try:
            qss = ThemeManager().load_theme("dark")
            if qss: self.setStyleSheet(qss)
        except Exception: pass

    def _new_conversation(self):
        self._stream_buf = ""
        self.chat_view.clear()
        self.status_label.setText("新对话已创建")
        if self._agent_loop:
            self._agent_loop.conversation = []
            self._agent_loop.conversation_id = str(uuid.uuid4())
            from src.core.storage import Database
            db = Database()
            db.create_conversation(self._agent_loop.conversation_id, title="新对话")

    def _open_project(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setWindowTitle("选择项目目录")
        if dlg.exec():
            p = dlg.selectedFiles()[0]
            self.status_label.setText("项目: " + p)

    def _open_settings(self):
        try:
            from src.ui.settings.settings_dialog import SettingsDialog
            SettingsDialog(self).exec()
        except Exception as e:
            QMessageBox.warning(self, "设置错误", str(e))

    def _open_api_config(self):
        try:
            from src.ui.settings.api_config import ApiConfigDialog
            ApiConfigDialog(self).exec()
        except Exception as e:
            QMessageBox.warning(self, "API 配置错误", str(e))

    def _toggle_theme(self):
        try:
            name, qss = ThemeManager().toggle()
            self.setStyleSheet(qss)
        except Exception: pass

    def _show_about(self):
        QMessageBox.about(self, "关于 OpenShelf",
            "OpenShelf v1.0.0\nWindows 本地 AI 编程助手\n\nMIT 开源协议")

    # ======== 导出 ========
    def _export_conversation(self):
        try:
            dlg = QFileDialog()
            dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dlg.setNameFilter("JSON 文件 (*.json);;Markdown 文件 (*.md)")
            dlg.setDefaultSuffix("json")
            dlg.setWindowTitle("导出对话记录")
            if dlg.exec():
                path = dlg.selectedFiles()[0]
                self._save_conversation_to_file(path)
                self.status_label.setText("已导出到: " + path)
        except Exception as e:
            QMessageBox.warning(self, "导出失败", str(e))

    def _save_conversation_to_file(self, filepath):
        from src.core.storage import Database
        db = Database()
        cid = self._agent_loop.conversation_id if self._agent_loop else ""
        msgs = db.get_messages(cid) if cid else []
        data = {"conversation_id": cid, "exported_at": datetime.utcnow().isoformat(), "messages": msgs}
        if filepath.endswith(".md"):
            lines = ["# OpenShelf 对话记录", "", "导出时间: " + datetime.utcnow().isoformat(), ""]
            for m in msgs:
                lines.append("### " + m.get("role", ""))
                if m.get("content"):
                    lines.append(m["content"])
                    lines.append("")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # ======== 自动保存 ========
    def _autosave(self):
        try:
            autosave_path = self._autosave_dir / AUTOSAVE_FILE
            self._save_conversation_to_file(str(autosave_path))
        except Exception:
            pass

    # ======== 自动加载 ========
    def autoload_conversation(self):
        try:
            autosave_path = self._autosave_dir / AUTOSAVE_FILE
            if not autosave_path.exists():
                return False
            with open(autosave_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            msgs = data.get("messages", [])
            if not msgs:
                return False
            self.chat_view.clear()
            for m in msgs:
                self._append_chat(m.get("role", ""), m.get("content", "") or "")
            if self._agent_loop:
                from src.api.base import ChatMessage
                self._agent_loop.conversation_id = data.get("conversation_id", str(uuid.uuid4()))
                self._agent_loop.conversation = []
                for m in msgs:
                    self._agent_loop.conversation.append(
                        ChatMessage(role=m.get("role",""), content=m.get("content","") or "")
                    )
            self.status_label.setText("已加载上次对话")
            return True
        except Exception:
            return False

    # ======== 发送/停止 ========
    def _on_send_click(self):
        if self.send_btn.text() == "停止":
            self._cancel_requested = True
            if self._agent_loop:
                self._agent_loop.cancel()
            self._msg_queue.put(("chat", "system", "已取消。"))
            self._msg_queue.put(("button_text", "发送"))
            self._msg_queue.put(("status", "就绪"))
            return
        self._cancel_requested = False
        self._do_send()

    def _do_send(self):
        text = self.chat_input.toPlainText().strip()
        if not text: return
        self.chat_input.clear()
        self._stream_buf = ""
        self._msg_queue.put(("chat", "user", text))
        self._msg_queue.put(("status", "处理中..."))
        self._msg_queue.put(("button_text", "停止"))
        if self._async_loop and self._agent_loop:
            asyncio.run_coroutine_threadsafe(self._process_message(text), self._async_loop)
        else:
            self._msg_queue.put(("chat", "error", "引擎未就绪，请重启应用。"))
            self._msg_queue.put(("button_text", "发送"))

    async def _process_message(self, text):
        try:
            if self._agent_loop is None:
                self._msg_queue.put(("chat", "error", "AI 引擎未初始化，请在设置中填入 API Key。"))
                return
            async for event in self._agent_loop.run(text):
                if event["type"] == "text_delta":
                    pass
                elif event["type"] == "tool_result":
                    self._msg_queue.put(("chat", "tool", f"结果: {str(event.get("result",""))[:300]}"))
                elif event["type"] == "tool_call":
                    self._msg_queue.put(("chat", "tool", "调用工具: " + event.get("name","")))
                elif event["type"] == "done":
                    self._msg_queue.put(("chat", "assistant", event.get("content","")))
                elif event["type"] == "cancelled":
                    self._msg_queue.put(("chat", "system", "已取消。"))
                elif event["type"] == "max_turns_exceeded":
                    self._msg_queue.put(("chat", "system", "已达最大轮次，请新建对话。"))
            self._autosave()
        except Exception as e:
            self._msg_queue.put(("chat", "error", str(e)))
        finally:
            self._msg_queue.put(("button_text", "发送"))
            self._msg_queue.put(("status", "就绪"))
            self._autosave()