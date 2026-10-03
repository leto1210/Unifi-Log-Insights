"""Unit tests for routes/_response_cache.py.

Not tied to FastAPI — exercises the decorator against a plain callable so
failures point at the cache itself, not the transport layer.
"""

import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest


@pytest.fixture(autouse=True)
def _clear_between_tests():
    from routes._response_cache import clear_cache
    clear_cache()
    yield
    clear_cache()


def test_second_call_within_ttl_skips_function():
    from routes._response_cache import ttl_cache

    calls = []

    @ttl_cache(ttl=60)
    def handler(time_range: str = "24h"):
        calls.append(time_range)
        return {"value": time_range}

    assert handler(time_range="24h") == {"value": "24h"}
    assert handler(time_range="24h") == {"value": "24h"}
    assert calls == ["24h"], "second call should be served from cache"


def test_different_kwargs_are_different_keys():
    from routes._response_cache import ttl_cache

    calls = []

    @ttl_cache(ttl=60)
    def handler(time_range: str = "24h"):
        calls.append(time_range)
        return {"value": time_range}

    handler(time_range="24h")
    handler(time_range="7d")
    handler(time_range="24h")
    handler(time_range="7d")
    assert calls == ["24h", "7d"], "each kwargs tuple maps to a distinct cache entry"


def test_expired_entry_is_recomputed(monkeypatch):
    """Advance monotonic clock past TTL and confirm the wrapped function runs again."""
    import routes._response_cache as rc

    now = [1_000.0]
    monkeypatch.setattr(rc.time, "monotonic", lambda: now[0])

    calls = []

    @rc.ttl_cache(ttl=30)
    def handler(time_range: str = "24h"):
        calls.append(now[0])
        return {"t": now[0]}

    handler(time_range="24h")            # miss, cached at t=1000, expires t=1030
    now[0] = 1_020.0
    handler(time_range="24h")            # still within TTL → cache hit
    now[0] = 1_031.0
    handler(time_range="24h")            # expired → miss, recompute
    assert calls == [1_000.0, 1_031.0]


def test_exception_is_not_cached():
    from routes._response_cache import ttl_cache

    attempts = []

    @ttl_cache(ttl=60)
    def handler(time_range: str = "24h"):
        attempts.append(time_range)
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        handler(time_range="24h")
    with pytest.raises(RuntimeError):
        handler(time_range="24h")
    assert attempts == ["24h", "24h"], "exceptions must never be cached"


def test_cached_value_isolated_from_caller_mutations():
    """A cache hit must not return a shared reference the caller can mutate."""
    from routes._response_cache import ttl_cache

    @ttl_cache(ttl=60)
    def handler():
        return {"items": [1, 2, 3]}

    first = handler()
    first["items"].append("polluted")
    second = handler()
    assert second == {"items": [1, 2, 3]}, "cache must deep-copy on read"


def test_clear_cache_empties_everything():
    from routes._response_cache import ttl_cache, clear_cache

    calls = []

    @ttl_cache(ttl=60)
    def handler(time_range: str = "24h"):
        calls.append(time_range)
        return {"v": time_range}

    handler(time_range="24h")
    handler(time_range="24h")
    assert len(calls) == 1

    clear_cache()
    handler(time_range="24h")
    assert len(calls) == 2, "clear_cache must force a recompute"


def test_many_distinct_keys_never_exceed_capacity():
    """A stream of unique filters must not grow the shared cache indefinitely."""
    from response_cache import _cache, ttl_cache

    @ttl_cache(ttl=600)
    def handler(filter_id):
        """Return a distinct cached response for each filter."""
        return {"filter": filter_id}

    for filter_id in range(5_000):
        assert handler(filter_id) == {"filter": filter_id}
        assert len(_cache._store) <= _cache._max_entries
    assert len(_cache._store) == _cache._max_entries


def test_oldest_unused_entry_is_evicted():
    """A hit should retain its entry when a full cache admits a new key."""
    from response_cache import _cache, ttl_cache

    calls = []

    @ttl_cache(ttl=600)
    def handler(key):
        """Track which keys require recomputation."""
        calls.append(key)
        return {"key": key}

    for key in range(_cache._max_entries):
        handler(key)
    handler(0)  # Keep the oldest inserted key active.
    handler(_cache._max_entries)
    handler(0)
    handler(1)
    assert calls[-2:] == [_cache._max_entries, 1]


def test_insertion_purges_expired_entries_without_revisiting_keys(monkeypatch):
    """Dead entries are removed on later writes, even when their keys are idle."""
    import response_cache as rc

    now = [1_000.0]
    monkeypatch.setattr(rc.time, "monotonic", lambda: now[0])

    @rc.ttl_cache(ttl=10)
    def handler(key):
        """Return one value per key."""
        return key

    for key in range(20):
        handler(key)
    assert len(rc._cache._store) == 20
    now[0] = 1_011.0
    handler(20)
    assert len(rc._cache._store) == 1


def test_blocked_handler_does_not_hold_cache_lock():
    """Another key remains accessible while a slow handler computes."""
    from response_cache import ttl_cache

    started = Event()
    release = Event()

    @ttl_cache(ttl=60)
    def handler(key):
        """Simulate a slow database request for one key."""
        if key == "slow":
            started.set()
            assert release.wait(5)
        return key

    assert handler("fast") == "fast"
    with ThreadPoolExecutor(max_workers=2) as pool:
        slow = pool.submit(handler, "slow")
        try:
            assert started.wait(5)
            fast = pool.submit(handler, "fast")
            assert fast.result(timeout=1) == "fast"
        finally:
            release.set()
        assert slow.result(timeout=5) == "slow"


def test_concurrent_insertions_keep_shared_store_bounded():
    """Concurrent misses may finish in any order but cannot exceed capacity."""
    from response_cache import _cache, ttl_cache

    @ttl_cache(ttl=600)
    def handler(key):
        """Return a unique value to exercise parallel writes."""
        return {"key": key}

    with ThreadPoolExecutor(max_workers=16) as pool:
        assert list(pool.map(handler, range(2_000))) == [
            {"key": key} for key in range(2_000)
        ]
    assert len(_cache._store) == _cache._max_entries
