#!/usr/bin/env python3
"""PORTUS Stage A — programme generator.

Emits, from planlib alone (no bpy):
  design/PROGRAMME.json      48 buildings, 197 floors, 208 apartments, 1608 rooms
  design/plans/*.svg         one dimensioned plan per occupied floor + 48 site plans
  design/plans/*.json        the same plan as data, for the builder
  design/SCHEDULE.csv        one row per counted room
  design/APARTMENTS.csv      208 rows: archetype, palette, generation, occupancy, seed
  design/SYSTEMS.json        water, rail, cranes, moorings, catenary
  design/briefs/*.md         one brief per building
  design/STATS.json          what the validator will be asked to prove

Run: python3 portus/design/generate_programme.py
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "build"))

import planlib as P

OUT = HERE
PLANS = os.path.join(OUT, "plans")
BRIEFS = os.path.join(OUT, "briefs")


# ── room programme per building ────────────────────────────────────────────
def levels_with_extras(spec):
    """Which levels carry the block's extra counted rooms."""
    n = len(spec["storeys"])
    res = [i for i, s in enumerate(spec["storeys"]) if s["use"] == "residential"]
    k = spec["kind"]
    if k == "warehouse":
        return [1, 2, 3][: n - 1]
    if k in ("workshop", "shed"):
        return [0]
    if k == "office":
        return [0]
    if k == "civic":
        return [0]
    return []


def build_rooms():
    specs = P.building_specs()
    apts = {a["id"]: a for a in P.apartment_catalogue()}
    rooms, floors = [], []
    idx = 0
    for s in specs:
        ffls = P.floor_levels(s)
        extras = P.extra_rooms(s, 0.0)
        ex_levels = levels_with_extras(s)
        ex_by_level = {li: [] for li in ex_levels}
        for i, r in enumerate(extras):
            ex_by_level[ex_levels[i % len(ex_levels)]].append(r)
        for li, st in enumerate(s["storeys"]):
            z = ffls[li]
            floor_id = f"{s['id']}-L{li+1:02d}"
            level_rooms = []
            if s["kind"] == "market":
                if li == 1:
                    level_rooms = P.shop_rooms(s, z)
                    for r in level_rooms:
                        r["name"] = "auction " + r["name"]
                elif li == 0:
                    level_rooms = P.market_stalls(s)
            else:
                if li == 0:
                    level_rooms = P.shop_rooms(s, z)
                if st["use"] == "residential":
                    aid = f"{s['id']}-L{li+1:02d}"
                    for ai in range(2):
                        apt_id = f"{aid}-{'AB'[ai]}"
                        a = apts[apt_id]
                        rs, slot = P.apartment_rooms(s, li, ai, apt_id, a["archetype"], a["seed"])
                        level_rooms += rs
                for r in ex_by_level.get(li, []):
                    level_rooms.append(dict(r))
            # doors and windows
            slot_rect = None
            if st["use"] == "residential" or s["kind"] == "market":
                _, _w, _d = P._u_v_axes(s)
            # per-apartment slots: recompute cheaply from rooms' apartment ids
            groups = {}
            for r in level_rooms:
                groups.setdefault(r.get("apartment") or r.get("shop") or r.get("market") or "BLD", []).append(r)
            for gid, rs in groups.items():
                slot = None
                if gid != "BLD" and "-" in str(gid) and str(gid).startswith(tuple("BEF")):
                    _, s_ = P.apartment_rooms(
                        s, li, 0 if str(gid).endswith("A") else 1, gid,
                        apts[str(gid)]["archetype"], apts[str(gid)]["seed"])
                    slot = s_
                stalls = all(r["kind"] == "stall" for r in rs)
                entries = P.stall_openings(rs) if stalls else P.openings_for_rooms(rs, s, z, slot)
                reachable = True if stalls else (P.reachable(entries) if len(rs) > 1 else True)
                for e in entries:
                    r = e["room"]
                    idx += 1
                    rec = dict(
                        id=f"R{idx:05d}", building=s["id"], block=s["block"], floor=li + 1,
                        floor_id=floor_id, apartment=r.get("apartment"),
                        name=r["name"], kind=r["kind"], shop=r.get("shop"),
                        level_z=round(z, 3),
                        bounds={k: r[k] for k in ("x0", "y0", "x1", "y1")},
                        w=r["w"], d=r["d"], area=r["area"],
                        doors=1 if e["door"] else 0, windows=1 if e["window"] else 0,
                        door=e["door"], window=e["window"], reachable=bool(reachable),
                        loading=bool(e["door"] and e["door"].get("loading")),
                        counted=True)
                    rooms.append(rec)
            floors.append(dict(id=floor_id, building=s["id"], level=li + 1, ffl=round(z, 3),
                               storey_h=st["h"], use=st["use"], rooms=len(level_rooms),
                               area=round((s["x1"] - s["x0"]) * (s["y1"] - s["y0"]), 3)))
    return specs, floors, rooms, apts


