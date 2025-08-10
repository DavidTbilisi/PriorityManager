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
@click.option("--wait", is_flag=True, help="Wait for user input after rendering (keep process alive).")
@click.option("--output", type=click.Path(dir_okay=False, writable=True), default=None, help="Save chart to HTML file instead of (or in addition to) opening browser.")
@click.option("--no-open", is_flag=True, help="Do not automatically open the chart in a browser.")
def gantt(wait, output, no_open):
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
        # Skip if no due date
        if task["Due Date"] in ("No due date", ""):
            continue
        start_str = task.get("Start Date")
        finish_str = task.get("Due Date")
        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d")
            finish_dt = datetime.strptime(finish_str, "%Y-%m-%d")
            if finish_dt < start_dt:
                # Swap or skip inconsistent dates; choose skip for now
                continue
        except Exception:
            # Skip tasks with unparsable dates
            continue
        task_dict = {
            "Task": task["Task Name"],
            "Start": start_dt,
            "Finish": finish_dt,
            "Resource": task["Status"],
        }
        data.append(task_dict)

    if not data:
        click.secho("No tasks with valid dates to build Gantt chart.", fg="yellow")
        return
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
    opened = False
    # Save to file if requested
    if output:
        try:
            fig.write_html(output, auto_open=not no_open)
            opened = not no_open
            click.echo(f"Gantt chart written to {output}")
        except Exception as e:
            click.secho(f"Failed to write HTML: {e}", fg="red")

    if not output:
        # Default behavior: open interactive window unless suppressed
        if not no_open:
            fig.show()
            opened = True

    if wait:
        # Provide a simple prompt so servers / scripts can keep process alive
        click.echo("Press Enter to exit Gantt view...")
        try:
            input()
        except KeyboardInterrupt:
            pass

