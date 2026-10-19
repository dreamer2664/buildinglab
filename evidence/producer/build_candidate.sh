#!/usr/bin/env bash
# Full reproducible candidate build; no credentials forwarded to Blender.
set -euo pipefail
cd "$(dirname "$0")/../.."
B="${BLENDER:-blender}"
LOG="$HOME/.cache/buildinglab-build-logs"; mkdir -p "$LOG"
run_blender() { local label="$1"; shift; echo "BUILD_STEP $label"; env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 OMP_NUM_THREADS=4 "$B" -t 4 --python-exit-code 1 "$@" > "$LOG/$label.log" 2>&1; }
run_blender shell -b --python assets/exterior/build_shell.py
run_blender shell-check -b scene/shell.blend --python tools/validate_shell.py
run_blender interiors -b scene/shell.blend --python assets/interiors/build_interiors.py
run_blender interiors-check -b scene/interiors.blend --python tools/validate_interiors.py
run_blender clearances -b scene/interiors.blend --python assets/interiors/audit_clearances.py
run_blender batch -b scene/interiors.blend --python evidence/producer/batch_meshes.py
run_blender assembly -b "$HOME/.cache/buildinglab-batch-stage.blend" --python evidence/producer/assemble.py
run_blender native-check -b scene/building-final.blend --python tools/validate_scene.py
run_blender export-reimport -b scene/building-final.blend --python tools/test_export.py
python3 evidence/producer/make_schedules.py
echo 'CANDIDATE_BUILT: mechanical only; images, producer inspections, publication and independent acceptance separate.'
