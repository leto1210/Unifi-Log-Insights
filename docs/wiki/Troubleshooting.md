# Troubleshooting

Common failures with the actual container log line that points at each, and what to do about it.

## Container exits at boot with `Schema migration failed`

Log signature:

```
psycopg2.errors.CantChangeRuntimeParam: parameter "log_autovacuum_min_duration" cannot be changed now
Schema migration failed
[supervisord] WARN exited: receiver (exit status 1; not expected)
```

The runtime `ALTER DATABASE … SET log_autovacuum_min_duration` migration needs superuser privilege to succeed on the target DB and can also fail when the current session doesn't allow it. Fixed in v3.8.0-beta.2+ — the migration is now best-effort (warns and continues). If you're on beta.1 or you built from a commit older than 4c7e45f, upgrade.

## Bulk syslog toggle fails with "Bulk update failed. One or more policies could not be processed."

Log signature:

```
KeyError: 'id'
    at unifi_api.py:… in bulk_patch_logging
```

Some UDM firewall policies come from the Integration API without an `id` field — they can't be PATCHed. Fixed in v3.8.0-beta.3+ (PR #32): the UI no longer offers a toggle for those policies, and the backend skips them gracefully. Upgrade to the current image.

If you still see it after upgrading: `docker logs unifi-log-insight | grep "skipping item with no id"` — the log line dumps the raw policy so we can characterise a new case. Open an issue with the output.

## Ingestion runs but the health check reports 0 logs

1. Confirm the UniFi gateway is reachable and sending: `sudo tcpdump -i <host-iface> -n port 514`. Expect UDP packets from the gateway IP.
2. Check the receiver socket bound: `docker logs unifi-log-insight | grep "listening on UDP port"`. Must say `UDP port 514`.
3. Firewall / NAT on the Docker host may drop the UDP traffic. Test with `nc -u <host-ip> 514` from any machine on the LAN.
4. Docker port mapping: `docker port unifi-log-insight` should list `514/udp -> 0.0.0.0:514`.

## `duplicate key value violates unique constraint` in `_ensure_schema` on boot

Benign — the schema migration retries on rare startup races between the receiver and the API process both trying to run `_ensure_schema` at the same time. There's an advisory lock but the second process still tries the DDL before giving up. If the container comes up healthy afterwards, ignore.

## Retention cleanup log shows deletes but disk usage doesn't drop

Autovacuum reclaim is scheduled aggressively (`scale_factor=0.01`) but VACUUM only frees space to the filesystem when it can truncate the trailing empty pages. Between big cleanups you'll see WAL and dead tuples pile up. The container runs an explicit `VACUUM ANALYZE logs` after any cleanup that deletes more than `VACUUM_MIN_DELETED` rows (see `receiver/db.py`).

If the DB genuinely won't shrink, check `pg_stat_user_tables.n_dead_tup` for the `logs` table — if it's growing, autovacuum isn't keeping up (raise `autovacuum_vacuum_cost_limit`, or investigate long-held transactions holding the tuples visible).

## MCP tool call returns "MCP server disabled"

`Settings > MCP > Enable MCP server` is off, or `AUTH_ENABLED=false`. Enable both. MCP requires auth to be on so tokens have meaning.

## UniFi status shows `connected: false`

Log line:

```
[unifi_api] ERROR: Authentication failed. Check your API key.
```

or:

```
[unifi_api] ERROR: SSL certificate verification failed. Enable "Skip SSL verification" for self-signed certificates.
```

- API key: regenerate in the UniFi controller, paste into Settings > UniFi.
- SSL: for a self-signed cert set `UNIFI_VERIFY_SSL=false` (env) or untick "Verify SSL" in Settings.
- Host: must include the scheme (`https://192.168.1.1`), no trailing slash.

## Container is running but `/api/health` hangs

Almost always DB-side. Check:

```bash
docker exec unifi-log-insight su - postgres -c "psql -c 'SELECT pid, state, wait_event, query FROM pg_stat_activity WHERE state != \\'idle\\';'"
```

If you see a long-running `COUNT(*)` on `logs`, you're on an old image (pre-v3.8.0). Upgrade — `get_stats` uses `pg_class.reltuples` now.

## Docker log volume explodes

The default compose file caps the container's Docker log at 10 MB × 5 rotated files. If you use a custom compose, add:

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "5"
```

## Where to look

- Container logs: `docker logs -f unifi-log-insight`
- Health snapshot: `curl -s http://<host>:8090/api/health | jq`
- Direct DB access (embedded mode): `docker exec -it unifi-log-insight su - postgres -c "psql unifi_logs"`
- App logs table (auth cleanup, retention runs, MCP audit): tables `audit_log`, `sessions` in the DB

Still stuck? [Open an issue](https://github.com/leto1210/Unifi-Log-Insights/issues) with the container logs (`docker logs --tail 200`) attached.