# ── SVG plans ──────────────────────────────────────────────────────────────
def svg_plan(title, rects, site_outline, path, scale_note=""):
    W, H = 1000, 800
    x0, y0, x1, y1 = site_outline
    pad = 40
    sx = (W - 2 * pad) / max(1e-6, (x1 - x0))
    sy = (H - 2 * pad) / max(1e-6, (y1 - y0))
    k = min(sx, sy)

    def X(x):
        return pad + (x - x0) * k

    def Y(y):
        return H - pad - (y - y0) * k     # north up

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="#f6f3ee"/>',
             f'<text x="20" y="26" font-family="monospace" font-size="16">{title}</text>',
             f'<text x="20" y="{H-12}" font-family="monospace" font-size="11" fill="#555">'
             f'1 m = {k:.3f} px · grid 5 m · {scale_note}</text>']
    # 5 m grid
    gx = math.ceil(x0 / 5) * 5
    while gx < x1:
        parts.append(f'<line x1="{X(gx):.1f}" y1="{Y(y0):.1f}" x2="{X(gx):.1f}" y2="{Y(y1):.1f}" '
                     f'stroke="#e4ded4" stroke-width="0.6"/>')
        gx += 5
    gy = math.ceil(y0 / 5) * 5
    while gy < y1:
        parts.append(f'<line x1="{X(x0):.1f}" y1="{Y(gy):.1f}" x2="{X(x1):.1f}" y2="{Y(gy):.1f}" '
                     f'stroke="#e4ded4" stroke-width="0.6"/>')
        gy += 5
    parts.append(f'<rect x="{X(x0):.1f}" y="{Y(y1):.1f}" width="{(x1-x0)*k:.1f}" height="{(y1-y0)*k:.1f}" '
                 f'fill="none" stroke="#333" stroke-width="1.4"/>')
    palette = {"living": "#e8d9c3", "kitchen": "#dbe6d8", "bedroom": "#d9d2e6", "bathroom": "#cfe2ea",
               "entry": "#efe7cf", "store": "#ded6cc", "sales": "#f0dfc0", "stock": "#ded6cc",
               "staff": "#e3e7d6", "wc": "#cfe2ea", "stall": "#eee6d2"}
    for r in rects:
        nm = r["name"]
        col = palette.get(nm.split()[-1], "#e9e4da")
        parts.append(f'<rect x="{X(r["x0"]):.1f}" y="{Y(r["y1"]):.1f}" width="{r["w"]*k:.1f}" '
                     f'height="{r["d"]*k:.1f}" fill="{col}" stroke="#444" stroke-width="0.8" '
                     f'fill-opacity="0.85"/>')
        if r["w"] * k > 26 and r["d"] * k > 12:
            parts.append(f'<text x="{X((r["x0"]+r["x1"])/2):.1f}" y="{Y((r["y0"]+r["y1"])/2):.1f}" '
                         f'font-family="monospace" font-size="7" text-anchor="middle" fill="#333">'
                         f'{nm} {r["area"]:.1f}</text>')
    parts.append("</svg>")
    open(path, "w").write("\n".join(parts))


