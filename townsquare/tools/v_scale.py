#!/usr/bin/env python3
"""
v_scale.py — Gate G1/G2 Scale and Construction tolerances (§16, §30).
Works under both `python3` and `blender --background --python-exit-code 1 --python`.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROG = ROOT / "design" / "PROGRAMME.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_scale.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def validate_scale(data: dict) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    sq = data.get("square", {})
    if abs(sq.get("clear_width_m", 0.0) - 64.0) > 1e-3 or abs(sq.get("clear_depth_m", 0.0) - 52.0) > 1e-3:
        errors.append(f"Square dimensions {sq.get('clear_width_m')}x{sq.get('clear_depth_m')} != 64x52m")
    if sq.get("origin") != [0.0, 0.0, 0.0]:
        errors.append(f"Origin {sq.get('origin')} != [0,0,0]")
    if abs(sq.get("christmas_tree_height_m", 0.0) - 11.0) > 0.25:
        errors.append(f"Christmas tree height {sq.get('christmas_tree_height_m')}m outside 11.0m tolerance")

    # Check Blender unit settings if running inside Blender with a loaded scene
    unit_system = "METRIC"
    scale_length = data.get("unit_scale_length", 1.0)
    if abs(scale_length - 1.0) > 1e-6:
        errors.append(f"unit_scale_length={scale_length} != 1.0")
    try:
        import bpy  # type: ignore
        if bpy.context and bpy.context.scene:
            us = bpy.context.scene.unit_settings
            unit_system = us.system
            if us.system != "METRIC" or abs(us.scale_length - 1.0) > 1e-5:
                errors.append(f"Blender scene units={us.system} scale={us.scale_length} (expected METRIC, 1.0)")
            for obj in bpy.context.scene.objects:
                if obj.get("role") == "human":
                    h = obj.dimensions.z
                    if not (1.65 <= h <= 1.85) and not obj.get("is_child", False):
                        errors.append(f"Human {obj.name} height {h:.3f}m outside 1.75±0.10m")
    except ImportError:
        pass

    for b in data.get("buildings", []):
        for fl in b.get("floors", []):
            sh = fl.get("storey_height_m", 0.0)
            ch = fl.get("ceiling_m", 0.0)
            slab = fl.get("slab_thickness_m", 0.22)
            if abs(slab - 0.22) > 0.01:
                errors.append(f"{fl['id']} slab {slab}m outside 0.22±0.01m")
            if fl.get("use") == "commercial":
                if abs(sh - 4.20) > 0.10:
                    errors.append(f"{fl['id']} commercial storey {sh}m outside 4.20±0.10m")
                if not (3.60 <= ch <= 3.80):
                    errors.append(f"{fl['id']} commercial ceiling {ch}m outside 3.60+0.20/-0.00m")
            else:
                if abs(sh - 3.20) > 0.05:
                    errors.append(f"{fl['id']} residential storey {sh}m outside 3.20±0.05m")
                if not (2.70 <= ch <= 2.80):
                    errors.append(f"{fl['id']} residential ceiling {ch}m outside 2.70+0.10/-0.00m")

    human_h = data.get("human_height_m", 1.75)
    if abs(human_h - 1.75) > 0.10:
        errors.append(f"human_height_m={human_h} outside 1.75±0.10m")
    door_w, door_h = data.get("door_opening_m", [0.90, 2.10])
    if abs(door_w - 0.90) > 0.02 or abs(door_h - 2.10) > 0.02:
        errors.append(f"door_opening_m={[door_w, door_h]} outside 0.90x2.10±0.02m")

    report = {
        "validator": "v_scale",
        "unit_system": unit_system,
        "scale_length": scale_length,
        "square_m": [sq.get("clear_width_m"), sq.get("clear_depth_m")],
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    return (len(errors) == 0), report, errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_PROG)
    args = p.parse_args(get_cli_argv())
    data = json.loads(args.input.read_text(encoding="utf-8"))
    ok, report, errors = validate_scale(data)
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
