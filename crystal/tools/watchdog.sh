#!/usr/bin/env bash
# watchdog.sh — Stage 0 self-alarm for PAXTON / CRYSTAL (§1.5, §20).
# Adapted from daedalus (underworks/tools/watchdog.sh, Appendix A).
#
#   Polls the ntfy topic every POLL_SEC (default 180s).
#   If the newest PAXTON beat (excluding alarms and pre-boot channel tests)
#   is older than SILENCE_MIN (default 16 minutes per §1.5 & §20) ->
#   posts Priority: urgent, Title: PAXTON SILENT,
#   body: "no beat for <N> min; last id <id>; expected seq <n>"
#
#   Supports ONCE=1 for deterministic single-shot verification and
#   SILENCE_SEC for sub-minute kill-test verification without manufacturing
#   an artificial 16-minute HB-GAP in the live ledger.
set -uo pipefail

R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$R"
if [ -z "${NTFY_TOPIC:-}" ]; then
  [ -r /home/user/.private/paxton.env ] && set -a && . /home/user/.private/paxton.env && set +a
fi
: "${NTFY_SERVER:=https://ntfy.sh}"

SILENCE_MIN="${SILENCE_MIN:-16}"
SILENCE_SEC="${SILENCE_SEC:-$((SILENCE_MIN * 60))}"
POLL_SEC="${POLL_SEC:-180}"
ONCE="${ONCE:-0}"
LOG="${WATCHDOG_LOG:-evidence/WATCHDOG.log}"
STATE_LAST="${WATCHDOG_STATE:-evidence/.watchdog_last_alarm}"
COOLDOWN_SEC="${COOLDOWN_SEC:-1800}"
mkdir -p evidence

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$LOG"; }
log "watchdog start pid=$$ silence_min=${SILENCE_MIN}m (${SILENCE_SEC}s) poll=${POLL_SEC}s"

last_alarm=0
[ -s "$STATE_LAST" ] && last_alarm=$(cat "$STATE_LAST" 2>/dev/null || echo 0)

# Beats are messages whose title starts with "PAXTON" and neither contains "SILENT"
# nor is the pre-boot "channel test".
BEAT_FILTER='
  [ .[]
    | select(.event == "message")
    | select((.title // "") | startswith("PAXTON"))
    | select(((.title // "") | contains("SILENT")) | not)
    | select(((.title // "") | contains("channel test")) | not)
  ]
  | sort_by(.time)
'

while true; do
  snap=$(curl -sS --max-time 15 \
           "${NTFY_SERVER}/${NTFY_TOPIC}/json?poll=1&since=all&scheduled=0" 2>/dev/null \
         | jq -c 'del(.topic)' 2>/dev/null | jq -s -c '.' 2>/dev/null)
  case "$snap" in ''|'null') snap="[]" ;; esac

  newest=$(printf '%s' "$snap" | jq -c "$BEAT_FILTER | (max_by(.time).time // 0)" 2>/dev/null)
  last_id=$(printf '%s' "$snap" | jq -c -r "$BEAT_FILTER | (max_by(.time).id // \"none\")" 2>/dev/null)
  beats=$(printf '%s' "$snap" | jq -c "$BEAT_FILTER | length" 2>/dev/null)
  case "$newest" in ''|*[!0-9]*) newest=0 ;; esac

  now=$(date -u +%s)

  if [ "$newest" = "0" ]; then
    log "poll: no beat visible (beats=${beats:-0}) — treating as silent"
    age_sec=$((SILENCE_SEC + 1))
    age_min=$((SILENCE_MIN + 1))
  else
    age_sec=$(( now - newest ))
    age_min=$(( age_sec / 60 ))
    log "poll: newest beat ${age_min}m (${age_sec}s) old (id=${last_id}, beats=${beats})"
  fi

  exp_seq=$(( $( [ -s evidence/HEARTBEATS.jsonl ] && tail -1 evidence/HEARTBEATS.jsonl | jq -r '.seq // -1' || echo -1) + 1 ))

  if [ "$age_sec" -ge "$SILENCE_SEC" ]; then
    if [ "$now" -gt $(( last_alarm + COOLDOWN_SEC )) ]; then
      log "ALARM: no beat for ${age_min}m (${age_sec}s >= ${SILENCE_SEC}s) last_beat_id=${last_id} expected_seq=${exp_seq}"
      ALARM_OUT=$(curl -sS --max-time 10 \
        -H "Title: PAXTON SILENT" -H "Priority: urgent" \
        -H "Tags: rotating_light,skull" \
        -d "no beat for ${age_min} min (${age_sec}s); last id ${last_id}; expected seq ${exp_seq}" \
        "${NTFY_SERVER}/${NTFY_TOPIC}" 2>/dev/null | jq -c 'del(.topic)' 2>/dev/null || true)
      ALARM_ID=$(printf '%s' "$ALARM_OUT" | jq -r '.id // "unknown"' 2>/dev/null || echo "unknown")
      echo "$now" > "$STATE_LAST"
      last_alarm=$now
      log "alarm posted id=${ALARM_ID}"
    else
      log "STILL SILENT ${age_min}m (${age_sec}s) — alarm suppressed (cooldown ${COOLDOWN_SEC}s)"
    fi
  fi

  [ "$ONCE" = "1" ] && break
  sleep "$POLL_SEC"
done
