"""Post-boot index specs (used by :meth:`Database.ensure_post_boot_indexes`).

The main ``_ensure_schema`` migration list is kept inline in
:class:`db.core.Database` (not here) so tests that assert on
``inspect.getsource(Database._ensure_schema)`` keep working — they need the
SQL text to appear inside the method body itself.
"""


def _log_based_wan_detection_active(db):
    """Gate for idx_logs_spgist_dst_ip_firewall.

    That 2.5 GB SP-GiST index exists only to accelerate the `dst_ip << subnet`
    containment scan in Database.detect_gateway_ips(), which runs *solely* when
    UniFi is not authoritative (``unifi_enabled`` false — see
    service/network_identity.py). On a UniFi-managed install the query never
    runs, so the index is pure INSERT write-amplification (maintained on every
    ingested row for a scan that never happens). Gate creation on log-based
    detection being active; when it isn't, ensure_post_boot_indexes() drops the
    index instead, reclaiming the space + write cost — and it comes back
    automatically if UniFi is later disabled.
    """
    return not bool(db.get_config('unifi_enabled', False))


# Heavyweight indexes created post-boot with CONCURRENTLY for upgrades.
# Fresh installs get these from init.sql; this list handles existing installs.
# Optional 'when' key: a predicate (db) -> bool. When present and it returns
# False, the index is not wanted on this install — ensure_post_boot_indexes()
# drops it if present rather than creating it.
POST_BOOT_INDEXES = [
    {
        'name': 'idx_logs_spgist_dst_ip_firewall',
        'sql': "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_logs_spgist_dst_ip_firewall "
               "ON logs USING spgist (dst_ip) WHERE log_type = 'firewall'",
        'label': 'SP-GiST dst_ip for WAN detection',
        'when': _log_based_wan_detection_active,
    },
    {
        'name': 'idx_logs_type_id',
        'sql': "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_logs_type_id "
               "ON logs (log_type, id)",
        'label': 'type+id for purge batches',
    },
    {
        'name': 'idx_logs_nondns_timestamp',
        'sql': "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_logs_nondns_timestamp "
               "ON logs (timestamp DESC) WHERE log_type != 'dns'",
        'label': 'non-DNS retention cleanup',
    },
]

# Redundant / unused indexes dropped on upgrade. DROP CONCURRENTLY IF EXISTS
# is idempotent. Two rationales:
#   1. Leftmost-prefix of an existing composite — the planner loses nothing.
#   2. Low-cardinality single-column index the planner never chose
#      (idx_scan=0 over days of prod traffic) — pure INSERT write-amplification.
# Both only cost write throughput on every ingest.
POST_BOOT_DROPS = [
    # (1) leftmost-prefix duplicates
    ('idx_logs_type',        "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_type"),
    ('idx_logs_rule_action', "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_rule_action"),
    # (2) unused low-cardinality single-column indexes (see db/core.py)
    ('idx_logs_direction',    "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_direction"),
    ('idx_logs_src_port',     "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_src_port"),
    ('idx_logs_dst_port',     "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_dst_port"),
    ('idx_logs_protocol',     "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_protocol"),
    ('idx_logs_service_name', "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_service_name"),
]
