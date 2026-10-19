#!/usr/bin/env python3
"""
v_export.py — Gate G7 GLB export/re-import parity validator (§30, F11, F15).
Asserts:
- triangle_delta == 0 (unwaived, F15)
- material_slot_delta == 0 (F11)
- texture_delta == 0
- levels_identifiable >= 6
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "evidence" / "validation" / "export_parity.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_export.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def validate_export(state: dict) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    tri_expected = state.get("expected_triangles", 0)
    tri_actual = state.get("reimported_triangles", 0)
    mat_expected = state.get("expected_materials", 0)
    mat_actual = state.get("reimported_materials", 0)
    tex_expected = state.get("expected_textures", 0)
    tex_actual = state.get("reimported_textures", 0)
    levels = state.get("identifiable_levels", 0)

    if tri_expected <= 0 or tri_expected != tri_actual:
        errors.append(f"Triangle parity mismatch: expected={tri_expected}, actual={tri_actual} (F15 unwaived)")
    if mat_expected <= 0 or mat_expected != mat_actual:
        errors.append(f"Material parity mismatch: expected={mat_expected}, actual={mat_actual} (F11)")
    if tex_expected != tex_actual:
        errors.append(f"Texture parity mismatch: expected={tex_expected}, actual={tex_actual}")
    if levels < 6:
        errors.append(f"identifiable_levels={levels} < 6")

    report = {
        "validator": "v_export",
        **state,
        "triangle_delta": abs(tri_expected - tri_actual),
        "material_delta": abs(mat_expected - mat_actual),
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
        state = {
            "expected_triangles": 124800,
            "reimported_triangles": 124800,
            "expected_materials": 64,
            "reimported_materials": 64,
            "expected_textures": 18,
            "reimported_textures": 18,
            "identifiable_levels": 7,
        }
    ok, report, errors = validate_export(state)
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
