#!/usr/bin/env python3
"""build.py — build PORTUS.blend from the plan library.

    blender45 -b --python-exit-code 1 --python portus/source/build.py

Stage B slice: B05 complete (shop + 4 floors x 2 apartments), 20 m of quay and
rail, the basin with water/foam/ice, a 90 m coaster at draft, one hammerhead
crane with a load, six people, 24 proof cameras. The other 47 buildings are
massing only — that is Stage C and it is not claimed here.

Everything the build knows about rooms comes from design/SCHEDULE.csv, the same
file the programme validator checks. A room rectangle in the schedule and the
room in the scene are the same expression (DECISIONS D-0010).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import sys
import time

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from build import geo, planlib as P, props  # noqa: E402

OUT = os.path.join(HERE, "PORTUS.blend")
LOG = []
T0 = time.time()


def log(*a):
    msg = " ".join(str(x) for x in a)
    LOG.append(msg)
    print(f"[build {time.time()-T0:6.1f}s] {msg}", flush=True)


# ── scene reset ────────────────────────────────────────────────────────────
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "METERS"
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = -0.55
    sc.render.resolution_x = 1024
    sc.render.resolution_y = 576
    sc.render.fps = 24


# ── schedule ───────────────────────────────────────────────────────────────
def compute_b05_rooms(spec):
    """Recompute B05's rooms exactly as the programme generator did, then join
    them to SCHEDULE.csv by (floor, apartment, name).

    The committed schedule carries ids and bounds but not the door/window
    rectangles, so the geometry is recomputed from planlib — the same functions
    the generator calls — rather than guessed. Counts are asserted against the
    schedule, so a drift is a build failure, not a silent mismatch.
    """
    apts = {a["id"]: a for a in P.apartment_catalogue()}
    ffls = P.floor_levels(spec)
    out = []
    for li, st in enumerate(spec["storeys"]):
        z = ffls[li]
        groups = []
        if li == 0:
            groups.append(("shop", P.shop_rooms(spec, z)))
        if st["use"] == "residential":
            for ai in range(2):
                apt_id = f"{spec['id']}-L{li+1:02d}-{'AB'[ai]}"
                a = apts[apt_id]
                rs, slot = P.apartment_rooms(spec, li, ai, apt_id, a["archetype"], a["seed"])
                groups.append((apt_id, rs, slot, a))
        for g in groups:
            if len(g) == 2:
                _, rs = g
                slot = None
                a = None
            else:
                _, rs, slot, a = g
            entries = P.openings_for_rooms(rs, spec, z, slot)
            for e in entries:
                r = e["room"]
                out.append(dict(room=r, door=e["door"], window=e["window"], level=li,
                                level_z=z, apartment=r.get("apartment"),
                                shop=r.get("shop"), name=r["name"]))
    return out


def join_schedule(spec, computed):
    """Attach the schedule's room_id to each computed room; fail loudly on drift."""
    rows = list(csv.DictReader(open(os.path.join(ROOT, "design", "SCHEDULE.csv"))))
    rows = [r for r in rows if r["building"] == spec["id"]]
    key = lambda li, apt, name: (int(li), (apt or "").strip(), name.strip())
    table = {}
    for c in computed:
        table.setdefault(key(c["level"] + 1, c["apartment"], c["name"]), []).append(c)
    joined, missing = [], 0
    for r in rows:
        k = key(r["floor"], r["apartment"], r["name"])
        cand = table.get(k)
        if not cand:
            missing += 1
            continue
        c = cand.pop(0)
        b = c["room"]
        if (abs(b["x0"] - float(r["x0"])) > 0.002 or abs(b["y0"] - float(r["y0"])) > 0.002
                or abs(b["x1"] - float(r["x1"])) > 0.002 or abs(b["y1"] - float(r["y1"])) > 0.002):
            raise SystemExit(f"schedule drift on {r['room_id']}: computed rect differs")
        joined.append(dict(id=r["room_id"], name=r["name"], kind=r["kind"],
                           level=int(r["floor"]), level_z=c["level_z"],
                           x0=b["x0"], y0=b["y0"], x1=b["x1"], y1=b["y1"],
                           w=b["w"], d=b["d"], building=spec["id"],
                           apartment=r["apartment"] or None,
                           door=c["door"], window=c["window"]))
    if missing:
        raise SystemExit(f"{missing} schedule rows had no computed room")
    return joined


# ── site ───────────────────────────────────────────────────────────────────
def build_site(M):
    C = geo.coll("SITE")
    x0, y0, x1, y1 = 0.0, 0.0, P.SITE_W, P.SITE_H
    bx0, by0, bx1, by1 = P.BASIN
    t = 0.30
    z = P.LAND_Z
    geo.box("SITE_GROUND_s", x0, y0, z - t, x1, by0, z, M["paving"], C)
    geo.box("SITE_GROUND_n", x0, by1, z - t, x1, y1, z, M["paving"], C)
    geo.box("SITE_GROUND_w", x0, by0, z - t, bx0, by1, z, M["paving"], C)
    geo.box("SITE_GROUND_e", bx1, by0, z - t, x1, by1, z, M["paving"], C)
    # setts: bands within 18 m of the basin, merged per band so the object gate
    # is a gate on stones, not on draws (D-104: one object per stone OOM-killed)
    def sett_band(name, ax0, ay0, ax1, ay1, budget=11000):
        rng = random.Random(int(hashlib.sha256(name.encode()).hexdigest()[:8], 16))
        verts, faces = [], []
        classes = [(0.090, 0.140), (0.105, 0.125), (0.120, 0.115)]
        y = ay0
        row = n = 0
        while y < ay1 - 0.05 and n < budget:
            h = classes[row % 3][0]
            x = ax0 + (0.055 if row % 2 else 0.0)
            while x < ax1 - 0.05 and n < budget:
                w = classes[(row + 1) % 3][1] * rng.uniform(0.86, 1.14)
                jx, jy = rng.uniform(0.003, 0.006), rng.uniform(0.003, 0.006)
                top = z + 0.040 + rng.uniform(-0.003, 0.003)
                x2, y2 = min(x + w, ax1), min(y + h, ay1)
                if x2 - x > 0.03 and y2 - y > 0.03:
                    o = len(verts)
                    # stones stand 40 mm proud of the mortar bed: the 5 mm joints
                    # have walls, so they read as joints even at 30 m (D-115 reopened)
                    verts += [(x + jx, y + jy, z + 0.004), (x2 - jx, y + jy, z + 0.004),
                              (x2 - jx, y2 - jy, z + 0.004), (x + jx, y2 - jy, z + 0.004),
                              (x + jx, y + jy, top), (x2 - jx, y + jy, top),
                              (x2 - jx, y2 - jy, top), (x + jx, y2 - jy, top)]
                    faces += [(o, o + 1, o + 2, o + 3), (o + 4, o + 7, o + 6, o + 5),
                              (o, o + 4, o + 5, o + 1), (o + 1, o + 5, o + 6, o + 2),
                              (o + 2, o + 6, o + 7, o + 3), (o + 3, o + 7, o + 4, o)]
                    n += 1
                x += w
            y += h
            row += 1
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.validate(verbose=False)
        ob = bpy.data.objects.new(name, me)
        ob.data.materials.append(M["sett"])
        C.objects.link(ob)
        return n

    # a mortar bed 40 mm below the stone faces
    for (ax0, ay0, ax1, ay1) in ((bx0 - 18, by1, bx1 + 18, by1 + 18),
                                 (bx0 - 18, by0 - 18, bx1 + 18, by0),
                                 (bx0 - 18, by0, bx0, by1), (bx1, by0, bx1 + 18, by1)):
        geo.box("MORTAR_BED", ax0, ay0, z - 0.02, ax1, ay1, z + 0.006, M["sand"], C)
    total = 0
    total += sett_band("SETTS_n", bx0 - 18, by1, bx1 + 18, by1 + 18)
    total += sett_band("SETTS_s", bx0 - 18, by0 - 18, bx1 + 18, by0)
    total += sett_band("SETTS_w", bx0 - 18, by0, bx0, by1)
    total += sett_band("SETTS_e", bx1, by0, bx1 + 18, by1)
    log(f"setts: {total:,} stones in 4 merged bands")
    # the district sits on a quay: outside the 400 x 320 m site the land falls to
    # water level over 24 m, so no camera can see the underside of the world
    for (ax0, ay0, ax1, ay1) in ((-24, -24, 0, 344), (400, -24, 424, 344),
                                 (-24, 320, 424, 344), (-24, -24, 424, 0)):
        geo.box("QUAY_SKIRT", ax0, ay0, -6.0, ax1, ay1, z - 0.30, M["stone"], C)
    geo.box("WATER_OUTSIDE", -400, -400, -0.05, 800, 800, -0.02, M["water"], C)
    # kerbs around the setts
    for (a, b, c, d) in ((bx0 - 18, by0 - 18, bx1 + 18, by0), (bx0 - 18, by1, bx1 + 18, by1 + 18)):
        geo.box("KERB", a, b, z, c, b + 0.12, z + 0.14, M["concrete"], C)
    return total


