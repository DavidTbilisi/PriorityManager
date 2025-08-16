import os
import click
import requests
# msgraph-sdk is installed optionally, but its fluent client surfaces many async patterns.
# For now we retain stable REST calls; future enhancement can add an async path.
try:  # presence flag only
    import msgraph  # noqa: F401
    _MSGRAPH_AVAILABLE = True
except Exception:
    _MSGRAPH_AVAILABLE = False
from .config import CONFIG

GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
LIST_NAME = "Priority Manager"

INSTRUCTION_URL = "https://developer.microsoft.com/en-us/graph/graph-explorer?request=me/todo/lists"

def get_token(show_help: bool = True):
    """Retrieve Microsoft Graph access token.

    Precedence:
      1. Environment variable MS_TODO_TOKEN
      2. config.yaml -> ms_todo.token (if non-empty)
      3. None (optionally print instructions)
    """
    # 1. Environment variable wins
    env_token = os.getenv("MS_TODO_TOKEN")
    if env_token:
        return env_token

    # 2. Config token fallback
    cfg_token = (
        CONFIG.get("ms_todo", {}).get("token")
        if isinstance(CONFIG.get("ms_todo"), dict)
        else None
    )
    if cfg_token and cfg_token.strip():
        return cfg_token.strip()

    # 3. Provide guidance
    if show_help:
        click.secho("MS_TODO_TOKEN is not set (env or config).", fg="red")
        click.echo("Quick setup (temporary token):")
        click.echo(f"  1. Open: {INSTRUCTION_URL}")
        click.echo("  2. Sign in, consent to Tasks.ReadWrite, run a sample.")
        click.echo("  3. Copy 'Access token' tab value and either:")
        if os.name == 'nt':
            click.echo("     setx MS_TODO_TOKEN <token>   # persist for new shells")
        else:
            click.echo("     export MS_TODO_TOKEN=<token> # current shell only")
        click.echo("     - OR - add under ms_todo.token in config.yaml")
        click.echo("Then re-run: priority-manager sync")
    return None

def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

def get_or_create_list(session, token):
    """Return the ID of the task list creating it if necessary.

    Currently uses raw REST. Placeholder left for future msgraph-sdk async integration.
    """
    url = f"{GRAPH_API_BASE}/me/todo/lists"
    resp = session.get(url, headers=_headers(token))
    click.echo(f"GET {url} - {resp.status_code}")
    resp.raise_for_status()
    lists = resp.json().get("value", [])
    for lst in lists:
        if lst.get("displayName") == LIST_NAME:
            return lst["id"]
    resp = session.post(url, headers=_headers(token), json={"displayName": LIST_NAME})
    resp.raise_for_status()
    return resp.json()["id"]

def get_tasks(session, token, list_id):
    """Return list of tasks in given list.

    Raw REST call only for now.
    """
    url = f"{GRAPH_API_BASE}/me/todo/lists/{list_id}/tasks"
    resp = session.get(url, headers=_headers(token))
    resp.raise_for_status()
    return resp.json().get("value", [])

def create_task(session, token, list_id, title, due_date=None):
    """Create a task via REST (SDK path reserved for future)."""
    url = f"{GRAPH_API_BASE}/me/todo/lists/{list_id}/tasks"
    payload = {"title": title}
    if due_date:
        payload["dueDateTime"] = {"dateTime": due_date, "timeZone": "UTC"}
    resp = session.post(url, headers=_headers(token), json=payload)
    resp.raise_for_status()
    return resp.json()
