import os
import click
from datetime import datetime
from ..utils.helpers import ensure_dirs, calculate_priority, show_tasks, files_to_tasks
from ..utils.logger import log_action
from ..utils.config import CONFIG
from ..utils.task_file import TaskFile


@click.command("edit", help="List tasks and edit one interactively. Use filter options to narrow the list.")
@click.option("--status", "filter_status", default=None, help="Filter tasks by status (exact match).")
@click.option("--name", "filter_name", default=None, help="Filter tasks by name substring.")
@click.option("--tags", "filter_tags", default=None, help="Filter tasks by tag substring.")
@click.option("--open-task", "filter_open", is_flag=True, help="Show only 'To Do' tasks.")
@click.option("--in-progress", "filter_in_progress", is_flag=True, help="Show only 'In Progress' tasks.")
@click.option("--done", "filter_done", is_flag=True, help="Show only 'Complete' tasks.")
def edit(filter_status, filter_name, filter_tags, filter_open, filter_in_progress, filter_done):
    """Edit an existing task, preserving all metadata fields."""
    ensure_dirs()
    tasks_dir = CONFIG["directories"]["tasks_dir"]
    statuses = CONFIG["statuses"]

    tasks = files_to_tasks(recursive=False, suppress_empty_message=True)
    if not tasks:
        click.secho("No tasks found.", fg="yellow")
        return

    # Apply filters
    if filter_open:
        tasks = [t for t in tasks if t["Status"].lower() == "to do"]
    elif filter_in_progress:
        tasks = [t for t in tasks if t["Status"].lower() == "in progress"]
    elif filter_done:
        tasks = [t for t in tasks if t["Status"].lower() == "complete"]
    if filter_status:
        tasks = [t for t in tasks if t["Status"].lower() == filter_status.lower()]
    if filter_name:
        tasks = [t for t in tasks if filter_name.lower() in t["Task Name"].lower()]
    if filter_tags:
        tasks = [t for t in tasks if filter_tags.lower() in t["Tags"].lower()]

    if not tasks:
        click.secho("No tasks match the given filters.", fg="yellow")
        return

    tasks = show_tasks(tasks)

    choice = click.prompt("Enter the number of the task you want to edit", type=int)
    while choice < 1 or choice > len(tasks):
        click.secho("Invalid choice. Please select a valid task number.", fg="red")
        choice = click.prompt("Enter the number of the task you want to edit", type=int)

    selected = tasks[choice - 1]
    filepath = selected.get("Filepath") or os.path.join(tasks_dir, selected["File Name"] + ".md")

    task = TaskFile.read(filepath)

    new_name = click.prompt("Enter new task name", default=task.name)
    new_description = click.prompt("Enter new description", default=task.description)
    new_due_date = click.prompt("Enter new due date (YYYY-MM-DD)", default=task.due_date)
    new_tags = click.prompt("Enter new tags (comma-separated)", default=task.tags)
    new_status = click.prompt("Enter new status", default=task.status, type=click.Choice(statuses))
    update_priority = click.confirm("Do you want to update the priority score?", default=False)
    new_priority = calculate_priority() if update_priority else task.priority_score

    task.name = new_name
    task.description = new_description
    task.due_date = new_due_date
    task.tags = new_tags
    task.status = new_status
    task.priority_score = int(new_priority)
    task.date_edited = datetime.now().isoformat()

    task.write()

    log_action(f"Edited task: {new_name} with status {new_status}")
    click.echo(f"Task edited successfully. New status: {new_status}")
