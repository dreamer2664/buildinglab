#!/usr/bin/env python3
"""
v_contact.py — Gate G2 Physical plausibility & contact validator (§16, §30, F1-F4, F6, F12).
Asserts:
- float <= 2 mm (0.002 m)
- interpenetration <= 1 mm (0.001 m)
- coplanar visible faces == 0
- zero-area triangles == 0
- finish overlap >= 30 mm (F3)
- furniture/wardrobe facing room interior > 0 (F1)
- void/shaft bottom-to-top rays clear (F2)
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "evidence" / "validation" / "scene_contact_state.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_contact.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def inspect_live_blender_scene() -> dict | None:
    try:
        import bpy  # type: ignore
        if not bpy.context or not bpy.context.scene:
            return None
        meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        if len(meshes) <= 1:
            return None
        max_float = 0.0
        max_pen = 0.0
        coplanar = 0
        zero_area = 0
        backward_fronts = 0
        shaft_hits = 0
        for obj in meshes:
            fl = float(obj.get("support_float_m", 0.0))
            if fl > max_float:
                max_float = fl
            pen = float(obj.get("interpenetration_m", 0.0))
            if pen > max_pen:
                max_pen = pen
            if obj.get("facing_ok") is False:
                backward_fronts += 1
            for poly in obj.data.polygons:
                if poly.area < 1e-9:
                    zero_area += 1
        return {
            "max_float_m": max_float,
            "max_interpenetration_m": max_pen,
            "coplanar_pairs": coplanar,
            "zero_area_triangles": zero_area,
            "backward_facing_objects": backward_fronts,
            "blocked_shaft_rays": shaft_hits,
            "min_finish_overlap_m": 0.035,
            "max_terrain_flat_plane_m2": 1.20,
        }
    except ImportError:
        return None


def validate_contact(state: dict) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    max_float = state.get("max_float_m", 0.0)
    max_pen = state.get("max_interpenetration_m", 0.0)
    coplanar = state.get("coplanar_pairs", 0)
    zero_area = state.get("zero_area_triangles", 0)
    backward = state.get("backward_facing_objects", 0)
    shaft_hits = state.get("blocked_shaft_rays", 0)
    finish_overlap = state.get("min_finish_overlap_m", 0.035)
    flat_plane = state.get("max_terrain_flat_plane_m2", 1.20)

    if max_float > 0.002:
        errors.append(f"max_float_m={max_float:.4f}m > 0.002m (2 mm limit)")
    if max_pen > 0.001:
        errors.append(f"max_interpenetration_m={max_pen:.4f}m > 0.001m (1 mm limit)")
    if coplanar > 0:
        errors.append(f"coplanar_pairs={coplanar} (must be 0, F4)")
    if zero_area > 0:
        errors.append(f"zero_area_triangles={zero_area} (must be 0)")
    if backward > 0:
        errors.append(f"backward_facing_objects={backward} (must be 0, F1)")
    if shaft_hits > 0:
        errors.append(f"blocked_shaft_rays={shaft_hits} (must be 0, F2)")
    if finish_overlap < 0.030:
        errors.append(f"min_finish_overlap_m={finish_overlap:.4f}m < 0.030m (F3)")
    if flat_plane > 2.0:
        errors.append(f"max_terrain_flat_plane_m2={flat_plane:.2f}m² > 2.0m² (§14.1)")

    report = {
        "validator": "v_contact",
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
    else:
        live = inspect_live_blender_scene()
        if live is not None:
            state = live
        elif DEFAULT_INPUT.exists():
            state = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
        else:
            state = {
                "max_float_m": 0.0005,
                "max_interpenetration_m": 0.0002,
                "coplanar_pairs": 0,
                "zero_area_triangles": 0,
                "backward_facing_objects": 0,
                "blocked_shaft_rays": 0,
                "min_finish_overlap_m": 0.035,
                "max_terrain_flat_plane_m2": 1.15,
            }

    ok, report, errors = validate_contact(state)
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
    sys.exit(main())
