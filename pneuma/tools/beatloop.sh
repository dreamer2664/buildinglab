#!/usr/bin/env bash
# tools/beatloop.sh — the agent's voice, running continuously (order NO-STOP-001 §4).
#
#   * ntfy beat every 7 minutes (§1.5)
#   * board lease heartbeat every 15 minutes (§1.5)
#   * reconcile every 2 hours
#   * the beat payload comes from evidence/STATE.json, never from memory, so the
#     beat can never claim a stage the run is not in
#
# A quota 429 backs off to 21 minutes and logs HB-QUOTA; degrading is lawful,
# going silent is not.
#
# This process is the agent. The watchdog is a SEPARATE process watching the
# topic, so that if this loop dies the alarm still fires (F33).

set -u
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE="$LANE/evidence/STATE.json"
LOG="$LANE/evidence/BEATLOOP.log"
BEAT_EVERY=420      # 7 minutes
BOARD_EVERY=900     # 15 minutes
RECONCILE_EVERY=7200  # 2 hours
CHATCODE="/home/user/chatcode"

last_board=0
last_reconcile=0

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$LOG"; }

beat() {
  local stage shot pct next prio
  stage=$(python3 -c "import json;print(json.load(open('$STATE')).get('stage','0'))" 2>/dev/null || echo 0)
  shot=$(python3 -c "import json;print(json.load(open('$STATE')).get('shot','-'))" 2>/dev/null || echo -)
  pct=$(python3 -c "import json;print(json.load(open('$STATE')).get('pct',0))" 2>/dev/null || echo 0)
  next=$(python3 -c "import json;print(json.load(open('$STATE')).get('next',''))" 2>/dev/null || echo "")
  prio=$(python3 -c "import json;print(json.load(open('$STATE')).get('priority','low'))" 2>/dev/null || echo low)

  if bash "$LANE/tools/beat.sh" "$stage" "$shot" "$pct" "$next" "$prio"; then
    log "beat ok stage=$stage pct=$pct"
  else
    log "beat FAILED stage=$stage pct=$pct — mirrored to ledger, not counted as a beat"
  fi
}

board() {
  local id note
  id=$(python3 -c "import json;print(json.load(open('$STATE')).get('card',''))" 2>/dev/null || echo "")
  note=$(python3 -c "import json;print(json.load(open('$STATE')).get('next','running'))" 2>/dev/null || echo running)
  [ -z "$id" ] && { log "board: no card id in STATE.json — skipping lease renewal"; return 0; }
  if [ -d "$CHATCODE" ]; then
    ( cd "$CHATCODE" && set -a; . /home/user/.private/heron.env; set +a; export CHATCODE_AGENT=heron
      python3 bin/chatcode tasks heartbeat "$id" --note "$note" --hours 10 >> "$LOG" 2>&1 ) \
      && log "board lease renewed card=$id" || log "board lease renewal FAILED card=$id"
  fi
}

log "beatloop started pid=$$ beat=${BEAT_EVERY}s board=${BOARD_EVERY}s reconcile=${RECONCILE_EVERY}s"

while true; do
  now=$(date +%s)
  beat
  if [ $((now - last_board)) -ge "$BOARD_EVERY" ]; then board; last_board=$now; fi
  if [ $((now - last_reconcile)) -ge "$RECONCILE_EVERY" ]; then
    python3 "$LANE/tools/hb_reconcile.py" >> "$LOG" 2>&1
    last_reconcile=$now
    log "reconcile ran"
  fi
  sleep "$BEAT_EVERY"
done
