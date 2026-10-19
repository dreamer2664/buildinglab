#!/usr/bin/env python3
"""v_contact.py — G2: things sit on things.

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_contact.py -- --native portus/source/PORTUS.blend

Method, stated plainly because it bounds what the result means: this is a
**bounding-box** test on horizontal support, plus an exact degenerate-face test
on the meshes. It cannot see an interpenetration that fits inside two boxes.
evidence/validation/v_contact.json says so.

  1  no prop floats: every furniture object's bottom is within 60 mm of its
     room floor, a shelf surface, or another prop's top
  2  no coplanar overlapping faces between props in the same room
  3  no degenerate faces (zero area) anywhere in the model
  4  no prop sits inside another prop's box by more than 30 mm on two axes
  5  every mesh object casts shadows (visibility flag is on)
Exit 0 PASS, 2 FAIL.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
FLOAT_TOL = 0.060
OVERLAP_TOL = 0.030


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    args = ap.parse_args()
    import bpy
    from mathutils import Vector

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

    rooms = {}
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("ROOM_") and "_" in o.name[5:]:
            rid = o.name.split("_")[1]
            rooms.setdefault(rid, []).append(o)

    def floor_z(rid):
        for o in rooms[rid]:
            if o.name.endswith("_floor"):
                b = bounds(o)
                return b[5] if b else None
        return None

    # 1 floating furniture
    floating = []
    for rid, objs in rooms.items():
        fz = floor_z(rid)
        if fz is None:
            continue
        boxes = [bounds(o) for o in objs]
        for o in objs:
            n = o.name
            if any(t in n for t in ("_floor", "_ceiling", "_lining", "_practical", "_glass",
                                    "_winfram", "_doorframe", "_doorhead", "_doorleaf", "_sill",
                                    "_lampcord")):
                continue
            b = bounds(o)
            if b is None:
                continue
            bottom = b[2]
            if bottom - fz <= FLOAT_TOL:
                continue                                    # standing on the floor
            # or standing on something whose top is just under it and overlaps in plan
            supported = False
            for c in boxes:
                if c is None:
                    continue
                if abs(c[5] - bottom) <= FLOAT_TOL and c[0] < b[3] and c[3] > b[0] \
                        and c[1] < b[4] and c[4] > b[1]:
                    supported = True
                    break
            if not supported:
                floating.append(f"{n} bottom {bottom:.3f} vs floor {fz:.3f}")
    check("no furniture floats", not floating,
          f"{len(floating)} floating: {floating[:5]}" if floating else "all supported")

    # 2 coplanar overlapping faces between props
    coplanar = []
    for rid, objs in rooms.items():
        bs = [(o.name, bounds(o)) for o in objs if bounds(o)]
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a, b = bs[i][1], bs[j][1]
                # two boxes share a face plane AND overlap in the other two axes
                same_x = abs(a[0] - b[0]) < 1e-4 or abs(a[3] - b[3]) < 1e-4
                same_y = abs(a[1] - b[1]) < 1e-4 or abs(a[4] - b[4]) < 1e-4
                same_z = abs(a[2] - b[2]) < 1e-4 or abs(a[5] - b[5]) < 1e-4
                if same_z and (min(a[3], b[3]) - max(a[0], b[0]) > 1e-3
                               and min(a[4], b[4]) - max(a[1], b[1]) > 1e-3):
                    coplanar.append(f"{bs[i][0]} / {bs[j][0]} share a z-plane")
    check("no coplanar overlapping faces", not coplanar,
          f"{len(coplanar)}: {coplanar[:3]}" if coplanar else "none found")

    # 3 degenerate faces
    bad_faces = 0
    worst = None
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        for p in o.data.polygons:
            if p.area < 1e-9:
                bad_faces += 1
                worst = worst or o.name
    check("no zero-area faces", bad_faces == 0, f"{bad_faces} faces, e.g. {worst}")

    # 4 gross interpenetration
    deep = []
    for rid, objs in rooms.items():
        bs = [(o.name, bounds(o)) for o in objs if bounds(o)]
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a, b = bs[i][1], bs[j][1]
                ox = min(a[3], b[3]) - max(a[0], b[0])
                oy = min(a[4], b[4]) - max(a[1], b[1])
                oz = min(a[5], b[5]) - max(a[2], b[2])
                if ox > OVERLAP_TOL and oy > OVERLAP_TOL and oz > OVERLAP_TOL:
                    deep.append(f"{bs[i][0]} x {bs[j][0]} ({ox*1000:.0f}x{oy*1000:.0f}x{oz*1000:.0f} mm)")
    check("no prop boxes interpenetrate deeply", not deep,
          f"{len(deep)}: {deep[:3]}" if deep else "none")

    # 5 shadows
    no_shadow = [o.name for o in bpy.data.objects
                 if o.type == "MESH" and (o.visible_shadow is False or o.visible_camera is False)]
    check("every mesh casts shadows", not no_shadow, f"{len(no_shadow)} disabled")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_contact", native=args.native, ok=ok, checks=checks,
                   method="bounding-box support + exact degenerate-face area test; "
                          "cannot detect an interpenetration contained inside two boxes",
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_contact.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_contact: {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
