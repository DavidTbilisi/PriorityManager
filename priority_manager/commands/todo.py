import os
import re
import sys
from datetime import datetime
import click
import requests
from ..utils.helpers import ensure_dirs, files_to_tasks
from ..utils.ms_todo import get_token, get_or_create_list, get_tasks, create_task, get_lists, get_access_token
from ..utils.config import CONFIG

# Use dynamic access inside the command so tests altering CONFIG take effect.
TASKS_DIR = CONFIG["directories"]["tasks_dir"]

@click.command(name="sync", help="Synchronize tasks with Microsoft To Do (push local, pull remote, or both). Optionally organize by folders (per list).")
@click.option("--open-instructions", is_flag=True, help="Open browser with instructions if MS_TODO_TOKEN is missing.")
@click.option("--verbose", is_flag=True, help="Verbose output (HTTP errors, diagnostics).")
@click.option("--push", "sync_push", is_flag=True, help="Push only: upload local tasks missing remotely.")
@click.option("--pull", "sync_pull", is_flag=True, help="Pull only: create local files for remote tasks missing locally.")
@click.option("--both", "sync_both", is_flag=True, help="Do both push and pull (default if no flag provided).")
@click.option("--list", "list_name", type=str, help="Target a specific list name instead of default.")
@click.option("--all-lists", is_flag=True, help="Pull tasks from ALL lists (push still targets chosen/default list).")
@click.option("--folders", is_flag=True, help="Organize pulled tasks into subfolders named by list. Push will recurse.")
def sync_tasks(open_instructions, verbose, sync_push, sync_pull, sync_both, list_name, all_lists, folders):
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
    # Prefer MSAL cached or interactive acquisition (non-blocking unless no legacy token and device flow needed)
    token = get_access_token(prefer_msal=True, silent_only=True)
    if not token:
        # Fall back to legacy env/config token (with help messaging)
        token = get_token()
    if not token:
        click.echo("No access token available. Run 'priority-manager auth' to authenticate (device code flow).")
        if open_instructions:
            import webbrowser
            from ..utils.ms_todo import INSTRUCTION_URL
            webbrowser.open(INSTRUCTION_URL)
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
        target_list_name = list_name or "Priority Manager"

        # If pulling all lists we fetch them first; push list is still resolved separately.
        all_remote_lists = []
        if all_lists:
            try:
                all_remote_lists = get_lists(session, token)
            except requests.HTTPError as e:
                click.secho(f"Failed to retrieve lists: {e}", fg='red')
                return
        else:
            # For interactive selection (only if not specifying list & not all-lists & interactive tty)
            if list_name is None:
                try:
                    lists_preview = get_lists(session, token)
                    # Only prompt if interactive and more than 1 list and default not present
                    if sys.stdin.isatty() and len(lists_preview) > 1 and not any(l.get('displayName') == target_list_name for l in lists_preview):
                        click.echo("Select a list (no default found):")
                        for idx, l in enumerate(lists_preview, 1):
                            click.echo(f"{idx}. {l.get('displayName')}")
                        choice = click.prompt("Enter number (or 0 to create default)", type=int, default=0)
                        if 1 <= choice <= len(lists_preview):
                            target_list_name = lists_preview[choice - 1].get('displayName')
                except Exception:
                    pass  # non-fatal
        try:
            # Resolve target list id (create if absent) for push operations
            if list_name and not all_lists:
                # If explicit list requested, we need to create if missing. get_or_create_list uses constant name so implement inline.
                # Simpler: temporarily adjust constant behavior by creating if missing manually.
                remote_lists_for_target = get_lists(session, token)
                match = next((l for l in remote_lists_for_target if l.get('displayName') == target_list_name), None)
                if match:
                    list_id = match.get('id')
                else:
                    # create
                    url = f"https://graph.microsoft.com/v1.0/me/todo/lists"
                    resp = session.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json={"displayName": target_list_name})
                    resp.raise_for_status()
                    list_id = resp.json().get('id')
            else:
                # default existing logic (constant name) still works
                list_id = get_or_create_list(session, token)
        except requests.HTTPError as e:
            status = getattr(e.response, 'status_code', None)
            body = getattr(e.response, 'text', '')
            if status == 401:
                click.secho("Unauthorized (401). Access token likely expired or invalid.", fg='red')
                click.echo("Obtain a fresh token by running: priority-manager auth")
                click.echo("If you previously set ms_todo.token in config.yaml and it is stale, clear/remove it so MSAL cache can be used.")
                click.echo("(Legacy method: set MS_TODO_TOKEN env var or config ms_todo.token)")
                if verbose:
                    click.echo(f"Response body: {body[:400]}")
                return
            else:
                click.secho(f"Failed to access list (status {status}).", fg='red')
                if verbose:
                    click.echo(body[:800])
                return
        # Remote tasks for primary list (used for push and default pull)
        remote_tasks = get_tasks(session, token, list_id)
        remote_titles = {t.get("title") for t in remote_tasks}

        pushed = 0
        pulled = 0

        # Push
        if mode in ("push", "both"):
            try:
                if folders:
                    local_tasks = files_to_tasks(recursive=True)
                else:
                    local_files = os.listdir(TASKS_DIR)
                    local_tasks = files_to_tasks(local_files)
            except FileNotFoundError:
                local_tasks = []
            for task in local_tasks:
                name = task["Task Name"]
                if name not in remote_titles:
                    due_date = task.get("Due Date")
                    due = None if due_date == "No due date" else due_date
                    create_task(session, token, list_id, name, due)
                    pushed += 1

        # Pull logic
        if mode in ("pull", "both"):
            def pull_from_list(tasks_list, list_display):
                nonlocal pulled
                try:
                    local_files_now = os.listdir(TASKS_DIR) if not folders else []
                except FileNotFoundError:
                    local_files_now = []
                local_tasks_parsed = files_to_tasks(local_files_now, recursive=folders) if (local_files_now or folders) else []
                local_title_pairs = {(t.get('Task Name'), t.get('List','')) for t in local_tasks_parsed}
                for r in tasks_list:
                    title = r.get("title")
                    if not title:
                        continue
                    due = None
                    due_dt = r.get("dueDateTime") if isinstance(r, dict) else None
                    if isinstance(due_dt, dict):
                        due = due_dt.get("dateTime")
                    if (title, list_display) in local_title_pairs:
                        continue
                    # Custom filename includes list slug for uniqueness
                    now = datetime.now()
                    timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
                    list_slug = re.sub(r"[^A-Za-z0-9 _-]+", "", list_display).strip().replace(" ", "_")[:20] or "list"
                    task_slug = re.sub(r"[^A-Za-z0-9 _-]+", "", title).strip().replace(" ", "_")[:30] or "task"
                    filename = f"{timestamp}_{task_slug}.md" if folders else f"{timestamp}_{list_slug}__{task_slug}.md"
                    dir_base = TASKS_DIR
                    if folders:
                        dir_base = os.path.join(TASKS_DIR, list_slug)
                        if not os.path.isdir(dir_base):
                            os.makedirs(dir_base, exist_ok=True)
                    path = os.path.join(dir_base, filename)
                    if os.path.exists(path):
                        filename = f"{timestamp}-{now.strftime('%f')}_{task_slug}.md" if folders else f"{timestamp}-{now.strftime('%f')}_{list_slug}__{task_slug}.md"
                        path = os.path.join(dir_base, filename)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(f"**Name:** {title}\n\n")
                        f.write(f"**List:** {list_display}\n\n")
                        f.write(f"**Description:** Pulled from Microsoft To Do\n\n")
                        f.write(f"**Priority Score:** 0\n\n")
                        f.write(f"**Due Date:** {due or 'No due date'}\n\n")
                        f.write(f"**Tags:** \n\n")
                        f.write(f"**Date Added:** {datetime.now().isoformat()}\n\n")
                        f.write(f"**Status:** To Do\n")
                    pulled += 1

            if all_lists:
                for lst in all_remote_lists:
                    lid = lst.get('id')
                    lname = lst.get('displayName')
                    try:
                        tasks_list = get_tasks(session, token, lid)
                    except Exception as e:
                        if verbose:
                            click.echo(f"Skipping list {lname}: {e}")
                        continue
                    pull_from_list(tasks_list, lname)
            else:
                pull_from_list(remote_tasks, target_list_name)

        click.echo(f"Sync complete. Mode={mode}. List={'ALL' if all_lists else target_list_name}. Pushed: {pushed}, Pulled: {pulled}, Remote existing: {len(remote_titles) - pushed}")
