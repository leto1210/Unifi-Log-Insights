"""Unit tests for routes/_response_cache.py.

Not tied to FastAPI — exercises the decorator against a plain callable so
failures point at the cache itself, not the transport layer.
"""

import time

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
