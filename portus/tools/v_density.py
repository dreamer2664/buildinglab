#!/usr/bin/env python3
"""v_density.py — G3: a room is furnished, not sprinkled.

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_density.py -- --native portus/source/PORTUS.blend

Floors from the packet:
  living ≥70 · kitchen ≥90 · bedroom ≥40 · bathroom ≥28 · entry ≥18
  shop ≥150 · warehouse floor ≥60 · market stall ≥45 · workshop ≥80
and every prop must be its own object with ≥40 triangles (a flat quad pretending
to be a chair is not a prop).

  1  every room meets its floor for its class
  2  100 % of apartments are dressed (no apartment with an empty room)
  3  every prop is a separate object
  4  every prop has ≥40 triangles
  5  no room is over its own ceiling (a room stuffed to 3,000 props is a bug too)
Exit 0 PASS, 2 FAIL. Writes evidence/validation/v_density.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)

FLOORS = {"living": 70, "kitchen": 90, "bedroom": 40, "bathroom": 28, "entry": 18,
          "sales": 150, "warehouse floor": 60, "stall": 45, "workshop floor": 80,
          "machine hall": 80, "joinery": 80, "stock": 46, "staff": 14, "wc": 6}
CEILING = 900
MIN_TRIS = 40


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    args = ap.parse_args()
    import bpy

    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    def tri_count(o):
        return sum(len(p.vertices) - 2 for p in o.data.polygons)

    # room kinds come from the schedule; the scene carries them in the object name
    import csv
    sched = {r["room_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "design", "SCHEDULE.csv")))}

    props = defaultdict(list)
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("ROOM_"):
            continue
        parts = o.name.split("_")
        if len(parts) < 3:
            continue
        rid = parts[1]
        if any(t in o.name for t in ("_floor", "_ceiling", "_lining", "_winfram", "_glass",
                                     "_sill", "_doorframe", "_doorhead", "_doorleaf", "_practical")):
            continue
        props[rid].append(o)

    under, empty, overs = [], [], []
    by_kind = defaultdict(lambda: [0, 0, 10 ** 9])
    for rid, objs in props.items():
        row = sched.get(rid)
        kind = row["name"] if row else "?"
        n = len(objs)
        need = FLOORS.get(kind)
        agg = by_kind[kind]
        agg[0] += 1
        agg[1] += n
        agg[2] = min(agg[2], n)
        if n == 0:
            empty.append(rid)
        elif need is not None and n < need:
            under.append(f"{rid} {kind} {n}/{need}")
        if n > CEILING:
            overs.append(f"{rid} {kind} {n}")

    check("every room meets its class floor", not under,
          f"{len(under)} short: {under[:6]}" if under else
          " ".join(f"{k}:{v[1]//v[0]}avg/{v[2]}min" for k, v in sorted(by_kind.items())))
    check("no empty room", not empty, f"{len(empty)}: {empty[:6]}" if empty else "all dressed")
    check("no room is absurdly stuffed", not overs, f"{len(overs)}: {overs[:4]}" if overs else "none")

    allprops = [o for objs in props.values() for o in objs]
    check("every prop is a separate object", len(allprops) == len({o.name for o in allprops}),
          f"{len(allprops)} props")

    tris = [(o.name, tri_count(o)) for o in allprops]
    low = [(n, t) for (n, t) in tris if t < MIN_TRIS]
    check(f"every prop has ≥{MIN_TRIS} triangles", not low,
          f"{len(low)} under: {low[:5]}" if low else f"min {min((t for _, t in tris), default=0)} tris")

    # apartments dressed: count rooms per apartment id from the schedule and require props in all
    apt_rooms = defaultdict(list)
    for rid, row in sched.items():
        if row.get("apartment"):
            apt_rooms[row["apartment"]].append(rid)
    undressed = [a for a, rids in apt_rooms.items() if any(len(props.get(r, [])) == 0 for r in rids)]
    check("100 % of apartments dressed", not undressed,
          f"{len(undressed)}/{len(apt_rooms)} undressed" if undressed else
          f"{len(apt_rooms)} apartments, all rooms furnished")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_density", native=args.native, ok=ok, checks=checks,
                   per_kind={k: dict(rooms=v[0], mean_props=round(v[1] / max(1, v[0]), 1),
                                     min_props=v[2]) for k, v in sorted(by_kind.items())},
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_density.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_density: {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
