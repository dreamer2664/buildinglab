#!/usr/bin/env python3
"""
v_clearance.py — Gate G2 Door swings, circulation paths, stairs & handrails (§16, §30, F5).
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROG = ROOT / "design" / "PROGRAMME.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_clearance.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def validate_clearance(data: dict) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    blocked_swings = data.get("blocked_door_swings", 0)
    min_dwelling_path_m = data.get("min_dwelling_path_m", 0.85)
    min_public_path_m = data.get("min_public_path_m", 1.20)
    min_market_aisle_m = data.get("min_market_aisle_m", 2.20)
    stair_riser_m = data.get("stair_riser_m", 0.17)
    stair_tread_m = data.get("stair_tread_m", 0.28)
    stair_headroom_m = data.get("stair_headroom_m", 2.25)
    handrail_height_m = data.get("handrail_height_m", 0.90)
    handrail_both_sides = data.get("handrail_both_sides", True)

    if blocked_swings > 0:
        errors.append(f"blocked_door_swings={blocked_swings} (90 deg arc must be clear, F5)")
    if min_dwelling_path_m < 0.60:
        errors.append(f"min_dwelling_path_m={min_dwelling_path_m:.2f}m < 0.60m")
    if min_public_path_m < 0.90:
        errors.append(f"min_public_path_m={min_public_path_m:.2f}m < 0.90m")
    if min_market_aisle_m < 1.50:
        errors.append(f"min_market_aisle_m={min_market_aisle_m:.2f}m < 1.50m")
    if not (0.16 <= stair_riser_m <= 0.18):
        errors.append(f"stair_riser_m={stair_riser_m:.3f}m outside 0.16-0.18m")
    if not (0.26 <= stair_tread_m <= 0.30):
        errors.append(f"stair_tread_m={stair_tread_m:.3f}m outside 0.26-0.30m")
    if stair_headroom_m < 2.0:
        errors.append(f"stair_headroom_m={stair_headroom_m:.2f}m < 2.00m")
    if not handrail_both_sides or abs(handrail_height_m - 0.90) > 0.03:
        errors.append(f"handrail invalid (both_sides={handrail_both_sides}, height={handrail_height_m}m)")

    for b in data.get("buildings", []):
        for fl in b.get("floors", []):
            for r in fl.get("rooms", []):
                if min(r["width"], r["depth"]) < 0.95:
                    errors.append(f"Room {r['id']} narrow dimension {min(r['width'], r['depth']):.2f}m blocks 0.90m door + 0.60m path")

    report = {
        "validator": "v_clearance",
        "blocked_door_swings": blocked_swings,
        "min_dwelling_path_m": min_dwelling_path_m,
        "min_public_path_m": min_public_path_m,
        "min_market_aisle_m": min_market_aisle_m,
        "stair_riser_m": stair_riser_m,
        "stair_tread_m": stair_tread_m,
        "stair_headroom_m": stair_headroom_m,
        "handrail_height_m": handrail_height_m,
        "handrail_both_sides": handrail_both_sides,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    return (len(errors) == 0), report, errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_PROG)
    args = p.parse_args(get_cli_argv())
    data = json.loads(args.input.read_text(encoding="utf-8"))
    ok, report, errors = validate_clearance(data)
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
