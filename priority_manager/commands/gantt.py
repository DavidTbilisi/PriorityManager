import os
import click
from tabulate import tabulate
import plotly.figure_factory as ff
from rich.pretty import pprint
from datetime import datetime
import re
from ..utils.helpers import ensure_dirs, files_to_tasks
from ..utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
STATUSES = CONFIG["statuses"]
GANTT_HEIGHT = CONFIG["gantt"]["height"]

@click.command(name="gantt", help="Generate a Gantt chart for tasks.")
def gantt():
    """Generate a Gantt chart for tasks."""
    ensure_dirs()
    files = os.listdir(TASKS_DIR)
    if not files:
        click.secho("No tasks found.", fg="yellow")
        return

    tasks = files_to_tasks(files)
    if not tasks:
        click.secho("No tasks found.", fg="yellow")
        return
    
    tasks.sort(key=lambda x: x["Priority Score"], reverse=True)
    # Prepare data for Gantt chart
    data = []
    for task in tasks:
        # pprint(task)
        if task["Due Date"] == "No due date":
            continue
        task_dict = {}
        task_dict["Task"] = task["Task Name"]
        task_dict["Start"] = datetime.strptime(task["Start Date"], "%Y-%m-%d")
        task_dict["Finish"] = datetime.strptime(task["Due Date"], "%Y-%m-%d")
        task_dict["Resource"] = task["Status"]

        data.append(task_dict)
    fig = ff.create_gantt(
        data, 
        index_col="Resource", 
        show_colorbar=True, 
        group_tasks=True, 
        showgrid_x=True, 
        showgrid_y=True,
        height=GANTT_HEIGHT
        )
    
    # add vertical transparent line indicating specific date (e.g. today)
    fig.add_vline(x=datetime.now(), line_width=.5, line_color="green")
    fig.show()

