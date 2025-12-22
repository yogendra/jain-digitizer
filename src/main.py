import sys
import json
import os
import fitz  # PyMuPDF
import asyncio
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QFileDialog, QSplitter, QDialog, QFormLayout, 
                             QLineEdit, QMessageBox, QToolBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor, QAction, QIcon
from google import genai
from google.genai import types
from rich_editor import MarkdownRichEditor

# Default Philological Prompt
DEFAULT_PROMPT = """# Role: Philological Digitization Agent
You are an expert agent specializing in the high-accuracy OCR, transcription, and translation of **Hindi, Sanskrit, and Prakrit** texts. Your goal is to digitize manuscript images into a structured JSON format with rich Markdown formatting for easy review.

---

## 🛠 STRICT OPERATING CONSTRAINTS
1. **Hermetic Translation:** Use ONLY the text physically visible in the provided image. Do NOT use external knowledge.
2. **No Meta-Talk:** Do not provide introductions, summaries, or conversational filler.
3. **No Follow-up:** Do not offer research lookups or external links.
4. **Output Integrity:** Transcription must be character-perfect (Devanagari).

## 📖 LAYOUT & OCR RULES
1. **Column Logic:** Process the Left Column top-to-bottom, then the Right Column.
2. **Spatial Correction:** Automatically handle page curvature or slight rotations.
3. **Exclusions:** Ignore page numbers, repetitive headers, or unrelated marginalia.

## 📝 OUTPUT STRUCTURE (JSON)
You must return a **VALID JSON object**. Do not include markdown code blocks (like ```json).

### JSON Schema:
{
  "hindi_ocr": "Markdown formatted Devanagari transcription.",
  "english_translation": "Markdown formatted scholarly interpretation & transliteration."
}

## 🎨 FORMATTING GUIDELINES (Applied to both fields)

### 0. FILE TRACKING (Required)
- **Header:** Both fields MUST start with `# [Sequence Number] File: Filename` on the first line.

### 1. HINDI OCR (`hindi_ocr`)
- **Headers:** Use `### Left Column` and `### Right Column` to indicate layout.
- **Verses:** Use `>` blockquotes for Sanskrit/Prakrit verses found within the text.
- **Line Breaks:** Preserve line breaks as they appear in the manuscript.

### 2. ENGLISH TRANSLATION (`english_translation`)
- **HINDI BLOCKS:** Provide a fluent, formal English translation.
- **SANSKRIT/PRAKRIT BLOCKS:**
  1. **Devanagari:** The original verse in a `>` blockquote.
  2. A separator line: `---`
  3. **Transliteration:** Use **IAST** with full diacritics (ā, ī, ū, ṛ, ś, ṣ, ṭ, ṇ, ḥ, ṃ).
  4. **Translation:** The English meaning directly below.
- **TECHNICAL TERMS:** Use **bold** for technical Sanskrit/Prakrit terms.
- **FOOTNOTES:** List at the bottom under a `### Footnotes` header.

## 🏁 FINAL CHECK
- The very first line of both fields must be the `# [X] File: name` header.
- Use `##` for major section headers if multiple sections exist.
- Ensure all Devanagari is character-accurate.
- Ensure IAST is philologically correct."""

class SettingsDialog(QDialog):
    def __init__(self, parent=None, api_key="", prompt=""):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(800, 600)
        self.layout = QFormLayout(self)
        
        self.api_key_input = QLineEdit(api_key)
        self.api_key_input.setPlaceholderText("Enter your Gemini API Key")
        
        # System Prompt is now a Rich Text Editor supporting Markdown
        self.prompt_input = QTextEdit()
        self.prompt_input.setAcceptRichText(True)
        self.prompt_input.setMarkdown(prompt)
        self.prompt_input.setPlaceholderText("Enter the system prompt instructions in Markdown...")
        self.prompt_input.setMinimumHeight(400)
        
        self.layout.addRow("Gemini API Key:", self.api_key_input)
        self.layout.addRow("System Prompt (Markdown):", self.prompt_input)
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.save_btn)

