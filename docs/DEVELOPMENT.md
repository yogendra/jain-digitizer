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
task setup-dev
```

### 3. Running for Development

Use `task` to run the application in development mode:

```bash
task run
```

## 🚀 Releasing a New Version

The release process is automated via GitHub Actions. To trigger a new release:

1.  **Commit Your Changes**:
    Ensure all your changes are committed to the repository. The release task will fail if there are uncommitted changes.

2.  **Run the trigger-release task**:
    This will calculate the next version based on the last tag and push a new tag to GitHub.

    ```bash
    task trigger-release
    ```

3.  **Wait for the Build**:
    GitHub Actions will see the new tag and start building the executables for Windows, Mac, and Linux. The version information will be automatically injected into the application and `pyproject.toml` during the build process.

## 🛠️ Contributing

We welcome contributions! To get started:

1. **Fork the Repository**
2. **Implement your changes**
3. **Run tests**:
   ```bash
   task test
   ```
4. **Submit a Pull Request**

---

Return to [README.md](../README.md)
