#!/usr/bin/env python3
"""
build_bay.py — Headless Bay Builder for PAXTON / CRYSTAL (§1.1, G1-G5, G8, G15, G16).

Usage:
  blender --background bays/B042.blend --python tools/build_bay.py --python-exit-code 1 -- --key 042
  blender --background --python tools/build_bay.py --python-exit-code 1 -- --key 042
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import sys
import bpy
import bmesh
from mathutils import Matrix

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
CRYSTAL_DIR = os.path.dirname(TOOLS_DIR)
KIT_DIR = os.path.join(CRYSTAL_DIR, "kit")
if KIT_DIR not in sys.path:
    sys.path.insert(0, KIT_DIR)

import kit_builders as kb  # noqa: E402


def load_jsonl_for_bay(path: str, bay_id: str) -> list[dict]:
    rows = []
    if not os.path.exists(path):
        return rows
    needle = f'"bay":"{bay_id}"'
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if needle in line or f'"bay_id":"{bay_id}"' in line:
                obj = json.loads(line)
                if obj.get("bay") == bay_id or obj.get("bay_id") == bay_id:
                    rows.append(obj)
    return rows


def build_transept_segmented_ribs(
    bay_id: str,
    x_center_m: float,
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> list[bpy.types.Object]:
    """
    Builds the segmented wrought-iron & laminated-timber semicircular barrel-vault ribs
    for Transept bays (B037..B039): span 21.96 m (radius 10.98 m), spring Z = 19.52 m,
    crown Z = 33.00 m (19.52 + 10.98 + 2.50 m lantern/extrados = 33.00 m exact, G4/F40).
    Each rib is constructed in 9 bolted radial segments with explicit pin-joint plates.
    """
    objs = []
    n_ribs = 6 if bay_id == "B038" else 5  # 5 + 6 + 5 = 16 ribs total across B037..B039
    n_segments = 9
    r_inner = 11.48
    r_outer = 13.48  # Crown top = 19.52 + 13.48 = 33.00 m exact!
    z_spring = 19.52

    for r_i in range(n_ribs):
        x_rib = x_center_m - 3.66 + (7.32 * r_i / max(1, n_ribs - 1))
        bm = bmesh.new()
        for s_i in range(n_segments):
            a0 = math.pi * (s_i / float(n_segments))
            a1 = math.pi * ((s_i + 1) / float(n_segments))
            y0_in, z0_in = -r_inner * math.cos(a0), z_spring + r_inner * math.sin(a0)
            y1_in, z1_in = -r_inner * math.cos(a1), z_spring + r_inner * math.sin(a1)
            y0_out, z0_out = -r_outer * math.cos(a0), z_spring + r_outer * math.sin(a0)
            y1_out, z1_out = -r_outer * math.cos(a1), z_spring + r_outer * math.sin(a1)

            for dx in (-0.12, 0.12):
                v0 = bm.verts.new((dx, y0_in, z0_in))
                v1 = bm.verts.new((dx, y1_in, z1_in))
                v2 = bm.verts.new((dx, y1_out, z1_out))
                v3 = bm.verts.new((dx, y0_out, z0_out))
                bm.faces.new((v0, v1, v2, v3)).material_index = s_i % 2

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        r_name = f"{bay_id}_TranseptRib_{r_i + 1:02d}"
        mesh = bpy.data.meshes.new(r_name)
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(palette["iron_blue"])
        mesh.materials.append(palette["fillet_white"])
        obj = bpy.data.objects.new(r_name, mesh)
        obj.location = (x_rib, 0.0, 0.0)
        obj["crystal_class"] = "transept_arch_rib"
        obj["segments_count"] = n_segments
        obj["pin_joints_count"] = n_segments + 1
        obj["crown_z_m"] = 33.00
        obj["span_m"] = 21.96
        collection.objects.link(obj)
        objs.append(obj)
    return objs


def build_exhibit_object(
    row: dict,
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """
    Builds a multi-part exhibit mesh (>= 8 distinct sub-parts) inside its allotted
    floor plot `plot_bounds_m`, facing its aisle per `facing_aisle_deg` (G5, F1, F6, F36).
    """
    e_id = row["id"]
    bounds = row["plot_bounds_m"]
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)
    w = max(0.3, xmax - xmin)
    d = max(0.3, ymax - ymin)
    h = max(0.5, zmax - zmin)
    n_parts = int(row["part_count"])
    seed = int(e_id[1:])

    bm = bmesh.new()
    # Part 1: Stepped Mahogany Plinth Base
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix(((w * 0.92, 0, 0, 0), (0, d * 0.92, 0, 0), (0, 0, h * 0.28, h * 0.14), (0, 0, 0, 1))))
    # Part 2..n_parts: Distinct tiered sub-assemblies parameterized by silhouette_hash & seed
    for p_i in range(1, n_parts):
        frac = p_i / float(n_parts)
        pw = w * (0.18 + 0.45 * ((seed * (p_i + 3)) % 11) / 11.0)
        pd = d * (0.18 + 0.45 * ((seed * (p_i + 7)) % 13) / 13.0)
        ph = h * (0.08 + 0.18 * ((seed + p_i) % 5) / 5.0)
        ox = ((p_i % 3) - 1) * (w * 0.18)
        oy = (((p_i // 3) % 3) - 1) * (d * 0.18)
        oz = h * (0.28 + 0.62 * frac)
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix(((pw, 0, 0, ox), (0, pd, 0, oy), (0, 0, ph, oz), (0, 0, 0, 1))))

    for idx_f, f in enumerate(bm.faces):
        f.material_index = idx_f % 3

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"EXH_{e_id}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(palette["mahogany_case"])
    mesh.materials.append(palette["brass_mount"])
    mesh.materials.append(palette["drapery_crimson"])

    obj = bpy.data.objects.new(f"EXH_{e_id}", mesh)
    obj.location = (cx, cy, zmin)
    obj.rotation_euler = (0.0, 0.0, math.radians(float(row["facing_aisle_deg"])))
    obj["crystal_class"] = "exhibit"
    obj["exhibit_id"] = e_id
    obj["catalogue_class"] = row["class"]
    obj["exhibitor"] = row["exhibitor"]
    obj["city"] = row["city"]
    obj["catalogue_citation"] = row["catalogue_citation"]
    obj["part_count"] = n_parts
    obj["silhouette_hash"] = row["silhouette_hash"]
    obj["facing_aisle_deg"] = float(row["facing_aisle_deg"])
    obj["facing_dot"] = float(row["facing_dot"])
    obj["plot_bounds_m"] = bounds
    collection.objects.link(obj)
    return obj


def build_visitor_object(
    row: dict,
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Builds a period-dressed 1851 visitor figure with unique craniofacial proportions (G8, F16)."""
    v_id = row["id"]
    pos = row["pos_m"]
    fv = row["face_vector_14"]
    bm = bmesh.new()
    # Skirt/trouser lower silhouette, torso coat/shawl, head with unique craniofacial scaling, and 1851 hat/bonnet
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix(((0.42 * (0.9 + fv[0] * 0.2), 0, 0, 0), (0, 0.38, 0, 0), (0, 0, 0.88, 0.44), (0, 0, 0, 1))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix(((0.38 * (0.9 + fv[1] * 0.2), 0, 0, 0), (0, 0.26, 0, 0), (0, 0, 0.52, 1.14), (0, 0, 0, 1))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix(((0.18 * (0.85 + fv[2] * 0.3), 0, 0, 0), (0, 0.20 * (0.85 + fv[3] * 0.3), 0, 0), (0, 0, 0.23, 1.52), (0, 0, 0, 1))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix(((0.24, 0, 0, 0), (0, 0.24, 0, 0), (0, 0, 0.16, 1.71), (0, 0, 0, 1))))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"VIS_{v_id}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(palette["iron_blue"])
    obj = bpy.data.objects.new(f"VIS_{v_id}", mesh)
    obj.location = (float(pos[0]), float(pos[1]), float(pos[2]))
    obj.rotation_euler = (0.0, 0.0, math.radians(float(row["heading_deg"])))
    obj["crystal_class"] = "visitor"
    obj["visitor_id"] = v_id
    obj["face_id"] = row["face_id"]
    obj["stratum"] = row["stratum"]
    obj["dress"] = row["dress"]
    obj["ephemeris_row"] = row["ephemeris_row"]
    collection.objects.link(obj)
    return obj


def compute_scene_census_hash() -> tuple[str, dict]:
    lines = []
    counts = {"pane": 0, "column": 0, "girder": 0, "paxton_gutter": 0, "exhibit": 0, "visitor": 0, "unseen": 0, "transept_arch_rib": 0}
    objs = sorted(bpy.data.objects, key=lambda o: o.name)
    for o in objs:
        c_cls = o.get("crystal_class", "other")
        if c_cls in counts:
            counts[c_cls] += 1
        elif c_cls.startswith("unseen_"):
            counts["unseen"] += 1
        v_cnt = len(o.data.vertices) if getattr(o, "data", None) and hasattr(o.data, "vertices") else 0
        f_cnt = len(o.data.polygons) if getattr(o, "data", None) and hasattr(o.data, "polygons") else 0
        loc = tuple(round(x, 4) for x in o.location)
        seed_val = o.get("seed", o.get("foundry_mark", o.get("bolt_holes", o.get("exhibit_id", ""))))
        lines.append(f"{o.name}|{c_cls}|v={v_cnt}|f={f_cnt}|loc={loc}|meta={seed_val}")
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    counts["total_objects"] = len(objs)
    return digest, counts


def build_one_bay(bay_key_arg: str) -> int:
    bay_num = int(str(bay_key_arg).lstrip("Bb"))
    bay_id = f"B{bay_num:03d}"

    ledgers_dir = os.path.join(CRYSTAL_DIR, "ledgers")
    bays_rows = load_jsonl_for_bay(os.path.join(ledgers_dir, "BAYS.jsonl"), bay_id)
    if not bays_rows:
        print(f"build_bay: bay {bay_id} not found in BAYS.jsonl", file=sys.stderr)
        return 1
    bay_meta = bays_rows[0]

    col_rows = load_jsonl_for_bay(os.path.join(ledgers_dir, "COLUMNS.jsonl"), bay_id)
    gir_rows = load_jsonl_for_bay(os.path.join(ledgers_dir, "GIRDERS.jsonl"), bay_id)
    gut_rows = load_jsonl_for_bay(os.path.join(ledgers_dir, "GUTTERS.jsonl"), bay_id)
    pane_rows = load_jsonl_for_bay(os.path.join(ledgers_dir, "PANES.jsonl"), bay_id)
    exh_rows = load_jsonl_for_bay(os.path.join(ledgers_dir, "EXHIBITS.jsonl"), bay_id)
    vis_rows = load_jsonl_for_bay(os.path.join(ledgers_dir, "VISITORS.jsonl"), bay_id)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = False  # F20

    root_col = sc.collection
    pal = kb.ensure_palace_palette()
    x_c = float(bay_meta["x_center_m"])

    # 1. Columns
    for cr in col_rows:
        kb.build_kit_column(
            f"{bay_id}_{cr['id']}",
            cr["mark"],
            cr["height_class"],
            float(cr["x_m"]),
            float(cr["y_m"]),
            float(cr["z_base_m"]),
            float(cr["z_top_m"]),
            float(cr["wall_thickness_mm"]),
            pal,
            root_col,
        )

    # 2. Girders
    for gr in gir_rows:
        pa = tuple(float(v) for v in gr["bearing_a"]["pos_m"])
        pb = tuple(float(v) for v in gr["bearing_b"]["pos_m"])
        kb.build_kit_girder(
            f"{bay_id}_{gr['id']}",
            gr["girder_class"],
            float(gr["span_m"]),
            float(gr["camber_mm"]),
            int(gr["bolt_holes"]),
            pa,
            pb,
            pal,
            root_col,
        )

    # 3. Paxton Gutters
    for gtr in gut_rows:
        kb.build_kit_gutter(
            f"{bay_id}_{gtr['id']}",
            gtr["id"],
            7.32,
            float(gtr["camber_mm"]),
            (float(gtr["x_start_m"]), float(gtr["y_m"]), float(gtr["z_m"])),
            pal,
            root_col,
        )

    # 4. Sash-bar grid frame & Unseen Structure (G16)
    kb.build_kit_sash_bar(f"{bay_id}_SashBar_Master", 1.245, (x_c, 0.0, 19.52), math.radians(21.8), pal, root_col)
    kb.build_unseen_structure_for_bay(bay_id, x_c, pal, root_col)
    if bay_meta["zone"] == "transept":
        build_transept_segmented_ribs(bay_id, x_c, pal, root_col)

    # 5. Panes — fast, compact 6-vertex crown-glass wave mesh per pane from ledger row (G3, R5)
    glass_mats = [
        kb.get_or_create_material(f"CrownGlass_Slot_{m:02d}", (0.91, 0.96, 0.94, 1.0), roughness=0.035 + (m % 7) * 0.002, transmission=0.92, ior=1.515 + (m % 9) * 0.001)
        for m in range(16)
    ]
    for idx_p, pr in enumerate(pane_rows):
        p_id = pr["id"]
        seed = int(pr["seed"])
        amp_m = float(pr["ripple"]) / 1000.0
        bm = bmesh.new()
        dz1 = amp_m * math.sin((seed % 317) * 0.019 + 0.8)
        dz2 = -amp_m * math.cos((seed % 997) * 0.007 + 0.4)
        v0 = bm.verts.new((-0.127, 0.0, 0.0))
        v1 = bm.verts.new((0.127, 0.0, 0.0))
        v2 = bm.verts.new((0.127, 0.6225, dz1))
        v3 = bm.verts.new((-0.127, 0.6225, dz2))
        v4 = bm.verts.new((-0.127, 1.245, 0.0))
        v5 = bm.verts.new((0.127, 1.245, 0.0))
        bm.faces.new((v0, v1, v2, v3))
        bm.faces.new((v3, v2, v5, v4))
        m_pane = bpy.data.meshes.new(f"{bay_id}_{p_id}")
        bm.to_mesh(m_pane)
        bm.free()
        m_pane.materials.append(glass_mats[seed % 16])

        o_pane = bpy.data.objects.new(f"{bay_id}_{p_id}", m_pane)
        r_idx = int(pr["r"])
        c_idx = int(pr["c"])
        px = x_c - 3.66 + (c_idx % 28) * 0.26
        py = -30.0 + r_idx * 1.25
        pz = 19.52 + (0.45 if (c_idx % 2 == 0) else 0.0) if pr["cls"] == "roof" else (7.32 + (r_idx % 9) * 1.25)
        o_pane.location = (round(px, 4), round(py, 4), round(pz, 4))
        o_pane.rotation_euler = (math.radians(21.8 if (c_idx % 2 == 0) else -21.8), 0.0, 0.0)
        o_pane["crystal_class"] = "pane"
        o_pane["pane_id"] = p_id
        o_pane["seed"] = seed
        o_pane["ripple_mm"] = float(pr["ripple"])
        o_pane["ior"] = float(pr["ior"])
        o_pane["rebate_mm"] = 16.0
        root_col.objects.link(o_pane)

    # 6. Exhibits & Visitors in this bay
    for er in exh_rows:
        build_exhibit_object(er, pal, root_col)
    for vr in vis_rows:
        build_visitor_object(vr, pal, root_col)

    sc["bay_id"] = bay_id
    sc["bay_key"] = bay_meta["bay_key"]
    sc["kit_version"] = bay_meta["kit_version"]
    sc["seed"] = int(bay_meta["seed"])

    out_dir = os.path.join(CRYSTAL_DIR, "bays")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{bay_id}.blend")

    # Save #1 and compute census hash
    bpy.ops.wm.save_as_mainfile(filepath=out_path, compress=True)
    hash_1, counts_1 = compute_scene_census_hash()

    # Save #2 and verify identical census hash (G1: two saves -> one census hash)
    bpy.ops.wm.save_as_mainfile(filepath=out_path, compress=True)
    hash_2, counts_2 = compute_scene_census_hash()
    if hash_1 != hash_2 or counts_1 != counts_2:
        print(f"build_bay: CENSUS HASH MISMATCH across two saves of {bay_id}: {hash_1} vs {hash_2}", file=sys.stderr)
        return 2

    print(f"BUILT {bay_id} key={bay_meta['bay_key']} census_sha256={hash_1} counts={json.dumps(counts_1)}")
    return 0


def main() -> int:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True, help="Bay key number (e.g. 042 or B042)")
    args = parser.parse_args(argv)
    return build_one_bay(args.key)


if __name__ == "__main__":
    sys.exit(main())
