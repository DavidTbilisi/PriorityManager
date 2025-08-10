import os
from datetime import datetime
import re
import click
from ..utils.helpers import ensure_dirs, calculate_priority
from ..utils.logger import log_action
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
STATUSES = CONFIG["statuses"]
DEFAULTS = CONFIG["defaults"]

@click.command('add', help="Add a new task with calculated priority.")
@click.argument("task_name")
@click.option("--yes", "-y", is_flag=True, help="Skip prompts and use default values.")
def add(task_name, yes):
    ensure_dirs()
    date_added = datetime.now().isoformat()
    if yes:
        priority = DEFAULTS["priority"]
        description = DEFAULTS["description"]
        due_date = DEFAULTS["due_date"]
        tags = DEFAULTS["tags"]
        status = DEFAULTS["status"]
    else:
        priority = calculate_priority()
        description = click.prompt("Enter task description", default="No description")
        due_date = click.prompt("Enter due date (YYYY-MM-DD)", default="No due date")
        tags = click.prompt("Enter tags (comma-separated)", default="")
        status = click.prompt(f"Enter task status", default="To Do", type=click.Choice(STATUSES))
    
    # Create a filename using timestamp + a slugified portion of the task name (ascii fallback)
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
    # Slugify: keep alphanumerics, replace spaces with underscore, strip others
    slug_base = re.sub(r"[^A-Za-z0-9 _-]+", "", task_name).strip().replace(" ", "_")
    slug = slug_base[:30] if slug_base else "task"
    base_filename = f"{timestamp}_{slug}.md"
    filepath = os.path.join(TASKS_DIR, base_filename)
    # If a file with same second exists, append microseconds to ensure uniqueness
    if os.path.exists(filepath):
        filename = f"{timestamp}-{now.strftime('%f')}_{slug}.md"
        filepath = os.path.join(TASKS_DIR, filename)
    
    # Write task details to the file with the task name as a property
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"**Name:** {task_name}\n\n")
        f.write(f"**Description:** {description}\n\n")
        f.write(f"**Priority Score:** {priority}\n\n")
        f.write(f"**Due Date:** {due_date}\n\n")
        f.write(f"**Tags:** {tags}\n\n")
        f.write(f"**Date Added:** {date_added}\n\n")
        f.write(f"**Status:** {status}\n")
    
    log_action(f"Added task: {task_name} with priority {priority} and status {status}")
    click.echo(f"Task added successfully with priority score: {priority} and status: {status}. File: {filepath}")
