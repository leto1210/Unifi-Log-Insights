"""Post-boot index specs (used by :meth:`Database.ensure_post_boot_indexes`).

The main ``_ensure_schema`` migration list is kept inline in
:class:`db.core.Database` (not here) so tests that assert on
``inspect.getsource(Database._ensure_schema)`` keep working — they need the
SQL text to appear inside the method body itself.
"""


# Heavyweight indexes created post-boot with CONCURRENTLY for upgrades.
# Fresh installs get these from init.sql; this list handles existing installs.
POST_BOOT_INDEXES = [
    {
        'name': 'idx_logs_spgist_dst_ip_firewall',
        'sql': "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_logs_spgist_dst_ip_firewall "
               "ON logs USING spgist (dst_ip) WHERE log_type = 'firewall'",
        'label': 'SP-GiST dst_ip for WAN detection',
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

# Redundant indexes dropped on upgrade. Each is a leftmost-prefix of an
# existing composite so the planner loses nothing, but they incur write
# amplification on every INSERT. DROP CONCURRENTLY IF EXISTS is idempotent.
POST_BOOT_DROPS = [
    ('idx_logs_type',        "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_type"),
    ('idx_logs_rule_action', "DROP INDEX CONCURRENTLY IF EXISTS idx_logs_rule_action"),
]
