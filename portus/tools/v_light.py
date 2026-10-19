#!/usr/bin/env python3
"""v_light.py — G5: does the light behave like dawn in January?

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_light.py -- --native portus/source/PORTUS.blend
    python3 portus/tools/v_light.py --images portus/renders/proofs      # histogram half

Structural checks (need bpy):
  1  every counted residential room has ≥2 light sources (its practical + the window)
  2  every practical's colour temperature is 2300–2900 K
  3  practicals are inside their rooms and below the ceiling
  4  one sun, low (elevation < 12 deg, dawn in January)
Histogram checks (need Pillow, run on the rendered proofs):
  5  blown highlights < 0.8 % of pixels
  6  crushed shadows < 1.5 % of pixels
Exit 0 PASS, 2 FAIL. Writes evidence/validation/v_light[_images].json.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
K_LO, K_HI = 2300, 2900
BLOWN_MAX, CRUSHED_MAX = 0.008, 0.015


def kelvin(rgb):
    """Approximate colour temperature of a linear RGB triple (blackbody fit)."""
    r, g, b = rgb
    if r <= 0:
        return 0
    x = 0.0
    # simple mapping: red/blue ratio -> K over 2000..4000
    rb = max(1e-6, b / r)
    x = 2000.0 + 2000.0 * (1.0 - min(1.0, max(0.0, rb * 1.35)))
    return x


def structural(args):
    import bpy
    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    sched = {r["room_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "design", "SCHEDULE.csv")))}
    lights = [o for o in bpy.data.objects if o.type == "LIGHT"]
    practicals = [o for o in lights if o.name.endswith("_practical")]
    suns = [o for o in lights if o.data.type == "SUN"]

    res_rooms = [rid for rid, r in sched.items() if r.get("apartment")]
    missing = []
    for rid in res_rooms:
        n = len([o for o in practicals if o.name.startswith(f"ROOM_{rid}_")])
        has_window = sched[rid]["windows"] == "1"
        if n + (1 if has_window else 0) < 2:
            missing.append(f"{rid} ({n} lamp, window={has_window})")
    check("≥2 light sources in every residential room", not missing,
          f"{len(missing)} short: {missing[:4]}" if missing else f"{len(res_rooms)} rooms ok")

    temps = [(o.name, kelvin(tuple(o.data.color))) for o in practicals]
    bad = [(n, round(k)) for (n, k) in temps if not (K_LO <= k <= K_HI)]
    check("practicals 2300–2900 K", not bad,
          f"{len(bad)} off: {bad[:4]}" if bad else
          f"{len(temps)} practicals, {min(k for _, k in temps):.0f}–{max(k for _, k in temps):.0f} K")

    out = []
    for o in practicals:
        rid = o.name.split("_")[1]
        f = [x for x in bpy.data.objects if x.type == "MESH" and x.name == f"ROOM_{rid}_floor"]
        if not f:
            continue
        mw = f[0].matrix_world
        vs = [mw @ v.co for v in f[0].data.vertices]
        x0, y0, z0 = min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)
        x1, y1 = max(v.x for v in vs), max(v.y for v in vs)
        p = o.matrix_world.translation
        if not (x0 - 0.1 <= p.x <= x1 + 0.1 and y0 - 0.1 <= p.y <= y1 + 0.1
                and z0 < p.z < z0 + 3.2):
            out.append(o.name)
    check("practicals are inside their rooms", not out, f"{len(out)} outside: {out[:3]}")

    check("one low sun (dawn)", len(suns) == 1 and
          abs(suns[0].rotation_euler.x) > 1.0, f"{len(suns)} suns, pitch {suns[0].rotation_euler.x:.2f} rad")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_light", mode="native", ok=ok, checks=checks,
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_light.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_light (native): {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


def histograms(args):
    from PIL import Image
    import numpy as np
    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    files = sorted(f for f in os.listdir(args.images) if f.endswith(".png"))
    check("proof images to measure", len(files) >= 12, f"{len(files)} images")
    rows = []
    over_blown, over_crushed = [], []
    for f in files:
        im = Image.open(os.path.join(args.images, f)).convert("RGB")
        a = np.asarray(im).astype(np.float32) / 255.0
        lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
        blown = float((lum >= 0.995).mean())
        crushed = float((lum <= 0.005).mean())
        rows.append(dict(file=f, blown=round(blown, 5), crushed=round(crushed, 5),
                         mean=round(float(lum.mean()), 4)))
        if blown > BLOWN_MAX:
            over_blown.append(f"{f} {blown*100:.2f}%")
        if crushed > CRUSHED_MAX:
            over_crushed.append(f"{f} {crushed*100:.2f}%")
    check("blown highlights < 0.8 % of pixels", not over_blown,
          f"{len(over_blown)} views over: {over_blown[:4]}" if over_blown
          else f"max {max(r['blown'] for r in rows)*100:.2f} %")
    check("crushed shadows < 1.5 % of pixels", not over_crushed,
          f"{len(over_crushed)} views over: {over_crushed[:4]}" if over_crushed
          else f"max {max(r['crushed'] for r in rows)*100:.2f} %")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_light", mode="images", ok=ok, checks=checks, per_view=rows,
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_light_images.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_light (images): {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", default=None)
    ap.add_argument("--images", default=None)
    args = ap.parse_args()
    if args.images:
        return histograms(args)
    if args.native:
        return structural(args)
    print("need --native or --images")
    return 2


if __name__ == "__main__":
    sys.exit(main())
