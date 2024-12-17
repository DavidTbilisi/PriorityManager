import os
import click
from utils.helpers import ensure_dirs

TASKS_DIR = "tasks"

# Search for tasks by keyword
@click.command(name="search")
@click.argument("keyword")
def search(keyword):
    """Search for tasks containing a specific keyword."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return

    found = False
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        with open(filepath, "r") as f:
            content = f.read()
            if keyword.lower() in content.lower():
                click.echo(f"Found in: {file}")
                found = True

    if not found:
        click.echo(f"No tasks found containing the keyword: {keyword}")

# Filter tasks by priority range
@click.command(name="filter-tasks")
@click.option("--min-priority", type=int, default=-999, help="Minimum priority score.")
@click.option("--max-priority", type=int, default=999, help="Maximum priority score.")
def filter_tasks(min_priority, max_priority):
    """Filter tasks within a specified priority range."""
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
                        return int(line.strip().split("**Priority Score:**")[1])
                    except ValueError:
                        pass
        return None

    filtered = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        priority = get_priority_from_file(filepath)
        if priority is not None and min_priority <= priority <= max_priority:
            filtered.append((file, priority))

    if not filtered:
        click.echo("No tasks found within the specified priority range.")
        return

    filtered.sort(key=lambda x: x[1], reverse=True)
    for idx, (file, priority) in enumerate(filtered, 1):
        click.echo(f"{idx}. {file} - Priority Score: {priority}")
