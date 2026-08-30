# Getting Started

Bring UniFi Log Insight up in 5 minutes against a UniFi Dream Machine (or any UniFi OS gateway with zone-based firewall).

## 1. Prerequisites

- Docker + Docker Compose on a host with a static IP or hostname on the same network as the UniFi gateway
- A [MaxMind GeoLite2 account](https://www.maxmind.com/en/geolite2/signup) (free — needed for GeoIP/ASN)
- A [UniFi API key](https://help.ui.com/hc/en-us/articles/115003895388) with read access to networks + firewall (Site Admin role is the safe default)
- Optional: an [AbuseIPDB API key](https://www.abuseipdb.com/register?plan=free) for threat scoring

Zone-based firewall is required for firewall policy matching and the Syslog Manager. If you're on the classic engine, migrate via Settings > Policy Engine in the UniFi controller before starting.

## 2. Bring the container up

Copy the reference compose file, edit the credentials, launch:

```bash
git clone https://github.com/leto1210/Unifi-Log-Insights
cd Unifi-Log-Insights
cp .env.example .env
# edit .env — at minimum: SECRET_KEY, POSTGRES_PASSWORD, MAXMIND_*, UNIFI_HOST, UNIFI_API_KEY
docker compose up -d
```

The image is pulled from `ghcr.io/leto1210/unifi-log-insights:latest`. It runs Postgres 16 + the receiver + the FastAPI backend + a cron job for GeoIP updates, all under supervisord.

Check the boot:

```bash
docker logs -f unifi-log-insight
# expect: "Syslog receiver listening on UDP port 514"
curl -sf http://localhost:8090/api/health
```

## 3. Point the UniFi gateway at the receiver

In the UniFi controller: **Settings > System > Advanced > Remote System Logging**.

- Enable
- Host: the IP of your Docker host
- Port: `514`
- Protocol: `UDP`
- Select which log types to send (Firewall is the useful one; DHCP/DNS/System optional)

Save. Logs start flowing within seconds — you'll see the counter climb on the dashboard.

## 4. Enable the Firewall Syslog Manager (optional but recommended)

Once the container is up and the UniFi API is configured, open the app at `http://<host>:8090`, go to **Firewall Syslog Manager**, and toggle logging on the specific policies you care about. Bulk enable/disable via the group toggles or the zone matrix.

Changes are applied immediately on the gateway but may take up to 5 minutes to reflect in the Log Stream.

## 5. Where to next

- [Configuration Reference](Configuration) — every env var, what it does, when to change it
- [MCP Server](MCP) — connect Claude Desktop, Claude Code, or any MCP client to query your network
- [Troubleshooting](Troubleshooting) — common issues and fixes
- [External PostgreSQL Migration Guide](External-PostgreSQL-Migration-Guide) — move to an external DB if you don't want the embedded one
