## Stage 1: Build React UI
FROM node:20-slim AS ui-builder
WORKDIR /ui
COPY ui/package.json ui/package-lock.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

## Stage 2: Runtime
FROM ubuntu:24.04

LABEL org.opencontainers.image.title="UniFi Log Insight"
LABEL org.opencontainers.image.description="Real-time log analysis for UniFi routers — syslog, GeoIP, threat intelligence, and a live dashboard in a single container"
LABEL org.opencontainers.image.source="https://github.com/leto1210/Unifi-Log-Insights"
LABEL org.opencontainers.image.url="https://github.com/leto1210/Unifi-Log-Insights"
LABEL org.opencontainers.image.licenses="BSL-1.1"
LABEL org.opencontainers.image.vendor="leto1210"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PGDATA=/var/lib/postgresql/data

# Install PostgreSQL 16 + Python 3 + supervisor + cron
# libcap2-bin provides setcap, used to grant CAP_NET_BIND_SERVICE to the
# receiver's python so it can bind UDP 514 without running as root.
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    postgresql-16 \
    postgresql-client-16 \
    python3 \
    python3-pip \
    python3-venv \
    supervisor \
    cron \
    tzdata \
    libcap2-bin \
    && rm -rf /var/lib/apt/lists/*

# Install geoipupdate from MaxMind
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && ARCH=$(dpkg --print-architecture) \
    && curl -sSL "https://github.com/maxmind/geoipupdate/releases/download/v7.1.1/geoipupdate_7.1.1_linux_${ARCH}.deb" -o /tmp/geoipupdate.deb \
    && dpkg -i /tmp/geoipupdate.deb \
    && rm /tmp/geoipupdate.deb \
    && apt-get remove -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Create Python venv to avoid system package conflicts.
# --copies (instead of the default symlinks) puts a real python binary inside
# the venv, so setcap can be applied specifically to it without touching the
# host-wide /usr/bin/python3.
RUN python3 -m venv --copies /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies then remove pip (not needed at runtime)
COPY receiver/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip uninstall -y pip setuptools \
    && rm -rf /app/venv/lib/python*/ensurepip \
    && apt-get remove -y python3-pip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy version file and application code
COPY VERSION /app/VERSION
COPY receiver/ /app/
COPY init.sql /app/init.sql
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /app/entrypoint.sh
COPY geoip-update.sh /app/geoip-update.sh
RUN chmod +x /app/entrypoint.sh /app/geoip-update.sh

# Copy built UI
COPY --from=ui-builder /ui/dist /app/static

# Create unprivileged runtime user for receiver + api (+ cron jobs).
# Fixed UID/GID 1000 keeps ownership stable across rebuilds and host bind mounts.
# Grant CAP_NET_BIND_SERVICE to the venv python so the receiver can bind
# UDP 514 (a privileged port) without needing root at runtime.
# GeoIP databases and the update log must be writable by uli (receiver reloads
# them on SIGUSR1; the cron job writes them).
# Ubuntu 24.04 ships a default 'ubuntu' user at UID/GID 1000; remove it so
# 'uli' can claim that slot (the value host bind mounts most often use).
RUN userdel -r ubuntu 2>/dev/null || true \
    && groupadd -g 1000 uli \
    && useradd -u 1000 -g 1000 -m -s /usr/sbin/nologin uli \
    && mkdir -p /app/maxmind \
    && chown -R uli:uli /app \
    && touch /var/log/geoip-update.log \
    && chown uli:uli /var/log/geoip-update.log \
    && setcap 'cap_net_bind_service=+ep' "$(readlink -f /app/venv/bin/python3)"

WORKDIR /app

EXPOSE 514/udp
EXPOSE 8000

CMD ["/app/entrypoint.sh"]
