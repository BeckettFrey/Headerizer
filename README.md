# Headerizer
![Run Tests](https://github.com/BeckettFrey/Headerizer/actions/workflows/test.yml/badge.svg)

**headerizer** is an experimental command-line utility that automatically adds file path headers to source files. It's ideal for maintaining clear provenance in large or multi-language projects by embedding the file's location directly into its contents using appropriate comment syntax.

> **Experimental**: Install in development mode and use at your own discretion.

---

## Benefits for AI-Assisted Development

Adding file path headers improves **context awareness** when using AI tools and large language models.

> By embedding the file's location, AI can make more accurate inferences about project structure and intent.

- Responses can be tailored based on file roles (e.g., tests, configs, utilities)
- File-specific conversations become easier and more meaningful
- Enhanced code understanding in modern AI-integrated development environments

---

## Supported File Types

Headerizer supports the following languages (and more):

- **Python**, **JavaScript**, **TypeScript**, **Java**, **C/C++**, **C#**
- **PHP**, **Ruby**, **Go**, **Rust**, **Shell**, **SQL**
- **R**, **MATLAB**, **Swift**, **Kotlin**

> 📋 Configurations are defined in `config.json` and can be extended.

---

## Installation

To install Headerizer for ongoing usage, it's recommended to use [pipx](https://pipxproject.github.io/pipx/):

```bash
pipx install git+https://github.com/BeckettFrey/Headerizer.git
```

For development or local testing:

```bash
git clone https://github.com/BeckettFrey/Headerizer.git
cd Headerizer
pip install -e .
```

---

## Quick Start

```bash
headerizer [options] [directory]
```

### Options

- `-r`, `--relative` – Use paths relative to the Git root in headers
- `-p`, `--print` – Print each file that a header was added to
- `-h`, `--help` – Show help message and exit

> If no directory is specified, Headerizer defaults to the current directory.

### Example

```bash
# Process all supported files under src/ with Git-relative paths
headerizer -rp src/
```

### Example workflow:

```bash
❯ headerizer -rp src/
🔍 Scanning files in src/...
📝 Found 15 files to process
⚠️ Proceed with header insertion? (y/N): y
✅ Added headers to 15 files
```

---


## Confirmation Prompt

Before modifying any files, Headerizer will display how many files are targeted for update and prompt you to confirm the operation:

```
⚠️ Proceed with header insertion? (y/N):
```

> **Smart Updates:** Headerizer intelligently checks for existing headers before making changes. Files that already have headers will only be updated if you're switching between relative and absolute path formats.

---

## Ignoring Files and Directories

### Project-Level Ignore

Add a `.headerignore` file to any project root with glob patterns:

```
node_modules
*.min.js
build
```

> **Note:** Do **not** include a trailing slash for directories (e.g., use `node_modules` instead of `node_modules/`).

### Global Defaults

Modify the `default_ignore` section in `config.json` before building/installing the package to control which files/directories are always skipped.

---

## Configuration

The `config.json` file defines:

- Supported file types and extensions
- Comment prefixes per language
- Default ignore patterns

> You can edit this file to support additional languages or tweak header behavior.

---

## Roadmap

Upcoming features for Headerizer:

* Add coverage reporting and badges
* Additional safety checks (e.g., dry-run mode)
* Distribute via PyPI for easier install (`pip install headerizer`)
* VSCode extension integration (long-term)

---

## Contributing

Ideas, PRs, and feature requests welcome! This project is in active development.

**Current Status**: Core functionality is working, but the project is experimental and evolving.

For development:

```bash
# Clone the repository
git clone https://github.com/BeckettFrey/Headerizer.git
cd Headerizer

# Install in editable development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

---

## License

This project is licensed under the MIT License.
