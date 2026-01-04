import os

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_prompt():
  # Move up one level to find the prompt file in src/jain_digitizer/  
  prompt_path = os.environ.get("PROMPT_FILE", os.path.join(BASE_DIR, "prompt-html.md"))
  if os.path.exists(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
      return f.read()
  raise FileNotFoundError("Prompt file not found")

DEFAULT_PROMPT = load_prompt()
