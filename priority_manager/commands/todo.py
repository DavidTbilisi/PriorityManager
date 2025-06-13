import os
import click
import requests
from ..utils.helpers import ensure_dirs, files_to_tasks
from ..utils.ms_todo import get_token, get_or_create_list, get_tasks, create_task
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]

@click.command(name="sync", help="Synchronize tasks with Microsoft To Do")
def sync_tasks():
    """Synchronize local tasks with Microsoft To Do list."""
    ensure_dirs()
    token = get_token()
    with requests.Session() as session:
        list_id = get_or_create_list(session, token)
        remote_tasks = get_tasks(session, token, list_id)
        remote_titles = {t.get("title") for t in remote_tasks}

        local_files = os.listdir(TASKS_DIR)
        local_tasks = files_to_tasks(local_files)
        created = 0
        for task in local_tasks:
            name = task["Task Name"]
            if name not in remote_titles:
                due_date = task.get("Due Date")
                due = None if due_date == "No due date" else due_date
                create_task(session, token, list_id, name, due)
                created += 1

        click.echo(f"Synchronized tasks. Created {created} new task(s) in Microsoft To Do.")
