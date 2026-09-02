"""UDP syslog receiver with batched database writes."""

import logging
import socket
import threading
import time

from parsers import parse_log
from db import Database, get_config
from enrichment import Enricher

from service.config import BATCH_SIZE, BATCH_TIMEOUT, SYSLOG_BUFFER_SIZE, SYSLOG_PORT

logger = logging.getLogger('receiver')


class SyslogReceiver:
    """UDP syslog receiver with batched database writes."""

    HEARTBEAT_INTERVAL = 60  # Log heartbeat every 60 seconds

    def __init__(self, db: Database, enricher: Enricher):
        """Create the receiver — does not open the socket until start() is called."""
        self.db = db
        self.enricher = enricher
        self.sock = None
        self.running = False
        self.batch: list[dict] = []
        self.batch_lock = threading.Lock()
        self.last_flush = time.time()
        self.last_heartbeat = time.time()
        self.last_receive_time = 0.0  # Track when we last received any packet
        self.consecutive_flush_errors = 0
        self.stats = {
            'received': 0,
            'parsed': 0,
            'filtered': 0,
            'failed': 0,
            'inserted': 0,
            'flush_errors': 0,
            'dropped': 0,
        }
        self._load_disabled_types()

    def _load_disabled_types(self):
        """Load set of log types that should be silently discarded."""
        disabled = set()
        if not get_config(self.db, 'wifi_processing_enabled', True):
            disabled.add('wifi')
        if not get_config(self.db, 'system_processing_enabled', True):
            disabled.add('system')
        self._disabled_log_types = disabled
        if disabled:
            logger.info("Log type filtering active: discarding %s", disabled)

    def start(self):
        """Start the UDP listener."""
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)  # dual-stack: accept IPv4 + IPv6
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Set receive buffer to 1MB to handle bursts
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
        actual_rcvbuf = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        logger.info("UDP socket SO_RCVBUF: requested=1048576, actual=%d", actual_rcvbuf)

        # Bind to all interfaces — syslog receivers must accept traffic from any
        # network the container is attached to (bridge, host, macvlan, LAN).
        # Access control is enforced at the Docker/host firewall boundary, not
        # here. See docker-compose.yml `ports: "514:514/udp"` which already
        # narrows exposure at the daemon level.
        self.sock.bind(('::', SYSLOG_PORT))  # noqa: S104  # lgtm[py/bind-socket-all-network-interfaces]
        self.sock.settimeout(1.0)  # Allow periodic batch flushing
        self.running = True

        logger.info("Syslog receiver listening on UDP port %d", SYSLOG_PORT)

        while self.running:
            try:
                data, addr = self.sock.recvfrom(SYSLOG_BUFFER_SIZE)
                self.last_receive_time = time.time()
                self._handle_message(data, addr)
            except socket.timeout:
                pass
            except OSError as e:
                if self.running:
                    logger.error("Socket error (will retry): %s", e)
                    time.sleep(0.1)  # Brief pause to avoid tight error loop
            finally:
                # Check if batch needs flushing by timeout
                self._maybe_flush_batch()
                self._maybe_log_heartbeat()

    def stop(self):
        """Stop the receiver and flush remaining logs."""
        logger.info("Stopping syslog receiver...")
        self.running = False
        self._flush_batch()
        if self.sock:
            self.sock.close()
        logger.info("Syslog receiver stopped. Stats: %s", self.stats)

    def _handle_message(self, data: bytes, addr: tuple):
        """Process a single syslog message."""
        self.stats['received'] += 1

        try:
            raw_log = data.decode('utf-8', errors='replace').strip()
        except Exception as e:
            logger.warning("Failed to decode message from %s: %s", addr, e)
            self.stats['failed'] += 1
            return

        if not raw_log:
            return

        parsed = parse_log(raw_log)
        if parsed is None:
            self.stats['failed'] += 1
            logger.debug("Unparseable log from %s: %.100s...", addr, raw_log)
            return

        self.stats['parsed'] += 1

        # Filter disabled log types before enrichment
        log_type = parsed.get('log_type')
        if log_type in self._disabled_log_types:
            self.stats['filtered'] += 1
            return

        # Enrich with GeoIP, ASN, AbuseIPDB, rDNS
        parsed = self.enricher.enrich(parsed)

        with self.batch_lock:
            self.batch.append(parsed)
            if len(self.batch) >= BATCH_SIZE:
                self._flush_batch()

    def _maybe_flush_batch(self):
        """Flush batch if timeout elapsed."""
        if time.time() - self.last_flush >= BATCH_TIMEOUT:
            with self.batch_lock:
                if self.batch:
                    self._flush_batch()

    def _flush_batch(self):
        """Write current batch to database."""
        if not self.batch:
            self.last_flush = time.time()
            return

        to_insert = self.batch[:]
        self.batch = []
        self.last_flush = time.time()
        batch_len = len(to_insert)

        flush_start = time.time()
        try:
            self.db.insert_logs_batch(to_insert)
            flush_elapsed = time.time() - flush_start
            self.stats['inserted'] += batch_len
            if self.consecutive_flush_errors > 0:
                logger.info("DB insert recovered after %d consecutive failures", self.consecutive_flush_errors)
            self.consecutive_flush_errors = 0
            if flush_elapsed > 1.0:
                logger.warning("Slow DB flush: %d logs took %.2fs (>1s blocks UDP receive)", batch_len, flush_elapsed)
            else:
                logger.debug("Flushed %d logs in %.3fs", batch_len, flush_elapsed)
        except Exception as e:
            flush_elapsed = time.time() - flush_start
            self.stats['flush_errors'] += 1
            self.stats['dropped'] += batch_len
            self.consecutive_flush_errors += 1
            logger.error("DB insert failed (%d logs lost, %.2fs, consecutive=%d): %s",
                         batch_len, flush_elapsed, self.consecutive_flush_errors, e)
            if self.consecutive_flush_errors >= 5:
                logger.critical("DB insert failing repeatedly (%d consecutive). "
                                "UDP packets are likely being dropped. Check DB connectivity.",
                                self.consecutive_flush_errors)

    def _maybe_log_heartbeat(self):
        """Periodic heartbeat log to confirm the receiver is alive."""
        now = time.time()
        if now - self.last_heartbeat < self.HEARTBEAT_INTERVAL:
            return
        self.last_heartbeat = now

        silence = now - self.last_receive_time if self.last_receive_time else 0
        logger.debug("Heartbeat — received=%d parsed=%d filtered=%d inserted=%d dropped=%d flush_errors=%d silence=%.0fs",
                     self.stats['received'], self.stats['parsed'], self.stats['filtered'],
                     self.stats['inserted'], self.stats['dropped'], self.stats['flush_errors'], silence)

        # Warn if no packets received for a long time (gateway may have stopped sending)
        if self.last_receive_time and silence > 30:
            logger.warning("No UDP packets received for %.0fs — gateway may have stopped sending or port is unreachable", silence)
