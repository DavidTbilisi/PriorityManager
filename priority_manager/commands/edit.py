import os
from datetime import datetime
import click
from ..utils.helpers import ensure_dirs, calculate_priority
from ..utils.logger import log_action
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
STATUSES = CONFIG["statuses"]

@click.command('edit', help="List all tasks and suggest which one to edit.")
def edit():
    """Edit an existing task."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return

    # Display the list of tasks with their names
    for idx, file in enumerate(files, 1):
        filepath = os.path.join(TASKS_DIR, file)
        with open(filepath, "r") as f:
            task_name = "Unknown Task"
            for line in f:
                if line.startswith("**Name:**"):
                    task_name = line.split("**Name:**")[1].strip()
                    break
        click.echo(f"{idx}. {task_name}")

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

    new_task_name = click.prompt("Enter new task name", default=task_data.get("Name", "Unknown Task"))
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
