import os
import pytest
from click.testing import CliRunner
from priority_manager.commands.gantt import gantt
from priority_manager.utils.config import CONFIG

TASKS_DIR = CONFIG['directories']['tasks_dir']

SAMPLE="""# Task 1

**Name:** Task 1

**Description:** Gantt test task.

**Priority Score:** 20

**Due Date:** 2025-02-10

**Tags:** gantt

**Date Added:** 2024-06-01T14:30:00

**Status:** In Progress
"""

# Plotly will attempt to open a browser; we cannot allow side effects. We'll monkeypatch fig.show.
@pytest.mark.parametrize('patch_show', [True])
def test_gantt_generates_chart(setup_dirs, monkeypatch, patch_show):
    # Include a date in filename so start date parsing works
    with open(os.path.join(TASKS_DIR, '2025-01-01_task1.md'), 'w') as f:
        f.write(SAMPLE)
    from plotly import figure_factory as ff
    # Monkeypatch the create_gantt to return an object with add_vline + show we can control
    orig_create_gantt = ff.create_gantt
    class DummyFig:
        def add_vline(self, *a, **k):
            pass
        def show(self):
            pass
    def fake_create_gantt(*a, **k):
        return DummyFig()
    monkeypatch.setattr(ff, 'create_gantt', fake_create_gantt)
    runner = CliRunner()
    res = runner.invoke(gantt)
    assert res.exit_code == 0
