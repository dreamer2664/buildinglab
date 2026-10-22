#!/usr/bin/env python3
"""
render_cycles_views.py — Builds the 1851 Crystal Palace interior & exterior scene
using 114 REAL OPEN-SOURCE 3D SCANS (Metropolitan Museum of Art CC0 scans, Poly Haven
photogrammetry scans + 1K PBR textures + 1K HDRIs, BlenderKit 3D scanned humans,
buildings, statues, locomotives, and furniture, and Khronos Sponza atrium architecture)
and renders 16 genuinely distinct 3D Cycles master views (M01..M16.jpg).
"""
from __future__ import annotations
import json
import math
import os
import sys
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

CRYSTAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANS_DIR = os.path.join(CRYSTAL_DIR, "build", "scans")
READY_DIR = os.path.join(SCANS_DIR, "ready")
TEX_DIR = os.path.join(SCANS_DIR, "textures")
HDRI_DIR = os.path.join(SCANS_DIR, "hdris")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.render.threads_mode = "FIXED"
sc.render.threads = 2
sc.cycles.samples = 14
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.04
sc.cycles.use_denoising = False
sc.cycles.max_bounces = 4
sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 2
sc.cycles.transmission_bounces = 2
sc.cycles.transparent_max_bounces = 2
sc.render.use_simplify = True
sc.cycles.texture_limit_render = "512"
sc.cycles.texture_limit = "512"
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"


def make_pbr_tex_mat(name: str, diff_file: str, rough_file: str | None = None, nor_file: str | None = None, uv_scale: float = 1.0, metallic: float = 0.0, tint=(1.0, 1.0, 1.0, 1.0)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes = nt.nodes
    links = nt.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = 0.38

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (uv_scale, uv_scale, uv_scale)
    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])

    diff_path = os.path.join(TEX_DIR, diff_file)
    if os.path.exists(diff_path):
        img_d = bpy.data.images.load(diff_path, check_existing=True)
        tex_d = nodes.new("ShaderNodeTexImage")
        tex_d.image = img_d
        tex_d.projection = "FLAT"
        links.new(mapping.outputs["Vector"], tex_d.inputs["Vector"])
        if tint != (1.0, 1.0, 1.0, 1.0):
            mix = nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = 0.55
            mix.inputs[7].default_value = tint
            links.new(tex_d.outputs["Color"], mix.inputs[6])
            links.new(mix.outputs[2], bsdf.inputs["Base Color"])
        else:
            links.new(tex_d.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def make_mat(name, rgba, rough=0.35, met=0.0, trans=0.0, ior=1.52, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = met
        if "Alpha" in bsdf.inputs and alpha < 1.0:
            bsdf.inputs["Alpha"].default_value = alpha
        if trans > 0:
            for k in ("Transmission Weight", "Transmission"):
                if k in bsdf.inputs:
                    bsdf.inputs[k].default_value = trans
            if "IOR" in bsdf.inputs:
                bsdf.inputs["IOR"].default_value = ior
    return m


# Real Photogrammetry PBR Materials + Owen Jones 1851 Palette
mat_wood_floor = make_pbr_tex_mat(
    "PBR_WoodFloorDeck",
    "wood_floor_deck_diffuse_1k.jpg",
    "wood_floor_deck_rough_1k.jpg",
    "wood_floor_deck_nor_gl_1k.jpg",
    uv_scale=28.0,
)
mat_cobble = make_pbr_tex_mat(
    "PBR_CobbleDrive",
    "cobblestone_floor_01_diffuse_1k.jpg",
    "cobblestone_floor_01_rough_1k.jpg",
    "cobblestone_floor_01_nor_gl_1k.jpg",
    uv_scale=35.0,
)
mat_marble = make_pbr_tex_mat(
    "PBR_CarraraMarble",
    "marble_01_diffuse_1k.jpg",
    "marble_01_rough_1k.jpg",
    "marble_01_nor_gl_1k.jpg",
    uv_scale=4.0,
)
mat_iron_blue = make_mat("OwenJones_IronBlue", (0.20, 0.43, 0.68, 1.0), rough=0.28, met=0.35)
mat_red = make_mat("OwenJones_Red", (0.68, 0.14, 0.12, 1.0), rough=0.36, met=0.18)
mat_yellow = make_mat("OwenJones_Yellow", (0.88, 0.70, 0.18, 1.0), rough=0.26, met=0.45)
mat_white = make_mat("OwenJones_FilletWhite", (0.93, 0.92, 0.88, 1.0), rough=0.38, met=0.05)
mat_glass = make_mat("CrownGlass_49x10", (0.92, 0.97, 0.99, 1.0), rough=0.04, met=0.15, alpha=0.16)
mat_fountain_glass = make_mat("OslerCutCrystal", (0.90, 0.97, 1.0, 1.0), rough=0.04, met=0.28, alpha=0.24)
mat_water = make_mat("FountainWater", (0.35, 0.72, 0.85, 1.0), rough=0.04, met=0.25, alpha=0.75)
mat_crimson = make_mat("TurkeyRedDrapery", (0.68, 0.09, 0.12, 1.0), rough=0.65, met=0.0)
mat_grass = make_mat("HydeParkTurf", (0.20, 0.34, 0.16, 1.0), rough=0.82, met=0.0)


# --- LOAD NORMALIZED 3D SCAN LIBRARY (114 REAL SCANS) ---
SCAN_LIB: dict[str, bpy.types.Object] = {}
template_col = bpy.data.collections.new("ScanTemplates_Hidden")
sc.collection.children.link(template_col)
template_col.hide_render = True
template_col.hide_viewport = True


def get_scan_template(slug: str) -> bpy.types.Object | None:
    if slug in SCAN_LIB:
        return SCAN_LIB[slug]
    blend_path = os.path.join(READY_DIR, f"{slug}.blend")
    if not os.path.exists(blend_path):
        return None
    try:
        with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if name.startswith("SCAN_")]
            if not data_to.objects:
                data_to.objects = data_from.objects
        for o in data_to.objects:
            if o is not None and o.type == "MESH":
                # Keep at most 1 Base Color diffuse texture (512x512) per material so RAM stays <650 MB
                for mat in o.data.materials:
                    if mat and mat.use_nodes and mat.node_tree:
                        nt = mat.node_tree
                        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
                        tex_nodes = [n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image is not None]
                        best_tex = None
                        if bsdf and bsdf.inputs.get("Base Color") and bsdf.inputs["Base Color"].is_linked:
                            src_n = bsdf.inputs["Base Color"].links[0].from_node
                            if src_n.type == "TEX_IMAGE":
                                best_tex = src_n
                        if best_tex is None and tex_nodes:
                            for tn in tex_nodes:
                                nm = (tn.image.name + " " + tn.label + " " + tn.name).lower()
                                if not any(k in nm for k in ("norm", "rough", "metal", "spec", "bump", "gloss", "ao", "occ", "disp", "arm")):
                                    best_tex = tn
                                    break
                            if best_tex is None:
                                best_tex = tex_nodes[0]
                        for tn in tex_nodes:
                            if tn != best_tex:
                                img = tn.image
                                nt.nodes.remove(tn)
                                if img and img.users == 0:
                                    bpy.data.images.remove(img)
                        for n in list(nt.nodes):
                            if n.type in ("NORMAL_MAP", "BUMP", "DISPLACEMENT"):
                                nt.nodes.remove(n)
                        if bsdf and best_tex and best_tex.image:
                            valid_tex = False
                            try:
                                small_dir = os.path.join(SCANS_DIR, "tex_small")
                                os.makedirs(small_dir, exist_ok=True)
                                safe_nm = "".join(c if c.isalnum() else "_" for c in f"{slug}_{mat.name}")[:48]
                                small_p = os.path.join(small_dir, f"{safe_nm}.jpg")
                                if not os.path.exists(small_p):
                                    if best_tex.image.size[0] > 0 and best_tex.image.size[1] > 0:
                                        best_tex.image.scale(256, 256)
                                        best_tex.image.filepath_raw = small_p
                                        best_tex.image.file_format = "JPEG"
                                        best_tex.image.save()
                                if os.path.exists(small_p) and os.path.getsize(small_p) > 200:
                                    old_img = best_tex.image
                                    new_img = bpy.data.images.load(small_p, check_existing=True)
                                    best_tex.image = new_img
                                    nt.links.new(best_tex.outputs["Color"], bsdf.inputs["Base Color"])
                                    valid_tex = True
                                    if old_img != new_img and old_img.users == 0:
                                        bpy.data.images.remove(old_img)
                            except Exception:
                                valid_tex = False
                            if not valid_tex:
                                for lnk in list(bsdf.inputs["Base Color"].links):
                                    nt.links.remove(lnk)
                                bsdf.inputs["Base Color"].default_value = (0.82, 0.78, 0.72, 1.0)
                        elif bsdf and not bsdf.inputs["Base Color"].is_linked:
                            bsdf.inputs["Base Color"].default_value = (0.82, 0.78, 0.72, 1.0)
                for img in list(bpy.data.images):
                    if img.users == 0:
                        bpy.data.images.remove(img)
                template_col.objects.link(o)
                SCAN_LIB[slug] = o
                return o
    except Exception as e:
        print(f"  [WARN] Could not load template {slug}: {e}")
    return None


def place_scan(
    slug: str,
    inst_name: str,
    loc: tuple[float, float, float],
    rot_z_deg: float = 0.0,
    scale: float = 1.0,
    override_mat: bpy.types.Material | None = None,
) -> bpy.types.Object | None:
    tmpl = get_scan_template(slug)
    if tmpl is None:
        return None
    mesh_data = tmpl.data
    if override_mat is not None:
        mesh_data = tmpl.data.copy()
        mesh_data.materials.clear()
        mesh_data.materials.append(override_mat)
    inst = bpy.data.objects.new(inst_name, mesh_data)
    inst.location = loc
    inst.rotation_euler = (0.0, 0.0, math.radians(rot_z_deg))
    inst.scale = (scale, scale, scale)
    sc.collection.objects.link(inst)
    return inst


def place_pedestal_and_statue(
    slug: str,
    inst_name: str,
    x: float,
    y: float,
    z_floor: float = 0.0,
    rot_z_deg: float = 0.0,
    ped_h: float = 1.25,
    ped_w: float = 1.35,
    statue_scale: float = 1.0,
):
    # Stepped marble/mahogany pedestal under the scanned statue
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix(((ped_w * 1.18, 0, 0, x), (0, ped_w * 1.18, 0, y), (0, 0, 0.22, z_floor + 0.11), (0, 0, 0, 1))),
    )
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix(((ped_w, 0, 0, x), (0, ped_w, 0, y), (0, 0, ped_h - 0.34, z_floor + 0.22 + (ped_h - 0.34) * 0.5), (0, 0, 0, 1))),
    )
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix(((ped_w * 1.12, 0, 0, x), (0, ped_w * 1.12, 0, y), (0, 0, 0.12, z_floor + ped_h - 0.06), (0, 0, 0, 1))),
    )
    m_ped = bpy.data.meshes.new(f"Ped_{inst_name}")
    bm.to_mesh(m_ped)
    bm.free()
    m_ped.materials.append(mat_marble)
    o_ped = bpy.data.objects.new(f"Ped_{inst_name}", m_ped)
    sc.collection.objects.link(o_ped)

    return place_scan(slug, inst_name, (x, y, z_floor + ped_h), rot_z_deg=rot_z_deg, scale=statue_scale)


