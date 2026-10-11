#!/bin/bash
# Sample who holds back the vacuum horizon (backend_xmin / open transactions)
# around the daily retention run (01:00 local = 23:00 UTC). Read-only.
#
# Context: on 2026-10-03 23:00 UTC the post-retention VACUUM ANALYZE ran 87 s
# but left ~590k dead tuples (vs 898k -> 30 at 15:00). Run on duncan:
#
#   nohup bash xmin_watch.sh >/tmp/xmin_watch.log 2>&1 &
#
# Env: START/END (UTC, HH:MM, default 22:55/23:15), INTERVAL (s, default 10).
START=${START:-22:55}
END=${END:-23:15}
INTERVAL=${INTERVAL:-10}
PSQL="docker exec unifi-logs-postgres psql -h 127.0.0.1 -U unifi -d unifi_logs -X -q"

SQL="
select now()::time(0) as t, pid, application_name app, state, backend_xmin,
       age(backend_xmin) xmin_age, now()-xact_start xact_age,
       now()-query_start q_age, left(query, 70) query
from pg_stat_activity
where pid <> pg_backend_pid() and backend_type = 'client backend'
  and (backend_xmin is not null or xact_start < now() - interval '2 seconds')
order by age(backend_xmin) desc nulls last;
select now()::time(0) as t, pid, phase, heap_blks_scanned, heap_blks_total,
       heap_blks_vacuumed
from pg_stat_progress_vacuum;"

while [ "$(date -u +%H:%M)" \< "$START" ]; do sleep 20; done
while [ "$(date -u +%H:%M)" \< "$END" ]; do
  echo "--- $(date -u +%T)"
  timeout 20 $PSQL -c "$SQL" 2>&1
  sleep "$INTERVAL"
done
