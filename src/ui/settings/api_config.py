# -*- coding: utf-8 -*-
"""API 配置对话框。"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QLabel, QDialogButtonBox, QWidget, QGroupBox, QPushButton, QHBoxLayout)
from src.utils.crypto import SecureStorage

class ApiConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API 配置")
        self.setMinimumSize(500, 350)
        self._storage = SecureStorage()
        layout = QVBoxLayout(self)

        # DeepSeek
        ds_group = QGroupBox("DeepSeek（推荐）")
        ds_form = QFormLayout(ds_group)
        self.ds_key = QLineEdit()
        self.ds_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.ds_key.setPlaceholderText("sk-...")
        self.ds_key.setText(self._storage.get_credential("deepseek_api_key") or "")
        ds_form.addRow("API Key:", self.ds_key)
        self.ds_url = QLineEdit()
        self.ds_url.setText(self._storage.get_config("deepseek_base_url","https://api.deepseek.com/v1"))
        ds_form.addRow("接口地址:", self.ds_url)
        ds_tip = QLabel("获取 Key: platform.deepseek.com")
        ds_tip.setStyleSheet("color: #6c7086; font-size: 11px;")
        ds_form.addRow("", ds_tip)
        layout.addWidget(ds_group)

        # OpenAI 兼容
        oa_group = QGroupBox("OpenAI 兼容接口")
        oa_form = QFormLayout(oa_group)
        self.oa_key = QLineEdit()
        self.oa_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.oa_key.setPlaceholderText("sk-...")
        self.oa_key.setText(self._storage.get_credential("openai_api_key") or "")
        oa_form.addRow("API Key:", self.oa_key)
        self.ollama_url = QLineEdit()
        self.ollama_url.setText(self._storage.get_config("ollama_base_url","http://localhost:11434/v1"))
        oa_form.addRow("Ollama 地址:", self.ollama_url)
        layout.addWidget(oa_group)

        # 按钮
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("保存")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")

        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self._test_connection)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(btns)
        layout.addLayout(btn_layout)

    def _save(self):
        if self.ds_key.text().strip():
            self._storage.set_credential("deepseek_api_key", self.ds_key.text().strip())
        self._storage.set_config("deepseek_base_url", self.ds_url.text().strip())
        if self.oa_key.text().strip():
            self._storage.set_credential("openai_api_key", self.oa_key.text().strip())
        self._storage.set_config("ollama_base_url", self.ollama_url.text().strip())
        self.accept()

    def _test_connection(self):
        from PyQt6.QtWidgets import QMessageBox, QApplication
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            import asyncio
            async def test():
                from src.api.deepseek import DeepSeekProvider
                from src.api.base import ChatMessage
                key = self.ds_key.text().strip()
                if not key:
                    return False, "请先填入 API Key"
                p = DeepSeekProvider(api_key=key, base_url=self.ds_url.text().strip())
                try:
                    resp = await p.chat([ChatMessage(role="user", content="hi")], max_tokens=5)
                    return True, f"连接成功！模型: {resp.model}"
                except Exception as e:
                    return False, str(e)
            loop = asyncio.new_event_loop()
            ok, msg = loop.run_until_complete(test())
            loop.close()
            if ok:
                QMessageBox.information(self, "测试结果", msg)
            else:
                QMessageBox.warning(self, "测试失败", msg)
        except Exception as e:
            QMessageBox.warning(self, "测试失败", str(e))
        finally:
            QApplication.restoreOverrideCursor()