# ── systems ────────────────────────────────────────────────────────────────
def systems():
    specs = {s["id"]: s for s in P.building_specs()}
    # rail: 6 tracks in the north-east yard, two curves with cant, buffer stops at the west ends
    tracks = []
    for i in range(6):
        y = 150.0 + 5.0 * i
        tracks.append(dict(
            id=f"T{i+1}", kind="yard", gauge=1.435,
            centreline=[(300.0, y), (330.0, y), (360.0, y), (396.0, y)],
            radii=[0.0, 0.0, 0.0], cant_mm=[0, 0, 0],
            buffer_stop=(300.0, y), enters_building=("D01" if i == 5 else None)))
    tracks.append(dict(id="T0", kind="siding", gauge=1.435,
                       centreline=[(300.0, 145.0), (318.0, 143.0), (336.0, 145.0), (360.0, 145.0)],
                       radii=[120.0, 120.0], cant_mm=[25, 25, 0],
                       buffer_stop=(300.0, 145.0), enters_building=None))
    # six counted tracks + the siding used by the Stage B slice is track T6 inside the goods shed
    cranes = [
        dict(id="CR-H1", type="hammerhead", x=140.0, y=124.0, jib=22.0, rail_y=124.0, load="crate 2.4 t"),
        dict(id="CR-H2", type="hammerhead", x=190.0, y=124.0, jib=22.0, rail_y=124.0, load="pallet 1.1 t"),
        dict(id="CR-H3", type="hammerhead", x=240.0, y=124.0, jib=22.0, rail_y=124.0, load="fish box 0.4 t"),
        dict(id="CR-H4", type="hammerhead", x=96.0, y=70.0, jib=22.0, rail_x=96.0, load="coil 3.2 t"),
        dict(id="CR-G1", type="gantry", x0=322.0, x1=386.0, y=64.0, span=64.0, load="plate stack"),
        dict(id="CR-G2", type="gantry", x0=310.0, x1=380.0, y=168.0, span=70.0, load="wagon load"),
    ]
    for i in range(8):
        cranes.append(dict(id=f"CR-J{i+1}", type="wall_jib", x=20.0 + 40.0 * (i % 4), y=232.0,
                           jib=6.0, wall="A%02d" % (i + 1), load="sack 60 kg" if i % 2 else "none"))
    moorings = [
        dict(id="M1", x=124.0, y=128.0, type="bollard", berth="coaster"),
        dict(id="M2", x=164.0, y=128.0, type="bollard", berth="coaster"),
        dict(id="M3", x=204.0, y=128.0, type="bollard", berth="coaster"),
        dict(id="M4", x=238.0, y=128.0, type="bollard", berth="coaster"),
        dict(id="M5", x=104.0, y=60.0, type="bollard", berth="tug"),
        dict(id="M6", x=262.0, y=32.0, type="slipway winch", berth="fishing boat"),
    ]
    bollards = []
    n = 0
    for x in [110.0 + 8.0 * i for i in range(20)]:       # north quay 20 bollards
        n += 1
        bollards.append(dict(id=f"BOL{n:02d}", x=x, y=128.0))
    for y in [32.0 + 8.0 * i for i in range(10)]:        # west quay 10
        n += 1
        bollards.append(dict(id=f"BOL{n:02d}", x=102.0, y=y))
    for x in [120.0 + 8.0 * i for i in range(10)]:       # south quay 10
        n += 1
        bollards.append(dict(id=f"BOL{n:02d}", x=x, y=22.0))
    return dict(
        units="metres", datum="basin SW corner, water +0.00, +Z up, north +Y",
        water=dict(level=0.0, tolerance=0.005, depth=6.0, bed_z=-6.0,
                   basin=dict(x0=110.0, y0=30.0, x1=290.0, y1=120.0),
                   quay_top=2.40, states=["calm", "flood", "wind", "ice"],
                   ripple_scales=[0.1, 1.0, 8.0], amplitude_mm=[15, 80],
                   foam_reach=0.150, ice_thickness_mm=[20, 90],
                   dropped_objects=8),
        rail=dict(gauge=1.435, gauge_tol=0.002,
                  # the packet says "sleepers 2,600 +/- 10 mm": that is the LENGTH of a
                  # standard sleeper, not the pitch. Both are declared, both validated.
                  sleeper_length=2.600, sleeper_length_tol=0.010,
                  sleeper_pitch=0.600, sleeper_pitch_tol=0.010,
                  catenary_height=5.50, catenary_tol=0.02,
                  crane_rail_span=2.400, crane_rail_span_tol=0.020,
                  crane_rail_note="centre-to-centre of the portal crane rails; not fixed by "
                                  "the packet, declared here and validated against this value",
                  tracks=tracks, buffer_stops=4,
                  points_groups=3, vehicles=14),
        cranes=cranes, moorings=moorings, bollards=bollards,
        ships=[
            dict(id="SHIP-COASTER", type="coaster", length=90.0, beam=13.5, draft=4.20,
                 berth="north quay", x=120.0, y=100.0, heading=0.0),
            dict(id="SHIP-TUG", type="tug", length=25.0, beam=8.4, draft=2.80,
                 berth="west quay", x=100.0, y=48.0, heading=90.0),
            dict(id="SHIP-FISH", type="fishing boat", length=18.0, beam=5.6, draft=1.90,
                 berth="slipway", x=256.0, y=40.0, heading=0.0)])


