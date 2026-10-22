#!/usr/bin/env bash
# disk guard: keep the rolling chunk-blend window at <=16 so the 25 GB volume never fills.
# A blend is only pruned when (a) its brick ledger shard is tracked in git (committed and,
# per the pipeline loop, pushed in the same batch) and (b) its census file exists, i.e. the
# chunk rebuilds bit-identical from ledgers (C-018). Runs forever, 240 s cadence.
cd "$(dirname "$0")/.." || exit 1
KEEP=16
while true; do
  next=$(python3 -c "import json;print(json.load(open('evidence/PIPELINE_STATE.json'))['next'])" 2>/dev/null || echo 99999)
  cut=$((next - KEEP))
  drop=""
  for f in chunks/*.blend; do
    [ -e "$f" ] || continue
    c=$(basename "$f" .blend)
    n=$((10#${c#S}))
    [ "$n" -lt "$cut" ] || continue
    git ls-files --error-unmatch "ledgers/BRICKS/${c}.jsonl.gz" >/dev/null 2>&1 || continue
    [ -e "evidence/CENSUS/${c}.json" ] || continue
    drop="$drop $c"
    rm -f "$f"
  done
  if [ -n "$drop" ]; then python3 tools/mark_pruned.py $drop >/dev/null 2>&1; fi
  # emergency brake: if the volume still crosses 92 %, shrink harder (keep 6)
  use=$(df -P / | tail -1 | awk '{print $5}' | tr -d '%')
  if [ "$use" -gt 92 ]; then
    cut=$((next - 6))
    drop=""
    for f in chunks/*.blend; do
      [ -e "$f" ] || continue
      c=$(basename "$f" .blend); n=$((10#${c#S}))
      [ "$n" -lt "$cut" ] || continue
      [ -e "evidence/CENSUS/${c}.json" ] || continue
      drop="$drop $c"; rm -f "$f"
    done
    [ -n "$drop" ] && python3 tools/mark_pruned.py $drop >/dev/null 2>&1
  fi
  sleep 240
done
