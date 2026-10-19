#!/usr/bin/env python3
"""
test_validators.py — Nine deliberate negative tests proving every validator in `townsquare/tools/`
fails loudly (non-zero exit code + `FAIL` last line) when given broken data, and passes (`PASS`)
on valid data (§30).
"""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PROG_PATH = ROOT / "design" / "PROGRAMME.json"


def run_validator(script: str, input_path: Path | None = None, extra_args: list[str] | None = None) -> tuple[int, str, str]:
    cmd = [sys.executable, str(TOOLS / script)]
    if input_path is not None:
        cmd += ["--input", str(input_path)]
    if extra_args:
        cmd += extra_args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main() -> int:
    base_prog = json.loads(PROG_PATH.read_text(encoding="utf-8"))
    results = []

    with tempfile.TemporaryDirectory(prefix="ts_neg_tests_") as tmpdir:
        tmp = Path(tmpdir)

        # 1. v_scale.py negative test: wrong storey height (3.60m residential) and wrong human height (2.10m)
        bad_scale = copy.deepcopy(base_prog)
        bad_scale["human_height_m"] = 2.10
        bad_scale["buildings"][0]["floors"][1]["storey_height_m"] = 3.60
        f_scale = tmp / "bad_scale.json"
        f_scale.write_text(json.dumps(bad_scale), encoding="utf-8")

        # 2. v_programme.py negative test: remove an apartment on B01_L02 and set a room window_count=0
        bad_prog = copy.deepcopy(base_prog)
        bad_prog["buildings"][0]["floors"][1]["apartments"].pop()
        bad_prog["buildings"][0]["floors"][1]["rooms"][1]["window_count"] = 0
        f_prog = tmp / "bad_prog.json"
        f_prog.write_text(json.dumps(bad_prog), encoding="utf-8")

        # 3. v_contact.py negative test: floating object (15 mm > 2 mm), coplanar pair, and backward wardrobe (F1, F2, F4)
        bad_contact = {
            "max_float_m": 0.015,
            "max_interpenetration_m": 0.004,
            "coplanar_pairs": 2,
            "zero_area_triangles": 1,
            "backward_facing_objects": 3,
            "blocked_shaft_rays": 1,
            "min_finish_overlap_m": 0.005,
            "max_terrain_flat_plane_m2": 4.5,
        }
        f_contact = tmp / "bad_contact.json"
        f_contact.write_text(json.dumps(bad_contact), encoding="utf-8")

        # 4. v_clearance.py negative test: blocked door swing (F5) and narrow dwelling path (0.42m < 0.60m)
        bad_clear = copy.deepcopy(base_prog)
        bad_clear["blocked_door_swings"] = 2
        bad_clear["min_dwelling_path_m"] = 0.42
        f_clear = tmp / "bad_clear.json"
        f_clear.write_text(json.dumps(bad_clear), encoding="utf-8")

        # 5. v_density.py negative test: sparse living room (12 props < 45 minimum, F17)
        bad_density = copy.deepcopy(base_prog)
        bad_density["buildings"][1]["floors"][1]["rooms"][2]["actual_props"] = 12
        f_density = tmp / "bad_density.json"
        f_density.write_text(json.dumps(bad_density), encoding="utf-8")

        # 6. v_distinct.py negative test: duplicate apartment arrangement signature (F13) & duplicate human identity in room (F16)
        bad_distinct = copy.deepcopy(base_prog)
        sig0 = bad_distinct["buildings"][0]["floors"][1]["apartments"][0]["arrangement_signature"]
        bad_distinct["buildings"][1]["floors"][1]["apartments"][0]["arrangement_signature"] = sig0
        bad_distinct["buildings"][0]["floors"][1]["rooms"][1]["people_identities"] = ["ID_01", "ID_01"]
        f_distinct = tmp / "bad_distinct.json"
        f_distinct.write_text(json.dumps(bad_distinct), encoding="utf-8")

        # 7. v_light.py negative test: buried emitter (2/8 clear rays, F7), camera inside wardrobe (F8), blown highlights (3.5%)
        bad_light = {
            "min_sources_per_room": 1,
            "min_emitter_clear_rays_of_8": 2,
            "max_blown_ratio": 0.035,
            "max_crushed_ratio": 0.045,
            "fireflies": 4,
            "practical_kelvin_range": [2600, 2900],
            "daylight_kelvin_range": [5800, 6200],
            "camera_sphere_0p5m_clear": False,
            "min_interior_camera_coverage": 0.25,
        }
        f_light = tmp / "bad_light.json"
        f_light.write_text(json.dumps(bad_light), encoding="utf-8")

        # 8. v_export.py negative test: 2,511 triangle mismatch on GLB re-import (F15) and lost material slots (F11)
        bad_export = {
            "expected_triangles": 449760,
            "reimported_triangles": 449751,
            "expected_materials": 22,
            "reimported_materials": 0,
            "expected_textures": 12,
            "reimported_textures": 12,
            "identifiable_levels": 6,
        }
        f_export = tmp / "bad_export.json"
        f_export.write_text(json.dumps(bad_export), encoding="utf-8")

        # 9. v_package.py negative test: unopened views, duplicate sha256, and missing views
        bad_package = {
            "expected_views": 271,
            "records": [
                {"view": "v1", "sha256": "dup", "opened": False, "observation": "", "critical_major_open": 1},
                {"view": "v2", "sha256": "dup", "opened": True, "observation": "ok", "critical_major_open": 0},
            ],
            "best_images": ["01.jpg"],
            "best_total_bytes": 95_000_000,
            "best_max_image_bytes": 6_000_000,
        }
        f_package = tmp / "bad_package.json"
        f_package.write_text(json.dumps(bad_package), encoding="utf-8")

        # 10. v_blind.py negative test: judge identifies 8/10 correctly (>= 7/10 fails G6)
        bad_blind = {
            "classes": {
                "interior": {"seed": 42, "trials": 10, "correct_identifications": 8, "reasons": ["Too clean"]}
            }
        }
        f_blind = tmp / "bad_blind.json"
        f_blind.write_text(json.dumps(bad_blind), encoding="utf-8")

        cases = [
            ("N1_v_scale", "v_scale.py", f_scale, []),
            ("N2_v_programme", "v_programme.py", f_prog, []),
            ("N3_v_contact", "v_contact.py", f_contact, []),
            ("N4_v_clearance", "v_clearance.py", f_clear, []),
            ("N5_v_density", "v_density.py", f_density, []),
            ("N6_v_distinct", "v_distinct.py", f_distinct, []),
            ("N7_v_light", "v_light.py", f_light, []),
            ("N8_v_export", "v_export.py", f_export, []),
            ("N9_v_package", "v_package.py", f_package, []),
            ("N10_v_blind", "v_blind.py", f_blind, ["--class", "interior"]),
        ]

        all_ok = True
        for name, script, bad_file, extra in cases:
            # First verify positive baseline passes
            rc_pos, out_pos, err_pos = run_validator(script, None, extra)
            pos_pass = (rc_pos == 0 and out_pos.splitlines()[-1] == "PASS")
            # Second verify negative test fails loudly
            rc_neg, out_neg, err_neg = run_validator(script, bad_file, extra)
            neg_Caught = (rc_neg != 0 and out_neg.splitlines()[-1] == "FAIL")

            status = "PASS" if (pos_pass and neg_Caught) else "FAIL"
            if status != "PASS":
                all_ok = False
            print(f"{name:18s} | pos_rc={rc_pos} ({out_pos.splitlines()[-1]}) | neg_rc={rc_neg} ({out_neg.splitlines()[-1]}) -> {status}")
            results.append({
                "test": name,
                "script": script,
                "positive_rc": rc_pos,
                "negative_rc": rc_neg,
                "negative_stderr": err_neg.splitlines()[:3],
                "status": status,
            })

    out_report = ROOT / "evidence" / "validation" / "negative_tests.json"
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(json.dumps({"tests": results, "status": "PASS" if all_ok else "FAIL"}, indent=2), encoding="utf-8")

    if not all_ok:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
