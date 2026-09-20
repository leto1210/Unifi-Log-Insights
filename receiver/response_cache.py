"""Single in-process TTL cache for expensive read-only API responses.

Foundational module with no heavy imports, so it can be unit-tested in
isolation and imported both by `deps` and by `routes._response_cache` without
pulling in database pools or enrichers.

One cache is shared by the whole API (the receiver runs a single uvicorn
worker, so per-process is effectively per-instance). Entries are keyed on the
decorated function plus its call args/kwargs, so parameterized handlers
(time_range, page, filters, …) each get their own bucket instead of clobbering
one another. Cached values are deep-copied on both store and read, so a caller
mutating a result (e.g. an annotation pass) can never poison a later hit.
Exceptions are never cached.

Test hooks: `clear_cache()` empties every bucket; `_cache` is the shared store.
"""

import copy
import functools
import threading
import time


class _TTLCache:
    """Thread-safe {key: (expires_at, value)} store with lazy expiry."""

    def __init__(self):
        """Initialise an empty store guarded by a lock."""
        self._store = {}
        self._lock = threading.Lock()

    def get(self, key):
        """Return the live value for key, or None if missing/expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            return value

    def set(self, key, value, ttl):
        """Store value under key for ttl seconds."""
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)

    def clear(self):
        """Empty every bucket."""
        with self._lock:
            self._store.clear()


_cache = _TTLCache()


def ttl_cache(ttl=30.0):
    """Cache a handler's return value for `ttl` seconds, keyed on its call args.

    Safe for both parameterless endpoints and handlers that take query/path
    params: the cache key is (qualified name, positional args, sorted kwargs).
    Values are deep-copied on read so downstream mutation can't poison the next
    hit; exceptions propagate without being cached.
    """
    def decorator(fn):
        """Wrap fn with the shared args-keyed TTL cache."""
        qualname = f"{fn.__module__}.{fn.__qualname__}"

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            """Return a cached copy or call fn and cache a copy of the result."""
            key = (qualname, args, tuple(sorted(kwargs.items())))
            hit = _cache.get(key)
            if hit is not None:
                return copy.deepcopy(hit)
            result = fn(*args, **kwargs)
            _cache.set(key, copy.deepcopy(result), ttl)
            return result
        return wrapper
    return decorator


def clear_cache():
    """Empty the shared response cache. Test hook — do not call from prod code."""
    _cache.clear()
