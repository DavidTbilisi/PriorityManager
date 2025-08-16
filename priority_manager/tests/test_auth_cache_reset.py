from click.testing import CliRunner
from priority_manager.commands.auth import auth_command
from priority_manager.utils.ms_todo import _cache_path


def test_auth_reset_cache(monkeypatch, tmp_path):
    # Redirect cache path via env
    monkeypatch.setenv('PRIORITY_MANAGER_HOME', str(tmp_path))
    # create fake cache
    cache = _cache_path()
    cache.write_text('{}', encoding='utf-8')
    assert cache.exists()
    runner = CliRunner()
    res = runner.invoke(auth_command, ['--reset-cache', '--silent'])
    assert res.exit_code == 0
    assert 'Deleted cache' in res.output or 'No cache file present' in res.output
    # After deletion file gone
    assert not cache.exists()
