"""Regression tests for background poller lifecycle guards."""

import threading
from unittest.mock import MagicMock

import pytest

import adguard_poller
import pihole_api
from unifi.core import UniFiAPI


class StubbornThread:
    """Thread double that remains alive after join to simulate a slow shutdown."""

    def __init__(self):
        """Initialise the fake thread as alive."""
        self.join_calls = []

    def is_alive(self):
        """Report that the old poller is still running."""
        return True

    def join(self, timeout=None):
        """Record join attempts without changing liveness."""
        self.join_calls.append(timeout)


def test_adguard_start_is_idempotent_while_thread_is_alive(monkeypatch):
    """AdGuard start() must not create duplicate daemon threads."""
    created = []

    class FakeThread:
        """Thread replacement that records creation and start calls."""

        def __init__(self, target, daemon=False, name=None):
            """Store constructor arguments for assertions."""
            self.target = target
            self.daemon = daemon
            self.name = name
            self.started = False
            created.append(self)

        def is_alive(self):
            """Report alive after start, matching a running poller."""
            return self.started

        def start(self):
            """Mark the fake thread as started."""
            self.started = True

    monkeypatch.setattr(adguard_poller.threading, 'Thread', FakeThread)
    poller = AdGuardHomePoller_for_test()

    poller.start()
    poller.start()

    assert len(created) == 1
    assert created[0].name == 'adguard-poller'


@pytest.mark.parametrize(
    'factory, start_method, stop_attr',
    [
        (lambda: PiHolePoller_for_test(), 'start_polling', '_poll_stop'),
        (lambda: UniFiAPI_for_test(), 'start_polling', '_poll_stop'),
    ],
)
def test_restartable_pollers_do_not_duplicate_when_old_thread_survives(
    monkeypatch,
    factory,
    start_method,
    stop_attr,
):
    """Restartable pollers should fail closed if the old daemon is still alive."""
    new_threads = []

    class FakeThread:
        """Thread replacement for detecting accidental replacement starts."""

        def __init__(self, *args, **kwargs):
            """Record any attempted replacement thread."""
            new_threads.append((args, kwargs))

        def start(self):
            """No-op start used only if duplication happens."""

    monkeypatch.setattr(pihole_api.threading, 'Thread', FakeThread)
    monkeypatch.setattr('unifi.core.threading.Thread', FakeThread)
    poller = factory()
    old_thread = StubbornThread()
    poller._poll_thread = old_thread

    getattr(poller, start_method)()

    assert getattr(poller, stop_attr).is_set()
    assert old_thread.join_calls == [5]
    assert new_threads == []


class AdGuardHomePoller_for_test(adguard_poller.AdGuardHomePoller):
    """Lightweight AdGuard poller without DB-backed initialisation."""

    def __init__(self):
        """Initialise only the lifecycle fields needed by start()."""
        self._stop = threading.Event()
        self._thread = None
        self._lifecycle_lock = threading.Lock()


class PiHolePoller_for_test(pihole_api.PiHolePoller):
    """Lightweight Pi-hole poller without DB-backed initialisation."""

    def __init__(self):
        """Initialise only fields used by start_polling()/stop_polling()."""
        self._db = MagicMock()
        self._enricher = None
        self.enabled = True
        self.poll_interval = 60
        self._poll_thread = None
        self._poll_stop = threading.Event()
        self._lifecycle_lock = threading.RLock()
        self._session = None
        self._sid = None


class UniFiAPI_for_test(UniFiAPI):
    """Lightweight UniFi client without DB-backed initialisation."""

    def __init__(self):
        """Initialise only fields used by start_polling()/stop_polling()."""
        self._db = MagicMock()
        self.enabled = True
        self._poll_thread = None
        self._poll_stop = threading.Event()
        self._lifecycle_lock = threading.RLock()
        self._session = None
        self._site_uuid = None
        self._csrf_token = None
        self._lock = threading.Lock()
        self._ip_to_name = {}
        self._mac_to_name = {}
