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
    assert 'MS_TODO_TOKEN is not set' in res.output
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
