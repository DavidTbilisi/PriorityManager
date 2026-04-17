import os
import click
from ..utils.helpers import ensure_dirs
from ..utils.config import CONFIG


@click.command(name="search", help="Search for tasks containing a specific keyword or tag.")
@click.argument("keyword", type=str, required=True)
@click.option("--tag", is_flag=True, help="Search within tags only.")
def search(keyword, tag):
    """Search for tasks containing a specific keyword or tag."""
    ensure_dirs()
    tasks_dir = CONFIG["directories"]["tasks_dir"]
    files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]
    if not files:
        click.echo("No tasks found.")
        return

    found = False
    for filename in files:
        filepath = os.path.join(tasks_dir, filename)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if tag:
            for line in content.splitlines():
                if line.startswith("**Tags:**") and keyword.lower() in line.lower():
                    click.echo(f"Found in: {filename}")
                    found = True
                    break
        else:
            if keyword.lower() in content.lower():
                click.echo(f"Found in: {filename}")
                found = True

    if not found:
        click.echo(f"No tasks found containing the keyword or tag: {keyword}")


@click.command(name="filter", help="Filter tasks within a specified priority range and/or by tag.")
@click.option("--min-priority", type=int, default=-999, help="Minimum priority score.")
@click.option("--max-priority", type=int, default=999, help="Maximum priority score.")
@click.option("--tag", default=None, help="Filter by tag.")
def filter_tasks(min_priority, max_priority, tag):
    """Filter tasks within a specified priority range and/or by tag."""
    ensure_dirs()
    tasks_dir = CONFIG["directories"]["tasks_dir"]
    files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]
    if not files:
        click.echo("No tasks found.")
        return

    filtered = []
    for filename in files:
        filepath = os.path.join(tasks_dir, filename)
        priority = None
        tags = ""
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("**Priority Score:**"):
                    try:
                        priority = int(line.strip().split("**Priority Score:**")[1].strip())
                    except ValueError:
                        pass
                elif line.startswith("**Tags:**"):
                    tags = line.split("**Tags:**")[1].strip()

        if priority is not None and min_priority <= priority <= max_priority:
            if tag is None or tag.lower() in tags.lower():
                filtered.append((filename, priority, tags))

    if not filtered:
        click.echo("No tasks found matching the specified criteria.")
        return

    filtered.sort(key=lambda x: x[1], reverse=True)
    for idx, (filename, priority, tags) in enumerate(filtered, 1):
        click.echo(f"{idx}. {filename} - Priority Score: {priority} - Tags: {tags}")
