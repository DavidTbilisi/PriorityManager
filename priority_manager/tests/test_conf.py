from click.testing import CliRunner
from priority_manager.commands.conf import conf

# We avoid actually launching external editors by only using --show which prints path.

def test_conf_show(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(conf, ['--show'])
    assert result.exit_code == 0
    assert 'config.yaml' in result.output.lower()
