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
    args = parse_args(DESIGN / "IRONWORK.json", "v_iron.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    trusses = d.get("trusses", [])
    cols = d.get("columns", [])
    cat = d.get("catenary", {})
    errors = []

    if len(trusses) != 8:
        errors.append(f"Truss count {len(trusses)} != 8")
    if len(cols) != 12:
        errors.append(f"Column count {len(cols)} != 12")
    if not d.get("all_bays_braced", False) or not d.get("every_turnbuckle_modelled", False):
        errors.append("Bracing or turnbuckles missing")
    for t in trusses:
        tid = t["truss_id"]
        if abs(t.get("rivet_pitch_mm", 0) - 60.0) > 1.0:
            errors.append(f"{tid} rivet_pitch_mm {t.get('rivet_pitch_mm')} outside 60 +-1 mm")
        if abs(t.get("rivet_head_diameter_mm", 0) - 18.0) > 0.5:
            errors.append(f"{tid} rivet_head_diameter_mm {t.get('rivet_head_diameter_mm')} outside 18 +-0.5 mm")
        if not t.get("loaded_joints_complete", False):
            errors.append(f"{tid} loaded_joints_complete is False")
        if t.get("member_interpenetration_mm", 9.0) > 0.0:
            errors.append(f"{tid} member_interpenetration_mm > 0")
        if t.get("lod_method") != "count_never_material":
            errors.append(f"{tid} violates F25 (lod_method != count_never_material)")
    for c in cols:
        cid = c["column_id"]
        if not (c.get("has_base_plate") and c.get("holding_down_bolts", 0) >= 4 and c.get("has_corinthian_cast_capital") and c.get("foundry_mark")):
            errors.append(f"{cid} missing base plate, bolts, capital, or foundry mark")
    if abs(cat.get("contact_wire_height_m", 0) - 5.50) > 0.02:
        errors.append(f"Catenary wire height {cat.get('contact_wire_height_m')} outside 5.50 +-0.02 m")
    if abs(cat.get("dropper_spacing_m", 0) - 7.50) > 0.05 or not cat.get("tension_weights_modelled", False):
        errors.append("Catenary dropper spacing != 7.5 m or tension weights missing")

    ok = len(errors) == 0
    report = {"validator": "v_iron", "status": "PASS" if ok else "FAIL", "errors": errors}
    write_report(report, args.json)
    print(f"v_iron: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
