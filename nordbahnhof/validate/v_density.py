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
    args = parse_args(DESIGN / "PROGRAMME.json", "v_density.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    rooms = d.get("rooms", [])
    errors = []

    floors_by_zone = {
        "retail_unit": 180,
        "restaurant": 200,
        "waiting_room": 90,
        "office": 70,
        "restroom": 40,
        "concourse": 2880,
        "platform": 144,
        "left_luggage": 220,
        "plant_room": 60,
    }
    for r in rooms:
        rid = r["id"]
        zone = r["zone"]
        req = floors_by_zone.get(zone, r.get("min_props", 20))
        act = r.get("actual_props", 0)
        if act < req:
            errors.append(f"Room {rid} ({zone}) actual_props {act} < required {req}")

    ok = len(errors) == 0
    report = {"validator": "v_density", "status": "PASS" if ok else "FAIL", "rooms_checked": len(rooms), "errors": errors}
    write_report(report, args.json)
    print(f"v_density: {'PASS' if ok else 'FAIL'} ({len(rooms)} rooms checked, {len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
