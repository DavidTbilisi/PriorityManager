import os
from click.testing import CliRunner
from commands.add import add
from utils.config import CONFIG


TASKS_DIR = CONFIG["directories"]["tasks_dir"]

def test_add_task(setup_dirs):
    runner = CliRunner()
    result = runner.invoke(add, ["Test Task"], input="3\n4\n2\nTest description\n2024-12-31\nwork, urgent\nTo Do\n")
    assert result.exit_code == 0
    assert "Task added successfully" in result.output

    # Verify the task file was created
    files = os.listdir(TASKS_DIR)
    assert len(files) == 1
    assert "Test_Task" in files[0]
