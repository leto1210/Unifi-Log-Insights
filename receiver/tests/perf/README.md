# Vacuum tuning: measurement harness

Purpose: get numbers behind the aggressive autovacuum settings PR #3 pushed
onto `logs` (`autovacuum_vacuum_scale_factor = 0.01`, `cost_delay = 2`,
`cost_limit = 10000`) and the explicit post-cleanup `VACUUM ANALYZE` gated by
`VACUUM_MIN_DELETED`. Do **not** re-tune before we have a baseline with the
current values.

Everything is read-only against Postgres counters (`pg_stat_user_tables`,
`pg_stat_io`, `pg_stat_activity`) plus one INSERT per snapshot into
`vacuum_metrics`. No `pg_relation_size()`, no `COUNT(*)`.

## Files

| File                | Role                                                        |
| ------------------- | ----------------------------------------------------------- |
| `schema.sql`        | `vacuum_metrics` table DDL (idempotent).                    |
| `vacuum_metrics.py` | Standalone collector: stdlib + `psycopg2`.                  |
| `analysis.sql`       | The six analysis queries, one per question in the brief.    |

## First-time setup

Runs from anywhere with network reach to the DB. Env vars mirror
[`receiver/db/connection.py`](../../db/connection.py): `DB_HOST`, `DB_PORT`,
`DB_NAME`, `DB_USER`, `DB_PASSWORD` (or `POSTGRES_PASSWORD`).

Easiest on prod (core-syno) is to `docker exec` into the receiver container —
`psycopg2` and env vars are already there:

```bash
docker exec -it unifi-log-insight python /app/receiver/tests/perf/vacuum_metrics.py --init
```

If the file isn't shipped in the image, bind-mount it or copy it in:

```bash
docker cp receiver/tests/perf/vacuum_metrics.py unifi-log-insight:/tmp/vacuum_metrics.py
docker cp receiver/tests/perf/schema.sql        unifi-log-insight:/tmp/schema.sql
docker exec -it unifi-log-insight python /tmp/vacuum_metrics.py --init
```

## 24 h baseline collection

**Do NOT use `docker exec -d ... --loop`.** That process dies when the
container restarts (deploys, image pulls). Confirmed 2026-08-31: the loop
lasted 90 min before a deploy killed it, and 2 days went by before anyone
noticed. Use a host-side loop instead.

### Recommended: host-side nohup loop (survives container restarts)

The scripts on the host live in `/tmp/vacuum_perf/`; a wrapper
`/tmp/vacuum_perf/loop.sh` re-`docker cp`s the collector into the container
when the container is missing it (its `/tmp` is ephemeral) and calls
`--once` every 5 min. Contents of `loop.sh`:

```bash
#!/bin/bash
while true; do
  /usr/local/bin/docker exec unifi-log-insight test -f /tmp/vacuum_metrics.py \
    || /usr/local/bin/docker cp /tmp/vacuum_perf/vacuum_metrics.py unifi-log-insight:/tmp/vacuum_metrics.py
  /usr/local/bin/docker exec unifi-log-insight \
    python /tmp/vacuum_metrics.py --once --notes baseline \
    >> /tmp/vacuum_perf/collector.log 2>&1
  sleep 300
done
```

Launch:

```bash
ssh tperigault@core-syno 'setsid nohup bash /tmp/vacuum_perf/loop.sh \
    </dev/null >/tmp/vacuum_perf/loop.out 2>&1 &'
```

Verify a snapshot landed:

```bash
ssh tperigault@core-syno 'tail -3 /tmp/vacuum_perf/collector.log'
```

### DSM (Synology) quirks — read before deploying to core-syno

Every one of these bit us once in the 2026-09-02 rollout. Preserve the
workarounds.

1. **`/tmp` is mounted `noexec`.** `chmod +x loop.sh` succeeds but
   `./loop.sh` returns `Permission denied`. Invoke via `bash loop.sh`
   (bash reads the file as data — bypasses noexec).
2. **`scp` SFTP subsystem fails.** Use `scp -O` (legacy protocol) for
   the initial push of scripts to the host.
3. **`docker` is not in PATH without sudo.** Always use the full path
   `/usr/local/bin/docker`.
