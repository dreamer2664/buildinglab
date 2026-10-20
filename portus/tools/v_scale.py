#!/usr/bin/env python3
"""v_scale.py — metric law validator.

Two modes:

  --design-only   checks the programme data and the declared constants
                  (storey heights, doors, human, quay, gauge, bollards).
                  Proves the design obeys the packet; proves nothing about a mesh.
  --native FILE   opens the .blend inside Blender and measures the built scene:
                  water plane, quay top, building heights, door leaves, humans.
                  Requires bpy; run with:
                    blender -b --python-exit-code 1 --python portus/tools/v_scale.py -- --native portus/source/PORTUS.blend

Exit 0 on PASS, 2 on FAIL. Writes evidence/validation/v_scale[_native].json.
A design-only PASS is never reported as a native PASS.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DESIGN = os.path.join(ROOT, "design")
EVID = os.path.join(ROOT, "evidence", "validation")

# the packet's §15.1 values, restated here so the validator does not trust the model
PACKET = dict(res_storey=3.20, res_tol=0.03, com_storey=4.40, com_tol=0.05,
              ware_storey=4.00, ware_tol=0.05, door_w=0.90, door_h=2.10, door_tol=0.015,
              loading_w=2.50, loading_h=3.00, human=1.75, human_tol=0.10,
              eye=1.62, eye_tol=0.02, slab=0.24, quay_above=2.40, quay_tol=0.01,
              basin_depth=6.00, gauge=1.435, gauge_tol=0.002, bollard=8.00, bollard_tol=0.05,
              site_w=400.0, site_h=320.0, water_tol=0.005)

STOREY_CLASS = {3.20: ("residential", PACKET["res_tol"]),
                4.40: ("commercial", PACKET["com_tol"]),
                4.00: ("warehouse", PACKET["ware_tol"])}


def design_checks(design=None):
    D = design or DESIGN
    prog = json.load(open(os.path.join(D, "PROGRAMME.json")))
    sysd = json.load(open(os.path.join(D, "SYSTEMS.json")))
    specials_path = os.path.join(D, "SPECIAL_STOREYS.json")
    specials = json.load(open(specials_path)) if os.path.exists(specials_path) else {"declared": []}
    declared = {(d["building"], d["level"]): d for d in specials["declared"]}

    checks, fails = [], []

    def check(name, ok, detail=""):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))
        if not ok:
            fails.append(f"{name}: {detail}")

    # site and basin
    check("site is 400 x 320 m",
          abs(prog["site"]["w"] - PACKET["site_w"]) < 1e-6 and abs(prog["site"]["h"] - PACKET["site_h"]) < 1e-6,
          f"{prog['site']['w']} x {prog['site']['h']}")
    check("basin is 180 x 90 m",
          abs(prog["basin"]["w"] - 180) < 1e-6 and abs(prog["basin"]["d"] - 90) < 1e-6,
          f"{prog['basin']['w']} x {prog['basin']['d']}")
    check("water level 0.00", abs(sysd["water"]["level"]) <= PACKET["water_tol"],
          f"{sysd['water']['level']}")
    check("basin depth 6.00 m", abs(sysd["water"]["depth"] - PACKET["basin_depth"]) < 0.02,
          f"{sysd['water']['depth']}")
    check("quay top +2.40 m", abs(sysd["water"]["quay_top"] - PACKET["quay_above"]) <= PACKET["quay_tol"],
          f"{sysd['water']['quay_top']}")

    # storeys
    undeclared = []
    for b in prog["buildings"]:
        for i, st in enumerate(b["storeys"]):
            h = round(st["h"], 3)
            if h in STOREY_CLASS:
                continue
            if (b["id"], i + 1) not in declared:
                undeclared.append(f"{b['id']} L{i+1:02d} = {h} m")
    check("every storey height is canonical or declared special", not undeclared,
          "; ".join(undeclared[:6]))
    for key, (cls, tol) in STOREY_CLASS.items():
        n = sum(1 for b in prog["buildings"] for st in b["storeys"] if abs(st["h"] - key) < 1e-9)
        check(f"storeys at {key:.2f} m ({cls})", n > 0 or key == PACKET["ware_storey"], f"{n} found")

    # declared specials must match their building
    bad_special = []
    for (bid, lvl), d in declared.items():
        b = next((x for x in prog["buildings"] if x["id"] == bid), None)
        if not b:
            bad_special.append(f"{bid} missing")
        elif abs(b["storeys"][lvl - 1]["h"] - d["height"]) > 0.01:
            bad_special.append(f"{bid} L{lvl} {b['storeys'][lvl-1]['h']} != declared {d['height']}")
    check("declared specials match the programme", not bad_special, "; ".join(bad_special[:6]))

    # doors in the plan data
    sched = list(csv.DictReader(open(os.path.join(D, "SCHEDULE.csv"))))
    big = [r for r in sched if float(r["area_m2"]) > 400]
    missing = [r["room_id"] + " " + r["name"] for r in big if r.get("loading_door") != "1"]
    check("every room > 400 m2 carries a 2.50 x 3.00 loading door", not missing,
          f"{len(big)} large rooms, {len(missing)} without: {missing[:4]}")

    # bollards at 8.00 m +-0.05 along each run
    gaps = []
    bol = sorted(sysd["bollards"], key=lambda b: (b["y"], b["x"]))
    runs = {}
    for b in bol:
        runs.setdefault(round(b["y"], 2), []).append(b)
    for y, bs in runs.items():
        bs.sort(key=lambda b: b["x"])
        for a, c in zip(bs, bs[1:]):
            gaps.append(round(c["x"] - a["x"], 3))
    bad_gaps = [g for g in gaps if abs(g - PACKET["bollard"]) > PACKET["bollard_tol"]]
    check("bollard spacing 8.00 +-0.05", not bad_gaps, f"{len(bad_gaps)} gaps off: {bad_gaps[:5]}")

    # rail
    check("gauge 1.435 m", abs(sysd["rail"]["gauge"] - PACKET["gauge"]) < 1e-9, f"{sysd['rail']['gauge']}")
    check("catenary 5.50 m", abs(sysd["rail"]["catenary_height"] - 5.50) < 1e-9,
          f"{sysd['rail']['catenary_height']}")

    # human
    check("human height constant 1.75", abs(PACKET["human"] - 1.75) < 1e-9, "constant")
    return checks, fails


def native_checks(path):
    import bpy  # noqa
    from mathutils import Vector

    checks, fails = [], []

    def check(name, ok, detail=""):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))
        if not ok:
            fails.append(f"{name}: {detail}")

    bpy.ops.wm.open_mainfile(filepath=path)
    sc = bpy.context.scene
    check("unit scale is 1.0", abs(sc.unit_settings.scale_length - 1.0) < 1e-9,
          f"{sc.unit_settings.scale_length}")
    check("units are metric", sc.unit_settings.system == "METRIC", sc.unit_settings.system)

    def objs(prefix):
        return [o for o in bpy.data.objects if o.name.startswith(prefix)]

    def bbox_world(o):
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        return mn, mx

    water = objs("WATER_SURFACE")
    check("water surface exists", len(water) >= 1, f"{len(water)} objects")
    if water:
        mn, mx = bbox_world(water[0])
        check("water level +0.00 +-5 mm", abs(mx.z) <= PACKET["water_tol"], f"top z={mx.z:.4f}")
        check("water covers the basin", (mx.x - mn.x) > 170 and (mx.y - mn.y) > 80,
              f"{mx.x-mn.x:.1f} x {mx.y-mn.y:.1f} m")

    quay = objs("QUAY_COPING")
    check("quay coping exists", len(quay) >= 1, f"{len(quay)} objects")
    if quay:
        mn, mx = bbox_world(quay[0])
        check("quay top +2.40 +-10 mm", abs(mx.z - PACKET["quay_above"]) <= PACKET["quay_tol"],
              f"top z={mx.z:.4f}")

    blds = {}
    for o in bpy.data.objects:
        if o.name.startswith("BLDG_"):
            bid = o.name.split("_")[1]
            blds.setdefault(bid, []).append(o)
    check("buildings present in the native", len(blds) >= 1, f"{len(blds)} buildings")
    prog = json.load(open(os.path.join(DESIGN, "PROGRAMME.json")))
    expected = {b["id"]: b["height"] for b in prog["buildings"]}
    for bid, os_ in sorted(blds.items())[:12]:
        zs = []
        for o in os_:
            mn, mx = bbox_world(o)
            zs += [mn.z, mx.z]
        h = max(zs) - min(zs)
        want = expected.get(bid)
        if want:
            check(f"{bid} height {want:.2f} m", abs(h - want) <= 0.30, f"measured {h:.2f} m")

    doors = objs("DOOR_")
    bad = []
    for d in doors[:400]:
        mn, mx = bbox_world(d)
        w = max(mx.x - mn.x, mx.y - mn.y)
        h = mx.z - mn.z
        if abs(w - PACKET["door_w"]) > PACKET["door_tol"] or abs(h - PACKET["door_h"]) > PACKET["door_tol"]:
            bad.append(f"{d.name} {w:.3f}x{h:.3f}")
    check("door leaves 0.90 x 2.10 +-15 mm", not bad, f"{len(bad)}/{len(doors)} off: {bad[:4]}")

    people = objs("PERSON_")
    badh = []
    for p in people[:400]:
        mn, mx = bbox_world(p)
        h = mx.z - mn.z
        if abs(h - PACKET["human"]) > PACKET["human_tol"]:
            badh.append(f"{p.name} {h:.3f}")
    check("people 1.75 +-0.10 m", not badh, f"{len(badh)}/{len(people)} off: {badh[:4]}")

    return checks, fails


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    argv_after_dash = True
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", default=None)
    ap.add_argument("--design", default=DESIGN)
    ap.add_argument("--design-only", action="store_true")
    args = ap.parse_args(argv)
    os.makedirs(EVID, exist_ok=True)
    if args.native:
        checks, fails = native_checks(args.native)
        mode = "native"
        out = os.path.join(EVID, "v_scale_native.json")
    else:
        if not args.design_only:
            # explicit: do not let a design-only run masquerade as a model check
            print("NOTE: no --native given; running design-only because --design-only was implied")
        checks, fails = design_checks(args.design)
        mode = "design-only"
        out = os.path.join(EVID, "v_scale_design.json")
    for f in fails:
        print("FAIL:", f)
    json.dump(dict(validator="v_scale", mode=mode, ok=not fails, checks=checks, fails=fails),
              open(out, "w"), indent=1)
    print(f"v_scale ({mode}): {sum(1 for c in checks if c['ok'])}/{len(checks)} checks")
    print("PASS" if not fails else "FAIL")
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main())
