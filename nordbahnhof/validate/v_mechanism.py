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
    args = parse_args(DESIGN / "TIMETABLE.json", "v_mechanism.json")
    tt = json.loads(args.input.read_text(encoding="utf-8"))
    prog = json.loads((DESIGN / "PROGRAMME.json").read_text(encoding="utf-8"))
    errors = []

    clocks = tt.get("clocks", {})
    if clocks.get("count") != 4 or clocks.get("parts_per_clock") != 240:
        errors.append("Clocks count != 4 or parts_per_clock != 240")
    if not clocks.get("escapement_modelled", False):
        errors.append("Clock escapement not modelled")
    if clocks.get("displayed_time") != tt.get("scene_time", "16:40:00"):
        errors.append("Clock displayed_time != scene_time")
    if not clocks.get("seconds_hand_advances_in_animation", False):
        errors.append("Clock seconds hand does not advance in animation")

    board = tt.get("departure_board", {})
    tiles = board.get("tiles", [])
    if len(tiles) != 240 or not board.get("driven_by_timetable_json", False):
        errors.append(f"Departure board tiles {len(tiles)} != 240 or not driven by TIMETABLE.json (F27)")
    if any(not t.get("flip_test_verified", False) for t in tiles):
        errors.append("One or more departure board tiles failed flip test")

    if prog.get("hinged_doors_count") != 200 or not prog.get("all_doors_open_90_deg_clear", False):
        errors.append("Hinged doors != 200 or 90-deg swing check failed")
    if prog.get("ticket_barriers_count") != 12 or prog.get("lifts_count") != 2 or prog.get("escalators_count") != 4:
        errors.append("Barriers (12), lifts (2), or escalators (4) count mismatch")

    ok = len(errors) == 0
    report = {"validator": "v_mechanism", "status": "PASS" if ok else "FAIL", "errors": errors}
    write_report(report, args.json)
    print(f"v_mechanism: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
