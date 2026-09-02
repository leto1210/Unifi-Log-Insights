"""
UniFi Log Insight - Syslog Receiver

UDP syslog listener that receives logs from UDR, parses them,
and stores them in PostgreSQL.

Phase 1: Receive → Parse → Store
Phase 2 will add: IP enrichment (GeoIP, AbuseIPDB, rDNS)
"""

import logging
import os
import signal
import sys
import threading

import parsers
from db import Database, build_conn_params, get_config, is_external_db, set_config, wait_for_postgres
from enrichment import Enricher
from backfill import BackfillTask
from blacklist import BlacklistFetcher
from unifi_api import UniFiAPI
from pihole_api import PiHolePoller
from adguard_poller import AdGuardHomePoller

from service.syslog_receiver import SyslogReceiver
from service.scheduler import (
    _register_retention_job,
    _retention_cleanup,
    _retention_reload_requested,
    _scheduler_tick,
    run_scheduler,
)
from service.network_identity import (
    _log_periodic_stats,
    _refresh_network_identity_from_logs,
    _use_log_identity_detection,
)
from service.signals import (
    make_reload_config_handler,
    make_reload_geoip_handler,
    make_shutdown_handler,
)

# ── Logging ────────────────────────────────────────────────────────────────────

_log_level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
if _log_level_name not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
    _log_level_name = 'INFO'

logging.basicConfig(
    level=getattr(logging, _log_level_name),
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
)
logger = logging.getLogger('receiver')


__all__ = [
    'SyslogReceiver',
    '_register_retention_job',
    '_retention_cleanup',
    '_retention_reload_requested',
    '_scheduler_tick',
    'run_scheduler',
    '_log_periodic_stats',
    '_refresh_network_identity_from_logs',
    '_use_log_identity_detection',
    'main',
]


def main():
    """Entrypoint: initialise the database, enricher, and syslog receiver."""
    # Build connection params from environment
    conn_params = build_conn_params()
    logger.info("Database: %s mode (host=%s:%s, db=%s)",
                "external" if is_external_db() else "embedded",
                conn_params['host'], conn_params['port'], conn_params['dbname'])

    # Wait for PostgreSQL
    wait_for_postgres(conn_params)

    # Initialize database
    db = Database(conn_params)
    db.connect()

    # Create performance indexes that require CONCURRENTLY (existing installs)
    db.ensure_post_boot_indexes()

    # Load system configuration and apply to parsers module
    # Check for existing user migration
    setup_complete = get_config(db, "setup_complete", None)
    if setup_complete is None:
        # Count firewall logs to detect existing installation
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM logs WHERE log_type = 'firewall'")
                log_count = cur.fetchone()[0]

        if log_count > 0:
            # Auto-migrate existing installation with safe defaults
            logger.info("Migrating existing installation to dynamic config...")
            set_config(db, "wan_interfaces", ["ppp0"])
            set_config(db, "interface_labels", {})  # Empty = use raw names
            set_config(db, "setup_complete", True)
            set_config(db, "config_version", 1)
            logger.info(
                "Migration complete with safe defaults (WAN=ppp0, labels=raw names). "
                "Users can customize via Settings → Reconfigure."
            )

    # Load config into parsers module
    parsers.reload_config_from_db(db)
    logger.info("Loaded config: WAN interfaces = %s", parsers.WAN_INTERFACES)

    # Detect and persist WAN IP + gateway IPs from existing log data
    # (skipped when UniFi API is authoritative — identity comes from poll)
    _refresh_network_identity_from_logs(db)

    # Check config version for future migrations
    current_version = get_config(db, 'config_version', 0)
    if current_version < 1:
        # Future: handle config schema migrations
        pass

    # Initialize UniFi API client (self-disables when not configured)
    unifi_api = UniFiAPI(db=db)

    # Initialize Pi-hole poller
    pihole = PiHolePoller(db=db, enricher=None)  # enricher set after creation

    # Initialize enrichment (with UniFi device name resolution)
    enricher = Enricher(db=db, unifi=unifi_api)

    # Wire enricher into Pi-hole poller (created before enricher for signal handler)
    pihole.set_enricher(enricher)

    # Start receiver
    receiver = SyslogReceiver(db, enricher)

    # Initialize AdGuard Home poller (self-disables when not configured)
    adguard_poller = AdGuardHomePoller(db)

    signal.signal(signal.SIGTERM, make_shutdown_handler(receiver, adguard_poller, unifi_api, pihole, enricher, db))
    signal.signal(signal.SIGINT, make_shutdown_handler(receiver, adguard_poller, unifi_api, pihole, enricher, db))
    signal.signal(signal.SIGUSR1, make_reload_geoip_handler(enricher))
    signal.signal(signal.SIGUSR2, make_reload_config_handler(db, receiver, unifi_api, pihole, enricher, adguard_poller))

    # Start scheduler in background thread
    blacklist_fetcher = BlacklistFetcher(db)
    scheduler_thread = threading.Thread(target=run_scheduler, args=(db, enricher, blacklist_fetcher), daemon=True)
    scheduler_thread.start()

    # Start backfill daemon (queue-driven threat enrichment every 5 min)
    backfill = BackfillTask(db, enricher)
    backfill.start()

    # Start UniFi client/device polling (only runs if enabled)
    unifi_api.start_polling()

    # Start Pi-hole polling (only runs if enabled)
    pihole.start_polling()

    # Start AdGuard Home query log poller (only polls when enabled + configured)
    adguard_poller.start()

    # Start receiving (blocks)
    try:
        receiver.start()
    except KeyboardInterrupt:
        receiver.stop()
        adguard_poller.stop()
        unifi_api.stop_polling()
        pihole.stop_polling()
        enricher.close()
        db.close()


if __name__ == '__main__':
    main()
