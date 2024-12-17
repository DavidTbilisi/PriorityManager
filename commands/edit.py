import os
from datetime import datetime
import click
from utils.helpers import ensure_dirs, calculate_priority
from utils.logger import log_action

TASKS_DIR = "tasks"

@click.command()
def edit():
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return
    
    for idx, file in enumerate(files, 1):
        click.echo(f"{idx}. {file}")
    
    choice = click.prompt("Enter the number of the task you want to edit", type=int)
    if 1 <= choice <= len(files):
        filepath = os.path.join(TASKS_DIR, files[choice - 1])
        
        with open(filepath, "r") as f:
            lines = f.readlines()
        
        click.echo("Current task details:")
        for line in lines:
            click.echo(line.strip())
        
        new_task_name = click.prompt("Enter new task name", default=lines[0].strip("# ").strip())
        new_description = click.prompt("Enter new description", default="No description")
        new_due_date = click.prompt("Enter new due date (YYYY-MM-DD)", default="No due date")
        new_priority = calculate_priority()
        
        with open(filepath, "w") as f:
            f.write(f"# {new_task_name}\n\n")
            f.write(f"**Description:** {new_description}\n\n")
            f.write(f"**Priority Score:** {new_priority}\n\n")
            f.write(f"**Due Date:** {new_due_date}\n\n")
            f.write(f"**Date Edited:** {datetime.now().isoformat()}\n\n")
            f.write("**Status:** Incomplete\n")
        
        log_action(f"Edited task: {new_task_name} with new priority {new_priority}")
        click.echo("Task edited successfully.")
    else:
        click.echo("Invalid choice. Please try again.")
