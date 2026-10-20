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
    args = parse_args(DESIGN / "MATERIALS.json", "v_material.json")
    d = json.loads(args.input.read_text(encoding="utf-8"))
    mats = d.get("materials", [])
    errors = []

    if len(mats) != 120:
        errors.append(f"Material count {len(mats)} != 120")
    if d.get("three_layer_paint_chip_objects", 0) < 20:
        errors.append(f"three_layer_paint_chip_objects {d.get('three_layer_paint_chip_objects')} < 20")
    for m in mats:
        mid = m["material_id"]
        min_td = 40.0 if m.get("is_hero", True) else 20.0
        if m.get("texel_density_px_per_cm", 0) < min_td:
            errors.append(f"{mid} texel_density {m.get('texel_density_px_per_cm')} < {min_td} px/cm")
        if m.get("uv_aspect_distortion", 9.9) > 1.15:
            errors.append(f"{mid} uv_aspect_distortion {m.get('uv_aspect_distortion')} > 1.15")
        if m.get("overlapping_uvs", 1) != 0:
            errors.append(f"{mid} overlapping_uvs != 0")
        if len(m.get("detail_scales", [])) < 5:
            errors.append(f"{mid} detail_scales < 5")
        if m.get("albedo_variation_pct", 0) < 15.0:
            errors.append(f"{mid} albedo_variation_pct < 15%")
        if m.get("roughness_variation", 0) < 0.10:
            errors.append(f"{mid} roughness_variation < 0.10")
        if m.get("missing_textures", 1) != 0:
            errors.append(f"{mid} has missing textures")

    ok = len(errors) == 0
    report = {"validator": "v_material", "status": "PASS" if ok else "FAIL", "material_count": len(mats), "errors": errors}
    write_report(report, args.json)
    print(f"v_material: {'PASS' if ok else 'FAIL'} ({len(mats)} materials, {len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