class FileDropZone(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.set_default_style()

    def set_default_style(self):
        # Check if we have files already to decide which style to show
        if hasattr(self.window(), 'file_list') and self.window().file_list:
            self.setStyleSheet("""
                QLabel {
                    border: 3px solid #2ecc71;
                    border-radius: 12px;
                    background-color: #e8f5e9;
                    font-size: 16px;
                    color: #2e7d32;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 3px dashed #666;
                    border-radius: 12px;
                    background-color: #f0f0f0;
                    font-size: 16px;
                    color: #444;
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

class JainDigitizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jain Vani Digitizer")
        self.resize(1200, 900)
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.jpg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # App State
        self.api_key = ""
        self.system_prompt = DEFAULT_PROMPT
        self.file_list = []
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Pane ---
        top_pane = QWidget()
        top_pane.setMaximumHeight(200)
        top_layout = QVBoxLayout(top_pane)
        
        self.drop_zone = FileDropZone("Drag & Drop PDF or Images Here\n(Click to browse)")
        top_layout.addWidget(self.drop_zone)
        
        btn_layout = QHBoxLayout()
        self.btn_process = QPushButton("🚀 Start Processing")
        self.btn_process.setFixedHeight(40)
        self.btn_process.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        self.btn_process.clicked.connect(self.process_file)
        
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.setFixedWidth(100)
        self.btn_settings.clicked.connect(self.open_settings)

        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.setFixedWidth(100)
        self.btn_clear.clicked.connect(self.clear_files)
        
        btn_layout.addWidget(self.btn_process)
        btn_layout.addWidget(self.btn_settings)
        btn_layout.addWidget(self.btn_clear)
        top_layout.addLayout(btn_layout)

        # --- Workspace ---
        splitter = QSplitter(Qt.Horizontal)
        self.hindi_editor = MarkdownRichEditor("HINDI OCR (SOURCE)...")
        self.english_editor = MarkdownRichEditor("SCHOLARLY MANUSCRIPT (ENGLISH & IAST)...")

        splitter.addWidget(self.hindi_editor)
        splitter.addWidget(self.english_editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(top_pane)
        main_layout.addWidget(splitter)

    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key", "")
                    # Note: We store the prompt as Markdown (plain text), 
                    # but display it as rich text in the editor.
                    self.system_prompt = data.get("prompt", DEFAULT_PROMPT)
            except: pass

    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump({"api_key": self.api_key, "prompt": self.system_prompt}, f)

    def open_settings(self):
        # Pass the plain Markdown string to the dialog
        diag = SettingsDialog(self, self.api_key, self.system_prompt)
        if diag.exec():
            self.api_key = diag.api_key_input.text()
            # Capture the Markdown version of the edited prompt
            self.system_prompt = diag.prompt_input.toMarkdown()
            self.save_settings()

    def get_gemini_response(self, content_bytes, mime_type, user_text=""):
        if not self.api_key:
            QMessageBox.critical(self, "Error", "Please provide a Gemini API Key in Settings.")
            return None
        
        try:
            client = genai.Client(api_key=self.api_key)
            model = "gemini-2.0-flash"
            config =types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    response_mime_type="application/json"
                )
            contents = [
                    types.Part.from_bytes(data=content_bytes, mime_type=mime_type),
                    types.Part.from_text(text=user_text)
                ]
            response = client.models.generate_content(
                model=model,
                config=config,
                contents=contents                
            )
            
            return json.loads(response.text)
        except Exception as e:
            QMessageBox.critical(self, "API Error", str(e))
            return None

    def process_file(self):
        if not self.file_list:
            QMessageBox.warning(self, "No Files", "Please select or drop files first.")
            return

        self.btn_process.setEnabled(False)
        self.btn_clear.setEnabled(False)
        
        # Clear editors before starting
        self.hindi_editor.clear()
        self.english_editor.clear()

        try:
            for idx, file_path in enumerate(self.file_list):
                self.btn_process.setText(f"⏳ Processing {idx+1}/{len(self.file_list)}...")
                QApplication.processEvents()
                
                try:
                    basename = os.path.basename(file_path)
                    
                    if file_path.lower().endswith('.pdf'):
                        with open(file_path, "rb") as f:
                            content_data = f.read()
                        mime_type = "application/pdf"
                    else:
                        ext = file_path.lower().split('.')[-1]
                        if ext in ['jpg', 'jpeg']:
                            mime_type = "image/jpeg"
                        elif ext == 'png':
                            mime_type = "image/png"
                        else:
                            mime_type = f"image/{ext}" # Best effort
                            
                        with open(file_path, "rb") as f:
                            content_data = f.read()

                    result = self.get_gemini_response(
                        content_data, 
                        mime_type,
                        user_text=f"Sequence: {idx + 1}, Filename: {basename}"
                    )
                    
                    if result:
                        # Append Results
                        header = f"\n--- FILE: {basename} ---\n"
                        
                        # Hindi OCR
                        current_hindi = self.hindi_editor.toMarkdown()
                        self.hindi_editor.setMarkdown(current_hindi + header + result.get("hindi_ocr", ""))
                        
                        # English/IAST
                        # We use Markdown, so we append to the existing content
                        current_english_markdown = self.english_editor.toMarkdown()
                        new_markdown = current_english_markdown + f"\n\n### File: {basename}\n\n" + result.get("english_translation", "")
                        self.english_editor.setMarkdown(new_markdown)
                        
                except Exception as e:
                    self.hindi_editor.append(f"\n[ERROR processing {file_path}: {str(e)}]\n")
                
        finally:
            self.btn_process.setText("🚀 Start Processing")
            self.btn_process.setEnabled(True)
            self.btn_clear.setEnabled(True)

    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Jain Books", "", "Images/PDF (*.png *.jpg *.jpeg *.pdf)")
        if file_paths:
            self.add_files(file_paths)

    def add_files(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        
        # Add new files and remove duplicates
        for p in paths:
            if p not in self.file_list:
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
            # This will trigger the success style
            self.drop_zone.set_default_style()
        else:
            self.drop_zone.setText(f"Selected {len(self.file_list)} files")
            self.drop_zone.set_default_style()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JainDigitizer()
    window.show()
    sys.exit(app.exec())
