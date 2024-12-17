import os
import click
from utils.helpers import ensure_dirs

TASKS_DIR = "tasks"

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
        return -999
    
    tasks = [(file, get_priority_from_file(os.path.join(TASKS_DIR, file))) for file in files]
    tasks.sort(key=lambda x: x[1], reverse=True)
    
    for idx, (file, priority) in enumerate(tasks, 1):
        click.echo(f"{idx}. {file} - Priority Score: {priority}")
