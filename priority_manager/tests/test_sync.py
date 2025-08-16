from click.testing import CliRunner
from priority_manager.commands.todo import sync_tasks
from priority_manager.utils.config import CONFIG
from priority_manager.utils.ms_todo import get_token
import os


def test_sync_missing_token(monkeypatch):
    # Ensure neither env nor config supplies a token
    monkeypatch.delenv('MS_TODO_TOKEN', raising=False)
    CONFIG.setdefault('ms_todo', {})['token'] = ""
    runner = CliRunner()
    res = runner.invoke(sync_tasks)
    assert res.exit_code == 0
    assert 'No access token available.' in res.output
    assert "priority-manager auth" in res.output
    assert 'Aborting sync; token required.' in res.output


def test_get_token_from_config(monkeypatch):
    # Env absent; config provides token
    monkeypatch.delenv('MS_TODO_TOKEN', raising=False)
    CONFIG.setdefault('ms_todo', {})['token'] = "TEST_CONFIG_TOKEN"
    token = get_token(show_help=False)
    assert token == "TEST_CONFIG_TOKEN"


def test_sync_pull_creates_files(monkeypatch, tmp_path):
    # Point tasks dir to temp
    test_dir = tmp_path / 'tasks'
    test_dir.mkdir()
    CONFIG['directories']['tasks_dir'] = str(test_dir)
    # Provide token via config
    monkeypatch.delenv('MS_TODO_TOKEN', raising=False)
    CONFIG.setdefault('ms_todo', {})['token'] = "TEST_CONFIG_TOKEN"

    # Mock network functions
    def fake_get_or_create_list(session, token):
        return 'list123'

    remote_sample = [
        {'title': 'Remote Task A'},
        {'title': 'Remote Task B', 'dueDateTime': {'dateTime': '2030-01-01', 'timeZone': 'UTC'}},
    ]

    def fake_get_tasks(session, token, list_id):
        return remote_sample

    # Monkeypatch imports inside command
    monkeypatch.setenv('TEST_MODE', 'true')
    monkeypatch.setenv('PYTHONHASHSEED', '0')
    from priority_manager.commands import todo as todo_module
    monkeypatch.setattr(todo_module, 'get_or_create_list', fake_get_or_create_list)
    monkeypatch.setattr(todo_module, 'get_tasks', fake_get_tasks)
    monkeypatch.setattr(todo_module, 'create_task', lambda *a, **k: None)

    runner = CliRunner()
    res = runner.invoke(sync_tasks, ['--pull'])
    assert res.exit_code == 0
    files = list(os.listdir(test_dir))
    assert len(files) == 2
    names = '\n'.join(open(os.path.join(test_dir, f), encoding='utf-8').read() for f in files)
    assert 'Remote Task A' in names
    assert 'Remote Task B' in names


def test_sync_unauthorized(monkeypatch, tmp_path):
    # Setup tasks dir
    test_dir = tmp_path / 'tasks'
    test_dir.mkdir()
    CONFIG['directories']['tasks_dir'] = str(test_dir)
    # Token present but will cause 401
    CONFIG.setdefault('ms_todo', {})['token'] = 'EXPIRED'
    from requests import HTTPError, Response

    def fake_get_or_create_list(session, token):
        r = Response()
        r.status_code = 401
        r._content = b'{"error":"invalid_token"}'
        raise HTTPError(response=r)

    def fake_get_tasks(*a, **k):
        return []

    from priority_manager.commands import todo as todo_module
    monkeypatch.setattr(todo_module, 'get_or_create_list', fake_get_or_create_list)
    monkeypatch.setattr(todo_module, 'get_tasks', fake_get_tasks)
    monkeypatch.setattr(todo_module, 'create_task', lambda *a, **k: None)
    runner = CliRunner()
    res = runner.invoke(sync_tasks, ['--pull', '--verbose'])
    assert res.exit_code == 0
    assert 'Unauthorized (401)' in res.output
    assert 'invalid_token' in res.output


def test_sync_pull_all_lists(monkeypatch, tmp_path):
    # Setup tasks dir (capture original to restore)
    original_tasks_dir = CONFIG['directories']['tasks_dir']
    test_dir = tmp_path / 'tasks'
    test_dir.mkdir()
    CONFIG['directories']['tasks_dir'] = str(test_dir)
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
    # create_task unused in pull-only test
    monkeypatch.setattr(todo_module, 'create_task', lambda *a, **k: None)
    # get_or_create_list for push path still needed
    monkeypatch.setattr(todo_module, 'get_or_create_list', lambda *a, **k: 'L1')

    runner = CliRunner()
    res = runner.invoke(sync_tasks, ['--pull', '--all-lists'])
    assert res.exit_code == 0
    files = os.listdir(test_dir)
    # Should create 4 files, but duplicate Shared Title appears twice with different lists
    assert len(files) == 4
    content = "\n".join(open(os.path.join(test_dir, f), encoding='utf-8').read() for f in files)
    assert '**List:** List Alpha' in content
    assert '**List:** List Beta' in content
    # Restore CONFIG to avoid leaking temp path to later tests
    CONFIG['directories']['tasks_dir'] = original_tasks_dir
