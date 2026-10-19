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
    args = parse_args(DESIGN / "PROGRAMME.json", "v_contact.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    cc = d.get("contact_circulation", d)
    errors = []

    if cc.get("max_float_mm", 99.0) > 1.0:
        errors.append(f"max_float_mm {cc.get('max_float_mm')} > 1.0 mm")
    if cc.get("max_interpenetration_mm", 99.0) > 0.5:
        errors.append(f"max_interpenetration_mm {cc.get('max_interpenetration_mm')} > 0.5 mm")
    if cc.get("coplanar_faces", 1) != 0:
        errors.append(f"coplanar_faces {cc.get('coplanar_faces')} != 0")
    if not cc.get("all_objects_cast_shadow", False):
        errors.append("all_objects_cast_shadow is False")
    if not cc.get("world_matrices_verified", False):
        errors.append("world_matrices_verified is False")

    ok = len(errors) == 0
    report = {"validator": "v_contact", "status": "PASS" if ok else "FAIL", "errors": errors}
    write_report(report, args.json)
    print(f"v_contact: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
