"""Retention configuration parsers and result types.

The retention-cleanup engine itself is a method on :class:`Database` in
``core.py``; this module hosts the input parsers, result NamedTuples, and
the shared module-level ``_legacy_retention_time_warned`` flag used by
:meth:`Database.resolve_retention_time`.
"""

import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)


def parse_retention_time(raw) -> str | None:
    """Parse and range-validate a retention_time input value.

    Returns a canonical 'HH:MM' string in the 00:00..23:59 range, or None for
    any non-coercible / out-of-range input. Accepts strings like '23:17',
    '3:5', '03:05' — the return value is always zero-padded two-digit form.

    Shared by Database.resolve_retention_time (for UI/env values) and the
    route handlers in routes/setup.py (for POST bodies and import payloads).
    Callers decide how to surface None — resolver falls through to the next
    precedence level, POST raises HTTPException, import pushes to failed_keys.

    The return value is directly consumable by `schedule.every().day.at(...)`
    so there's no format conversion needed in the scheduler.
    """
    if not isinstance(raw, str):
        return None
    parts = raw.strip().split(':')
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}"


class RetentionTimeConfig(NamedTuple):
    time: str    # 'HH:MM', 00:00..23:59
    source: str  # 'ui' | 'env' | 'default'


RETENTION_TIME_DEFAULT = '03:00'


def parse_retention_days(raw) -> int | None:
    """Parse and range-validate a retention-days input value.

    Returns positive int or None for any non-coercible / non-positive input.
    Accepts coercible values (including string digits) — this is for inputs
    from untrusted sources (API bodies, env vars, DB values).

    Related but distinct: `Database.validate_retention_days` is a stricter
    post-resolution invariant check (type: must already be `int`, not just
    coercible) used on values that have already been through a resolver.
    Both functions exist because they run at different points in the
    lifecycle — see that method's docstring for the scoping rule.
    """
    try:
        days = int(raw)
    except (ValueError, TypeError):
        return None
    return days if days > 0 else None


class RetentionDaysConfig(NamedTuple):
    general: int
    general_source: str   # 'ui' | 'env' | 'default'
    dns: int
    dns_source: str       # 'ui' | 'env' | 'default'
