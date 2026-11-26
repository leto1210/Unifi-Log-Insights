# Logs table partitioning

Since the partitioning release, the `logs` table can be split into one partition per UTC day. Retention then removes a whole expired day with `DROP TABLE` instead of deleting it row by row. That leaves no dead rows for autovacuum to grind through, and queries over a time range only read the days they need.

- **New installs** are partitioned from the start. There is nothing to do.
- **Existing installs** keep their plain `logs` table, and keep working exactly as before, until you run the migration below. It never runs on its own.

## How the partitioned table is laid out

| Table | Holds |
|---|---|
| `logs` | Parent table. Queries and inserts use it exactly as before. |
| `logs_pYYYYMMDD` | One UTC day each, created a week ahead by the receiver (hourly job). |
| `logs_default` | Rows whose timestamp has no day partition (a device clock far off). Moved into the right partition when that day's partition is created. |
| `logs_legacy` | Migrated installs only: your former table, holding everything before the cutover date. Dropped automatically once all of it is past retention. |

## Migrating an existing install

**Before you start:**

- Make sure you have a recent backup.
- The app must be on a release that contains the partitioning code.
- You need PostgreSQL 12 or later (the embedded database is 16).

### 1. Look at the plan

```bash
docker exec unifi-log-insight python -m db.migrate_partitions --dry-run
```

Nothing is changed. The plan shows:

- the **cutover** date: the first UTC midnight at least 48 h away;
- the indexes the new table will carry;
- the indexes it will leave on `logs_legacy` only (the primary key, invalid leftovers, indexes already scheduled for removal);
- the size of the extra `id` index to build.

### 2. Run it

```bash
docker exec unifi-log-insight python -m db.migrate_partitions --yes
```

Run it when nobody is opening 7-day or 30-day dashboards, because the swap needs a moment with no long query on `logs`. The command goes through five phases:

| Phase | What it does | Blocks ingestion? |
|---|---|---|
| 1. cutover | Picks and stores the cutover date | No |
| 2. twin index | `CREATE INDEX CONCURRENTLY idx_logs_id_legacy ON logs (id)` (minutes on a large table) | No |
| 3. bound | Adds `CHECK (timestamp < cutover)` and validates it (one full read of the table) | No |
| 4. swap | One short transaction: new partitioned `logs`, the old table attached as `logs_legacy`, `logs_default`, the first day partitions | Briefly: a fraction of a second on a small table, several seconds on a very large one (see the example below); retried up to 10 times if a long query holds the table |
| 5. analyze | `ANALYZE logs` | No |

The command can be interrupted and re-run: it resumes where it stopped. Until the cutover date, new rows still go into `logs_legacy`; after it, they go into the day partitions.

On a large table the run lasts well over half an hour. To keep it going if your terminal or SSH session drops, start it detached and follow its output:

```bash
docker exec -d unifi-log-insight sh -c "python -m db.migrate_partitions --yes > /tmp/migrate_partitions.log 2>&1; echo EXIT=\$? >> /tmp/migrate_partitions.log"
docker exec unifi-log-insight cat /tmp/migrate_partitions.log
```

A container restart stops it. Run the same command again and it resumes.

#### Example: a 109 million row install

This is a real run, on PostgreSQL 16 on a separate host with 30 GB of RAM. The `logs` table held about 109 million rows (~100 GB with its 16 indexes), and logs kept arriving at roughly 100,000 rows per hour throughout.

| Phase | Time |
|---|---|
| 1. cutover | instant (cutover set about 50 h ahead) |
| 2. twin index (~2.5 GiB) | 21 min 39 s |
| 3. bound (full read of the table) | 9 min 53 s |
| 4. swap | 13.2 s, on the first attempt |
| 5. analyze | 3 min 12 s |
| **Total** | **about 35 minutes** |

What it meant for ingestion:

- No rows were rejected and no insert failed.
- Phases 2 and 3 load the disk. A few batch writes took up to 5 s, against well under 1 s normally.
- During the swap, inserts waited for the lock. One batch write took 12.5 s, and the rows received that minute fell to about half the usual count. Syslog is UDP, so some messages sent during those seconds were probably lost.

Scale your own estimate from your row count (shown by `--dry-run`): phases 2, 3 and 5 grow roughly with the table size.

### 3. Afterwards

- The receiver log shows `Partition logs_pYYYYMMDD created` once a day.
- Retention logs `partitions_dropped`.
- `logs_legacy` disappears by itself once all of it is past your retention, about *retention + 3 days* after the migration.

## Undoing it

### Before the swap: `--abort`

If phases 2–3 ran but the swap did not (the command failed or you stopped it), this removes the twin index, the bound and the stored cutover:

