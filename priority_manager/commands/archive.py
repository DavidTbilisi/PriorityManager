import os
import shutil
import click
from ..utils.helpers import ensure_dirs
from ..utils.config import CONFIG
from ..utils.logger import log_action
from ..utils.task_file import TaskFile


@click.command("archive", help="Move a task to the archive.")
def archive():
    ensure_dirs()
    tasks_dir = CONFIG["directories"]["tasks_dir"]
    archive_dir = CONFIG["directories"]["archive_dir"]

    files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]
    if not files:
        click.echo("No tasks found.")
        return

    for idx, filename in enumerate(files, 1):
        task = TaskFile.read(os.path.join(tasks_dir, filename))
        click.echo(f"{idx}. {task.name}")

    choice = click.prompt("Enter the number of the task you want to archive", type=int)
    if 1 <= choice <= len(files):
        src = os.path.join(tasks_dir, files[choice - 1])
        dest = os.path.join(archive_dir, files[choice - 1])
        shutil.move(src, dest)
        log_action(f"Archived task: {files[choice - 1]}")
        click.echo(f"Task archived: {files[choice - 1]}")
    else:
        click.secho("Invalid choice. Please try again.", fg="red")
