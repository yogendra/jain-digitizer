import os
import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QMessageBox, QSplitter, QApplication, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon

from .rich_editor import MarkdownRichEditor
from .settings_dialog import SettingsDialog
from .file_drop_zone import FileDropZone
from .constants import DEFAULT_PROMPT
from .translator import Translator
from .logger_setup import logger
from .overlay import LoadingOverlay

class TranslationWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, translator, file_list):
        super().__init__()
        self.translator = translator
        self.file_list = file_list

    def run(self):
        try:
            results = self.translator.translate_files(self.file_list)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class JainDigitizer(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing Main Window")
        self.setWindowTitle("Jain Digitizer")
        self.resize(1200, 900)
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # App State
        self.api_key = ""
        self.system_prompt = DEFAULT_PROMPT
        self.file_list = []
        self.worker = None # Track worker
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Pane ---
        top_pane = QWidget()
        top_pane.setFixedHeight(120)  # Fixed height for symmetry
        top_layout = QHBoxLayout(top_pane)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(10)
        
        self.drop_zone = FileDropZone("Drag & Drop PDF or Images Here\n(Click to browse)")
        top_layout.addWidget(self.drop_zone, 1) # Give dropzone stretch
        
        # Right-side button stack
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(5)
        self.btn_process = QPushButton("🚀 Start Processing")
        self.btn_process.setFixedHeight(30)
        self.btn_process.setFixedWidth(150)
        self.btn_process.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        self.btn_process.clicked.connect(self.process_file)
        
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.setFixedHeight(30)
        self.btn_settings.setFixedWidth(150)
        self.btn_settings.clicked.connect(self.open_settings)

        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.setFixedHeight(30)
        self.btn_clear.setFixedWidth(150)
        self.btn_clear.clicked.connect(self.clear_files)
        
        btn_layout.addWidget(self.btn_process)
        btn_layout.addWidget(self.btn_settings)
        btn_layout.addWidget(self.btn_clear)
        
        top_layout.addWidget(btn_container)

        # --- Workspace ---
        splitter = QSplitter(Qt.Horizontal)
        self.hindi_editor = MarkdownRichEditor("HINDI OCR (SOURCE)...")
        self.english_editor = MarkdownRichEditor("SCHOLARLY MANUSCRIPT (ENGLISH & IAST)...")

        splitter.addWidget(self.hindi_editor)
        splitter.addWidget(self.english_editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setHeight = 10
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 20px;
            }
        """)

        main_layout.addWidget(top_pane)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(splitter)

        # --- Loading Overlay ---
        self.loading_overlay = LoadingOverlay(self.centralWidget())
        self.loading_overlay.hide()

    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key", "")
                    self.system_prompt = data.get("prompt", DEFAULT_PROMPT)
            except: pass

    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump({"api_key": self.api_key, "prompt": self.system_prompt}, f)

    def open_settings(self):
        diag = SettingsDialog(self, self.api_key, self.system_prompt)
        if diag.exec():
            self.api_key = diag.api_key_input.text()
            self.system_prompt = diag.prompt_input.toPlainText()
            self.save_settings()

    def process_file(self):
        if not self.file_list:
            logger.warning("Process clicked with no files selected")
            QMessageBox.warning(self, "No Files", "Please select or drop files first.")
            return

        if not self.api_key:
            logger.error("Process clicked without API key")
            QMessageBox.critical(self, "Error", "Please provide a Gemini API Key in Settings.")
            return

        logger.info(f"UI initiating batch processing for {len(self.file_list)} files")
        
        # UI Feedback
        self.btn_process.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.btn_process.setText("⏳ Processing...")
        self.progress_bar.setVisible(True)
        self.loading_overlay.setGeometry(self.centralWidget().rect())
        self.loading_overlay.show()
        
        # Clear editors before starting
        self.hindi_editor.clear()
        self.english_editor.clear()

        # Initialize the Translator library
        translator = Translator(self.api_key, self.system_prompt)

        # Create and start the worker thread
        self.worker = TranslationWorker(translator, self.file_list)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

    def on_processing_finished(self, results):
        logger.info("Background processing finished successfully")
        try:
            for idx, result in enumerate(results):
                file_path = self.file_list[idx] if idx < len(self.file_list) else "Unknown"
                basename = os.path.basename(file_path)
                logger.debug(f"Displaying results for {basename}")
                
                if result:
                    if "error" in result:
                        logger.error(f"Error result received for {basename}: {result['error']}")
                        if "raw" in result:
                            logger.error(f"Full raw response for {basename} that failed to parse: {result['raw']}")
                        self.hindi_editor.append(f"\n[ERROR processing {basename}: {result['error']}]\n")
                        continue
                        
                    # Append Results
                    header = f"\n--- FILE: {basename} ---\n"
                    
                    # Hindi OCR
                    current_hindi = self.hindi_editor.toMarkdown()
                    self.hindi_editor.setMarkdown(current_hindi + header + result.get("hindi_ocr", ""))
                    
                    # English/IAST
                    current_english_markdown = self.english_editor.toMarkdown()
                    new_markdown = current_english_markdown + f"\n\n### File: {basename}\n\n" + result.get("english_translation", "")
                    self.english_editor.setMarkdown(new_markdown)
        except Exception as e:
            logger.exception(f"Error display results: {str(e)}")
            QMessageBox.critical(self, "Display Error", f"Error displaying results: {str(e)}")
        finally:
            self.finalize_processing()

    def on_processing_error(self, error_msg):
        logger.error(f"Background processing error: {error_msg}")
        QMessageBox.critical(self, "Processing Error", error_msg)
        self.finalize_processing()

    def finalize_processing(self):
        self.btn_process.setText("🚀 Start Processing")
        self.btn_process.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.loading_overlay.hide()

    def open_file_dialog(self):
        from PySide6.QtWidgets import QFileDialog
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Jain Books", "", "Images/PDF (*.png *.jpg *.jpeg *.pdf)")
        if file_paths:
            self.add_files(file_paths)

    def add_files(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        
        for p in paths:
            if p not in self.file_list:
                logger.info(f"Added file to list: {p}")
                self.file_list.append(p)
        
        self.update_drop_zone_text()

    def clear_files(self):
        self.file_list = []
        self.update_drop_zone_text()
        self.hindi_editor.clear()
        self.english_editor.clear()

    def update_drop_zone_text(self):
        if not self.file_list:
            self.drop_zone.setText("Drag & Drop PDF or Images Here\n(Click to browse)")
            self.drop_zone.set_default_style()
        elif len(self.file_list) == 1:
            self.drop_zone.setText(f"Selected: {os.path.basename(self.file_list[0])}")
            self.drop_zone.set_default_style()
        else:
            self.drop_zone.setText(f"Selected {len(self.file_list)} files")
            self.drop_zone.set_default_style()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay') and self.loading_overlay.isVisible():
            self.loading_overlay.setGeometry(self.centralWidget().rect())
