import os
import click
from ..utils.helpers import ensure_dirs, show_tasks, get_task_details, files_to_tasks
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
STATUSES = CONFIG["statuses"]
TABLE_CONFIG = CONFIG["table"]["columns"]

@click.command(name="ls", help="List all tasks or filter by status. Supports nested folders from sync --folders.")
@click.option("--status", is_flag=True, help="Filter tasks by status interactively.")
@click.option("--recursive", is_flag=True, help="Recurse into subdirectories (auto if top-level empty).")
def list_tasks(status, recursive):
    """List tasks sorted by priority, optionally filtered by status interactively.

    If tasks dir contains only subdirectories (from sync --folders), recurse automatically unless disabled.
    """
    ensure_dirs()
    global TASKS_DIR
    TASKS_DIR = CONFIG["directories"]["tasks_dir"]
    try:
        entries = os.listdir(TASKS_DIR)
    except FileNotFoundError:
        entries = []

    # If every entry is a directory, treat as auto-recursive.
    # Determine if there are any top-level files
    top_level_files = [e for e in entries if os.path.isfile(os.path.join(TASKS_DIR, e))]
    if not entries:
        click.secho("No tasks found.", fg="yellow")
        return
    has_subdirs = any(os.path.isdir(os.path.join(TASKS_DIR, e)) for e in entries)
    # Auto recursive if user asked OR no top-level files but subdirectories present
    use_recursive = recursive or (has_subdirs and not top_level_files)

    # When auto_recursive is true but there are only subdirs (no direct files), we should proceed
    # even if there are no direct Markdown files at top level. Avoid premature 'No tasks found.'

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

    if use_recursive:
        tasks = files_to_tasks(recursive=True, selected_status=selected_status, suppress_empty_message=True)
        if not tasks:
            # Attempt one more scan without suppression just in case
            tasks = files_to_tasks(recursive=True, selected_status=selected_status, suppress_empty_message=False)
        if not tasks:
            click.secho("No tasks found.", fg="yellow")
            return
        show_tasks(tasks)
    else:
        show_tasks(files_to_tasks(top_level_files, selected_status))
