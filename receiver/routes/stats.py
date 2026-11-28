"""Dashboard statistics endpoint."""

import csv
import io
import ipaddress
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from psycopg2.errors import QueryCanceled
from psycopg2.extras import RealDictCursor

from db import get_config, get_wan_ips_from_config
from deps import get_conn, put_conn, enricher_db
from ip_identity import load_identity_config, annotate_record, annotate_ip
from query_helpers import (parse_time_range, build_log_query, validate_time_params,
                          VALID_TIME_RANGES, device_name_client_lateral,
                          device_name_device_lateral, device_name_coalesce,
                          sanitize_csv_cell)
from routes._response_cache import ttl_cache
import stats_rollup

# Dashboard stats — each first-page-load request runs 4-10 aggregations over
# the multi-million-row `logs` table. Cache for 30 s so repeated loads /
# tab-flipping don't re-fire the whole cascade. First hit still pays full cost.
_STATS_TTL_SECS = 30

# The per-IP top-N tables are not in the hourly rollup and scan raw `logs`:
# ~4 s warm for 24h, but past 30 s under ingest contention or a cold cache.
# ponytail: raw scans still exceed this on 7d+ while logs_legacy is in range;
# roll the per-IP tables up if long ranges must always answer.
_TABLES_STATEMENT_TIMEOUT = '90s'

logger = logging.getLogger('api.stats')

router = APIRouter()


def _apply_ip_filters(where, params, src_ip, dst_ip, interface_in, interface_out) -> tuple[str, list]:
    """Validate and append IP/interface exact-match filters to a WHERE clause."""
    if src_ip:
        try:
            ipaddress.ip_address(src_ip)
        except ValueError as err:
            raise HTTPException(status_code=400, detail="Invalid src_ip") from err
        where += " AND src_ip = %s::inet"
        params.append(src_ip)
    if dst_ip:
        try:
            ipaddress.ip_address(dst_ip)
        except ValueError as err:
            raise HTTPException(status_code=400, detail="Invalid dst_ip") from err
        where += " AND dst_ip = %s::inet"
        params.append(dst_ip)
    if interface_in:
        where += " AND interface_in = %s"
        params.append(interface_in)
    if interface_out:
        where += " AND interface_out = %s"
        params.append(interface_out)
    return where, params


def _build_exclude_ips():
    """Build the WAN IP exclusion list used by top-N queries."""
    wan_ips = get_wan_ips_from_config(enricher_db)
    exclude_ips = ['0.0.0.0']
    for ip in wan_ips:
        if ip not in exclude_ips:
            exclude_ips.append(ip)
    return exclude_ips


def _annotate_internal_ips(*ip_lists):
    """Annotate internal IP lists with gateway/WAN/VPN device names."""
    cfg = load_identity_config(enricher_db)
    for ip_list in ip_lists:
        for item in ip_list:
            name, vlan, _ = annotate_ip(cfg, item['ip'], item.get('device_name'))
            if name and not item.get('device_name'):
                item['device_name'] = name
            if vlan is not None:
                item['vlan'] = vlan


def _query_top_blocked_ips(cur, cutoff, exclude_ips):
    """Top blocked external IPs (public src_ip, exclude WAN)."""
    cur.execute(
        "SELECT host(src_ip) as ip, COUNT(*) as count, "
        "MAX(geo_country) as country, MAX(asn_name) as asn, "
        "MAX(threat_score) as threat_score "
        "FROM logs "
        "WHERE timestamp >= %s AND rule_action = 'block' AND src_ip IS NOT NULL "
        "AND host(src_ip) != ALL(%s) "
        "AND is_public_inet(src_ip) "
        "GROUP BY src_ip ORDER BY count DESC LIMIT 10",
        [cutoff, exclude_ips]
    )
    return [dict(r) for r in cur.fetchall()]


def _query_top_blocked_internal_ips(cur, cutoff):
    """Top blocked internal IPs with device name enrichment."""
    cur.execute(
        "WITH top_ips AS ("
        "  SELECT src_ip, host(src_ip) as ip, COUNT(*) as count "
        "  FROM logs "
        "  WHERE timestamp >= %s AND rule_action = 'block' AND src_ip IS NOT NULL "
        "  AND NOT is_public_inet(src_ip) "
        "  GROUP BY src_ip ORDER BY count DESC LIMIT 10"
        ") SELECT t.ip, t.count, "
        + device_name_coalesce('c', column_alias='device_name') + " "
        "FROM top_ips t "
        + device_name_client_lateral('t.src_ip', 'c', recency_expr='%s') + " "
        "ORDER BY t.count DESC",
        [cutoff, cutoff]
    )
    return [dict(r) for r in cur.fetchall()]


