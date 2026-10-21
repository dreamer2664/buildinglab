#!/usr/bin/env bash
# Continuous 7-minute beat. Context (stage/line/next) is read from evidence/BEAT_CTX.json
# so the numbers always describe what the run is actually doing. Degrades to 21 min on 429 (§1.5).
set -uo pipefail
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; EV="$LANE/evidence"
CAD=${BEAT_CADENCE_S:-420}; FAILS=0
while true; do
  STAGE=$(python3 -c 'import json;print(json.load(open("'"$EV"'/BEAT_CTX.json")).get("stage","0"))' 2>/dev/null || echo 0)
  LINE=$(python3 -c 'import json;print(json.load(open("'"$EV"'/BEAT_CTX.json")).get("line","none"))' 2>/dev/null || echo none)
  NEXT=$(python3 -c 'import json;print(json.load(open("'"$EV"'/BEAT_CTX.json")).get("next",""))' 2>/dev/null || echo "")
  PCT=$(python3 -c 'import json;print(json.load(open("'"$EV"'/STATE.json")).get("pct",0))' 2>/dev/null || echo 0)
  if bash "$LANE/tools/beat.sh" "$STAGE" "$LINE" "$PCT" "$NEXT" routine; then FAILS=0; else FAILS=$((FAILS+1)); fi
  # board beat every 15 min (2 of every ~3 ntfy beats is wrong cadence; use a counter on minutes)
  N=$(( $(grep -c . "$EV/HEARTBEATS.jsonl" 2>/dev/null || echo 0) ))
  if [ $((N % 2)) -eq 0 ]; then
    ( cd /home/user/work/chatcode && timeout 120 python3 bin/chatcode tasks heartbeat t-20261021-8511 --hours 10 \
        --note "resume point: $(cat "$EV/BEAT_CTX.json" 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin).get("next",""))' 2>/dev/null)" >/dev/null 2>&1 ) || true
  fi
  if [ $((N % 17)) -eq 0 ]; then ( cd "$LANE" && python3 tools/hb_reconcile.py >> "$EV/RECONCILE.log" 2>&1 ) || true; fi
  if [ $FAILS -ge 3 ]; then CAD=1260; echo "$(date -u +%FT%TZ) HB-QUOTA/3-fails -> degraded to 21 min" >> "$EV/HEARTBEAT_ERRORS.log"; fi
  sleep $CAD
done
