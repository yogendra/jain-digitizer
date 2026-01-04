import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QLabel, QPushButton, QSizePolicy, QHBoxLayout, QWidget, QPlainTextEdit, QSplitter, QTextEdit)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from jain_digitizer.version import __version__, __commit__

class SettingsDialog(QDialog):
    def __init__(self, parent=None, api_key="", prompt=""):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(800, 600)
        
        main_layout = QVBoxLayout(self)
        
        # API Key Section
        label_api = QLabel("Gemini API Key:")
        main_layout.addWidget(label_api)
        
        # API Key Field with Show/Hide toggle
        self.api_key_container = QWidget()
        self.api_key_layout = QHBoxLayout(self.api_key_container)
        self.api_key_layout.setContentsMargins(0, 0, 0, 0)
        
        self.api_key_input = QLineEdit(api_key)
        self.api_key_input.setPlaceholderText("Enter your Gemini API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        
        self.reveal_btn = QPushButton("Show")
        self.reveal_btn.setFixedWidth(60)
        self.reveal_btn.setCheckable(True)
        self.reveal_btn.setToolTip("Show/Hide API Key")
        self.reveal_btn.clicked.connect(self.toggle_api_key_visibility)
        
        self.api_key_layout.addWidget(self.api_key_input, 1) # Add stretch factor
        self.api_key_layout.addWidget(self.reveal_btn)
        
        main_layout.addWidget(self.api_key_container)
        
        # Prompt Header with Preview Button
        prompt_header = QWidget()
        prompt_header_layout = QHBoxLayout(prompt_header)
        prompt_header_layout.setContentsMargins(0, 0, 0, 0)
        
        label_prompt = QLabel("System Prompt (Markdown):")
        self.btn_preview = QPushButton("👁️ Preview Markdown")
        self.btn_preview.setFixedWidth(150)
        self.btn_preview.clicked.connect(self.render_preview)
        
        prompt_header_layout.addWidget(label_prompt)
        prompt_header_layout.addStretch()
        prompt_header_layout.addWidget(self.btn_preview)
        
        main_layout.addWidget(prompt_header)
        
        # Splitter for Editor and Preview
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 1. Editor
        self.prompt_input = QPlainTextEdit()
        self.prompt_input.setPlainText(prompt)
        self.prompt_input.setFont(QFont("Courier New", 12) if os.name != 'posix' else QFont("Menlo", 12))
        self.prompt_input.setPlaceholderText("Enter the system prompt instructions here...")
        self.prompt_input.setStyleSheet("""
            QPlainTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        
        # 2. Preview Pane
        self.preview_pane = QTextEdit()
        self.preview_pane.setReadOnly(True)
        self.preview_pane.setPlaceholderText("Markdown preview will appear here...")
        self.preview_pane.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        
        self.splitter.addWidget(self.prompt_input)
        self.splitter.addWidget(self.preview_pane)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(self.splitter, 1) # Set stretch factor to 1 to take max height
        
        # Render initial preview
        self.render_preview()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.accept)
        main_layout.addWidget(self.save_btn)
        
        # Version Information
        version_text = f"Version: {__version__}"
        if __commit__ and __commit__ != "unknown":
            version_text += f" ({__commit__})"
            
        version_label = QLabel(version_text)
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #888; font-size: 11px; margin-top: 10px; font-style: italic;")
        main_layout.addWidget(version_label)

    def toggle_api_key_visibility(self):
        if self.reveal_btn.isChecked():
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.reveal_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.reveal_btn.setText("Show")

    def render_preview(self):
        markdown_text = self.prompt_input.toPlainText()
        self.preview_pane.setMarkdown(markdown_text)