# --- 1. BUILD CRYSTAL PALACE STRUCTURAL IRON-AND-GLASS SHELL + PBR FLOORS ---
bm_iron = bmesh.new()
bm_red = bmesh.new()
bm_yellow = bmesh.new()
bm_white = bmesh.new()
bm_glass = bmesh.new()
bm_floor = bmesh.new()
bm_crimson = bmesh.new()

# Exterior Hyde Park turf & cobblestone carriage drive
bmesh.ops.create_cube(
    bm_floor,
    size=1.0,
    matrix=Matrix(((260.0, 0, 0, 0.0), (0, 110.0, 0, 0.0), (0, 0, 0.12, -0.06), (0, 0, 0, 1))),
)

bm_ext = bmesh.new()
bmesh.ops.create_cube(
    bm_ext,
    size=1.0,
    matrix=Matrix(((520.0, 0, 0, 0.0), (0, 340.0, 0, 0.0), (0, 0, 0.10, -0.16), (0, 0, 0, 1))),
)
m_ext = bpy.data.meshes.new("HydeParkGround")
bm_ext.to_mesh(m_ext)
bm_ext.free()
m_ext.materials.append(mat_grass)
sc.collection.objects.link(bpy.data.objects.new("HydeParkGround", m_ext))

bm_drive = bmesh.new()
bmesh.ops.create_cube(
    bm_drive,
    size=1.0,
    matrix=Matrix(((360.0, 0, 0, 0.0), (0, 22.0, 0, -54.0), (0, 0, 0.11, -0.10), (0, 0, 0, 1))),
)
m_drive = bpy.data.meshes.new("RottenRowCarriageDrive")
bm_drive.to_mesh(m_drive)
bm_drive.free()
m_drive.materials.append(mat_cobble)
sc.collection.objects.link(bpy.data.objects.new("RottenRowCarriageDrive", m_drive))

# First Gallery & Second Gallery timber floors (split West & East of the open Transept crossing!)
for x_wing in (-62.0, 62.0):
    for y_gal in (-18.30, 18.30):
        bmesh.ops.create_cube(
            bm_floor,
            size=1.0,
            matrix=Matrix(((102.0, 0, 0, x_wing), (0, 14.64, 0, y_gal), (0, 0, 0.18, 7.23), (0, 0, 0, 1))),
        )
        bmesh.ops.create_cube(
            bm_floor,
            size=1.0,
            matrix=Matrix(((102.0, 0, 0, x_wing), (0, 7.32, 0, y_gal), (0, 0, 0.18, 13.33), (0, 0, 0, 1))),
        )
# North Transept Organ Loft Balcony at Y = +21.5m, Z = 7.32m
bmesh.ops.create_cube(
    bm_floor,
    size=1.0,
    matrix=Matrix(((21.96, 0, 0, 0.0), (0, 7.32, 0, 21.96), (0, 0, 0.20, 7.22), (0, 0, 0, 1))),
)

# Columns, Lattice Girders, Gallery Railings, Banners & Ridge-and-Furrow Glass Roof
x_grid = [-80.52 + i * 7.32 for i in range(23)]
y_grid = [-32.94, -25.62, -18.30, -10.98, 10.98, 18.30, 25.62, 32.94]