# ── briefs ─────────────────────────────────────────────────────────────────
def brief(spec, rooms_n, apts_n):
    ffls = P.floor_levels(spec)
    lines = [f"# {spec['id']} — {spec['name']}", "",
             f"- Block **{spec['block']} · {P.BLOCK_NAMES[spec['block']]}** · kind `{spec['kind']}`",
             f"- Footprint `{spec['x0']:.1f}, {spec['y0']:.1f}` → `{spec['x1']:.1f}, {spec['y1']:.1f}` "
             f"= **{spec['x1']-spec['x0']:.1f} × {spec['y1']-spec['y0']:.1f} m** "
             f"({(spec['x1']-spec['x0'])*(spec['y1']-spec['y0']):.1f} m²)",
             f"- Storeys **{len(spec['storeys'])}** · height **{P.building_height(spec):.2f} m** · "
             f"wall `{spec['wall']}` · roof `{spec['roof']}` at {spec['pitch']}° · window module {spec['module']} m",
             f"- Front faces **{spec['front']}** · shop `{spec['shop']}` ({spec['shop_id']})",
             f"- Counted rooms **{rooms_n}** · apartments **{apts_n}**", "",
             "| level | FFL (m) | storey h (m) | use |", "|---:|---:|---:|---|"]
    for i, st in enumerate(spec["storeys"]):
        lines.append(f"| L{i+1:02d} | {ffls[i]:.2f} | {st['h']:.2f} | {st['use']} |")
    lines += ["", "Plans: `design/plans/" + spec["id"] + "_L*.svg`.", ""]
    return "\n".join(lines)


