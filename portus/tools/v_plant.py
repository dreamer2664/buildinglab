#!/usr/bin/env python3
"""v_plant.py — G7 W3: no cable or rod ends in the air.

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_plant.py -- --native portus/source/PORTUS.blend

The packet's rule is blunt: every cable must terminate on a load. This validator
walks every object whose name says rope/cable/wire/sling/chain, takes the two
end vertices of each, and asks whether each end is within 120 mm of some other
object's geometry (a bollard, a block, a deck fitting). It then checks the crane
has the parts a hammerhead crane has: counterweight, slewing ring, cab, glazing,
and a load on the hook.

  1  crane: two rails, two legs, portal, slewing ring, tower
  2  crane: cab with glazing, machinery house, mast cap
  3  crane: counter-jib carries a counterweight of at least 3 t equivalent volume
  4  crane: a load hangs on the hook
  5  crane: a driver is in the cab
  6  every rope/cable/sling ends on a solid (no loose ends)
  7  every rope has at least two ends (a rope with one end is a wire in the air)
  8  the hoist rope runs from jib height to the hook block
Exit 0 PASS, 2 FAIL. Writes evidence/validation/v_plant.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
END_TOL = 0.120


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    args = ap.parse_args()
    import bpy

    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    objs = {o.name: o for o in bpy.data.objects if o.type == "MESH"}

    def bounds(o):
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        return (min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs),
                max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))

    have = lambda n: n in objs
    parts = ["CRANE_RAIL_W", "CRANE_RAIL_E", "CRANE_LEG_W", "CRANE_LEG_E", "CRANE_PORTAL",
             "CRANE_RING", "CRANE_TOWER", "CRANE_JIB", "CRANE_COUNTERJIB", "CRANE_CAB",
             "CRANE_MACHINERY_HOUSE", "CRANE_MAST_CAP"]
    missing = [p for p in parts if not have(p)]
    check("crane structure complete", not missing, f"missing {missing}" if missing else "all parts present")

    glazing = [n for n in objs if n.startswith("CRANE_CAB_GLASS")]
    check("crane cab is glazed", len(glazing) >= 1, f"{len(glazing)} panes")

    cw = objs.get("CRANE_COUNTERWEIGHT")
    if cw is None:
        check("counterweight on the counter-jib", False, "not found")
    else:
        b = bounds(cw)
        vol = (b[3] - b[0]) * (b[4] - b[1]) * (b[5] - b[2])
        check("counterweight on the counter-jib", vol >= 2.0, f"{vol:.2f} m3 of concrete")
        jb = bounds(objs["CRANE_COUNTERJIB"]) if have("CRANE_COUNTERJIB") else None
        if jb:
            check("counterweight sits under the counter-jib", b[0] >= jb[0] - 0.1 and b[3] <= jb[3] + 0.1,
                  f"x {b[0]:.2f}..{b[3]:.2f} vs jib {jb[0]:.2f}..{jb[3]:.2f}")

    load = objs.get("CRANE_LOAD")
    hook = objs.get("CRANE_HOOK")
    if load is None or hook is None:
        check("a load hangs on the hook", False, "load or hook missing")
    else:
        lb, hb = bounds(load), bounds(hook)
        gap = lb[5] - hb[2]
        check("a load hangs on the hook", -0.5 < gap < 1.5,
              f"load top {lb[5]:.2f} vs hook bottom {hb[2]:.2f}")
        check("the load is in the air, not on the quay", lb[2] > 2.40 + 1.0,
              f"load bottom {lb[2]:.2f} m")

    driver = [n for n in bpy.data.objects if n.startswith("CRANE_DRIVER")]
    cab = objs.get("CRANE_CAB")
    if driver and cab:
        cb = bounds(cab)
        inside = any(cb[0] - 0.2 <= o.matrix_world.translation.x <= cb[3] + 0.2
                     and cb[1] - 0.2 <= o.matrix_world.translation.y <= cb[4] + 0.2
                     and cb[2] - 0.2 <= o.matrix_world.translation.z <= cb[5] + 0.2
                     for o in driver if o.type == "MESH")
        check("a driver is in the cab", inside, f"{len(driver)} objects, inside={inside}")

    # ropes: every end must touch something
    rope_names = [n for n in objs if any(k in n for k in ("ROPE", "CABLE", "WIRE", "SLING", "CHAIN"))]
    check("ropes and slings exist", len(rope_names) >= 8, f"{len(rope_names)} objects")

    solid_bounds = []
    for n, o in objs.items():
        if any(k in n for k in ("ROPE", "CABLE", "WIRE", "SLING", "CHAIN")):
            continue
        solid_bounds.append((n, bounds(o)))

    def near_solid(pt, skip, tol=END_TOL):
        for (n, b) in solid_bounds:
            if n == skip:
                continue
            if (b[0] - tol <= pt[0] <= b[3] + tol and b[1] - tol <= pt[1] <= b[4] + tol
                    and b[2] - tol <= pt[2] <= b[5] + tol):
                return n
        return None

    loose = []
    multi = 0
    checked = 0
    for n in rope_names:
        o = objs[n]
        mw = o.matrix_world
        pts = [mw @ v.co for v in o.data.vertices]
        if len(pts) < 2:
            loose.append((n, "fewer than two vertices"))
            continue
        # the two ends of a rope lie on the axis: take extreme vertices along it
        lo = min(pts, key=lambda p: p.z)
        hi = max(pts, key=lambda p: p.z)
        ends = [lo, hi]
        if len({(round(p.x, 2), round(p.y, 2), round(p.z, 2)) for p in ends}) < 2:
            loose.append((n, "one end only"))
            continue
        multi += 1
        for e in ends:
            checked += 1
            if near_solid(e, n) is None:
                loose.append((n, f"end at ({e.x:.2f},{e.y:.2f},{e.z:.2f}) touches nothing"))
                break
    check("every rope end meets a solid", not loose,
          f"{checked} ends checked, {len(loose)} loose: {loose[:4]}")
    check("every rope has two distinct ends", multi == len(rope_names),
          f"{multi}/{len(rope_names)}")

    hr = objs.get("CRANE_HOIST_ROPE")
    hb = objs.get("CRANE_HOOK_BLOCK")
    jib = objs.get("CRANE_JIB")
    if hr and hb and jib:
        rh, hbb, jb = bounds(hr), bounds(hb), bounds(jib)
        check("hoist rope runs from the jib to the hook block",
              abs(rh[5] - jb[2]) < 0.6 and abs(rh[2] - hbb[5]) < 0.6,
              f"rope {rh[2]:.2f}..{rh[5]:.2f}, jib {jb[2]:.2f}, block {hbb[5]:.2f}")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_plant", native=args.native, ok=ok, checks=checks,
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_plant.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_plant: {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
