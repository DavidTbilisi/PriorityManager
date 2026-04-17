"""Comprehensive edit command tests covering the bugs that were fixed."""
import os
import pytest
from click.testing import CliRunner
from priority_manager.commands.edit import edit
from priority_manager.utils.config import CONFIG
from priority_manager.utils.task_file import TaskFile


TASKS_DIR = CONFIG["directories"]["tasks_dir"]


def _make_task(filename, **kwargs):
    """Write a task file directly to TASKS_DIR using TaskFile."""
    path = os.path.join(TASKS_DIR, filename)
    task = TaskFile(
        name=kwargs.get("name", "Default Task"),
        list_name=kwargs.get("list_name", "My List"),
        description=kwargs.get("description", "A description"),
        priority_score=kwargs.get("priority_score", 5),
        due_date=kwargs.get("due_date", "2026-12-31"),
        tags=kwargs.get("tags", "tag1, tag2"),
        date_added=kwargs.get("date_added", "2026-01-01T00:00:00"),
        status=kwargs.get("status", "To Do"),
        filepath=path,
    )
    task.write()
    return path


# ---------------------------------------------------------------------------
# Data preservation (the critical bug fix)
# ---------------------------------------------------------------------------

def test_edit_preserves_date_added(setup_dirs):
    _make_task("task.md", date_added="2026-01-01T00:00:00", name="Preserve Me")
    runner = CliRunner()
    # Select task 1, change name, keep rest defaults, skip priority update
    result = runner.invoke(edit, input="1\nNew Name\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    task = TaskFile.read(os.path.join(TASKS_DIR, "task.md"))
    assert task.date_added == "2026-01-01T00:00:00"


def test_edit_preserves_list_name(setup_dirs):
    _make_task("task.md", list_name="Work", name="List Task")
    runner = CliRunner()
    result = runner.invoke(edit, input="1\nList Task\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    task = TaskFile.read(os.path.join(TASKS_DIR, "task.md"))
    assert task.list_name == "Work"


def test_edit_sets_date_edited(setup_dirs):
    _make_task("task.md", name="Edit Me")
    runner = CliRunner()
    result = runner.invoke(edit, input="1\nEdit Me\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    task = TaskFile.read(os.path.join(TASKS_DIR, "task.md"))
    assert task.date_edited != ""


def test_edit_preserves_extra_fields(setup_dirs):
    path = os.path.join(TASKS_DIR, "task.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "**Name:** Custom Fields Task\n\n"
            "**Description:** desc\n\n"
            "**Priority Score:** 5\n\n"
            "**Due Date:** No due date\n\n"
            "**Tags:** \n\n"
            "**Date Added:** 2026-01-01T00:00:00\n\n"
            "**MyCustomField:** preserved_value\n\n"
            "**Status:** To Do\n"
        )
    runner = CliRunner()
    result = runner.invoke(edit, input="1\nCustom Fields Task\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    task = TaskFile.read(path)
    assert task._extra.get("MyCustomField") == "preserved_value"


# ---------------------------------------------------------------------------
# Validation loop fix
# ---------------------------------------------------------------------------

def test_edit_invalid_choice_reprompts(setup_dirs):
    _make_task("task.md", name="Only Task")
    runner = CliRunner()
    # Enter 99 (invalid), then 1 (valid), then defaults
    result = runner.invoke(edit, input="99\n1\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "Invalid choice" in result.output
    assert "Task edited successfully" in result.output


def test_edit_choice_zero_reprompts(setup_dirs):
    _make_task("task.md", name="Only Task")
    runner = CliRunner()
    result = runner.invoke(edit, input="0\n1\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "Invalid choice" in result.output


# ---------------------------------------------------------------------------
# Filter options
# ---------------------------------------------------------------------------

def test_edit_filter_by_status(setup_dirs):
    _make_task("todo.md", name="Todo Task", status="To Do")
    _make_task("done.md", name="Done Task", status="Complete")
    runner = CliRunner()
    # Filter to Complete tasks only — only 1 result, select it, keep defaults
    result = runner.invoke(edit, ["--status", "Complete"], input="1\n\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "Done Task" in result.output
    # Todo Task should not appear
    assert "Todo Task" not in result.output


def test_edit_filter_by_name(setup_dirs):
    _make_task("alpha.md", name="Alpha Task")
    _make_task("beta.md", name="Beta Task")
    runner = CliRunner()
    result = runner.invoke(edit, ["--name", "Beta"], input="1\n\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "Beta Task" in result.output
    assert "Alpha Task" not in result.output


def test_edit_filter_by_tags(setup_dirs):
    _make_task("work.md", name="Work Task", tags="work, urgent")
    _make_task("personal.md", name="Personal Task", tags="personal")
    runner = CliRunner()
    result = runner.invoke(edit, ["--tags", "urgent"], input="1\n\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "Work Task" in result.output
    assert "Personal Task" not in result.output


def test_edit_filter_open_task(setup_dirs):
    _make_task("todo.md", name="Open Task", status="To Do")
    _make_task("progress.md", name="Progress Task", status="In Progress")
    runner = CliRunner()
    result = runner.invoke(edit, ["--open-task"], input="1\n\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "Open Task" in result.output
    assert "Progress Task" not in result.output


def test_edit_filter_in_progress(setup_dirs):
    _make_task("progress.md", name="WIP Task", status="In Progress")
    _make_task("todo.md", name="Pending Task", status="To Do")
    runner = CliRunner()
    result = runner.invoke(edit, ["--in-progress"], input="1\n\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "WIP Task" in result.output
    assert "Pending Task" not in result.output


def test_edit_filter_done(setup_dirs):
    _make_task("done.md", name="Done Task", status="Complete")
    _make_task("todo.md", name="Not Done", status="To Do")
    runner = CliRunner()
    result = runner.invoke(edit, ["--done"], input="1\n\n\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert "Done Task" in result.output
    assert "Not Done" not in result.output


def test_edit_filter_no_match_exits(setup_dirs):
    _make_task("task.md", name="My Task", status="To Do")
    runner = CliRunner()
    result = runner.invoke(edit, ["--status", "Blocked"])
    assert result.exit_code == 0
    assert "No tasks match" in result.output


# ---------------------------------------------------------------------------
# Empty tasks dir
# ---------------------------------------------------------------------------

def test_edit_no_tasks(setup_dirs):
    runner = CliRunner()
    result = runner.invoke(edit)
    assert result.exit_code == 0
    assert "No tasks found" in result.output


# ---------------------------------------------------------------------------
# Priority update path
# ---------------------------------------------------------------------------

def test_edit_update_priority(setup_dirs):
    _make_task("task.md", name="Priority Task", priority_score=3)
    runner = CliRunner()
    # Select task 1, keep name/desc/date/tags/status defaults, confirm priority update (y), enter 5,5,1
    result = runner.invoke(edit, input="1\n\n\n\n\n\ny\n5\n5\n1\n")
    assert result.exit_code == 0, result.output
    assert "Task edited successfully" in result.output
    task = TaskFile.read(os.path.join(TASKS_DIR, "task.md"))
    # 5*2 + 5*3 - 1 = 24
    assert task.priority_score == 24
