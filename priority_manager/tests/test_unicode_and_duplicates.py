import os
from click.testing import CliRunner
from priority_manager.commands.add import add
from priority_manager.commands.ls import list_tasks
from priority_manager.utils.config import CONFIG

TASKS_DIR = CONFIG['directories']['tasks_dir']

# Inputs: complexity(1-5), impact(1-5), urgency(1-5), description, due date, tags, status
UNICODE_NAME = 'Запланировать встречу'  # Cyrillic

def test_add_unicode_task(setup_dirs):
    runner = CliRunner()
    result = runner.invoke(add, [UNICODE_NAME], input="3\n4\n2\nОписание задачи\n2025-03-01\nwork, intl\nTo Do\n")
    assert result.exit_code == 0
    ls_res = runner.invoke(list_tasks)
    assert UNICODE_NAME in ls_res.output


def test_duplicate_task_names(setup_dirs):
    runner = CliRunner()
    result1 = runner.invoke(add, ['Duplicate Task'], input="3\n3\n3\nDesc1\n2025-01-01\nalpha\nTo Do\n")
    result2 = runner.invoke(add, ['Duplicate Task'], input="2\n2\n2\nDesc2\n2025-01-02\nalpha\nTo Do\n")
    assert result1.exit_code == 0
    assert result2.exit_code == 0
    files = os.listdir(TASKS_DIR)
    assert len(files) == 2  # Both tasks should exist with different timestamps in filename