def _query_by_type(cur, cutoff):
    """Log counts per log_type since cutoff, as {log_type: count} ordered by count desc.

    A plain ``GROUP BY log_type`` makes the planner scan the whole
    ``idx_logs_type_time (log_type, timestamp)`` index (timestamp is not the
    leading column), which exceeds statement_timeout on large tables for 24h+
    ranges. Emulate a loose index scan instead: enumerate the few distinct
    log_types, then range-count each one on (log_type, timestamp).
    """
    cur.execute(
        "WITH RECURSIVE t AS ("
        "  (SELECT log_type FROM logs ORDER BY log_type LIMIT 1) "
        "  UNION ALL "
        "  SELECT (SELECT log_type FROM logs WHERE log_type > t.log_type "
        "          ORDER BY log_type LIMIT 1) FROM t WHERE t.log_type IS NOT NULL"
        ") "
        "SELECT t.log_type, (SELECT COUNT(*) FROM logs l "
        "  WHERE l.log_type = t.log_type AND l.timestamp >= %s) AS count "
        "FROM t WHERE t.log_type IS NOT NULL",
        [cutoff]
    )
    rows = sorted(cur.fetchall(), key=lambda r: r['count'], reverse=True)
    return {r['log_type']: r['count'] for r in rows if r['count']}


def _query_top_threat_ips(cur, cutoff, exclude_ips):
    """Top threat IPs with categories from ip_threats and last_seen ISO format."""
    cur.execute(
        "SELECT host(l.src_ip) as ip, COUNT(*) as count, "
        "MAX(l.geo_country) as country, MAX(l.asn_name) as asn, "
        "MAX(l.geo_city) as city, MAX(l.rdns) as rdns, "
        "MAX(l.threat_score) as threat_score, "
        "COALESCE(MAX(l.threat_categories), MAX(t.threat_categories)) as threat_categories, "
        "MAX(l.timestamp) as last_seen "
        "FROM logs l "
        "LEFT JOIN ip_threats t ON l.src_ip = t.ip "
        "WHERE l.timestamp >= %s AND l.threat_score > 50 AND l.src_ip IS NOT NULL "
        "AND host(l.src_ip) != ALL(%s) "
        "GROUP BY l.src_ip ORDER BY max(l.threat_score) DESC, count DESC LIMIT 10",
        [cutoff, exclude_ips]
    )
    results = []
    for r in cur.fetchall():
        row = dict(r)
        if row.get('last_seen'):
            row['last_seen'] = row['last_seen'].isoformat()
        results.append(row)
    return results


def _query_top_allowed_destinations(cur, cutoff, exclude_ips):
    """Top allowed external destinations (public dst_ip, exclude WAN)."""
    cur.execute(
        "SELECT host(dst_ip) as ip, COUNT(*) as count, "
        "MAX(geo_country) as country, MAX(asn_name) as asn "
        "FROM logs "
        "WHERE timestamp >= %s AND rule_action = 'allow' AND dst_ip IS NOT NULL "
        "AND host(dst_ip) != ALL(%s) "
        "AND is_public_inet(dst_ip) "
        "GROUP BY dst_ip ORDER BY count DESC LIMIT 10",
        [cutoff, exclude_ips]
    )
    return [dict(r) for r in cur.fetchall()]


