import os
import json
from google import genai
from google.genai import types
from jain_digitizer.common.logger_setup import logger

class Translator:
    """
    A non-UI library class that handles communication with the Gemini API
     for OCR and translation of philological texts.
    """
    def __init__(self, api_key, system_prompt):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.model = "gemini-2.0-flash"
        logger.debug(f"Translator initialized with model: {self.model}")

    def translate_files(self, file_paths):
        """
        Takes a list of file paths and sends them all to Gemini in a single request.
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        parts = []
        for idx, path in enumerate(file_paths):
            logger.debug(f"Preparing file {idx+1}: {path}")
            mime_type = self._get_mime_type(path)
            with open(path, "rb") as f:
                data = f.read()
            parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))
            parts.append(types.Part.from_text(text=f"File {idx+1}: {os.path.basename(path)}"))
        
        return self._generate(parts, len(file_paths))

    def translate_bytes(self, files_data):
        """
        Takes a list of (bytes, filename, mime_type) tuples.
        """
        parts = []
        for idx, (data, filename, mime_type) in enumerate(files_data):
            parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))
            parts.append(types.Part.from_text(text=f"File {idx+1}: {filename}"))
        
        return self._generate(parts, len(files_data))

    def _generate(self, parts, num_files):
        if not self.api_key:
            logger.error("Attempted to translate without API key")
            raise ValueError("Gemini API Key is not set.")

        logger.info(f"Starting translation for {num_files} files")
        client = genai.Client(api_key=self.api_key)
        
        # Update prompt to handle multiple files if needed
        instruct = self.system_prompt
        if num_files > 1:
            instruct += "\n\nCRITICAL: You are processing multiple files. Return a JSON ARRAY of objects, one for each file in the same order."
        else:
            instruct += "\n\nReturn a single JSON object for the file."

        config = types.GenerateContentConfig(
            system_instruction=instruct,
            response_mime_type="application/json"
        )
        
        logger.debug("Calling Gemini API...")
        response = client.models.generate_content(
            model=self.model,
            config=config,
            contents=parts
        )

        
        raw_response = response.text
        logger.debug(f"Received raw response from Gemini: {raw_response}")
        
        try:
            results = json.loads(raw_response)
            logger.info("Successfully received and parsed Gemini response")
            # Ensure it's a list if multiple files were sent
            if num_files >= 1 and not isinstance(results, list):
                logger.warning("Expected list from API but got single object; wrapping in list")
                return [results]
            return results if isinstance(results, list) else [results]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from Gemini. Error: {str(e)}\nRaw Response Content: {raw_response}")
            return [{"error": f"Invalid JSON response from API: {str(e)}", "raw": raw_response}]

    def _get_mime_type(self, file_path):
        """Determines the MIME type based on file extension."""
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            return "application/pdf"
        elif ext in ['jpg', 'jpeg']:
            return "image/jpeg"
        elif ext == 'png':
            return "image/png"
        else:
            return f"image/{ext}"  # Best effort
