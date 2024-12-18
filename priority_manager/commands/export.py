import os
import csv
import json
import yaml
import click
from ..utils.helpers import ensure_dirs

from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]

@click.command(name="export", help="Export tasks to CSV, JSON, or YAML file.")
@click.argument("format", type=click.Choice(["csv", "json", "yaml"], case_sensitive=False))
@click.option("--output", default="tasks_export", help="Base name of the output file.")
def export_tasks(format, output):
    """Export tasks to CSV, JSON, or YAML file."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    
    if not files:
        click.echo("No tasks found to export.")
        return

    tasks = []

    for file in files:
        filepath = os.path.join(TASKS_DIR, file)
        with open(filepath, "r") as f:
            task_data = {}
            for line in f:
                if line.startswith("#"):
                    task_data["Task Name"] = line.strip("# ").strip()
                elif line.startswith("**Description:**"):
                    task_data["Description"] = line.split("**Description:**")[1].strip()
                elif line.startswith("**Priority Score:**"):
                    task_data["Priority Score"] = line.split("**Priority Score:**")[1].strip()
                elif line.startswith("**Due Date:**"):
                    task_data["Due Date"] = line.split("**Due Date:**")[1].strip()
                elif line.startswith("**Date Added:**"):
                    task_data["Date Added"] = line.split("**Date Added:**")[1].strip()
                elif line.startswith("**Status:**"):
                    task_data["Status"] = line.split("**Status:**")[1].strip()
            tasks.append(task_data)

    if format == "csv":
        export_file = f"{output}.csv"
        with open(export_file, mode="w", newline="") as csv_file:
            fieldnames = ["Task Name", "Description", "Priority Score", "Due Date", "Date Added", "Status"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tasks)
        click.echo(f"Tasks exported successfully to {export_file}.")

    elif format == "json":
        export_file = f"{output}.json"
        with open(export_file, mode="w") as json_file:
            json.dump(tasks, json_file, indent=4)
        click.echo(f"Tasks exported successfully to {export_file}.")

    elif format == "yaml":
        export_file = f"{output}.yaml"
        with open(export_file, mode="w") as yaml_file:
            yaml.dump(tasks, yaml_file, default_flow_style=False)
        click.echo(f"Tasks exported successfully to {export_file}.")