def _query_top_dns(cur, cutoff):
    """Top DNS queries, sourced according to which integrations are enabled.

    Both DNS integrations write different targets:
      * AdGuard poller  → `adguard_logs.domain`
      * Pi-hole poller  → `logs.log_type='dns' AND dns_query`

    The widget respects the existing `adguard_enabled` / `pihole_enabled`
    toggles (Settings → Integrations). Enable both → UNION and dedupe by
    domain. Enable neither → return empty (a truthful state; the widget
    renders "No data" until the user turns one on).

    Rationale for gating instead of always-UNION: on an AdGuard-only box
    the Pi-hole CTE scans through `idx_logs_nondns_timestamp` for nothing
    and can push `/api/stats/tables` past the 30 s statement_timeout.
    Gating on the enabled flag skips the empty side entirely.
    """
    adguard_on = bool(get_config(enricher_db, 'adguard_enabled', False))
    pihole_on = bool(get_config(enricher_db, 'pihole_enabled', False))

    if adguard_on and pihole_on:
        cur.execute(
            """
            SELECT name AS dns_query, SUM(c)::bigint AS count
            FROM (
                SELECT domain AS name, COUNT(*)::bigint AS c
                FROM adguard_logs
                WHERE timestamp >= %s AND domain <> ''
                GROUP BY domain
                UNION ALL
                SELECT dns_query AS name, COUNT(*)::bigint AS c
                FROM logs
                WHERE log_type = 'dns' AND timestamp >= %s AND dns_query IS NOT NULL
                GROUP BY dns_query
            ) merged
            GROUP BY name
            ORDER BY count DESC
            LIMIT 10
            """,
            [cutoff, cutoff],
        )
    elif adguard_on:
        cur.execute(
            """
            SELECT domain AS dns_query, COUNT(*)::bigint AS count
            FROM adguard_logs
            WHERE timestamp >= %s AND domain <> ''
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 10
            """,
            [cutoff],
        )
    elif pihole_on:
        cur.execute(
            """
            SELECT dns_query, COUNT(*)::bigint AS count
            FROM logs
            WHERE log_type = 'dns' AND timestamp >= %s AND dns_query IS NOT NULL
            GROUP BY dns_query
            ORDER BY count DESC
            LIMIT 10
            """,
            [cutoff],
        )
    else:
        return []

    return [dict(r) for r in cur.fetchall()]


def _query_top_active_internal_ips(cur, cutoff):
    """Top active internal IPs (most allowed traffic, exclude gateway IPs)."""
    gateway_ips = get_config(enricher_db, 'gateway_ips') or []
    gw_filter = "  AND host(src_ip) != ALL(%s) " if gateway_ips else ""
    params = [cutoff, gateway_ips, cutoff] if gateway_ips else [cutoff, cutoff]
    cur.execute(
        "WITH top_ips AS ("
        "  SELECT src_ip, host(src_ip) as ip, COUNT(*) as count "
        "  FROM logs "
        "  WHERE timestamp >= %s AND rule_action = 'allow' AND src_ip IS NOT NULL "
        "  AND NOT is_public_inet(src_ip) "
        + gw_filter +
        "  GROUP BY src_ip ORDER BY count DESC LIMIT 10"
        ") SELECT t.ip, t.count, "
        + device_name_coalesce('c', column_alias='device_name') + " "
        "FROM top_ips t "
        + device_name_client_lateral('t.src_ip', 'c', recency_expr='%s') + " "
        "ORDER BY t.count DESC",
        params
    )
    return [dict(r) for r in cur.fetchall()]


def _get_bucket(time_range):
    """Return the adaptive time bucket for a given time_range string."""
    bucket_map = {
        '1h': 'hour', '6h': 'hour', '24h': 'hour',
        '7d': 'day', '30d': 'day', '60d': 'day',
        '90d': 'week',
        '180d': 'month', '365d': 'month',
    }
    return bucket_map.get(time_range, 'day')


def _query_logs_over_time(cur, cutoff, bucket):
    """Logs over time with adaptive bucketing."""
    cur.execute(
        f"SELECT date_trunc('{bucket}', timestamp) as period, COUNT(*) as count "
        "FROM logs WHERE timestamp >= %s "
        "GROUP BY period ORDER BY period",
        [cutoff]
    )
    return [
        {'period': r['period'].isoformat(), 'count': r['count']}
        for r in cur.fetchall()
    ]


def _query_traffic_by_action(cur, cutoff, bucket):
    """Traffic by action over time (firewall logs only)."""
    cur.execute(
        f"SELECT date_trunc('{bucket}', timestamp) as period, "
        "rule_action, COUNT(*) as count "
        "FROM logs WHERE timestamp >= %s AND log_type = 'firewall' "
        "AND rule_action IS NOT NULL "
        "GROUP BY period, rule_action ORDER BY period",
        [cutoff]
    )
    action_map = {}
    for r in cur.fetchall():
        p = r['period'].isoformat()
        if p not in action_map:
            action_map[p] = {'period': p, 'allow': 0, 'block': 0, 'redirect': 0}
        action = r['rule_action']
        if action in ('allow', 'block', 'redirect'):
            action_map[p][action] = r['count']
    return sorted(action_map.values(), key=lambda x: x['period'])


