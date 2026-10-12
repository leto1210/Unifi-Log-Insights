"""Log-based WAN/gateway identity detection and periodic stats logging."""

import logging

import psycopg2

import parsers
from db import Database
from enrichment import Enricher

logger = logging.getLogger('receiver')


def _use_log_identity_detection(db: Database) -> bool:
    """Return True when log-based WAN/gateway detection should run."""
    return not bool(db.get_config('unifi_enabled', False))


# Identity keys the parsers load; _loaded_identity holds the values they last
# loaded after a refresh (None until the first one). Only the refresh below
# touches it, and only after a successful reload, so failures retry next run.
_IDENTITY_KEYS = ('wan_ip_by_iface', 'wan_ips', 'wan_ip', 'gateway_ips')
_loaded_identity = None


def _refresh_network_identity_from_logs(db: Database):
    """Run log-based WAN/gateway detection only when UniFi is not authoritative.

    When the persisted identity differs from what the parsers last loaded,
    they reload it so a newly learned WAN IP takes effect without a restart.
    Never raises: schedule.run_pending() does not catch job exceptions, so
    one would end the scheduler thread.
    """
    global _loaded_identity
    try:
        if not _use_log_identity_detection(db):
            return
    except Exception as e:
        logger.error("Network identity refresh skipped (UniFi gate check failed): %s", e)
        return
    try:
        db.detect_wan_ip()
    except Exception as e:
        logger.error("WAN IP detection failed: %s", e)
    try:
        db.detect_gateway_ips()
    except Exception as e:
        logger.error("Gateway IP detection failed: %s", e)
    try:
        persisted = tuple(db.get_config(key) for key in _IDENTITY_KEYS)
        if persisted != _loaded_identity:
            parsers.reload_config_from_db(db)
            _loaded_identity = persisted
    except Exception as e:
        logger.error("Reloading detected network identity failed, will retry: %s", e)


def _log_periodic_stats(db: Database, enricher: Enricher):
    """Collect and log stats only when DEBUG logging is enabled."""
    if not logger.isEnabledFor(logging.DEBUG):
        return
    db_stats = None
    enrich_stats = None

    try:
        db_stats = db.get_stats()
    except psycopg2.Error as e:
        logger.error("Failed to get DB stats: %s", e)
    except Exception as e:
        # Last-resort safeguard: stats must never break scheduler loop.
        logger.error("Failed to get DB stats (unexpected): %s", e)

    try:
        enrich_stats = enricher.get_stats()
    except Exception as e:
        # Last-resort safeguard: stats must never break scheduler loop.
        logger.error("Failed to get enrichment stats (unexpected): %s", e)

    try:
        if db_stats is not None:
            logger.debug("DB stats — total: %s, last hour: %s", db_stats['total'], db_stats['last_hour'])
        if enrich_stats is not None:
            logger.debug("Enrichment stats — %s", enrich_stats)
    except (KeyError, TypeError) as e:
        logger.error("Failed to log stats payload: %s", e)
