#!/usr/bin/env python3
"""
dump_bay.py — Deterministic Bay Census Dumper for PAXTON / CRYSTAL (§1.1, G1, G15).

Usage:
  python3 tools/dump_bay.py 042 > build/b042_a.txt
  python3 tools/dump_bay.py 042 > build/b042_b.txt
  diff build/b042_a.txt build/b042_b.txt && echo "BAY CENSUS MATCH"
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
CRYSTAL_DIR = os.path.dirname(TOOLS_DIR)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 tools/dump_bay.py <bay_num>", file=sys.stderr)
        return 1
    bay_num = int(str(sys.argv[1]).lstrip("Bb"))
    bay_id = f"B{bay_num:03d}"
    blend_path = os.path.join(CRYSTAL_DIR, "bays", f"{bay_id}.blend")
    if not os.path.exists(blend_path):
        print(f"dump_bay: {blend_path} does not exist", file=sys.stderr)
        return 1

    expr = """
import bpy, hashlib, json
objs = sorted(bpy.data.objects, key=lambda o: o.name)
lines = []
counts = {}
for o in objs:
    c_cls = o.get("crystal_class", "other")
    counts[c_cls] = counts.get(c_cls, 0) + 1
    v_cnt = len(o.data.vertices) if getattr(o, "data", None) and hasattr(o.data, "vertices") else 0
    f_cnt = len(o.data.polygons) if getattr(o, "data", None) and hasattr(o.data, "polygons") else 0
    loc = tuple(round(x, 4) for x in o.location)
    meta = o.get("seed", o.get("foundry_mark", o.get("bolt_holes", o.get("exhibit_id", ""))))
    lines.append(f"{o.name}|{c_cls}|v={v_cnt}|f={f_cnt}|loc={loc}|meta={meta}")
digest = hashlib.sha256("\\n".join(lines).encode("utf-8")).hexdigest()
print("CENSUS_HEADER|" + json.dumps({"bay_id": bpy.context.scene.get("bay_id", ""), "bay_key": bpy.context.scene.get("bay_key", ""), "census_sha256": digest, "counts": counts}, sort_keys=True))
for ln in lines:
    print("OBJ|" + ln)
"""
    proc = subprocess.run(
        ["blender", "--background", blend_path, "--python-exit-code", "1", "--python-expr", expr],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return proc.returncode

    for line in proc.stdout.splitlines():
        if line.startswith("CENSUS_HEADER|") or line.startswith("OBJ|"):
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
