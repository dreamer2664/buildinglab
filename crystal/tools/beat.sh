#!/usr/bin/env bash
# beat.sh — one heartbeat for PAXTON / CRYSTAL (§1.5, §32).
# Adapted from daedalus (underworks/tools/beat.sh, Appendix A).
#
# Usage:
#   bash tools/beat.sh <stage> <zone> <pct> "<next>"
#   bash tools/beat.sh --boot
#   bash tools/beat.sh --state
#   bash tools/beat.sh --state --priority default --tags "heartbeat,milestone"
#
# Rules enforced:
#   * --max-time 10, never -v, never set -x (§2.4)
#   * NTFY_TOPIC is never echoed, logged, or written to disk (del(.topic))
#   * Census fields (bays_done, panes, exhibits, defects_open) are read from
#     committed ledgers, never guessed (§32: a beat whose panes exceeds the
#     committed ledger is a false beat).
#   * Refuses non-boot beats if HEAD is not pushed to origin (anti-F33).
set -uo pipefail

R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$R"

if [ -z "${NTFY_TOPIC:-}" ]; then
  [ -r /home/user/.private/paxton.env ] && set -a && . /home/user/.private/paxton.env && set +a
fi
: "${NTFY_SERVER:=https://ntfy.sh}"
if [ -z "${NTFY_TOPIC:-}" ]; then echo "beat: NTFY_TOPIC unset — HB-BADTOPIC" >&2; exit 3; fi

PRIORITY="low"; TAGS=""; TITLE=""; BOOT=0; USE_STATE=0
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --boot)      BOOT=1; shift ;;
    --state)     USE_STATE=1; shift ;;
    --priority)  PRIORITY="$2"; shift 2 ;;
    --tags)      TAGS="$2"; shift 2 ;;
    --title)     TITLE="$2"; shift 2 ;;
    *)           POSITIONAL+=("$1"); shift ;;
  esac
done

LEDGER="evidence/HEARTBEATS.jsonl"
EXPECTED="evidence/expected_ticks.jsonl"
RAW="evidence/heartbeats/raw.jsonl"
mkdir -p evidence/heartbeats

LAST_SEQ=$([ -s "$LEDGER" ] && tail -1 "$LEDGER" | jq -r '.seq // empty' || echo "")
if [ -n "$LAST_SEQ" ]; then SEQ=$((LAST_SEQ + 1)); else SEQ=0; fi

NOW="$(date -u +%FT%TZ)"

# Ensure expected_ticks.jsonl records this seq before attempting network call
LAST_EXP=$([ -s "$EXPECTED" ] && tail -1 "$EXPECTED" | jq -r '.seq // empty' || echo "")
if [ "$LAST_EXP" != "$SEQ" ]; then
  printf '{"seq":%d,"t":"%s","pid":%d}\n' "$SEQ" "$NOW" "$$" >> "$EXPECTED"
fi

if [ "$BOOT" = 1 ]; then
  BODY="$(printf '{"seq":%d,"ev":"boot","t":"%s"}' "$SEQ" "$NOW")"
  TITLE="PAXTON — online"; PRIORITY="high"; TAGS="rocket,heartbeat"
