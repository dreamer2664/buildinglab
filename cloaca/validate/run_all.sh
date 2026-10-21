#!/usr/bin/env bash
# §1.1 command 6: fail fast. PENDING (3) is not a failure; it is an honest absence of subject.
set -uo pipefail
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0; PENDING=0; PASSED=0
for v in "$LANE"/validate/v_*.py; do
  python3 "$v"; rc=$?
  case $rc in
    0) PASSED=$((PASSED+1));;
    3) PENDING=$((PENDING+1));;
    *) FAILED=$((FAILED+1)); echo "  ^ FAIL from $(basename "$v")";;
  esac
done
echo "battery: $PASSED passed · $PENDING pending · $FAILED failed"
[ $FAILED -eq 0 ] || exit 1
