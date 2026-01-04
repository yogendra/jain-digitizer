# Developer Guide 🛠️

This document provides instructions for developers who want to contribute to Jain Digitizer or run it from source.

## 🏗️ Development Setup

### 1. Prerequisites

- **Conda** (Miniconda or Anaconda)
- **Gemini API Key**: Obtain one from the [Google AI Studio](https://aistudio.google.com/).
- **Task**: We use [go-task](https://taskfile.dev/) for automation.

### 2. Setup Development Environment

Clone the repository and set up the environment:

```bash
git clone https://github.com/yogendra/jain-digitizer.git
cd jain-digitizer
conda env create -f environment.yml
conda activate jain-digitizer
pip install -e .
```

### 3. Running for Development

Use `task` to run the application in development mode:

```bash
task run
```

## 🚀 Publishing Updates

Once you've made changes and updated the version in `pyproject.toml` and `src/jain_digitizer/__init__.py`:

```bash
# To publish to Pip
task publish-pip

# To publish to Conda
task publish-conda
```

## 🛠️ Contributing

We welcome contributions! To get started:

1. **Fork the Repository**
2. **Implement your changes**
3. **Run tests** (Ensure you have the `test` dependencies installed):
   ```bash
   pip install -e ".[test]"
   pytest
   ```
4. **Submit a Pull Request**

---

Return to [README.md](../README.md)
