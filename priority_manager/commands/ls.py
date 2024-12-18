import os
import click
import shutil
from tabulate import tabulate
from ..utils.helpers import ensure_dirs
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
STATUSES = CONFIG["statuses"]
TABLE_CONFIG = CONFIG["table"]["columns"]

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
        name = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("**Name:**"):
                    name = line.strip().split("**Name:**")[1].strip()
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
        return {
            "Task Name": name,
            "Priority Score": priority,
            "Status": task_status,
            "Description": description,
            "Tags": tags,
        }

    def truncate(text, length):
        """Truncate text to the given length with ellipses if necessary."""
        return (text[:length] + "...") if len(text) > length else text

    tasks = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        task_details = get_task_details(filepath)
        if selected_status is None or task_details["Status"].lower() == selected_status.lower():
            tasks.append(task_details)

    if not tasks:
        click.secho(f"No tasks found with status: {selected_status}" if selected_status else "No tasks found.", fg="yellow")
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
            row.append(truncate(str(cell_value), max_length))
        table.append(row)

    # Insert "#" as the first header
    headers.insert(0, "#")

    # Display the table
    click.echo(tabulate(table, headers=headers, tablefmt="github"))
