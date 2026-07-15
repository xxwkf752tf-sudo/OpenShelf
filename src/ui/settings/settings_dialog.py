"""设置对话框 - 中文界面。"""
from PyQt6.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QLabel, QDialogButtonBox, QWidget)
from src.utils.crypto import SecureStorage

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OpenShelf 设置")
        self.setMinimumSize(550, 400)
        self._storage = SecureStorage()
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._model_page(), "模型")
        tabs.addTab(QLabel("MCP 配置即将上线。"), "MCP")
        tabs.addTab(QLabel("技能管理即将上线。"), "技能")
        layout.addWidget(tabs)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("确定")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        layout.addWidget(btns)

    def _model_page(self):
        page = QWidget()
        form = QFormLayout(page)

        self.ds_key = QLineEdit()
        self.ds_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.ds_key.setPlaceholderText("sk-...")
        self.ds_key.setText(self._storage.get_credential("deepseek_api_key") or "")
        form.addRow("DeepSeek API Key:", self.ds_key)

        self.ds_url = QLineEdit()
        self.ds_url.setText(self._storage.get_config("deepseek_base_url","https://api.deepseek.com/v1"))
        form.addRow("DeepSeek 接口地址:", self.ds_url)

        self.oa_key = QLineEdit()
        self.oa_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.oa_key.setPlaceholderText("sk-...")
        self.oa_key.setText(self._storage.get_credential("openai_api_key") or "")
        form.addRow("OpenAI API Key:", self.oa_key)

        self.ollama_url = QLineEdit()
        self.ollama_url.setText(self._storage.get_config("ollama_base_url","http://localhost:11434/v1"))
        form.addRow("Ollama 接口地址:", self.ollama_url)

        tip = QLabel("提示：获取 DeepSeek API Key 请访问 platform.deepseek.com")
        tip.setStyleSheet("color: #6c7086; font-size: 11px;")
        form.addRow("", tip)

        return page

    def _save(self):
        self._storage.set_credential("deepseek_api_key", self.ds_key.text())
        self._storage.set_config("deepseek_base_url", self.ds_url.text())
        self._storage.set_credential("openai_api_key", self.oa_key.text())
        self._storage.set_config("ollama_base_url", self.ollama_url.text())
        self.accept()
