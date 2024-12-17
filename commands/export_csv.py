import os
import csv
import click
from utils.helpers import ensure_dirs

TASKS_DIR = "tasks"
EXPORT_FILE = "tasks_export.csv"

@click.command(name="export-csv")
def export_csv():
    """Export tasks to a CSV file."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    
    if not files:
        click.echo("No tasks found to export.")
        return

    with open(EXPORT_FILE, mode="w", newline="") as csv_file:
        fieldnames = ["Task Name", "Description", "Priority Score", "Due Date", "Date Added", "Status"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

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

                writer.writerow(task_data)

    click.echo(f"Tasks exported successfully to {EXPORT_FILE}.")

