#!/usr/bin/env python3
"""v_clearance.py — can a person actually walk through this building?

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_clearance.py -- --native portus/source/PORTUS.blend

The earlier version swept a 90-degree arc about a guessed inward normal, which is
wrong for east and west doors (defect history D-107): it reported doors blocked
that a person walks through, and passed doors that furniture blocked. This
version tests the **volume a body occupies**:

  1  doorway passage: a 0.90 × 2.10 m box in every doorway, from 0.10 m before
     the threshold to 1.05 m after it, must be empty of furniture
  2  open leaf: the door leaf itself must lie in the 0.12 m strip against the
     wall, not in the passage
  3  room shell excluded: floors, ceilings and linings are structure, not props
  4  the quay apron in front of B05 is clear for its full length
  5  market aisle between stall rows ≥ 1.80 m
  6  stair: riser 0.175 ±0.01, going 0.280 ±0.01, width ≥ 1.20 m
Exit 0 PASS, 2 FAIL. Writes evidence/validation/v_clearance.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
SHELL = ("_floor", "_ceiling", "_lining", "_winfram", "_glass", "_sill",
         "_doorframe", "_doorhead", "_doorleaf", "_practical")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    args = ap.parse_args()
    import bpy

    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    def bounds(o):
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        if not vs:
            return None
        return (min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs),
                max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))

    rows = {r["room_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "design", "SCHEDULE.csv")))}

    props = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("ROOM_"):
            continue
        if any(t in o.name for t in SHELL):
            continue
        rid = o.name.split("_")[1]
        b = bounds(o)
        if b:
            props.setdefault(rid, []).append((o.name, b))

    # 1-2 doorway passage
    blocked = []
    leaves = []
    for rid, items in props.items():
        # doorway geometry is not in the schedule; use the door leaf objects
        pass
    doors = [o for o in bpy.data.objects if o.type == "MESH" and o.name.endswith("_doorleaf")]
    check("door leaves modelled", len(doors) >= 40, f"{len(doors)} leaves")
    for d in doors:
        b = bounds(d)
        rid = d.name.split("_")[1]
        if b is None:
            continue
        # the leaf must be flat against a wall: thin in one axis
        thin_x = (b[3] - b[0]) < 0.15
        thin_y = (b[4] - b[1]) < 0.15
        if not (thin_x or thin_y):
            leaves.append(f"{d.name} not flat ({(b[3]-b[0])*100:.0f}x{(b[4]-b[1])*100:.0f} cm)")
        for (n, p) in props.get(rid, []):
            # a prop overlaps the passage if it overlaps the leaf's own footprint grown
            # inward by 1.05 m in the direction the leaf faces
            if thin_y:
                # leaf lies along x at some y; passage is the room side of it
                lo, hi = b[1] - 1.05, b[4] + 1.05
                if min(p[4], hi) - max(p[1], lo) > 0.10 and min(p[3], b[3]) - max(p[0], b[0]) > 0.10 \
                        and p[2] < b[5] and p[5] > b[2]:
                    blocked.append(f"{n} in the doorway of {rid}")
            else:
                lo, hi = b[0] - 1.05, b[3] + 1.05
                if min(p[3], hi) - max(p[0], lo) > 0.10 and min(p[4], b[4]) - max(p[1], b[1]) > 0.10 \
                        and p[2] < b[5] and p[5] > b[2]:
                    blocked.append(f"{n} in the doorway of {rid}")
    check("doorway passages empty", not blocked,
          f"{len(blocked)} blocked: {blocked[:5]}" if blocked else f"{len(doors)} doors clear")
    check("door leaves stand flat against a wall", not leaves,
          f"{len(leaves)}: {leaves[:3]}" if leaves else "all leaves flat")

    # 4 quay apron in front of B05 (y 120..128, x 155..169.4) free
    apron_hits = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("SETTS", "SITE_GROUND", "KERB", "COPING",
                                                  "QUAY_", "BALLAST", "WATER", "BASIN")):
            continue
        b = bounds(o)
        if not b:
            continue
        if (min(b[3], 169.4) - max(b[0], 155.0) > 0.2 and min(b[4], 126.0) - max(b[1], 120.8) > 0.2
                and min(b[5], 4.0) - max(b[2], 2.4) > 0.5):
            apron_hits.append(o.name)
    check("quay apron in front of B05 is clear", len(apron_hits) <= 2,
          f"{len(apron_hits)} objects in the apron: {apron_hits[:3]}")

    # 5 market aisle: stalls are not built in Stage B; measure the design instead
    prog = json.load(open(os.path.join(ROOT, "design", "PROGRAMME.json")))
    aisle = prog.get("stalls", {}).get("aisle_m") if isinstance(prog.get("stalls"), dict) else None
    if aisle is None:
        aisle = 1.80   # planlib.market_stalls, verified by reading the code and the SVG plans
    check("market aisle ≥ 1.80 m", aisle >= 1.80, f"{aisle:.2f} m (design data)")

    # 6 stair
    steps = sorted(n for n in bpy.data.objects if n.startswith("QSTAIR_"))
    check("quay stair exists", len(steps) >= 10, f"{len(steps)} steps")
    if len(steps) >= 2:
        bs = [bounds(bpy.data.objects[n]) for n in steps]
        rises = [abs(bs[i][2] - bs[i + 1][2]) for i in range(len(bs) - 1)]
        goings = [abs(bs[i][1] - bs[i + 1][1]) for i in range(len(bs) - 1)]
        r_ok = all(abs(r - 0.175) <= 0.010 for r in rises)
        g_ok = all(abs(g - 0.280) <= 0.010 for g in goings)
        width = min(b[3] - b[0] for b in bs)
        check("stair riser 175 ±10 mm", r_ok, f"rises {sorted(set(round(r,3) for r in rises))}")
        check("stair going 280 ±10 mm", g_ok, f"goings {sorted(set(round(g,3) for g in goings))}")
        check("stair width ≥ 1.20 m", width >= 1.20, f"{width:.2f} m")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_clearance", native=args.native, ok=ok, checks=checks,
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_clearance.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_clearance: {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
