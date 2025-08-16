import os
import re
from datetime import datetime
import click
import requests
from ..utils.helpers import ensure_dirs, files_to_tasks
from ..utils.ms_todo import get_token, get_or_create_list, get_tasks, create_task
from ..utils.config import CONFIG

# Use dynamic access inside the command so tests altering CONFIG take effect.
TASKS_DIR = CONFIG["directories"]["tasks_dir"]

@click.command(name="sync", help="Synchronize tasks with Microsoft To Do (push local, pull remote, or both).")
@click.option("--open-instructions", is_flag=True, help="Open browser with instructions if MS_TODO_TOKEN is missing.")
@click.option("--verbose", is_flag=True, help="Verbose output (HTTP errors, diagnostics).")
@click.option("--push", "sync_push", is_flag=True, help="Push only: upload local tasks missing remotely.")
@click.option("--pull", "sync_pull", is_flag=True, help="Pull only: create local files for remote tasks missing locally.")
@click.option("--both", "sync_both", is_flag=True, help="Do both push and pull (default if no flag provided).")
def sync_tasks(open_instructions, verbose, sync_push, sync_pull, sync_both):
    """Synchronize local tasks with Microsoft To Do list.

    Modes:
      --push  : local -> remote only
      --pull  : remote -> local only
      --both  : bidirectional (default)
    """
    # Refresh tasks dir in case CONFIG changed (e.g., tests)
    global TASKS_DIR
    TASKS_DIR = CONFIG["directories"]["tasks_dir"]
    ensure_dirs()
    token = get_token()
    if not token:
        if open_instructions:
            import webbrowser
            from ..utils.ms_todo import INSTRUCTION_URL
            webbrowser.open(INSTRUCTION_URL)
        # Exit gracefully
        click.echo("Aborting sync; token required.")
        return

    # Determine mode
    mode = "both"
    specified = [sync_push, sync_pull, sync_both]
    if sum(1 for x in specified if x) > 1:
        click.secho("Specify only one of --push / --pull / --both", fg="red")
        return
    if sync_push:
        mode = "push"
    elif sync_pull:
        mode = "pull"
    elif sync_both:
        mode = "both"

    def slugify(name: str) -> str:
        base = re.sub(r"[^A-Za-z0-9 _-]+", "", name).strip().replace(" ", "_")
        return base[:30] if base else "task"

    def write_task_file(title: str, due_date: str | None):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        slug = slugify(title)
        filename = f"{timestamp}_{slug}.md"
        path = os.path.join(TASKS_DIR, filename)
        if os.path.exists(path):
            filename = f"{timestamp}-{now.strftime('%f')}_{slug}.md"
            path = os.path.join(TASKS_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"**Name:** {title}\n\n")
            f.write(f"**Description:** Pulled from Microsoft To Do\n\n")
            f.write(f"**Priority Score:** 0\n\n")
            f.write(f"**Due Date:** {due_date or 'No due date'}\n\n")
            f.write(f"**Tags:** \n\n")
            f.write(f"**Date Added:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Status:** To Do\n")
        return path

    with requests.Session() as session:
        try:
            list_id = get_or_create_list(session, token)
        except requests.HTTPError as e:
            status = getattr(e.response, 'status_code', None)
            body = getattr(e.response, 'text', '')
            if status == 401:
                click.secho("Unauthorized (401). Access token likely expired or invalid.", fg='red')
                click.echo("Obtain a fresh token (Graph Explorer or app registration) and update:")
                if os.name == 'nt':
                    click.echo("  setx MS_TODO_TOKEN <new_token>")
                else:
                    click.echo("  export MS_TODO_TOKEN=<new_token>")
                click.echo("Or place it in config.yaml under ms_todo.token.")
                if verbose:
                    click.echo(f"Response body: {body[:400]}")
                return
            else:
                click.secho(f"Failed to access list (status {status}).", fg='red')
                if verbose:
                    click.echo(body[:800])
                return
        remote_tasks = get_tasks(session, token, list_id)
        remote_titles = {t.get("title") for t in remote_tasks}

        pushed = 0
        pulled = 0

        # Push
        if mode in ("push", "both"):
            local_files = os.listdir(TASKS_DIR)
            local_tasks = files_to_tasks(local_files)
            for task in local_tasks:
                name = task["Task Name"]
                if name not in remote_titles:
                    due_date = task.get("Due Date")
                    due = None if due_date == "No due date" else due_date
                    create_task(session, token, list_id, name, due)
                    pushed += 1

        # Pull
        if mode in ("pull", "both"):
            # Build local name set to avoid duplicates
            local_files_now = os.listdir(TASKS_DIR)
            # Extract names from local tasks
            local_name_set = {t["Task Name"] for t in files_to_tasks(local_files_now)} if local_files_now else set()
            for r in remote_tasks:
                title = r.get("title")
                if not title or title in local_name_set:
                    continue
                # Due date from Graph response: structure may include dueDateTime
                due = None
                due_dt = r.get("dueDateTime") if isinstance(r, dict) else None
                if isinstance(due_dt, dict):
                    due = due_dt.get("dateTime")
                write_task_file(title, due)
                pulled += 1

        click.echo(f"Sync complete. Mode={mode}. Pushed: {pushed}, Pulled: {pulled}, Remote existing: {len(remote_titles) - pushed}")
