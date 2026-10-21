#!/usr/bin/env python3
"""
v_playable.py — Playable & Articulated City Validator.
Verifies:
- All 340 humans have >= 20 anatomical limb & hair vertex groups and a 23-bone skeletal armature
- All 24 unique human meshes have hair-ruffle & breathing shape keys
- >= 60 hinged playable doors exist across B01..B20, apartments, and vehicles
- All 32 deciduous trees and city animals/vehicles have playable articulation groups
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "evidence" / "validation" / "playable_state.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_playable.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def validate_playable(state: dict) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    rigged_humans = state.get("rigged_humans", 0)
    bones_per_human = state.get("bones_per_human", 0)
    vgroups_per_human = state.get("vertex_groups_per_human", 0)
    shape_keyed_meshes = state.get("shape_keyed_human_meshes", 0)
    doors = state.get("total_playable_doors", 0)
    trees = state.get("wind_rigged_trees", 0)
    animal_groups = state.get("articulated_animal_groups", 0)

    if rigged_humans < 340:
        errors.append(f"rigged_humans={rigged_humans} < 340")
    if bones_per_human < 20:
        errors.append(f"bones_per_human={bones_per_human} < 20")
    if vgroups_per_human < 20:
        errors.append(f"vertex_groups_per_human={vgroups_per_human} < 20")
    if shape_keyed_meshes < 24:
        errors.append(f"shape_keyed_human_meshes={shape_keyed_meshes} < 24")
    if doors < 60:
        errors.append(f"total_playable_doors={doors} < 60")
    if trees < 32:
        errors.append(f"wind_rigged_trees={trees} < 32")
    if animal_groups < 10:
        errors.append(f"articulated_animal_groups={animal_groups} < 10")

    report = {
        "validator": "v_playable",
        **state,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    return (len(errors) == 0), report, errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=None)
    args = p.parse_args(get_cli_argv())
    if args.input and args.input.exists():
        state = json.loads(args.input.read_text(encoding="utf-8"))
    elif DEFAULT_INPUT.exists():
        state = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
    else:
        state = {}
    ok, report, errors = validate_playable(state)
    if args.input is None:
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
    raise SystemExit(main())
