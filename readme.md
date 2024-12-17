# Priority Manager CLI

A command-line tool for managing tasks with features like adding, editing, listing, searching, filtering, exporting to CSV, and archiving tasks. Designed for compatibility with **Obsidian.md** by storing tasks in Markdown files.

### Project Structure

```
priority_manager/
├── main.py
├── commands/
│   ├── __init__.py
│   ├── add.py
│   ├── edit.py
│   ├── list_tasks.py
│   ├── export_csv.py
│   └── search_filter.py
└── utils/
    ├── __init__.py
    ├── helpers.py
    └── logger.py
```

### Features

1. **Add Task**: Add a new task with a calculated priority, description, and due date.
2. **Edit Task**: Edit task details (name, description, due date, and priority).
3. **List Tasks**: List tasks sorted by priority score.
4. **Search Tasks**: Search tasks by keyword.
5. **Filter Tasks**: Filter tasks by a specified priority range.
6. **Export to CSV**: Export all tasks to a CSV file.
7. **Archive Task**: Move tasks to an archive folder instead of deleting them.
8. **Logging**: All actions are logged in `log.txt`.

---

### Installation

1. **Clone the Repository**:

   ```bash
   git clone <repository_url>
   cd priority_manager
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install click
   ```

---

### Usage

Activate the virtual environment if it's not already active:

```bash
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

Run the `main.py` script followed by the desired command.

#### 1. **Add a Task**

```bash
python main.py add "Task Name"
```

You'll be prompted to enter:
- **Urgency** (1-5)
- **Importance** (1-5)
- **Effort** (1-5)
- **Description**
- **Due Date** (YYYY-MM-DD)

#### 2. **Edit a Task**

```bash
python main.py edit
```

Select the task you want to edit and update the details as prompted.

#### 3. **List Tasks**

```bash
python main.py list-tasks
```

Lists all tasks sorted by their priority score.

#### 4. **Search Tasks by Keyword**

```bash
python main.py search <keyword>
```

Example:

```bash
python main.py search urgent
```

#### 5. **Filter Tasks by Priority Range**

```bash
python main.py filter-tasks --min-priority 10 --max-priority 20
```

#### 6. **Export Tasks to CSV**

```bash
python main.py export-csv
```

Exports all tasks to `tasks_export.csv`.

#### 7. **Archive a Task**

```bash
python main.py archive
```

Moves the selected task to the `archive` folder.

---

### Directory Structure

- **Tasks** are stored in the `tasks` directory as Markdown (`.md`) files.
- **Archived Tasks** are moved to the `archive` directory.
- **Logs** are saved in `log.txt`.

---

### Example Task File Format

```markdown
# Task Title

**Description:** This is a sample task description.

**Priority Score:** 15

**Due Date:** 2024-12-31

**Date Added:** 2024-06-01T14:30:00

**Status:** Incomplete
```

---

### License

This project is licensed under the MIT License.
