import os
import click
from ..utils.helpers import ensure_dirs, show_tasks, get_task_details, files_to_tasks
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

    show_tasks(files_to_tasks(files, selected_status))
