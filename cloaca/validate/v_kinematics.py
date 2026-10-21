#!/usr/bin/env python3
"""G6 motion clauses: full animated cycle per engine, 14 strokes/min +/-0.5, flywheel angular
velocity within +/-2 % sampled every 5 degrees. Reads what the animation session recorded:
CYCLE_<id>.json (frames, fps, measured strokes/min, measured beam stroke, keyed object count) and
FLYWHEEL_<id>.json (72 omega samples at 5 degrees, measured deviation)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import verdict, LANE, jload
EXPECT = [f"AM-E{i}" for i in range(1, 9)] + [f"CX-E{i}" for i in range(1, 5)] + \
         [f"DF-E{i}" for i in range(1, 7)] + [f"CH-E{i}" for i in range(1, 5)]
def main():
    probs = []; n = 0; devs = []; spm = []
    for eid in EXPECT:
        cyc = jload(os.path.join(LANE, "evidence", f"CYCLE_{eid}.json"))
        fw = jload(os.path.join(LANE, "evidence", f"FLYWHEEL_{eid}.json"))
        if not cyc or not fw: continue
        n += 1
        if cyc.get("frames", 0) < cyc.get("fps", 24) * cyc.get("cycle_s", 0) - 1:
            probs.append(f"{eid}: frame range shorter than one cycle")
        s = cyc.get("strokes_per_min_measured", 0)
        spm.append(s)
        if not (13.5 <= s <= 14.5): probs.append(f"{eid}: {s} strokes/min outside 14 +/-0.5")
        if abs(cyc.get("beam_stroke_m_measured", 0) - 3.05) > 0.02:
            probs.append(f"{eid}: beam stroke {cyc.get('beam_stroke_m_measured')} m != 3.05 m")
        if cyc.get("keyed_objects", 0) < 18:
            probs.append(f"{eid}: only {cyc.get('keyed_objects')} objects carry the cycle")
        if fw.get("sample_step_deg") != 5 or len(fw.get("samples", [])) != 72:
            probs.append(f"{eid}: flywheel not sampled every 5 deg over the revolution")
        if not fw.get("within_2pct"): probs.append(f"{eid}: flywheel deviation outside +/-2 %")
        devs.append(fw.get("max_deviation_pct", 99))
    if n == 0: return verdict("v_kinematics", 3, {"subject_files": 0, "target": 22},
                              "no animated cycle recorded yet - Stage H")
    return verdict("v_kinematics", 1 if probs else (0 if n == 22 else 3),
                   {"engines_animated": n, "target": 22,
                    "strokes_per_min_min": round(min(spm), 4) if spm else None,
                    "strokes_per_min_max": round(max(spm), 4) if spm else None,
                    "flywheel_dev_max_pct": round(max(devs), 4) if devs else None,
                    "violations": len(probs)},
                   "; ".join(probs[:4]) if probs else
                   "22 engines complete a full keyed cycle; speed and ripple measured, not declared")
if __name__ == "__main__": sys.exit(main())
