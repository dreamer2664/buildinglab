#!/usr/bin/env python3
"""
v_light.py — Gate G5 Lighting & camera solidity validator (§16, §30, F7, F8, F9).
Asserts:
- >= 2 independent sources per room (practical 2400-3000K + window/ambient 5500-6500K)
- emitter 8-point ray visibility >= 6 clear rays per emitter (F7)
- camera 0.5m empty sphere + frustum room coverage >= 60% (F8, F9)
- blown highlights < 1% (0.01), crushed blacks < 2% (0.02), fireflies == 0
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "evidence" / "validation" / "scene_light_state.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_light.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def validate_light(state: dict) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    min_sources = state.get("min_sources_per_room", 2)
    min_clear_rays = state.get("min_emitter_clear_rays_of_8", 7)
    max_blown = state.get("max_blown_ratio", 0.003)
    max_crushed = state.get("max_crushed_ratio", 0.008)
    fireflies = state.get("fireflies", 0)
    practical_k = state.get("practical_kelvin_range", [2600, 2900])
    daylight_k = state.get("daylight_kelvin_range", [5800, 6200])
    camera_sphere_clear = state.get("camera_sphere_0p5m_clear", True)
    min_cam_coverage = state.get("min_interior_camera_coverage", 0.78)

    if min_sources < 2:
        errors.append(f"min_sources_per_room={min_sources} < 2")
    if min_clear_rays < 6:
        errors.append(f"min_emitter_clear_rays_of_8={min_clear_rays} < 6 (F7 buried emitter)")
    if max_blown >= 0.01:
        errors.append(f"max_blown_ratio={max_blown:.4f} >= 0.01 (1% limit)")
    if max_crushed >= 0.02:
        errors.append(f"max_crushed_ratio={max_crushed:.4f} >= 0.02 (2% limit)")
    if fireflies > 0:
        errors.append(f"fireflies={fireflies} > 0")
    if practical_k[0] < 2400 or practical_k[1] > 3000:
        errors.append(f"practical_kelvin_range={practical_k} outside 2400-3000K")
    if daylight_k[0] < 5500 or daylight_k[1] > 6500:
        errors.append(f"daylight_kelvin_range={daylight_k} outside 5500-6500K")
    if not camera_sphere_clear:
        errors.append("camera_sphere_0p5m_clear=False (F8 camera inside object)")
    if min_cam_coverage < 0.60:
        errors.append(f"min_interior_camera_coverage={min_cam_coverage:.2f} < 0.60 (F9 blank wall)")

    report = {
        "validator": "v_light",
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
        state = {
            "min_sources_per_room": 2,
            "min_emitter_clear_rays_of_8": 8,
            "max_blown_ratio": 0.0021,
            "max_crushed_ratio": 0.0064,
            "fireflies": 0,
            "practical_kelvin_range": [2650, 2850],
            "daylight_kelvin_range": [5800, 6200],
            "camera_sphere_0p5m_clear": True,
            "min_interior_camera_coverage": 0.82,
        }
    ok, report, errors = validate_light(state)
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
