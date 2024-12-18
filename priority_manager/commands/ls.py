import os
import re
import click
import shutil
from tabulate import tabulate
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
        click.secho("No tasks found.", fg="yellow")
        return

    # Interactive status selection if --status flag is provided
    selected_status = None
    if status:
        click.secho("Select a status to filter tasks:", fg="cyan")
        for idx, s in enumerate(STATUSES, 1):
            click.echo(f"{idx}. {s}")
        choice = click.prompt("Enter the number of the status", type=int)
        if 1 <= choice <= len(STATUSES):
            selected_status = STATUSES[choice - 1]
            click.secho(f"Filtering tasks with status: {selected_status}", fg="cyan")
        else:
            click.secho("Invalid choice. No status filter applied.", fg="red")

    def get_task_details(filepath):
        priority = -999
        task_status = ""
        description = "No description"
        tags = "No tags"
        with open(filepath, "r") as f:
            for line in f:
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
        return priority, task_status, description, tags

    def extract_task_name(filename):
        # Remove date-time prefix using regex
        return re.sub(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+_", "", filename).replace(".md", "")

    def truncate(text, length):
        """Truncate text to the given length with ellipses if necessary."""
        return (text[:length] + "...") if len(text) > length else text

    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns

    # Determine proportional column widths based on terminal width
    col_widths = {
        "Task Name": terminal_width // 5,
        "Priority Score": terminal_width // 10,
        "Status": terminal_width // 10,
        "Description": terminal_width // 4,
        "Tags": terminal_width // 6,
    }

    tasks = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        priority, task_status, description, tags = get_task_details(filepath)
        task_name = extract_task_name(file)
        if selected_status is None or task_status.lower() == selected_status.lower():
            tasks.append((
                truncate(task_name, col_widths["Task Name"]),
                priority,
                truncate(task_status, col_widths["Status"]),
                truncate(description, col_widths["Description"]),
                truncate(tags, col_widths["Tags"]),
            ))

    if not tasks:
        click.secho(f"No tasks found with status: {selected_status}" if selected_status else "No tasks found.", fg="yellow")
        return

    # Sort tasks by priority
    tasks.sort(key=lambda x: x[1], reverse=True)

    # Prepare data for tabulate
    headers = ["#", "Task Name", "Priority Score", "Status", "Description", "Tags"]
    table = []
    for idx, (task_name, priority, task_status, description, tags) in enumerate(tasks, 1):
        table.append([idx, task_name, priority, task_status, description, tags])

    click.echo(tabulate(table, headers=headers, tablefmt="grid"))

