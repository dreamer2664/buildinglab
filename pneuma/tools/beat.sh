#!/usr/bin/env bash
# tools/beat.sh — the heartbeat. One lawful beat per 7 minutes of wall clock.
#
#   bash tools/beat.sh "H" "shot-07" 52 "frame 5184/10800 · grain rate check"
#   bash tools/beat.sh "I" "-" 100 "release r01 verified" high release
#   HERON_BEAT_DRYRUN=1 bash tools/beat.sh "0" "-" 3 "stage 0 bootstrap"   # no network
#
# Contract (§1.5, §32):
#   * the payload is built from files, never from what the agent believes
#   * frames_rendered may not exceed ledgers/FRAMES.jsonl — a beat that lies is a
#     false beat, and a false beat ends the commission
#   * a beat that cannot be proven delivered is not a beat: exit 1, mirror it
#   * 429 => HB-QUOTA, degrade to a 21-minute cadence, keep going (never silent)
#   * no secret is ever echoed, and `set -x` is never used in this file
#
# Exit: 0 delivered (or lawfully degraded) · 1 not delivered (never counted as a beat)

set -u
LANE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EV="$LANE_ROOT/evidence"
HB="$EV/HEARTBEATS.jsonl"
DRY="${HERON_BEAT_DRYRUN:-0}"

STAGE="${1:?stage letter required}"; SHOT="${2:- -}"; PCT="${3:?pct required}"; NEXT="${4:-}"
PRIORITY="${5:-low}"; EXTRA_TAGS="${6:-}"

[ -d "$EV" ] || { echo "beat: no evidence/ dir at $EV" >&2; exit 1; }
[ -f "$HB" ] || : > "$HB"

# ---- counting, done in python: `grep -c` exits 1 on a zero count and would
#      silently append a second "0" to the arithmetic (a bug this file had, and
#      which the first test run caught) -----------------------------------------
count() {  # count <jsonl-file> <jq-style predicate on a dict>
  python3 - "$HB" "$1" <<'PY' 2>/dev/null || echo 0
import json, sys
path, key = sys.argv[1], sys.argv[2]
n = 0
try:
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                if json.loads(line).get(key) is True:
                    n += 1
            except json.JSONDecodeError:
                continue
except FileNotFoundError:
    pass
print(n)
PY
}

# ---- seq: delivered beats only, counted from the ledger, never invented --------
SEQ=$(( $(count delivered) + 1 ))

# ---- the payload is read from the repo, not remembered -------------------------
COMMIT="$(git -C "$LANE_ROOT" rev-parse --short HEAD 2>/dev/null || echo "")"
[ -n "$COMMIT" ] && COMMIT="${COMMIT:0:7}"
BLEND=""
if [ -f "$LANE_ROOT/machines/PNEUMA.blend" ]; then
  BLEND="$(sha256sum "$LANE_ROOT/machines/PNEUMA.blend" | cut -c1-12)"
fi
FRAMES=0
[ -f "$LANE_ROOT/ledgers/FRAMES.jsonl" ] && FRAMES=$(grep -c . "$LANE_ROOT/ledgers/FRAMES.jsonl" 2>/dev/null || true)
[ -z "${FRAMES:-}" ] && FRAMES=0
TRAJ_OK="$(count reproduced)"
DEFECTS=0
if [ -f "$EV/DEFECTS.jsonl" ]; then
  DEFECTS=$(python3 - "$EV/DEFECTS.jsonl" <<'PY' 2>/dev/null || echo 0
import json, sys
n = 0
try:
    for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
        line = line.strip()
        if line and json.loads(line).get("status") == "open":
            n += 1
except (FileNotFoundError, json.JSONDecodeError):
    pass
print(n)
PY
)
fi
[ -z "${DEFECTS:-}" ] && DEFECTS=0
[ "$SHOT" = "-" ] && SHOT_TITLE="" || SHOT_TITLE=" · shot-$SHOT"
T="$(date -u +%FT%TZ)"

