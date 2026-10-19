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
    args = parse_args(DESIGN / "PEOPLE.json", "v_people.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    people = d.get("people", [])
    identities = d.get("identities", [])
    errors = []

    if len(people) < 400:
        errors.append(f"Total people {len(people)} < 400")
    passengers = sum(1 for p in people if p.get("role") == "passenger")
    staff = sum(1 for p in people if p.get("role") == "staff")
    heroes = sum(1 for p in people if p.get("is_hero", False))
    if passengers < 240:
        errors.append(f"Passengers {passengers} < 240")
    if staff < 160:
        errors.append(f"Staff {staff} < 160")
    if len(identities) < 60:
        errors.append(f"Distinct identities {len(identities)} < 60")
    if heroes < 20:
        errors.append(f"Hero figures {heroes} < 20")

    by_room: dict[str, set[str]] = {}
    retail_ids: set[str] = set()
    for p in people:
        pid = p["person_id"]
        iid = p["identity_id"]
        rid = p["room_id"]
        if p.get("is_capsule", False) or p.get("is_billboard", False):
            errors.append(f"{pid} is capsule or billboard")
        if p.get("sole_z_float_mm", 9.0) > 1.0:
            errors.append(f"{pid} sole float {p.get('sole_z_float_mm')} > 1.0 mm")
        used = by_room.setdefault(rid, set())
        if iid in used:
            errors.append(f"Duplicate identity {iid} in room/platform {rid} (F29)")
        used.add(iid)
        if rid.startswith("RET_"):
            if iid in retail_ids:
                errors.append(f"Duplicate identity {iid} in retail parade {rid}")
            retail_ids.add(iid)

    lic_file = ROOT / "assets" / "ASSET_LICENSES.md"
    if not lic_file.exists() or "ID_60" not in lic_file.read_text(encoding="utf-8"):
        errors.append("ASSET_LICENSES.md missing or incomplete")

    ok = len(errors) == 0
    report = {
        "validator": "v_people",
        "status": "PASS" if ok else "FAIL",
        "total_people": len(people),
        "passengers": passengers,
        "staff": staff,
        "identities": len(identities),
        "heroes": heroes,
        "errors": errors,
    }
    write_report(report, args.json)
    print(f"v_people: {'PASS' if ok else 'FAIL'} ({len(people)} people, {len(identities)} identities, {len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
