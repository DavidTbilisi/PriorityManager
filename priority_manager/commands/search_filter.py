import os
import click
from ..utils.helpers import ensure_dirs

TASKS_DIR = "tasks"

# Search for tasks by keyword or tag
@click.command(name="search", help="Search for tasks containing a specific keyword or tag.")
@click.argument("keyword", type=str, required=True)
@click.option("--tag", is_flag=True, help="Search within tags only.")
def search(keyword, tag):
    """Search for tasks containing a specific keyword or tag."""
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
            if tag:
                for line in content.splitlines():
                    if line.startswith("**Tags:**") and keyword.lower() in line.lower():
                        click.echo(f"Found in: {file}")
                        found = True
                        break
            else:
                if keyword.lower() in content.lower():
                    click.echo(f"Found in: {file}")
                    found = True

    if not found:
        click.echo(f"No tasks found containing the keyword or tag: {keyword}")

# Filter tasks by priority range and/or tags
@click.command(name="filter", help="Filter tasks within a specified priority range and/or by tag.")
@click.option("--min-priority", type=int, default=-999, help="Minimum priority score.")
@click.option("--max-priority", type=int, default=999, help="Maximum priority score.")
@click.option("--tag", default=None, help="Filter by tag.")
def filter_tasks(min_priority, max_priority, tag):
    """Filter tasks within a specified priority range and/or by tag."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.echo("No tasks found.")
        return

    def get_task_details(filepath):
        details = {"priority": None, "tags": ""}
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("**Priority Score:**"):
                    try:
                        details["priority"] = int(line.strip().split("**Priority Score:**")[1].strip())
                    except ValueError:
                        details["priority"] = None
                elif line.startswith("**Tags:**"):
                    details["tags"] = line.split("**Tags:**")[1].strip()
        return details

    filtered = []
    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        details = get_task_details(filepath)
        priority = details["priority"]
        tags = details["tags"]

        if priority is not None and min_priority <= priority <= max_priority:
            if tag:
                if tag.lower() in tags.lower():
                    filtered.append((file, priority, tags))
            else:
                filtered.append((file, priority, tags))

    if not filtered:
        click.echo("No tasks found matching the specified criteria.")
        return

    filtered.sort(key=lambda x: x[1], reverse=True)
    for idx, (file, priority, tags) in enumerate(filtered, 1):
        click.echo(f"{idx}. {file} - Priority Score: {priority} - Tags: {tags}")