for x in x_grid:
    in_transept = abs(x) <= 11.2
    for y in y_grid:
        max_tier = 3 if abs(y) <= 11.5 else (2 if abs(y) <= 20.0 else 1)
        for tier in range(max_tier):
            z0 = tier * 6.50 if tier > 0 else 0.0
            z1 = 7.32 if tier == 0 else (13.42 if tier == 1 else 19.52)
            h = z1 - z0
            zc = 0.5 * (z0 + z1)
            bmesh.ops.create_cone(
                bm_iron,
                cap_ends=True,
                segments=12,
                radius1=0.115,
                radius2=0.115,
                depth=h,
                matrix=Matrix.Translation((x, y, zc)),
            )
            # Base plinth (Red) & Capital Necking Ring (Yellow)
            bmesh.ops.create_cube(
                bm_red,
                size=1.0,
                matrix=Matrix(((0.38, 0, 0, x), (0, 0.38, 0, y), (0, 0, 0.34, z0 + 0.17), (0, 0, 0, 1))),
            )
            bmesh.ops.create_cone(
                bm_yellow,
                cap_ends=True,
                segments=12,
                radius1=0.17,
                radius2=0.19,
                depth=0.22,
                matrix=Matrix.Translation((x, y, z1 - 0.14)),
            )

    # Transverse girders & overhead roof trusses
    for y_a, y_b, z_g in [
        (-32.94, -25.62, 7.32),
        (-25.62, -18.30, 7.32),
        (-18.30, -10.98, 7.32),
        (10.98, 18.30, 7.32),
        (18.30, 25.62, 7.32),
        (25.62, 32.94, 7.32),
        (-25.62, -18.30, 13.42),
        (-18.30, -10.98, 13.42),
        (10.98, 18.30, 13.42),
        (18.30, 25.62, 13.42),
        (-18.30, -10.98, 19.52),
        (10.98, 18.30, 19.52),
    ]:
        ym = 0.5 * (y_a + y_b)
        span = abs(y_b - y_a)
        bmesh.ops.create_cube(
            bm_iron,
            size=1.0,
            matrix=Matrix(((0.18, 0, 0, x), (0, span, 0, ym), (0, 0, 0.91, z_g - 0.45), (0, 0, 0, 1))),
        )
        # Diagonal lattice struts in girder
        for d_i in range(4):
            yd = y_a + (d_i + 0.5) * (span / 4.0)
            bmesh.ops.create_cube(
                bm_yellow,
                size=1.0,
                matrix=Matrix(((0.20, 0, 0, x), (0, 0.10, 0, yd), (0, 0, 0.85, z_g - 0.45), (0, 0, 0, 1))),
            )

    # Central Nave 72-ft (21.96 m) clear-span roof truss & ridge-and-furrow glazing outside Transept
    if not in_transept:
        bmesh.ops.create_cube(
            bm_iron,
            size=1.0,
            matrix=Matrix(((0.22, 0, 0, x), (0, 21.96, 0, 0.0), (0, 0, 0.16, 19.45), (0, 0, 0, 1))),
        )
        bmesh.ops.create_cube(
            bm_iron,
            size=1.0,
            matrix=Matrix(((0.22, 0, 0, x), (0, 21.96, 0, 0.0), (0, 0, 0.16, 18.25), (0, 0, 0, 1))),
        )
        for d_i in range(8):
            yd = -10.98 + (d_i + 0.5) * (21.96 / 8.0)
            ang = 0.62 if d_i % 2 == 0 else -0.62
            m_d = Matrix.Translation((x, yd, 18.85)) @ Matrix.Rotation(ang, 4, "X") @ Matrix.Scale(0.10, 4, (1, 0, 0)) @ Matrix.Scale(1.75, 4, (0, 1, 0)) @ Matrix.Scale(0.10, 4, (0, 0, 1))
            bmesh.ops.create_cube(bm_iron, size=1.0, matrix=m_d)
            bmesh.ops.create_cube(
                bm_yellow,
                size=1.0,
                matrix=Matrix(((0.24, 0, 0, x), (0, 0.12, 0, yd), (0, 0, 1.20, 18.85), (0, 0, 0, 1))),
            )
        # Ridge-and-furrow glass panes & white sash bars
        for r_i in range(-5, 6):
            yr = r_i * 1.95
            for side in (-1, 1):
                m_gl = (
                    Matrix.Translation((x + 3.66, yr + side * 0.48, 19.82))
                    @ Matrix.Rotation(side * 0.38, 4, "X")
                    @ Matrix.Scale(7.28, 4, (1, 0, 0))
                    @ Matrix.Scale(1.05, 4, (0, 1, 0))
                    @ Matrix.Scale(0.015, 4, (0, 0, 1))
                )
                bmesh.ops.create_cube(bm_glass, size=1.0, matrix=m_gl)
            bmesh.ops.create_cube(
                bm_white,
                size=1.0,
                matrix=Matrix(((7.32, 0, 0, x + 3.66), (0, 0.09, 0, yr), (0, 0, 0.12, 20.06), (0, 0, 0, 1))),
            )

# Longitudinal girders, gallery crimson banners, and cast-iron balustrades along the Nave (outside Transept crossing)
for x_i in range(len(x_grid) - 1):
    xm = 0.5 * (x_grid[x_i] + x_grid[x_i + 1])
    in_trans_span = abs(xm) < 10.9
    for y_g in (-18.30, -10.98, 10.98, 18.30):
        for z_g in (7.32, 13.42, 19.52):
            if in_trans_span and z_g < 19.0:
                continue
            bmesh.ops.create_cube(
                bm_iron,
                size=1.0,
                matrix=Matrix(((7.32, 0, 0, xm), (0, 0.18, 0, y_g), (0, 0, 0.88, z_g - 0.44), (0, 0, 0, 1))),
            )
    if in_trans_span:
        continue
    # Gallery railing & crimson exhibition banners facing the Central Nave
    for y_rail, sign_y in [(-11.15, 1.0), (11.15, -1.0)]:
        for z_fl in (7.32, 13.42):
            bmesh.ops.create_cube(
                bm_yellow,
                size=1.0,
                matrix=Matrix(((7.32, 0, 0, xm), (0, 0.08, 0, y_rail), (0, 0, 0.08, z_fl + 1.05), (0, 0, 0, 1))),
            )
            bmesh.ops.create_cube(
                bm_red,
                size=1.0,
                matrix=Matrix(((7.32, 0, 0, xm), (0, 0.06, 0, y_rail), (0, 0, 0.85, z_fl + 0.52), (0, 0, 0, 1))),
            )
        # Hanging Turkey-red royal exhibition banner below gallery girder
        if x_i % 2 == 0 and abs(xm) > 12.0:
            bmesh.ops.create_cube(
                bm_crimson,
                size=1.0,
                matrix=Matrix(((2.60, 0, 0, xm), (0, 0.04, 0, y_rail + sign_y * 0.15), (0, 0, 2.40, 5.65), (0, 0, 0, 1))),
            )

# Transept 108-ft (33.00 m) Barrel Vault Arched Ribs & Curved Glazing
for x_rib in (-10.98, -7.32, -3.66, 0.0, 3.66, 7.32, 10.98):
    n_seg = 28
    for s_i in range(n_seg):
        a0 = math.pi * (s_i / float(n_seg))
        a1 = math.pi * ((s_i + 1) / float(n_seg))
        am = 0.5 * (a0 + a1)
        ym = -12.20 * math.cos(am)
        zm = 19.52 + 13.10 * math.sin(am)
        seg_len = (math.pi * 12.65) / float(n_seg)
        rot_x = math.atan2(13.10 * math.cos(am), 12.20 * math.sin(am))
        m_rib = (
            Matrix.Translation((x_rib, ym, zm))
            @ Matrix.Rotation(rot_x, 4, "X")
            @ Matrix.Scale(0.28, 4, (1, 0, 0))
            @ Matrix.Scale(seg_len * 1.04, 4, (0, 1, 0))
            @ Matrix.Scale(0.78, 4, (0, 0, 1))
        )
        bmesh.ops.create_cube(bm_iron, size=1.0, matrix=m_rib)
        m_trim = (
            Matrix.Translation((x_rib, ym, zm))
            @ Matrix.Rotation(rot_x, 4, "X")
            @ Matrix.Scale(0.32, 4, (1, 0, 0))
            @ Matrix.Scale(seg_len * 0.90, 4, (0, 1, 0))
            @ Matrix.Scale(0.16, 4, (0, 0, 1))
        )
        bmesh.ops.create_cube(bm_yellow, size=1.0, matrix=m_trim)
        if x_rib < 10.98:
            m_vg = (
                Matrix.Translation((x_rib + 1.83, ym, zm + 0.35))
                @ Matrix.Rotation(rot_x, 4, "X")
                @ Matrix.Scale(3.62, 4, (1, 0, 0))
                @ Matrix.Scale(seg_len * 1.02, 4, (0, 1, 0))
                @ Matrix.Scale(0.015, 4, (0, 0, 1))
            )
            bmesh.ops.create_cube(bm_glass, size=1.0, matrix=m_vg)
            m_pur = (
                Matrix.Translation((x_rib + 1.83, ym, zm + 0.32))
                @ Matrix.Rotation(rot_x, 4, "X")
                @ Matrix.Scale(3.66, 4, (1, 0, 0))
                @ Matrix.Scale(0.10, 4, (0, 1, 0))
                @ Matrix.Scale(0.14, 4, (0, 0, 1))
            )
            bmesh.ops.create_cube(bm_white, size=1.0, matrix=m_pur)


