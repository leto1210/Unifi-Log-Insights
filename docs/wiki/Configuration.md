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
| `SETUP_TOKEN` | *(empty)* | Long random token required to enroll the first administrator when `AUTH_ENABLED=true`. |

With `AUTH_ENABLED=true`, an installation with no administrator exposes only
`/api/health`, `/api/auth/status`, and `/api/auth/setup`. Create the first
administrator before using setup/configuration routes. Set a strong `SETUP_TOKEN`
in the container environment. The enrollment request must use HTTPS and send
the token in `X-Setup-Token`; a proxy's `X-Forwarded-Proto` is accepted only
when it also sends the application's `X-ULI-Proxy-Auth` secret. The login page
shows a first-administrator form until enrollment is complete. For an embedded
database, an operator on the Docker host can retrieve the proxy
secret without placing it in a public endpoint:

```sh
docker exec -u postgres unifi-log-insight psql -d unifi_logs -Atc "SELECT value #>> '{}' FROM system_config WHERE key = 'proxy_auth_token'"
```

Keep the returned secret private. Configure the reverse proxy to set
`X-ULI-Proxy-Auth` to that value and `X-Forwarded-Proto` to `https`, then use
the first-administrator form over HTTPS. A local administrative client can
also POST `/api/auth/setup` with `X-Setup-Token` and JSON fields `username`
and `password`:

```http
POST https://your-internal-host/api/auth/setup
Content-Type: application/json
X-Setup-Token: <your SETUP_TOKEN>

{"username":"admin","password":"<new strong password>"}
```

The password must be at least 8 characters and no more than 72 UTF-8 bytes.
The response sets a secure session cookie. Keep the setup token and proxy
secret out of shell history, logs, and support tickets. For an external
database, retrieve the same
`system_config` key through a local administrator connection. With
`AUTH_ENABLED=false`, the internal single-user mode remains available without
this enrollment.

If users already exist but no active administrator remains, first enrollment
is unavailable. Restore an administrator through a local database backup or
controlled maintenance before returning to the login page; the public setup
route must not be used to take over an existing installation.

`/api/setup/status` returns only `setup_complete`. Its former exact
`logs_count` field was removed because it counted the large logs table on a
public setup request. Clients that relied on an exact count must obtain it
separately; this status route no longer provides one.

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

When `UNIFI_API_KEY` comes from the environment, set `UNIFI_HOST` there too.
The key is used only for that configured destination. This pairing requirement
applies only to the API-key (UniFi OS) flow — self-hosted username/password
testing and host changes never read `UNIFI_API_KEY` and are unaffected by it.
A saved key or saved self-hosted credentials cannot be reused when the
controller address changes; provide new credentials for the new controller.
A connection test never sends saved credentials to an address other than the
one associated with them.
When importing a configuration backup, a new UniFi API key is associated with
the effective host. Importing only a host does not move an existing key to it.
An export that includes the saved API key records its bound host, even when
`UNIFI_HOST` overrides the database host. If an older saved key has no valid
host binding, the API refuses to include it until the association is repaired.

## GeoIP / Threat intelligence

| Var | Default | Purpose |
| --- | --- | --- |
| `MAXMIND_ACCOUNT_ID` | *(empty)* | Numeric ID from MaxMind. Required for cron-driven GeoIP updates. |
| `MAXMIND_LICENSE_KEY` | *(empty)* | MaxMind license key. |
| `GEOIP_MIN_UPDATE_INTERVAL_HOURS` | `12` | Freshness guard for GeoIP downloads: `geoip-update.sh` skips downloading only when both databases are present and the older one was refreshed within this many hours, protecting MaxMind's daily download limit without retaining partial data. The Wed/Sat cron is unaffected (>3 days apart). Set `0` to disable; run `geoip-update.sh --force` to bypass once. |
| `ABUSEIPDB_API_KEY` | *(empty)* | Enables threat scoring + daily blacklist pre-seed. Free tier = 1000 `/check` lookups/day. |
| `ABUSEIPDB_ENABLED` | `true` | Runtime kill-switch (Settings > Integrations). Pauses all outbound AbuseIPDB calls without removing the key; env var overrides the toggle when set. |
| `ABUSEIPDB_SAFETY_BUFFER` | `20` | Reserve of daily `/check` calls left unused, so lookups stop *before* the hard cap is hit (avoids the provider's "daily limit reached" email). `0` disables the reserve. |
| `ABUSEIPDB_MIN_HITS` | `3` | A blocked remote IP must be seen this many times before a `/check` lookup is spent on it. Focuses the daily budget on recurring offenders and skips one-shot scanners. Cached and blacklisted IPs are scored regardless. Minimum `1`. |
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

When `PIHOLE_PASSWORD` comes from the environment, set `PIHOLE_HOST` there too.
Changing a saved Pi-hole address requires a new password. Connection tests
cannot reuse the saved password for another address.

Secret-bearing UniFi and Pi-hole requests do not follow HTTP redirects. A
controller that relies on a redirect for its API must be configured with its
final URL instead.

AdGuard Home has an equivalent — configure it in Settings > Integrations after boot (no env vars).

## Enabling / disabling integrations

Each integration (UniFi, Pi-hole, AdGuard Home, AbuseIPDB) has a runtime on/off
switch that acts as a **kill-switch**: turning it off stops all polling and
outbound API calls immediately, **without erasing credentials or API keys**, so
you can re-enable later in one click.

- **UniFi** — Settings > WAN & Networks > UniFi Gateway (`Disable` / `Enable`).
- **Pi-hole / AdGuard Home** — Settings > Integrations (toggle on each panel).
- **AbuseIPDB** — Settings > Integrations (toggle). The key stays in
  `ABUSEIPDB_API_KEY`; only enrichment is paused.

When an integration is off, on-demand endpoints that would call it return
HTTP `409 {"detail": "integration disabled"}` (distinct from `400` when it was
never configured). An env var (`UNIFI_ENABLED`, `PIHOLE_ENABLED`,
`ABUSEIPDB_ENABLED`, …) overrides the Settings toggle when explicitly set.

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
