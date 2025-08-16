import os
from click.testing import CliRunner
from priority_manager.commands.todo import sync_tasks
from priority_manager.utils.config import CONFIG


def test_sync_pull_all_lists_folders(monkeypatch, tmp_path):
    # Setup tasks dir
    base = tmp_path / 'tasks'
    base.mkdir()
    CONFIG['directories']['tasks_dir'] = str(base)
    CONFIG.setdefault('ms_todo', {})['token'] = 'OK'

    lists = [
        {'id': 'L1', 'displayName': 'List Alpha'},
        {'id': 'L2', 'displayName': 'List Beta'},
    ]
    tasks_alpha = [{'title': 'Alpha Task 1'}, {'title': 'Shared Title'}]
    tasks_beta = [{'title': 'Beta Task 1'}, {'title': 'Shared Title'}]

    from priority_manager.commands import todo as todo_module
    monkeypatch.setattr(todo_module, 'get_lists', lambda *a, **k: lists)
    def fake_get_tasks(session, token, list_id):
        return tasks_alpha if list_id == 'L1' else tasks_beta
    monkeypatch.setattr(todo_module, 'get_tasks', fake_get_tasks)
    monkeypatch.setattr(todo_module, 'create_task', lambda *a, **k: None)
    monkeypatch.setattr(todo_module, 'get_or_create_list', lambda *a, **k: 'L1')

    runner = CliRunner()
    res = runner.invoke(sync_tasks, ['--pull', '--all-lists', '--folders'])
    assert res.exit_code == 0
    # Expect two subdirectories
    dirs = sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])
    assert len(dirs) == 2
    # Each directory should have 2 files
    for d in dirs:
        files = os.listdir(os.path.join(base, d))
        assert len(files) == 2
        content = "\n".join(open(os.path.join(base, d, f), encoding='utf-8').read() for f in files)
        assert '**List:**' in content