# Filters shared by the raw and rollup paths of the top countries/services tables.
_COUNTRIES_WHERE = ("rule_action IN ('block', 'allow') AND geo_country IS NOT NULL "
                    "AND (rule_action = 'block' OR direction = 'outbound')")
_SERVICES_WHERE = "rule_action IN ('block', 'allow') AND service_name IS NOT NULL"


def _top_by_action(rows, key):
    """Split (value, rule_action, count) rows into top-10 blocked and allowed lists."""
    def top(action_is_block):
        """Top 10 entries for one side, highest count first."""
        entries = [{key: value, 'count': n} for value, action, n in rows
                   if (action == 'block') == action_is_block]
        return sorted(entries, key=lambda x: -x['count'])[:10]
    return top(True), top(False)


def _desc(counts_by_key):
    """{key: count} ordered by count descending, zero counts dropped."""
    return dict(sorted(((k, n) for k, n in counts_by_key.items() if n),
                       key=lambda kv: kv[1], reverse=True))


def _overview_from_rollup(cur, cutoff, span):
    """total/allowed/blocked/by_direction/by_type from the hourly rollup (no threats)."""
    total = allowed = blocked = 0
    by_type, by_direction = {}, {}
    for (log_type, action, direction), n in stats_rollup.counts(
            cur, cutoff, span,
            [('log_type', 'log_type'), ('rule_action', 'rule_action'), ('direction', 'direction')]).items():
        total += n
        by_type[log_type] = by_type.get(log_type, 0) + n
        if action == 'block':
            blocked += n
        if log_type == 'firewall' and action == 'allow':
            allowed += n
        if direction is not None:
            by_direction[direction] = by_direction.get(direction, 0) + n
    return {'total': total, 'allowed': allowed, 'blocked': blocked,
            'by_direction': _desc(by_direction), 'by_type': _desc(by_type)}


def _charts_from_rollup(cur, cutoff, span, bucket):
    """(logs_over_time, traffic_by_action) from the hourly rollup, same shape as the raw queries."""
    per_period, action_map = {}, {}  # keyed by datetime: sorting ISO strings breaks across DST
    for (period, log_type, action), n in stats_rollup.counts(
            cur, cutoff, span,
            [('period', f"date_trunc('{bucket}', {{ts}})"),
             ('log_type', 'log_type'), ('rule_action', 'rule_action')]).items():
        per_period[period] = per_period.get(period, 0) + n
        if log_type == 'firewall' and action is not None:
            entry = action_map.setdefault(
                period, {'period': period.isoformat(), 'allow': 0, 'block': 0, 'redirect': 0})
            if action in entry:
                entry[action] += n
    logs_over_time = [{'period': p.isoformat(), 'count': per_period[p]} for p in sorted(per_period)]
    return logs_over_time, [action_map[p] for p in sorted(action_map)]


@router.get("/api/stats")
def get_stats(
    time_range: str = Query("24h", description="1h,6h,24h,7d,30d,60d"),
):
    """Return aggregated dashboard stats: counts, top IPs, service breakdown, and trends.

    The union of /api/stats/overview, /tables and /charts, so it takes their
    hourly-rollup path and shares their response cache instead of re-running
    every aggregation over raw `logs` (which timed out on 7d+ ranges).
    """
    return {
        **get_stats_overview(time_range=time_range),
        **get_stats_tables(time_range=time_range),
        **get_stats_charts(time_range=time_range),
    }


