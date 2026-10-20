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
    args = parse_args(DESIGN / "PROGRAMME.json", "v_scale.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    errors = []

    fp = d.get("footprint_m", [0, 0])
    if abs(fp[0] - 240.0) > 0.05 or abs(fp[1] - 120.0) > 0.05:
        errors.append(f"Footprint {fp} outside 240x120 +-0.05 m")
    sh = d.get("shed_m", [0, 0])
    if abs(sh[0] - 180.0) > 0.03 or abs(sh[1] - 84.0) > 0.03:
        errors.append(f"Shed {sh} outside 180x84 +-0.03 m")
    if abs(d.get("shed_ridge_z_m", 0) - 26.0) > 0.03:
        errors.append(f"Shed ridge {d.get('shed_ridge_z_m')} outside +26.0 +-0.03 m")
    if abs(d.get("shed_eaves_z_m", 0) - 14.0) > 0.03:
        errors.append(f"Shed eaves {d.get('shed_eaves_z_m')} outside +14.0 +-0.03 m")
    if abs(d.get("platform_length_m", 0) - 180.0) > 0.10:
        errors.append(f"Platform length {d.get('platform_length_m')} outside 180.0 +-0.10 m")
    for ph in d.get("platform_heights_mm", []):
        if min(abs(ph - 550), abs(ph - 760)) > 10:
            errors.append(f"Platform height {ph} mm outside 550/760 +-10 mm")
    if abs(d.get("track_gauge_mm", 0) - 1435.0) > 2.0:
        errors.append(f"Track gauge {d.get('track_gauge_mm')} mm outside 1435 +-2 mm")
    st = d.get("storey_clear_heights_m", {})
    for k, target in [("L0", 6.40), ("L1", 4.60), ("B1", 4.20), ("B2", 4.80)]:
        if abs(st.get(k, 0) - target) > 0.05:
            errors.append(f"Storey {k} height {st.get(k)} outside {target} +-0.05 m")
    if abs(d.get("column_grid_m", 0) - 21.0) > 0.02:
        errors.append(f"Column grid {d.get('column_grid_m')} outside 21.0 +-0.02 m")
    if abs(d.get("human_height_m", 0) - 1.75) > 0.08:
        errors.append(f"Human height {d.get('human_height_m')} outside 1.75 +-0.08 m")
    if abs(d.get("eye_height_m", 0) - 1.62) > 0.02:
        errors.append(f"Eye height {d.get('eye_height_m')} outside 1.62 +-0.02 m")
    if abs(d.get("seat_height_m", 0) - 0.45) > 0.010:
        errors.append(f"Seat height {d.get('seat_height_m')} outside 0.45 +-0.010 m")
    if abs(d.get("handrail_height_m", 0) - 0.90) > 0.010:
        errors.append(f"Handrail height {d.get('handrail_height_m')} outside 0.90 +-0.010 m")
    if abs(d.get("clock_dial_m", 0) - 3.20) > 0.005:
        errors.append(f"Clock dial {d.get('clock_dial_m')} outside 3.20 +-0.005 m")

    ok = len(errors) == 0
    report = {"validator": "v_scale", "status": "PASS" if ok else "FAIL", "errors": errors}
    write_report(report, args.json)
    print(f"v_scale: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