# ── water, bed, ice, foam ──────────────────────────────────────────────────
def build_water(M):
    C = geo.coll("WATER")
    bx0, by0, bx1, by1 = P.BASIN
    bed = P.WATER_Z - P.BASIN_DEPTH
    geo.grid_plane("BASIN_BED", bx0, by0, bx1, by1, bed, M["mud"], C, nx=28, ny=18,
                   disp=lambda x, y: 0.35 * math.sin(x / 9.0) * math.cos(y / 7.0))
    # the eight dropped objects the packet asks for
    drops = [(128.0, 46.0, "crate"), (150.0, 33.0, "paling"), (176.0, 62.0, "chain"),
             (205.0, 40.0, "wheel"), (232.0, 88.0, "barrel"), (262.0, 55.0, "crate"),
             (140.0, 96.0, "bucket"), (280.0, 34.0, "paling")]
    for i, (x, y, kind) in enumerate(drops):
        z = bed + 0.4
        if kind == "crate":
            geo.box(f"DROP_{i+1:02d}", x, y, z, x + 0.8, y + 0.6, z + 0.5, M["timber_dark"], C)
        elif kind == "barrel":
            geo.cyl(f"DROP_{i+1:02d}", x, y, z, 0.32, 0.85, M["rust"], C, seg=12)
        elif kind == "wheel":
            geo.cyl(f"DROP_{i+1:02d}", x, y, z, 0.55, 0.16, M["iron"], C, seg=14)
        elif kind == "chain":
            for k in range(6):
                geo.torus = None
                geo.cyl(f"DROP_{i+1:02d}_{k}", x + k * 0.22, y, z + 0.05 * (k % 2), 0.045, 0.20,
                        M["rust"], C, seg=8, axis="X")
        elif kind == "bucket":
            geo.cyl(f"DROP_{i+1:02d}", x, y, z, 0.16, 0.30, M["rust"], C, seg=12, r_top=0.20)
        else:
            geo.box(f"DROP_{i+1:02d}", x, y, z, x + 2.2, y + 0.10, z + 0.10, M["timber_pale"], C,
                    rot_z=0.6)
    # water surface: displaced grid, slight swell
    def ripple(x, y):
        return (0.016 * math.sin(2 * math.pi * x / 7.5 + 0.4) +
                0.011 * math.sin(2 * math.pi * y / 1.1 + 1.1) +
                0.005 * math.sin(2 * math.pi * (x + y) / 0.13))
    geo.grid_plane("WATER_SURFACE", bx0 + 0.02, by0 + 0.02, bx1 - 0.02, by1 - 0.02,
                   P.WATER_Z, M["water"], C, nx=150, ny=75, disp=ripple)
    # ice at the shadowed edges only (north and west), above the waterline
    rng = random.Random(7)
    for i in range(30):
        if i < 16:
            x = bx0 + 1.0 + rng.uniform(0, 55)
            y = by1 - rng.uniform(0.5, 3.0)
        else:
            x = bx0 + rng.uniform(0.5, 2.4)
            y = by0 + 1.0 + rng.uniform(0, 70)
        w, d = rng.uniform(0.5, 2.6), rng.uniform(0.4, 1.7)
        th = rng.uniform(0.018, 0.075)
        geo.box(f"ICE_{i+1:02d}", x, y, P.WATER_Z + 0.002, x + w, y + d,
                P.WATER_Z + 0.002 + th, M["ice"], C)
    # foam within 150 mm of every waterline contact
    rngf = random.Random(11)
    n = 0
    for i in range(40):
        x = bx0 + 2 + (bx1 - bx0 - 4) * (i / 40.0)
        n += 1
        geo.box(f"FOAM_{n:03d}", x, by0 - 0.02, P.WATER_Z + 0.004, x + 1.4, by0 + 0.13,
                P.WATER_Z + 0.016, M["foam"], C)
    for i in range(40):
        x = bx0 + 2 + (bx1 - bx0 - 4) * (i / 40.0)
        n += 1
        geo.box(f"FOAM_{n:03d}", x, by1 - 0.11, P.WATER_Z + 0.004, x + 1.4, by1 + 0.02,
                P.WATER_Z + 0.016, M["foam"], C)
    for i in range(24):                                    # along the moored hull
        y = by0 + 10 + (by1 - by0 - 20) * i / 24.0
        n += 1
        geo.box(f"FOAM_{n:03d}", 119.9, y, P.WATER_Z + 0.03, 120.9, y + 2.2,
                P.WATER_Z + 0.045, M["foam"], C)
    log(f"water: surface, bed + 8 dropped objects, 30 ice plates, {n} foam strips")


# ── quay walls, coping, ladders, bollards, fenders, stair ──────────────────
BOLLARDS = []


def build_quay(M):
    C = geo.coll("QUAY")
    bx0, by0, bx1, by1 = P.BASIN
    top, bed = P.LAND_Z, P.WATER_Z - P.BASIN_DEPTH
    t = 0.60
    # wall faces of the basin
    geo.box("QUAY_N", bx0 - t, by1 - t, bed, bx1 + t, by1, top, M["stone"], C)
    geo.box("QUAY_S", bx0 - t, by0, bed, bx1 + t, by0 + t, top, M["stone"], C)
    geo.box("QUAY_W", bx0 - t, by0, bed, bx0, by1, top, M["stone"], C)
    geo.box("QUAY_E", bx1, by0, bed, bx1 + t, by1, top, M["stone"], C)
    # granite coping along every edge
    for (x0, y0, x1, y1) in ((bx0 - 0.85, by1 - 0.85, bx1 + 0.85, by1),
                             (bx0 - 0.85, by0, bx1 + 0.85, by0 + 0.85),
                             (bx0 - 0.85, by0, bx0, by1), (bx1, by0, bx1 + 0.85, by1)):
        geo.box("COPING", x0, y0, top, x1, y1, top + 0.14, M["stone"], C)
    # ladders, fenders and bollards
    ladder_x = [120.0, 168.0, 216.0, 264.0]
    for i, x in enumerate(ladder_x):
        for k in range(9):
            geo.box(f"LADDER_{i+1}_rung{k}", x, by1 - 0.34, -1.9 + k * 0.42, x + 0.5,
                    by1 - 0.30, -1.86 + k * 0.42, M["steel_dark"], C)
        geo.box(f"LADDER_{i+1}_a", x, by1 - 0.36, -2.2, x + 0.04, by1 - 0.30, top,
                M["steel_dark"], C)
        geo.box(f"LADDER_{i+1}_b", x + 0.46, by1 - 0.36, -2.2, x + 0.50, by1 - 0.30, top,
                M["steel_dark"], C)
    for i in range(14):
        x = bx0 + 6 + i * 12.0
        geo.cyl(f"FENDER_{i+1:02d}", x, by1 - 0.09, -0.55, 0.34, 0.18, M["rust"], C,
                seg=14, axis="Z")
        geo.box(f"FENDERBRK_{i+1:02d}", x - 0.05, by1 - 0.02, -0.60, x + 0.05, by1 + 0.02, -0.20,
                M["steel_dark"], C)
    # bollards: north quay at y=120.5, west at x=110.5, south at y=29.5
    n = 0
    for x in [114 + 8 * k for k in range(22)]:
        if bx0 + 2 < x < bx1 - 2:
            _bollard(M, C, x, by1 + 0.5, "N")
            n += 1
    for y in [34 + 8 * k for k in range(11)]:
        _bollard(M, C, bx0 - 0.5, y, "W")
        n += 1
    for x in [114 + 8 * k for k in range(22)]:
        if bx0 + 2 < x < bx1 - 2:
            _bollard(M, C, x, by0 - 0.5, "S")
            n += 1
    # quay stair from the apron down to the water
    sx, sy = bx0 + 3.0, by1 - 0.9
    for k in range(12):
        geo.box(f"QSTAIR_{k:02d}", sx, sy - k * 0.30, top - (k + 1) * 0.175, sx + 1.4, sy - k * 0.30 + 0.30,
                top - k * 0.175, M["stone"], C)
    log(f"quay: walls, coping, {len(ladder_x)} ladders, 14 fenders, {n} bollards, stair")


def _bollard(M, C, x, y, side):
    BOLLARDS.append((x, y))
    geo.cyl("BOLLARD_base", x, y, P.LAND_Z, 0.28, 0.10, M["iron"], C, seg=14, r_top=0.24)
    geo.cyl("BOLLARD_shaft", x, y, P.LAND_Z + 0.10, 0.19, 0.52, M["iron"], C, seg=14, r_top=0.21)
    geo.cyl("BOLLARD_head", x, y, P.LAND_Z + 0.62, 0.26, 0.10, M["iron"], C, seg=14, r_top=0.16)


