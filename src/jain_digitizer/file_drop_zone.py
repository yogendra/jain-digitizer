from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class FileDropZone(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.set_default_style()

    def set_default_style(self):
        # Check if we have files already to decide which style to show
        # Note: self.window() refers to the top-level window (JainDigitizer)
        if hasattr(self.window(), 'file_list') and self.window().file_list:
            self.setStyleSheet("""
                QLabel {
                    border: 3px solid #2ecc71;
                    border-radius: 12px;
                    background-color: #f0fdf4;
                    font-size: 16px;
                    color: #166534;
                    font-weight: bold;
                }
                QLabel:hover {
                    background-color: #dcfce7;
                    border-color: #27ae60;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 3px dashed #95a5a6;
                    border-radius: 12px;
                    background-color: #f4f7f6;
                    font-size: 16px;
                    color: #7f8c8d;
                }
                QLabel:hover {
                    border: 3px dashed #3498db;
                    background-color: #ecf0f1;
                    color: #3498db;
                }
            """)

    def set_active_style(self):
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #3498db;
                border-radius: 12px;
                background-color: #ebf5fb;
                font-size: 16px;
                color: #3498db;
                font-weight: bold;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.set_active_style()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.set_default_style()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            urls = event.mimeData().urls()
            if urls:
                file_paths = [u.toLocalFile() for u in urls]
                self.window().add_files(file_paths)
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window().open_file_dialog()