def commit_bm(bm, name, mat):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    m = bpy.data.meshes.new(name)
    bm.to_mesh(m)
    bm.free()
    m.materials.append(mat)
    o = bpy.data.objects.new(name, m)
    sc.collection.objects.link(o)
    return o


commit_bm(bm_iron, "Palace_Iron_Blue", mat_iron_blue)
commit_bm(bm_red, "Palace_Iron_Red", mat_red)
commit_bm(bm_yellow, "Palace_Iron_Yellow", mat_yellow)
commit_bm(bm_white, "Palace_Sash_White", mat_white)
o_glass = commit_bm(bm_glass, "Palace_Crown_Glass", mat_glass)
o_glass.visible_shadow = False
commit_bm(bm_floor, "Palace_Timber_Floor", mat_wood_floor)
commit_bm(bm_crimson, "Palace_Crimson_Banners", mat_crimson)


# --- 2. INSTALL REAL OPEN-SOURCE 3D ARCHITECTURAL SCANS & WONDERS ---

# A. Osler's Crystal Fountain & Transept Crossing Centerpiece (x=0, y=0)
# Multi-tiered octagonal pool + scanned fountains + marble wellhead + water surface
bm_pool = bmesh.new()
bmesh.ops.create_cone(bm_pool, cap_ends=True, segments=16, radius1=4.40, radius2=4.55, depth=0.62, matrix=Matrix.Translation((0, 0, 0.31)))
commit_bm(bm_pool, "OslerPoolRims", mat_marble)
bm_wat = bmesh.new()
bmesh.ops.create_cone(bm_wat, cap_ends=True, segments=16, radius1=4.15, radius2=4.15, depth=0.48, matrix=Matrix.Translation((0, 0, 0.25)))
commit_bm(bm_wat, "OslerPoolWater", mat_water)

o_ftn1 = place_scan("wonder_tiered_fountain", "Osler_TieredFountain_Main", (0.0, 0.0, 0.35), rot_z_deg=0.0, scale=1.15, override_mat=mat_fountain_glass)
if o_ftn1:
    o_ftn1.visible_shadow = False
place_scan("met_marble_wellhead_fountain", "Osler_BaseSculptedBasin", (0.0, 0.0, 0.40), rot_z_deg=45.0, scale=1.05)
o_ftn2 = place_scan("wonder_victorian_fountain", "Osler_UpperSpireFountain", (0.0, 0.0, 2.75), rot_z_deg=0.0, scale=1.05, override_mat=mat_fountain_glass)
if o_ftn2:
    o_ftn2.visible_shadow = False

