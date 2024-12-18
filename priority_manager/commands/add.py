import os
from datetime import datetime
import click
from ..utils.helpers import ensure_dirs, calculate_priority
from ..utils.logger import log_action
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
STATUSES = CONFIG["statuses"]
DEFAULTS = CONFIG["defaults"]

@click.command('add', help="Add a new task with calculated priority.")
@click.argument("task_name")
def add(task_name):
    ensure_dirs()
    priority = calculate_priority()
    description = click.prompt("Enter task description", default="No description")
    due_date = click.prompt("Enter due date (YYYY-MM-DD)", default="No due date")
    tags = click.prompt("Enter tags (comma-separated)", default="")
    status = click.prompt(f"Enter task status", default="To Do", type=click.Choice(STATUSES))
    date_added = datetime.now().isoformat()
    
    # Create a filename using a timestamp only
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{timestamp}.md"
    filepath = os.path.join(TASKS_DIR, filename)
    
    # Write task details to the file with the task name as a property
    with open(filepath, "w") as f:
        f.write(f"**Name:** {task_name}\n\n")
        f.write(f"**Description:** {description}\n\n")
        f.write(f"**Priority Score:** {priority}\n\n")
        f.write(f"**Due Date:** {due_date}\n\n")
        f.write(f"**Tags:** {tags}\n\n")
        f.write(f"**Date Added:** {date_added}\n\n")
        f.write(f"**Status:** {status}\n")
    
    log_action(f"Added task: {task_name} with priority {priority} and status {status}")
    click.echo(f"Task added successfully with priority score: {priority} and status: {status}. File: {filepath}")
