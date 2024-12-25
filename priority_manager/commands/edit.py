import os
import click
import re
from datetime import datetime
from tabulate import tabulate
from ..utils.helpers import ensure_dirs, calculate_priority
from ..utils.logger import log_action
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]
STATUSES = CONFIG["statuses"]
TABLE_CONFIG = CONFIG["table"]["columns"]

@click.command('edit', help="List all tasks and suggest which one to edit.")
def edit():
    """Edit an existing task."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return

    # List tasks in a table format
    tasks = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        task_name = os.path.splitext(file)[0]
        print(task_name)
        task_name_without_date = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+_", "", task_name).strip()
        task_details = {"Task Name": task_name_without_date, "Priority Score": -999, "Status": "Unknown", "Description": "", "Tags": ""}
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("**Name:**"):
                    task_details["Task Name"] = line.split("**Name:**")[1].strip()
                if line.startswith("**Priority Score:**"):
                    task_details["Priority Score"] = int(line.split("**Priority Score:**")[1].strip())
                if line.startswith("**Status:**"):
                    task_details["Status"] = line.split("**Status:**")[1].strip()
                if line.startswith("**Description:**"):
                    task_details["Description"] = line.split("**Description:**")[1].strip()
                if line.startswith("**Tags:**"):
                    task_details["Tags"] = line.split("**Tags:**")[1].strip()
            tasks.append(task_details)

    if not tasks:
        click.echo("No tasks found.")
        return

    # Sort tasks by priority
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
            row.append((str(cell_value)[:max_length] + "...") if len(str(cell_value)) > max_length else cell_value)
        table.append(row)

    # Insert "#" as the first header
    headers.insert(0, "#")

    # Display the table
    click.echo(tabulate(table, headers=headers, tablefmt="github"))

    choice = click.prompt("Enter the number of the task you want to edit", type=int)
    if not (1 <= choice <= len(files)):
        click.echo("Invalid choice. Please try again.")
        return

    filepath = os.path.join(TASKS_DIR, files[choice - 1])

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

    new_task_name = click.prompt("Enter new task name", default=task_data.get("Name", os.path.splitext(files[choice - 1])[0]))
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
