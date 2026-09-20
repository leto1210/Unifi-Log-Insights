"""In-process TTL cache for expensive read-only API responses.

The implementation now lives in `deps.ttl_cache` so the whole API shares one
cache with a single set of semantics (args-keyed, deep-copied on read, single
uvicorn worker → effectively shared). This module re-exports it so the existing
`from routes._response_cache import ttl_cache` / `clear_cache` sites keep working.

Applied to `/api/stats*`, `/api/flows/graph` and `/api/logs` handlers so the
dashboard's first page load doesn't serialize many aggregation queries over the
40 M-row `logs` table.

Test hooks: `clear_cache()` empties every bucket; `_cache` is the shared store.
"""

from __future__ import annotations

import time  # re-exported so tests can monkeypatch `_response_cache.time.monotonic`

from deps import _cache, clear_cache, ttl_cache

__all__ = ["ttl_cache", "clear_cache", "_cache", "time"]
