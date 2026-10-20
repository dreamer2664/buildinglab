#!/usr/bin/env python3
"""
v_programme.py — Gate G1 Programme validator (§21, §30).
Works under both `python3` and `blender --background --python-exit-code 1 --python`.
"""
from __future__ import annotations
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROG = ROOT / "design" / "PROGRAMME.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_programme.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_PROG)
    p.add_argument("--people", action="store_true")
    return p.parse_args(get_cli_argv())


def validate_programme(data: dict, check_people: bool = False) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    buildings = data.get("buildings", [])
    n_buildings = len(buildings)
    res_floors = 0
    apartments = 0
    apt_rooms = 0
    shop_rooms = 0
    landings = 0
    zero_door_rooms = 0
    zero_window_rooms = 0
    unreachable_rooms = 0
    min_occ_ratio = 1.0
    every_res_floor_has_2 = True

    required_apt_types = {"entry", "living", "kitchen", "bedroom", "bathroom", "wc", "storage"}

    footprints = []
    for b in buildings:
        cx, cy = b["center"]
        hw, hd = b["width"] / 2.0, b["depth"] / 2.0
        footprints.append((b["id"], cx - hw, cy - hd, cx + hw, cy + hd))
    for i in range(len(footprints)):
        id1, x1a, y1a, x1b, y1b = footprints[i]
        for j in range(i + 1, len(footprints)):
            id2, x2a, y2a, x2b, y2b = footprints[j]
            dx = max(0.0, max(x1a - x2b, x2a - x1b))
            dy = max(0.0, max(y1a - y2b, y2a - y1b))
            gap = (dx * dx + dy * dy) ** 0.5
            if gap < 0.50:
                errors.append(f"Buildings {id1} and {id2} share/collide party wall (gap={gap:.2f}m)")

    for b in buildings:
        for fl in b.get("floors", []):
            rooms = fl.get("rooms", [])
            occ_ratio = fl.get("occupied_ratio", 0.0)
            if occ_ratio < min_occ_ratio:
                min_occ_ratio = occ_ratio
            if occ_ratio < 0.70:
                errors.append(f"{fl['id']} occupied_ratio {occ_ratio:.2f} < 0.70")

            room_ids = {r["id"] for r in rooms}
            adj: dict[str, set[str]] = {r["id"]: set() for r in rooms}
            entry_nodes: set[str] = set()
            for r in rooms:
                rid = r["id"]
                if r.get("door_count", 0) <= 0:
                    zero_door_rooms += 1
                if r.get("window_count", 0) <= 0:
                    zero_window_rooms += 1
                if r["room_type"] in ("landing", "shop_sales"):
                    entry_nodes.add(rid)
                for target in r.get("connects_to", []):
                    if target in room_ids:
                        adj[rid].add(target)
                        adj[target].add(rid)

            visited: set[str] = set()
            q = collections.deque(entry_nodes)
            while q:
                curr = q.popleft()
                if curr in visited:
                    continue
                visited.add(curr)
                for nxt in adj.get(curr, ()):
                    if nxt not in visited:
                        q.append(nxt)
            unreach = len(room_ids - visited)
            unreachable_rooms += unreach

            if fl.get("use") == "commercial":
                for r in rooms:
                    if r["room_type"].startswith("shop_"):
                        shop_rooms += 1
            else:
                res_floors += 1
                apts = fl.get("apartments", [])
                apartments += len(apts)
                if len(apts) != 2:
                    every_res_floor_has_2 = False
                    errors.append(f"{fl['id']} has {len(apts)} apartments (expected 2)")
                for apt in apts:
                    aid = apt["id"]
                    arooms = [r for r in rooms if r.get("apartment") == aid]
                    if len(arooms) < 5:
                        errors.append(f"{aid} has {len(arooms)} rooms (<5)")
                    rtypes = {r["room_type"] for r in arooms}
                    missing_t = required_apt_types - rtypes
                    if missing_t:
                        errors.append(f"{aid} missing room types: {sorted(missing_t)}")
                for r in rooms:
                    if r["room_type"] == "landing":
                        landings += 1
                    else:
                        apt_rooms += 1

    apts_per_floor = (apartments / res_floors) if res_floors else 0.0
    floor_area_pass = min_occ_ratio >= 0.70

    if n_buildings not in (12, 20):
        errors.append(f"buildings={n_buildings} (expected 12 or 20)")
    expected_res = 55 if n_buildings == 12 else 88
    expected_apts = expected_res * 2
    expected_shops = n_buildings * 4
    if res_floors != expected_res:
        errors.append(f"residential_floors={res_floors} (expected {expected_res})")
    if apartments != expected_apts or not every_res_floor_has_2:
        errors.append(f"apartments={apartments} (expected {expected_apts}, 2.00/floor)")
    if apt_rooms < expected_apts * 6:
        errors.append(f"apartment_rooms={apt_rooms} (expected >= {expected_apts * 6})")
    if shop_rooms != expected_shops:
        errors.append(f"shop_rooms={shop_rooms} (expected {expected_shops})")
    if landings != expected_res:
        errors.append(f"landings={landings} (expected {expected_res})")
    if zero_door_rooms != 0:
        errors.append(f"zero_door_rooms={zero_door_rooms}")
    if zero_window_rooms != 0:
        errors.append(f"zero_window_rooms={zero_window_rooms}")
    if unreachable_rooms != 0:
        errors.append(f"unreachable_rooms={unreachable_rooms}")

    if check_people:
        pprog = data.get("people_programme", {})
        if pprog.get("total_people", 0) < 220 or pprog.get("indoors", 0) < 110 or pprog.get("distinct_identities", 0) < 40:
            errors.append("people_programme below §14.4 minimums")

    metrics = {
        "buildings": n_buildings,
        "residential_floors": res_floors,
        "apartments": apartments,
        "apartments_per_floor": round(apts_per_floor, 2),
        "apartment_rooms": apt_rooms,
        "shop_rooms": shop_rooms,
        "landings": landings,
        "rooms_with_0_doors": zero_door_rooms,
        "rooms_with_0_windows": zero_window_rooms,
        "unreachable_rooms": unreachable_rooms,
        "min_occupied_ratio": round(min_occ_ratio, 4),
        "floor_area_balance": "PASS" if floor_area_pass else "FAIL",
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    return (len(errors) == 0), metrics, errors


def main() -> int:
    args = parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    ok, m, errors = validate_programme(data, check_people=args.people)

    avg_rooms = m["apartment_rooms"] / m["apartments"] if m["apartments"] else 0.0
    print(f"buildings ............ {m['buildings']}")
    print(f"residential floors ... {m['residential_floors']}   (must equal 55)")
    print(f"apartments ........... {m['apartments']}  (must equal 2 × floors)")
    print(f"apartments/floor ..... {m['apartments_per_floor']:.2f} (every residential floor)")
    print(f"apartment rooms ...... {m['apartment_rooms']}  (>= 5 per apartment; {avg_rooms:.2f} average)")
    print(f"shop rooms ........... {m['shop_rooms']}   (12 shops × 4)")
    print(f"landings ............. {m['landings']}")
    print(f"rooms with 0 doors ... {m['rooms_with_0_doors']}")
    print(f"rooms with 0 windows . {m['rooms_with_0_windows']}")
    print(f"unreachable rooms .... {m['unreachable_rooms']}")
    print(f"floor area balance ... {m['floor_area_balance']} (no floor plate < 70 % occupied)")

    if args.input == DEFAULT_PROG:
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(m, indent=2), encoding="utf-8")

    if not ok:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
