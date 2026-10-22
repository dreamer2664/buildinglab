#!/usr/bin/env python3
"""
prepare_scan_library.py — Normalizes, grounds (Z_min=0), scales to real-world metric dimensions,
decimates ultra-heavy meshes to <=18k faces while preserving UV-mapped baked PBR textures,
and saves clean ready-to-link .blend assets in build/scans/ready/<slug>.blend.
Runs each asset with a strict 25-second timeout and memory-safe pre-join decimation.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys

CRYSTAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANS_DIR = os.path.join(CRYSTAL_DIR, "build", "scans")
READY_DIR = os.path.join(SCANS_DIR, "ready")

ASSET_SPECS = [
    # --- 1. REAL 3D SCANNED HUMANS & CLOTHED PEOPLE (20 distinct models) ---
    ("human_scan_standing_man_01", "blenderkit/human_scan_standing_man_01.blend", 1.76, "cloth", 14000),
    ("human_scan_standing_man_02", "blenderkit/human_scan_standing_man_02.blend", 1.78, "cloth", 14000),
    ("human_scan_woman_jacket", "blenderkit/human_scan_woman_jacket.blend", 1.66, "cloth", 14000),
    ("human_scan_woman_hat", "blenderkit/human_scan_woman_hat.blend", 1.68, "cloth", 14000),
    ("human_scan_seated_man_02", "blenderkit/human_scan_seated_man_02.blend", 1.32, "cloth", 12000),
    ("human_scan_seated_boy_hat", "blenderkit/human_scan_seated_boy_hat.blend", 1.18, "cloth", 12000),
    ("human_gentleman_coat_hat", "blenderkit/human_gentleman_coat_hat.blend", 1.80, "cloth", 14000),
    ("human_old_gentleman", "blenderkit/human_old_gentleman.blend", 1.72, "cloth", 12000),
    ("human_man_suit_01", "blenderkit/human_man_suit_01.blend", 1.77, "cloth", 12000),
    ("human_man_suit_02", "blenderkit/human_man_suit_02.blend", 1.79, "cloth", 12000),
    ("human_man_walking_02", "blenderkit/human_man_walking_02.blend", 1.76, "cloth", 12000),
    ("human_woman_coat_01", "blenderkit/human_woman_coat_01.blend", 1.67, "cloth", 12000),
    ("human_woman_walking_01", "blenderkit/human_woman_walking_01.blend", 1.65, "cloth", 12000),
    ("human_woman_walking_02", "blenderkit/human_woman_walking_02.blend", 1.66, "cloth", 12000),
    ("human_man_standing_03", "blenderkit/human_man_standing_03.blend", 1.75, "cloth", 12000),
    ("human_woman_standing_03", "blenderkit/human_woman_standing_03.blend", 1.64, "cloth", 12000),
    ("human_female02", "github/female02/female02.obj", 1.66, "cloth", 14000),
    ("human_male02", "github/male02/male02.obj", 1.78, "cloth", 14000),
    ("human_tranthi", "github/gh_human_tranthi.glb", 1.65, "cloth", 14000),
    ("human_suit_glb", "github/gh_human_suit.glb", 1.77, "cloth", 14000),
    ("victorian_top_hat", "blenderkit/victorian_top_hat.blend", 0.24, "cloth", 6000),

    # --- 2. REAL 3D SCANNED BUILDINGS, HALLS & ARCHITECTURAL INTERIORS ---
    ("arch_sponza_atrium", "sponza/Sponza.gltf", 14.50, "stone", 35000),
    ("arch_berlin_dome_entrance", "blenderkit/arch_berlin_dome_entrance_scan.blend", 11.50, "stone", 20000),
    ("arch_greenhouse_hall", "blenderkit/arch_greenhouse_hall.blend", 6.80, "iron", 16000),
    ("arch_glass_pavilion", "blenderkit/arch_glass_pavilion.blend", 7.20, "iron", 16000),
    ("arch_classical_museum_hall", "blenderkit/arch_classical_museum_hall.blend", 10.50, "stone", 20000),
    ("arch_medieval_guild_hall", "blenderkit/arch_medieval_guild_hall.blend", 9.80, "stone", 18000),
    ("arch_gothic_church_doorway", "blenderkit/arch_gothic_church_doorway_scan.blend", 6.40, "stone", 18000),
    ("arch_stone_archway", "blenderkit/arch_stone_archway_scan.blend", 5.80, "stone", 16000),
    ("arch_dome_scanned", "blenderkit/arch_dome_scanned.blend", 8.50, "stone", 18000),
    ("arch_chinese_pavilion", "blenderkit/arch_chinese_pavilion.blend", 7.60, "wood", 20000),
    ("arch_victorian_iron_bridge", "blenderkit/arch_victorian_iron_bridge.blend", 5.40, "iron", 16000),
    ("arch_corinthian_column", "blenderkit/arch_corinthian_column.blend", 7.32, "marble", 14000),
    ("arch_balustrades", "blenderkit/arch_balustrades.blend", 1.15, "marble", 12000),
    ("arch_large_gothic_window", "blenderkit/arch_large_gothic_window.blend", 6.80, "stone", 16000),
    ("met_temple_of_dendur", "met/met_temple_of_dendur_building.fbx", 6.50, "stone", 20000),
    ("met_islamic_niche", "met/met_islamic_architectural_niche.fbx", 4.20, "marble", 16000),
    ("met_cloisters_arch", "met/met_cloisters_arch_spandrel.fbx", 3.80, "stone", 16000),
    ("met_gothic_tomb_ermengol", "met/met_gothic_tomb_ermengol.fbx", 4.60, "stone", 18000),
    ("ph_large_iron_gate", "polyhaven/large_iron_gate/large_iron_gate_1k.gltf", 5.20, "iron", 16000),
    ("ph_large_castle_door", "polyhaven/large_castle_door/large_castle_door_1k.gltf", 4.40, "wood", 16000),

    # --- 3. FOUNTAINS, TREES, STATUES & EXHIBITION WONDERS ---
    ("wonder_tiered_fountain", "blenderkit/wonder_tiered_fountain.blend", 6.80, "glass", 20000),
    ("wonder_victorian_fountain", "blenderkit/wonder_victorian_fountain.blend", 3.60, "marble", 18000),
    ("met_marble_wellhead_fountain", "met/met_marble_wellhead_fountain.fbx", 2.40, "marble", 18000),
    ("ph_island_tree_01", "polyhaven/island_tree_01/island_tree_01_1k.gltf", 25.00, "wood", 24000),
    ("ph_island_tree_02", "polyhaven/island_tree_02/island_tree_02_1k.gltf", 24.00, "wood", 24000),
    ("ph_potted_plant_01", "polyhaven/potted_plant_01/potted_plant_01_1k.gltf", 1.45, "wood", 10000),
    ("ph_potted_plant_02", "polyhaven/potted_plant_02/potted_plant_02_1k.gltf", 1.65, "wood", 10000),
    ("ph_fern_02", "polyhaven/fern_02/fern_02_1k.gltf", 1.10, "wood", 10000),

    # Statues & Sculptures
    ("met_canova_perseus", "met/met_canova_perseus_marble.fbx", 3.60, "marble", 18000),
    ("met_carpeaux_ugolino", "met/met_carpeaux_ugolino_marble.fbx", 3.20, "marble", 18000),
    ("met_mourning_victory", "met/met_mourning_victory_marble.fbx", 3.50, "marble", 18000),
    ("met_aphrodite_statue", "met/met_aphrodite_statue.fbx", 2.90, "marble", 16000),
    ("met_herakles_statue", "met/met_herakles_statue.fbx", 3.10, "marble", 16000),
    ("met_woman_statue", "met/met_woman_statue.fbx", 2.75, "marble", 16000),
    ("met_marble_female_figure", "met/met_marble_female_figure.fbx", 2.60, "marble", 16000),
    ("met_medieval_pieta", "met/met_medieval_pieta_sculpture.fbx", 2.40, "stone", 16000),
    ("met_standing_buddha", "met/met_standing_buddha_brass.fbx", 2.80, "brass", 16000),
    ("met_seated_court_lady", "met/met_seated_court_lady.fbx", 1.85, "marble", 14000),
    ("met_bronze_boy", "met/met_bronze_boy_eastern_dress.fbx", 2.10, "brass", 16000),
    ("met_standing_horse", "met/met_standing_horse_carved.fbx", 2.45, "wood", 16000),
    ("met_lion_sarcophagus", "met/met_marble_lion_sarcophagus.fbx", 1.85, "marble", 16000),
    ("met_sphinx_capital", "met/met_marble_sphinx_capital.fbx", 2.20, "marble", 14000),
    ("met_morning_glories_screen", "met/met_morning_glories_screen.fbx", 2.60, "wood", 14000),

    ("statue_polyhymnia", "blenderkit/statue_scan_polyhymnia.blend", 3.40, "marble", 16000),
    ("statue_nymphe_salmacis", "blenderkit/statue_scan_nymphe_salmacis.blend", 2.85, "marble", 16000),
    ("statue_st_francis", "blenderkit/statue_scan_st_francis.blend", 3.80, "marble", 16000),
    ("statue_athena", "blenderkit/statue_scan_athena.blend", 3.50, "marble", 16000),
    ("statue_farnese_dionysos", "blenderkit/statue_scan_farnese_dionysos.blend", 3.30, "marble", 16000),
    ("statue_classical_woman", "blenderkit/statue_scan_classical_woman.blend", 2.95, "marble", 16000),

    ("ph_gothic_statue", "polyhaven/gothic_statue/gothic_statue_1k.gltf", 2.90, "stone", 16000),
    ("ph_marble_bust_01", "polyhaven/marble_bust_01/marble_bust_01_1k.gltf", 1.45, "marble", 14000),
    ("ph_horse_statue_01", "polyhaven/horse_statue_01/horse_statue_01_1k.gltf", 2.40, "brass", 14000),
    ("ph_lion_head", "polyhaven/lion_head/lion_head_1k.gltf", 1.50, "brass", 12000),
    ("ph_bull_head", "polyhaven/bull_head/bull_head_1k.gltf", 1.45, "brass", 12000),
    ("ph_bronze_whale", "polyhaven/bronze_whale_statue/bronze_whale_statue_1k.gltf", 1.60, "brass", 12000),
    ("ph_carved_elephant", "polyhaven/carved_wooden_elephant/carved_wooden_elephant_1k.gltf", 1.85, "wood", 12000),

    ("stanford_lucy_statue", "github/stanford_lucy.obj", 3.60, "marble", 18000),
    ("stanford_igea_bust", "github/stanford_igea_bust.obj", 1.50, "marble", 14000),
    ("stanford_bimba_bust", "github/stanford_bimba_bust.obj", 1.45, "marble", 14000),
    ("stanford_nefertiti_bust", "github/stanford_nefertiti_bust.obj", 1.55, "marble", 14000),
    ("stanford_happy_buddha", "github/stanford_happy_buddha.obj", 2.50, "brass", 16000),
    ("stanford_dragon", "github/stanford_dragon.obj", 2.10, "malachite", 16000),

    # Machinery, Locomotives, Carriages, Furniture, Chandeliers & Instruments
    ("exh_green_locomotive", "blenderkit/exh_green_steam_locomotive.blend", 3.80, "iron", 22000),
    ("exh_sewing_machine", "blenderkit/exh_scan_antique_sewing_machine.blend", 1.25, "iron", 14000),
    ("exh_grand_piano", "blenderkit/exh_grand_piano.blend", 1.65, "wood", 16000),
    ("exh_standing_globe", "blenderkit/exh_antique_standing_globe.blend", 1.55, "wood", 12000),
    ("exh_display_case", "blenderkit/exh_glass_display_case.blend", 2.25, "wood", 12000),
    ("exh_victorian_bench", "blenderkit/exh_victorian_street_bench.blend", 1.05, "iron", 12000),

    ("ph_cannon_01", "polyhaven/cannon_01/cannon_01_1k.gltf", 1.45, "iron", 14000),
    ("ph_dutch_ship", "polyhaven/dutch_ship_large_01/dutch_ship_large_01_1k.gltf", 3.20, "wood", 18000),
    ("ph_drill_press", "polyhaven/drill_press_01/drill_press_01_1k.gltf", 2.10, "iron", 14000),
    ("ph_vintage_microscope", "polyhaven/vintage_microscope/vintage_microscope_1k.gltf", 0.95, "brass", 10000),
    ("ph_camera_01", "polyhaven/Camera_01/Camera_01_1k.gltf", 1.40, "wood", 10000),
    ("ph_cash_register", "polyhaven/CashRegister_01/CashRegister_01_1k.gltf", 1.15, "brass", 10000),
    ("ph_armchair_01", "polyhaven/ArmChair_01/ArmChair_01_1k.gltf", 1.25, "wood", 10000),
    ("ph_classic_console", "polyhaven/ClassicConsole_01/ClassicConsole_01_1k.gltf", 1.10, "wood", 10000),
    ("ph_gothic_cabinet", "polyhaven/GothicCabinet_01/GothicCabinet_01_1k.gltf", 2.35, "wood", 12000),
    ("ph_gothic_commode", "polyhaven/GothicCommode_01/GothicCommode_01_1k.gltf", 1.35, "wood", 10000),
    ("ph_gothic_table", "polyhaven/gothic_coffee_table/gothic_coffee_table_1k.gltf", 0.95, "wood", 10000),
    ("ph_sofa_01", "polyhaven/Sofa_01/Sofa_01_1k.gltf", 1.20, "wood", 10000),
    ("ph_grandfather_clock", "polyhaven/vintage_grandfather_clock_01/vintage_grandfather_clock_01_1k.gltf", 2.45, "wood", 12000),
    ("ph_mantel_clock", "polyhaven/mantel_clock_01/mantel_clock_01_1k.gltf", 0.95, "brass", 10000),
    ("ph_chandelier_01", "polyhaven/Chandelier_01/Chandelier_01_1k.gltf", 1.85, "brass", 12000),
    ("ph_chandelier_02", "polyhaven/Chandelier_02/Chandelier_02_1k.gltf", 1.65, "brass", 12000),
    ("ph_chandelier_03", "polyhaven/Chandelier_03/Chandelier_03_1k.gltf", 1.95, "brass", 12000),
    ("ph_lantern_chandelier", "polyhaven/lantern_chandelier_01/lantern_chandelier_01_1k.gltf", 1.55, "brass", 10000),
    ("ph_chinese_chandelier", "polyhaven/chinese_chandelier/chinese_chandelier_1k.gltf", 1.75, "wood", 10000),
    ("ph_chinese_armchair", "polyhaven/chinese_armchair/chinese_armchair_1k.gltf", 1.15, "wood", 10000),
    ("ph_chinese_cabinet", "polyhaven/chinese_cabinet/chinese_cabinet_1k.gltf", 2.15, "wood", 12000),
    ("ph_chinese_screen", "polyhaven/chinese_screen_panels/chinese_screen_panels_1k.gltf", 2.35, "wood", 12000),
    ("ph_chinese_table", "polyhaven/chinese_console_table/chinese_console_table_1k.gltf", 1.10, "wood", 10000),
    ("ph_picture_frame_01", "polyhaven/fancy_picture_frame_01/fancy_picture_frame_01_1k.gltf", 1.65, "brass", 10000),
    ("ph_picture_frame_02", "polyhaven/fancy_picture_frame_02/fancy_picture_frame_02_1k.gltf", 1.85, "brass", 10000),
    ("ph_brass_vase_01", "polyhaven/brass_vase_01/brass_vase_01_1k.gltf", 1.25, "brass", 10000),
    ("ph_brass_vase_03", "polyhaven/brass_vase_03/brass_vase_03_1k.gltf", 1.15, "brass", 10000),
    ("ph_ceramic_vase_01", "polyhaven/antique_ceramic_vase_01/antique_ceramic_vase_01_1k.gltf", 1.20, "marble", 10000),
    ("ph_brass_candleholders", "polyhaven/brass_candleholders/brass_candleholders_1k.gltf", 0.85, "brass", 10000),
]

BLENDER_WORKER_CODE = r"""
import bpy, os, sys, math, json
from mathutils import Vector