```bash
docker exec unifi-log-insight python -m db.migrate_partitions --abort
```

You don't strictly have to run it. A failed run removes the bound itself, and the receiver also removes a forgotten one when its cutover is less than a day away. Without that, every row from the cutover date onwards would be rejected.

### After the swap: back to a plain table

This only works while `logs_legacy` still exists, which is roughly the first *retention* days after the migration. Once retention has dropped it, there is no plain table left to go back to, and the partitioned table is the supported layout.

**Important:** releases older than the partitioning release cannot start on a partitioned `logs`. Their schema migration fails with `cannot specify storage parameters for a partitioned table`. Roll back **before** downgrading the app, never after.

#### 1. See how much there is to copy back

Rows that arrived after the cutover live in the day partitions and `logs_default`, and are copied back into the old table. Before the cutover date there are none, and the rollback is instant.

Connect to the database. Embedded database:

```bash
docker exec -it unifi-log-insight psql -h 127.0.0.1 -U unifi -d unifi_logs
```

For an external database, use your usual `psql` connection. Then count the rows:

```sql
SELECT count(*) FROM logs WHERE tableoid <> 'logs_legacy'::regclass;
```

The rollback holds a lock on `logs` while it copies those rows.

- **Up to a few hundred thousand rows:** this takes seconds. The app keeps running; its inserts wait for the lock, then resume on the plain table.
- **Millions of rows:** this can take minutes. Inserts that wait more than 30 s fail, and syslog messages received meanwhile are lost (UDP). With an external database, stop the app container first (`docker compose stop`) and start it again afterwards.

#### 2. Run the rollback

Paste this as one block. It is a single transaction: if anything fails, nothing changes.

<!-- rollback-sql -->
```sql
BEGIN;
SET LOCAL lock_timeout = '10s';

-- 1. Take the former table out of the partitioned one (its data and indexes stay).
ALTER TABLE logs DETACH PARTITION logs_legacy;

-- 2. Remove the migration's bound: rows from after the cutover go back in.
DO $$ DECLARE r record; BEGIN
  FOR r IN SELECT conname FROM pg_constraint
           WHERE conrelid = 'public.logs_legacy'::regclass
             AND conname LIKE 'logs\_legacy\_before\_%' LOOP
    EXECUTE format('ALTER TABLE logs_legacy DROP CONSTRAINT %I', r.conname);
  END LOOP;
END $$;

-- 3. Copy back what arrived since the cutover (day partitions + logs_default).
INSERT INTO logs_legacy SELECT * FROM logs;

-- 4. Hand the id sequence back, then drop the partitioned table.
ALTER SEQUENCE logs_id_seq OWNED BY logs_legacy.id;
DROP TABLE logs;
ALTER TABLE logs_legacy RENAME TO logs;

-- 5. Restore the original index names; the migration's extra id index is not
--    needed on a plain table (its primary key covers id).
DROP INDEX IF EXISTS idx_logs_id_legacy;
DO $$ DECLARE r record; BEGIN
  FOR r IN SELECT c.relname FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
           WHERE i.indrelid = 'public.logs'::regclass AND c.relname LIKE '%\_legacy' LOOP
    EXECUTE format('ALTER INDEX %I RENAME TO %I', r.relname, left(r.relname, -7));
  END LOOP;
END $$;

COMMIT;
```

If it stops with `canceling statement due to lock timeout`, a long query was holding `logs`. Nothing changed: run it again.

#### 3. Check and restart

```sql
SELECT relkind FROM pg_class WHERE relname = 'logs';   -- 'r' = plain table again
SELECT count(*) FROM logs;
```

If you stopped the app, start it again. The current release works on the plain table as before. Retention goes back to deleting row by row, and the migration can be run again later.

## Troubleshooting

| Message | Meaning | What to do |
|---|---|---|
| `Refused: N row(s) are timestamped at/after the cutover` | A device clock was far ahead, so some rows are dated in the future. | Run the `DELETE` printed in the message, then re-run the migration. |
| `could not get the lock on logs after 10 attempts` | Long queries (wide dashboard ranges, exports) kept holding the table. | Re-run when the dashboard is idle. The earlier phases are not redone. |
| `parent index(es) match no index of logs_legacy, so ATTACH would rebuild them under lock` | A safety check stopped the swap before it could lock ingestion for minutes. Nothing changed. | Open an issue with the `--dry-run` output. |
| `Dropped logs_legacy_before_YYYYMMDD: an interrupted partition migration left it armed` | The receiver removed a leftover bound before it could block inserts. | Re-run the migration; it picks a new cutover. |
| Boot: `'logs' is partitioned but index 'idx_logs_id' is missing` | The table was converted outside the command. | Re-run `python -m db.migrate_partitions --yes`, or roll back. |
