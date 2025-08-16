import click
from .commands.add import add
from .commands.edit import edit
from .commands.ls import list_tasks
from .commands.archive import archive
from .commands.export import export_tasks
from .commands.todo import sync_tasks
from .commands.search_filter import search, filter_tasks
from .commands.gantt import gantt
from .commands.conf import conf
from .commands.auth import auth_command

@click.group()
def cli():
    pass

cli.add_command(add)
cli.add_command(edit)
cli.add_command(list_tasks)
cli.add_command(archive)
cli.add_command(export_tasks)
cli.add_command(search)
cli.add_command(filter_tasks)
cli.add_command(gantt)
cli.add_command(conf)
cli.add_command(sync_tasks)
cli.add_command(auth_command)

if __name__ == "__main__":
    cli()
