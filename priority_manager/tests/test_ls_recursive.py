import os
from click.testing import CliRunner
from priority_manager.commands.ls import list_tasks
from priority_manager.utils.config import CONFIG


def test_ls_auto_recursive(monkeypatch, tmp_path):
    # Setup nested folder scenario
    tasks_root = tmp_path / 'tasks'
    tasks_root.mkdir()
    CONFIG['directories']['tasks_dir'] = str(tasks_root)
    sub = tasks_root / 'List_Alpha'
    sub.mkdir()
    sample = sub / '2025-01-01_Task.md'
    sample.write_text("**Name:** Sample Task\n\n**Priority Score:** 1\n\n**Status:** To Do\n\n", encoding='utf-8')

    runner = CliRunner()
    res = runner.invoke(list_tasks)
    assert res.exit_code == 0
    assert 'Sample Task' in res.output


def test_ls_recursive_flag(monkeypatch, tmp_path):
    tasks_root = tmp_path / 'tasks'
    tasks_root.mkdir()
    CONFIG['directories']['tasks_dir'] = str(tasks_root)
    sub = tasks_root / 'Beta'
    sub.mkdir()
    (sub / '2025-01-01_TaskB.md').write_text("**Name:** Task B\n\n**Priority Score:** 2\n\n**Status:** To Do\n\n", encoding='utf-8')

    runner = CliRunner()
    res = runner.invoke(list_tasks, ['--recursive'])
    assert res.exit_code == 0
    assert 'Task B' in res.output
