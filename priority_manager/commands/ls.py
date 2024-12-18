import os
import click
from ..utils.helpers import ensure_dirs
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
STATUSES = CONFIG["statuses"]

@click.command(name="ls", help="List all tasks or filter by status.")
@click.option("--status", is_flag=True, help="Filter tasks by status interactively.")
def list_tasks(status):
    """List tasks sorted by priority, optionally filtered by status interactively."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return

    # Interactive status selection if --status flag is provided
    selected_status = None
    if status:
        click.echo("Select a status to filter tasks:")
        for idx, s in enumerate(STATUSES, 1):
            click.echo(f"{idx}. {s}")
        choice = click.prompt("Enter the number of the status", type=int)
        if 1 <= choice <= len(STATUSES):
            selected_status = STATUSES[choice - 1]
            click.echo(f"Filtering tasks with status: {selected_status}")
        else:
            click.echo("Invalid choice. No status filter applied.")

    def get_task_details(filepath):
        priority = -999
        task_status = ""
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("**Priority Score:**"):
                    try:
                        priority = int(line.strip().split("**Priority Score:**")[1].strip())
                    except ValueError:
                        pass
                if line.startswith("**Status:**"):
                    task_status = line.strip().split("**Status:**")[1].strip()
        return priority, task_status

    tasks = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        priority, task_status = get_task_details(filepath)
        if selected_status is None or task_status.lower() == selected_status.lower():
            tasks.append((file, priority, task_status))

    if not tasks:
        click.echo(f"No tasks found with status: {selected_status}" if selected_status else "No tasks found.")
        return

    # Sort tasks by priority
    tasks.sort(key=lambda x: x[1], reverse=True)

    for idx, (file, priority, task_status) in enumerate(tasks, 1):
        click.echo(f"{idx}. {file} - Priority Score: {priority} - Status: {task_status}")
