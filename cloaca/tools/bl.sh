#!/usr/bin/env bash
# Every headless blender call goes through here: --python-exit-code 1 AND an independent
# traceback guard (F21, re-verified in this lane), while stdout still reaches the caller (D-004).
set -uo pipefail
LOG="${BL_LOG:-/tmp/bl.log}"
blender --background --factory-startup --python-exit-code 1 "$@" 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
if grep -q "^Traceback (most recent call last):" "$LOG"; then
  echo "bl.sh: python exception inside the blender session (blender reported rc=$RC)" >&2
  exit 1
fi
if [ -z "$(grep -v '^Blender\|^Read\|^$' "$LOG")" ] && [ "${BL_ALLOW_EMPTY:-0}" != "1" ]; then
  echo "bl.sh: the script produced no output at all - refusing to call that a pass (D-004)" >&2
  exit 1
fi
exit $RC