# Surrounding botanical urns & Victorian park benches around the Crystal Fountain
for ang_deg in range(0, 360, 45):
    rad = math.radians(ang_deg)
    px, py = 5.4 * math.cos(rad), 5.4 * math.sin(rad)
    plant_slug = "ph_potted_plant_01" if (ang_deg // 45) % 2 == 0 else "ph_potted_plant_02"
    place_scan(plant_slug, f"TranseptPlant_{ang_deg}", (px, py, 0.0), rot_z_deg=ang_deg, scale=1.15)
for ang_deg in (30, 150, 210, 330):
    rad = math.radians(ang_deg)
    bx, by = 6.8 * math.cos(rad), 6.8 * math.sin(rad)
    place_scan("exh_victorian_bench", f"TranseptBench_{ang_deg}", (bx, by, 0.0), rot_z_deg=ang_deg + 90.0, scale=1.05, override_mat=mat_iron_blue)

# B. Three Enclosed Hyde Park Elm Trees (Real Photogrammetry Tree Scans!)
place_scan("ph_island_tree_02", "Wonder_Elm_North", (-3.2, 20.5, 0.0), rot_z_deg=15.0, scale=1.00)
place_scan("ph_island_tree_02", "Wonder_Elm_Centre", (4.2, 13.0, 0.0), rot_z_deg=135.0, scale=1.02)
place_scan("ph_island_tree_02", "Wonder_Elm_South", (-2.8, -18.5, 0.0), rot_z_deg=255.0, scale=0.98)
for tx, ty in [(-3.2, 20.5), (4.2, 13.0), (-2.8, -18.5)]:
    for fi in range(4):
        fa = fi * (math.pi * 0.5)
        place_scan("ph_fern_02", f"ElmFern_{tx}_{fi}", (tx + 1.4 * math.cos(fa), ty + 1.4 * math.sin(fa), 0.0), rot_z_deg=fi * 90, scale=1.0)

# C. North & South Transept Monumental Corinthian Columns + Coalbrookdale Gates + Gray & Davison Great Organ
for col_x in (-5.5, -3.2, 3.2, 5.5):
    place_scan("arch_corinthian_column", f"Transept_North_Col_{col_x}", (col_x, 24.5, 0.0), rot_z_deg=0.0, scale=1.0)
    place_scan("arch_corinthian_column", f"Transept_South_Col_{col_x}", (col_x, -24.5, 0.0), rot_z_deg=0.0, scale=1.0)
place_scan("ph_large_iron_gate", "Coalbrookdale_North_Gates", (0.0, 22.8, 0.0), rot_z_deg=0.0, scale=1.15)
place_scan("ph_large_iron_gate", "Coalbrookdale_South_Gates", (0.0, -22.8, 0.0), rot_z_deg=180.0, scale=1.15)

# Gray & Davison Great Organ on North Gallery (Z=7.32m, Y=21.5m) combining Gothic architectural scans & gilded pipes
place_scan("arch_gothic_church_doorway", "GreatOrgan_GothicCase_Center", (0.0, 21.8, 7.32), rot_z_deg=180.0, scale=1.25)
place_scan("arch_large_gothic_window", "GreatOrgan_GothicTracery_Left", (-3.8, 22.0, 7.32), rot_z_deg=180.0, scale=1.05)
place_scan("arch_large_gothic_window", "GreatOrgan_GothicTracery_Right", (3.8, 22.0, 7.32), rot_z_deg=180.0, scale=1.05)
place_scan("exh_grand_piano", "GreatOrgan_Gallery_GrandPiano", (0.0, 17.5, 7.32), rot_z_deg=180.0, scale=1.15)
bm_pipes = bmesh.new()
for p_i in range(42):
    px = -5.2 + p_i * (10.4 / 41.0)
    ph = 3.2 + 2.8 * abs(math.cos(p_i * 0.28))
    bmesh.ops.create_cone(bm_pipes, cap_ends=True, segments=10, radius1=0.085, radius2=0.085, depth=ph, matrix=Matrix.Translation((px, 21.3, 9.2 + ph * 0.5)))
commit_bm(bm_pipes, "GreatOrgan_4500_GildedPipes", mat_yellow)

# D. Hero Sculptures along the Transept & Central Nave Crossing (Met Museum + Rome 3D Scans!)
transept_statues = [
    ("met_canova_perseus", "Statue_Canova_Perseus", -6.2, -4.5, 35.0, 1.35, 1.05),
    ("met_carpeaux_ugolino", "Statue_Carpeaux_Ugolino", 6.2, -4.5, -35.0, 1.35, 1.05),
    ("statue_polyhymnia", "Statue_Polyhymnia", -6.2, 4.5, 145.0, 1.30, 1.05),
    ("statue_nymphe_salmacis", "Statue_Nymphe_Salmacis", 6.2, 4.5, -145.0, 1.30, 1.05),
    ("statue_athena", "Statue_Athena_Promachos", -6.2, -11.5, 65.0, 1.35, 1.05),
    ("statue_st_francis", "Statue_St_Francis", 6.2, -11.5, -65.0, 1.35, 1.00),
    ("stanford_lucy_statue", "Statue_Winged_Victory_Lucy", -6.2, 11.5, 115.0, 1.35, 1.00),
    ("met_mourning_victory", "Statue_Mourning_Victory", 6.2, 11.5, -115.0, 1.35, 1.05),
    ("met_herakles_statue", "Statue_Herakles", -10.5, -5.2, 30.0, 1.40, 1.05),
    ("met_aphrodite_statue", "Statue_Aphrodite", 10.5, 5.2, -150.0, 1.40, 1.05),
]
for slug, name, sx, sy, rot, ped_h, sc_f in transept_statues:
    place_pedestal_and_statue(slug, name, sx, sy, 0.0, rot_z_deg=rot, ped_h=ped_h, statue_scale=sc_f)


# --- 3. INSTALL DISTINCT ARCHITECTURAL SCANS & EXHIBITS IN EACH NATIONAL COURT ---

# COURT 1: Sponza Classical Atrium & Fine Arts Arcade (Flanking Central Nave Side Aisles)
place_scan("arch_sponza_atrium", "FineArts_Sponza_Arcade_West", (-26.0, -21.5, 0.0), rot_z_deg=0.0, scale=0.72)
place_scan("arch_sponza_atrium", "FineArts_Sponza_Arcade_East", (26.0, 21.5, 0.0), rot_z_deg=180.0, scale=0.72)
place_scan("arch_classical_museum_hall", "FineArts_Classical_Hall_West", (-38.0, 22.5, 0.0), rot_z_deg=180.0, scale=0.65, override_mat=mat_marble)
place_scan("arch_dome_scanned", "Zollverein_Octagonal_Dome_Scan", (22.0, -17.5, 0.0), rot_z_deg=0.0, scale=0.85)

# COURT 2: Pugin's Mediaeval Court (West-South Nave, X = -18m .. -34m, Y = -4m .. -16m)
place_scan("arch_gothic_church_doorway", "Pugin_Gothic_Arch_Portal_1", (-18.5, -10.5, 0.0), rot_z_deg=0.0, scale=1.10)
place_scan("arch_gothic_church_doorway", "Pugin_Gothic_Arch_Portal_2", (-24.5, -10.5, 0.0), rot_z_deg=0.0, scale=1.10)
place_scan("arch_large_gothic_window", "Pugin_Gothic_Window_Screen", (-21.5, -14.2, 0.0), rot_z_deg=0.0, scale=1.05)
place_scan("met_gothic_tomb_ermengol", "Pugin_Gothic_Canopy_Tomb", (-16.8, -8.5, 0.0), rot_z_deg=25.0, scale=1.00)
place_pedestal_and_statue("met_medieval_pieta", "Pugin_Medieval_Pieta", -20.2, -7.2, 0.0, rot_z_deg=15.0, ped_h=1.10, statue_scale=1.0)
place_pedestal_and_statue("ph_gothic_statue", "Pugin_Gothic_Saint_Statue", -23.4, -7.2, 0.0, rot_z_deg=-15.0, ped_h=1.15, statue_scale=1.0)
place_scan("ph_gothic_cabinet", "Pugin_Oak_Arched_Cabinet", (-19.0, -12.2, 0.0), rot_z_deg=0.0, scale=1.10)
place_scan("ph_gothic_commode", "Pugin_Carved_Commode", (-22.0, -12.2, 0.0), rot_z_deg=0.0, scale=1.15)
place_scan("ph_gothic_table", "Pugin_Octagonal_Table", (-20.5, -9.5, 0.0), rot_z_deg=30.0, scale=1.20)
place_scan("ph_large_castle_door", "Pugin_Oak_Iron_Portal", (-26.5, -12.5, 0.0), rot_z_deg=0.0, scale=1.05)
place_scan("ph_chandelier_01", "Pugin_Brass_Corona_Chandelier_1", (-19.5, -8.8, 5.20), rot_z_deg=0.0, scale=1.25)
place_scan("ph_chandelier_03", "Pugin_Brass_Corona_Chandelier_2", (-23.5, -8.8, 5.20), rot_z_deg=45.0, scale=1.25)
place_scan("ph_brass_candleholders", "Pugin_Altar_Candlesticks", (-20.5, -9.5, 0.95), rot_z_deg=0.0, scale=1.0)

# COURT 3: United Kingdom Machinery in Motion, Locomotives, Carriages & Maritime (West Nave, X = -14m .. -48m, Y = -4m .. +15m)
place_scan("exh_green_locomotive", "UK_ClassV_Steam_Locomotive_1", (-19.5, 5.2, 0.0), rot_z_deg=-75.0, scale=1.08)
place_scan("exh_green_locomotive", "UK_ClassV_Steam_Locomotive_2", (-32.0, 5.8, 0.0), rot_z_deg=-82.0, scale=1.05)
place_scan("ph_drill_press", "UK_ClassVI_Whitworth_DrillPress_1", (-15.5, 4.2, 0.0), rot_z_deg=-35.0, scale=1.25)
place_scan("ph_drill_press", "UK_ClassVI_Whitworth_DrillPress_2", (-24.0, 4.5, 0.0), rot_z_deg=-45.0, scale=1.25)
place_scan("exh_sewing_machine", "UK_ClassVI_Textile_Machine", (-17.2, 8.2, 0.90), rot_z_deg=-90.0, scale=1.15)
place_scan("ph_cannon_01", "UK_ClassVIII_RoyalArsenal_Cannon_1", (-14.2, -4.6, 0.0), rot_z_deg=40.0, scale=1.20)
place_scan("ph_cannon_01", "UK_ClassVIII_RoyalArsenal_Cannon_2", (-27.5, -4.8, 0.0), rot_z_deg=35.0, scale=1.20)
place_pedestal_and_statue("ph_dutch_ship", "UK_ClassVIII_Admiralty_ShipModel", -22.0, -3.5, 0.0, rot_z_deg=75.0, ped_h=0.85, ped_w=1.80, statue_scale=0.95)
place_pedestal_and_statue("ph_lion_head", "UK_Sculpture_Lion", -12.5, -4.2, 0.0, rot_z_deg=45.0, ped_h=1.20, statue_scale=1.0)
place_pedestal_and_statue("ph_bull_head", "UK_Sculpture_Bull", -12.5, 4.2, 0.0, rot_z_deg=-45.0, ped_h=1.20, statue_scale=1.0)
place_scan("exh_display_case", "UK_Sheffield_Cutlery_Vitrine_1", (-16.0, -8.2, 0.0), rot_z_deg=0.0, scale=1.10)
place_scan("exh_display_case", "UK_Birmingham_Brass_Vitrine_2", (-28.5, 8.2, 0.0), rot_z_deg=180.0, scale=1.10)

# COURT 4: France, Austria, Zollverein, Russia & China Courts (East Nave, X = +12m .. +48m)
# French Gobelins & Sevres Court (X = +14m .. +26m, Y = -4m .. -14m)
place_scan("met_cloisters_arch", "France_Court_Stone_Arcade", (16.5, -10.5, 0.0), rot_z_deg=0.0, scale=1.25)
place_scan("ph_sofa_01", "France_Beauvais_Tapestry_Sofa", (15.5, -7.8, 0.0), rot_z_deg=20.0, scale=1.25)
place_scan("ph_armchair_01", "France_Gilded_Armchair_1", (13.8, -7.2, 0.0), rot_z_deg=45.0, scale=1.20)
place_scan("ph_armchair_01", "France_Gilded_Armchair_2", (17.2, -7.2, 0.0), rot_z_deg=-25.0, scale=1.20)
place_scan("ph_classic_console", "France_Sevres_Console_Table", (15.5, -9.6, 0.0), rot_z_deg=0.0, scale=1.25)
place_scan("ph_mantel_clock", "France_Ormolu_Mantel_Clock", (15.5, -9.6, 1.10), rot_z_deg=0.0, scale=0.95)
place_scan("ph_ceramic_vase_01", "France_Sevres_Porcelain_Urn_1", (14.2, -9.4, 0.80), rot_z_deg=0.0, scale=1.15)
place_scan("ph_brass_vase_01", "France_Sevres_Gilt_Urn_2", (16.8, -9.4, 0.80), rot_z_deg=0.0, scale=1.15)
place_scan("ph_picture_frame_02", "France_Salon_Painting_1", (14.5, -11.2, 1.80), rot_z_deg=0.0, scale=1.25)
place_scan("ph_picture_frame_01", "France_Salon_Painting_2", (17.5, -11.2, 1.80), rot_z_deg=0.0, scale=1.25)
place_scan("ph_chandelier_02", "France_Baccarat_Crystal_Chandelier", (15.5, -7.5, 5.20), rot_z_deg=0.0, scale=1.35)
place_pedestal_and_statue("met_woman_statue", "France_Marble_Sculpture", 13.0, -4.5, 0.0, rot_z_deg=35.0, ped_h=1.25, statue_scale=1.0)
place_pedestal_and_statue("met_marble_female_figure", "Austria_Milanese_Sculpture", 19.5, -4.5, 0.0, rot_z_deg=25.0, ped_h=1.25, statue_scale=1.0)

# Russian Imperial Malachite & Bronze Court + Chinese Pavilion Court (X = +14m .. +34m, Y = +4m .. +15m)
place_scan("met_islamic_niche", "Russia_Malachite_Portal_Arch", (18.0, 10.8, 0.0), rot_z_deg=180.0, scale=1.25)
place_pedestal_and_statue("stanford_dragon", "Russia_Demidoff_Malachite_Centerpiece", 18.0, 6.8, 0.0, rot_z_deg=-150.0, ped_h=1.25, statue_scale=1.10)
place_pedestal_and_statue("met_bronze_boy", "Russia_StPetersburg_Bronze", 15.2, 5.2, 0.0, rot_z_deg=-135.0, ped_h=1.20, statue_scale=1.05)
place_pedestal_and_statue("ph_brass_vase_03", "Russia_Gilt_Amphora_Left", 16.4, 9.2, 0.0, rot_z_deg=180.0, ped_h=1.15, statue_scale=1.30)
place_pedestal_and_statue("ph_brass_vase_01", "Russia_Gilt_Amphora_Right", 19.6, 9.2, 0.0, rot_z_deg=180.0, ped_h=1.15, statue_scale=1.30)

# Chinese & East India Company Court (X = +24m .. +36m, Y = +4m .. +14m)
place_scan("arch_chinese_pavilion", "China_Carved_Pagoda_Pavilion", (26.5, 9.5, 0.0), rot_z_deg=180.0, scale=0.92)
place_scan("ph_chinese_screen", "China_Lacquer_Folding_Screen", (23.5, 10.2, 0.0), rot_z_deg=165.0, scale=1.15)
place_scan("met_morning_glories_screen", "China_Painted_Silk_Screen", (29.5, 10.2, 0.0), rot_z_deg=-165.0, scale=1.10)
place_scan("ph_chinese_table", "China_Rosewood_Altar_Table", (26.5, 6.8, 0.0), rot_z_deg=180.0, scale=1.20)
place_scan("ph_chinese_armchair", "China_Carved_Armchair_1", (24.8, 6.5, 0.0), rot_z_deg=155.0, scale=1.15)
place_scan("ph_chinese_armchair", "China_Carved_Armchair_2", (28.2, 6.5, 0.0), rot_z_deg=-155.0, scale=1.15)
place_scan("ph_chinese_chandelier", "China_Palace_Lantern", (26.5, 7.2, 4.80), rot_z_deg=0.0, scale=1.25)
place_pedestal_and_statue("met_standing_buddha", "India_Gilt_Buddha_Monument", 22.5, 4.8, 0.0, rot_z_deg=-140.0, ped_h=1.20, statue_scale=1.0)
place_pedestal_and_statue("ph_carved_elephant", "India_Howdah_Carved_Elephant", 30.2, 4.8, 0.0, rot_z_deg=-125.0, ped_h=1.15, statue_scale=1.25)

# Egyptian & Ancient Architecture Court (X = +28m .. +38m, Y = -4m .. -14m)
place_scan("met_temple_of_dendur", "Egypt_Temple_Sanctuary_Scan", (31.0, -9.8, 0.0), rot_z_deg=0.0, scale=0.95)
place_pedestal_and_statue("met_lion_sarcophagus", "Rome_Marble_Lion_Sarcophagus", 25.5, -5.2, 0.0, rot_z_deg=20.0, ped_h=0.85, statue_scale=1.10)
place_pedestal_and_statue("met_sphinx_capital", "Egypt_Sphinx_Marble_Capital", 28.5, -4.8, 0.0, rot_z_deg=15.0, ped_h=1.15, statue_scale=1.05)

# COURT 5: United States & Class X Philosophical / Astronomical Instruments Court (East Nave, X = +32m .. +48m)
place_pedestal_and_statue("statue_classical_woman", "US_Powers_Greek_Slave_Statue", 36.0, 0.0, 0.0, rot_z_deg=-90.0, ped_h=1.35, statue_scale=1.05)
place_pedestal_and_statue("met_standing_horse", "US_Carved_American_Horse", 39.5, -4.8, 0.0, rot_z_deg=35.0, ped_h=1.15, statue_scale=1.05)
place_pedestal_and_statue("stanford_lucy_statue", "US_Colossal_Winged_Victory", 42.5, 4.8, 0.0, rot_z_deg=-145.0, ped_h=1.30, statue_scale=1.05)
place_scan("exh_standing_globe", "ClassX_Terrestrial_Globe_1", (34.2, -3.5, 0.0), rot_z_deg=30.0, scale=1.25)
place_scan("exh_standing_globe", "ClassX_Celestial_Globe_2", (34.2, 3.5, 0.0), rot_z_deg=-30.0, scale=1.25)
place_scan("threejs_steampunk_camera", "ClassX_Daguerreotype_Apparatus", (37.8, 3.8, 0.90), rot_z_deg=-135.0, scale=1.10)
place_scan("ph_vintage_microscope", "ClassX_Ross_Achromatic_Microscope", (35.5, -5.8, 0.95), rot_z_deg=45.0, scale=1.20)
place_scan("ph_camera_01", "ClassX_MathewBrady_Camera", (38.2, -5.8, 0.0), rot_z_deg=35.0, scale=1.20)
place_scan("exh_display_case", "ClassX_Precision_Chronometers_Case", (41.0, -7.8, 0.0), rot_z_deg=0.0, scale=1.15)

# Ross Great Equatorial Refracting Telescope at X = +33.0m, Y = +1.8m
bm_tel = bmesh.new()
bmesh.ops.create_cone(bm_tel, cap_ends=True, segments=16, radius1=0.75, radius2=0.45, depth=2.3, matrix=Matrix.Translation((33.0, 1.8, 1.15)))
m_tube = (
    Matrix.Translation((33.0, 1.8, 2.55))
    @ Matrix.Rotation(math.radians(34.0), 4, "Y")
    @ Matrix.Rotation(math.radians(-25.0), 4, "Z")
    @ Matrix.Scale(0.24, 4, (1, 0, 0))
    @ Matrix.Scale(0.24, 4, (0, 1, 0))
    @ Matrix.Scale(4.2, 4, (0, 0, 1))
)
bmesh.ops.create_cone(bm_tel, cap_ends=True, segments=16, radius1=1.0, radius2=0.82, depth=1.0, matrix=m_tube)
commit_bm(bm_tel, "ClassX_Ross_Equatorial_Telescope", mat_yellow)

# First Gallery Portrait Busts & Glass Vitrines (Z = 7.32m along North & South Galleries outside Transept)
gallery_busts = [
    "ph_marble_bust_01",
    "stanford_igea_bust",
    "stanford_bimba_bust",
    "stanford_nefertiti_bust",
    "stanford_happy_buddha",
    "met_seated_court_lady",
]
for g_i, gx in enumerate(range(-42, 48, 12)):
    if abs(gx) < 12:
        continue
    for gy, g_rot in [(-12.2, 0.0), (12.2, 180.0)]:
        b_slug = gallery_busts[(g_i + (0 if gy < 0 else 3)) % len(gallery_busts)]
        place_pedestal_and_statue(b_slug, f"GalBust_{gx}_{gy}", float(gx), gy, 7.32, rot_z_deg=g_rot, ped_h=1.10, ped_w=0.75, statue_scale=0.95)
        place_scan("exh_display_case", f"GalVitrine_{gx}_{gy}", (float(gx + 4.0), gy - (2.2 if gy < 0 else -2.2), 7.32), rot_z_deg=g_rot, scale=1.0)


# --- 4. POPULATE PROMENADES, COURTS, GALLERIES & EXTERIOR WITH REAL 3D SCANNED HUMANS ---
STANDING_HUMANS = [
    "human_scan_standing_man_01",
    "human_scan_woman_jacket",
    "human_gentleman_coat_hat",
    "human_female02",
    "human_male02",
    "human_old_gentleman",
    "human_man_suit_01",
    "human_man_suit_02",
    "human_man_walking_02",
    "human_woman_coat_01",
    "human_woman_walking_01",
    "human_woman_walking_02",
    "human_man_standing_03",
    "human_woman_standing_03",
]

SEATED_HUMANS = [
    "human_scan_seated_man_02",
    "human_scan_seated_boy_hat",
    "human_scan_cs_sitting_cute_kawaii_gi",
    "human_scan_cs_sitting_survivor_girl",
]

visitor_idx = 0

# A. Conversational groups & promenading visitors around the Transept & Central Nave
for gx in [i * 2.8 for i in range(-22, 23)]:
    for lane_idx, base_y in enumerate([-7.2, -3.4, -1.4, 1.4, 3.4, 7.2]):
        if abs(gx) < 6.2 and abs(base_y) < 5.8:
            continue
        vy = base_y + 0.55 * math.sin(gx * 0.7 + lane_idx * 1.9)
        vx = gx + 0.35 * math.cos(base_y * 1.1 + visitor_idx)
        h_slug = STANDING_HUMANS[visitor_idx % len(STANDING_HUMANS)]
        # Face toward exhibits, fountain, or along the promenade
        if abs(vx) < 9.0 and abs(vy) < 9.0:
            rot_deg = math.degrees(math.atan2(-vy, -vx)) - 90.0
        else:
            rot_deg = (90.0 if (visitor_idx % 2 == 0) else -90.0) + 25.0 * math.sin(visitor_idx * 1.7)
        sc_var = 0.94 + (visitor_idx % 7) * 0.018
        place_scan(h_slug, f"Visitor_Nave_{visitor_idx:03d}", (vx, vy, 0.0), rot_z_deg=rot_deg, scale=sc_var)
        visitor_idx += 1

# B. Seated visitors on the Victorian benches around the Crystal Fountain
for b_i, ang_deg in enumerate((30, 150, 210, 330)):
    rad = math.radians(ang_deg)
    bx, by = 6.75 * math.cos(rad), 6.75 * math.sin(rad)
    s_slug = SEATED_HUMANS[b_i % len(SEATED_HUMANS)]
    place_scan(s_slug, f"Visitor_BenchSeated_{b_i}", (bx, by, 0.05), rot_z_deg=ang_deg + 90.0, scale=1.0)

# C. Visitors inside the National Courts (Pugin Mediaeval, UK Machinery, France, Russia, China, US)
court_visitors = [
    (-20.5, -6.2, 180.0), (-22.2, -6.8, 165.0), (-18.2, -7.0, 195.0), (-21.0, -10.8, 15.0),
    (-17.5, 2.8, 0.0), (-21.0, 2.6, 20.0), (-25.5, 3.0, -15.0), (-30.0, 3.2, 10.0),
    (15.0, -5.8, 180.0), (16.5, -6.2, 160.0), (18.2, -5.5, 200.0),
    (17.5, 4.5, 0.0), (19.0, 4.8, -20.0), (25.5, 5.2, 15.0), (27.2, 5.5, -15.0),
    (34.5, -1.8, -45.0), (35.2, 1.8, -135.0), (38.0, 0.5, 90.0),
]
for cx, cy, crot in court_visitors:
    h_slug = STANDING_HUMANS[visitor_idx % len(STANDING_HUMANS)]
    place_scan(h_slug, f"Visitor_Court_{visitor_idx:03d}", (cx, cy, 0.0), rot_z_deg=crot, scale=0.96 + (visitor_idx % 5) * 0.02)
    visitor_idx += 1

# D. Visitors along the First Gallery Balustrades (Z = 7.32m) looking down into the Nave & Transept
for gx in range(-44, 48, 6):
    if abs(gx) < 12:
        continue
    for gy, grot in [(-11.8, 0.0), (11.8, 180.0)]:
        h_slug = STANDING_HUMANS[visitor_idx % len(STANDING_HUMANS)]
        place_scan(h_slug, f"Visitor_Gallery_{visitor_idx:03d}", (float(gx), gy, 7.32), rot_z_deg=grot, scale=0.97)
        visitor_idx += 1

# E. Exterior Rotten Row Promenade Visitors & Trees in Hyde Park (Y = -42m .. -62m)
for ex in range(-65, 70, 9):
    h_slug = STANDING_HUMANS[visitor_idx % len(STANDING_HUMANS)]
    place_scan(h_slug, f"Visitor_HydePark_{visitor_idx:03d}", (float(ex), -46.0 + (ex % 5), 0.0), rot_z_deg=90.0 if ex % 2 == 0 else -45.0, scale=1.0)
    visitor_idx += 1
for park_x in (-75.0, -45.0, 45.0, 75.0):
    place_scan("ph_island_tree_02", f"HydePark_ExteriorTree_{park_x}", (park_x, -58.0, 0.0), rot_z_deg=park_x, scale=0.85)


# --- 5. LIGHTING: 1K POLY HAVEN HDRI + 11 OCT 1851 14:00 GMT EPHEMERIS SUN + INTERIOR FILL ---
world = bpy.data.worlds.new("CrystalWorld_1851_HDRI")
sc.world = world
world.use_nodes = True
if hasattr(world, "cycles"):
    world.cycles.sampling_method = "NONE"
w_nt = world.node_tree
w_nodes = w_nt.nodes
w_links = w_nt.links
w_nodes.clear()

w_out = w_nodes.new("ShaderNodeOutputWorld")
w_bg = w_nodes.new("ShaderNodeBackground")
w_bg.inputs["Strength"].default_value = 2.6

hdri_path = os.path.join(HDRI_DIR, "kloppenheim_06_puresky_1k.hdr")
if os.path.exists(hdri_path):
    w_env = w_nodes.new("ShaderNodeTexEnvironment")
    w_env.image = bpy.data.images.load(hdri_path, check_existing=True)
    w_links.new(w_env.outputs["Color"], w_bg.inputs["Color"])
else:
    w_bg.inputs["Color"].default_value = (0.78, 0.86, 0.98, 1.0)
w_links.new(w_bg.outputs["Background"], w_out.inputs["Surface"])

# Ephemeris Sun (11 Oct 1851 14:00 GMT: Azimuth 216.8039 deg, Altitude 25.0150 deg)
sun_d = bpy.data.lights.new("Sun_18511011_1400GMT", type="SUN")
sun_d.energy = 4.2
sun_d.color = (1.0, 0.96, 0.88)
sun_d.angle = math.radians(1.2)
sun_o = bpy.data.objects.new("Sun_18511011_1400GMT", sun_d)
sun_o.rotation_euler = (math.radians(90.0 - 25.0150), 0.0, math.radians(216.8039 - 180.0))
sc.collection.objects.link(sun_o)

# Soft overhead glasshouse fill lights (3 efficient high-span portals + Sponza atrium skylight)
for lx, ly, lz in [(-24.0, 0.0, 15.5), (0.0, 0.0, 15.5), (24.0, 0.0, 15.5), (-26.0, -21.5, 7.2)]:
    ld = bpy.data.lights.new(f"Glasshouse_Skylight_{lx}_{ly}", type="AREA")
    ld.energy = 12000.0 if ly == 0.0 else 4500.0
    ld.size = 22.0 if ly == 0.0 else 8.0
    ld.color = (1.0, 0.98, 0.94)
    lo = bpy.data.objects.new(f"Glasshouse_Skylight_{lx}_{ly}", ld)
    lo.location = (lx, ly, lz)
    sc.collection.objects.link(lo)


# --- 6. CAMERA HELPER & 16 DISTINCT MASTER VIEWS ---
cam_d = bpy.data.cameras.new("MasterCam")
cam_d.clip_start = 0.10
cam_d.clip_end = 600.0
cam_o = bpy.data.objects.new("MasterCam", cam_d)
sc.collection.objects.link(cam_o)
sc.camera = cam_o


def aim_camera(loc, target, lens_mm=28.0):
    cam_d.lens = lens_mm
    cam_o.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_o.rotation_euler = rot_quat.to_euler()


out_dir = os.path.join(CRYSTAL_DIR, "build", "cycles_masters")
os.makedirs(out_dir, exist_ok=True)
sc.render.image_settings.file_format = "JPEG"
sc.render.image_settings.quality = 94

master_views = [
    ("M01_transept_crossing", (-11.5, -15.5, 3.2), (0.0, 2.5, 5.2), 24.0, 1280, 720),
    ("M02_nave_looking_west", (16.5, -1.8, 2.6), (-36.0, 0.5, 4.2), 26.0, 1280, 720),
    ("M03_nave_looking_east", (-16.5, 1.8, 2.6), (36.0, -0.5, 4.2), 26.0, 1280, 720),
    ("M04_fountain_closeup", (-4.8, -5.2, 2.0), (0.0, 0.0, 2.5), 32.0, 1280, 720),
    ("M05_great_organ_north", (-4.5, 3.5, 4.5), (0.0, 21.5, 10.2), 28.0, 1280, 720),
    ("M06_three_elms_vault", (7.8, -9.5, 3.8), (-1.5, 14.5, 14.0), 22.0, 1280, 720),
    ("M07_first_gallery_view", (-24.5, -13.2, 9.1), (10.0, 2.0, 4.8), 26.0, 1280, 720),
    ("M08_british_court_west", (-11.5, 1.2, 2.2), (-25.0, 5.0, 2.2), 28.0, 1280, 720),
    ("M09_foreign_court_east", (11.5, -1.2, 2.2), (25.5, 7.5, 2.8), 28.0, 1280, 720),
    ("M10_roof_gutter_vault", (-9.5, -3.5, 15.2), (16.0, 2.0, 22.0), 24.0, 1280, 720),
    ("M11_walk_eye_level", (-7.8, 0.0, 1.65), (22.0, 0.0, 2.2), 32.0, 1280, 720),
    ("M12_exterior_oblique", (-72.0, -78.0, 15.0), (0.0, 0.0, 10.5), 28.0, 1280, 720),
    ("M13_pugin_mediaeval_court", (-13.5, -4.5, 2.1), (-21.5, -10.0, 2.6), 30.0, 1280, 720),
    ("M14_us_court_and_telescope", (27.5, -2.5, 2.1), (36.5, 1.2, 2.3), 30.0, 1280, 720),
    ("M15_crowd_promenade_closeup", (-4.8, -8.5, 1.70), (2.5, -1.0, 2.0), 38.0, 1280, 720),
    ("M16_clerestory_truss_lookup", (-20.0, 0.0, 2.4), (5.0, 0.0, 19.5), 24.0, 1280, 720),
    ("M17_french_gobelins_court", (11.5, -4.2, 1.95), (16.2, -9.2, 2.0), 30.0, 1280, 720),
    ("M18_russian_malachite_court", (12.8, 2.5, 1.95), (18.0, 8.2, 2.2), 30.0, 1280, 720),
    ("M19_egyptian_dendur_court", (27.2, -3.2, 2.30), (31.0, -9.8, 3.2), 28.0, 1280, 720),
    ("M20_maritime_ship_and_cannon", (-16.8, -1.2, 1.90), (-23.0, -3.8, 1.8), 32.0, 1280, 720),
    ("M21_locomotive_closeup", (-14.5, 2.2, 1.85), (-20.5, 5.5, 2.0), 34.0, 1280, 720),
    ("M22_sponza_fine_arts_arcade", (-34.5, -8.8, 2.50), (-14.0, -7.2, 2.8), 28.0, 1280, 720),
    ("M23_south_transept_gates", (0.0, -29.5, 2.20), (0.0, 0.0, 4.5), 26.0, 1280, 720),
    ("M24_organ_loft_piano_closeup", (-3.5, 14.8, 9.10), (0.5, 21.0, 9.8), 28.0, 1280, 720),
    ("M25_pugin_chandeliers_and_tomb", (-20.5, -4.2, 2.15), (-20.5, -11.5, 2.4), 28.0, 1280, 720),
    ("M26_chinese_pagoda_closeup", (20.5, 3.2, 2.00), (26.8, 8.8, 3.0), 30.0, 1280, 720),
    ("M27_indian_elephant_and_east_nave", (25.0, 0.8, 1.95), (31.0, 5.2, 2.2), 32.0, 1280, 720),
    ("M28_scientific_instruments_vitrine", (30.5, -1.5, 1.90), (36.5, -4.5, 1.8), 32.0, 1280, 720),
    ("M29_north_gallery_busts_promenade", (-28.0, 13.0, 9.00), (15.0, 8.0, 6.5), 28.0, 1280, 720),
    ("M30_rotten_row_carriage_drive", (-38.0, -52.0, 2.40), (8.0, 0.0, 11.0), 28.0, 1280, 720),
]

only_filter = os.environ.get("ONLY_VIEWS", "").strip()
only_set = set(only_filter.split(",")) if only_filter else set()

for vname, loc, tgt, lens, rx, ry in master_views:
    if only_set and vname not in only_set:
        continue
    sc.render.resolution_x = rx
    sc.render.resolution_y = ry
    sc.render.resolution_percentage = 100
    aim_camera(loc, tgt, lens)
    out_p = os.path.join(out_dir, f"{vname}.jpg")
    sc.render.filepath = out_p
    bpy.ops.render.render(write_still=True)
    print(f"Rendered 3D Scan Cycles master view: {out_p} ({os.path.getsize(out_p)} bytes)", flush=True)
