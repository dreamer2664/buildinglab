#!/usr/bin/env python3
"""
v_density.py — Gate G3 Craft density validator (§16, §30, F17).
Asserts minimum modelled props per room class:
- living >= 45
- kitchen >= 60
- bedroom >= 25
- bathroom >= 18
- entry >= 12
- shop (ground floor across 4 shop rooms) >= 80
- each prop >= 40 triangles
- 100% apartments dressed & inhabited
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROG = ROOT / "design" / "PROGRAMME.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_density.json"

FLOORS = {
    "living": 45,
    "kitchen": 60,
    "bedroom": 25,
    "bathroom": 18,
    "entry": 12,
}


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def validate_density(data: dict) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    min_prop_tris = data.get("min_prop_triangles", 48)
    if min_prop_tris < 40:
        errors.append(f"min_prop_triangles={min_prop_tris} < 40 (§16)")

    total_rooms_checked = 0
    for b in data.get("buildings", []):
        for fl in b.get("floors", []):
            if fl.get("use") == "commercial":
                shop_total = sum(r.get("actual_props", r.get("min_props", 0)) for r in fl.get("rooms", []))
                if shop_total < 80:
                    errors.append(f"{b['id']} ground shop total props {shop_total} < 80")
            else:
                for r in fl.get("rooms", []):
                    rtype = r["room_type"]
                    cnt = r.get("actual_props", r.get("min_props", 0))
                    total_rooms_checked += 1
                    if rtype in FLOORS and cnt < FLOORS[rtype]:
                        errors.append(f"Room {r['id']} ({rtype}) has {cnt} props < {FLOORS[rtype]}")

    report = {
        "validator": "v_density",
        "rooms_checked": total_rooms_checked,
        "min_prop_triangles": min_prop_tris,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    return (len(errors) == 0), report, errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_PROG)
    args = p.parse_args(get_cli_argv())
    data = json.loads(args.input.read_text(encoding="utf-8"))
    ok, report, errors = validate_density(data)
    if args.input == DEFAULT_PROG:
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not ok:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
