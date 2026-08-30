"""Log-insert column list, INSERT SQL, and the ``count_logs`` helper.

Named ``logs_sql`` (not ``logs``) to avoid shadowing the ``logging`` module
in intra-package imports and to keep the file name distinct from any table
named ``logs``.
"""

# Column names matching the logs table
INSERT_COLUMNS = [
    'timestamp', 'log_type', 'direction',
    'src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol', 'service_name',
    'rule_name', 'rule_desc', 'rule_action',
    'interface_in', 'interface_out',
    'mac_address', 'hostname',
    'dns_query', 'dns_type', 'dns_answer',
    'dhcp_event', 'wifi_event',
    'geo_country', 'geo_city', 'geo_lat', 'geo_lon',
    'asn_number', 'asn_name',
    'threat_score', 'threat_categories', 'rdns',
    'abuse_usage_type', 'abuse_hostnames',
    'abuse_total_reports', 'abuse_last_reported',
    'abuse_is_whitelisted', 'abuse_is_tor',
    'src_device_name', 'dst_device_name',
    'remote_ip',
    'raw_log',
]

INSERT_SQL = f"""
    INSERT INTO logs ({', '.join(INSERT_COLUMNS)})
    VALUES ({', '.join(['%s'] * len(INSERT_COLUMNS))})
"""


def count_logs(db, log_type='firewall'):
    """Count logs by type."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM logs WHERE log_type = %s", [log_type])
            return cur.fetchone()[0]