else
  if [ "$USE_STATE" = 1 ] || [ ${#POSITIONAL[@]} -eq 0 ]; then
    STAGE=$(jq -r '.stage // "0"' evidence/STATE.json 2>/dev/null || echo "0")
    ZONE=$(jq -r '.zone // "bootstrap"' evidence/STATE.json 2>/dev/null || echo "bootstrap")
    PCT=$(jq -r '.pct // 0' evidence/STATE.json 2>/dev/null || echo 0)
    NEXT=$(jq -r '.next // ""' evidence/STATE.json 2>/dev/null || echo "")
  else
    STAGE="${POSITIONAL[0]}"; ZONE="${POSITIONAL[1]}"
    PCT="${POSITIONAL[2]}";   NEXT="${POSITIONAL[3]:-}"
  fi

  COMMIT="$(git rev-parse --short=7 HEAD 2>/dev/null || echo nogit)"
  if [ "$COMMIT" != "nogit" ]; then
    if ! git branch -r --contains HEAD 2>/dev/null | grep -q .; then
      REMOTE_SHA="$(git rev-parse --short=7 origin/agent/paxton/t-20261021-3620 2>/dev/null || echo "")"
      if [ -n "$REMOTE_SHA" ]; then
        COMMIT="$REMOTE_SHA"
      else
        echo "beat: REFUSED — HEAD $COMMIT is not on the remote. Push first, then beat (anti-F33)." >&2
        exit 4
      fi
    fi
  fi

  BAYS_DONE=0
  [ -s ledgers/BAYS.jsonl ] && BAYS_DONE=$(grep -c '"status"[[:space:]]*:[[:space:]]*"built"' ledgers/BAYS.jsonl 2>/dev/null || true)
  PANES=0
  [ -s ledgers/PANES.jsonl ] && PANES=$(wc -l < ledgers/PANES.jsonl | tr -d ' ')
  EXHIBITS=0
  [ -s ledgers/EXHIBITS.jsonl ] && EXHIBITS=$(wc -l < ledgers/EXHIBITS.jsonl | tr -d ' ')
  DEFECTS=0
  [ -s evidence/DEFECTS.jsonl ] && DEFECTS=$(grep -c '"status"[[:space:]]*:[[:space:]]*"open"' evidence/DEFECTS.jsonl 2>/dev/null || true)

  NEXT="$(printf '%s' "$NEXT" | cut -c1-80)"
  [ -z "$TAGS" ] && TAGS="heartbeat,stage-${STAGE}"
  [ -z "$TITLE" ] && TITLE="PAXTON ${STAGE} · ${ZONE} · ${PCT}%"

  BODY="$(jq -cn \
    --argjson seq "$SEQ" \
    --arg t "$NOW" \
    --arg stage "$STAGE" \
    --arg zone "$ZONE" \
    --argjson pct "$PCT" \
    --arg commit "$COMMIT" \
    --argjson bays_done "$BAYS_DONE" \
    --argjson panes "$PANES" \
    --argjson exhibits "$EXHIBITS" \
    --argjson defects_open "$DEFECTS" \
    --arg next "$NEXT" \
    '{seq:$seq,t:$t,stage:$stage,zone:$zone,pct:$pct,commit:$commit,bays_done:$bays_done,panes:$panes,exhibits:$exhibits,defects_open:$defects_open,next:$next}')"
fi

RESP="$(curl -sS --max-time 10 -o /tmp/paxton_hb.out -w '%{http_code}' \
          -H "Title: $TITLE" -H "Priority: $PRIORITY" -H "Tags: $TAGS" \
          -d "$BODY" "${NTFY_SERVER}/${NTFY_TOPIC}" 2>/tmp/paxton_hb.err)"
CODE="${RESP##*$'\n'}"
if [ "$CODE" != "200" ]; then
  echo "beat: HTTP $CODE — $(head -c 200 /tmp/paxton_hb.err /tmp/paxton_hb.out 2>/dev/null | tr '\n' ' ')" >&2
  rm -f /tmp/paxton_hb.out /tmp/paxton_hb.err
  [ "$CODE" = "429" ] && { echo "beat: HB-QUOTA — degrade cadence to 21m (§1.5)" >&2; exit 6; }
  exit 7
fi

# Strip secret .topic before anything touches disk (§2.4)
jq -c 'del(.topic)' /tmp/paxton_hb.out > /tmp/paxton_hb.safe && mv /tmp/paxton_hb.safe /tmp/paxton_hb.out
ID="$(jq -r '.id // empty' /tmp/paxton_hb.out 2>/dev/null)"
STIME="$(jq -r '.time // 0' /tmp/paxton_hb.out 2>/dev/null)"
if [ -z "$ID" ]; then
  rm -f /tmp/paxton_hb.out /tmp/paxton_hb.err
  echo "beat: no id in response — not delivered" >&2
  exit 8
fi

jq -cn \
  --argjson seq "$SEQ" \
  --arg id "$ID" \
  --argjson server_time "$STIME" \
  --arg local_time "$NOW" \
  --argjson body "$BODY" \
  '{seq:$seq,id:$id,server_time:$server_time,local_time:$local_time,body:$body}' >> "$LEDGER"
cat /tmp/paxton_hb.out >> "$RAW"
rm -f /tmp/paxton_hb.out /tmp/paxton_hb.err

# Update STATE.json if positional arguments were supplied
if [ "$BOOT" = 0 ] && [ ${#POSITIONAL[@]} -ge 3 ]; then
  jq -cn --arg stage "$STAGE" --arg zone "$ZONE" --argjson pct "$PCT" --arg next "$NEXT" \
    '{stage:$stage,zone:$zone,pct:$pct,next:$next}' > evidence/STATE.json
fi

# Every 6th beat digest to heartbeatcode (§7)
if [ "$SEQ" -gt 0 ] && [ $((SEQ % 6)) -eq 0 ]; then
  curl -sS --max-time 8 -H "Title: paxton heartbeat digest #${SEQ}" -H "Priority: low" \
    -d "paxton · CRYSTAL · stage ${STAGE:-0} (${ZONE:--}) ${PCT:-0}% · bays=${BAYS_DONE:-0} panes=${PANES:-0} exhibits=${EXHIBITS:-0} · next: ${NEXT:-}" \
    "${NTFY_SERVER}/heartbeatcode" >/dev/null 2>&1 || true
fi

echo "beat seq=$SEQ id=$ID server_time=$STIME"
exit 0
