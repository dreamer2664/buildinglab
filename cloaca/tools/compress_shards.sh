#!/bin/bash
# The brick ledger master is the gzipped shard (committed); the plain shard is a working copy.
# R3: only pushes survive - a plain-only shard is a ledger that exists on one disk. This loop
# gzips every settled plain shard, verifies the gzip decompresses to the same sha256, then removes
# the plain copy. The chunk the pipeline is writing right now is never touched.
cd "$(dirname "$0")/.." || exit 1
while true; do
  next=$(python3 -c "
import json
try: print(json.load(open('evidence/PIPELINE_STATE.json'))['next'])
except Exception: print(0)")
  limit=$((next-3))
  for f in ledgers/BRICKS/*.jsonl; do
    [ -e "$f" ] || continue
    c=$(basename "$f" .jsonl); i=$((10#${c#S}))
    [ "$c" = "S0042" ] && continue   # the reproduction chunk keeps its tracked plain ledger in git
    [ "$i" -le "$limit" ] || continue
    gz="$f.gz"
    if [ -e "$gz" ] && [ "$gz" -nt "$f" ]; then continue; fi
    gzip -c "$f" > "$gz.tmp" 2>/dev/null || { rm -f "$gz.tmp"; continue; }
    a=$(sha256sum "$f" | cut -d' ' -f1)
    b=$(zcat "$gz.tmp" 2>/dev/null | sha256sum | cut -d' ' -f1)
    if [ "$a" = "$b" ]; then mv "$gz.tmp" "$gz"; rm -f "$f"; echo "compressed $c"; else rm -f "$gz.tmp"; echo "VERIFY FAIL $c"; fi
  done
  python3 tools/mark_pruned.py >/dev/null 2>&1
  sleep 45
done
