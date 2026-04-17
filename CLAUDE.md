# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Priority Manager is a Python CLI tool for managing markdown-based tasks with priorities, statuses, tags, and due dates. It supports Microsoft To Do sync, Gantt chart export, multi-folder organization, and CSV/JSON/YAML export.

## Commands

### Development
```bash
pip install -e .                  # Install locally in editable mode
./rebuild.sh --local              # Build and install locally
./rebuild.sh --prod               # Bump version, build, upload to PyPI
```

### Testing
```bash
TEST_MODE=true pytest                                    # Run all tests
TEST_MODE=true pytest priority_manager/tests/test_add.py # Run a single test file
TEST_MODE=true pytest -k "test_add_task"                 # Run a single test by name
```

### Versioning & Release
```bash
bumpversion patch                  # Bump patch version (updates .bumpversion.cfg and setup.py)
python setup.py sdist bdist_wheel  # Build distributions
twine check dist/*                 # Validate
twine upload dist/*                # Upload to PyPI
```

## Architecture

### Entry Point
`priority_manager/main.py` — Click CLI group that registers all subcommands.

### Command Modules (`priority_manager/commands/`)
Each command is a standalone Click command registered in `main.py`:
- `add.py` — Create tasks; calculates priority via `(urgency×2) + (importance×3) - effort`
- `ls.py` — List/filter tasks recursively across subfolders, sorted by priority
- `edit.py` — Interactive task editing
- `archive.py` — Move completed tasks to archive directory
- `export.py` — Export to CSV/JSON/YAML
- `gantt.py` — Plotly-based Gantt chart generation
- `todo.py` — Microsoft To Do sync (push/pull via MS Graph API)
- `auth.py` — MSAL device code flow authentication and cache management
- `search_filter.py` — Filter tasks by keyword, status, tags
- `conf.py` — Open config file for editing

### Core Utilities (`priority_manager/utils/`)
- `config.py` — Loads `config.yaml`; detects `TEST_MODE` env var and switches to test directories
- `helpers.py` — Task parsing from markdown, priority display, directory traversal, file movement
- `ms_todo.py` — Microsoft Graph API client; supports MSAL device flow + legacy env/config tokens
- `logger.py` — Action logging

### Data Model
Tasks are stored as individual markdown files with key-value lines:
```
Name: Task Title
Description: Optional description
Priority Score: 12
Due Date: 2026-05-01
Tags: work, urgent
Status: To Do
Date Added: 2026-04-17
```

Active tasks live in `tasks/` (or subfolders like `tasks/Work/`); archived in `archive/`.

### Configuration
`priority_manager/config.yaml` — All settings: directory paths, status definitions, export naming, display columns, MS To Do credentials, Gantt chart height.

### Microsoft To Do Authentication
Three methods tried in order:
1. Env var `MS_TODO_TOKEN`
2. `ms_todo.token` in `config.yaml`
3. MSAL device code flow (interactive; caches to `.msal_token_cache.json`)

### Testing Pattern
- `TEST_MODE=true` switches config to use test directories (`test_tasks/`, `test_archive/`)
- `conftest.py` provides fixtures for directory setup/teardown and test isolation
- Tests are function-scoped; each test cleans up its own files