SCANS_DIR = sys.argv[sys.argv.index("--") + 1]
READY_DIR = sys.argv[sys.argv.index("--") + 2]
SPEC_JSON = sys.argv[sys.argv.index("--") + 3]

slug, rel_path, target_h, mat_kind, max_faces = json.loads(SPEC_JSON)
out_blend = os.path.join(READY_DIR, f"{slug}.blend")
src_path = os.path.join(SCANS_DIR, rel_path)

FALLBACK_COLORS = {
    "marble": ((0.91, 0.89, 0.85, 1.0), 0.22, 0.0),
    "stone": ((0.76, 0.72, 0.65, 1.0), 0.55, 0.0),
    "brass": ((0.83, 0.66, 0.26, 1.0), 0.22, 0.88),
    "iron": ((0.18, 0.24, 0.30, 1.0), 0.38, 0.78),
    "wood": ((0.36, 0.20, 0.11, 1.0), 0.36, 0.0),
    "malachite": ((0.09, 0.44, 0.26, 1.0), 0.16, 0.05),
    "glass": ((0.88, 0.95, 0.98, 1.0), 0.04, 0.0),
    "cloth": ((0.28, 0.22, 0.20, 1.0), 0.65, 0.0),
}

def make_fallback_mat(kind):
    rgba, rough, met = FALLBACK_COLORS.get(kind, ((0.7, 0.7, 0.7, 1.0), 0.4, 0.0))
    m = bpy.data.materials.new(f"Fallback_{kind}")
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = met
        if kind == "glass" and "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = 0.88
    return m

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
ext = os.path.splitext(src_path)[1].lower()
if ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=src_path)
elif ext in (".gltf", ".glb"):
    bpy.ops.import_scene.gltf(filepath=src_path)
