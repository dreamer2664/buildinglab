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
    args = parse_args(ROOT / "renders" / "best" / "MANIFEST.json", "v_package.json")
    errors = []

    if args.input.exists():
        manifest = json.loads(args.input.read_text(encoding="utf-8"))
        imgs = manifest.get("images", [])
        if len(imgs) > 30:
            errors.append(f"renders/best image count {len(imgs)} > 30")
        total_bytes = 0
        for im in imgs:
            fn = im.get("filename", "")
            b = im.get("bytes", 0)
            total_bytes += b
            if fn.lower().endswith(".png"):
                errors.append(f"Forbidden PNG in renders/best/: {fn}")
            if b > 4 * 1024 * 1024:
                errors.append(f"Image {fn} bytes {b} > 4 MB limit")
        if total_bytes > 100 * 1024 * 1024:
            errors.append(f"renders/best total bytes {total_bytes} > 100 MB limit")

    # Also check actual files in renders/best if directory exists
    best_dir = ROOT / "renders" / "best"
    if best_dir.exists() and args.input == ROOT / "renders" / "best" / "MANIFEST.json":
        for p in best_dir.iterdir():
            if p.suffix.lower() == ".png":
                errors.append(f"Forbidden PNG file in renders/best/: {p.name}")
            if p.is_file() and p.stat().st_size > 4 * 1024 * 1024:
                errors.append(f"File {p.name} exceeds 4 MB ({p.stat().st_size} bytes)")

    ok = len(errors) == 0
    report = {"validator": "v_package", "status": "PASS" if ok else "FAIL", "errors": errors}
    write_report(report, args.json)
    print(f"v_package: {'PASS' if ok else 'FAIL'} ({len(errors)} errors)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
