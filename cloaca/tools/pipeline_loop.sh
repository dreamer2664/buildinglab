#!/bin/bash
# Network pipeline: lay the ledger, build the chunk, measure the census, record, publish in
# batches. Resumable from evidence/PIPELINE_STATE.json. Chunk binaries are reproducible from
# ledger + seed (G13), so only a rolling window stays on disk; the ledgers are the master.
cd "$(dirname "$0")/.." || exit 1
STATE=evidence/PIPELINE_STATE.json
LOG=evidence/PIPELINE.jsonl
WINDOW=40
BATCH=25
mkdir -p build chunks ledgers/BRICKS evidence/CENSUS
next=$(python3 -c "
import json,os
try: print(json.load(open('$STATE'))['next'])
except Exception: print(11)")
done_count=0; batch_a=$next
while [ "$next" -lt 1320 ]; do
  c=$(printf 'S%04d' "$next")
  if [ -f "evidence/CENSUS/$c.json" ] && grep -q "\"chunk\": \"$c\".*\"state\": \"built\"" ledgers/INDEX.jsonl; then
    next=$((next+1)); python3 -c "import json;json.dump({'next':$next},open('$STATE','w'))"; continue
  fi
  t0=$(date +%s)
  python3 tools/generator/bricks.py "$c" > "build/lay_$c.log" 2>&1
  lay_rc=$?
  BL_LOG="build/${c}_build.log" bash tools/bl.sh --python tools/build_chunk.py -- --chunk "$c" --save --out "$PWD/chunks/$c.blend" >/dev/null 2>&1
  b_rc=$?
  python3 tools/index_update.py "$c" >/dev/null 2>&1
  i_rc=$?
  t1=$(date +%s)
  python3 - "$c" "$lay_rc" "$b_rc" "$i_rc" "$((t1-t0))" <<'PY'
import json, sys, datetime, os
c, lay, b, i, dt = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
cen = {}
try: cen = json.load(open(f"evidence/CENSUS/{c}.json"))
except Exception: pass
row = {"t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "chunk": c,
       "lay_rc": lay, "build_rc": b, "index_rc": i, "wall_s": dt,
       "census": cen.get("brick_objects"), "u_hash_match": cen.get("u_hash_match"),
       "peak_mb": cen.get("peak_mb"), "build_s": cen.get("build_s"),
       "ok": lay == 0 and b == 0 and i == 0 and cen.get("u_hash_match") is True}
with open("evidence/PIPELINE.jsonl", "a") as f: f.write(json.dumps(row, sort_keys=True) + "\n")
print(f"{c} ok={row['ok']} census={row['census']} {dt}s")
PY
  p=$((next - WINDOW))
  if [ "$p" -ge 0 ]; then
    pc=$(printf 'S%04d' "$p")
    if [ -f "chunks/$pc.blend" ] && [ -f "evidence/CENSUS/$pc.json" ] && grep -q "\"chunk\": \"$pc\".*\"state\": \"built\"" ledgers/INDEX.jsonl; then
      rm -f "chunks/$pc.blend" "chunks/$pc.blend1"
      python3 tools/mark_pruned.py "$pc" >/dev/null 2>&1
    fi
  fi
  next=$((next+1)); done_count=$((done_count+1))
  python3 -c "import json;json.dump({'next':$next,'updated':'$(date -u +%FT%TZ)'},open('$STATE','w'))"
  if [ $((done_count % BATCH)) -eq 0 ]; then
    cd /home/user/work/buildinglab || exit 1
    for attempt in 1 2 3; do
      git add -A cloaca/ledgers cloaca/evidence 2>/dev/null
      if git -c user.name=bazalgette -c user.email=bazalgette@agents.buildinglab.local commit -q \
        -m "cloaca pipeline: chunks $batch_a..$((next-1)) laid, built, census recorded, binaries pruned to window" 2>/dev/null; then
        set -a; . /home/user/.private/bazalgette.env; set +a
        git push -q origin agent/bazalgette/t-20261021-8511 2>/dev/null
        break
      fi
      sleep 2
    done
    cd cloaca || exit 1
    batch_a=$next
  fi
done
echo "pipeline complete at $(date -u +%FT%TZ)" >> evidence/PIPELINE.jsonl
