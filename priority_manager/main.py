import click
from .commands.add import add
from .commands.edit import edit
from .commands.ls import list_tasks
from .commands.archive import archive
from .commands.export import export_tasks
from .commands.search_filter import search, filter_tasks
from .commands.gantt import gantt

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

if __name__ == "__main__":
    cli()
