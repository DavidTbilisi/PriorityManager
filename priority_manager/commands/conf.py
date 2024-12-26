# Edit configurations in priority_manager/commands/conf.py:
import click
from ..utils.config import CONFIG_PATH


@click.command(name="cnf", help="Edit configurations.")
@click.option("--open", is_flag=True, help="Open the configuration file in the default editor.")
@click.option("--show", is_flag=True, help="Show the path to the configuration file.")
def conf(open, show):
    """Edit configurations."""
    if open:
        click.launch(CONFIG_PATH, wait=True, locate=True)
    elif show:
        click.echo(CONFIG_PATH)
    else:
        click.launch(CONFIG_PATH, wait=True)
        click.echo("Opened the configuration file in the default editor.")
        click.echo("Please make sure to restart the application after editing the configuration file.")