def main():
    os.makedirs(PLANS, exist_ok=True)
    os.makedirs(BRIEFS, exist_ok=True)
    specs, floors, rooms, apts = build_rooms()

    # ── SCHEDULE.csv ──────────────────────────────────────────────────────
    prop_floor = {"living": 70, "kitchen": 90, "bedroom": 40, "bathroom": 28, "entry": 18,
                  "store": 12, "wc": 8, "sales": 150, "stock": 40, "staff": 10,
                  "warehouse floor": 60, "loft": 30, "hoist office": 12,
                  "machine hall": 80, "joinery": 50, "paint shop": 40, "foreman office": 12,
                  "office floor": 30, "drawing office": 24, "records": 18, "lavatory block": 10,
                  "public hall": 40, "counter office": 20, "interview room": 12, "staff room": 10,
                  "workshop floor": 80, "tool store": 30, "bench room": 40,
                  "auction sales": 150, "auction stock": 40, "auction staff": 10, "auction wc": 8}
    sched_path = os.path.join(OUT, "SCHEDULE.csv")
    with open(sched_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["room_id", "building", "block", "floor", "apartment", "name", "kind",
                    "x0", "y0", "x1", "y1", "w", "d", "area_m2", "doors", "windows",
                    "loading_door", "required_props", "reachable"])
        for r in rooms:
            if r["kind"] == "stall":
                req = 45
            else:
                nm = r["name"].replace("auction ", "")
                req = prop_floor.get(nm, 12)
            w.writerow([r["id"], r["building"], r["block"], r["floor"], r["apartment"] or "",
                        r["name"], r["kind"], r["bounds"]["x0"], r["bounds"]["y0"],
                        r["bounds"]["x1"], r["bounds"]["y1"], r["w"], r["d"], r["area"],
                        r["doors"], r["windows"],
                        1 if (r.get("door") and r["door"].get("loading")) else 0,
                        req, int(r["reachable"])])

    # ── APARTMENTS.csv ────────────────────────────────────────────────────
    with open(os.path.join(OUT, "APARTMENTS.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["apartment_id", "building", "block", "level", "ffl", "index",
                    "archetype", "palette", "generation", "occupancy", "seed"])
        for a in sorted(apts.values(), key=lambda x: x["index"]):
            w.writerow([a["id"], a["building"], a["block"], a["level"], a["ffl"], a["index"],
                        a["archetype"], a["palette"], a["generation"], a["occupancy"], a["seed"]])

    # ── plans + PROGRAMME ─────────────────────────────────────────────────
    by_b = {}
    for r in rooms:
        by_b.setdefault(r["building"], []).append(r)
    site = (0.0, 0.0, 400.0, 320.0)
    for s in specs:
        s_rooms = by_b.get(s["id"], [])
        s["counted_rooms"] = len(s_rooms)
        s["apartments"] = [a["id"] for a in apts.values() if a["building"] == s["id"]]
        s["ffl"] = P.floor_levels(s)
        s["height"] = P.building_height(s)
        s["area_m2"] = round((s["x1"] - s["x0"]) * (s["y1"] - s["y0"]), 2)
        # floor plans
        for li in range(len(s["storeys"])):
            fid = f"{s['id']}-L{li+1:02d}"
            rs = [r for r in s_rooms if r["floor_id"] == fid]
            rects = [dict(name=r["name"], x0=r["bounds"]["x0"], y0=r["bounds"]["y0"],
                          x1=r["bounds"]["x1"], y1=r["bounds"]["y1"], w=r["w"], d=r["d"],
                          area=r["area"]) for r in rs]
            svg_plan(f"{s['id']} {s['name']} — L{li+1:02d} ({s['storeys'][li]['use']}, FFL {P.floor_levels(s)[li]:.2f})",
                     rects, (s["x0"] - 2, s["y0"] - 2, s["x1"] + 2, s["y1"] + 2),
                     os.path.join(PLANS, f"{s['id']}_L{li+1:02d}.svg"),
                     f"{len(rs)} rooms")
            json.dump(dict(building=s["id"], floor=li + 1, ffl=P.floor_levels(s)[li],
                           rooms=rects), open(os.path.join(PLANS, f"{s['id']}_L{li+1:02d}.json"), "w"), indent=1)
        # site plan: this building among its block
        blk = [b for b in specs if b["block"] == s["block"]]
        rects = [dict(name=b["id"], x0=b["x0"], y0=b["y0"], x1=b["x1"], y1=b["y1"],
                      w=b["x1"] - b["x0"], d=b["y1"] - b["y0"],
                      area=(b["x1"] - b["x0"]) * (b["y1"] - b["y0"])) for b in blk]
        svg_plan(f"{s['id']} — site plan, block {s['block']} ({P.BLOCK_NAMES[s['block']]})",
                 rects, site, os.path.join(PLANS, f"SITE_{s['id']}.svg"),
                 f"block {s['block']}, {len(blk)} buildings")
        open(os.path.join(BRIEFS, f"{s['id']}.md"), "w").write(
            brief(s, len(s_rooms), len(s["apartments"])))

    programme = dict(
        project="PORTUS", created="2026-10-19", units="metres",
        site=dict(w=400.0, h=320.0, area_ha=12.8, origin="basin SW corner",
                  north="+Y", up="+Z", water_z=0.0, land_z=2.40),
        basin=dict(x0=110.0, y0=30.0, x1=290.0, y1=120.0, w=180.0, d=90.0, depth=6.0, quay_top=2.40),
        counts=dict(buildings=len(specs), floors=len(floors), apartments=len(apts),
                    apartments_per_floor=round(len(apts) / sum(1 for f in floors if f["use"] == "residential"), 4),
                    rooms=len(rooms), shops=48, blocks=6,
                    warehouses=sum(1 for s in specs if s["kind"] == "warehouse"),
                    civic=sum(1 for s in specs if s["kind"] == "civic"),
                    market_stalls=sum(1 for r in rooms if r["kind"] == "stall")),
        blocks={b: dict(count=n, name=P.BLOCK_NAMES[b]) for b, n in P.BLOCK_ORDER},
        buildings=specs, floors=floors, rooms=rooms,
        apartments=[a for a in sorted(apts.values(), key=lambda x: x["index"])],
    )
    json.dump(programme, open(os.path.join(OUT, "PROGRAMME.json"), "w"), indent=1)

    sysd = systems()
    json.dump(sysd, open(os.path.join(OUT, "SYSTEMS.json"), "w"), indent=1)

    stats = dict(
        buildings=len(specs), floors=len(floors), apartments=len(apts),
        rooms=len(rooms), stalls=sum(1 for r in rooms if r["kind"] == "stall"),
        shops=len({r.get("shop") for r in rooms if r["kind"] == "shop_room"}),
        rooms_without_door=sum(1 for r in rooms if r["doors"] == 0 and r["kind"] != "stall"),
        rooms_without_window=sum(1 for r in rooms if r["windows"] == 0 and r["kind"] != "stall"),
        stalls_without_aisle_front=sum(1 for r in rooms if r["kind"] == "stall" and not (
            r["door"] and r["door"].get("open_front") and r["door"]["w"] >= 1.5)),
        unreachable=sum(1 for r in rooms if not r["reachable"]),
        plans_svg=len([f for f in os.listdir(PLANS) if f.endswith(".svg")]),
        tracks=len([t for t in sysd["rail"]["tracks"] if t["kind"] == "yard"]),
        moorings=len(sysd["moorings"]),
        archetypes=len({a["archetype"] for a in apts.values()}),
        palettes=len({a["palette"] for a in apts.values()}),
        generations=len({a["generation"] for a in apts.values()}),
        occupancies=len({a["occupancy"] for a in apts.values()}),
        unique_apartment_signatures=len({P.signature([dict(name=r["name"], x0=r["bounds"]["x0"],
                                                           y0=r["bounds"]["y0"], w=r["w"], d=r["d"])
                                                     for r in rooms if r["apartment"] == a["id"]])
                                         for a in apts.values()}),
    )
    json.dump(stats, open(os.path.join(OUT, "STATS.json"), "w"), indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