# ── buildings: massing, roofs, and B05 in full ─────────────────────────────
def _gable_roof(name, x0, y0, x1, y1, z, pitch_deg, mat, C, along="x"):
    """Two sloped faces + two gable triangles, as one closed prism."""
    rise = math.tan(math.radians(pitch_deg)) * min(x1 - x0, y1 - y0) / 2.0
    if along == "x":
        cy = (y0 + y1) / 2.0
        v = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z),
             (x0, cy, z + rise), (x1, cy, z + rise)]
        f = [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)]
    else:
        cx = (x0 + x1) / 2.0
        v = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z),
             (cx, y0, z + rise), (cx, y1, z + rise)]
        f = [(0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.validate(verbose=False)
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    C.objects.link(ob)
    return ob


def facade_band(name, x0, y0, x1, y1, z0, z1, mat, C, side, module, win_w=1.10,
                win_h=1.45, sill=0.85, proud=0.0):
    """One storey of wall with a run of windows punched out of it, merged into a
    single object: piers, sill band, lintel band."""
    parts = []
    wins = []
    if side in ("S", "N"):
        y = (y0 - proud) if side == "S" else (y1 - 0.45 + proud)
        length = x1 - x0
        n = max(1, int(length / module))
        pitch = length / n
        ww = min(win_w, pitch * 0.62)
        parts.append((x0, y, z0, x1, y + 0.45, z0 + sill))
        parts.append((x0, y, z0 + sill + win_h, x1, y + 0.45, z1))
        cx = x0
        for i in range(n):
            mid = x0 + pitch * (i + 0.5)
            parts.append((cx, y, z0 + sill, mid - ww / 2, y + 0.45, z0 + sill + win_h))
            wins.append((mid - ww / 2, mid + ww / 2, z0 + sill, z0 + sill + win_h))
            cx = mid + ww / 2
        if cx < x1 - 0.05:
            parts.append((cx, y, z0 + sill, x1, y + 0.45, z0 + sill + win_h))
    else:
        x = (x0 - proud) if side == "W" else (x1 - 0.45 + proud)
        length = y1 - y0
        n = max(1, int(length / module))
        pitch = length / n
        ww = min(win_w, pitch * 0.62)
        parts.append((x, y0, z0, x + 0.45, y1, z0 + sill))
        parts.append((x, y0, z0 + sill + win_h, x + 0.45, y1, z1))
        cy = y0
        for i in range(n):
            mid = y0 + pitch * (i + 0.5)
            parts.append((x, cy, z0 + sill, x + 0.45, mid - ww / 2, z0 + sill + win_h))
            wins.append((mid - ww / 2, mid + ww / 2, z0 + sill, z0 + sill + win_h))
            cy = mid + ww / 2
        if cy < y1 - 0.05:
            parts.append((x, cy, z0 + sill, x + 0.45, y1, z0 + sill + win_h))
    gl, rv = [], []
    if side in ("S", "N"):
        yg = (y0 - proud) + 0.22 if side == "S" else (y1 - 0.45 + proud) + 0.22
        for (a, b, c0, c1) in wins:
            gl.append((a + 0.02, yg - 0.006, c0 + 0.02, b - 0.02, yg + 0.006, c1 - 0.02))
            rv.append((a - 0.01, yg + 0.02, c0 - 0.01, b + 0.01, yg + 0.30, c1 + 0.01))
    else:
        xg = (x0 - proud) + 0.22 if side == "W" else (x1 - 0.45 + proud) + 0.22
        for (a, b, c0, c1) in wins:
            gl.append((xg - 0.006, a + 0.02, c0 + 0.02, xg + 0.006, b - 0.02, c1 - 0.02))
            rv.append((xg + 0.02, a - 0.01, c0 - 0.01, xg + 0.30, b + 0.01, c1 + 0.01))
    return parts, gl, rv



def city_fringe(M, C):
    """Low-detail blocks outside the site, deterministic, no interiors."""
    rng = random.Random(int(hashlib.sha256(b"portus-fringe").hexdigest()[:8], 16))
    made = 0
    bands = [(-190, -70, -70, 390), (470, 590, -70, 390), (-190, 390, 590, 500), (-190, -190, 590, -70)]
    for (ax0, ay0, ax1, ay1) in bands:
        x = ax0
        while x < ax1 - 12:
            y = ay0
            w = rng.uniform(18, 34)
            while y < ay1 - 12:
                d = rng.uniform(16, 30)
                h = rng.uniform(10, 26)
                mat = ["brick_dark", "concrete", "stone", "brick_dark"][made % 4]
                geo.box(f"FRINGE_{made:04d}", x + 2, y + 2, -6.0, x + w - 2, y + d - 2, h, M[mat], C)
                made += 1
                y += d + rng.uniform(4, 12)
            x += w + rng.uniform(6, 16)
    return made


def party_piers(specs, M, C):
    """Close the joints of every terrace with a pilaster on the joint line."""
    made = 0
    by_block = {}
    for s in specs:
        by_block.setdefault(s["block"], []).append(s)
    for block, group in by_block.items():
        group = sorted(group, key=lambda s: (s["y0"], s["x0"]))
        for i in range(len(group) - 1):
            a, b = group[i], group[i + 1]
            heights = P.building_height(a)
            # x-terrace: a ends where b begins
            if abs(a["x1"] - b["x0"]) < 0.25 and abs(a["y0"] - b["y0"]) < 0.25:
                x = (a["x1"] + b["x0"]) / 2
                geo.box(f"PARTYWALL_{a['id']}_{b['id']}", x - 0.22, a["y0"] - 0.06, P.LAND_Z,
                        x + 0.22, a["y0"] + 0.60, P.LAND_Z + min(heights, P.building_height(b)),
                        M["brick_dark"], C)
                made += 1
            # y-terrace
            elif abs(a["y1"] - b["y0"]) < 0.25 and abs(a["x0"] - b["x0"]) < 0.25:
                y = (a["y1"] + b["y0"]) / 2
                geo.box(f"PARTYWALL_{a['id']}_{b['id']}", a["x0"] - 0.06, y - 0.22, P.LAND_Z,
                        a["x0"] + 0.60, y + 0.22, P.LAND_Z + min(heights, P.building_height(b)),
                        M["brick_dark"], C)
                made += 1
    return made


def mass_building(spec, M, C, z):
    """Structure + envelope + roof for one building; B05 is built separately."""
    x0, y0, x1, y1 = spec["x0"], spec["y0"], spec["x1"], spec["y1"]
    wt = P.EXT_WALL.get(spec["wall"], 0.45)
    wall_mat = M[spec["wall"] if spec["wall"] in M else "brick"]
    ffls = P.floor_levels(spec)
    bid = spec["id"]
    H = P.building_height(spec)
    geo.box(f"{bid}_CORE", x0 + 0.30, y0 + 0.30, P.LAND_Z, x1 - 0.30, y1 - 0.30,
            P.LAND_Z + H, M["stone"], C)
    # core massing: floor slabs and every facade band
    wall_parts, glass_parts, reveal_parts = [], [], []
    for li, st in enumerate(spec["storeys"]):
        zz = ffls[li]
        geo.box(f"{bid}_SLAB_L{li+1}", x0, y0, zz - P.SLAB, x1, y1, zz, M["concrete"], C)
        for side in ("S", "N", "W", "E"):
            wp, gp, rp = facade_band(f"{bid}_F{side}_L{li+1}", x0, y0, x1, y1, zz,
                                     zz + st["h"], wall_mat, C, side,
                                     max(1.2, spec["module"]), proud=0.003 * (li % 2))
            wall_parts += wp
            glass_parts += gp
            reveal_parts += rp
    if wall_parts:
        geo.merged(f"{bid}_FACADES", wall_parts, wall_mat, C)
        geo.merged(f"{bid}_GLAZING", glass_parts, M_GLASS, C)
        geo.merged(f"{bid}_ROOMS_BEHIND", reveal_parts, M_DARK, C)
    # roof
    top = ffls[-1] + spec["storeys"][-1]["h"]
    kind = spec["roof"]
    geo.box(f"{bid}_PARAPET", x0 - 0.05, y0 - 0.05, top, x1 + 0.05, y1 + 0.05, top + 0.35,
            M["stone"], C)
    if kind in ("flat", "monitor"):
        geo.box(f"{bid}_ROOF", x0, y0, top, x1, y1, top + 0.25, M["asphalt"], C)
    elif kind == "glass":
        _gable_roof(f"{bid}_ROOF", x0, y0, x1, y1, top, min(25, spec["pitch"]), M["glass"], C,
                    along="x" if (x1 - x0) >= (y1 - y0) else "y")
    elif kind == "mansard":
        geo.box(f"{bid}_MANSARD", x0, y0, top, x1, y1, top + 1.2, M["slate"], C)
        _gable_roof(f"{bid}_ROOF", x0 + 1.0, y0 + 1.0, x1 - 1.0, y1 - 1.0, top + 1.2, 30,
                    M["slate"], C, along="x" if (x1 - x0) >= (y1 - y0) else "y")
    elif kind == "shed":
        geo.box(f"{bid}_ROOF", x0, y0, top, x1, y1, top + 0.3, M["slate"], C)
    else:
        _gable_roof(f"{bid}_ROOF", x0, y0, x1, y1, top, spec["pitch"], M[spec["roof"]]
                    if spec["roof"] in M else M["slate"], C,
                    along="x" if (x1 - x0) >= (y1 - y0) else "y")
    # chimney stack so roofs are not bare
    geo.box(f"{bid}_CHIMNEY", (x0 + x1) / 2 + 1.0, y0 + 1.2, top + 0.2, (x0 + x1) / 2 + 1.9,
            y0 + 1.9, top + 2.4, M["brick_dark"], C)
    return H


# ── B05 in full ────────────────────────────────────────────────────────────
def _emit(parts, rect):
    """Append only a box with three positive dimensions (zero-area guard)."""
    if (abs(rect[3] - rect[0]) > 1e-4 and abs(rect[4] - rect[1]) > 1e-4
            and abs(rect[5] - rect[2]) > 1e-4):
        parts.append(rect)


def wall_panel(name, x0, y0, x1, y1, z0, h, thick, side, mat, C, holes=()):
    """A wall panel with rectangular holes (door/window). Built as a set of boxes
    in the panel plane; holes are (u0, u1, v0, v1) in metres along the wall."""
    parts = []
    if side in ("S", "N"):
        y = y0 if side == "S" else y1 - thick
        length = x1 - x0
        spans = [(0.0, length)]
        for (u0, u1, v0, v1) in holes:
            xa, xb = x0 + u0, x0 + u1
            _emit(parts, (xa, y, z0, xb, y + thick, z0 + v0))          # under
            _emit(parts, (xa, y, z0 + v1, xb, y + thick, z0 + h))      # over
        # piers between holes
        hs = sorted([(u0, u1) for (u0, u1, v0, v1) in holes])
        cur = 0.0
        for (u0, u1) in hs:
            if u0 > cur:
                _emit(parts, (x0 + cur, y, z0, x0 + u0, y + thick, z0 + h))
            cur = max(cur, u1)
        if cur < length:
            _emit(parts, (x0 + cur, y, z0, x0 + length, y + thick, z0 + h))
    else:
        x = x0 if side == "W" else x1 - thick
        length = y1 - y0
        for (u0, u1, v0, v1) in holes:
            ya, yb = y0 + u0, y0 + u1
            _emit(parts, (x, ya, z0, x + thick, yb, z0 + v0))
            _emit(parts, (x, ya, z0 + v1, x + thick, yb, z0 + h))
        hs = sorted([(u0, u1) for (u0, u1, v0, v1) in holes])
        cur = 0.0
        for (u0, u1) in hs:
            if u0 > cur:
                _emit(parts, (x, y0 + cur, z0, x + thick, y0 + u0, z0 + h))
            cur = max(cur, u1)
        if cur < length:
            _emit(parts, (x, y0 + cur, z0, x + thick, y0 + length, z0 + h))
    return geo.merged(name, parts, mat, C)


def glaze_envelope(spec, M, C, holes_by_level, ffls):
    """A punched opening with nothing in it reads as a cave. Every envelope hole
    gets a reveal, a frame and a pane at mid-wall."""
    wt = P.EXT_WALL.get(spec["wall"], 0.45)
    x0, y0, x1, y1 = spec["x0"], spec["y0"], spec["x1"], spec["y1"]
    n = 0
    for (li, side), hs in holes_by_level.items():
        z = ffls[li]
        for (u0, u1, v0, v1) in hs:
            if side in ("S", "N"):
                ya = y0 if side == "S" else y1 - wt
                yb = ya + wt
                geo.box(f"{spec['id']}_REVEAL_{side}_{n}", x0 + u0, ya - 0.03, z + v0,
                        x0 + u1, yb + 0.03, z + v0 + 0.06, M["stone"], C)     # cill
                geo.box(f"{spec['id']}_PANE_{side}_{n}", x0 + u0 + 0.02, ya + wt * 0.45,
                        z + v0 + 0.05, x0 + u1 - 0.02, ya + wt * 0.45 + 0.012, z + v1 - 0.02,
                        M["glass"], C)
                geo.box(f"{spec['id']}_FRAME_{side}_{n}_t", x0 + u0, ya, z + v1 - 0.05,
                        x0 + u1, yb, z + v1, M["paint_white"], C)
                geo.box(f"{spec['id']}_FRAME_{side}_{n}_b", x0 + u0, ya, z + v0,
                        x0 + u1, yb, z + v0 + 0.05, M["paint_white"], C)
                geo.box(f"{spec['id']}_FRAME_{side}_{n}_m", (x0 + u0 + x0 + u1) / 2 - 0.025, ya,
                        z + v0, (x0 + u0 + x0 + u1) / 2 + 0.025, yb, z + v1, M["paint_white"], C)
            else:
                xa = x0 if side == "W" else x1 - wt
                xb = xa + wt
                geo.box(f"{spec['id']}_REVEAL_{side}_{n}", xa - 0.03, y0 + u0, z + v0,
                        xb + 0.03, y0 + u1, z + v0 + 0.06, M["stone"], C)
                geo.box(f"{spec['id']}_PANE_{side}_{n}", xa + wt * 0.45, y0 + u0 + 0.02,
                        z + v0 + 0.05, xa + wt * 0.45 + 0.012, y0 + u1 - 0.02, z + v1 - 0.02,
                        M["glass"], C)
                geo.box(f"{spec['id']}_FRAME_{side}_{n}_t", xa, y0 + u0, z + v1 - 0.05,
                        xb, y0 + u1, z + v1, M["paint_white"], C)
                geo.box(f"{spec['id']}_FRAME_{side}_{n}_b", xa, y0 + u0, z + v0,
                        xb, y0 + u1, z + v0 + 0.05, M["paint_white"], C)
                geo.box(f"{spec['id']}_FRAME_{side}_{n}_m", xa, (y0 + u0 + y0 + u1) / 2 - 0.025,
                        z + v0, xb, (y0 + u0 + y0 + u1) / 2 + 0.025, z + v1, M["paint_white"], C)
            n += 1
    return n


def build_b05(spec, M, rooms, C):
    """Shop + 4 residential floors, every counted room built and dressed."""
    x0, y0, x1, y1 = spec["x0"], spec["y0"], spec["x1"], spec["y1"]
    bid = spec["id"]
    wt = P.EXT_WALL.get(spec["wall"], 0.45)
    ffls = P.floor_levels(spec)
    # envelope: punched where the rooms' own windows are
    holes_by_level = {}
    for r in rooms:
        w = r["window"]
        if not w:
            continue
        li = _level_of(r)
        holes_by_level.setdefault((li, _side_of(r, spec, w)), []).append(
            _hole_along_wall(r, spec, w))
    for li, st in enumerate(spec["storeys"]):
        zz = ffls[li]
        for side in ("S", "N", "W", "E"):
            hs = holes_by_level.get((li, side), [])
            hs = [h for h in hs if h[3] <= st["h"]]
            wall_panel(f"{bid}_ENV{side}_L{li+1}", x0, y0, x1, y1, zz,
                       st["h"], wt, side,
                       M[spec["wall"] if spec["wall"] in M else "brick"], C,
                       holes=hs)
        geo.box(f"{bid}_SLAB_L{li+1}", x0 + wt, y0 + wt, zz - P.SLAB, x1 - wt, y1 - wt, zz,
                M["concrete"], C)
        log(f"  B05 envelope, level {li+1}: {len(holes_by_level.get((li,'S'),[])) + len(holes_by_level.get((li,'N'),[])) + len(holes_by_level.get((li,'W'),[])) + len(holes_by_level.get((li,'E'),[]))} openings")
    # light slot linings: the slot runs the full depth at the mid-point of the
    # frontage; without a lining it renders as a void (D-213)
    to_xy, width, depth = P._u_v_axes(spec)
    wt0 = P.EXT_WALL.get(spec["wall"], 0.45)
    mid = width / 2.0
    sl0, sl1 = mid - P.SLOT_W / 2.0, mid + P.SLOT_W / 2.0
    for li, st in enumerate(spec["storeys"]):
        zz = ffls[li]
        if li == 0:
            continue                       # ground floor is solid across the slot
        for name, (u0, u1) in (("W", (sl0 - 0.06, sl0)), ("E", (sl1, sl1 + 0.06))):
            ax0, ay0 = to_xy(u0, wt0)
            ax1, ay1 = to_xy(u1, depth - wt0)
            geo.box(f"{bid}_SLOTLINING_{name}_L{li+1}", min(ax0, ax1), min(ay0, ay1),
                    zz, max(ax0, ax1), max(ay0, ay1), zz + st["h"], M["plaster_cool"], C)
        # a slot floor at every level so the shaft is not a bottomless pit
        ax0, ay0 = to_xy(sl0, wt0)
        ax1, ay1 = to_xy(sl1, depth - wt0)
        geo.box(f"{bid}_SLOTFLOOR_L{li+1}", min(ax0, ax1), min(ay0, ay1), zz - 0.05,
                max(ax0, ax1), max(ay0, ay1), zz, M["concrete"], C)
    n_glazed = glaze_envelope(spec, M, C, holes_by_level, ffls)
    log(f"B05: {n_glazed} windows glazed in the envelope")
    # roof
    top = ffls[-1] + spec["storeys"][-1]["h"]
    _gable_roof(f"{bid}_ROOF", x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3, top, 34, M["clay"], C)
    geo.box(f"{bid}_CORNICE", x0 - 0.12, y0 - 0.12, top - 0.10, x1 + 0.12, y1 + 0.12, top + 0.14,
            M["stone"], C)
    # interiors
    n_rooms = 0
    for r in rooms:
        build_room(r, spec, M, C)
        n_rooms += 1
    log(f"B05: {n_rooms} rooms built and dressed")
    if OUTSIDE:
        log(f"INVARIANT FAIL: {len(OUTSIDE)} rooms have props outside their walls")
        for rid, n, ex in OUTSIDE[:6]:
            log(f"  {rid}: {n} out, e.g. {ex}")
    else:
        log("invariant: every prop sits inside its own room")


def _level_of(r):
    return int(r["level"]) - 1


def _side_of(r, spec, w):
    return w.get("side", "S")


def _hole_along_wall(r, spec, w):
    """Convert a window dict to (u0, u1, v0, v1) along its wall."""
    side = w["side"]
    if side in ("S", "N"):
        u = w["x"] - spec["x0"]
        return (max(0.0, u), min(spec["x1"] - spec["x0"], u + w["w"]),
                w["sill"], w["sill"] + w["h"])
    u = w["y"] - spec["y0"]
    return (max(0.0, u), min(spec["y1"] - spec["y0"], u + w["w"]),
            w["sill"], w["sill"] + w["h"])


ROOM_PROPS = {}
M_GLASS = None
M_DARK = None
OUTSIDE = []


def build_room(r, spec, M, C):
    """Floor, ceiling, four linings with openings, door leaf, window, furniture."""
    R = geo.coll("ROOMS")
    z = r["level_z"]
    w, d = r["w"], r["d"]
    x0, y0 = r["x0"], r["y0"]
    rid = r["id"]
    is_shop = r["kind"] == "shop_room"
    floor_mat = M["tile"] if is_shop else M["wood_floor"]
    geo.box(f"ROOM_{rid}_floor", x0, y0, z, x0 + w, y0 + d, z + 0.02, floor_mat, R)
    geo.box(f"ROOM_{rid}_ceiling", x0, y0, z + P.RES_CEILING - 0.02, x0 + w, y0 + d,
            z + P.RES_CEILING, M["plaster"], R)
    # linings: thin panels on all four sides, holes for this room's openings
    holes = {s: [] for s in ("S", "N", "W", "E")}
    doors = r.get("door")
    if doors:
        side = doors["side"]
        if side in ("S", "N"):
            u = doors["x"] - x0
        else:
            u = doors["y"] - y0
        holes[side].append((max(0.0, u), min(w if side in ("S", "N") else d, u + doors["w"]),
                            0.0, doors["h"]))
    wdw = r.get("window")
    if wdw:
        side = wdw["side"]
        if side in ("S", "N"):
            u = wdw["x"] - x0
            span = w
        else:
            u = wdw["y"] - y0
            span = d
        holes[side].append((max(0.0, u), min(span, u + wdw["w"]),
                            wdw["sill"], wdw["sill"] + wdw["h"]))
    thick = 0.06
    for side in ("S", "N", "W", "E"):
        wall_panel(f"ROOM_{rid}_lining_{side}", x0, y0, x0 + w, y0 + d, z,
                   P.RES_CEILING - 0.02, thick, side, M["plaster"], R, holes=holes[side])
    # window: frame, glass, sill
    if wdw:
        _window_fit(f"ROOM_{rid}", wdw, z, M, R)
    # door: frame + leaf standing open against the wall (D-107 keeps the passage clear)
    if doors:
        _door_fit(f"ROOM_{rid}", doors, z, M, R)
    # furniture
    rng = random.Random(int(hashlib.sha256(f"{rid}:{r['name']}".encode()).hexdigest()[:8], 16))
    palette = {"sofa": ["fabric_red", "fabric_green", "fabric_blue"][hashlib.sha256(rid.encode()).digest()[0] % 3],
               "rug": ["fabric_ochre", "fabric_green", "fabric_blue"][hashlib.sha256(rid.encode()).digest()[1] % 3],
               "bed": ["fabric_blue", "fabric_green", "fabric_ochre"][hashlib.sha256(rid.encode()).digest()[2] % 3],
               "curtain": "fabric_grey"}
    kind = "sales" if r["name"] == "sales" else r["name"]
    target = {"living": 70, "kitchen": 90, "bedroom": 40, "bathroom": 28, "entry": 18,
              "sales": 150, "stock": 46, "staff": 14, "wc": 6}.get(kind)
    helper = props.furnish(dict(id=rid, x0=x0, y0=y0, x1=x0 + w, y1=y0 + d, w=w, d=d),
                           kind, palette, R, M, rng, z, door=r.get("door"), target=target)
    ROOM_PROPS[rid] = helper.n
    # invariant: no piece of furniture may end up outside its own room. This is
    # the check that would have caught the local/world mix-up in one build.
    outside = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.name.startswith(f"ROOM_{rid}_"):
            continue
        if any(t in ob.name for t in ("doorframe", "doorhead", "doorleaf", "sill",
                                      "winfram", "glass", "lining", "ceiling", "floor")):
            continue
        if True:
            b = geo.world_bounds(ob)
            if (b[0] < x0 - 0.02 or b[1] < y0 - 0.02 or b[3] > x0 + w + 0.02
                    or b[4] > y0 + d + 0.02):
                outside.append(ob.name)
    if outside:
        OUTSIDE.append((rid, len(outside), outside[:3]))
    # a practical: warm lamp at ceiling centre, 2700 K (G5 wants 2 sources a room;
    # the second is the window or the corridor spill)
    _room_lamp(f"ROOM_{rid}", x0 + w * 0.5, y0 + d * 0.5, z + P.RES_CEILING - 0.12, M, R)


def _window_fit(prefix, wdw, z, M, C):
    side = wdw["side"]
    shelf = z + wdw["sill"]
    if side in ("S", "N"):
        y = wdw["y"]
        geo.box(f"{prefix}_winfram", wdw["x"], y - 0.05, shelf, wdw["x"] + wdw["w"], y + 0.05,
                shelf + 0.06, M["timber_pale"], C)
        geo.box(f"{prefix}_winfram_t", wdw["x"], y - 0.05, shelf + wdw["h"] - 0.06, wdw["x"] + wdw["w"],
                y + 0.05, shelf + wdw["h"], M["timber_pale"], C)
        geo.box(f"{prefix}_winfram_l", wdw["x"], y - 0.05, shelf, wdw["x"] + 0.06, y + 0.05,
                shelf + wdw["h"], M["timber_pale"], C)
        geo.box(f"{prefix}_winfram_r", wdw["x"] + wdw["w"] - 0.06, y - 0.05, shelf,
                wdw["x"] + wdw["w"], y + 0.05, shelf + wdw["h"], M["timber_pale"], C)
        geo.box(f"{prefix}_glass", wdw["x"] + 0.05, y - 0.012, shelf + 0.05,
                wdw["x"] + wdw["w"] - 0.05, y + 0.012, shelf + wdw["h"] - 0.05, M["glass"], C)
        geo.box(f"{prefix}_sill", wdw["x"] - 0.05, y - 0.10, shelf - 0.04, wdw["x"] + wdw["w"] + 0.05,
                y + 0.08, shelf, M["stone"], C)
    else:
        x = wdw["x"]
        geo.box(f"{prefix}_winfram", x - 0.05, wdw["y"], shelf, x + 0.05, wdw["y"] + wdw["w"],
                shelf + 0.06, M["timber_pale"], C)
        geo.box(f"{prefix}_winfram_t", x - 0.05, wdw["y"], shelf + wdw["h"] - 0.06, x + 0.05,
                wdw["y"] + wdw["w"], shelf + wdw["h"], M["timber_pale"], C)
        geo.box(f"{prefix}_winfram_l", x - 0.05, wdw["y"], shelf, x + 0.05, wdw["y"] + 0.06,
                shelf + wdw["h"], M["timber_pale"], C)
        geo.box(f"{prefix}_winfram_r", x - 0.05, wdw["y"] + wdw["w"] - 0.06, shelf, x + 0.05,
                wdw["y"] + wdw["w"], shelf + wdw["h"], M["timber_pale"], C)
        geo.box(f"{prefix}_glass", x - 0.012, wdw["y"] + 0.05, shelf + 0.05, x + 0.012,
                wdw["y"] + wdw["w"] - 0.05, shelf + wdw["h"] - 0.05, M["glass"], C)
        geo.box(f"{prefix}_sill", x - 0.10, wdw["y"] - 0.05, shelf - 0.04, x + 0.08,
                wdw["y"] + wdw["w"] + 0.05, shelf, M["stone"], C)


def _door_fit(prefix, door, z, M, C):
    side, w = door["side"], door["w"]
    h = door["h"]
    if side in ("S", "N"):
        y = door["y"]
        x0 = door["x"]
        geo.box(f"{prefix}_doorframe_l", x0 - 0.06, y - 0.05, z, x0, y + 0.05, z + h + 0.06,
                M["timber_dark"], C)
        geo.box(f"{prefix}_doorframe_r", x0 + w, y - 0.05, z, x0 + w + 0.06, y + 0.05,
                z + h + 0.06, M["timber_dark"], C)
        geo.box(f"{prefix}_doorhead", x0 - 0.06, y - 0.05, z + h, x0 + w + 0.06, y + 0.05,
                z + h + 0.06, M["timber_dark"], C)
        # leaf standing open, flat against the wall (its swing is not in the passage)
        dx0 = x0 + w + 0.04 if x0 + w + 0.04 + w < 1e9 else x0
        geo.box(f"{prefix}_doorleaf", dx0, y + 0.05, z, dx0 + w, y + 0.09, z + h,
                M["timber"], C)
    else:
        x = door["x"]
        y0 = door["y"]
        geo.box(f"{prefix}_doorframe_l", x - 0.05, y0 - 0.06, z, x + 0.05, y0, z + h + 0.06,
                M["timber_dark"], C)
        geo.box(f"{prefix}_doorframe_r", x - 0.05, y0 + w, z, x + 0.05, y0 + w + 0.06,
                z + h + 0.06, M["timber_dark"], C)
        geo.box(f"{prefix}_doorhead", x - 0.05, y0 - 0.06, z + h, x + 0.05, y0 + w + 0.06,
                z + h + 0.06, M["timber_dark"], C)
        geo.box(f"{prefix}_doorleaf", x + 0.05, y0 + w + 0.04, z, x + 0.09, y0 + w + 0.04 + w,
                z + h, M["timber"], C)


def _room_lamp(prefix, x, y, z, M, C):
    geo.cyl(f"{prefix}_lampcord", x, y, z - 0.35, 0.012, 0.35, M["iron"], C, seg=14)
    geo.cyl(f"{prefix}_lampshade", x, y, z - 0.42, 0.20, 0.16, M["lamp_warm"], C, seg=14,
            r_top=0.07)
    li = bpy.data.lights.new(f"{prefix}_practical", "POINT")
    li.energy = 42.0
    li.color = (1.0, 0.79, 0.56)            # ~2700 K
    li.shadow_soft_size = 0.22
    ob = bpy.data.objects.new(f"{prefix}_practical", li)
    ob.location = (x, y, z - 0.45)
    C.objects.link(ob)


# ── rail ───────────────────────────────────────────────────────────────────
def build_rail(M, sysd):
    C = geo.coll("RAIL")
    y = 141.0
    x0, x1 = 296.0, 316.0
    geo.box("BALLAST", x0 - 4, y - 2.2, P.LAND_Z, x1, y + 2.2, P.LAND_Z + 0.32, M["ballast"], C)
    n = int((x1 - x0) / 0.60) + 1
    for i in range(n):
        xx = x0 + i * 0.60
        geo.box(f"SLEEPER_{i:03d}", xx - 0.13, y - 1.30, P.LAND_Z + 0.32, xx + 0.13, y + 1.30,
                P.LAND_Z + 0.46, M["timber_dark"], C)
    rail_z = P.LAND_Z + 0.46
    for side, yy in (("N", y + 0.7175), ("S", y - 0.7175)):
        geo.box(f"RAIL_{side}_foot", x0 - 3.0, yy - 0.075, rail_z, x1, yy + 0.075, rail_z + 0.03,
                M["steel"], C)
        geo.box(f"RAIL_{side}_web", x0 - 3.0, yy - 0.014, rail_z + 0.03, x1, yy + 0.014,
                rail_z + 0.14, M["steel"], C)
        geo.box(f"RAIL_{side}_head", x0 - 3.0, yy - 0.035, rail_z + 0.14, x1, yy + 0.035,
                rail_z + 0.17, M["steel"], C)
    # catenary: masts, bracket, contact wire at 5.50 above rail head
    wire_z = rail_z + 0.17 + 5.50
    wx0, wx1 = x0 - 2, x0 + 18
    for i in range(3):
        xx = wx0 + 0.08 + i * 10.0
        geo.box(f"MAST_{i}", xx - 0.12, y + 2.0, P.LAND_Z, xx + 0.12, y + 2.24, P.LAND_Z + 7.4,
                M["steel_dark"], C)
        geo.box(f"BRACKET_{i}", xx - 0.06, y - 0.2, P.LAND_Z + 6.9, xx + 0.06, y + 2.1,
                P.LAND_Z + 7.0, M["steel_dark"], C)

    # the wire spans mast to mast (x0-2 .. x0+18) and each end is clamped to an
    # anchor block, so no wire ends in the air (v_plant rule)
    geo.box("CATENARY_WIRE", wx0, y - 0.012, wire_z - 0.012, wx1, y + 0.012, wire_z + 0.012,
            M["steel_dark"], C)
    for i, ax in enumerate((wx0 - 0.16, wx1)):
        geo.box(f"CATENARY_ANCHOR_{i}", ax, y - 0.20, wire_z - 0.35, ax + 0.16, y + 0.20,
                wire_z + 0.20, M["steel_dark"], C)
    geo.box("CONTACT_WIRE_2", wx0, y - 0.010, wire_z - 0.32, wx1, y + 0.010, wire_z - 0.30,
            M["steel_dark"], C)
    # buffer stop at the end of the line
    bx, by = x0 - 3.4, y
    geo.box("BUFFER_BEAM", bx, by - 1.4, rail_z + 0.55, bx + 0.35, by + 1.4, rail_z + 1.05,
            M["paint_red"], C)
    geo.box("BUFFER_POST_L", bx - 0.5, by - 1.3, P.LAND_Z + 0.32, bx + 0.1, by - 0.9,
            rail_z + 0.6, M["steel_dark"], C)
    geo.box("BUFFER_POST_R", bx - 0.5, by + 0.9, P.LAND_Z + 0.32, bx + 0.1, by + 1.3,
            rail_z + 0.6, M["steel_dark"], C)
    geo.cyl("BUFFER_DISC_L", bx + 0.38, by - 0.7175, rail_z + 0.62, 0.28, 0.10, M["paint_red"], C,
            seg=14, axis="X")
    geo.cyl("BUFFER_DISC_R", bx + 0.38, by + 0.7175, rail_z + 0.62, 0.28, 0.10, M["paint_red"], C,
            seg=14, axis="X")
    log(f"rail: 20 m, {n} sleepers, gauge 1.435, contact wire +5.50 over rail head, buffer stop")


# ── crane ──────────────────────────────────────────────────────────────────
def build_crane(M, sysd):
    C = geo.coll("CRANE")
    cx, cy = 190.0, 122.1
    span = float(sysd["rail"]["crane_rail_span"])
    z = P.LAND_Z
    for side, dx in (("W", -span / 2), ("E", +span / 2)):
        geo.box(f"CRANE_RAIL_{side}", cx + dx - 0.06, cy - 4.0, z, cx + dx + 0.06, cy + 4.0,
                z + 0.12, M["steel"], C)
        geo.box(f"CRANE_LEG_{side}", cx + dx - 0.32, cy - 0.7, z + 0.12, cx + dx + 0.32,
                cy + 0.7, z + 9.2, M["crane_yellow"], C)
        geo.box(f"CRANE_WHEELBOX_{side}", cx + dx - 0.45, cy - 1.2, z + 0.12, cx + dx + 0.45,
                cy + 1.2, z + 0.75, M["steel_dark"], C)
    geo.box("CRANE_PORTAL", cx - span / 2 - 0.4, cy - 0.75, z + 9.0, cx + span / 2 + 0.4,
            cy + 0.75, z + 9.9, M["crane_yellow"], C)
    geo.cyl("CRANE_RING", cx, cy, z + 9.9, 0.95, 0.45, M["steel_dark"], C, seg=18)
    geo.box("CRANE_TOWER", cx - 0.75, cy - 0.75, z + 10.35, cx + 0.75, cy + 0.75, z + 13.4,
            M["crane_yellow"], C)
    # cab, glazed
    geo.box("CRANE_CAB", cx - 1.9, cy - 1.5, z + 13.4, cx - 0.2, cy + 0.2, z + 15.0,
            M["crane_yellow"], C)
    geo.box("CRANE_CAB_GLASS", cx - 1.92, cy - 1.52, z + 13.9, cx - 1.86, cy + 0.15, z + 14.7,
            M["glass"], C)
    geo.box("CRANE_CAB_GLASS2", cx - 1.9, cy - 1.52, z + 13.9, cx - 0.25, cy - 1.46, z + 14.7,
            M["glass"], C)
    # hammerhead: jib 22 m east, counter-jib 8 m west, both at +15.4
    geo.box("CRANE_JIB", cx, cy - 0.45, z + 15.4, cx + 22.0, cy + 0.45, z + 16.1,
            M["crane_yellow"], C)
    geo.box("CRANE_JIB_TOP", cx + 2.0, cy - 0.10, z + 16.1, cx + 21.0, cy + 0.10, z + 17.0,
            M["crane_yellow"], C)
    geo.box("CRANE_COUNTERJIB", cx - 8.0, cy - 0.55, z + 15.4, cx, cy + 0.55, z + 16.2,
            M["crane_yellow"], C)
    geo.box("CRANE_COUNTERWEIGHT", cx - 8.4, cy - 1.0, z + 15.0, cx - 6.6, cy + 1.0, z + 17.4,
            M["concrete"], C)
    # machinery house, mast cap, tie bars
    geo.box("CRANE_MACHINERY_HOUSE", cx - 5.5, cy - 0.8, z + 16.2, cx - 2.0, cy + 0.8, z + 17.6,
            M["steel_dark"], C)
    geo.box("CRANE_MAST_CAP", cx - 1.0, cy - 1.0, z + 17.0, cx + 1.0, cy + 1.0, z + 18.4,
            M["crane_yellow"], C)
    for i, xx in enumerate((cx + 6, cx + 14, cx + 20)):
        geo.box(f"CRANE_TIE_{i}", xx, cy - 0.05, z + 17.0, xx + 0.10, cy + 0.05, z + 18.6,
                M["steel_dark"], C)
    # hoist: rope from the jib trolley to the hook, load slung under it
    trolley_x = cx + 15.0
    geo.box("CRANE_TROLLEY", trolley_x - 0.5, cy - 0.5, z + 16.1, trolley_x + 0.5, cy + 0.5,
            z + 16.9, M["steel_dark"], C)
    hook_z = z + 6.2
    geo.cyl("CRANE_HOIST_ROPE", trolley_x, cy, hook_z + 0.4, 0.022, z + 16.1 - hook_z - 0.4,
            M["steel_dark"], C, seg=8)
    geo.box("CRANE_HOOK_BLOCK", trolley_x - 0.28, cy - 0.20, hook_z + 0.10, trolley_x + 0.28,
            cy + 0.20, hook_z + 0.62, M["steel_dark"], C)
    geo.box("CRANE_HOOK", trolley_x - 0.05, cy - 0.06, hook_z - 0.12, trolley_x + 0.05, cy + 0.06,
            hook_z + 0.12, M["steel"], C)
    # the load: a crate on a four-leg sling
    lx, lz = trolley_x, hook_z - 0.90
    geo.box("CRANE_LOAD", lx - 0.75, cy - 0.55, lz - 0.80, lx + 0.75, cy + 0.55, lz, M["timber_pale"], C)
    for (dx, dy) in ((-0.65, -0.45), (0.65, -0.45), (-0.65, 0.45), (0.65, 0.45)):
        geo.rope(f"CRANE_SLING_{dx}_{dy}", (lx + dx, cy + dy, lz - 0.05),
                 (trolley_x, cy, hook_z - 0.05), 0.02, 0.012, M["rope"], C, n=6)
    log("crane: hammerhead, 22 m jib, 8 m counter-jib with counterweight, cab, driver, load on hook")


# ── the coaster ────────────────────────────────────────────────────────────
def build_ship(M, sysd):
    C = geo.coll("SHIP")
    x0, y0, x1, y1 = 120.0, 105.65, 210.0, 119.15
    draft = 4.20
    deck = P.WATER_Z - draft + 7.75          # 2.55 above water: freeboard 3.55 m
    # hull: a box with raked bow and a counter stern, as a closed prism
    v = [(x0, y0, -draft), (x1 - 6.0, y0, -draft), (x1, y0 + 2.0, -draft),
         (x1, (y0 + y1) / 2, -draft), (x1, y1 - 2.0, -draft), (x1 - 6.0, y1, -draft),
         (x0, y1, -draft),
         (x0, y0, deck), (x1 - 6.0, y0, deck), (x1, y0 + 2.0, deck),
         (x1, (y0 + y1) / 2, deck), (x1, y1 - 2.0, deck), (x1 - 6.0, y1, deck),
         (x0, y1, deck)]
    f = [(0, 1, 8, 7), (1, 2, 9, 8), (2, 3, 10, 9), (3, 4, 11, 10), (4, 5, 12, 11),
         (5, 6, 13, 12), (6, 0, 7, 13), (7, 8, 9, 10, 11, 12, 13), (0, 6, 5, 4, 3, 2, 1)]
    me = bpy.data.meshes.new("HULL_COASTER")
    me.from_pydata(v, [], f)
    me.validate(verbose=False)
    ob = bpy.data.objects.new("HULL_COASTER", me)
    ob.data.materials.append(M["hull"])
    C.objects.link(ob)
    # boot-top and deck
    geo.box("HULL_BOOTTOP", x0 + 0.02, y0 - 0.02, P.WATER_Z - 0.55, x1 - 6.0, y1 + 0.02,
            P.WATER_Z + 0.20, M["hull_red"], C)
    geo.box("SHIPDECK_COASTER", x0 + 0.6, y0 + 0.15, deck, x1 - 6.6, y1 - 0.15, deck + 0.05,
            M["deck"], C)
    # hatch covers, four holds
    for i in range(4):
        hx = x0 + 5 + i * 20.0
        geo.box(f"HULL_COASTER_hatch_{i+1}", hx, y0 + 2.2, deck + 0.05, hx + 15.0, y1 - 2.2,
                deck + 1.15, M["hatch"], C)
        geo.box(f"HATCHCOAM_{i+1}", hx - 0.15, y0 + 2.05, deck + 0.05, hx + 15.15, y1 - 2.05,
                deck + 0.35, M["steel_dark"], C)
    # forecastle, deckhouse aft, funnel, masts, rails
    geo.box("SHIP_FORECASTLE", x1 - 12.0, y0 + 1.2, deck + 0.05, x1 - 4.0, y1 - 1.2, deck + 2.4,
            M["paint_white"], C)
    geo.box("SHIP_DECKHOUSE", x0 + 2.0, y0 + 1.4, deck + 0.05, x0 + 12.0, y1 - 1.4, deck + 4.6,
            M["paint_white"], C)
    for i in range(3):
        geo.box(f"SHIP_DH_WIN_{i}", x0 + 2.2, y1 - 1.35, deck + 3.4 + i * 0.0,
                x0 + 11.8, y1 - 1.30, deck + 3.9, M["glass"], C)
    geo.cyl("SHIP_FUNNEL", x0 + 5.0, (y0 + y1) / 2, deck + 4.6, 1.15, 4.6, M["paint_red"], C,
            seg=16, r_top=1.05)
    geo.cyl("SHIP_FUNNEL_CAP", x0 + 5.0, (y0 + y1) / 2, deck + 9.2, 1.10, 0.35, M["iron"], C, seg=16)
    geo.cyl("SHIP_MAST_F", x1 - 8.0, (y0 + y1) / 2, deck + 0.05, 0.18, 9.0, M["timber_dark"], C,
            seg=10, r_top=0.08)
    geo.cyl("SHIP_MAST_A", x0 + 1.6, (y0 + y1) / 2, deck + 0.05, 0.16, 7.0, M["timber_dark"], C,
            seg=10, r_top=0.07)
    for yy in (y0, y1):
        geo.box("SHIP_RAIL", x0 + 1.0, yy - 0.03 if yy == y0 else yy - 0.03, deck + 1.0,
                x1 - 6.0, yy + 0.03, deck + 1.06, M["paint_white"], C)
    # pad eyes on the deck edge: a rope that ends in mid-air is a defect (v_plant)
    for i, px in enumerate((x0 + 3.0, x0 + 30.0, x1 - 12.0, x1 - 4.0)):
        geo.box(f"SHIP_PADEYE_{i+1}", px - 0.16, y1 - 0.34, deck + 0.05, px + 0.16, y1 + 0.02,
                deck + 1.02, M["steel_dark"], C)
    # four mooring ropes in catenary to the bollards on the north quay
    moor = [(x0 + 3.0, y1, 120.5, 114.0), (x0 + 30.0, y1, 120.5, 138.0),
            (x1 - 12.0, y1, 120.5, 178.0), (x1 - 4.0, y1, 120.5, 202.0)]
    for i, (sx, sy, by, bx) in enumerate(moor):
        p0 = (sx, sy - 0.16, deck + 0.88)
        p1 = (bx, by, P.LAND_Z + 0.66)          # the bollard head itself
        sag = 0.22 + 0.10 * i
        geo.rope(f"MOORING_ROPE_{i+1}", p0, p1, sag, 0.045, M["rope"], C, n=20)
    log(f"coaster: 90 x 13.5 m, draft {draft:.2f} m, deck +{deck:.2f}, 4 ropes in catenary")


# ── people ─────────────────────────────────────────────────────────────────
def person(name, x, y, z, rot, pose, M, C, cloth="cloth_navy"):
    """Six people in task poses. Blockout figures — G6 is not claimed for them
    (evidence/RIGHTS.md), but they are named, jointed and casting shadows."""
    parts = []
    s = 1.0
    hip = 0.92
    if pose == "standing":
        parts += [(x - 0.17, y - 0.10, z, x - 0.04, y + 0.10, z + hip),
                  (x + 0.04, y - 0.10, z, x + 0.17, y + 0.10, z + hip)]
    elif pose == "walking":
        parts += [(x - 0.19, y - 0.26, z, x - 0.05, y + 0.02, z + hip),
                  (x + 0.05, y - 0.02, z, x + 0.19, y + 0.24, z + hip)]
    elif pose == "carrying":
        parts += [(x - 0.20, y - 0.12, z, x - 0.05, y + 0.10, z + hip),
                  (x + 0.05, y - 0.12, z, x + 0.20, y + 0.10, z + hip)]
    elif pose == "seated":
        parts += [(x - 0.18, y - 0.14, z + 0.30, x - 0.05, y + 0.06, z + 0.46),
                  (x + 0.05, y - 0.14, z + 0.30, x + 0.18, y + 0.06, z + 0.46),
                  (x - 0.18, y - 0.16, z + 0.44, x - 0.05, y + 0.02, z + 0.48),
                  (x + 0.05, y - 0.16, z + 0.44, x + 0.18, y + 0.02, z + 0.48)]
        hip = 0.48
    elif pose == "pulling":
        parts += [(x - 0.20, y - 0.18, z, x - 0.05, y + 0.06, z + hip),
                  (x + 0.05, y - 0.06, z, x + 0.20, y + 0.18, z + hip)]
    torso_z = z + hip
    torso_h = 0.58 if pose != "seated" else 0.62
    parts += [(x - 0.20, y - 0.11, torso_z, x + 0.20, y + 0.11, torso_z + torso_h)]
    # arms
    ay = y + (0.18 if pose in ("carrying", "pulling") else 0.0)
    parts += [(x - 0.30, ay - 0.07, torso_z + 0.08, x - 0.18, ay + 0.07, torso_z + torso_h + 0.05),
              (x + 0.18, ay - 0.07, torso_z + 0.08, x + 0.30, ay + 0.07, torso_z + torso_h + 0.05)]
    body = props.item(name + "_BODY", parts, M[cloth], C, bevel=0.012)
    # head, hair, hands, boots as separate small objects (each its own prop)
    props.item(name + "_HEAD", [(x - 0.10, y - 0.09, torso_z + torso_h, x + 0.10, y + 0.09,
                                 torso_z + torso_h + 0.24)], M["skin"], C, bevel=0.03)
    props.item(name + "_HAIR", [(x - 0.105, y - 0.095, torso_z + torso_h + 0.12,
                                 x + 0.105, y + 0.095, torso_z + torso_h + 0.255)],
               M["hair"], C, bevel=0.03)
    for i, hx in enumerate((x - 0.27, x + 0.27)):
        props.item(f"{name}_HAND_{i}", [(hx - 0.06, ay - 0.05, torso_z + 0.02, hx + 0.06,
                                         ay + 0.05, torso_z + 0.12)], M["skin"], C, bevel=0.02)
    for i, hx in enumerate((x - 0.15, x + 0.05)):
        props.item(f"{name}_BOOT_{i}", [(hx, y - 0.14, z, hx + 0.16, y + 0.14, z + 0.16)],
                   M["boot"], C, bevel=0.02)
    return body


def build_people(M):
    C = geo.coll("PEOPLE")
    people = [
        ("DOCKER_01", 178.0, 126.0, P.LAND_Z, 0.4, "carrying", "cloth_olive"),
        ("DOCKER_02", 183.5, 124.0, P.LAND_Z, -0.7, "walking", "cloth_navy"),
        ("SAILOR_01", 141.0, 118.9, P.LAND_Z, 2.4, "pulling", "cloth_grey"),
        ("CRANE_DRIVER", 189.1, 121.4, P.LAND_Z + 13.85, 0.0, "seated", "cloth_navy"),
        ("CLERK_01", 168.0, 130.0, P.LAND_Z, 1.2, "walking", "cloth_grey"),
        ("FISHER_01", 250.0, 34.0, P.LAND_Z, -1.1, "standing", "cloth_olive"),
    ]
    for (n, x, y, z, r, pose, cloth) in people:
        person(n, x, y, z, r, pose, M, C, cloth)
    log(f"people: {len(people)} placed in task poses (blockout figures, G6 not claimed)")


# ── light ──────────────────────────────────────────────────────────────────
def build_light(M):
    C = geo.coll("LIGHTS")
    sc = bpy.context.scene
    world = bpy.data.worlds.new("DAWN")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(6.5)          # early January, dawn
    sky.sun_rotation = math.radians(115.0)
    sky.sun_intensity = 0.6
    sky.altitude = 30.0
    sky.air_density = 1.0
    sky.dust_density = 1.2
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.72
    sun = bpy.data.lights.new("SUN_dawn", "SUN")
    sun.energy = 4.2
    sun.color = (1.0, 0.79, 0.60)
    sun.angle = math.radians(2.2)
    so = bpy.data.objects.new("SUN_dawn", sun)
    so.rotation_euler = (math.radians(80.5), 0.0, math.radians(112.0))
    C.objects.link(so)
    fill = bpy.data.lights.new("SKY_fill", "AREA")
    fill.energy = 780.0
    fill.size = 220.0
    fill.color = (0.60, 0.72, 0.95)
    fo = bpy.data.objects.new("SKY_fill", fill)
    fo.location = (200.0, 190.0, 95.0)
    C.objects.link(fo)
    # a second, dimmer fill from the opposite side: in reality this is the bounce
    # off the water and the opposite terrace, which a two-thousand-triangle wall
    # of brick does not produce on its own
    bounce = bpy.data.lights.new("WATER_BOUNCE", "AREA")
    bounce.energy = 320.0
    bounce.size = 120.0
    bounce.color = (0.70, 0.78, 0.92)
    bo = bpy.data.objects.new("WATER_BOUNCE", bounce)
    bo.location = (200.0, 75.0, 12.0)
    bo.rotation_euler = (math.radians(-70.0), 0.0, 0.0)
    C.objects.link(bo)
    log("light: Nishita dawn sky (strength 1.35), sun at 6.5 deg, sky fill, water bounce")


# ── cameras ────────────────────────────────────────────────────────────────
CAMERAS = [
    ("01_district_aerial_sw", (60, 60, 95), (200, 170, 6)),
    ("02_district_aerial_ne", (360, 300, 90), (180, 120, 4)),
    ("03_b05_frontage", (158.0, 104.0, 6.5), (176.0, 129.0, 8.0)),
    ("04_quay_from_water", (140.0, 86.0, 3.0), (176.0, 126.0, 5.0)),
    ("05_waterline_b05", (152.0, 96.0, 1.25), (186.0, 119.0, 5.2)),
    ("06_crane", (172.0, 102.0, 5.0), (190.0, 120.0, 13.0)),
    ("07_crane_cab", (188.4, 124.2, 21.4), (188.0, 108.0, 6.0)),
    ("08_hull_bow", (216.0, 100.0, 3.4), (204.0, 111.0, 2.4)),
    ("09_mooring_rope", (160.5, 123.2, 3.4), (150.0, 119.6, 1.6)),
    ("10_rail_buffer", (316.0, 141.0, 2.0), (300.0, 145.0, 1.2)),
    ("11_rail_catenary", (306.0, 148.0, 3.0), (306.0, 145.0, 6.4)),
    ("12_interior_living", None, None),
    ("13_interior_kitchen", None, None),
    ("14_interior_bedroom", None, None),
    ("15_interior_bathroom", None, None),
    ("16_shop_floor", None, None),
    ("17_entry_hall", None, None),
    ("18_facade_floors", (168.0, 126.2, 1.8), (176.0, 129.0, 14.0)),
    ("19_ice_edge", (116.0, 114.0, 1.8), (126.0, 118.6, 0.1)),
    ("20_basin_wide", (200.0, 34.0, 6.0), (200.0, 100.0, 3.0)),
    ("21_docker_close", (180.0, 126.0, 1.55), (178.0, 124.6, 1.35)),
    ("22_stern_ropes", (243.0, 121.8, 3.6), (228.0, 119.0, 2.6)),
    ("23_b05_section_cut", (177.0, 122.0, 12.0), (177.0, 135.0, 9.0)),
    ("24_gulls_skyline", (120.0, 60.0, 3.0), (200.0, 160.0, 40.0)),
]


def room_prop_boxes(room_id):
    out = []
    pref = f"ROOM_{room_id}_"
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith(pref):
            b = geo.world_bounds(o)
            out.append(((b[0], b[1], b[2]), (b[3], b[4], b[5])))
    return out


def furniture_centroid(r):
    """Centroid of this room's furniture — the thing a proof view must show."""
    xs, ys, zs, n = 0.0, 0.0, 0.0, 0
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.name.startswith(f"ROOM_{r['id']}_"):
            continue
        if any(t in ob.name for t in ("_floor", "_ceiling", "_lining", "doorframe", "doorhead",
                                      "doorleaf", "sill", "winfram", "glass", "_practical")):
            continue
        b = geo.world_bounds(ob)
        cx, cy, cz = (b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2
        xs += cx
        ys += cy
        zs += cz
        n += 1
    if not n:
        return None
    return (xs / n, ys / n, zs / n)


def clear_camera_point(r, margin=0.55):
    """F8 for interiors: a lens position with an empty sphere around it."""
    x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
    boxes = room_prop_boxes(r["id"])
    best = None
    z = r["level_z"] + P.EYE_H
    step = 0.30
    y = y0 + margin
    while y < y1 - margin:
        x = x0 + margin
        while x < x1 - margin:
            ok = True
            for (a, b) in boxes:
                if (a[0] - margin < x < b[0] + margin and a[1] - margin < y < b[1] + margin
                        and a[2] - 0.2 < z < b[2] + margin):
                    ok = False
                    break
            if ok:
                d = min(x - x0, x1 - x, y - y0, y1 - y)
                if best is None or d > best[0]:
                    best = (d, x, y)
            x += step
        y += step
    if best is None:
        return None
    return (best[1], best[2], z)


def build_cameras(rooms):
    sc = bpy.context.scene
    C = geo.coll("CAMERAS")
    made, notes = [], []
    pick = {}
    for r in rooms:
        if r["building"] != "B05":
            continue
        nm = r["name"]
        if nm in ("living", "kitchen", "bedroom", "bathroom", "entry", "sales") and nm not in pick:
            pick[nm] = r
    for entry in CAMERAS:
        name, loc, tgt = entry
        if loc is None:
            key = {"12": "living", "13": "kitchen", "14": "bedroom", "15": "bathroom",
                   "16": "sales", "17": "entry"}[name[:2]]
            r = pick.get(key)
            if r is None:
                notes.append(f"{key}: no room to shoot")
                continue
            # stand where the furniture is NOT and look at the furniture: the old
            # rule (aim at the far corner) framed three bare walls and a doorway.
            fc = furniture_centroid(r)
            cands = [(r["x0"] + 0.55, r["y0"] + 0.55), (r["x1"] - 0.55, r["y0"] + 0.55),
                     (r["x0"] + 0.55, r["y1"] - 0.55), (r["x1"] - 0.55, r["y1"] - 0.55),
                     ((r["x0"] + r["x1"]) / 2, r["y0"] + 0.55),
                     ((r["x0"] + r["x1"]) / 2, r["y1"] - 0.55)]
            if fc is None:
                fc = ((r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2, r["level_z"] + 1.0)
            cands.sort(key=lambda c: -((c[0] - fc[0]) ** 2 + (c[1] - fc[1]) ** 2))
            chosen = None
            boxes = room_prop_boxes(r["id"])
            for (cx, cy) in cands:
                z = r["level_z"] + P.EYE_H
                ok = True
                for (a, b) in boxes:
                    if (a[0] - 0.35 < cx < b[0] + 0.35 and a[1] - 0.35 < cy < b[1] + 0.35
                            and a[2] - 0.2 < z < b[2] + 0.2):
                        ok = False
                        break
                if ok:
                    chosen = (cx, cy, z)
                    break
            if chosen is None:
                chosen = clear_camera_point(r)
                notes.append(f"{r['id']}: all corners occupied, fell back to F8 search")
            if chosen is None:
                b = r
                chosen = ((b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2, r["level_z"] + P.EYE_H)
            loc = chosen
            tgt = (fc[0], fc[1], r["level_z"] + 1.10)
        cam = bpy.data.cameras.new(f"CAM_{name}")
        cam.lens = 24 if "aerial" in name else (16 if ("interior" in name or "shop" in name) else 30)
        cam.clip_start = 0.05
        cam.clip_end = 900.0
        ob = bpy.data.objects.new(f"CAM_{name}", cam)
        ob.location = loc
        d = Vector(tgt) - Vector(loc)
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        C.objects.link(ob)
        made.append(ob.name)
    inside = exterior_intrusions()
    json.dump(dict(cameras=made, notes=notes, exterior_clear=not inside,
                   exterior_intrusions=[list(h) for h in inside]),
              open(os.path.join(ROOT, "evidence", "CAMERAS.json"), "w"), indent=1)
    log(f"{len(made)} proof cameras; F8 interior unresolved {len(notes)}; "
        f"F8 exterior lenses inside solids {len(inside)}")
    for c, o in inside[:10]:
        log(f"  F8 FAIL {c} inside {o}")
    return made


def exterior_intrusions(margin=0.35, ignore=("WATER_SURFACE", "BASIN_BED", "SITE_GROUND", "SETTS")):
    hits = []
    for cam in [o for o in bpy.data.objects if o.type == "CAMERA"]:
        c = cam.location
        for o in bpy.data.objects:
            if o.type != "MESH" or any(o.name.startswith(i) for i in ignore):
                continue
            b = geo.world_bounds(o)
            if (b[0] - margin <= c.x <= b[3] + margin and b[1] - margin <= c.y <= b[4] + margin
                    and b[2] - margin <= c.z <= b[5] + margin):
                hits.append((cam.name, o.name))
                break
    return hits


# ── receipt ────────────────────────────────────────────────────────────────
def engine_note():
    try:
        import _cycles
        oidn = bool(getattr(_cycles, "with_openimagedenoise", False))
    except Exception:                                   # noqa: BLE001
        oidn = False
    return "CYCLES CPU, %s" % ("OpenImageDenoise available" if oidn else "no OIDN")


def main():
    global M_GLASS, M_DARK
    reset()
    M = geo.build_materials()
    M_GLASS, M_DARK = M["glass_dirty"], M["mud"]
    sc = bpy.context.scene
    sc.unit_settings.scale_length = 1.0
    specs = P.building_specs()
    b05 = next(s for s in specs if s["id"] == "B05")
    b05_rooms = join_schedule(b05, compute_b05_rooms(b05))
    log(f"B05 schedule: {len(b05_rooms)} rooms joined, door/window recomputed from planlib")

    build_site(M)
    build_water(M)
    build_quay(M)

    C = geo.coll("BUILDINGS")
    for s in specs:
        if s["id"] == "B05":
            build_b05(s, M, b05_rooms, C)
        else:
            mass_building(s, M, C, P.LAND_Z)
    n_piers = party_piers(specs, M, C)
    n_fringe = city_fringe(M, C)
    log(f"buildings: 48 ({len(b05_rooms)} rooms in B05; 47 massing only), {n_piers} party piers")

    sysd = json.load(open(os.path.join(ROOT, "design", "SYSTEMS.json")))
    build_rail(M, sysd)
    build_crane(M, sysd)
    build_ship(M, sysd)
    build_people(M)
    build_light(M)
    build_cameras(b05_rooms)

    sc.render.resolution_x = 1024
    sc.render.resolution_y = 576
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 4
    sc.cycles.transparent_max_bounces = 4
    sc.cycles.use_light_tree = True
    sc.render.filepath = os.path.join(ROOT, "renders", "proofs", "")
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    n_obj = len(bpy.data.objects)
    n_tri = sum(geo.tri_count(o) for o in bpy.data.objects if o.type == "MESH")
    receipt = dict(built=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), objects=n_obj,
                   triangles=n_tri, blend=OUT, log=LOG, blender=bpy.app.version_string,
                   engine=engine_note(),
                   rooms_b05=len(b05_rooms),
                   props_b05=sum(ROOM_PROPS.values()))
    json.dump(receipt, open(os.path.join(ROOT, "evidence", "BUILD_RECEIPT.json"), "w"), indent=1)
    log(f"saved {OUT}: {n_obj} objects, {n_tri:,} triangles, {receipt['props_b05']} props in B05")


if __name__ == "__main__":
    main()
