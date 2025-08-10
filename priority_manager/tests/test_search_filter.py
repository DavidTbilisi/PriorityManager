from click.testing import CliRunner
from priority_manager.commands.search_filter import search, filter_tasks
from priority_manager.utils.config import CONFIG
import os

TASKS_DIR = CONFIG["directories"]["tasks_dir"]

SAMPLE_CONTENT = """# Alpha Task\n\n**Name:** Alpha Task\n\n**Description:** First test task.\n\n**Priority Score:** 15\n\n**Due Date:** 2025-01-15\n\n**Tags:** alpha, test\n\n**Date Added:** 2024-06-01T14:30:00\n\n**Status:** In Progress\n"""
SAMPLE_CONTENT_2 = """# Beta Task\n\n**Name:** Beta Task\n\n**Description:** Second test task.\n\n**Priority Score:** 5\n\n**Due Date:** 2025-02-01\n\n**Tags:** beta, experiment\n\n**Date Added:** 2024-06-02T09:15:00\n\n**Status:** To Do\n"""

def _write(name, content):
    with open(os.path.join(TASKS_DIR, name), 'w') as f:
        f.write(content)


def test_search_keyword(setup_dirs):
    _write('alpha.md', SAMPLE_CONTENT)
    runner = CliRunner()
    res = runner.invoke(search, ['Alpha'])
    assert res.exit_code == 0
    assert 'Found in:' in res.output


def test_search_tag_only(setup_dirs):
    _write('alpha.md', SAMPLE_CONTENT)
    runner = CliRunner()
    res = runner.invoke(search, ['alpha', '--tag'])
    assert res.exit_code == 0
    assert 'Found in:' in res.output


def test_filter_priority_range(setup_dirs):
    _write('alpha.md', SAMPLE_CONTENT)
    _write('beta.md', SAMPLE_CONTENT_2)
    runner = CliRunner()
    res = runner.invoke(filter_tasks, ['--min-priority', '10'])
    assert res.exit_code == 0
    assert 'alpha.md' in res.output
    assert 'beta.md' not in res.output


def test_filter_by_tag(setup_dirs):
    _write('alpha.md', SAMPLE_CONTENT)
    _write('beta.md', SAMPLE_CONTENT_2)
    runner = CliRunner()
    res = runner.invoke(filter_tasks, ['--tag', 'beta'])
    assert res.exit_code == 0
    assert 'beta.md' in res.output
    assert 'alpha.md' not in res.output


def test_filter_no_results(setup_dirs):
    _write('alpha.md', SAMPLE_CONTENT)
    runner = CliRunner()
    res = runner.invoke(filter_tasks, ['--min-priority', '100'])
    assert res.exit_code == 0
    assert 'No tasks found matching the specified criteria.' in res.output
