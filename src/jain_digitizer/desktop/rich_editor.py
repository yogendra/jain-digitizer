from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QToolBar)
from PySide6.QtGui import (QFont, QTextCursor, QAction, QTextCharFormat)
from PySide6.QtCore import Qt, QMimeData, QEvent
from jain_digitizer.common.logger_setup import logger

class HtmlTextEdit(QTextEdit):
    """
    A QTextEdit that handles HTML content.
    """
    def insertFromMimeData(self, source: QMimeData):
        if source.hasHtml():
            self.textCursor().insertHtml(source.html())
        elif source.hasText():
            self.textCursor().insertText(source.text())
        else:
            super().insertFromMimeData(source)

    def createMimeDataFromSelection(self):
        """
        Custom mime data creation to ensure rich text/HTML is 
        correctly placed on the clipboard for apps like Word.
        """
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return None
        
        fragment = cursor.selection()
        mime = QMimeData()
        
        # Plain text
        mime.setText(cursor.selectedText().replace('\u2029', '\n'))
        
        # HTML content
        # fragment.toHtml() provides a full HTML document including CSS for formatting
        mime.setHtml(fragment.toHtml())
        
        return mime

    def wheelEvent(self, event):
        """Handle Ctrl+Scroll for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
            event.accept()
        else:
            super().wheelEvent(event)

    def contextMenuEvent(self, event):
        """Custom context menu for easier copying."""
        menu = self.createStandardContextMenu()
        
        # We can add custom actions here if needed
        # But for now, the standard menu should be fine 
        # as it uses createMimeDataFromSelection internally
        
        menu.exec(event.globalPos())

    def event(self, event):
        """Handle Mac trackpad pinch gesture."""
        if event.type() == QEvent.NativeGesture:
            if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
                # On macOS, scale is positive for pinch out (spread), negative for pinch in (contract)
                scale = event.value()
                
                if scale > 0.01:      # Pinch Out / Spread
                    self.zoomIn()
                elif scale < -0.01:   # Pinch In / Contract
                    self.zoomOut()
                return True
        return super().event(event)

class HtmlRichEditor(QWidget):
    """
    A Rich Text Editor that allows WYSIWYG-style editing 
    using HTML for internal and external representation.
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

        # Editor
        self.editor = HtmlTextEdit()
        self.editor.setPlaceholderText(placeholder)
        self.editor.setFont(QFont("Arial", 14))
        self.editor.setAcceptRichText(True)
        # Set a reasonable tab stop for indentation
        self.editor.setTabStopDistance(20)

        # Toolbar actions
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
        self.toolbar.addSeparator()

        # Font size controls
        self.add_action("A+", "Increase Font Size", self.zoomIn)
        self.add_action("A-", "Decrease Font Size", self.zoomOut)
        self.toolbar.addSeparator()
        self.add_action("📋", "Copy All", self.copy_all)
        self.add_action("⌫", "Normal Text (Clear Formatting)", self.clear_formatting)
        
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.editor)

    def copy_all(self):
        """Copies the entire content as HTML to the clipboard."""
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtCore import QMimeData
        
        mime = QMimeData()
        # Set both HTML and Plain Text
        mime.setHtml(self.editor.toHtml())
        mime.setText(self.editor.toPlainText().replace('\u2029', '\n'))
        
        QGuiApplication.clipboard().setMimeData(mime)
        logger.info("Copied all content to clipboard as rich text")

    def clear_formatting(self):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            # If no selection, just clear the current character format
            self.editor.setCurrentCharFormat(QTextCharFormat())
            # Also reset font to default
            self.editor.setFont(QFont("Arial", 14))
            return

        # If there is a selection, clear formatting of the selected text
        cursor.beginEditBlock()
        
        # 1. Reset character format (bold, italic, color, etc.)
        cursor.setCharFormat(QTextCharFormat())
        
        # 2. Reset block format (alignment, margins, etc.)
        from PySide6.QtGui import QTextBlockFormat
        cursor.setBlockFormat(QTextBlockFormat())
        
        cursor.endEditBlock()
        self.editor.setTextCursor(cursor)

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

    def zoomIn(self):
        self.editor.zoomIn()

    def zoomOut(self):
        self.editor.zoomOut()

    def setHtml(self, text):
        self.editor.setHtml(text)

    def toHtml(self):
        return self.editor.toHtml()

    def setMarkdown(self, text):
        self.editor.setMarkdown(text)

    def toMarkdown(self):
        return self.editor.toMarkdown()

    def setPlainText(self, text):
        self.editor.setPlainText(text)

    def toPlainText(self):
        return self.editor.toPlainText()

    def clear(self):
        self.editor.clear()

    def append(self, text):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.editor.setTextCursor(cursor)
        
        # Check if it looks like HTML
        if text.strip().startswith("<") or "</" in text:
            self.editor.insertHtml(text)
        else:
            self.editor.append(text)