elif ext == ".obj":
    bpy.ops.wm.obj_import(filepath=src_path)
elif ext == ".blend":
    with bpy.data.libraries.load(src_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    for o in data_to.objects:
        if o is not None and o.type == "MESH":
            bpy.context.scene.collection.objects.link(o)

bpy.context.view_layer.update()
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and len(o.data.polygons) > 4]
if not meshes:
    sys.exit(0)

if len(meshes) > 1 and slug != "arch_sponza_atrium":
    filtered = []
    for o in meshes:
        corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
        dx = max(c.x for c in corners) - min(c.x for c in corners)
        dy = max(c.y for c in corners) - min(c.y for c in corners)
        dz = max(c.z for c in corners) - min(c.z for c in corners)
        if max(dx, dy) > 25.0 and dz < 0.25:
            continue
        if "plane" in o.name.lower() or "backdrop" in o.name.lower() or "bg" in o.name.lower():
            if len(meshes) > 2:
                continue
        filtered.append(o)
    if filtered:
        meshes = filtered

# Keep top 40 largest meshes if there are hundreds of tiny bolt sub-objects
if len(meshes) > 40:
    meshes.sort(key=lambda o: len(o.data.polygons), reverse=True)
    meshes = meshes[:40]

bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.context.scene.objects):
    if o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
