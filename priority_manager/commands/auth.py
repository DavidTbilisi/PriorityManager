import os
import click
from ..utils.ms_todo import get_access_token, _cache_path
from ..utils.config import CONFIG

@click.command(name="auth", help="Authenticate with Microsoft To Do via device code (MSAL). Caches token.")
@click.option("--silent", is_flag=True, help="Only use cached token; do not start device flow.")
@click.option("--reset-cache", is_flag=True, help="Delete the MSAL token cache before attempting auth.")
@click.option("--show-config", is_flag=True, help="Show effective client_id and tenant then exit.")
def auth_command(silent, reset_cache, show_config):
    if show_config:
        section = CONFIG.get('ms_todo', {}) if isinstance(CONFIG.get('ms_todo'), dict) else {}
        client_id = section.get('client_id') or 'DEFAULT_GRAPH_EXPLORER'
        tenant = section.get('tenant') or 'common'
        click.echo(f"client_id={client_id}\ntenant={tenant}")
        return

    if reset_cache:
        cache_file = _cache_path()
        if cache_file.exists():
            try:
                cache_file.unlink()
                click.echo(f"Deleted cache: {cache_file}")
            except Exception as e:
                click.echo(f"Failed to delete cache: {e}")
        else:
            click.echo("No cache file present.")
        if silent:
            return  # user only wanted reset

    token = get_access_token(prefer_msal=True, silent_only=silent)
    if token:
        if silent:
            click.echo("Cached token available.")
        else:
            click.echo("Authentication successful; token cached.")
    else:
        if silent:
            click.echo("No cached token found.")
        else:
            click.echo("Authentication not completed.")
            click.echo("If you see errors like 'No state or url query parameter provided':")
            click.echo("  - Ensure device code flow was followed fully in the browser.")
            click.echo("  - Remove any stale ms_todo.token in config.yaml to allow MSAL cache usage.")
            click.echo("  - Optionally set your own Azure AD app client_id & tenant in config.yaml (public client).")
