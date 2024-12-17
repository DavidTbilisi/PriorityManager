import click
from commands.add import add
from commands.edit import edit
from commands.list_tasks import list_tasks
from commands.archive import archive

@click.group()
def cli():
    pass

cli.add_command(add)
cli.add_command(edit)
cli.add_command(list_tasks)
cli.add_command(archive)

if __name__ == "__main__":
    cli()