@router.get("/api/stats/overview")
@ttl_cache(_STATS_TTL_SECS)
def get_stats_overview(
    time_range: str = Query("24h", description="1h,6h,24h,7d,30d,60d"),
):
    """Lightweight traffic overview: total, allowed, blocked, threats, direction breakdown.

    Single query — designed for the browser extension popup where latency matters.
    """
    cutoff = parse_time_range(time_range)
    if not cutoff:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            span = stats_rollup.plan(cur, cutoff, datetime.now(timezone.utc))
            if span:
                overview = _overview_from_rollup(cur, cutoff, span)
                # threat_score is backfilled late, so it is never rolled up
                cur.execute("SELECT COUNT(*) AS threats FROM logs "
                            "WHERE timestamp >= %s AND threat_score > 50", [cutoff])
                overview['threats'] = cur.fetchone()['threats']
            else:
                cur.execute("""
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (WHERE log_type = 'firewall' AND rule_action = 'allow') AS allowed,
                        COUNT(*) FILTER (WHERE rule_action = 'block') AS blocked,
                        COUNT(*) FILTER (WHERE threat_score > 50) AS threats
                    FROM logs WHERE timestamp >= %s
                """, [cutoff])
                overview = dict(cur.fetchone())

                cur.execute("""
                    SELECT direction, COUNT(*) AS count
                    FROM logs
                    WHERE timestamp >= %s AND direction IS NOT NULL
                    GROUP BY direction ORDER BY count DESC
                """, [cutoff])
                overview['by_direction'] = {r['direction']: r['count'] for r in cur.fetchall()}

                overview['by_type'] = _query_by_type(cur, cutoff)

        conn.commit()
        return {
            'time_range': time_range,
            'total': overview['total'],
            'allowed': overview['allowed'],
            'blocked': overview['blocked'],
            'threats': overview['threats'],
            'by_direction': overview['by_direction'],
            'by_type': overview['by_type'],
        }
    except Exception as e:
        conn.rollback()
        logger.exception("Error fetching stats overview")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    finally:
        put_conn(conn)


@router.get("/api/stats/tables")
@ttl_cache(_STATS_TTL_SECS)
def get_stats_tables(
    time_range: str = Query("24h", description="1h,6h,24h,7d,30d,60d"),
):
    """Top-N table data: blocked/allowed countries, IPs, services, DNS, threats."""
    cutoff = parse_time_range(time_range)
    if not cutoff:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SET LOCAL statement_timeout = '{_TABLES_STATEMENT_TIMEOUT}'")
            # --- WAN IP exclusion (shared across multiple queries) ---
            exclude_ips = _build_exclude_ips()

            span = stats_rollup.plan(cur, cutoff, datetime.now(timezone.utc))
            if span:
                country_rows = [
                    (country, action, n) for (country, action), n in stats_rollup.counts(
                        cur, cutoff, span, [('country', 'geo_country'), ('rule_action', 'rule_action')],
                        _COUNTRIES_WHERE, dim=stats_rollup.DIM_COUNTRY).items()]
                service_rows = [
                    (service, action, n) for (service, action), n in stats_rollup.counts(
                        cur, cutoff, span, [('service_name', 'service_name'), ('rule_action', 'rule_action')],
                        _SERVICES_WHERE, dim=stats_rollup.DIM_SERVICE).items()]
            else:
                # --- Consolidated countries query (blocked + allowed) ---
                cur.execute(
                    "SELECT geo_country AS country, rule_action, COUNT(*) AS count FROM logs "
                    f"WHERE timestamp >= %s AND {_COUNTRIES_WHERE} "
                    "GROUP BY geo_country, rule_action ORDER BY count DESC",
                    [cutoff]
                )
                country_rows = [(r['country'], r['rule_action'], r['count']) for r in cur.fetchall()]

                # --- Consolidated services query (blocked + allowed) ---
                cur.execute(
                    "SELECT service_name, rule_action, COUNT(*) AS count FROM logs "
                    f"WHERE timestamp >= %s AND {_SERVICES_WHERE} "
                    "GROUP BY service_name, rule_action ORDER BY count DESC",
                    [cutoff]
                )
                service_rows = [(r['service_name'], r['rule_action'], r['count']) for r in cur.fetchall()]

            top_blocked_countries, top_allowed_countries = _top_by_action(country_rows, 'country')
            top_blocked_services, top_allowed_services = _top_by_action(service_rows, 'service_name')

            top_blocked_ips = _query_top_blocked_ips(cur, cutoff, exclude_ips)
            top_blocked_internal_ips = _query_top_blocked_internal_ips(cur, cutoff)
            top_threat_ips = _query_top_threat_ips(cur, cutoff, exclude_ips)
            top_allowed_destinations = _query_top_allowed_destinations(cur, cutoff, exclude_ips)
            top_dns = _query_top_dns(cur, cutoff)
            top_active_internal_ips = _query_top_active_internal_ips(cur, cutoff)

            _annotate_internal_ips(top_blocked_internal_ips, top_active_internal_ips)

        conn.commit()
        return {
            'top_blocked_countries': top_blocked_countries,
            'top_blocked_ips': top_blocked_ips,
            'top_blocked_internal_ips': top_blocked_internal_ips,
            'top_threat_ips': top_threat_ips,
            'top_blocked_services': top_blocked_services,
            'top_allowed_destinations': top_allowed_destinations,
            'top_allowed_countries': top_allowed_countries,
            'top_allowed_services': top_allowed_services,
            'top_active_internal_ips': top_active_internal_ips,
            'top_dns': top_dns,
        }
    except QueryCanceled as e:
        # Actionable for MCP agents: a generic 500 makes them retry the same
        # range until their client trips its circuit breaker.
        conn.rollback()
        logger.warning("Stats tables timed out for time_range=%s", time_range)
        raise HTTPException(
            status_code=504,
            detail=f"Stats query timed out for time_range={time_range}; retry with a shorter range",
        ) from e
    except Exception as e:
        conn.rollback()
        logger.exception("Error fetching stats tables")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    finally:
        put_conn(conn)


