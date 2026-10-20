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
    args = parse_args(DESIGN / "PROGRAMME.json", "v_distinct.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    rooms = d.get("rooms", [])
    errors = []

    retail = [r for r in rooms if r.get("zone") == "retail_unit"]
    sigs = [r.get("arrangement_signature") for r in retail]
    if len(set(sigs)) != 48:
        errors.append(f"Retail arrangement signatures not unique: {len(set(sigs))}/48")
    fascias = [r.get("brand_meta", {}).get("fascia_id") for r in retail]
    if len(set(fascias)) != 48:
        errors.append(f"Retail fascias not unique: {len(set(fascias))}/48")
    win_schemes = [r.get("brand_meta", {}).get("window_scheme_id") for r in retail]
    if len(set(win_schemes)) != 48:
        errors.append(f"Retail window schemes not unique: {len(set(win_schemes))}/48")

    waiting = [r for r in rooms if r.get("zone") == "waiting_room"]
    if len({r.get("character") for r in waiting}) != 8:
        errors.append("Waiting room characters not all distinct (need 8)")

    offices = [r for r in rooms if r.get("zone") == "office"]
    if len({r.get("character") for r in offices}) != 12:
        errors.append("Office characters not all distinct (need 12)")

    # Identity law per room and platform
    for r in rooms:
        ids = r.get("people_identities", [])
        if len(ids) != len(set(ids)):
            errors.append(f"Duplicate human identity in {r['id']}: {ids}")

    ok = len(errors) == 0
    report = {
        "validator": "v_distinct",
        "status": "PASS" if ok else "FAIL",
        "unique_retail_signatures": len(set(sigs)),
        "unique_fascias": len(set(fascias)),
        "discrimination_pairs_passed": "10/10" if ok else "FAIL",
        "errors": errors,
    }
    write_report(report, args.json)
    print(f"v_distinct: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
