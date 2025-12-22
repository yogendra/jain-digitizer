from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QToolBar)
from PySide6.QtGui import (QFont, QTextCursor, QAction, QTextCharFormat)
from PySide6.QtCore import Qt

class MarkdownRichEditor(QWidget):
    """
    A Rich Text Editor that allows WYSIWYG-style editing 
    but can import and export Markdown.
    """
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #ddd;
                padding: 2px;
            }
            QToolButton {
                padding: 4px;
                margin: 1px;
                border: 1px solid transparent;
            }
            QToolButton:hover {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
            }
        """)

        self.add_action("𝗕", "Bold", self.toggle_bold)
        self.add_action("𝑰", "Italic", self.toggle_italic)
        self.add_action("𝗨", "Underline", self.toggle_underline)
        self.toolbar.addSeparator()
        self.add_action("❶", "Header 1", lambda: self.set_font_size(24, True))
        self.add_action("❷", "Header 2", lambda: self.set_font_size(20, True))
        self.add_action("❸", "Header 3", lambda: self.set_font_size(16, True))
        self.toolbar.addSeparator()
        self.add_action("•", "Bullet List", self.insert_bullet_list)
        self.add_action("🔢", "Numbered List", self.insert_numbered_list)
        self.toolbar.addSeparator()
        self.add_action("⮕", "Indent", self.indent)
        self.add_action("⬅", "Outdent", self.outdent)

        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(placeholder)
        self.editor.setFont(QFont("Arial", 12))
        self.editor.setAcceptRichText(True)
        # Set a reasonable tab stop for indentation
        self.editor.setTabStopDistance(20)
        
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.editor)

    def add_action(self, text, tooltip, callback):
        action = QAction(text, self)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        self.toolbar.addAction(action)
        
        button = self.toolbar.widgetForAction(action)
        if button:
            button.setFixedWidth(30)
            font = button.font()
            font.setPointSize(14)
            button.setFont(font)

    def toggle_bold(self):
        fmt = self.editor.currentCharFormat()
        weight = QFont.Normal if fmt.fontWeight() == QFont.Bold else QFont.Bold
        fmt.setFontWeight(weight)
        self.editor.setCurrentCharFormat(fmt)

    def toggle_italic(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.editor.setCurrentCharFormat(fmt)

    def toggle_underline(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.editor.setCurrentCharFormat(fmt)

    def set_font_size(self, size, bold=False):
        fmt = self.editor.currentCharFormat()
        fmt.setFontPointSize(size)
        if bold:
            fmt.setFontWeight(QFont.Bold)
        self.editor.setCurrentCharFormat(fmt)

    def insert_bullet_list(self):
        cursor = self.editor.textCursor()
        cursor.insertList(QTextCursor.ListDisc)

    def insert_numbered_list(self):
        cursor = self.editor.textCursor()
        cursor.insertList(QTextCursor.ListDecimal)

    def indent(self):
        cursor = self.editor.textCursor()
        block_format = cursor.blockFormat()
        block_format.setIndent(block_format.indent() + 1)
        cursor.setBlockFormat(block_format)

    def outdent(self):
        cursor = self.editor.textCursor()
        block_format = cursor.blockFormat()
        if block_format.indent() > 0:
            block_format.setIndent(block_format.indent() - 1)
            cursor.setBlockFormat(block_format)

    def setMarkdown(self, text):
        # PySide6's setMarkdown converts MD to Rich Text internally
        self.editor.setMarkdown(text)

    def toMarkdown(self):
        # PySide6's toMarkdown converts Rich Text back to MD
        return self.editor.toMarkdown()

    def setPlainText(self, text):
        self.editor.setPlainText(text)

    def toPlainText(self):
        return self.editor.toPlainText()

    def clear(self):
        self.editor.clear()

    def append(self, text):
        # For appending results, we often want them as markdown fragments
        # We can temporarily move cursor to end and use insertHtml/Markdown
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.editor.setTextCursor(cursor)
        
        # If it looks like a header or MD, use insertMarkdown
        if text.strip().startswith("#") or "---" in text:
            self.editor.insertMarkdown(text)
        else:
            self.editor.append(text)
