"""PostgreSQL connection parameter helpers."""

import logging
import os
import sys
import time

import psycopg2

logger = logging.getLogger(__name__)


def _normalize_db_host(raw: str) -> str:
    """Normalize DB_HOST: strip leading/trailing whitespace, lowercase.
    Shared by build_conn_params() and is_external_db() to guarantee
    the same host value is used for detection and connection."""
    return raw.strip().lower()


def build_conn_params() -> dict:
    """Build PostgreSQL connection parameters from environment variables."""
    host = _normalize_db_host(os.environ.get('DB_HOST', '127.0.0.1'))
    params = {
        'host': host,
        'port': int(os.environ.get('DB_PORT', '5432')),
        'dbname': os.environ.get('DB_NAME', 'unifi_logs'),
        'user': os.environ.get('DB_USER', 'unifi'),
        'password': os.environ.get('DB_PASSWORD') or os.environ.get('POSTGRES_PASSWORD', 'changeme'),
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 3,
    }
    sslmode = os.environ.get('DB_SSLMODE')
    if sslmode:
        params['sslmode'] = sslmode
    sslrootcert = os.environ.get('DB_SSLROOTCERT')
    if sslrootcert:
        params['sslrootcert'] = sslrootcert
    sslcert = os.environ.get('DB_SSLCERT')
    if sslcert:
        params['sslcert'] = sslcert
    sslkey = os.environ.get('DB_SSLKEY')
    if sslkey:
        params['sslkey'] = sslkey
    return params


def is_external_db() -> bool:
    """Check if the app is configured to use an external database."""
    host = _normalize_db_host(os.environ.get('DB_HOST', '127.0.0.1'))
    return host not in ('127.0.0.1', 'localhost', 'localhost.localdomain', '::1', '')


def wait_for_postgres(conn_params: dict, max_retries: int = 30, delay: float = 2.0):
    """Wait for PostgreSQL to be ready. Used by both receiver and API."""
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**conn_params)
            conn.close()
            logger.info("PostgreSQL is ready.")
            return
        except psycopg2.OperationalError:
            logger.warning("Waiting for PostgreSQL... (%d/%d)", i + 1, max_retries)
            time.sleep(delay)
    logger.critical("PostgreSQL not available after %d retries. Check DB_HOST, DB_PORT, "
                    "DB_USER, DB_PASSWORD, network connectivity, and firewall rules.", max_retries)
    sys.exit(1)