try:
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
except Exception:
    pass
if len(meshes) > 1:
    bpy.ops.object.join()

joined = bpy.context.view_layer.objects.active
joined.name = f"SCAN_{slug}"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

if ext == ".obj" and "stanford" in slug:
    corners = [Vector(c) for c in joined.bound_box]
    dx = max(c.x for c in corners) - min(c.x for c in corners)
    dy = max(c.y for c in corners) - min(c.y for c in corners)
    dz = max(c.z for c in corners) - min(c.z for c in corners)
    if dy > dz * 1.15:
        joined.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

f_count = len(joined.data.polygons)
if f_count > max_faces:
    ratio = max(0.04, float(max_faces) / float(f_count))
    mod = joined.modifiers.new(name="DecimateScan", type='DECIMATE')
    mod.ratio = ratio
    bpy.ops.object.modifier_apply(modifier=mod.name)

verts = [v.co for v in joined.data.vertices]
if verts:
    xmin = min(v.x for v in verts); xmax = max(v.x for v in verts)
    ymin = min(v.y for v in verts); ymax = max(v.y for v in verts)
    zmin = min(v.z for v in verts); zmax = max(v.z for v in verts)
    cur_h = max(1e-4, zmax - zmin)
    scale_f = float(target_h) / cur_h
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)
    for v in joined.data.vertices:
        v.co.x = (v.co.x - cx) * scale_f
        v.co.y = (v.co.y - cy) * scale_f
        v.co.z = (v.co.z - zmin) * scale_f
    joined.data.update()

