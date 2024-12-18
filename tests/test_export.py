import os
from click.testing import CliRunner
from commands.export import export_tasks
from utils.config import CONFIG


TASKS_DIR = CONFIG["directories"]["tasks_dir"]
EXPORT_CSV = CONFIG["export_files"]["csv"]

def test_export_tasks(setup_dirs, sample_task_file):
    runner = CliRunner()
    result = runner.invoke(export_tasks, ["csv"])
    assert result.exit_code == 0
    assert f"Tasks exported successfully to {EXPORT_CSV}" in result.output

    # Verify the export file was created
    assert os.path.exists(EXPORT_CSV)

    # Clean up export file
    os.remove(EXPORT_CSV)
