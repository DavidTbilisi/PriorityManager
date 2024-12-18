import os
from click.testing import CliRunner
from commands.ls import list_tasks
from utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]

def test_list_tasks(setup_dirs, sample_task_file):
    runner = CliRunner()
    result = runner.invoke(list_tasks)
    assert result.exit_code == 0
    assert "1. sample_task.md" in result.output
    assert "Priority Score: 10" in result.output
