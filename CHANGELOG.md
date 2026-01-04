# Changelog

All notable changes to the Jain Digitizer project will be documented in this file.

## [Unreleased] - 2026-01-04

### Changed

- **Taskfile Simplification**:
  - Replaced Python-based `build-prep` with a simplified multi-line Bash script using `sed`.
  - Removed manual `publish-pip` and `publish-conda` tasks as publishing is currently deferred.
  - Updated `trigger-release` to include a safety check for uncommitted changes.
- **Documentation Overhaul**:
  - Updated `README.md` and `DEVELOPMENT.md` to reflect the pivot from package managers (Pip/Conda) to executable-based distribution.
  - Simplified developer setup and testing instructions using `task` commands.

## [0.21] - 2025-12-22

### Added

- **Centralized Logging System**:
  - Created `src/logger_setup.py` for uniform logging across the app.
  - Integrated `rich` for colorized terminal output with timestamps and line numbers.
  - Implemented automatic file logging to a `logs/` directory with rotating handlers.
- **Improved Gesture Support**:
  - Added native Mac trackpad pinch-to-zoom support for all rich text editors.
  - Added `Ctrl/Cmd + Scroll wheel` support for zooming in the editors.
- **Enhanced Settings UI**:
  - Added "Show/Hide" toggle for the Gemini API Key field.
  - Upgraded the System Prompt field to use the full `MarkdownRichEditor`.
- **Batch Translation Support**:
  - The new `Translator` library now sends multiple files in a single Gemini API call for better speed and context maintenance.

### Changed

- **Codebase Refactoring**:
  - Extracted UI components into dedicated files: `app_window.py`, `settings_dialog.py`, `file_drop_zone.py`.
  - Decoupled logic: Created `translator.py` as a standalone, non-UI library for Gemini API interactions.
  - Minimal `main.py` now serves as the clean entry point.
- **UI Redesign**:
  - Reorganized the main window header: Control buttons are now positioned symmetrically next to the dropzone to save vertical space.
  - Improved `SettingsDialog` layout: Fields are now vertically stacked and use the full dialog width.
- **Rich Editor Enhancements**:
  - Pasting text now automatically renders as Markdown.
  - Replaced font size dropdown with intuitive "A+" and "A-" zoom controls.
- **Version Control & Environment**:
  - Added comprehensive `.gitignore` rules for Python, macOS, and VS Code.
  - Updated `environment.yml` with the `rich` library dependency.

### Fixed

- Resolved `AttributeError` when accessing `self.editor` during toolbar initialization.
- Fixed `NameError` in the gesture event handler.
- Corrected trackpad zoom directionality to match natural Mac behavior.
- Improved API error handling by logging raw responses when JSON decoding fails.
