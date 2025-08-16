import os
import json
import click
import requests
from pathlib import Path
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

# MSAL constants / defaults
DEFAULT_SCOPES = ["Tasks.ReadWrite"]
DEFAULT_TENANT = "common"  # can be overridden in config ms_todo.tenant
DEFAULT_CLIENT_ID = "04f0c124-f2bc-4f59-8241-bf6df9866bbd"  # Microsoft Graph Explorer public client (used if user does not supply one)

# Token cache path (user config dir). Do not commit this file.
CACHE_FILENAME = ".msal_token_cache.json"
APP_DIR_ENV = "PRIORITY_MANAGER_HOME"

def _app_storage_dir():
    base = os.getenv(APP_DIR_ENV)
    if base:
        return Path(base)
    # default: project root directory (CONFIG already loaded) -> place beside config.yaml
    # Try to locate config.yaml directory
    try:
        from .config import CONFIG_PATH  # optional if defined
        return Path(CONFIG_PATH).parent
    except Exception:
        return Path.cwd()

def _cache_path():
    return _app_storage_dir() / CACHE_FILENAME

def _load_cache():
    p = _cache_path()
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(data):
    p = _cache_path()
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

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

def get_access_token(prefer_msal: bool = True, silent_only: bool = False):
    """Retrieve an access token using MSAL device code flow with caching.

    Workflow:
      1. If legacy token (env/config) present -> return it (backward compatibility).
      2. If prefer_msal True: attempt cached MSAL token.
      3. If not silent_only and no valid cache -> start device code flow prompting user.
      4. Cache result (refresh + access token metadata) for reuse.

    silent_only is used by non-interactive commands to avoid blocking for auth.
    Use `priority-manager auth` command (to be implemented) to force interactive device flow.
    """
    # Prefer MSAL cache first so a stale manual token in config does not override refreshed device-flow tokens.
    try:
        import msal  # local import so missing dependency doesn't break other paths
    except Exception:
        # Fallback to legacy only if msal missing
        return get_token(show_help=False)

    if not prefer_msal:
        return get_token(show_help=False)

    cfg_section = CONFIG.get("ms_todo", {}) if isinstance(CONFIG.get("ms_todo"), dict) else {}
    client_id = cfg_section.get("client_id") or DEFAULT_CLIENT_ID
    tenant = cfg_section.get("tenant") or DEFAULT_TENANT
    authority = f"https://login.microsoftonline.com/{tenant}"

    cache_data = _load_cache()
    cache = msal.SerializableTokenCache()
    if cache_data:
        try:
            cache.deserialize(json.dumps(cache_data))
        except Exception:
            pass

    app = msal.PublicClientApplication(client_id=client_id, authority=authority, token_cache=cache)

    # Attempt silent
    accounts = app.get_accounts()
    if accounts:
        for acct in accounts:
            result = app.acquire_token_silent(DEFAULT_SCOPES, account=acct)
            if result and "access_token" in result:
                return result["access_token"]

    if silent_only:
        # As a last resort, legacy token (may be stale)
        legacy = get_token(show_help=False)
        return legacy

    # Interactive device code flow
    try:
        flow = app.initiate_device_flow(scopes=DEFAULT_SCOPES)
    except Exception as e:
        click.secho(f"Failed to initiate device flow: {e}", fg="red")
        return None
    if "user_code" not in flow:
        click.secho("Device flow initiation failed (no user_code).", fg="red")
        return None
    click.echo("Authenticate with Microsoft To Do:")
    click.echo(flow.get("message"))
    click.echo("(You can run 'priority-manager auth' later; this will be cached.)")
    result = app.acquire_token_by_device_flow(flow)
    if result and "access_token" in result:
        # persist cache
        try:
            _save_cache(json.loads(cache.serialize()))
        except Exception:
            pass
        return result["access_token"]
    error = result.get('error') if isinstance(result, dict) else 'unknown'
    click.secho(f"Device flow failed: {error}", fg='red')
    # Fallback to legacy token if present
    return get_token(show_help=False)

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


def get_lists(session, token):
    """Return all To Do lists (raw JSON value array)."""
    url = f"{GRAPH_API_BASE}/me/todo/lists"
    resp = session.get(url, headers=_headers(token))
    resp.raise_for_status()
    return resp.json().get("value", [])
