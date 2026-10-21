#!/usr/bin/env bash
# Polls my own topic. 16 minutes without a beat from me -> one urgent BAZALGETTE SILENT.
# An untested watchdog is a lying watchdog (F33): see evidence/NEGATIVE_TESTS.md WD-1.
set -uo pipefail
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; EV="$LANE/evidence"
LIMIT_MIN="${WATCHDOG_LIMIT_MIN:-16}"; POLL_S="${WATCHDOG_POLL_S:-60}"
[ -s /home/user/.private/bazalgette.env ] && { set -a; . /home/user/.private/bazalgette.env; set +a; }
: "${NTFY_TOPIC:?}"; NTFY_SERVER="${NTFY_SERVER:-https://ntfy.sh}"
LOG="$EV/WATCHDOG.log"; FIRED="$EV/.watchdog_fired"
echo "$(date -u +%FT%TZ) watchdog armed limit=${LIMIT_MIN}m poll=${POLL_S}s" >> "$LOG"
while true; do
  NOW=$(date +%s)
  LAST=$(printf 'url = "%s/%s/json?poll=1&since=%s"\n' "$NTFY_SERVER" "$NTFY_TOPIC" "$((NOW-7200))" \
        | curl -sS -K - 2>/dev/null \
        | python3 -c 'import json,sys
m=[json.loads(l) for l in sys.stdin if l.strip()]
hb=[x for x in m if x.get("event")=="message" and "heartbeat" in (x.get("tags") or [])]
print(hb[-1]["time"] if hb else 0)' 2>/dev/null || echo 0)
  [ -z "$LAST" ] && LAST=0
  GAP=$(( (NOW - LAST) / 60 ))
  echo "$(date -u +%FT%TZ) last_beat_age=${GAP}m" >> "$LOG"
  if [ "$GAP" -ge "$LIMIT_MIN" ]; then
    if [ ! -f "$FIRED" ] || [ $(( NOW - $(stat -c %Y "$FIRED" 2>/dev/null || echo 0) )) -ge 1800 ]; then
      WRESP=$(printf 'url = "%s/%s"\nheader = "Title: BAZALGETTE SILENT"\nheader = "Priority: 5"\nheader = "Tags: watchdog,silent"\ndata = "{\\"ev\\":\\"silent\\",\\"last_seq\\":%s,\\"gap_min\\":%s,\\"t\\":\\"%s\\"}"\n' \
        "$NTFY_SERVER" "$NTFY_TOPIC" "$(grep -c . "$EV/HEARTBEATS.jsonl" 2>/dev/null || echo 0)" "$GAP" "$(date -u +%FT%TZ)" \
        | curl -sS -K - 2>/dev/null)
      WID=$(printf '%s' "$WRESP" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("id",""))
except Exception: print("")' 2>/dev/null)
      touch "$FIRED"
      echo "$(date -u +%FT%TZ) FIRED urgent SILENT gap=${GAP}m id=${WID:-none}" >> "$LOG"
    fi
  else
    rm -f "$FIRED"
  fi
  sleep "$POLL_S"
done
