"""Background scheduler jobs: retention cleanup, stats, blacklist, WAN refresh."""

import logging
import threading
import time

import schedule

from db import Database
from enrichment import Enricher
from blacklist import BlacklistFetcher
from routes.auth import auth_cleanup

from service.config import STATS_INTERVAL_MINUTES, WAN_REFRESH_INTERVAL_MINUTES
from service.network_identity import _log_periodic_stats, _refresh_network_identity_from_logs

logger = logging.getLogger('receiver')

# Set by the SIGUSR2 handler when retention_time may have changed.
# Consumed by the scheduler loop (single-writer, single-reader — safe).
# All `schedule` registry mutation stays on the scheduler thread.
_retention_reload_requested = threading.Event()


def _retention_cleanup(db: Database):
    """Run a full retention cleanup pass. Called by the schedule library."""
    try:
        cfg = Database.resolve_retention_days(db)
        logger.info("Retention cleanup starting (general_retention=%d days, dns_retention=%d days)",
                    cfg.general, cfg.dns)
        result = db.run_retention_cleanup(cfg.general, cfg.dns)
        if result['status'] == 'partial':
            logger.warning("Retention cleanup partial: %d deleted, error: %s",
                           result['deleted_so_far'], result['error'])
        elif result['status'] == 'failed':
            logger.error("Retention cleanup failed: %s", result['error'])
    except Exception as e:
        logger.error("Retention cleanup failed: %s", e)

    # rdns_cache sweep — independent pass so a failure here is not misreported
    # as log-retention failure.
    try:
        deleted = db.cleanup_rdns_cache()
        if deleted:
            logger.info("rdns_cache retention sweep deleted %d rows", deleted)
    except Exception as e:
        logger.warning("rdns_cache retention sweep failed: %s", e)


def _register_retention_job(db: Database):
    """(Re-)register the daily retention cleanup with the saved time.

    MUST only be called on the scheduler thread — mutates the `schedule`
    module's job registry, which is not thread-safe.

    Tagged 'retention' so we can clear and re-register without touching the
    other scheduled jobs (stats, blacklist, auth cleanup, wan refresh).
    """
    schedule.clear('retention')
    cfg = Database.resolve_retention_time(db)
    (schedule.every()
             .day
             .at(cfg.time)   # 'HH:MM' — schedule library's native format
             .do(_retention_cleanup, db=db)
             .tag('retention'))
    logger.info("Retention cleanup scheduled daily at %s (source=%s, container-local time)",
                cfg.time, cfg.source)


def _scheduler_tick(db: Database):
    """One iteration of the scheduler loop — extracted so tests can run it
    deterministically. Observes the retention-reload Event (set by the signal
    handler on another thread) and rebuilds the job before dispatching pending
    runs. All `schedule` registry mutation therefore stays on this thread.
    """
    if _retention_reload_requested.is_set():
        _retention_reload_requested.clear()
        _register_retention_job(db)
    schedule.run_pending()


def run_scheduler(db: Database, enricher: Enricher, blacklist_fetcher: BlacklistFetcher = None):
    """Background thread for scheduled tasks (retention cleanup, stats, blacklist)."""

    def log_stats():
        _log_periodic_stats(db, enricher)

    def pull_blacklist():
        """Fetch the latest IP blacklist and store it in the database."""
        if blacklist_fetcher:
            try:
                blacklist_fetcher.fetch_and_store()
            except Exception as e:
                logger.error("Blacklist pull failed: %s", e)

    def refresh_wan_ip():
        """Refresh WAN/gateway identity from recent log data (no-op when UniFi is active)."""
        _refresh_network_identity_from_logs(db)

    schedule.every(STATS_INTERVAL_MINUTES).minutes.do(log_stats)
    schedule.every(WAN_REFRESH_INTERVAL_MINUTES).minutes.do(refresh_wan_ip)
    _register_retention_job(db)
    schedule.every().day.at("04:00").do(pull_blacklist)
    # auth_cleanup has its own internal try/except — no wrapper needed here.
    schedule.every().day.at("03:30").do(auth_cleanup)

    logger.info("Scheduler started — stats every %dm, WAN refresh every %dm, blacklist daily at 04:00, auth cleanup daily at 03:30",
                 STATS_INTERVAL_MINUTES, WAN_REFRESH_INTERVAL_MINUTES)

    # Initial blacklist pull after 30s startup delay
    time.sleep(30)
    pull_blacklist()

    # Run retention cleanup once at startup so the first cleanup does not have
    # to wait until the scheduled daily window before executing.
    _retention_cleanup(db)

    while True:
        _scheduler_tick(db)
        time.sleep(10)
