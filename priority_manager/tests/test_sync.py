import pytest

@pytest.mark.skip(reason="Network-dependent Microsoft To Do sync not tested; requires mocking external API.")
def test_sync_placeholder():
    assert True
