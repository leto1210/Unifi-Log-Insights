#!/bin/bash
# MaxMind GeoLite2 database updater
# Runs geoipupdate and signals the receiver to reload databases.
#
# A client-side freshness guard prevents MaxMind's daily download limit from
# being tripped by repeated invocations (redeploys, container restart loops,
# manual re-runs, cron misfires). If the databases were refreshed within
# GEOIP_MIN_UPDATE_INTERVAL_HOURS, the download is skipped. The scheduled cron
# runs every 3-4 days, so it is never affected by this guard.
#
# Usage: geoip-update.sh [--force]
#   --force  Bypass the freshness guard and download unconditionally.

LOG_PREFIX="[geoip-update]"
DB_DIR="/app/maxmind"
MIN_INTERVAL_HOURS="${GEOIP_MIN_UPDATE_INTERVAL_HOURS:-12}"

FORCE=0
if [ "$1" = "--force" ]; then
    FORCE=1
fi

# Freshness guard: skip if any database was updated within the min interval.
if [ "$FORCE" -ne 1 ]; then
    newest_mtime=0
    for db in "$DB_DIR/GeoLite2-City.mmdb" "$DB_DIR/GeoLite2-ASN.mmdb"; do
        if [ -f "$db" ]; then
            mtime=$(stat -c %Y "$db" 2>/dev/null || echo 0)
            if [ "$mtime" -gt "$newest_mtime" ]; then
                newest_mtime="$mtime"
            fi
        fi
    done

    if [ "$newest_mtime" -gt 0 ]; then
        age_seconds=$(( $(date +%s) - newest_mtime ))
        min_seconds=$(( MIN_INTERVAL_HOURS * 3600 ))
        if [ "$age_seconds" -lt "$min_seconds" ]; then
            age_hours=$(( age_seconds / 3600 ))
            echo "$LOG_PREFIX Databases updated ${age_hours}h ago (< ${MIN_INTERVAL_HOURS}h); skipping download to protect MaxMind daily limit. Use --force to override."
            exit 0
        fi
    fi
fi

echo "$LOG_PREFIX Starting GeoLite2 database update..."

# Run geoipupdate
if geoipupdate -d "$DB_DIR" -f /etc/GeoIP.conf -v 2>&1; then
    echo "$LOG_PREFIX GeoLite2 databases updated successfully"

    # Signal receiver to reload databases (SIGUSR1)
    RECEIVER_PID=$(pgrep -f "python.*main.py" | head -1)
    if [ -n "$RECEIVER_PID" ]; then
        kill -USR1 "$RECEIVER_PID"
        echo "$LOG_PREFIX Sent reload signal to receiver (PID $RECEIVER_PID)"
    else
        echo "$LOG_PREFIX WARNING: Receiver process not found, databases will load on next restart"
    fi
else
    echo "$LOG_PREFIX ERROR: geoipupdate failed"
fi