@router.get("/api/stats/charts")
@ttl_cache(_STATS_TTL_SECS)
def get_stats_charts(
    time_range: str = Query("24h", description="1h,6h,24h,7d,30d,60d"),
):
    """Time-series chart data: logs over time and traffic by action."""
    cutoff = parse_time_range(time_range)
    if not cutoff:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    bucket = _get_bucket(time_range)

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            span = stats_rollup.plan(cur, cutoff, datetime.now(timezone.utc))
            if span:
                logs_over_time, traffic_by_action = _charts_from_rollup(cur, cutoff, span, bucket)
            else:
                logs_over_time = _query_logs_over_time(cur, cutoff, bucket)
                traffic_by_action = _query_traffic_by_action(cur, cutoff, bucket)

        conn.commit()
        return {
            'logs_over_time': logs_over_time,
            'logs_per_hour': logs_over_time,  # backward-compat alias
            'traffic_by_action': traffic_by_action,
        }
    except Exception as e:
        conn.rollback()
        logger.exception("Error fetching stats charts")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    finally:
        put_conn(conn)


@router.get("/api/stats/ip-pairs")
def get_ip_pairs(
    time_range: Optional[str] = Query("24h"),
    time_from: Optional[str] = Query(None),
    time_to: Optional[str] = Query(None),
    log_type: Optional[str] = Query("firewall"),
    rule_action: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    interface: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    src_ip: Optional[str] = Query(None),
    dst_ip: Optional[str] = Query(None),
    dst_port: Optional[str] = Query(None),
    protocol: Optional[str] = Query(None),
    interface_in: Optional[str] = Query(None),
    interface_out: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
):
    """Return top source/destination IP pairs for the connection-pairs table."""
    time_range, time_from, time_to = validate_time_params(time_range, time_from, time_to)

    # Pass dst_port and protocol through build_log_query (they use = matching)
    where, params = build_log_query(
        log_type=log_type, time_range=time_range, time_from=time_from, time_to=time_to,
        src_ip=None, dst_ip=None, ip=None, direction=direction,
        rule_action=rule_action, rule_name=None, country=None, threat_min=None,
        search=None, service=service, interface=interface,
        dst_port=dst_port, protocol=protocol,
    )

    # Exact-match filters for cross-filtering (NOT through build_log_query LIKE path)
    where, params = _apply_ip_filters(where, params, src_ip, dst_ip, interface_in, interface_out)

    sql = f"""
    WITH pair_counts AS (
        SELECT
            src_ip, dst_ip, dst_port, LOWER(protocol) AS protocol,
            MAX(service_name) AS service_name,
            COUNT(*) AS total_count,
            COUNT(*) FILTER (WHERE rule_action = 'allow') AS allow_count,
            COUNT(*) FILTER (WHERE rule_action = 'block') AS block_count,
            MAX(threat_score) AS max_threat_score,
            MAX(asn_name) AS asn_name,
            MAX(direction) AS direction
        FROM logs
        WHERE {where}
          AND src_ip IS NOT NULL AND dst_ip IS NOT NULL
          AND dst_port IS NOT NULL AND protocol IS NOT NULL
        GROUP BY src_ip, dst_ip, dst_port, LOWER(protocol)
        ORDER BY total_count DESC
        LIMIT %s
    )
    SELECT
        host(p.src_ip) AS src_ip, host(p.dst_ip) AS dst_ip,
        p.dst_port, p.protocol, p.service_name,
        p.total_count, p.allow_count, p.block_count, p.max_threat_score, p.asn_name, p.direction,
        """ + device_name_coalesce('cs', 'ds', 'src_device_name') + """,
        """ + device_name_coalesce('cd', 'dd', 'dst_device_name') + """
    FROM pair_counts p
    """ + device_name_client_lateral('p.src_ip', 'cs') + """
    """ + device_name_device_lateral('p.src_ip', 'ds') + """
    """ + device_name_client_lateral('p.dst_ip', 'cd') + """
    """ + device_name_device_lateral('p.dst_ip', 'dd') + """
    ORDER BY p.total_count DESC
    """
    params.append(limit)

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            pairs = [dict(r) for r in cur.fetchall()]

        # Enrich with gateway + WAN + VPN device names
        cfg = load_identity_config(enricher_db)
        for pair in pairs:
            annotate_record(cfg, pair)

        conn.commit()
        return {"pairs": pairs}
    except Exception as e:
        conn.rollback()
        logger.exception("Error fetching IP pairs")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    finally:
        put_conn(conn)


