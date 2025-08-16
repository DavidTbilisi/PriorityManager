import os
from click.testing import CliRunner
from priority_manager.commands.add import add
from priority_manager.utils.config import CONFIG

def test_add_with_folder_option(tmp_path, monkeypatch):
    tasks_root = tmp_path / 'tasks'
    tasks_root.mkdir()
    CONFIG['directories']['tasks_dir'] = str(tasks_root)
    runner = CliRunner()
    res = runner.invoke(add, ['My Task', '--folder', 'Area1/SubArea', '--yes'])
    assert res.exit_code == 0
    # Expect nested dirs
    subdir = tasks_root / 'Area1' / 'SubArea'
    assert subdir.is_dir()
    files = list(subdir.glob('*.md'))
    assert len(files) == 1
    content = files[0].read_text(encoding='utf-8')
    assert '**Name:** My Task' in content


def test_add_with_path_syntax(tmp_path):
    tasks_root = tmp_path / 'tasks'
    tasks_root.mkdir()
    CONFIG['directories']['tasks_dir'] = str(tasks_root)
    runner = CliRunner()
    res = runner.invoke(add, ['Work/Deep Feature', '--yes'])
    assert res.exit_code == 0
    subdir = tasks_root / 'Work'
    assert subdir.is_dir()
    files = list(subdir.glob('*.md'))
    assert len(files) == 1
    assert 'Deep Feature' in files[0].read_text(encoding='utf-8')
