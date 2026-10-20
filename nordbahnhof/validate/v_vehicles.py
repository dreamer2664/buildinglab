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
    args = parse_args(DESIGN / "TIMETABLE.json", "v_vehicles.json")
    tt = json.loads(args.input.read_text(encoding="utf-8"))
    trains = tt.get("trains", [])
    errors = []

    if len(trains) != 6:
        errors.append(f"Train count {len(trains)} != 6")
    vehicles = [v for t in trains for v in t.get("vehicles", [])]
    if len(vehicles) != 34:
        errors.append(f"Vehicle count {len(vehicles)} != 34")
    for t in trains:
        if not (1 <= t.get("platform", 0) <= 8):
            errors.append(f"Train {t['train_id']} platform {t.get('platform')} outside 1..8")
        for v in t.get("vehicles", []):
            vid = v["vehicle_id"]
            if abs(v.get("wheel_rail_gap_mm", 9.0)) > 0.1:
                errors.append(f"Vehicle {vid} wheel_rail_gap_mm {v.get('wheel_rail_gap_mm')} > 0.1 mm")
            if not v.get("coupling_closed", False):
                errors.append(f"Vehicle {vid} coupling not closed")
            if not v.get("buffers_touching", False):
                errors.append(f"Vehicle {vid} buffers not touching")
            if "pantograph_contact_z_m" in v and abs(v["pantograph_contact_z_m"] - 5.50) > 0.02:
                errors.append(f"Vehicle {vid} pantograph Z {v['pantograph_contact_z_m']} != 5.50 m")

    ok = len(errors) == 0
    report = {"validator": "v_vehicles", "status": "PASS" if ok else "FAIL", "train_count": len(trains), "vehicle_count": len(vehicles), "errors": errors}
    write_report(report, args.json)
    print(f"v_vehicles: {'PASS' if ok else 'FAIL'} ({len(trains)} trains, {len(vehicles)} vehicles, {len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
