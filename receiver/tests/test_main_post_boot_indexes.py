"""Post-boot index maintenance must not hold the receiver before UDP listen.

2026-11-27: two CONCURRENTLY builds over a ~100 GB partition ran inline in
main(), so the syslog listener stayed closed and incoming logs were lost.
"""
import inspect
import sys
import threading
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def main_module(monkeypatch):
    """Import main.py with heavy deps stubbed."""
    for name in ('parsers', 'enrichment', 'backfill', 'blacklist',
                 'unifi_api', 'pihole_api', 'routes.auth'):
        monkeypatch.setitem(sys.modules, name, MagicMock())
    monkeypatch.delitem(sys.modules, 'main', raising=False)
    import main
    return main


def test_post_boot_indexes_run_in_background(main_module):
    """The helper returns while the index build is still running."""
    started, release = threading.Event(), threading.Event()

    def slow_build():
        """Stand in for a long CREATE INDEX CONCURRENTLY."""
        started.set()
        release.wait(5)

    db = MagicMock(ensure_post_boot_indexes=slow_build)
    thread = main_module._start_post_boot_indexes(db)
    try:
        assert started.wait(5)
        assert thread.is_alive() and thread.daemon
    finally:
        release.set()
        thread.join(5)


def test_main_does_not_build_indexes_inline(main_module):
    """main() hands index maintenance to the background helper."""
    source = inspect.getsource(main_module.main)
    assert 'db.ensure_post_boot_indexes()' not in source
    assert '_start_post_boot_indexes(db)' in source
