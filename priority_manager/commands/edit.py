import os
import click
import re
from datetime import datetime
from tabulate import tabulate
from rich.pretty import pprint
from ..utils.helpers import ensure_dirs, calculate_priority, show_tasks, files_to_tasks, get_sorted_files
from ..utils.logger import log_action
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]
STATUSES = CONFIG["statuses"]
TABLE_CONFIG = CONFIG["table"]["columns"]

@click.command('edit', help="List all tasks and suggest which one to edit.")
@click.option("--status", is_flag=True, help="Filter tasks by status interactively.")
@click.option("--priority", is_flag=True, help="Filter tasks by priority interactively.")
@click.option("--due-date", is_flag=True, help="Filter tasks by due date interactively.")
@click.option("--tags", is_flag=True, help="Filter tasks by tags interactively.")
@click.option("--name", is_flag=True, help="Filter tasks by name interactively.")
@click.option("--description", is_flag=True, help="Filter tasks by description interactively.")
@click.option("--date-created", is_flag=True, help="Filter tasks by date created interactively.")
@click.option("--date-edited", is_flag=True, help="Filter tasks by date edited interactively.")
@click.option("--open-task", is_flag=True, help="Filter tasks by open status.")
@click.option("--in-progress", is_flag=True, help="Filter tasks by in progress status.")
@click.option("--done", is_flag=True, help="Filter tasks by done status.")
@click.option("--archived", is_flag=True, help="Filter tasks by archived status.")
@click.option("--priority-score", is_flag=True, help="Filter tasks by priority score.")


def edit(status, priority, due_date, tags, name, description, date_created, date_edited, open_task, in_progress, done, archived, priority_score):
    """Edit an existing task."""
    ensure_dirs()
    files = get_sorted_files(TASKS_DIR)
    # pprint(files_to_tasks(files))   
    if not files:
        click.echo("No tasks found.")
        return

    show_tasks(files_to_tasks(files))

    choice = click.prompt("Enter the number of the task you want to edit", type=int)
    if choice < 1 or choice > len(files):
        click.secho("Invalid choice. Please select a valid task number.", fg="red")
        return
    while files[choice-1] not in files:
        click.secho("Invalid choice. Please select a valid task number.", fg="red")
        # pprint(files)
        choice = click.prompt("Enter the number of the task you want to edit", type=int)

    filepath = os.path.join(TASKS_DIR, files[choice-1])
    # pprint({"filePath":filepath, "sorted": files, "Choice":choice})

    task_data = {}
    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("**Name:**"):
                task_data["Name"] = line.split("**Name:**")[1].strip()
            elif line.startswith("**Description:**"):
                task_data["Description"] = line.split("**Description:**")[1].strip()
            elif line.startswith("**Priority Score:**"):
                task_data["Priority Score"] = line.split("**Priority Score:**")[1].strip()
            elif line.startswith("**Due Date:**"):
                task_data["Due Date"] = line.split("**Due Date:**")[1].strip()
            elif line.startswith("**Tags:**"):
                task_data["Tags"] = line.split("**Tags:**")[1].strip()
            elif line.startswith("**Status:**"):
                task_data["Status"] = line.split("**Status:**")[1].strip()

    new_task_name = click.prompt("Enter new task name", default=task_data.get("Name", os.path.splitext(files[choice-1])[0]))
    new_description = click.prompt("Enter new description", default=task_data.get("Description", "No description"))
    new_due_date = click.prompt("Enter new due date (YYYY-MM-DD)", default=task_data.get("Due Date", "No due date"))
    new_tags = click.prompt("Enter new tags (comma-separated)", default=task_data.get("Tags", ""))
    new_status = click.prompt(f"Enter new status ({', '.join(STATUSES)})", default=task_data.get("Status", "To Do"), type=click.Choice(STATUSES))
    update_priority = click.confirm("Do you want to update the priority score?", default=False)
    new_priority = calculate_priority() if update_priority else task_data.get("Priority Score", "0")

    with open(filepath, "w") as f:
        f.write(f"**Name:** {new_task_name}\n\n")
        f.write(f"**Description:** {new_description}\n\n")
        f.write(f"**Priority Score:** {new_priority}\n\n")
        f.write(f"**Due Date:** {new_due_date}\n\n")
        f.write(f"**Tags:** {new_tags}\n\n")
        f.write(f"**Date Edited:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Status:** {new_status}\n")

    log_action(f"Edited task: {new_task_name} with status {new_status}")
    click.echo(f"Task edited successfully. New status: {new_status}")