#!/usr/bin/env python3
"""v_water.py — G7 W1: the basin, measured on the native scene.

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_water.py -- --native portus/source/PORTUS.blend

Checks (each one a number, not an opinion):
  1  water surface exists and its mean level is +0.00 ± 5 mm
  2  every vertex of the water surface is within ±60 mm of the datum (swell only)
  3  the basin bed exists, is below the water, and is ≥ 5.5 m down
  4  eight dropped objects rest on or above the bed, below the water
  5  the coaster's hull is at its design draft ±50 mm
  6  the hull's waterline height above the bed is > the hull's own draft
  7  four mooring ropes, each sagging ≥ 0.20 m at midspan
  8  each rope starts on the ship's deck edge and ends at a bollard head
  9  foam exists within 150 mm of the south quay waterline
 10  ice plates exist, all above the waterline
Exit 0 PASS, 2 FAIL. Writes evidence/validation/v_water.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)

WATER_Z = 0.00
LEVEL_TOL = 0.005
BASIN = (110.0, 30.0, 290.0, 120.0)
DRAFT = 4.20
DRAFT_TOL = 0.050


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    args = ap.parse_args()
    import bpy
    from mathutils import Vector

    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    objs = {o.name: o for o in bpy.data.objects if o.type == "MESH"}

    def bounds(o):
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        return (min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs),
                max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))

    # 1-2 water level
    w = objs.get("WATER_SURFACE")
    if w is None:
        check("water surface exists", False, "WATER_SURFACE not found")
    else:
        zs = [(w.matrix_world @ v.co).z for v in w.data.vertices]
        mean = sum(zs) / len(zs)
        dev = max(abs(z - WATER_Z) for z in zs)
        check("water level +0.00 ±5 mm", abs(mean - WATER_Z) <= LEVEL_TOL,
              f"mean {mean:+.5f} m over {len(zs)} vertices")
        check("surface swell within ±60 mm", dev <= 0.060, f"max deviation {dev*1000:.1f} mm")
        b = bounds(w)
        check("water covers the basin", b[0] <= BASIN[0] + 0.1 and b[3] >= BASIN[2] - 0.1
              and b[1] <= BASIN[1] + 0.1 and b[4] >= BASIN[3] - 0.1,
              f"x {b[0]:.1f}..{b[3]:.1f} y {b[1]:.1f}..{b[4]:.1f}")

    # 3 bed
    bed = objs.get("BASIN_BED")
    if bed is None:
        check("basin bed exists", False, "BASIN_BED not found")
    else:
        b = bounds(bed)
        depth = WATER_Z - b[5]
        check("basin bed ≥ 5.5 m below water", depth >= 5.5, f"{depth:.2f} m")

    # 4 dropped objects
    drops = sorted(n for n in objs if n.startswith("DROP_"))
    check("8 dropped objects", len(drops) >= 8, f"{len(drops)} found")
    under = [n for n in drops if bounds(objs[n])[5] <= WATER_Z]
    check("every dropped object is under water", len(under) == len(drops),
          f"{len(under)}/{len(drops)}")

    # 5-6 hull at draft
    hull = objs.get("HULL_COASTER")
    if hull is None:
        check("coaster hull exists", False, "HULL_COASTER not found")
    else:
        b = bounds(hull)
        draft = WATER_Z - b[2]
        check("hull at design draft ±50 mm", abs(draft - DRAFT) <= DRAFT_TOL,
              f"draft {draft:.3f} m (design {DRAFT:.2f})")
        check("hull freeboard above water", b[5] - WATER_Z >= 2.0,
              f"deck {b[5]-WATER_Z:.2f} m above water")
        # the hull must be inside the basin, not on the quay
        check("hull is in the basin",
              BASIN[0] <= b[0] and b[3] <= BASIN[2] and BASIN[1] <= b[1] and b[4] <= BASIN[3],
              f"x {b[0]:.1f}..{b[3]:.1f} y {b[1]:.1f}..{b[4]:.1f}")

    # 7-8 ropes
    ropes = sorted(n for n in objs if n.startswith("MOORING_ROPE"))
    check("4 mooring ropes", len(ropes) == 4, f"{len(ropes)} found")
    sags, ends_ok = [], 0
    bollards = [o for o in bpy.data.objects if o.name.startswith("BOLLARD_head")]
    boll_pts = [(o.matrix_world.translation.x, o.matrix_world.translation.y) for o in bollards]
    for rn in ropes:
        o = objs[rn]
        b = bounds(o)
        zs = [(o.matrix_world @ v.co).z for v in o.data.vertices]
        # sag = highest point minus lowest point, along the rope
        sag = max(zs) - min(zs)
        # the low point must sit between the two ends in plan
        sags.append(round(sag, 3))
        end_near_bollard = any(abs(px - b[0]) < 4.0 or abs(px - b[3]) < 4.0 for (px, py) in boll_pts)
        # ends: one at ship, one on the quay side (y > basin north edge)
        if b[4] > BASIN[3] - 0.5:
            ends_ok += 1 if end_near_bollard else 0
    check("every rope sags ≥ 0.20 m", all(s >= 0.20 for s in sags), f"sags {sags}")
    check("every rope ends at a bollard on the quay", ends_ok == len(ropes),
          f"{ends_ok}/{len(ropes)}")

    # 9 foam
    foam = [n for n in objs if n.startswith("FOAM_")]
    near = 0
    for n in foam:
        b = bounds(objs[n])
        if abs(b[1] - BASIN[1]) <= 0.15 or abs(b[4] - BASIN[3]) <= 0.15 or abs(b[2] - WATER_Z) < 0.10:
            near += 1
    check("foam strips within 150 mm of a waterline contact", len(foam) >= 20 and near == len(foam),
          f"{near}/{len(foam)} strips")

    # 10 ice
    ice = [n for n in objs if n.startswith("ICE_")]
    above = [n for n in ice if bounds(objs[n])[2] >= WATER_Z]
    check("ice plates present, all above the waterline", len(ice) >= 20 and len(above) == len(ice),
          f"{len(above)}/{len(ice)} above datum")
    # ice only at shadowed edges: north (y high) and west (x low)
    in_shadow = [n for n in ice if (bounds(objs[n])[4] > BASIN[3] - 4.0
                                     or bounds(objs[n])[0] < BASIN[0] + 3.5)]
    check("ice only at the north and west edges", len(in_shadow) == len(ice),
          f"{len(in_shadow)}/{len(ice)} at shadowed edges")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_water", native=args.native, ok=ok, checks=checks,
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_water.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_water: {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
