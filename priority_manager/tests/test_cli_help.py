from click.testing import CliRunner
from priority_manager.main import cli

# Ensure each command is listed in root help and its own help works
COMMANDS = [
    'add', 'edit', 'ls', 'archive', 'export', 'search', 'filter', 'gantt', 'cnf', 'sync'
]

def test_root_help_lists_commands():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    for cmd in COMMANDS:
        assert cmd in result.output


def test_each_subcommand_help():
    runner = CliRunner()
    for cmd in COMMANDS:
        result = runner.invoke(cli, [cmd, '--help'])
        assert result.exit_code == 0, f"--help failed for {cmd}: {result.output}"
