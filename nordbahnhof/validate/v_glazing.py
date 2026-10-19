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
    args = parse_args(DESIGN / "GLAZING.json", "v_glazing.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    panes = d.get("panes", [])
    errors = []

    if len(panes) != 4200:
        errors.append(f"Pane count {len(panes)} != 4200")
    seeds = {p.get("waviness_seed") for p in panes}
    if len(seeds) != len(panes):
        errors.append(f"Duplicate waviness seeds found (F26): {len(seeds)} unique of {len(panes)}")
    cracked_n = sum(1 for p in panes if p.get("condition") == "cracked" and p.get("bay") == 8)
    tarp_n = sum(1 for p in panes if p.get("condition") == "missing_tarpaulin" and p.get("bay") == 8)
    if cracked_n != 6:
        errors.append(f"Cracked panes in north bay {cracked_n} != 6")
    if tarp_n != 2:
        errors.append(f"Missing tarpaulin panes in north bay {tarp_n} != 2")
    for p in panes:
        if p.get("came_width_mm") != 4.0 or not p.get("came_soldered_intersections", False):
            errors.append(f"{p.get('pane_id')} came != 4 mm or unsoldered")
            break
        if not (6.0 <= p.get("thickness_mm", 0) <= 14.0):
            errors.append(f"{p.get('pane_id')} thickness {p.get('thickness_mm')} outside 6-14 mm")
            break
        if not p.get("reflects_shed_interior", False):
            errors.append(f"{p.get('pane_id')} does not reflect shed interior")
            break

    ok = len(errors) == 0
    report = {"validator": "v_glazing", "status": "PASS" if ok else "FAIL", "pane_count": len(panes), "distinct_seeds": len(seeds), "errors": errors}
    write_report(report, args.json)
    print(f"v_glazing: {'PASS' if ok else 'FAIL'} ({len(panes)} panes, {len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
