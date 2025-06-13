import os
from click.testing import CliRunner
from priority_manager.commands.add import add
from priority_manager.utils.config import CONFIG


TASKS_DIR = CONFIG["directories"]["tasks_dir"]

def test_add_task(setup_dirs):
    runner = CliRunner()
    result = runner.invoke(add, ["Test Task"], input="3\n4\n2\nTest description\n2024-12-31\nwork, urgent\nTo Do\n")
    assert result.exit_code == 0
    assert "Task added successfully" in result.output

    # Verify the task file was created
    files = os.listdir(TASKS_DIR)
    assert len(files) == 1
    assert files[0].endswith(".md")
    with open(os.path.join(TASKS_DIR, files[0])) as f:
        content = f.read()
    assert "**Name:** Test Task" in content
