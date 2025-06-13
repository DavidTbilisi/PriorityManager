# 📋 Priority Manager

**Priority Manager** is a Command-Line Interface (CLI) tool for managing tasks with priorities, statuses, tags, and due dates. It's designed to help you organize and prioritize your tasks efficiently with ease of use and flexibility.

---

## 🚀 Features

- **Add Tasks**: Create tasks with descriptions, priorities, due dates, tags, and statuses.
- **Edit Tasks**: Modify existing tasks interactively.
- **List Tasks**: Display tasks sorted by priority, with optional filtering by status or tags.
- **Search and Filter**: Search tasks by keywords or filter them by status and tags.
- **Export Tasks**: Export tasks to various formats, including CSV, JSON, and YAML.
- **Archive Tasks**: Archive completed tasks to keep your workspace clean.
- **Sync with Microsoft To Do**: Synchronize tasks with a dedicated list in Microsoft To Do.
- **Task Completion**: Mark tasks as complete or reopen them if needed.
- **Configurable**: Customize task directories and settings through a configuration file (`config.yaml`).

---

## 📦 Installation

You can install **Priority Manager** from PyPI:

```bash
pip install priority-manager
```

Or upgrade 
```bash
pip install --upgrade priority-manager
```

### Update `pip` if Necessary

```bash
pip install --upgrade pip
```

---

## 🛠️ Usage

After installation, you can use the `priority-manager` command. Here are some basic commands:

### General Help

```bash
priority-manager --help
```

### Add a Task

```bash
priority-manager add "Finish the report"
```

You'll be prompted to provide additional details such as priority, description, due date, tags, and status.

### List Tasks

```bash
priority-manager ls
```

List all tasks sorted by priority.

#### Filter by Status

```bash
priority-manager ls --status "In Progress"
```

### Edit a Task

```bash
priority-manager edit
```

You’ll be prompted to select a task and edit its details interactively.

### Complete a Task

```bash
priority-manager complete
```

Mark a task as completed.

### Archive Tasks

```bash
priority-manager archive
```

Move completed tasks to the archive directory.

### Export Tasks

Export tasks to CSV, JSON, or YAML:

```bash
priority-manager export --format csv
```

Available formats: `csv`, `json`, `yaml`.

### Sync with Microsoft To Do

Synchronize local tasks with your Microsoft To Do list. Set the `MS_TODO_TOKEN` environment variable with a valid Microsoft Graph token before running:

```bash
priority-manager sync
```

---

## ⚙️ Configuration

### `config.yaml`

The tool uses a `config.yaml` file for customizable settings. The default `config.yaml` looks like this:

```yaml
directories:
  tasks_dir: "tasks"
  archive_dir: "archive"
  test_tasks_dir: "tests/test_tasks"
  test_archive_dir: "tests/test_archive"

statuses:
  - "To Do"
  - "In Progress"
  - "Blocked"
  - "Complete"
  - "Archived"

export_files:
  csv: "tasks_export.csv"
  json: "tasks_export.json"
  yaml: "tasks_export.yaml"

defaults:
  description: "No description"
  due_date: "No due date"
  tags: ""
  status: "To Do"
```

---

## 🧪 Testing

Run tests using `pytest`:

```bash
TEST_MODE=true pytest
```

Ensure all dependencies are installed:

```bash
pip install pytest
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the Repository**.
2. **Create a New Branch**: `git checkout -b feature-name`.
3. **Make Changes and Commit**: `git commit -m "Add new feature"`.
4. **Push to the Branch**: `git push origin feature-name`.
5. **Create a Pull Request**.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 📝 Author

**David Chincharashvili**  
Email: [davidchincharashvili@gmail.com](mailto:ydavidchincharashvili@gmail.com)  
GitHub: [davidtbilisi](https://github.com/davidtbilisi)

---

## 🌟 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI functionality.
- YAML parsing powered by [PyYAML](https://pyyaml.org/).

