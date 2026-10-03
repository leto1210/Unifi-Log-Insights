#!/bin/bash
# Host-side collector loop for core-syno (DSM). Run with `bash loop.sh`
# (/tmp is noexec). See README.md § "24 h baseline collection".
#
# Every call is wrapped in `timeout`: a `docker exec` that straddles a
# container restart otherwise hangs forever (12 h silent gap on 2026-09-19).
D=/usr/local/bin/docker
C=unifi-log-insight
DIR=/tmp/vacuum_perf
NOTES=${NOTES:-baseline}

while true; do
  timeout 30 $D exec $C test -f /tmp/vacuum_metrics.py \
    || timeout 30 $D cp $DIR/vacuum_metrics.py $C:/tmp/vacuum_metrics.py
  # Receiver logs go to container stdout, unreachable from inside the
  # container: pipe `docker logs` into the collector's stdin, and let
  # `--flush-log-cmd cat` read it (subprocess inherits stdin).
  timeout 60 $D logs --since 6m $C 2>&1 \
    | timeout 60 $D exec -i $C \
        python /tmp/vacuum_metrics.py --once --notes "$NOTES" --flush-log-cmd cat \
    >> $DIR/collector.log 2>&1
  sleep 300
done
