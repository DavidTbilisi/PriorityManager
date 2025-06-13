import os
from click.testing import CliRunner
from priority_manager.commands.ls import list_tasks
from priority_manager.utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]

def test_list_tasks(setup_dirs, sample_task_file):
    runner = CliRunner()
    result = runner.invoke(list_tasks)
    assert result.exit_code == 0
    assert "sample_task" in result.output
    assert "10" in result.output