4. **No user `crontab` on DSM.** `/etc/crontab` is DSM-managed and needs
   sudo to edit. Use the nohup loop above, or DSM Task Scheduler
   (Panneau de config → Tâches planifiées → Script défini par l'utilisateur,
   trigger "@reboot") if you need reboot-survival.
5. **`pgrep` is missing on DSM.** Use `ps -ef | grep loop.sh | grep -v grep`.
6. **`pkill -f vacuum_perf/loop.sh` matches its own ssh shell** because the
   pattern appears in the shell's command line — pkill suicides before the
   next statement runs. Do the kill in a separate ssh call, or don't kill.
7. **Container env var name is `POSTGRES_PASSWORD`, not `DB_PASSWORD`.**
   The receiver's `build_conn_params` falls back to `POSTGRES_PASSWORD` when
   `DB_PASSWORD` is unset — which is the case in prod. Use
   `PGPASSWORD="${DB_PASSWORD:-$POSTGRES_PASSWORD}"` in any psql wrapper.

### Notes on flush latency

* The receiver logs `Flushed N logs in X.XXXs` at DEBUG level and
  `Slow DB flush: N logs took X.XXs` at WARN. Without `LOG_LEVEL=DEBUG` you
  only see the slow ones — P95/P99 will still be meaningful (they'll converge
  to the slow tail), but P50 will be missing on healthy periods.
* `--flush-log-cmd 'tail -n 5000 /proc/1/fd/1'` targets supervisord, not the
  receiver directly. For fidelity, point at the supervisord log file for the
  receiver process instead (path varies by image build).
* If you want full-fidelity flush stats, `LOG_LEVEL=DEBUG` for 24 h is fine
  — it's one INFO-sized line per batch every ~1 s.

## A/B run for `scale_factor`

Baseline first, then per the brief:

```sql
-- Raise scale_factor to Postgres default-ish (0.2) for a comparison window.
ALTER TABLE logs SET (autovacuum_vacuum_scale_factor = 0.2);
```

Restart is not needed — autovacuum picks up per-table storage params on the
next launcher wake. Add a note to the collector for the new window (kill and
relaunch the loop with a different `--notes` value).

To revert:

```sql
ALTER TABLE logs RESET (autovacuum_vacuum_scale_factor);
-- then re-apply init.sql tuning (0.01) if RESET took it back to global default
```

## Reading results

```bash
ssh tperigault@core-syno "/usr/local/bin/docker exec -i unifi-log-insight sh -c \
    'PGPASSWORD=\"\${DB_PASSWORD:-\$POSTGRES_PASSWORD}\" psql \
        -h \"\$DB_HOST\" -U \"\$DB_USER\" -d \"\$DB_NAME\"'" \
    < receiver/tests/perf/analysis.sql
```

Each block in `analysis.sql` has a comment naming the question it answers:

| Question in brief                            | Query |
| -------------------------------------------- | ----- |
| Autovacuum cadence & duration                | Q1    |
| Explicit VACUUM triggered? how often?        | Q2    |
| `n_dead_tup` trajectory (avg/max, ratio)     | Q3    |
| Insert throughput vs vacuum activity         | Q4    |
| Flush P95 during vs outside VACUUM           | Q5    |
| Vacuum I/O cost (PG16 `pg_stat_io`)          | Q6    |

## Deciding the next move

Trigger levels:

* Autovacuum firing more than ~30 ×/h *and* Q6 shows > 20 % of vacuum I/O:
  `scale_factor` is too aggressive — try `0.05`, re-measure 24 h.
* `n_dead_tup` peaks over 500 k between two consecutive vacuums (Q3 max):
  `scale_factor` is too loose *or* `_run_explicit_vacuum` isn't firing.
  Consider lowering `VACUUM_MIN_DELETED` from 5 000.
* Q5 shows flush P99 more than 2× higher during vacuums than outside: nap the
  explicit VACUUM out of peak ingestion hours (or raise
  `autovacuum_vacuum_cost_delay` to slow autovacuum's I/O).

No tuning change goes in without a 24 h dataset on both sides of the change.

## Cost

`pg_stat_user_tables` / `pg_stat_io` are in-memory counters — one snapshot
is a few microseconds of CPU and a single INSERT (< 1 KB). At 5 min cadence
the collector adds ~300 rows/day; `vacuum_metrics` stays under 1 MB per
month with no maintenance. Truncate whenever a run is over.
