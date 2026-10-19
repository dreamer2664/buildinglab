#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design"
EVIDENCE = ROOT / "evidence"
EVIDENCE_UPPER = ROOT / "EVIDENCE"

def parse_args(default_input: Path, default_json_name: str):
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("--native", type=Path, default=ROOT / "source" / "NORDBAHNHOF.blend")
    p.add_argument("--input", type=Path, default=default_input)
    p.add_argument("--json", type=Path, default=EVIDENCE / default_json_name)
    p.add_argument("--class", dest="blind_class", type=str, default="all")
    p.add_argument("--trials", type=int, default=20)
    return p.parse_args(argv)

def write_report(report: dict, json_path: Path):
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    EVIDENCE_UPPER.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_UPPER / json_path.name).write_text(json.dumps(report, indent=2), encoding="utf-8")

def main() -> int:
    args = parse_args(DESIGN / "PROGRAMME.json", "v_circulation.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    cc = d.get("contact_circulation", d)
    errors = []

    if cc.get("min_passenger_path_mm", 0) < 1200:
        errors.append(f"min_passenger_path_mm {cc.get('min_passenger_path_mm')} < 1200 mm")
    if cc.get("min_platform_clear_behind_yellow_line_mm", 0) < 1500:
        errors.append(f"min_platform_clear_behind_yellow_line_mm {cc.get('min_platform_clear_behind_yellow_line_mm')} < 1500 mm")
    if abs(cc.get("yellow_line_offset_from_edge_mm", 0) - 500) > 10:
        errors.append(f"yellow_line_offset_from_edge_mm {cc.get('yellow_line_offset_from_edge_mm')} != 500 mm")
    if cc.get("min_concourse_main_axis_mm", 0) < 3000:
        errors.append(f"min_concourse_main_axis_mm {cc.get('min_concourse_main_axis_mm')} < 3000 mm")
    if cc.get("min_retail_aisle_mm", 0) < 1000:
        errors.append(f"min_retail_aisle_mm {cc.get('min_retail_aisle_mm')} < 1000 mm")
    if cc.get("door_swing_clear_deg", 0) < 90.0:
        errors.append(f"door_swing_clear_deg {cc.get('door_swing_clear_deg')} < 90 deg")
    if not (0.15 <= cc.get("stair_riser_m", 0) <= 0.17):
        errors.append(f"stair_riser_m {cc.get('stair_riser_m')} outside 0.15-0.17 m")
    if not (0.28 <= cc.get("stair_tread_m", 0) <= 0.32):
        errors.append(f"stair_tread_m {cc.get('stair_tread_m')} outside 0.28-0.32 m")
    if cc.get("stair_headroom_m", 0) < 2.20:
        errors.append(f"stair_headroom_m {cc.get('stair_headroom_m')} < 2.20 m")
    if abs(cc.get("escalator_angle_deg", 0) - 30.0) > 0.5:
        errors.append(f"escalator_angle_deg {cc.get('escalator_angle_deg')} outside 30 +-0.5 deg")
    if cc.get("escalator_step_width_mm", 0) != 1000:
        errors.append(f"escalator_step_width_mm {cc.get('escalator_step_width_mm')} != 1000 mm")
    if cc.get("min_seating_clear_front_m", 0) < 0.60:
        errors.append(f"min_seating_clear_front_m {cc.get('min_seating_clear_front_m')} < 0.60 m")
    if not cc.get("all_luggage_supported", False):
        errors.append("all_luggage_supported is False")

    ok = len(errors) == 0
    report = {"validator": "v_circulation", "status": "PASS" if ok else "FAIL", "errors": errors}
    write_report(report, args.json)
    print(f"v_circulation: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
