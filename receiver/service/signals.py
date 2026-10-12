"""Signal handler factories: SIGTERM/SIGINT (shutdown), SIGUSR1 (GeoIP reload), SIGUSR2 (config reload)."""

import logging
import sys
import time
from pathlib import Path

import parsers

from service.scheduler import _retention_reload_requested

logger = logging.getLogger('receiver')


def make_shutdown_handler(receiver, adguard_poller, unifi_api, pihole, enricher, db):
    """Return a SIGTERM/SIGINT handler that flushes pending logs and exits cleanly."""
    def shutdown(signum, frame):
        logger.info("Received signal %d, shutting down...", signum)
        receiver.stop()
        adguard_poller.stop()
        unifi_api.stop_polling()
        pihole.stop_polling()
        enricher.close()
        db.close()
        sys.exit(0)
    return shutdown


def make_reload_geoip_handler(enricher):
    """Return a SIGUSR1 handler that hot-reloads GeoIP databases."""
    def reload_geoip(signum, frame):
        logger.info("Received SIGUSR1, reloading GeoIP databases...")
        enricher.reload_geoip()
    return reload_geoip


def make_reload_config_handler(db, receiver, unifi_api, pihole, enricher, adguard_poller):
    """Return a SIGUSR2 handler that reloads config from the database."""
    def reload_config(signum, frame):
        logger.info("Received SIGUSR2, reloading config from database...")
        # Each step runs on its own: a transient DB error in one must not leave
        # the others (or the retention rebuild below) stale.
        steps = (
            ('parsers', lambda: parsers.reload_config_from_db(db)),
            ('unifi_api', unifi_api.reload_config),
            ('pihole', pihole.reload_config),
            ('enricher', enricher.reload_config),
            ('adguard_poller', adguard_poller.reload_config),
            ('disabled log types', receiver._load_disabled_types),
        )
        for name, step in steps:
            try:
                step()
            except Exception as e:
                logger.error("Config reload step '%s' failed: %s", name, e)
        # scheduler thread will rebuild the retention job on its next tick
        _retention_reload_requested.set()

        # Write timestamp to confirm reload completed
        try:
            Path('/tmp/config_reloaded').write_text(str(time.time()))
        except Exception as e:
            logger.debug("Failed to write reload timestamp: %s", e)

        logger.info("Config reloaded: WAN=%s", parsers.WAN_INTERFACES)
    return reload_config
