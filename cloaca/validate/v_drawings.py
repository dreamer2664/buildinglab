#!/usr/bin/env python3
"""340 sections + 158 tiles + 12 maps. Stage subject: returns PENDING (3) with the count of what exists, never a false PASS."""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, LANE, jload
PATTERNS = {"v_stations": ["stations/*.blend"], "v_parts": ["engines/*.blend"],
            "v_kinematics": ["engines/*.blend"], "v_cycle": ["engines/*.blend", "evidence/PV/*.json"],
            "v_people": ["ledgers/PEOPLE.jsonl"], "v_drawings": ["drawings/*.json"]}["v_drawings"]
TARGET = {"v_stations": 4, "v_parts": 22, "v_kinematics": 22, "v_cycle": 22,
          "v_people": 120, "v_drawings": 510}["v_drawings"]
def main():
    found = []
    for pat in PATTERNS:
        found += glob.glob(os.path.join(LANE, pat))
    n = len(found)
    if n == 0:
        return verdict("v_drawings", 3, {"subject_files": 0, "target": TARGET},
                       "no subject in the lane yet - Stage H")
    return verdict("v_drawings", 1, {"subject_files": n, "target": TARGET}, "subject present but not yet inspected to the gate")
if __name__ == "__main__": sys.exit(main())
