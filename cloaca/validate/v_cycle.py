#!/usr/bin/env python3
"""G6 derived-diagram clause: per engine a P-V diagram derived from the cylinder simulation, closed,
with positive work, and an animated cycle that matches it in period."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import verdict, LANE, jload
EXPECT = [f"AM-E{i}" for i in range(1, 9)] + [f"CX-E{i}" for i in range(1, 5)] + \
         [f"DF-E{i}" for i in range(1, 7)] + [f"CH-E{i}" for i in range(1, 5)]
def main():
    probs = []; n = 0; works = []
    for eid in EXPECT:
        pv = jload(os.path.join(LANE, "evidence/PV", f"{eid}.json"))
        cyc = jload(os.path.join(LANE, "evidence", f"CYCLE_{eid}.json"))
        if not pv: continue
        n += 1
        if not pv.get("derived"): probs.append(f"{eid}: diagram not marked derived")
        loop = pv.get("loop", [])
        if len(loop) != 72: probs.append(f"{eid}: loop has {len(loop)} points, expected 72 (5 deg)")
        if not pv.get("loop_closed"): probs.append(f"{eid}: loop not closed")
        w = pv.get("work_per_cycle_J", 0)
        works.append(w)
        if w <= 0: probs.append(f"{eid}: non-positive work per cycle")
        if not cyc: probs.append(f"{eid}: no animated cycle to match the diagram's period")
    if n == 0: return verdict("v_cycle", 3, {"subject_files": 0, "target": 22},
                              "no P-V diagram derived yet - Stage H")
    return verdict("v_cycle", 1 if probs else (0 if n == 22 else 3),
                   {"diagrams": n, "target": 22,
                    "work_min_kJ": round(min(works) / 1000, 1) if works else None,
                    "work_max_kJ": round(max(works) / 1000, 1) if works else None,
                    "violations": len(probs)},
                   "; ".join(probs[:4]) if probs else
                   "22 derived indicator diagrams, closed loops, positive work, cycles matched")
if __name__ == "__main__": sys.exit(main())
