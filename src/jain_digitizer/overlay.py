from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # Overlay background
        self.bg_color = QColor(255, 255, 255, 180)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("⚡ Processing with Gemini AI...")
        self.label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #3498db;
        """)
        
        layout.addWidget(self.label)
        
        # Animating opacity for a pulse effect
        self.opacity_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0.4)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setLoopCount(-1) # Infinite
        
        self.hide()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)

    def showEvent(self, event):
        self.animation.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.animation.stop()
        super().hideEvent(event)

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)
