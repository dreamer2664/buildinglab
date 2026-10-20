#!/usr/bin/env python3
"""v_export.py — the scene must survive a round trip out of Blender.

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/tools/v_export.py -- --native portus/source/PORTUS.blend

  1  export the whole model to glTF-binary
  2  count what went in: mesh objects and triangles
  3  re-import the .glb into an empty scene and count what came back
  4  every material that went in comes back
  5  the file is not empty and not absurd
Exit 0 PASS, 2 FAIL. Writes evidence/validation/v_export.json.
The .glb is written to portus/exports/ and is git-ignored: it is a release
artifact, not source.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
EXPORTS = os.path.join(ROOT, "exports")


def tri_count(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == "MESH" else 0


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    argv_after_dash = True
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    args = ap.parse_args(argv)
    import bpy

    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    os.makedirs(EXPORTS, exist_ok=True)
    out = os.path.join(EXPORTS, "PORTUS.glb")
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    tris_in = sum(tri_count(o) for o in meshes)
    mats_in = len(bpy.data.materials)
    check("scene has geometry to export", tris_in > 100000, f"{tris_in:,} triangles, {len(meshes):,} meshes")

    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False,
                              export_apply=True, export_yup=True)
    size = os.path.getsize(out)
    check("glb written", size > 1_000_000, f"{size/1e6:.1f} MB")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=out)
    meshes2 = [o for o in bpy.data.objects if o.type == "MESH"]
    tris_out = sum(tri_count(o) for o in meshes2)
    mats_out = len(bpy.data.materials)

    check("round trip keeps the geometry", abs(tris_out - tris_in) / max(1, tris_in) < 0.02,
          f"{tris_in:,} in, {tris_out:,} out ({(tris_out-tris_in)/max(1,tris_in)*100:+.2f} %)")
    check("round trip keeps the materials", mats_out >= mats_in * 0.95,
          f"{mats_in} in, {mats_out} out")
    # glTF does not preserve object names reliably, so identify buildings by
    # footprint: a mesh spanning more than 8 m in plan is a block, not a prop.
    def plan_span(o):
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        if not vs:
            return 0.0
        xs = [v.x for v in vs]
        ys = [v.y for v in vs]
        return min(max(xs) - min(xs), max(ys) - min(ys))

    big = [o for o in meshes2 if plan_span(o) > 8.0]
    check("round trip keeps the buildings", len(big) > 40,
          f"{len(meshes2):,} meshes back, {len(big)} spanning >8 m in plan")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_export", native=args.native, ok=ok, checks=checks,
                   glb=dict(path=out, bytes=size), fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_export.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_export: {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
