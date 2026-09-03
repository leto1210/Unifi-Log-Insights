-- vacuum_metrics: append-only snapshot of pg_stat_user_tables (+ pg_stat_io if
-- available) for the `logs` table. Populated by vacuum_metrics.py every N min.
--
-- Cheap to read from -- everything comes from in-memory Postgres counters.
-- Deltas between rows give VACUUM cadence, insert/delete throughput, and the
-- n_dead_tup trajectory that motivates the tuned autovacuum scale_factor.

CREATE TABLE IF NOT EXISTS vacuum_metrics (
    id                    BIGSERIAL PRIMARY KEY,
    captured_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- pg_stat_user_tables, filtered to relname='logs'
    n_live_tup            BIGINT,
    n_dead_tup            BIGINT,
    n_mod_since_analyze   BIGINT,
    n_tup_ins             BIGINT,
    n_tup_upd             BIGINT,
    n_tup_del             BIGINT,
    n_tup_hot_upd         BIGINT,
    vacuum_count          BIGINT,
    autovacuum_count      BIGINT,
    analyze_count         BIGINT,
    autoanalyze_count     BIGINT,
    last_vacuum           TIMESTAMPTZ,
    last_autovacuum       TIMESTAMPTZ,
    last_analyze          TIMESTAMPTZ,
    last_autoanalyze      TIMESTAMPTZ,

    -- pg_stat_io aggregate (PG16+); NULL on older versions.
    -- Sums across backend types for context='vacuum' on relation objects.
    io_vacuum_reads       BIGINT,
    io_vacuum_writes      BIGINT,
    io_vacuum_read_time   DOUBLE PRECISION,
    io_vacuum_write_time  DOUBLE PRECISION,

    -- Concurrent VACUUM/autovacuum activity on `logs` at snapshot time
    active_vacuums        INT,

    -- Optional: parsed from receiver logs since previous snapshot.
    -- Populated only when --flush-log-cmd is passed and readable.
    flush_batches         INT,
    flush_slow_batches    INT,
    flush_p50_ms          DOUBLE PRECISION,
    flush_p95_ms          DOUBLE PRECISION,
    flush_p99_ms          DOUBLE PRECISION,
    flush_max_ms          DOUBLE PRECISION,

    notes                 TEXT
);

CREATE INDEX IF NOT EXISTS vacuum_metrics_captured_at_idx
    ON vacuum_metrics (captured_at DESC);
