import os
from datetime import datetime
import click
import sys
import shutil

TASKS_DIR = "tasks"
ARCHIVE_DIR = "archive"
LOG_FILE = "log.txt"

# Ensure tasks and archive directories exist
def ensure_dirs():
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

# Log operations
def log_action(action):
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now().isoformat()} - {action}\n")

# Calculate priority score based on urgency, importance, and effort
def calculate_priority():
    urgency = click.prompt("Enter urgency (1-5, 5 = most urgent)", type=int, default=3)
    importance = click.prompt("Enter importance (1-5, 5 = most important)", type=int, default=3)
    effort = click.prompt("Enter effort (1-5, 5 = most effort required)", type=int, default=3)
    
    # Ensure values are within range
    urgency = max(1, min(5, urgency))
    importance = max(1, min(5, importance))
    effort = max(1, min(5, effort))
    
    priority_score = urgency * 2 + importance * 3 - effort
    click.echo(f"Calculated Priority Score: {priority_score}")
    return priority_score

# Add a task
@click.command()
@click.argument("task_name")
def add(task_name):
    ensure_dirs()
    priority = calculate_priority()
    description = click.prompt("Enter task description", default="No description")
    due_date = click.prompt("Enter due date (YYYY-MM-DD)", default="No due date")
    date_added = datetime.now().isoformat()
    
    # Create a filename based on the task name and date
    safe_task_name = "_".join(task_name.split()).replace("/", "_").replace("\\", "_")
    filename = f"{date_added.replace(':', '-')}_{safe_task_name}.md"
    filepath = os.path.join(TASKS_DIR, filename)
    
    # Write the task details to the markdown file
    with open(filepath, "w") as f:
        f.write(f"# {task_name}\n\n")
        f.write(f"**Description:** {description}\n\n")
        f.write(f"**Priority Score:** {priority}\n\n")
        f.write(f"**Due Date:** {due_date}\n\n")
        f.write(f"**Date Added:** {date_added}\n\n")
        f.write("**Status:** Incomplete\n")
    
    log_action(f"Added task: {task_name} with priority {priority}")
    click.echo(f"Task added successfully with priority score: {priority}. File: {filepath}")

# List tasks sorted by priority
@click.command(name="list-tasks")
def list_tasks():
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return
    
    def get_priority_from_file(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("**Priority Score:**"):
                    try:
                        return int(line.strip().split("**Priority Score:** ")[1])
                    except ValueError:
                        pass
        return -999  # Default low priority if score not found
    
    tasks = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        priority = get_priority_from_file(filepath)
        tasks.append((file, priority))
    
    tasks.sort(key=lambda x: x[1], reverse=True)
    
    for idx, (file, priority) in enumerate(tasks, 1):
        click.echo(f"{idx}. {file} - Priority Score: {priority}")

# Mark a task as complete
@click.command()
def complete():
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return

    for idx, file in enumerate(files, 1):
        click.echo(f"{idx}. {file}")
    
    choice = click.prompt("Enter the number of the task to mark as complete", type=int)
    if 1 <= choice <= len(files):
        filepath = os.path.join(TASKS_DIR, files[choice - 1])
        
        with open(filepath, "r") as f:
            lines = f.readlines()
        
        with open(filepath, "w") as f:
            for line in lines:
                if line.startswith("**Status:**"):
                    f.write("**Status:** Complete\n")
                else:
                    f.write(line)
        
        log_action(f"Marked task as complete: {files[choice - 1]}")
        click.echo("Task marked as complete.")
    else:
        click.echo("Invalid choice. Please try again.")

# Archive a task
@click.command()
def archive():
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return

    for idx, file in enumerate(files, 1):
        click.echo(f"{idx}. {file}")
    
    choice = click.prompt("Enter the number of the task to archive", type=int)
    if 1 <= choice <= len(files):
        src = os.path.join(TASKS_DIR, files[choice - 1])
        dest = os.path.join(ARCHIVE_DIR, files[choice - 1])
        shutil.move(src, dest)
        log_action(f"Archived task: {files[choice - 1]}")
        click.echo(f"Task archived: {files[choice - 1]}")
    else:
        click.echo("Invalid choice. Please try again.")

# Main CLI group
@click.group()
def cli():
    pass

cli.add_command(add)
cli.add_command(list_tasks)
cli.add_command(complete)
cli.add_command(archive)

if __name__ == "__main__":
    try:
        cli()
    except SystemExit as e:
        if e.code != 0:
            sys.exit(e.code)
