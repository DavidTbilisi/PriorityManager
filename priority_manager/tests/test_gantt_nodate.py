from click.testing import CliRunner
from priority_manager.commands.gantt import gantt
from priority_manager.utils.config import CONFIG
import os

TASKS_DIR = CONFIG['directories']['tasks_dir']

def test_gantt_no_date_filename(setup_dirs):
    # Filename has no date; Start Date should fallback to Date Added
    with open(os.path.join(TASKS_DIR, 'plainname.md'), 'w', encoding='utf-8') as f:
        f.write("""**Name:** Plain

**Description:** Test

**Priority Score:** 7

**Due Date:** 2025-05-10

**Tags:** demo

**Date Added:** 2025-05-01T08:00:00

**Status:** To Do
""")
    runner = CliRunner()
    # Monkeypatching Plotly create_gantt similar to previous test isn't here; rely on internal skip if needed.
    from plotly import figure_factory as ff
    orig_create = ff.create_gantt
    class DummyFig:
        def add_vline(self, *a, **k):
            pass
        def show(self):
            pass
    def fake_create(*a, **k):
        return DummyFig()
    # Patch
    from _pytest.monkeypatch import MonkeyPatch
    mp = MonkeyPatch()
    mp.setattr(ff, 'create_gantt', fake_create)
    res = runner.invoke(gantt, ["--no-open"])  # use new flag
    mp.undo()
    assert res.exit_code == 0, res.output
