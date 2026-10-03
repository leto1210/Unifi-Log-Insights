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

The store holds at most 256 responses (LRU eviction). This limits the number
of distinct filter combinations retained, not their total byte size; callers
must still bound individual response sizes. Expired entries are purged on
insertion (scanned at most once per second), including entries whose keys
are never requested again.

Test hooks: `clear_cache()` empties every bucket; `_cache` is the shared store.
"""

import copy
import functools
import threading
import time
from collections import OrderedDict


_MAX_CACHE_ENTRIES = 256
_SWEEP_INTERVAL = 1.0  # seconds between full scans for expired entries


class _TTLCache:
    """Thread-safe bounded LRU store of {key: (expires_at, value)} entries."""

    def __init__(self, max_entries=_MAX_CACHE_ENTRIES):
        """Initialise a bounded store guarded by a lock."""
        self._store = OrderedDict()
        self._max_entries = max_entries
        self._next_sweep = 0.0
        self._lock = threading.Lock()

    def get(self, key):
        """Return the live value for key, or None if missing/expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at <= time.monotonic():
                del self._store[key]
                return None
            self._store.move_to_end(key)
            return value

    def set(self, key, value, ttl):
        """Store one value with LRU eviction, sweeping expired ones at most once per second."""
        with self._lock:
            now = time.monotonic()
            if now >= self._next_sweep:
                # The scan is O(entries); throttling it keeps bursts of cache
                # misses from repeatedly walking the store under the lock.
                self._next_sweep = now + _SWEEP_INTERVAL
                for expired_key, (expires_at, _) in tuple(self._store.items()):
                    if expires_at <= now:
                        del self._store[expired_key]
            self._store[key] = (now + ttl, value)
            self._store.move_to_end(key)
            while len(self._store) > self._max_entries:
                self._store.popitem(last=False)

    def clear(self):
        """Empty every bucket."""
        with self._lock:
            self._store.clear()
            self._next_sweep = 0.0


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
