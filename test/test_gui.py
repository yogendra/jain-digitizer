import os
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from unittest.mock import MagicMock, patch
from jain_digitizer.app_window import JainDigitizer

@pytest.fixture
def app(qtbot):
    """Fixture to create the main window."""
    window = JainDigitizer()
    window.api_key = "fake_api_key" # Set a fake API key for testing
    qtbot.addWidget(window)
    return window

def test_main_window_initial_state(app):
    """Test that the main window initializes with default values."""
    assert app.windowTitle() == "Jain Digitizer"
    assert app.btn_process.text() == "🚀 Start Processing"
    assert app.hindi_editor.toPlainText() == ""
    assert app.english_editor.toPlainText() == ""

def test_main_window_single_file_operation(app, qtbot):
    """
    Test 1: Main Window Single File Operation
    - Add file
    - Click process
    - Check if editors are updated
    """
    test_file = "test_image.jpg"
    app.add_files([test_file])
    
    assert len(app.file_list) == 1
    assert os.path.basename(test_file) in app.drop_zone.text()
    
    mock_results = [{"hindi_ocr": "नमस्तस्यै", "english_translation": "Salutations to her"}]
    
    with patch("jain_digitizer.app_window.Translator.translate_files", return_value=mock_results):
        qtbot.mouseClick(app.btn_process, Qt.LeftButton)
        
    # Check if results are displayed
    assert "नमस्तस्यै" in app.hindi_editor.toMarkdown()
    assert "Salutations to her" in app.english_editor.toMarkdown()
    assert "FILE: test_image.jpg" in app.hindi_editor.toMarkdown()

def test_main_window_multiple_file_operation(app, qtbot):
    """
    Test 2: Main Window Multiple File Operation
    - Add multiple files
    - Click process
    - Check if editors are updated with both results
    """
    test_files = ["file1.jpg", "file2.jpg"]
    app.add_files(test_files)
    
    assert len(app.file_list) == 2
    assert "Selected 2 files" in app.drop_zone.text()
    
    mock_results = [
        {"hindi_ocr": "ocr1", "english_translation": "trans1"},
        {"hindi_ocr": "ocr2", "english_translation": "trans2"}
    ]
    
    with patch("jain_digitizer.app_window.Translator.translate_files", return_value=mock_results):
        qtbot.mouseClick(app.btn_process, Qt.LeftButton)
        
    # Check if both results are displayed
    hindi_content = app.hindi_editor.toMarkdown()
    english_content = app.english_editor.toMarkdown()
    
    assert "ocr1" in hindi_content
    assert "ocr2" in hindi_content
    assert "trans1" in english_content
    assert "trans2" in english_content
    assert "FILE: file1.jpg" in hindi_content
    assert "FILE: file2.jpg" in hindi_content

def test_clear_button(app):
    """Test the clear button functionality."""
    app.add_files(["test.jpg"])
    app.hindi_editor.setPlainText("some ocr")
    app.english_editor.setPlainText("some trans")
    
    app.clear_files()
    
    assert len(app.file_list) == 0
    assert app.hindi_editor.toPlainText() == ""
    assert app.english_editor.toPlainText() == ""
    assert "Drag & Drop" in app.drop_zone.text()

def test_process_no_files_warning(app, qtbot):
    """Test that a warning is shown if process is clicked with no files."""
    with patch.object(QMessageBox, 'warning') as mock_warning:
        qtbot.mouseClick(app.btn_process, Qt.LeftButton)
        mock_warning.assert_called_once()
        assert "No Files" in mock_warning.call_args[0][1]

def test_process_no_api_key_error(app, qtbot):
    """Test that an error is shown if process is clicked with no API key."""
    app.api_key = ""
    app.add_files(["test.jpg"])
    with patch.object(QMessageBox, 'critical') as mock_critical:
        qtbot.mouseClick(app.btn_process, Qt.LeftButton)
        mock_critical.assert_called_once()
        assert "Error" in mock_critical.call_args[0][1]
