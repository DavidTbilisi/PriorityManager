import os
from click.testing import CliRunner
from commands.edit import edit
from utils.config import CONFIG


TASKS_DIR = CONFIG["directories"]["tasks_dir"]

def test_edit_task(setup_dirs, sample_task_file):
    runner = CliRunner()
    result = runner.invoke(edit, input="1\nNew Task Name\nNew description\n2024-11-01\nnew, edited\nn\n")
    assert result.exit_code == 0
    assert "Task edited successfully" in result.output

    # Verify the changes in the task file
    with open(sample_task_file, "r") as f:
        content = f.read()
        assert "New Task Name" in content
        assert "New description" in content
        assert "2024-11-01" in content
        assert "new, edited" in content
