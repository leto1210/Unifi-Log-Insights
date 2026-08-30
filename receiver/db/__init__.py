"""UniFi Log Insight — Database package.

This package replaces the former ``receiver/db.py`` module.  All public
symbols are re-exported here so existing callers (``from db import X``,
``import db as db_module``) keep working unchanged.

Layout:
    * :mod:`db.connection` — connection param helpers, ``wait_for_postgres``.
    * :mod:`db.config`     — API-key crypto, module-level ``get_config`` /
                             ``set_config`` / ``get_wan_ips_from_config`` /
                             ``parse_vpn_config``.
    * :mod:`db.retention`  — retention parsers and result NamedTuples.
    * :mod:`db.logs_sql`   — INSERT column list, INSERT SQL, ``count_logs``.
    * :mod:`db.schema`     — SQL migration statements.
    * :mod:`db.exceptions` — ``AdGuardHostMismatch``.
    * :mod:`db.core`       — the :class:`Database` class.

``_legacy_retention_time_warned`` lives on this package (not on
``db.retention``) so tests can toggle it via ``db._legacy_retention_time_warned
= False``; ``Database.resolve_retention_time`` reads and writes it here.
"""

# psycopg2 is re-exported for tests that reach through the ``db`` module
# to patch ``psycopg2.errors`` (see ``tests/test_db_schema_migrations.py``
# which does ``monkeypatch.setattr(db_module.psycopg2.errors, ...)``).
import logging

import psycopg2  # noqa: F401  (public API)

# The package-level logger.  Submodules route their log calls through this
# via ``_PackageLoggerProxy`` in :mod:`db.core` so tests that
# ``monkeypatch.setattr(db_module, 'logger', fake)`` (matching the old
# monolithic ``db.py`` behaviour) keep capturing output.
logger = logging.getLogger('db')

from .connection import (
    _normalize_db_host,
    build_conn_params,
    is_external_db,
    wait_for_postgres,
)
from .config import (
    _derive_fernet_key,
    _get_secret_key,
    decrypt_api_key,
    encrypt_api_key,
    get_config,
    get_wan_ips_from_config,
    parse_vpn_config,
    set_config,
)
from .exceptions import AdGuardHostMismatch
from .logs_sql import INSERT_COLUMNS, INSERT_SQL, count_logs
from .retention import (
    RETENTION_TIME_DEFAULT,
    RetentionDaysConfig,
    RetentionTimeConfig,
    parse_retention_days,
    parse_retention_time,
)
from .core import Database

# Module-level flag so the legacy RETENTION_TIME deprecation warning fires
# once per process, not on every resolver call (the resolver runs on every
# GET /api/config/retention and every SIGUSR2 scheduler rebuild).
#
# Kept on the package (not on ``db.retention``) because
# ``receiver/tests/conftest.py`` resets it via ``db._legacy_retention_time_warned
# = False`` between test cases.  ``Database.resolve_retention_time`` reads
# and writes it through ``import db``.
_legacy_retention_time_warned = False

__all__ = [
    'AdGuardHostMismatch',
    'Database',
    'INSERT_COLUMNS',
    'INSERT_SQL',
    'RETENTION_TIME_DEFAULT',
    'RetentionDaysConfig',
    'RetentionTimeConfig',
    '_derive_fernet_key',
    '_get_secret_key',
    '_legacy_retention_time_warned',
    '_normalize_db_host',
    'build_conn_params',
    'count_logs',
    'decrypt_api_key',
    'encrypt_api_key',
    'get_config',
    'get_wan_ips_from_config',
    'is_external_db',
    'parse_retention_days',
    'parse_retention_time',
    'parse_vpn_config',
    'set_config',
    'wait_for_postgres',
]