@router.get("/api/stats/ip-pairs/csv")
def get_ip_pairs_csv(
    time_range: Optional[str] = Query("24h"),
    time_from: Optional[str] = Query(None),
    time_to: Optional[str] = Query(None),
    log_type: Optional[str] = Query("firewall"),
    rule_action: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    interface: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    src_ip: Optional[str] = Query(None),
    dst_ip: Optional[str] = Query(None),
    dst_port: Optional[str] = Query(None),
    protocol: Optional[str] = Query(None),
    interface_in: Optional[str] = Query(None),
    interface_out: Optional[str] = Query(None),
):
    """Stream all filtered IP pairs as CSV (hard cap 10,000 rows)."""
    time_range, time_from, time_to = validate_time_params(time_range, time_from, time_to)

    where, params = build_log_query(
        log_type=log_type, time_range=time_range, time_from=time_from, time_to=time_to,
        src_ip=None, dst_ip=None, ip=None, direction=direction,
        rule_action=rule_action, rule_name=None, country=None, threat_min=None,
        search=None, service=service, interface=interface,
        dst_port=dst_port, protocol=protocol,
    )

    where, params = _apply_ip_filters(where, params, src_ip, dst_ip, interface_in, interface_out)

    sql = f"""
    SELECT
        host(src_ip) AS source_ip, host(dst_ip) AS destination_ip,
        dst_port AS port, LOWER(protocol) AS protocol,
        MODE() WITHIN GROUP (ORDER BY service_name) AS service,
        COUNT(*) FILTER (WHERE rule_action = 'allow') AS allow_count,
        COUNT(*) FILTER (WHERE rule_action = 'block') AS block_count
    FROM logs
    WHERE {where}
      AND src_ip IS NOT NULL AND dst_ip IS NOT NULL
      AND dst_port IS NOT NULL AND protocol IS NOT NULL
    GROUP BY src_ip, dst_ip, dst_port, LOWER(protocol)
    ORDER BY (COUNT(*)) DESC
    LIMIT 10000
    """

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')

    def generate():
        """Stream CSV rows from the query result one chunk at a time."""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                cols = [desc[0] for desc in cur.description]
                buf = io.StringIO()
                writer = csv.writer(buf)
                # Header row
                writer.writerow(cols)
                yield buf.getvalue()
                # Data rows
                for row in cur:
                    buf.seek(0)
                    buf.truncate()
                    writer.writerow([sanitize_csv_cell(str(v)) if v is not None else '' for v in row])
                    yield buf.getvalue()
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Error streaming CSV export")
            raise
        finally:
            put_conn(conn)

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ip_pairs_{timestamp}.csv"},
    )
