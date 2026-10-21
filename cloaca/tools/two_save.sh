#!/usr/bin/env bash
# G1 two-save determinism: build+save -> open+re-save -> open+dump twice -> census hashes must agree.
set -uo pipefail
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; C="${1:?chunk id}"
mkdir -p "$LANE/build"
cat > /tmp/resave.py <<'PY'
import bpy, sys, os
chunk = sys.argv[sys.argv.index("--")+1]
lane  = sys.argv[sys.argv.index("--")+2]
p = os.path.join(lane,"chunks",f"{chunk}.blend")
bpy.ops.wm.open_mainfile(filepath=p)
bpy.ops.wm.save_as_mainfile(filepath=p)
print("RESAVED", p, os.path.getsize(p))
PY
BL_LOG="$LANE/build/resave_$C.log" bash "$LANE/tools/bl.sh" --python /tmp/resave.py -- "$C" "$LANE" || { echo "RESAVE FAILED"; exit 1; }
for t in a b; do
  BL_LOG="$LANE/build/dump_${C}_$t.log" bash "$LANE/tools/bl.sh" --python "$LANE/tools/dump_chunk.py" -- "$C" \
    > "$LANE/build/c${C}_$t.txt" 2>&1 || { echo "DUMP $t FAILED"; tail -5 "$LANE/build/dump_${C}_$t.log"; exit 1; }
done
HA=$(grep -c '^CENSUS_SHA256 ' "$LANE/build/c${C}_a.txt" || true)
HB=$(grep -c '^CENSUS_SHA256 ' "$LANE/build/c${C}_b.txt" || true)
if [ "$HA" != "1" ] || [ "$HB" != "1" ]; then
  echo "REFUSED: dump did not produce exactly one CENSUS_SHA256 line (a=$HA b=$HB). No pass is claimed from an empty diff (D-004)."
  exit 1
fi
if [ ! -s "$LANE/build/c${C}_a.txt" ]; then echo "REFUSED: empty dump"; exit 1; fi
if diff -q "$LANE/build/c${C}_a.txt" "$LANE/build/c${C}_b.txt" >/dev/null; then
  echo "CHUNK CENSUS MATCH ($C)"; grep '^CENSUS_SHA256' "$LANE/build/c${C}_a.txt"
  python3 -c 'import json,sys
a=json.load(open(sys.argv[1])) if 0 else None' "$LANE/build/c${C}_a.txt" 2>/dev/null || true
else echo "CENSUS MISMATCH ($C)"; diff "$LANE/build/c${C}_a.txt" "$LANE/build/c${C}_b.txt" | head -20; exit 1; fi
