#!/bin/bash
# Resume-safe proof render loop: one Blender session per view, register upserts by id, commit in
# batches. Skips anything already in the register, so a dead sandbox resumes where it stopped.
# Memory doctrine (§SANDBOX): while the chunk pipeline is building, SKIP_CHUNK keeps a second
# heavy Blender out of RAM; an OOM kill costs a 45 s backoff instead of a hot retry.
cd "$(dirname "$0")/.." || exit 1
while true; do
  if pgrep -f "build_chun[k]" >/dev/null 2>&1; then export SKIP_CHUNK=1; else unset SKIP_CHUNK; fi
  ITEM=$(python3 tools/pick_render.py)
  if [ -z "$ITEM" ]; then
    if [ "$SKIP_CHUNK" = "1" ]; then
      # chunk scenes remain but the pipeline holds the memory budget; wait it out
      sleep 30; continue
    fi
    echo "schedule complete at $(date -u +%FT%TZ)"; break
  fi
  SCENE=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['scene'])" "$ITEM")
  ID=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['id'])" "$ITEM")
  case "$SCENE" in
    chunk:*) BLEND="chunks/$(echo "$SCENE" | cut -d: -f2).blend"
             if [ ! -f "$BLEND" ]; then
               # C-018: pruned chunks rebuild from ledger + seed on demand; the render proves the
               # reproduction path as it goes
               BL_LOG="build/rebuild_$ID.log" bash tools/bl.sh --python tools/build_chunk.py -- --chunk "$(echo "$SCENE" | cut -d: -f2)" --save --out "$PWD/$BLEND" >/dev/null 2>&1 || { echo "REBUILD FAIL $ID"; continue; }
             fi;;
    *) BLEND="$SCENE";;
  esac
  BL_LOG="build/render_$ID.log" bash tools/bl.sh "$BLEND" --python tools/render_batch.py -- --item "$ITEM" > /dev/null 2>&1
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "RENDER FAIL $ID rc=$RC"
    if [ $RC -eq 137 ] || grep -q "Killed" "build/render_$ID.log" 2>/dev/null; then
      echo "OOM backoff 45s after $ID"
      sleep 45
    fi
    continue
  fi
  N=$((N+1))
  if [ $((N % 60)) -eq 0 ]; then
    cd /home/user/work/buildinglab || exit 1
    for a in 1 2 3; do
      git add -A cloaca/evidence/RENDERS.jsonl cloaca/renders 2>/dev/null
      git -c user.name=bazalgette -c user.email=bazalgette@agents.buildinglab.local commit -q -m "cloaca renders: proof batch to $ID" 2>/dev/null && { git push -q origin agent/bazalgette/t-20261021-8511 2>/dev/null; break; }
      sleep 2
    done
    cd cloaca || exit 1
  fi
done
