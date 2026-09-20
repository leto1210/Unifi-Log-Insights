-- Analysis queries for vacuum_metrics. Run against unifi_logs.
--
-- All queries scope to a 24 h window by default; tighten with WHERE clauses
-- for A/B comparisons across tuning changes.

------------------------------------------------------------
-- Q1. How often does autovacuum actually fire on `logs`?
--     Reports each autovacuum event with the gap since the previous one.
--     (Window funcs aren't allowed in WHERE, so LAG lives in a CTE.)
------------------------------------------------------------
WITH lagged AS (
    SELECT captured_at,
           last_autovacuum,
           autovacuum_count,
           LAG(autovacuum_count) OVER (ORDER BY captured_at) AS prev_count,
           LAG(last_autovacuum)  OVER (ORDER BY captured_at) AS prev_ts
    FROM vacuum_metrics
    WHERE captured_at > NOW() - INTERVAL '24 hours'
)
SELECT captured_at,
       last_autovacuum,
       autovacuum_count,
       last_autovacuum - prev_ts AS gap_since_prev
FROM lagged
WHERE autovacuum_count > COALESCE(prev_count, 0)
ORDER BY captured_at;

------------------------------------------------------------
-- Q2. Does the explicit post-cleanup VACUUM ever trigger?
--     `vacuum_count` (as opposed to `autovacuum_count`) increments only on
--     the manual VACUUM path used by _run_explicit_vacuum().
------------------------------------------------------------
SELECT captured_at,
       last_vacuum,
       vacuum_count,
       vacuum_count - LAG(vacuum_count) OVER (ORDER BY captured_at)
           AS explicit_vacs_since_prev
FROM vacuum_metrics
WHERE captured_at > NOW() - INTERVAL '24 hours'
ORDER BY captured_at;

------------------------------------------------------------
-- Q3. n_dead_tup trajectory: mean, max, and dead/live ratio over the window.
------------------------------------------------------------
SELECT date_trunc('hour', captured_at)     AS hour,
       ROUND(AVG(n_dead_tup))              AS avg_dead,
       MAX(n_dead_tup)                     AS max_dead,
       ROUND(AVG(n_live_tup))              AS avg_live,
       ROUND(AVG(n_dead_tup::numeric / NULLIF(n_live_tup, 0)), 4)
                                           AS avg_dead_ratio,
       ROUND(MAX(n_dead_tup::numeric / NULLIF(n_live_tup, 0)), 4)
                                           AS max_dead_ratio
FROM vacuum_metrics
WHERE captured_at > NOW() - INTERVAL '24 hours'
GROUP BY 1
ORDER BY 1;

------------------------------------------------------------
-- Q4. Insert throughput vs vacuum activity, per hour.
------------------------------------------------------------
WITH d AS (
    SELECT captured_at,
           n_tup_ins - LAG(n_tup_ins) OVER (ORDER BY captured_at)  AS d_ins,
           n_tup_del - LAG(n_tup_del) OVER (ORDER BY captured_at)  AS d_del,
           autovacuum_count - LAG(autovacuum_count)
               OVER (ORDER BY captured_at)                         AS d_autovac,
           vacuum_count - LAG(vacuum_count)
               OVER (ORDER BY captured_at)                         AS d_vac,
           active_vacuums
    FROM vacuum_metrics
    WHERE captured_at > NOW() - INTERVAL '24 hours'
)
SELECT date_trunc('hour', captured_at) AS hour,
       SUM(GREATEST(d_ins, 0))         AS inserts,
       SUM(GREATEST(d_del, 0))         AS deletes,
       SUM(GREATEST(d_autovac, 0))     AS autovacs,
       SUM(GREATEST(d_vac, 0))         AS explicit_vacs,
       MAX(active_vacuums)             AS max_concurrent_vac
FROM d
GROUP BY 1
ORDER BY 1;

------------------------------------------------------------
-- Q5. Does batch-flush latency spike when a VACUUM is running?
--     Requires --flush-log-cmd on the collector so flush_p95_ms is populated.
--     Compares P95 flush latency by whether a vacuum was concurrent.
------------------------------------------------------------
SELECT active_vacuums > 0                AS during_vacuum,
       COUNT(*)                          AS snapshots,
       ROUND(AVG(flush_p50_ms))          AS avg_p50_ms,
       ROUND(AVG(flush_p95_ms))          AS avg_p95_ms,
       ROUND(AVG(flush_p99_ms))          AS avg_p99_ms,
       ROUND(MAX(flush_max_ms))          AS max_flush_ms,
       SUM(flush_slow_batches)           AS total_slow_batches
FROM vacuum_metrics
WHERE captured_at > NOW() - INTERVAL '24 hours'
  AND flush_batches IS NOT NULL
  AND flush_batches > 0
GROUP BY 1
ORDER BY 1;

------------------------------------------------------------
-- Q6. Vacuum I/O cost (PG16+ only; NULL rows on older PG).
--     Deltas of pg_stat_io vacuum reads/writes over the window.
------------------------------------------------------------
SELECT date_trunc('hour', captured_at) AS hour,
       MAX(io_vacuum_reads)  - MIN(io_vacuum_reads)   AS vac_reads,
       MAX(io_vacuum_writes) - MIN(io_vacuum_writes)  AS vac_writes,
       ROUND((MAX(io_vacuum_read_time) - MIN(io_vacuum_read_time))::numeric, 1)
                                                      AS vac_read_ms,
       ROUND((MAX(io_vacuum_write_time) - MIN(io_vacuum_write_time))::numeric, 1)
                                                      AS vac_write_ms
FROM vacuum_metrics
WHERE captured_at > NOW() - INTERVAL '24 hours'
  AND io_vacuum_reads IS NOT NULL
GROUP BY 1
ORDER BY 1;
