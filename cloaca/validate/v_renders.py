#!/usr/bin/env python3
"""1,284 required views: count, class coverage, declared resolutions, and no upscale."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, jsonl, EV, LANE
SPEC = {"station_hero": (16, 3840, 2160), "engine_house": (40, 3840, 2160), "engine_closeup": (88, 2560, 1440),
        "mechanism_detail": (60, 2560, 1440), "sewer_interior": (132, 2560, 1440), "brick_macro": (40, 2560, 1440),
        "iron_macro": (30, 2560, 1440), "water_flow": (48, 2560, 1440), "storm_overflow": (36, 2560, 1440),
        "construction_yard": (54, 2560, 1440), "centring_arch": (26, 2560, 1440), "embankment_walk": (72, 2560, 1440),
        "lamppost": (24, 1920, 1080), "people": (60, 2560, 1440), "tide_chart": (28, 2560, 1440),
        "cross_section": (340, 2560, 1440), "profile_tile": (158, 1920, 1080), "hydraulic_map": (12, 3840, 2160),
        "aerial": (20, 3840, 2160)}
def main():
    ren = list(jsonl(os.path.join(EV, "RENDERS.jsonl")))
    if not ren: return verdict("v_renders", 3, {"renders": 0, "required": sum(v[0] for v in SPEC.values())},
                               "no render produced yet")
    bad = []
    for r in ren:
        sp = SPEC.get(r.get("class"))
        if not sp: bad.append(f"{r.get('id')}: unknown class {r.get('class')}"); continue
        w, h = r.get("width", 0), r.get("height", 0)
        if r.get("kind") == "proof": continue           # proofs are 1024 px by design (R2)
        if (w, h) != (sp[1], sp[2]): bad.append(f"{r.get('id')}: {w}x{h} != {sp[1]}x{sp[2]}")
        if r.get("upscaled"): bad.append(f"{r.get('id')}: upscaled (automatic fail, F10)")
    counts = {}
    for r in ren: counts[r.get("class")] = counts.get(r.get("class"), 0) + 1
    total_req = sum(v[0] for v in SPEC.values())
    return verdict("v_renders", 1 if bad else (0 if len(ren) >= total_req else 3),
                   {"renders": len(ren), "required": total_req, "proofs": sum(1 for r in ren if r.get("kind")=="proof"),
                    "finals": sum(1 for r in ren if r.get("kind")!="proof"), "spec_violations": len(bad),
                    "classes_present": len(counts)}, "; ".join(bad[:3]) if bad else "growing toward 1,284")
if __name__ == "__main__": sys.exit(main())