BODY="$(printf '{"seq":%s,"ev":"beat","t":"%s","stage":"%s","shot":"%s","pct":%s,"commit":"%s","blend":"%s","frames_rendered":%s,"traj_hashes_ok":%s,"defects_open":%s,"next":"%s"}' \
  "$SEQ" "$T" "$STAGE" "$SHOT" "$PCT" "$COMMIT" "$BLEND" "$FRAMES" "$TRAJ_OK" "$DEFECTS" "$NEXT")"
TITLE="HERON ${STAGE}${SHOT_TITLE} · ${PCT}%"
TAGS="heartbeat,stage-${STAGE}${EXTRA_TAGS:+,$EXTRA_TAGS}"

if [ "$DRY" = "1" ]; then
  printf '{"ev":"beat","delivered":false,"dry_run":true,"seq":%s,"t":"%s","stage":"%s","shot":"%s","pct":%s,"frames_rendered":%s,"traj_hashes_ok":%s,"defects_open":%s,"next":"%s"}\n' \
    "$SEQ" "$T" "$STAGE" "$SHOT" "$PCT" "$FRAMES" "$TRAJ_OK" "$DEFECTS" "$NEXT" >> "$HB"
  printf 'beat: DRY-RUN seq=%s title=%q priority=%s\n' "$SEQ" "$TITLE" "$PRIORITY"
  printf 'beat: body=%s\n' "$BODY"
  printf 'beat: NOT POSTED — set HERON_BEAT_DRYRUN=0 to post.\n'
  exit 0
fi

# ---- post ---------------------------------------------------------------------
set -a; . /home/user/.private/heron.env; set +a
RESP="$(curl -sS --max-time 25 -w '\n%{http_code}' \
  -H "Title: $TITLE" -H "Priority: $PRIORITY" -H "Tags: $TAGS" \
  -d "$BODY" "$NTFY_SERVER/$NTFY_TOPIC" 2>&1)"
CODE="$(printf '%s' "$RESP" | tail -1)"
JSON="$(printf '%s' "$RESP" | sed '$d')"
NTFY_ID="$(printf '%s' "$JSON" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("id",""))
except Exception: print("")' 2>/dev/null)"

if [ "$CODE" = "200" ]; then
  printf '{"ev":"beat","delivered":true,"seq":%s,"t":"%s","stage":"%s","shot":"%s","pct":%s,"frames_rendered":%s,"traj_hashes_ok":%s,"defects_open":%s,"next":"%s","ntfy_id":"%s"}\n' \
    "$SEQ" "$T" "$STAGE" "$SHOT" "$PCT" "$FRAMES" "$TRAJ_OK" "$DEFECTS" "$NEXT" "$NTFY_ID" >> "$HB"
  printf 'beat: delivered seq=%s ntfy_id=%s\n' "$SEQ" "$NTFY_ID"
  exit 0
fi

if [ "$CODE" = "429" ]; then
  # quota law: degrade to 21-minute cadence, log HB-QUOTA, mirror to board+ledger
  printf '{"ev":"beat","delivered":false,"hb_quota":true,"seq":%s,"t":"%s","stage":"%s","shot":"%s","pct":%s,"next":"%s"}\n' \
    "$SEQ" "$T" "$STAGE" "$SHOT" "$PCT" "$NEXT" >> "$HB"
  printf 'beat: HB-QUOTA (429) — degraded to 21-minute cadence, seq=%s mirrored locally\n' "$SEQ" >&2
  exit 0
fi

# anything else: not delivered, not counted, never backfilled
printf '{"ev":"beat","delivered":false,"seq":%s,"t":"%s","stage":"%s","http":"%s"}\n' \
  "$SEQ" "$T" "$STAGE" "$CODE" >> "$HB"
printf 'beat: NOT DELIVERED (http %s) — this is not a heartbeat; mirror to board\n' "$CODE" >&2
exit 1
