import os
import csv
import json
import yaml
import click
from ..utils.helpers import ensure_dirs
from ..utils.config import CONFIG
from ..utils.task_file import TaskFile


@click.command(name="export", help="Export tasks to CSV, JSON, or YAML file.")
@click.argument("format", type=click.Choice(["csv", "json", "yaml"], case_sensitive=False))
@click.option("--output", default="tasks_export", help="Base name of the output file.")
def export_tasks(format, output):
    """Export tasks to CSV, JSON, or YAML file."""
    ensure_dirs()
    tasks_dir = CONFIG["directories"]["tasks_dir"]
    files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]

    if not files:
        click.echo("No tasks found to export.")
        return

    tasks = []
    for filename in files:
        filepath = os.path.join(tasks_dir, filename)
        task = TaskFile.read(filepath)
        tasks.append({
            "Task Name": task.name,
            "Description": task.description,
            "Priority Score": task.priority_score,
            "Due Date": task.due_date,
            "Date Added": task.date_added,
            "Status": task.status,
            "Tags": task.tags,
            "List": task.list_name,
        })

    if format == "csv":
        export_file = f"{output}.csv"
        fieldnames = ["Task Name", "Description", "Priority Score", "Due Date", "Date Added", "Status", "Tags", "List"]
        with open(export_file, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tasks)
        click.echo(f"Tasks exported successfully to {export_file}.")

    elif format == "json":
        export_file = f"{output}.json"
        with open(export_file, mode="w", encoding="utf-8") as json_file:
            json.dump(tasks, json_file, indent=4)
        click.echo(f"Tasks exported successfully to {export_file}.")

    elif format == "yaml":
        export_file = f"{output}.yaml"
        with open(export_file, mode="w", encoding="utf-8") as yaml_file:
            yaml.dump(tasks, yaml_file, default_flow_style=False)
        click.echo(f"Tasks exported successfully to {export_file}.")
