#!/usr/bin/env python3
"""Vacuum / autovacuum metrics collector for the `logs` table.

Snapshots pg_stat_user_tables (+ pg_stat_io on PG16+, + optional
receiver-log-tail flush latencies) into the `vacuum_metrics` table so we can
retroactively answer:
  * How often does autovacuum actually fire on `logs`?
  * How high does n_dead_tup climb between vacuums?
  * Does the explicit post-cleanup VACUUM ever trigger, and how long does it run?
  * Do insert-batch latencies spike while a VACUUM is running?

Cheap on the DB: all counters are in-memory (pg_stat_*), no pg_relation_size(),
no COUNT(*).

Usage
-----
    # First time: create the metrics table (idempotent).
    python vacuum_metrics.py --init

    # Ad-hoc single snapshot (useful to verify connectivity).
    python vacuum_metrics.py --once

    # Long-running collector: snapshot every 300 s (default).
    python vacuum_metrics.py --loop 300

    # Same, but also parse the receiver container's stdout to compute
    # batch-flush P50/P95/P99 latency between snapshots.
    python vacuum_metrics.py --loop 300 \\
        --flush-log-cmd 'docker logs --since 6m unifi-log-insight 2>&1'

Env vars (same convention as receiver/db/connection.py):
    DB_HOST      default 127.0.0.1
    DB_PORT      default 5432
    DB_NAME      default unifi_logs
    DB_USER      default unifi
    DB_PASSWORD  or POSTGRES_PASSWORD
    DB_SSLMODE   optional
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras

SCHEMA_FILE = Path(__file__).with_name("schema.sql")

# Regex on the receiver's flush log lines. Two shapes coexist:
#   "Flushed 50 logs in 0.032s"                (DEBUG, needs LOG_LEVEL=DEBUG)
#   "Slow DB flush: 50 logs took 1.24s (>1s blocks UDP receive)"  (WARN, always on)
FLUSH_RE = re.compile(
    r"(?:Flushed\s+\d+\s+logs\s+in|Slow DB flush:\s+\d+\s+logs\s+took)\s+([\d.]+)s"
)
SLOW_FLUSH_RE = re.compile(r"Slow DB flush")

logger = logging.getLogger("vacuum_metrics")


def _conn_params() -> dict:
    return {
        "host": os.environ.get("DB_HOST", "127.0.0.1").strip().lower(),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "dbname": os.environ.get("DB_NAME", "unifi_logs"),
        "user": os.environ.get("DB_USER", "unifi"),
        "password": os.environ.get("DB_PASSWORD")
        or os.environ.get("POSTGRES_PASSWORD", "changeme"),
        "connect_timeout": 10,
        "application_name": "vacuum_metrics",
    }


def init_schema() -> None:
    ddl = SCHEMA_FILE.read_text()
    with psycopg2.connect(**_conn_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
    logger.info("vacuum_metrics table ready")


def _pg_stat_user_tables(cur) -> dict:
    cur.execute(
        """
        SELECT n_live_tup, n_dead_tup, n_mod_since_analyze,
               n_tup_ins, n_tup_upd, n_tup_del, n_tup_hot_upd,
               vacuum_count, autovacuum_count, analyze_count, autoanalyze_count,
               last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
        FROM pg_stat_user_tables
        WHERE schemaname = 'public' AND relname = 'logs'
        """
    )
    row = cur.fetchone()
    if not row:
        return {}
    cols = [
        "n_live_tup", "n_dead_tup", "n_mod_since_analyze",
        "n_tup_ins", "n_tup_upd", "n_tup_del", "n_tup_hot_upd",
        "vacuum_count", "autovacuum_count", "analyze_count", "autoanalyze_count",
        "last_vacuum", "last_autovacuum", "last_analyze", "last_autoanalyze",
    ]
    return dict(zip(cols, row))


def _pg_stat_io_vacuum(cur) -> dict:
    """Return aggregate vacuum I/O from pg_stat_io. Empty dict on PG<16."""
    try:
        cur.execute(
            """
            SELECT COALESCE(SUM(reads), 0), COALESCE(SUM(writes), 0),
                   COALESCE(SUM(read_time), 0), COALESCE(SUM(write_time), 0)
            FROM pg_stat_io
            WHERE context = 'vacuum'
            """
        )
        r = cur.fetchone()
        return {
            "io_vacuum_reads": int(r[0]),
            "io_vacuum_writes": int(r[1]),
            "io_vacuum_read_time": float(r[2]),
            "io_vacuum_write_time": float(r[3]),
        }
    except psycopg2.Error:
        # PG<16, or pg_stat_io not available: keep going without those cols.
        return {}


def _active_vacuums(cur) -> int:
    cur.execute(
        """
        SELECT COUNT(*) FROM pg_stat_activity
        WHERE (query ILIKE 'autovacuum:%%logs%%'
               OR query ILIKE 'VACUUM%%logs%%')
          AND state = 'active'
        """
    )
    return int(cur.fetchone()[0])


def _parse_flush_log(flush_log_cmd: Optional[str]) -> dict:
    """Run flush_log_cmd, parse latencies, return summary. Empty if no cmd."""
    if not flush_log_cmd:
        return {}
    try:
        out = subprocess.run(
            flush_log_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        ).stdout
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.warning("flush-log-cmd failed: %s", exc)
        return {}

    latencies_ms: list[float] = []
    slow = 0
    for line in out.splitlines():
        m = FLUSH_RE.search(line)
        if not m:
            continue
        try:
            latencies_ms.append(float(m.group(1)) * 1000.0)
        except ValueError:
            continue
        if SLOW_FLUSH_RE.search(line):
            slow += 1

    if not latencies_ms:
        return {"flush_batches": 0, "flush_slow_batches": slow}

    latencies_ms.sort()

    def pct(p: float) -> float:
        if len(latencies_ms) < 2:
            return latencies_ms[-1]
        idx = min(len(latencies_ms) - 1, int(round((p / 100.0) * (len(latencies_ms) - 1))))
        return latencies_ms[idx]

    return {
        "flush_batches": len(latencies_ms),
        "flush_slow_batches": slow,
        "flush_p50_ms": statistics.median(latencies_ms),
        "flush_p95_ms": pct(95),
        "flush_p99_ms": pct(99),
        "flush_max_ms": latencies_ms[-1],
    }


def snapshot(flush_log_cmd: Optional[str] = None, notes: Optional[str] = None) -> None:
    with psycopg2.connect(**_conn_params()) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            stats = _pg_stat_user_tables(cur)
            if not stats:
                logger.warning("no pg_stat_user_tables row for public.logs — table missing?")
                return
            io = _pg_stat_io_vacuum(cur)
            active = _active_vacuums(cur)

        flush = _parse_flush_log(flush_log_cmd)

        row = {**stats, **io, "active_vacuums": active, **flush, "notes": notes}
        cols = list(row.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        col_sql = ", ".join(cols)
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO vacuum_metrics ({col_sql}) VALUES ({placeholders})",
                [row[c] for c in cols],
            )
        conn.commit()

    logger.info(
        "snapshot: dead=%s live=%s dead/live=%.4f autovac=%s vac=%s active_vac=%s%s",
        stats.get("n_dead_tup"),
        stats.get("n_live_tup"),
        (stats["n_dead_tup"] / stats["n_live_tup"]) if stats.get("n_live_tup") else 0.0,
        stats.get("autovacuum_count"),
        stats.get("vacuum_count"),
        active,
        f" flush_p95={flush['flush_p95_ms']:.0f}ms" if flush.get("flush_p95_ms") else "",
    )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--init", action="store_true", help="create the vacuum_metrics table")
    g.add_argument("--once", action="store_true", help="capture one snapshot and exit")
    g.add_argument("--loop", type=int, metavar="SECS", help="loop, sleeping SECS between snapshots")
    p.add_argument(
        "--flush-log-cmd",
        help="shell command whose stdout is scanned for 'Flushed N logs in X.XXXs' "
        "lines to compute batch flush P50/P95/P99 between snapshots",
    )
    p.add_argument("--notes", help="free-form note stored with each snapshot")
    args = p.parse_args()

    try:
        if args.init:
            init_schema()
            return 0

        if args.once:
            snapshot(args.flush_log_cmd, args.notes)
            return 0

        interval = max(30, int(args.loop))
        logger.info("collecting every %ds (Ctrl-C to stop)", interval)
        while True:
            try:
                snapshot(args.flush_log_cmd, args.notes)
            except psycopg2.Error as exc:
                logger.warning("snapshot failed: %s", exc)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("interrupted, exiting")
        return 0


if __name__ == "__main__":
    sys.exit(main())
