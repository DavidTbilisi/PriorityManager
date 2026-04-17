"""Tests for priority input validation (1-5 clamping with re-prompt)."""
import pytest
from click.testing import CliRunner
from priority_manager.commands.add import add
from priority_manager.utils.config import CONFIG
import os


TASKS_DIR = CONFIG["directories"]["tasks_dir"]


def test_add_valid_priority_range(setup_dirs):
    """Values 1-5 accepted without re-prompting."""
    runner = CliRunner()
    # urgency=1, importance=5, effort=3 → 1*2 + 5*3 - 3 = 14
    result = runner.invoke(add, ["Valid Range"], input="1\n5\n3\nDesc\nNo due date\n\nTo Do\n")
    assert result.exit_code == 0, result.output
    files = os.listdir(TASKS_DIR)
    assert len(files) == 1
    with open(os.path.join(TASKS_DIR, files[0]), encoding="utf-8") as f:
        content = f.read()
    assert "**Priority Score:** 14" in content


def test_add_out_of_range_reprompts(setup_dirs):
    """Value 0 is out of range → re-prompt then accept 3."""
    runner = CliRunner()
    # urgency: enter 0 (invalid) then 3; importance=3, effort=3 → 3*2+3*3-3=12
    result = runner.invoke(add, ["Reprompt Task"], input="0\n3\n3\n3\nDesc\nNo due date\n\nTo Do\n")
    assert result.exit_code == 0, result.output
    assert "Please enter a value between 1 and 5" in result.output
    files = os.listdir(TASKS_DIR)
    assert len(files) == 1
    with open(os.path.join(TASKS_DIR, files[0]), encoding="utf-8") as f:
        content = f.read()
    assert "**Priority Score:** 12" in content


def test_add_value_above_5_reprompts(setup_dirs):
    """Value 6 is out of range → re-prompt then accept 5."""
    runner = CliRunner()
    # urgency: 6 (invalid) then 5; importance=5, effort=1 → 5*2+5*3-1=24
    result = runner.invoke(add, ["High Priority"], input="6\n5\n5\n1\nDesc\nNo due date\n\nTo Do\n")
    assert result.exit_code == 0, result.output
    assert "Please enter a value between 1 and 5" in result.output
    files = os.listdir(TASKS_DIR)
    assert len(files) == 1
    with open(os.path.join(TASKS_DIR, files[0]), encoding="utf-8") as f:
        content = f.read()
    assert "**Priority Score:** 24" in content
