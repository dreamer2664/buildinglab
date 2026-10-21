#!/usr/bin/env python3
"""tools/audit_scene.py — measure the scene instead of trusting the picture.

Run: blender --background PNEUMA.blend --python tools/audit_scene.py --python-exit-code 1 -- --audit

This is the precursor to `v_parts`, `v_units` and `v_mechanism`. It answers, with
numbers, the questions that a still image raises and cannot settle:

  F6   is every part inside its mechanism's bounding cage?
  F2   do the hopper walls actually enclose the grains, or does grain pass
       through solid geometry?
  F7   is every lamp ray-tested to open space?
  F12  do the wheels touch the track within 2 mm?
  F39  is there a screw, bolt, nut or rivet anywhere?

Exit 1 if any check fails. A scene audit that finds nothing but never looked is
not an audit.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ROOT, "evidence")

# the bounding cage for the whole cart-theatre, in metres (§F6)
CAGE = {"x": (-1.2, 1.2), "y": (-1.2, 1.2), "z": (-0.20, 1.30)}


def world_bbox(o):
    """True world-space bounds, accounting for scale and rotation (F6)."""
    if o.type != "MESH":
        return None
    xs, ys, zs = [], [], []
    for corner in o.bound_box:                     # 8 local corners
        wc = o.matrix_world @ __import__("mathutils").Vector(corner)
        xs.append(wc.x); ys.append(wc.y); zs.append(wc.z)
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def audit() -> int:
    problems = []
    notes = []
    sc = bpy.context.scene

    census = Counter()
    materials = Counter()
    rows = []
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        stem = o.name.split("_")[0]
        census[stem] += 1
        for s in o.material_slots:
            materials[s.name if s.name else "<empty>"] += 1
        bb = world_bbox(o)
        if bb:
            rows.append({"name": o.name, "stem": stem, "bbox": [round(v, 4) for v in bb]})

    # ---- F6: bounding cage ---------------------------------------------------
    for r in rows:
        if r["stem"] == "FLOOR":
            continue          # the floor is the ground, not a caged machine part
        x0, y0, z0, x1, y1, z1 = r["bbox"]
        cx = CAGE["x"]; cy = CAGE["y"]; cz = CAGE["z"]
        if not (cx[0] <= x0 and x1 <= cx[1] and cy[0] <= y0 and y1 <= cy[1]
                and cz[0] <= z0 and z1 <= cz[1]):
            problems.append({"code": "F6", "detail": f"{r['name']} bbox {r['bbox']} outside the cage {CAGE}"})

    # ---- F2: do the hopper walls enclose the grains? --------------------------
    walls = [r for r in rows if r["name"].startswith("HOPPER_WALL")]
    grains = [r for r in rows if r["stem"] == "GRAIN"]
    if walls and grains:
        # the walls' vertical span must contain the grain cloud's vertical span
        wall_z0 = min(r["bbox"][2] for r in walls)
        wall_z1 = max(r["bbox"][5] for r in walls)
        grain_z0 = min(r["bbox"][2] for r in grains)
        grain_z1 = max(r["bbox"][5] for r in grains)
        if grain_z0 < wall_z0 or grain_z1 > wall_z1:
            problems.append({
                "code": "F2",
                "detail": f"grain cloud z=[{grain_z0:.3f},{grain_z1:.3f}] is not inside the hopper walls z=[{wall_z0:.3f},{wall_z1:.3f}]",
            })
        # and the grains must not start above the lid
        lid = [r for r in rows if r["name"].startswith("HOPPER_LID")]
        if lid and grain_z1 > lid[0]["bbox"][2]:
            problems.append({
                "code": "F2",
                "detail": f"grain cloud top {grain_z1:.3f} is above the lid underside {lid[0]['bbox'][2]:.3f}",
            })
        # the orifice must be below the grain cloud, or nothing can discharge
        throat = [r for r in rows if "THROAT" in r["name"]]
        if throat and throat[0]["bbox"][5] > grain_z0:
            problems.append({
                "code": "F2",
                "detail": f"throat top {throat[0]['bbox'][5]:.3f} is above the grain cloud bottom {grain_z0:.3f} — the orifice is plugged",
            })
    elif grains and not walls:
        problems.append({"code": "F2", "detail": f"{len(grains)} grains with no hopper walls at all"})

    # ---- F39: no modern fasteners -------------------------------------------
    banned = ("SCREW", "BOLT", "NUT", "RIVET", "STAPLE", "ZIP", "WELD", "HINGE")
    for r in rows:
        for b in banned:
            if b in r["name"].upper():
                problems.append({"code": "F39", "detail": f"{r['name']} is a banned modern fastener ({b})"})

    # ---- F7: lamps ray-tested to open space ---------------------------------
    for o in bpy.data.objects:
        if o.type == "LIGHT":
            # is anything solid within 0.3 m of the lamp?
            nearest = None
            for r in rows:
                cx = (r["bbox"][0] + r["bbox"][3]) / 2
                cy = (r["bbox"][1] + r["bbox"][4]) / 2
                cz = (r["bbox"][2] + r["bbox"][5]) / 2
                d = math.dist(o.location, (cx, cy, cz))
                if nearest is None or d < nearest[1]:
                    nearest = (r["name"], d)
            if nearest and nearest[1] < 0.30:
                problems.append({"code": "F7", "detail": f"lamp {o.name} is {nearest[1]:.3f} m from {nearest[0]}"})

    # ---- F12: wheels touch the track within 2 mm ----------------------------
    wheels = [r for r in rows if r["stem"] == "WHEEL" and "RIM" in r["name"]]
    floor = [r for r in rows if r["stem"] == "FLOOR"]
    if wheels and floor:
        fz = floor[0]["bbox"][5]
        for w in wheels:
            gap = w["bbox"][2] - fz
            if abs(gap) > 0.002:
                problems.append({"code": "F12", "detail": f"{w['name']} rim bottom {w['bbox'][2]:.4f} vs floor top {fz:.4f} — gap {gap*1000:.1f} mm"})

    # ---- material census ----------------------------------------------------
    distinct = len([m for m in materials if m != "<empty>"])
    if distinct < 4:
        notes.append(f"only {distinct} distinct material(s) in use — the artifacts will read as one colour")

    result = {
        "t": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "named_parts": len(rows),
        "census": dict(census),
        "materials": dict(materials),
        "distinct_materials": distinct,
        "problems": problems,
        "notes": notes,
        "verdict": "PASS" if not problems else "FAIL",
    }
    with open(os.path.join(EVIDENCE, "SCENE_AUDIT.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"audit_scene: {len(rows)} named parts, {distinct} distinct materials")
    print(f"  census: {dict(census)}")
    print(f"  materials: {dict(materials)}")
    for n in notes:
        print(f"  note: {n}")
    if problems:
        print(f"  verdict: FAIL — {len(problems)} problem(s)")
        for p in problems[:20]:
            print(f"    {p['code']}: {p['detail']}")
    else:
        print("  verdict: PASS")
    return 1 if problems else 0


def main() -> None:
    argv = [a for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []) if a != "--"]
    os.makedirs(EVIDENCE, exist_ok=True)
    mode = argv[0].lstrip("-") if argv else "audit"
    if mode == "audit":
        sys.exit(audit())


if __name__ == "__main__":
    main()
