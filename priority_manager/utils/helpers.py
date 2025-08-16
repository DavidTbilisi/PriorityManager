import os
import re
from ..utils.config import CONFIG
from tabulate import tabulate
import click
from rich.pretty import pprint
import shutil

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]
TABLE_CONFIG = CONFIG["table"]["columns"]

def truncate(text, length):
    """Truncate text to the given length with ellipses if necessary."""
    return (text[:length] + "...") if len(text) > length else text

def ensure_dirs():
    # Refresh directories each call to respect test mutations to CONFIG
    global TASKS_DIR, ARCHIVE_DIR
    TASKS_DIR = CONFIG["directories"]["tasks_dir"]
    ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

def calculate_priority():
    urgency = click.prompt("Enter urgency (1-5, 5 = most urgent)", type=int, default=3)
    importance = click.prompt("Enter importance (1-5, 5 = most important)", type=int, default=3)
    effort = click.prompt("Enter effort (1-5, 5 = most effort required)", type=int, default=3)
    return urgency * 2 + importance * 3 - effort

def files_to_tasks(files=None, selected_status=None, recursive=False, suppress_empty_message=False):
    """Return a list of task detail dicts for provided filenames or by scanning tasks dir.

    If recursive=True, walk subdirectories under tasks_dir.
    """
    tasks = []
    base_dir = CONFIG["directories"]["tasks_dir"]
    if recursive and files is None:
        for root, _, filenames in os.walk(base_dir):
            for fname in filenames:
                path = os.path.join(root, fname)
                if not os.path.isfile(path):
                    continue
                task_details = get_task_details(path)
                if selected_status is None or task_details["Status"].lower() == selected_status.lower():
                    tasks.append(task_details)
    else:
        if files is None:
            files = os.listdir(base_dir) if os.path.isdir(base_dir) else []
        for file in files:
            filepath = os.path.join(base_dir, file)
            if not os.path.isfile(filepath):
                continue
            task_details = get_task_details(filepath)
            if selected_status is None or task_details["Status"].lower() == selected_status.lower():
                tasks.append(task_details)

    if not tasks and not suppress_empty_message:
        click.secho(
            f"No tasks found with status: {selected_status}" if selected_status else "No tasks found.",
            fg="yellow",
        )
    return tasks

def show_tasks(tasks):
    """Display tasks in a table sorted by priority."""
    tasks.sort(key=lambda x: x["Priority Score"], reverse=True)
    headers = [col["name"] for col in TABLE_CONFIG]
    table_rows = []
    for idx, task in enumerate(tasks, 1):
        row: list = [idx]
        for col in TABLE_CONFIG:
            column_name = col["name"]
            max_length = col["max_length"]
            cell_value = task.get(column_name, "")
            row.append(truncate(str(cell_value), max_length))
        table_rows.append(row)
    headers.insert(0, "#")
    click.echo(tabulate(table_rows, headers=headers, tablefmt="github"))
    return tasks

def get_sorted_files(dir=None, by="Priority Score"):
    """Return list of files in directory sorted descending by given field parsed from task details."""
    if dir is None:
        dir = CONFIG["directories"]["tasks_dir"]
    files = os.listdir(dir)
    files.sort(key=lambda x: get_task_details(os.path.join(dir, x))[by], reverse=True)
    return files

def move_to_archive(files, choice):
    """Move the chosen file index from tasks to archive directory."""
    current_tasks_dir = CONFIG["directories"]["tasks_dir"]
    current_archive_dir = CONFIG["directories"]["archive_dir"]
    src = os.path.join(current_tasks_dir, files[choice - 1])
    dest = os.path.join(current_archive_dir, files[choice - 1])
    shutil.move(src, dest)
    return files[choice - 1]



def get_task_details(filepath):
    priority = -999
    task_status = "No status"
    description = "No description"
    tags = "No tags"
    list_name = ""  # optional List origin
    name = os.path.splitext(os.path.basename(filepath))[0]
    due_date = "No due date"
    date_added = None
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("**Name:**"):
                name = line.strip().split("**Name:**")[1].strip()
            elif line.startswith("**List:**"):
                list_name = line.strip().split("**List:**")[1].strip()
            elif line.startswith("**Priority Score:**"):
                try:
                    priority = int(line.strip().split("**Priority Score:**")[1].strip())
                except ValueError:
                    pass
            elif line.startswith("**Status:**"):
                task_status = line.strip().split("**Status:**")[1].strip()
            elif line.startswith("**Description:**"):
                description = line.strip().split("**Description:**")[1].strip()
            elif line.startswith("**Tags:**"):
                tags = line.strip().split("**Tags:**")[1].strip()
            elif line.startswith("**Due Date:**"):
                due_date = line.strip().split("**Due Date:**")[1].strip() or "No due date"
            elif line.startswith("**Date Added:**"):
                date_added = line.strip().split("**Date Added:**")[1].strip()

    match = re.search(r"\d{4}-\d{2}-\d{2}", file_name)
    if match:
        start_date = match.group()
    else:
        if date_added and len(date_added) >= 10:
            start_date = date_added[:10]
        else:
            start_date = "N/A"
    return {
        "Task Name": name,
        "Priority Score": priority,
        "File Name": file_name,
        "Start Date": start_date,
        "Due Date": due_date,
        "Status": task_status,
        "Description": description,
        "Tags": tags,
        "Date Added": date_added or "",
        "List": list_name,
    }