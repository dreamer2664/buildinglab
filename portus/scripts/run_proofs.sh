#!/usr/bin/env bash
# One Blender process per view. A single process rendering all 24 at 1024 px
# exceeds the worker's 1.9 GiB (observed OOM kill at 1.27 GB RSS); loading the
# blend per view costs ~2 s and buys a clean heap for every frame.
#
#   bash portus/scripts/run_proofs.sh [res] [samples]
set -u
RES="${1:-1024}"
SAMPLES="${2:-32}"
cd "$(dirname "$0")/../.." || exit 1
LOG="portus/renders/proofs_run.log"
: > "$LOG"
for cam in $(ls portus/renders/proofs/*.png 2>/dev/null | sed 's#.*/##; s#\.png$##' | cut -c1-2; \
             seq -w 1 24 | cut -c1-2); do :; done
# enumerate camera prefixes from the blend itself, once
PREFIXES=$(/home/user/tools/blender45/blender -b portus/source/PORTUS.blend --python-expr \
  "import bpy;print('CAMS='+','.join(sorted(o.name.split('_')[1] for o in bpy.data.objects if o.type=='CAMERA')))" \
  2>/dev/null | grep '^CAMS=' | cut -d= -f2 | tr ',' ' ')
for p in $PREFIXES; do
  echo "=== view $p ===" | tee -a "$LOG"
  /home/user/tools/blender45/blender -b portus/source/PORTUS.blend --python-exit-code 1 \
    --python portus/scripts/render.py -- --class proofs --res "$RES" --samples "$SAMPLES" --only "${p}_" \
    2>&1 | grep -E "RENDERED|CACHED|FAILED|SUMMARY" | tee -a "$LOG"
done
echo "=== PASS COMPLETE ===" | tee -a "$LOG"
grep -c "RENDERED\|CACHED" "$LOG"
