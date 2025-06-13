import os
import requests

GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
LIST_NAME = "Priority Manager"

def get_token():
    """Retrieve Microsoft Graph access token from environment."""
    token = os.getenv("MS_TODO_TOKEN")
    if not token:
        raise RuntimeError("MS_TODO_TOKEN environment variable is not set")
    return token

def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

def get_or_create_list(session, token):
    """Return the ID of the task list creating it if necessary."""
    url = f"{GRAPH_API_BASE}/me/todo/lists"
    resp = session.get(url, headers=_headers(token))
    resp.raise_for_status()
    lists = resp.json().get("value", [])
    for lst in lists:
        if lst.get("displayName") == LIST_NAME:
            return lst["id"]
    # create list if not found
    resp = session.post(url, headers=_headers(token), json={"displayName": LIST_NAME})
    resp.raise_for_status()
    return resp.json()["id"]

def get_tasks(session, token, list_id):
    url = f"{GRAPH_API_BASE}/me/todo/lists/{list_id}/tasks"
    resp = session.get(url, headers=_headers(token))
    resp.raise_for_status()
    return resp.json().get("value", [])

def create_task(session, token, list_id, title, due_date=None):
    url = f"{GRAPH_API_BASE}/me/todo/lists/{list_id}/tasks"
    payload = {"title": title}
    if due_date:
        payload["dueDateTime"] = {"dateTime": due_date, "timeZone": "UTC"}
    resp = session.post(url, headers=_headers(token), json=payload)
    resp.raise_for_status()
    return resp.json()
