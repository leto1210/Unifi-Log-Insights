# Configuration Reference

Every environment variable the container reads, what it controls, and safe defaults. Set them in your `docker-compose.yml` or via a `.env` file.

## Required

| Var | Purpose | Notes |
| --- | --- | --- |
| `SECRET_KEY` | KDF/Fernet key for encrypting stored API keys in the DB | Random string ≥ 32 chars. **Do not change** on an existing DB — you'll lose access to any stored API key. |
| `POSTGRES_PASSWORD` | Superuser password for the embedded PostgreSQL | Only used with the embedded DB (default mode) |

## Core

| Var | Default | Purpose |
| --- | --- | --- |
| `TZ` | `UTC` | Container timezone. Affects retention cleanup window and log display. |
| `LOG_LEVEL` | `INFO` | One of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Applies to receiver + API. |
| `AUTH_ENABLED` | `false` | Enable session-based auth. Enables the login screen and required for MCP tokens. |

## UniFi integration

| Var | Default | Purpose |
| --- | --- | --- |
| `UNIFI_HOST` | *(empty)* | e.g. `https://192.168.1.1`. When set, unlocks device/client names, firewall syslog toggle, network discovery. |
| `UNIFI_API_KEY` | *(empty)* | UniFi OS API key (preferred). |
| `UNIFI_SITE` | `default` | Site id for multi-site controllers. |
| `UNIFI_VERIFY_SSL` | `true` | Set to `false` for self-signed controller certs. |
| `UNIFI_POLL_INTERVAL` | `300` | Seconds between polls for device/client updates. |
| `UNIFI_ENABLED` | *(runtime)* | Runtime toggle in Settings; env var override rarely needed. |

Self-hosted (UniFi Network Server) controllers use username/password instead of an API key — set them via the Settings UI, no env var equivalent.

## GeoIP / Threat intelligence

| Var | Default | Purpose |
| --- | --- | --- |
| `MAXMIND_ACCOUNT_ID` | *(empty)* | Numeric ID from MaxMind. Required for cron-driven GeoIP updates. |
| `MAXMIND_LICENSE_KEY` | *(empty)* | MaxMind license key. |
| `ABUSEIPDB_API_KEY` | *(empty)* | Enables threat scoring + daily blacklist pre-seed. Free tier = 1000 lookups/day. |
| `RDNS_ENABLED` | `true` | Reverse-DNS lookup with per-status TTL cache. Set to `false` if your resolver is unreliable or you don't want the DNS traffic. |

## Retention

| Var | Default | Purpose |
| --- | --- | --- |
| `RETENTION_DAYS` | `60` | General log retention. Adjustable at runtime via Settings (Settings > cleanup wins over env). |
| `DNS_RETENTION_DAYS` | `10` | DNS logs retention (shorter — they're voluminous). |
| `RETENTION_CLEANUP_TIME` | `03:00` | Daily cleanup start time, `HH:MM` container-local. |
| `RETENTION_TIME` | *(deprecated)* | Legacy alias for `RETENTION_CLEANUP_TIME`. Warns once at boot, will be removed. |

Retention cleanup runs in batches with `SKIP LOCKED` to avoid blocking ingestion. Autovacuum is tuned to reclaim dead tuples promptly (`scale_factor=0.01` on the logs table).

## Pi-hole integration

| Var | Default | Purpose |
| --- | --- | --- |
| `PIHOLE_ENABLED` | `false` | Enable the Pi-hole v6+ query-log poller. |
| `PIHOLE_HOST` | *(empty)* | e.g. `http://pihole.lan:80` |
| `PIHOLE_PASSWORD` | *(empty)* | Web UI password (used for the session-based API). |
| `PIHOLE_POLL_INTERVAL` | `60` | Seconds between polls. |

AdGuard Home has an equivalent — configure it in Settings > Integrations after boot (no env vars).

## External database

Setting any of the `DB_*` vars to a non-localhost value disables the embedded Postgres and connects to your external instance. See the [External PostgreSQL Migration Guide](External-PostgreSQL-Migration-Guide) for the full flow.

| Var | Default | Purpose |
| --- | --- | --- |
| `DB_HOST` | `127.0.0.1` | External Postgres host. `127.0.0.1`/`localhost` = embedded mode. |
| `DB_PORT` | `5432` | |
| `DB_NAME` | `unifi_logs` | |
| `DB_USER` | `unifi` | |
| `DB_PASSWORD` | *(empty)* | Required in external mode. |
| `DB_SSLMODE` | `prefer` | One of `disable`, `allow`, `prefer`, `require`, `verify-ca`, `verify-full`. |
| `DB_SSLROOTCERT` | *(empty)* | CA cert path (inside container) — needed for `verify-ca`/`verify-full`. |
| `DB_SSLCERT` / `DB_SSLKEY` | *(empty)* | Client cert + key for mTLS. |

## Precedence

For values that appear in both env and Settings UI (retention days, cleanup time, RDNS toggle), **UI value wins**. The env value is the fallback when nothing is stored. Source is reported in the health endpoint response (`retention_days_source: 'ui'|'env'|'default'`).
