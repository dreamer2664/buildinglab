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
    args = parse_args(DESIGN / "PROGRAMME.json", "v_programme.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    rooms = d.get("rooms", [])
    errors = []

    levels = d.get("levels", [])
    n_levels = len(levels)
    n_rooms = len(rooms)
    n_retail = sum(1 for r in rooms if r.get("zone") == "retail_unit")
    n_rest = sum(1 for r in rooms if r.get("zone") == "restaurant")
    n_wait = sum(1 for r in rooms if r.get("zone") == "waiting_room")
    n_off = sum(1 for r in rooms if r.get("zone") == "office")
    n_wc = sum(1 for r in rooms if r.get("zone") == "restroom")
    n_plat = sum(1 for r in rooms if r.get("zone") == "platform")
    n_tracks = d.get("track_count", 0)
    n_trains = d.get("train_count", 0)
    n_veh = d.get("vehicle_count", 0)
    n_panes = d.get("glazing_pane_count", 0)
    n_trusses = d.get("truss_count", 0)
    n_clock = d.get("clock_parts_count", 0)
    n_board = d.get("departure_board_tiles_count", 0)
    doorless = sum(1 for r in rooms if r.get("doors", 0) <= 0)
    windowless = sum(1 for r in rooms if r.get("windows", 0) <= 0)

    checks = [
        ("levels", n_levels, 5),
        ("rooms", n_rooms, 240),
        ("retail_units", n_retail, 48),
        ("restaurants", n_rest, 6),
        ("waiting_rooms", n_wait, 8),
        ("offices", n_off, 12),
        ("restrooms", n_wc, 6),
        ("platforms", n_plat, 8),
        ("tracks", n_tracks, 12),
        ("trains", n_trains, 6),
        ("vehicles", n_veh, 34),
        ("glazing_panes", n_panes, 4200),
        ("trusses", n_trusses, 8),
        ("clock_parts", n_clock, 240),
        ("board_tiles", n_board, 240),
        ("doorless_rooms", doorless, 0),
        ("windowless_rooms", windowless, 0),
    ]
    for name, actual, expected in checks:
        if actual != expected:
            errors.append(f"{name}: got {actual}, expected {expected}")

    ok = len(errors) == 0
    summary_line = f"{n_levels} / {n_rooms} / {n_retail} / {n_rest} / {n_wait} / {n_off} / {n_veh}, zero doorless={doorless==0}, zero windowless={windowless==0}"
    report = {
        "validator": "v_programme",
        "status": "PASS" if ok else "FAIL",
        "summary": summary_line,
        "counts": {k: a for k, a, _ in checks},
        "errors": errors,
    }
    write_report(report, args.json)
    print(f"v_programme: {summary_line} -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
