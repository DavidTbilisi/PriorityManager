import os
from datetime import datetime
import click
from utils.helpers import ensure_dirs, calculate_priority
from utils.logger import log_action

TASKS_DIR = "tasks"

@click.command()
@click.argument("task_name")
def add(task_name):
    ensure_dirs()
    priority = calculate_priority()
    description = click.prompt("Enter task description", default="No description")
    due_date = click.prompt("Enter due date (YYYY-MM-DD)", default="No due date")
    date_added = datetime.now().isoformat()
    
    safe_task_name = "_".join(task_name.split()).replace("/", "_").replace("\\", "_")
    filename = f"{date_added.replace(':', '-')}_{safe_task_name}.md"
    filepath = os.path.join(TASKS_DIR, filename)
    
    with open(filepath, "w") as f:
        f.write(f"# {task_name}\n\n")
        f.write(f"**Description:** {description}\n\n")
        f.write(f"**Priority Score:** {priority}\n\n")
        f.write(f"**Due Date:** {due_date}\n\n")
        f.write(f"**Date Added:** {date_added}\n\n")
        f.write("**Status:** Incomplete\n")
    
    log_action(f"Added task: {task_name} with priority {priority}")
    click.echo(f"Task added successfully with priority score: {priority}. File: {filepath}")