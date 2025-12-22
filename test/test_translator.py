import pytest
from unittest.mock import MagicMock, patch
from jain_digitizer.common.translator import Translator

def test_translator_initialization():
    translator = Translator(api_key="test_key", system_prompt="test_prompt")
    assert translator.api_key == "test_key"
    assert translator.system_prompt == "test_prompt"
    assert translator.model == "gemini-2.0-flash"

@patch("google.genai.Client")
def test_translate_single_file(mock_client_class):
    # Setup mock client and response
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = '{"hindi_ocr": "नमस्तस्यै", "english_translation": "Salutations to her"}'
    mock_client.models.generate_content.return_value = mock_response
    
    translator = Translator(api_key="test_key", system_prompt="test_prompt")
    
    # We need a dummy file to test
    with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b"fake data")))))):
        results = translator.translate_files(["test.jpg"])
    
    assert len(results) == 1
    assert results[0]["hindi_ocr"] == "नमस्तस्यै"
    assert results[0]["english_translation"] == "Salutations to her"
    
    # Verify client was called with correct parameters
    mock_client.models.generate_content.assert_called_once()
    args, kwargs = mock_client.models.generate_content.call_args
    assert kwargs['model'] == "gemini-2.0-flash"
    assert "test_prompt" in kwargs['config'].system_instruction
    assert "Return a single JSON object" in kwargs['config'].system_instruction

@patch("google.genai.Client")
def test_translate_multiple_files(mock_client_class):
    # Setup mock client and response
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = '[{"hindi_ocr": "file1", "english_translation": "trans1"}, {"hindi_ocr": "file2", "english_translation": "trans2"}]'
    mock_client.models.generate_content.return_value = mock_response
    
    translator = Translator(api_key="test_key", system_prompt="test_prompt")
    
    with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=b"fake data")))))):
        results = translator.translate_files(["test1.jpg", "test2.jpg"])
    
    assert len(results) == 2
    assert results[0]["hindi_ocr"] == "file1"
    assert results[1]["hindi_ocr"] == "file2"
    
    # Verify client was called with correct parameters for multiple files
    mock_client.models.generate_content.assert_called_once()
    args, kwargs = mock_client.models.generate_content.call_args
    assert "Return a JSON ARRAY of objects" in kwargs['config'].system_instruction

def test_translator_no_api_key():
    translator = Translator(api_key="", system_prompt="test_prompt")
    with pytest.raises(ValueError, match="Gemini API Key is not set"):
        translator.translate_files(["test.jpg"])
