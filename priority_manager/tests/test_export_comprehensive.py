"""Tests verifying export correctly reads task names via **Name:** field."""
import csv
import json
import os
import pytest
import yaml
from click.testing import CliRunner
from priority_manager.commands.export import export_tasks
from priority_manager.utils.config import CONFIG
from priority_manager.utils.task_file import TaskFile


TASKS_DIR = CONFIG["directories"]["tasks_dir"]


def _make_task(filename, **kwargs):
    path = os.path.join(TASKS_DIR, filename)
    task = TaskFile(
        name=kwargs.get("name", "Test Task"),
        description=kwargs.get("description", "A description"),
        priority_score=kwargs.get("priority_score", 5),
        due_date=kwargs.get("due_date", "2026-12-31"),
        tags=kwargs.get("tags", ""),
        date_added=kwargs.get("date_added", "2026-01-01T00:00:00"),
        status=kwargs.get("status", "To Do"),
        list_name=kwargs.get("list_name", ""),
        filepath=path,
    )
    task.write()
    return path


# ---------------------------------------------------------------------------
# Task name bug fix: must use **Name:** not # heading
# ---------------------------------------------------------------------------

def test_export_csv_includes_correct_task_name(setup_dirs, tmp_path):
    _make_task("task.md", name="Correctly Named Task")
    runner = CliRunner()
    export_file = str(tmp_path / "out")
    result = runner.invoke(export_tasks, ["csv", "--output", export_file])
    assert result.exit_code == 0, result.output

    out_path = export_file + ".csv"
    assert os.path.exists(out_path)
    with open(out_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["Task Name"] == "Correctly Named Task"


def test_export_json_includes_correct_task_name(setup_dirs, tmp_path):
    _make_task("task.md", name="JSON Task")
    runner = CliRunner()
    export_file = str(tmp_path / "out")
    result = runner.invoke(export_tasks, ["json", "--output", export_file])
    assert result.exit_code == 0, result.output

    with open(export_file + ".json", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["Task Name"] == "JSON Task"


def test_export_yaml_includes_correct_task_name(setup_dirs, tmp_path):
    _make_task("task.md", name="YAML Task")
    runner = CliRunner()
    export_file = str(tmp_path / "out")
    result = runner.invoke(export_tasks, ["yaml", "--output", export_file])
    assert result.exit_code == 0, result.output

    with open(export_file + ".yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data[0]["Task Name"] == "YAML Task"


# ---------------------------------------------------------------------------
# Multiple tasks exported
# ---------------------------------------------------------------------------

def test_export_multiple_tasks(setup_dirs, tmp_path):
    _make_task("a.md", name="Alpha", priority_score=10, status="To Do")
    _make_task("b.md", name="Beta", priority_score=5, status="In Progress")
    runner = CliRunner()
    export_file = str(tmp_path / "out")
    result = runner.invoke(export_tasks, ["json", "--output", export_file])
    assert result.exit_code == 0, result.output

    with open(export_file + ".json", encoding="utf-8") as f:
        data = json.load(f)
    names = {d["Task Name"] for d in data}
    assert names == {"Alpha", "Beta"}


# ---------------------------------------------------------------------------
# All CSV fields present
# ---------------------------------------------------------------------------

def test_export_csv_has_all_fields(setup_dirs, tmp_path):
    _make_task("task.md", name="Full Fields", tags="work", list_name="My List")
    runner = CliRunner()
    export_file = str(tmp_path / "out")
    runner.invoke(export_tasks, ["csv", "--output", export_file])

    with open(export_file + ".csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    assert "Task Name" in fieldnames
    assert "Description" in fieldnames
    assert "Priority Score" in fieldnames
    assert "Due Date" in fieldnames
    assert "Status" in fieldnames
    assert "Tags" in fieldnames
    assert "List" in fieldnames
    assert rows[0]["Tags"] == "work"
    assert rows[0]["List"] == "My List"


# ---------------------------------------------------------------------------
# Empty tasks dir
# ---------------------------------------------------------------------------

def test_export_no_tasks(setup_dirs):
    runner = CliRunner()
    result = runner.invoke(export_tasks, ["csv"])
    assert result.exit_code == 0
    assert "No tasks found" in result.output
