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
    args = parse_args(DESIGN / "PROGRAMME.json", "v_light.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    lm = d.get("light_metrics", d)
    rooms = d.get("rooms", [])
    errors = []

    if lm.get("blown_highlight_pct", 99.0) >= 0.6:
        errors.append(f"blown_highlight_pct {lm.get('blown_highlight_pct')} >= 0.6%")
    if lm.get("crushed_black_pct", 99.0) >= 1.2:
        errors.append(f"crushed_black_pct {lm.get('crushed_black_pct')} >= 1.2%")
    if abs(lm.get("interior_exposure_ev", 9.0)) > 0.20:
        errors.append(f"interior_exposure_ev {lm.get('interior_exposure_ev')} outside 0.0 +-0.20 EV")
    if not lm.get("steam_volumetric", False):
        errors.append("steam_volumetric is False")
    if lm.get("steam_nearest_geometry_clearance_m", 0.0) < 3.0:
        errors.append(f"steam_nearest_geometry_clearance_m {lm.get('steam_nearest_geometry_clearance_m')} < 3.0 m (F28)")
    if lm.get("fireflies_at_100pct", 1) != 0:
        errors.append(f"fireflies_at_100pct {lm.get('fireflies_at_100pct')} != 0")

    for r in rooms:
        srcs = r.get("light_sources", [])
        if len(srcs) < 3:
            errors.append(f"Room {r['id']} has {len(srcs)} light sources (< 3)")
        for s in srcs:
            if s.get("clear_rays_of_10", 0) < 9:
                errors.append(f"Room {r['id']} emitter {s.get('type')} has {s.get('clear_rays_of_10')}/10 clear rays (< 9)")

    ok = len(errors) == 0
    report = {"validator": "v_light", "status": "PASS" if ok else "FAIL", "errors": errors}
    write_report(report, args.json)
    print(f"v_light: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
