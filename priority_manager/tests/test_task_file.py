"""Tests for the TaskFile dataclass — read/write round-trips and edge cases."""
import os
import pytest
from priority_manager.utils.task_file import TaskFile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_raw(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Round-trip: every known field is preserved
# ---------------------------------------------------------------------------

def test_round_trip_all_fields(tmp_path):
    p = tmp_path / "task.md"
    _write_raw(p, (
        "**Name:** My Task\n\n"
        "**List:** Work\n\n"
        "**Description:** Do something\n\n"
        "**Priority Score:** 12\n\n"
        "**Due Date:** 2026-06-01\n\n"
        "**Tags:** work, urgent\n\n"
        "**Date Added:** 2026-04-01T10:00:00\n\n"
        "**Date Edited:** 2026-04-10T15:30:00\n\n"
        "**Status:** In Progress\n"
    ))
    task = TaskFile.read(str(p))

    assert task.name == "My Task"
    assert task.list_name == "Work"
    assert task.description == "Do something"
    assert task.priority_score == 12
    assert task.due_date == "2026-06-01"
    assert task.tags == "work, urgent"
    assert task.date_added == "2026-04-01T10:00:00"
    assert task.date_edited == "2026-04-10T15:30:00"
    assert task.status == "In Progress"

    # Write and re-read
    out = tmp_path / "out.md"
    task.write(str(out))
    task2 = TaskFile.read(str(out))

    assert task2.name == task.name
    assert task2.list_name == task.list_name
    assert task2.description == task.description
    assert task2.priority_score == task.priority_score
    assert task2.due_date == task.due_date
    assert task2.tags == task.tags
    assert task2.date_added == task.date_added
    assert task2.date_edited == task.date_edited
    assert task2.status == task.status


# ---------------------------------------------------------------------------
# Name fallback when **Name:** is absent
# ---------------------------------------------------------------------------

def test_name_fallback_to_filename_stem(tmp_path):
    p = tmp_path / "my_task_file.md"
    _write_raw(p, "**Status:** To Do\n")
    task = TaskFile.read(str(p))
    assert task.name == "my_task_file"


# ---------------------------------------------------------------------------
# Invalid priority score is ignored (keeps default 0)
# ---------------------------------------------------------------------------

def test_invalid_priority_score_ignored(tmp_path):
    p = tmp_path / "t.md"
    _write_raw(p, "**Name:** X\n\n**Priority Score:** not_a_number\n\n**Status:** To Do\n")
    task = TaskFile.read(str(p))
    assert task.priority_score == 0


# ---------------------------------------------------------------------------
# Extra / unknown fields are preserved verbatim
# ---------------------------------------------------------------------------

def test_extra_fields_preserved_on_round_trip(tmp_path):
    p = tmp_path / "t.md"
    _write_raw(p, (
        "**Name:** X\n\n"
        "**Custom Field:** hello\n\n"
        "**Status:** To Do\n"
    ))
    task = TaskFile.read(str(p))
    assert task._extra == {"Custom Field": "hello"}

    out = tmp_path / "out.md"
    task.write(str(out))
    content = out.read_text(encoding="utf-8")
    assert "**Custom Field:** hello" in content


# ---------------------------------------------------------------------------
# write() raises when no filepath provided
# ---------------------------------------------------------------------------

def test_write_raises_without_filepath():
    task = TaskFile(name="No path")
    with pytest.raises(ValueError, match="No filepath"):
        task.write()


# ---------------------------------------------------------------------------
# list_name is omitted from output when empty
# ---------------------------------------------------------------------------

def test_list_name_omitted_when_empty(tmp_path):
    task = TaskFile(name="X", status="To Do")
    out = tmp_path / "t.md"
    task.write(str(out))
    content = out.read_text(encoding="utf-8")
    assert "**List:**" not in content


def test_list_name_written_when_set(tmp_path):
    task = TaskFile(name="X", list_name="Personal", status="To Do")
    out = tmp_path / "t.md"
    task.write(str(out))
    assert "**List:** Personal" in out.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# date_added and date_edited omitted when empty
# ---------------------------------------------------------------------------

def test_dates_omitted_when_empty(tmp_path):
    task = TaskFile(name="X", status="To Do")
    out = tmp_path / "t.md"
    task.write(str(out))
    content = out.read_text(encoding="utf-8")
    assert "**Date Added:**" not in content
    assert "**Date Edited:**" not in content


# ---------------------------------------------------------------------------
# to_dict() compatibility with legacy get_task_details format
# ---------------------------------------------------------------------------

def test_to_dict_shape(tmp_path):
    p = tmp_path / "2026-04-17T12-00-00_my_task.md"
    _write_raw(p, (
        "**Name:** My Task\n\n"
        "**Priority Score:** 8\n\n"
        "**Status:** To Do\n"
    ))
    task = TaskFile.read(str(p))
    d = task.to_dict()

    assert d["Task Name"] == "My Task"
    assert d["Priority Score"] == 8
    assert d["Status"] == "To Do"
    assert d["Filepath"] == str(p)
    # Start date extracted from filename
    assert d["Start Date"] == "2026-04-17"


# ---------------------------------------------------------------------------
# Encoding: UTF-8 content written and read correctly
# ---------------------------------------------------------------------------

def test_unicode_name_round_trip(tmp_path):
    task = TaskFile(name="Täsk wïth ünïcödé", status="To Do", priority_score=5)
    out = tmp_path / "unicode.md"
    task.write(str(out))
    task2 = TaskFile.read(str(out))
    assert task2.name == "Täsk wïth ünïcödé"


# ---------------------------------------------------------------------------
# Mutating and re-writing updates only changed fields
# ---------------------------------------------------------------------------

def test_partial_update_preserves_other_fields(tmp_path):
    p = tmp_path / "t.md"
    _write_raw(p, (
        "**Name:** Original\n\n"
        "**List:** Work\n\n"
        "**Description:** Original desc\n\n"
        "**Priority Score:** 7\n\n"
        "**Due Date:** 2026-12-31\n\n"
        "**Tags:** tag1\n\n"
        "**Date Added:** 2026-01-01T00:00:00\n\n"
        "**Status:** To Do\n"
    ))
    task = TaskFile.read(str(p))
    task.name = "Updated"
    task.write()

    task2 = TaskFile.read(str(p))
    assert task2.name == "Updated"
    assert task2.list_name == "Work"
    assert task2.date_added == "2026-01-01T00:00:00"
    assert task2.priority_score == 7
