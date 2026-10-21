#!/usr/bin/env bash
# hb_daemon.sh — Background heartbeat + board lease renewal + reconciler for PAXTON (§1.5, §32).
# Adapted from daedalus (underworks/tools/hb_daemon.sh, Appendix A).
#
#   Every 7 min (420 s)  : write expected tick + post ntfy beat
#   Every 15 min (900 s) : board heartbeat on chatcode + agency pulse
#   Every 2 h (7200 s)   : run python3 tools/hb_reconcile.py
set -uo pipefail

R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$R"
[ -r /home/user/.private/paxton.env ] && set -a && . /home/user/.private/paxton.env && set +a
export CHATCODE_AGENT=paxton
export AGENCY_AGENT=paxton

TASK_ID="${TASK_ID:-t-20261021-3620}"
CHATCODE_DIR="${CHATCODE_DIR:-/home/user/chatcode}"
AGENCY_DIR="${AGENCY_DIR:-/home/user/agency}"
BEAT_SEC="${BEAT_SEC:-420}"
LEDGER="evidence/HEARTBEATS.jsonl"
EXPECTED="evidence/expected_ticks.jsonl"
LOG="evidence/HEARTBEAT_DAEMON.log"
mkdir -p evidence

tick=0
log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$LOG"; }
log "hb_daemon start pid=$$ beat=${BEAT_SEC}s task=${TASK_ID}"

last_lease=$(date -u +%s)
last_recon=$(date -u +%s)

while true; do
  sleep "$BEAT_SEC"
  now=$(date -u +%s)

  tick=$((tick + 1))
  next_seq=$(( $( [ -s "$LEDGER" ] && tail -1 "$LEDGER" | jq -r '.seq // -1' || echo -1) + 1 ))
  printf '{"seq":%d,"t":"%s","pid":%d}\n' "$next_seq" "$(date -u +%FT%TZ)" "$$" >> "$EXPECTED"

  out=$(bash tools/beat.sh --state 2>&1)
  rc=$?
  log "beat seq~$next_seq rc=$rc $out"
  if [ "$rc" -eq 6 ]; then
    log "HB-QUOTA detected: degrading cadence to 21m (1260s) per §1.5"
    BEAT_SEC=1260
  fi

  # Board heartbeat every 15 min (900 s) per §1.5
  if [ $(( now - last_lease )) -ge 900 ]; then
    stage=$(jq -r '.stage // "0"' evidence/STATE.json 2>/dev/null || echo "0")
    zone=$(jq -r '.zone // "-"' evidence/STATE.json 2>/dev/null || echo "-")
    pct=$(jq -r '.pct // 0' evidence/STATE.json 2>/dev/null || echo 0)
    nxt=$(jq -r '.next // ""' evidence/STATE.json 2>/dev/null | cut -c1-60)
    commit=$(git rev-parse --short=7 HEAD 2>/dev/null || echo nogit)
    note="stage ${stage} (${zone}) ${pct}% @${commit}; next: ${nxt}"
    ( cd "$CHATCODE_DIR" && python3 bin/chatcode tasks heartbeat "$TASK_ID" --hours 10 --note "$note" ) >>"$LOG" 2>&1 || true
    ( cd "$AGENCY_DIR" && python3 bin/agency heartbeat --note "$note" ) >>"$LOG" 2>&1 || true
    last_lease=$now
    log "board heartbeat renewed"
  fi

  # Reconcile every 2 h (7200 s) per §1.5
  if [ $(( now - last_recon )) -ge 7200 ]; then
    python3 tools/hb_reconcile.py >>"$LOG" 2>&1 || true
    last_recon=$now
    log "reconciled"
  fi
done
