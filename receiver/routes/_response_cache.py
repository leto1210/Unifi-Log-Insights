"""In-process TTL cache for expensive read-only API responses.

Applied to `/api/stats*` handlers so the dashboard's first page load doesn't
serialize 8-10 aggregation queries over the 40 M-row `logs` table. Cache
values live in-process (per-worker) — the receiver runs a single uvicorn
worker, so this is effectively a shared cache.

Cache key = (fully-qualified function name, sorted kwargs). Cached values
are deep-copied on read so downstream mutations by the caller (e.g. an
annotation pass) can't poison the next hit. Exceptions are never cached.

Test hooks: `clear_cache()` empties every bucket; used by test fixtures to
keep tests independent.
"""

from __future__ import annotations

import copy
import functools
import threading
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class _TTLCache:
    def __init__(self) -> None:
        self._store: dict[tuple[Any, ...], tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: tuple[Any, ...]) -> Any:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            return value

    def set(self, key: tuple[Any, ...], value: Any, ttl: float) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


_cache = _TTLCache()


def ttl_cache(ttl: float = 30.0) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache the return value of a FastAPI handler for `ttl` seconds.

    Positional args are unsupported (FastAPI passes query/path params as
    kwargs, so this is fine for router handlers). Cache misses call the
    wrapped function; exceptions propagate without caching.
    """
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        qualname = f"{fn.__module__}.{fn.__qualname__}"

        @functools.wraps(fn)
        def wrapper(**kwargs: Any) -> T:
            key = (qualname, tuple(sorted(kwargs.items())))
            hit = _cache.get(key)
            if hit is not None:
                return copy.deepcopy(hit)
            result = fn(**kwargs)
            _cache.set(key, copy.deepcopy(result), ttl)
            return result

        return wrapper

    return decorator


def clear_cache() -> None:
    """Empty the shared response cache. Test hook — do not call from prod code."""
    _cache.clear()
