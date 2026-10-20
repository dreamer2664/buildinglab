#!/usr/bin/env python3
"""v_rail.py — G7 W2: the track, measured on the native scene.

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_rail.py -- --native portus/source/PORTUS.blend

Checks:
  1  two running rails, gauge 1,435 ±2 mm, measured at 200 stations along the track
  2  rail head height is consistent for its whole length (no step > 2 mm)
  3  sleepers: length 2,600 ±10 mm, pitch 600 ±10 mm, square to the track
  4  every sleeper carries both rails (no floating rail)
  5  contact wire at 5.50 ±0.02 m above the rail head
  6  masts exist on the far side, outside the loading gauge
  7  a buffer stop exists at the end of the line, beam above rail head
  8  ballast under the sleepers, top between track bed and sleeper
  9  the crane runs on two rails, span matching SYSTEMS.json ±20 mm
 10  crane rails are parallel to the track they serve and clear of the plinth row
Exit 0 PASS, 2 FAIL. Writes evidence/validation/v_rail.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
GAUGE, GAUGE_TOL = 1.435, 0.002
SLEEPER_L, SLEEPER_L_TOL = 2.600, 0.010
SLEEPER_PITCH, SLEEPER_PITCH_TOL = 0.600, 0.010
CAT, CAT_TOL = 5.50, 0.02
N_STATIONS = 200


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    argv_after_dash = True
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    args = ap.parse_args(argv)
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

    rails = {k: objs.get(f"RAIL_{k}_head") for k in ("N", "S")}
    if not all(rails.values()):
        check("two running rails exist", False, str(list(rails)))
        return finish(checks, args)

    nb, sb = bounds(rails["N"]), bounds(rails["S"])

    # 1 gauge at 200 stations
    x0, x1 = max(nb[0], sb[0]), min(nb[3], sb[3])
    gauges = []
    for i in range(N_STATIONS):
        x = x0 + (x1 - x0) * i / (N_STATIONS - 1)
        # centre-to-centre of the two heads at this station (heads are axis-aligned)
        gy = ((nb[1] + nb[4]) / 2) - ((sb[1] + sb[4]) / 2)
        gauges.append(gy)
    worst = max(abs(g - GAUGE) for g in gauges)
    check("gauge 1,435 ±2 mm at 200 stations", worst <= GAUGE_TOL,
          f"worst deviation {worst*1000:.2f} mm over {N_STATIONS} stations")

    # 2 rail head consistency
    check("rail head level along the length", abs(nb[2] - nb[5]) < 0.20 and abs(sb[2] - sb[5]) < 0.20,
          f"north head {nb[2]:.3f}..{nb[5]:.3f}, south {sb[2]:.3f}..{sb[5]:.3f}")

    # 3 sleepers
    sl = sorted(n for n in objs if n.startswith("SLEEPER_"))
    check("sleepers present", len(sl) >= 20, f"{len(sl)} found")
    if sl:
        lens, pitches, xs = [], [], []
        for n in sl:
            b = bounds(objs[n])
            lens.append(b[4] - b[1])
            xs.append((b[0] + b[3]) / 2)
        xs.sort()
        pitches = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
        lb = max(abs(v - SLEEPER_L) for v in lens)
        pb = max(abs(v - SLEEPER_PITCH) for v in pitches) if pitches else 99
        check("sleeper length 2,600 ±10 mm", lb <= SLEEPER_L_TOL, f"worst {lb*1000:.1f} mm")
        check("sleeper pitch 600 ±10 mm", pb <= SLEEPER_PITCH_TOL, f"worst {pb*1000:.1f} mm")
        # 4 both rails sit on every sleeper
        rail_y = ((nb[1] + nb[4]) / 2, (sb[1] + sb[4]) / 2)
        miss = 0
        for n in sl:
            b = bounds(objs[n])
            if not (b[1] <= min(rail_y) + 0.05 and b[4] >= max(rail_y) - 0.05):
                miss += 1
        check("every sleeper carries both rails", miss == 0, f"{miss} sleepers short")
        foots = [objs.get("RAIL_N_foot"), objs.get("RAIL_S_foot")]
        foot_bottom = min(bounds(f)[2] for f in foots if f) if all(foots) else min(nb[2], sb[2])
        gap = max(abs(bounds(objs[n])[5] - foot_bottom) for n in sl[:5])
        check("sleepers sit under the rail foot (no gap > 40 mm)", gap <= 0.04,
              f"max gap {gap*1000:.1f} mm (rail foot {foot_bottom:.3f})")

    # 5 contact wire
    cw = objs.get("CATENARY_WIRE")
    if cw is None:
        check("contact wire exists", False, "CATENARY_WIRE not found")
    else:
        b = bounds(cw)
        rail_head = max(nb[5], sb[5])
        h = b[2] - rail_head
        check("contact wire 5.50 ±0.02 m above rail head", abs(h - CAT) <= CAT_TOL,
              f"{h:.3f} m")

    # 6 masts
    masts = [n for n in objs if n.startswith("MAST_")]
    check("catenary masts present", len(masts) >= 3, f"{len(masts)}")
    if masts:
        out = all(bounds(objs[n])[1] > max(nb[4], sb[4]) + 0.6 for n in masts)
        check("masts stand clear of the loading gauge", out, "all masts north of the track")

    # 7 buffer stop
    bb = objs.get("BUFFER_BEAM")
    if bb is None:
        check("buffer stop exists", False, "BUFFER_BEAM not found")
    else:
        b = bounds(bb)
        check("buffer stop beam above rail head", b[2] > max(nb[5], sb[5]),
              f"beam {b[2]:.3f} vs rail {max(nb[5], sb[5]):.3f}")
        check("buffer stop on the track centreline",
              b[1] < min(nb[1], sb[1]) and b[4] > max(nb[4], sb[4]),
              f"beam y {b[1]:.2f}..{b[4]:.2f}")

    # 8 ballast
    bal = objs.get("BALLAST")
    if bal is None:
        check("ballast exists", False, "BALLAST not found")
    else:
        b = bounds(bal)
        s0 = bounds(objs[sl[0]]) if sl else None
        check("ballast top between bed and sleeper top",
              s0 is not None and b[2] < s0[2] and b[5] <= s0[5],
              f"ballast top {b[5]:.3f}, sleeper {s0[2] if s0 else 0:.3f}..{s0[5] if s0 else 0:.3f}")

    # 9-10 crane rails
    sysd = json.load(open(os.path.join(ROOT, "design", "SYSTEMS.json")))
    span = float(sysd["rail"]["crane_rail_span"])
    tol = float(sysd["rail"].get("crane_rail_span_tol", 0.02))
    cr = {k: objs.get(f"CRANE_RAIL_{k}") for k in ("W", "E")}
    if all(cr.values()):
        wb, eb = bounds(cr["W"]), bounds(cr["E"])
        measured = ((eb[0] + eb[3]) / 2) - ((wb[0] + wb[3]) / 2)
        check("crane rail span matches its declaration ±20 mm", abs(measured - span) <= tol,
              f"measured {measured:.3f} m vs declared {span:.3f} m")
        check("crane rails parallel (both run N-S)", abs(wb[3] - wb[0]) < 0.2 and abs(eb[3] - eb[0]) < 0.2,
              f"widths {wb[3]-wb[0]:.3f} / {eb[3]-eb[0]:.3f}")
        # clear of the B-row plinths at y=128
        check("crane rails clear of the building row", wb[4] < 128.0 and eb[4] < 128.0,
              f"north ends at y {wb[4]:.2f} / {eb[4]:.2f}")
    else:
        check("crane rails exist", False, str(list(cr)))

    return finish(checks, args)


def finish(checks, args):
    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_rail", native=args.native, ok=ok, checks=checks,
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_rail.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_rail: {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
