import sys
from PySide6.QtWidgets import QApplication
from .app_window import JainDigitizer

def main():
    app = QApplication(sys.argv)
    window = JainDigitizer()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
