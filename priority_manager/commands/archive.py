import os
import click
from ..utils.helpers import ensure_dirs
from ..utils.logger import log_action
import shutil

TASKS_DIR = "tasks"
ARCHIVE_DIR = "archive"
# Archive a task
@click.command('archive', help="Move a task to the archive.")
def archive():
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return
    
    for idx, file in enumerate(files, 1):
        click.echo(f"{idx}. {file}")
    
    choice = click.prompt("Enter the number of the task you want to archive", type=int)
    if 1 <= choice <= len(files):
        src = os.path.join(TASKS_DIR, files[choice - 1])
        dest = os.path.join(ARCHIVE_DIR, files[choice - 1])
        shutil.move(src, dest)
        log_action(f"Archived task: {files[choice - 1]}")
        click.echo(f"Task archived: {files[choice - 1]}")
    else:
        click.echo("Invalid choice. Please try again.")