if len(joined.data.materials) == 0 or all(m is None for m in joined.data.materials):
    joined.data.materials.clear()
    joined.data.materials.append(make_fallback_mat(mat_kind))

base_dir = os.path.dirname(src_path)
for img in bpy.data.images:
    if img.filepath:
        abs_p = bpy.path.abspath(img.filepath, library=img.library)
        if not os.path.exists(abs_p):
            cand = os.path.join(base_dir, os.path.basename(img.filepath.replace("\\", "/")))
            if os.path.exists(cand):
                abs_p = cand
            else:
                cand2 = os.path.join(base_dir, "textures", os.path.basename(img.filepath.replace("\\", "/")))
                if os.path.exists(cand2):
                    abs_p = cand2
        img.filepath = abs_p

bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
print(f"  [READY] {slug:32s} -> {len(joined.data.polygons):6d} faces, h={target_h:.2f}m ({os.path.getsize(out_blend)//1024} KB)")
"""


def main():
    os.makedirs(READY_DIR, exist_ok=True)
    worker_script = os.path.join(SCANS_DIR, "_worker_prepare_one.py")
    with open(worker_script, "w", encoding="utf-8") as fh:
        fh.write(BLENDER_WORKER_CODE)

    for spec in ASSET_SPECS:
        slug = spec[0]
        out_blend = os.path.join(READY_DIR, f"{slug}.blend")
        if os.path.exists(out_blend) and os.path.getsize(out_blend) > 4096:
            continue
        cmd = [
            "blender",
            "--background",
            "--python",
            worker_script,
            "--python-exit-code",
            "1",
            "--",
            SCANS_DIR,
            READY_DIR,
            json.dumps(spec),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            for line in res.stdout.splitlines():
                if "[READY]" in line:
                    print(line, flush=True)
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT-SKIP] {slug} (>25s)", flush=True)
            subprocess.run(["pkill", "-9", "-f", "_worker_prepare_one"], check=False)

    ready_files = sorted(f for f in os.listdir(READY_DIR) if f.endswith(".blend"))
    print(f"\nTotal ready 3D scan assets in {READY_DIR}: {len(ready_files)}")


if __name__ == "__main__":
    main()
