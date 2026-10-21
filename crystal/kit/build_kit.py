#!/usr/bin/env python3
"""
build_kit.py — Builds the 5 canonical versioned kit files in crystal/kit/ (Stage B, F18):
  - crystal/kit/column.blend
  - crystal/kit/girder.blend
  - crystal/kit/sash_bar.blend
  - crystal/kit/pane.blend
  - crystal/kit/gutter.blend
  - crystal/kit/KIT_VERSION.json
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import sys
import bpy

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
if KIT_DIR not in sys.path:
    sys.path.insert(0, KIT_DIR)

import kit_builders as kb  # noqa: E402


def reset_scene() -> bpy.types.Collection:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = False  # F20: Debian Blender has no OpenImageDenoise
    return sc.collection


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    os.makedirs(KIT_DIR, exist_ok=True)
    artifacts = {}

    # 1. Column
    col = reset_scene()
    pal = kb.ensure_palace_palette()
    kb.build_kit_column("KIT_Column_24ft", "FXH-SMETHWICK-1851-M01-C0001", "ground_24ft", 0.0, 0.0, 0.0, 7.32, 19.05, pal, col)
    p_col = os.path.join(KIT_DIR, "column.blend")
    bpy.ops.wm.save_as_mainfile(filepath=p_col, compress=True)
    artifacts["column"] = {"file": "kit/column.blend", "sha256": sha256_file(p_col)}

    # 2. Girder
    col = reset_scene()
    pal = kb.ensure_palace_palette()
    kb.build_kit_girder("KIT_Girder_24ft", "cast_24ft", 7.32, 6.5, 12, (0.0, 0.0, 7.32), (7.32, 0.0, 7.32), pal, col)
    p_gir = os.path.join(KIT_DIR, "girder.blend")
    bpy.ops.wm.save_as_mainfile(filepath=p_gir, compress=True)
    artifacts["girder"] = {"file": "kit/girder.blend", "sha256": sha256_file(p_gir)}

    # 3. Sash Bar
    col = reset_scene()
    pal = kb.ensure_palace_palette()
    kb.build_kit_sash_bar("KIT_SashBar_49in", 1.245, (0.0, 0.0, 0.0), math.radians(21.8), pal, col)
    p_sash = os.path.join(KIT_DIR, "sash_bar.blend")
    bpy.ops.wm.save_as_mainfile(filepath=p_sash, compress=True)
    artifacts["sash_bar"] = {"file": "kit/sash_bar.blend", "sha256": sha256_file(p_sash)}

    # 4. Seeded Pane
    col = reset_scene()
    kb.build_kit_pane("KIT_Pane_P000001", "P000001", 1851000001, 0.425, 1.5182, (0.0, 0.0, 0.0), math.radians(21.8), col, unique_material=True)
    p_pane = os.path.join(KIT_DIR, "pane.blend")
    bpy.ops.wm.save_as_mainfile(filepath=p_pane, compress=True)
    artifacts["pane"] = {"file": "kit/pane.blend", "sha256": sha256_file(p_pane)}

    # 5. Paxton Gutter
    col = reset_scene()
    pal = kb.ensure_palace_palette()
    kb.build_kit_gutter("KIT_PaxtonGutter_24ft", "GT0001", 7.32, 25.0, (0.0, 0.0, 19.52), pal, col)
    p_gut = os.path.join(KIT_DIR, "gutter.blend")
    bpy.ops.wm.save_as_mainfile(filepath=p_gut, compress=True)
    artifacts["gutter"] = {"file": "kit/gutter.blend", "sha256": sha256_file(p_gut)}

    kit_meta = {
        "kit_version": "1.0.0",
        "builder_sha256": sha256_file(os.path.join(KIT_DIR, "kit_builders.py")),
        "parts": artifacts,
    }
    with open(os.path.join(KIT_DIR, "KIT_VERSION.json"), "w", encoding="utf-8") as fh:
        json.dump(kit_meta, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print("Built all 5 kit files:", json.dumps(kit_meta, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
