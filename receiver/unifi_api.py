"""Backward-compatible shim for the legacy `unifi_api` module.

The implementation moved into the `unifi` package (see receiver/unifi/).
This module remains so existing callers (deps, main, routes, tests) can keep
using `from unifi_api import UniFiAPI, UniFiPermissionError` and so tests that
patch `sys.modules['unifi_api']` continue to work unchanged.
"""

import time  # noqa: F401  — exposed for tests that patch `unifi_api.time.sleep`

from unifi.core import (  # noqa: F401
    UniFiAPI,
    _WAN_PHYSICAL_MAP,
    _EPOCH_MIN,
    _parse_epoch,
)
from unifi.exceptions import UniFiPermissionError  # noqa: F401

__all__ = ['UniFiAPI', 'UniFiPermissionError']
