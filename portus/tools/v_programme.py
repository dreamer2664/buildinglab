#!/usr/bin/env python3
"""v_programme.py — G1 arithmetic validator.

Recomputes every count from the emitted data (never trusts STATS.json) and
prints the block the packet asks for, then PASS or FAIL last.

    python3 portus/tools/v_programme.py
    python3 portus/tools/v_programme.py --design /path/to/portus/design   # for negative fixtures

Exit 0 on PASS, 2 on FAIL. Writes evidence/validation/v_programme.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DEFAULT_DESIGN = os.path.join(ROOT, "design")
EVID = os.path.join(ROOT, "evidence", "validation")

EXPECT = dict(buildings=48, floors=197, apartments=208, apartments_per_floor=2.00,
              rooms=1608, shops=48, warehouses=8, civic=5, moorings=6, tracks=6,
              blocks=6, stalls=80)


def load(design):
    prog = json.load(open(os.path.join(design, "PROGRAMME.json")))
    sysd = json.load(open(os.path.join(design, "SYSTEMS.json")))
    sched = list(csv.DictReader(open(os.path.join(design, "SCHEDULE.csv"))))
    apts = list(csv.DictReader(open(os.path.join(design, "APARTMENTS.csv"))))
    return prog, sysd, sched, apts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", default=DEFAULT_DESIGN)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    prog, sysd, sched, apts = load(args.design)
    checks, fails = [], []

    def check(name, got, want, tol=0.005):
        ok = abs(got - want) <= tol if isinstance(want, float) else got == want
        checks.append(dict(name=name, got=got, want=want, ok=bool(ok)))
        if not ok:
            fails.append(f"{name}: got {got!r}, required {want!r}")
        return ok

    # ── counts, recomputed from the data ─────────────────────────────────
    buildings = prog["buildings"]
    floors = prog["floors"]
    rooms = prog["rooms"]
    n_bld = len(buildings)
    n_floors = len(floors)
    n_apts = len(apts)
    res_floors = [f for f in floors if f["use"] == "residential"]
    apts_per_floor = n_apts / len(res_floors) if res_floors else 0.0
    n_rooms = len(rooms)
    n_stalls = sum(1 for r in rooms if r["kind"] == "stall")
    n_shops = len({r.get("shop") for r in rooms if r["kind"] == "shop_room"})
    n_ware = sum(1 for b in buildings if b["kind"] == "warehouse")
    n_civic = sum(1 for b in buildings if b["kind"] == "civic")
    n_moorings = len(sysd["moorings"])
    n_tracks = len([t for t in sysd["rail"]["tracks"] if t["kind"] == "yard"])
    blocks = sorted({b["block"] for b in buildings})
    by_block = Counter(b["block"] for b in buildings)

    no_door = [r for r in rooms if r["doors"] == 0 and r["kind"] != "stall"]
    no_win = [r for r in rooms if r["windows"] == 0 and r["kind"] != "stall"]
    unreach = [r for r in rooms if not r["reachable"]]
    bad_stall = [r for r in rooms if r["kind"] == "stall" and not (
        r.get("door") and r["door"].get("open_front") and r["door"]["w"] >= 1.5)]

    # 208×6 + 48×4 + 8×3 + 5×6 + 6×3 + 4×4 + 80
    expected_rooms = (n_apts * 6 + n_shops * 4 + n_ware * 3 + n_civic * 6 +
                      by_block.get("G", 0) * 3 + by_block.get("C", 0) * 4 + n_stalls)

    check("buildings", n_bld, EXPECT["buildings"])
    check("occupied floors", n_floors, EXPECT["floors"])
    check("apartments", n_apts, EXPECT["apartments"])
    check("apartments/floor", round(apts_per_floor, 2), EXPECT["apartments_per_floor"])
    check("rooms", n_rooms, EXPECT["rooms"])
    check("rooms == 208x6+48x4+8x3+5x6+6x3+4x4+80", n_rooms, expected_rooms)
    check("shops", n_shops, EXPECT["shops"])
    check("warehouses", n_ware, EXPECT["warehouses"])
    check("civic buildings", n_civic, EXPECT["civic"])
    check("mooring points", n_moorings, EXPECT["moorings"])
    check("rail tracks", n_tracks, EXPECT["tracks"])
    # the packet names seven quarters A-G but fixes the count at six street blocks;
    # the market hall (D) stands in its own square and is counted separately.
    street_blocks = [b for b in blocks if b != "D"]
    check("blocks", len(street_blocks), EXPECT["blocks"])
    check("quarters named", len(blocks), 7)
    check("market stalls", n_stalls, EXPECT["stalls"])
    check("rooms with 0 doors", len(no_door), 0)
    check("rooms with 0 windows", len(no_win), 0)
    check("unreachable rooms", len(unreach), 0)
    check("stalls without an aisle front", len(bad_stall), 0)

    # per-block counts fixed by the packet
    for blk, want, key in (("A", 8, "buildings"), ("B", 12, "buildings"), ("C", 4, "buildings"),
                           ("D", 1, "buildings"), ("E", 12, "buildings"),
                           ("F", 5, "buildings"), ("G", 6, "buildings")):
        check(f"block {blk} buildings", by_block.get(blk, 0), want)

    # apartments per block
    apt_block = Counter(a["block"] for a in apts)
    check("block B apartments", apt_block.get("B", 0), 96)
    check("block E apartments", apt_block.get("E", 0), 72)
    check("block F apartments", apt_block.get("F", 0), 40)

    # two apartments on every residential floor, no floor with 1 or 3
    per_floor = Counter(a["building"] + "-L" + f"{int(a['level'])+1:02d}" for a in apts)
    check("floors with != 2 apartments", sum(1 for v in per_floor.values() if v != 2), 0)

    # room schedule integrity
    ids = [r["id"] for r in rooms]
    check("duplicate room ids", len(ids) - len(set(ids)), 0)
    zero_area = [r for r in rooms if r["area"] <= 1.0]
    check("rooms with area <= 1 m2", len(zero_area), 0)
    outside = [r for r in rooms
               if not (0 <= r["bounds"]["x0"] <= 400 and 0 <= r["bounds"]["y0"] <= 320
                       and 0 <= r["bounds"]["x1"] <= 400 and 0 <= r["bounds"]["y1"] <= 320)]
    check("rooms outside the site", len(outside), 0)

    # variational law
    check("plan archetypes >= 10", len({a["archetype"] for a in apts}) >= 10, True)
    check("palettes >= 8", len({a["palette"] for a in apts}) >= 8, True)
    check("furnishing generations >= 5", len({a["generation"] for a in apts}) >= 5, True)
    check("occupancy types >= 4", len({a["occupancy"] for a in apts}) >= 4, True)

    # building rhythm triples must be 48 unique
    triples = {(tuple(s["h"] for s in b["storeys"]), b["module"], b["pitch"]) for b in buildings}
    check("unique building rhythm triples", len(triples), 48)

    # systems sanity that belongs to G1
    check("water level", sysd["water"]["level"], 0.0)
    check("rail gauge", sysd["rail"]["gauge"], 1.435)
    check("catenary height", sysd["rail"]["catenary_height"], 5.50)
    check("ships", len(sysd["ships"]), 3)
    check("cranes", len([c for c in sysd["cranes"] if c["type"] == "hammerhead"]), 4)
    check("gantry cranes", len([c for c in sysd["cranes"] if c["type"] == "gantry"]), 2)
    check("wall jib cranes", len([c for c in sysd["cranes"] if c["type"] == "wall_jib"]), 8)

    # ── report ───────────────────────────────────────────────────────────
    n = lambda k: next(c["got"] for c in checks if c["name"] == k)
    lines = [
        f"buildings ............ {n('buildings')}",
        f"occupied floors ...... {n('occupied floors')}",
        f"apartments ........... {n('apartments')}",
        f"apartments/floor ..... {n('apartments/floor'):.2f}",
        f"rooms ................ {n('rooms'):,}  "
        f"({n('apartments')}x6 + {n('shops')}x4 + {n('warehouses')}x3 + {n('civic buildings')}x6 "
        f"+ {by_block.get('G', 0)}x3 + {by_block.get('C', 0)}x4 + {n('market stalls')} stalls)",
        f"shops ................ {n('shops')}",
        f"warehouses ........... {n('warehouses')}",
        f"civic buildings ...... {n('civic buildings')}",
        f"mooring points ....... {n('mooring points')}",
        f"rail tracks .......... {n('rail tracks')}",
        f"street blocks ........ {n('blocks')}  (+ market square D: 1 building)",
        f"rooms with 0 doors ... {n('rooms with 0 doors')}",
        f"rooms with 0 windows . {n('rooms with 0 windows')}",
        f"unreachable rooms .... {n('unreachable rooms')}",
        f"stalls w/o aisle ..... {n('stalls without an aisle front')}",
        f"plan archetypes ...... {len({a['archetype'] for a in apts})}",
        f"palettes ............. {len({a['palette'] for a in apts})}",
        f"generations .......... {len({a['generation'] for a in apts})}",
        f"occupancies .......... {len({a['occupancy'] for a in apts})}",
        f"floor-plan SVGs ...... {len([f for f in os.listdir(os.path.join(args.design, 'plans')) if f.endswith('.svg')])}",
    ]
    if not args.quiet:
        print("\n".join(lines))
    for f in fails:
        print("FAIL:", f)
    ok = not fails
    os.makedirs(EVID, exist_ok=True)
    json.dump(dict(validator="v_programme", design=args.design, ok=ok,
                   checks=checks, fails=fails), open(os.path.join(EVID, "v_programme.json"), "w"), indent=1)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
