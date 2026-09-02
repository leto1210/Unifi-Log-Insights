"""Runtime configuration constants for the receiver service."""

import os


SYSLOG_PORT = 514
SYSLOG_BUFFER_SIZE = 8192      # Max UDP packet size
BATCH_SIZE = 50                 # Insert logs in batches
BATCH_TIMEOUT = 2.0             # Flush batch after N seconds even if not full
STATS_INTERVAL_MINUTES = 15     # Log stats every N minutes
RETENTION_INTERVAL_HOURS = 12   # Run retention cleanup every N hours


def _env_int(name: str, default: int) -> int:
    """Read an integer env var with safe fallback."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
        return value if value > 0 else default
    except ValueError:
        return default


WAN_REFRESH_INTERVAL_MINUTES = _env_int('WAN_REFRESH_INTERVAL_MINUTES', 360)
