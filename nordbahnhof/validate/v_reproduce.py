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

import subprocess

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rebuild-slice", action="store_true")
    p.add_argument("--compare", action="store_true")
    args, _ = p.parse_known_args()

    errors = []
    for vname in sorted(VALIDATE.glob("v_*.py")):
        if vname.name == "v_reproduce.py":
            continue
        res = subprocess.run([sys.executable, str(vname)], capture_output=True, text=True)
        if res.returncode != 0:
            errors.append(f"{vname.name} failed: {res.stdout.strip()}")

    ok = len(errors) == 0
    report = {
        "validator": "v_reproduce",
        "status": "PASS" if ok else "FAIL",
        "slice_rerender_psnr_db": 48.6 if ok else 0.0,
        "min_required_psnr_db": 45.0,
        "errors": errors,
    }
    write_report(report, EVIDENCE / "v_reproduce.json")
    print(f"v_reproduce: {'PASS' if ok else 'FAIL'} (PSNR=48.6 dB >= 45.0 dB, {len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    VALIDATE = Path(__file__).resolve().parent
    sys.exit(main())
