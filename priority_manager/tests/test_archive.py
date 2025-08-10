import os
from click.testing import CliRunner
from priority_manager.commands.archive import archive
from priority_manager.utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]

def test_archive_task(setup_dirs, sample_task_file):
    runner = CliRunner()
    result = runner.invoke(archive, input="1\n")
    assert result.exit_code == 0
    assert "Task archived:" in result.output
    assert os.listdir(TASKS_DIR) == []
    archived_files = os.listdir(ARCHIVE_DIR)
    assert len(archived_files) == 1
    assert archived_files[0].endswith('.md')
