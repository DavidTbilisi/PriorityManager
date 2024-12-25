import os
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
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

def calculate_priority():
    urgency = click.prompt("Enter urgency (1-5, 5 = most urgent)", type=int, default=3)
    importance = click.prompt("Enter importance (1-5, 5 = most important)", type=int, default=3)
    effort = click.prompt("Enter effort (1-5, 5 = most effort required)", type=int, default=3)
    return urgency * 2 + importance * 3 - effort

def files_to_tasks(files, selected_status=None):
    """
    Convert a list of filenames to a list of task details dictionaries.
    """
    tasks = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        task_details = get_task_details(filepath)
        if selected_status is None or task_details["Status"].lower() == selected_status.lower():
            tasks.append(task_details)

        if not tasks:
            click.secho(f"No tasks found with status: {selected_status}" if selected_status else "No tasks found.", fg="yellow")
    return tasks

def get_sorted_files(dir=TASKS_DIR, by="Priority Score"):
    files = os.listdir(dir)
    files.sort(key=lambda x: get_task_details(os.path.join(dir, x))[by], reverse=True)
    return files


def show_tasks(tasks):
    # Sort tasks by priority
    # pprint(tasks)
    tasks.sort(key=lambda x: x["Priority Score"], reverse=True)

    # Prepare headers and rows based on config
    headers = [col["name"] for col in TABLE_CONFIG]
    table = []
    for idx, task in enumerate(tasks, 1):
        row = [idx]
        for col in TABLE_CONFIG:
            column_name = col["name"]
            max_length = col["max_length"]
            cell_value = task.get(column_name, "")
            row.append(truncate(str(cell_value), max_length))
        table.append(row)

    # Insert "#" as the first header
    headers.insert(0, "#")

    # Display the table
    click.echo(tabulate(table, headers=headers, tablefmt="github"))
    return tasks

def move_to_archive(files, choice):
    src = os.path.join(TASKS_DIR, files[choice - 1])
    dest = os.path.join(ARCHIVE_DIR, files[choice - 1])
    shutil.move(src, dest)
    return files[choice - 1]



def get_task_details(filepath):
    priority = -999
    task_status = "No status"
    description = "No description"
    tags = "No tags"
    name = os.path.splitext(os.path.basename(filepath))[0]
    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("**Name:**"):
                name = line.strip().split("**Name:**")[1].strip()
            if line.startswith("**Priority Score:**"):
                try:
                    priority = int(line.strip().split("**Priority Score:**")[1].strip())
                except ValueError:
                    pass
            if line.startswith("**Status:**"):
                task_status = line.strip().split("**Status:**")[1].strip()
            if line.startswith("**Description:**"):
                description = line.strip().split("**Description:**")[1].strip()
            if line.startswith("**Tags:**"):
                tags = line.strip().split("**Tags:**")[1].strip()

    return {
        "Task Name": name,
        "Priority Score": priority,
        "Status": task_status,
        "Description": description,
        "Tags": tags,
    }