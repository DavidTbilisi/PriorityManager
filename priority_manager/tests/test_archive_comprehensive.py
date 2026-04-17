"""Tests verifying archive uses CONFIG dirs (not hardcoded 'tasks'/'archive')."""
import os
import pytest
from click.testing import CliRunner
from priority_manager.commands.archive import archive
from priority_manager.utils.config import CONFIG
from priority_manager.utils.task_file import TaskFile


TASKS_DIR = CONFIG["directories"]["tasks_dir"]
ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]


def _make_task(filename, name="Test Task"):
    path = os.path.join(TASKS_DIR, filename)
    TaskFile(name=name, status="To Do", filepath=path).write()
    return path


def test_archive_uses_config_dirs(setup_dirs):
    """Archived file must land in CONFIG archive_dir, not hardcoded 'archive'."""
    _make_task("task.md", name="Archive Me")
    runner = CliRunner()
    result = runner.invoke(archive, input="1\n")
    assert result.exit_code == 0, result.output
    assert "Task archived:" in result.output

    # File moved out of tasks dir
    assert os.listdir(TASKS_DIR) == []
    # File present in CONFIG archive dir (not hardcoded)
    archived = os.listdir(ARCHIVE_DIR)
    assert len(archived) == 1
    assert archived[0] == "task.md"


def test_archive_shows_task_name_not_filename(setup_dirs):
    _make_task("ugly_filename_123.md", name="Pretty Task Name")
    runner = CliRunner()
    result = runner.invoke(archive, input="1\n")
    assert result.exit_code == 0, result.output
    assert "Pretty Task Name" in result.output


def test_archive_invalid_choice_rejected(setup_dirs):
    _make_task("task.md", name="Solo Task")
    runner = CliRunner()
    result = runner.invoke(archive, input="99\n")
    assert result.exit_code == 0
    assert "Invalid choice" in result.output
    # File not moved
    assert len(os.listdir(TASKS_DIR)) == 1


def test_archive_no_tasks(setup_dirs):
    runner = CliRunner()
    result = runner.invoke(archive)
    assert result.exit_code == 0
    assert "No tasks found" in result.output


def test_archive_multiple_tasks_selects_correct_one(setup_dirs):
    _make_task("first.md", name="First Task")
    _make_task("second.md", name="Second Task")
    runner = CliRunner()
    # Files are sorted by os.listdir; archive whichever is at index 1
    files = [f for f in os.listdir(TASKS_DIR) if os.path.isfile(os.path.join(TASKS_DIR, f))]
    result = runner.invoke(archive, input="1\n")
    assert result.exit_code == 0, result.output
    # One file moved
    assert len(os.listdir(TASKS_DIR)) == 1
    assert len(os.listdir(ARCHIVE_DIR)) == 1
