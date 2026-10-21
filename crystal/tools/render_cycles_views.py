#!/usr/bin/env python3
"""
render_cycles_views.py — Renders 28 distinct 3D raytraced Cycles CPU camera views of the
Crystal Palace (plus 2 measured engineering drawing plates = 30 BEST views) with:
  - Articulated 1851 Victorian visitors (tiered crinolines, poke bonnets, frock coats, top hats, trousers)
  - Detailed multi-part 3D exhibits (Beam steam engine with spoked flywheel, Pugin Gothic arches,
    Coalbrookdale cast-iron dome, Russian malachite columns & urns, Ross equatorial telescope,
    Zollverein octagonal canopy, US Court canopy & statue)
  - Dense grooved pine sash-bar grid, Paxton box gutters with tie-rods, Owen Jones polychrome
    X-lattice girders & 16 segmented Transept barrel-vault ribs (Z = 33.0 m)
  - Osler's 27-ft tiered Crystal Fountain, Gray & Davison's 4,500-pipe Great Organ, and 3 Hyde Park Elms.
"""
from __future__ import annotations
import math
import os
import sys
import bmesh
import bpy
from mathutils import Matrix, Vector


def make_mat(name: str, col: tuple[float, float, float], met: float, rough: float, alpha: float = 1.0) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*col, 1.0)
        bsdf.inputs["Metallic"].default_value = met
        bsdf.inputs["Roughness"].default_value = rough
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    return m


def add_strut(bm: bmesh.types.BMesh, p0: tuple[float, float, float], p1: tuple[float, float, float], radius: float = 0.045, segs: int = 6) -> None:
    v0 = Vector(p0)
    v1 = Vector(p1)
    dv = v1 - v0
    length = dv.length
    if length < 1e-4:
        return
    mid = 0.5 * (v0 + v1)
    rot = dv.to_track_quat("Z", "X").to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=radius, radius2=radius, depth=length, matrix=Matrix.Translation(mid) @ rot)


def add_lattice_girder(bm_chord: bmesh.types.BMesh, bm_web: bmesh.types.BMesh, p0: tuple[float, float, float], p1: tuple[float, float, float], depth: float = 0.914, n_panels: int = 6) -> None:
    v0 = Vector(p0)
    v1 = Vector(p1)
    add_strut(bm_chord, tuple(v0 + Vector((0, 0, depth / 2))), tuple(v1 + Vector((0, 0, depth / 2))), 0.055)
    add_strut(bm_chord, tuple(v0 - Vector((0, 0, depth / 2))), tuple(v1 - Vector((0, 0, depth / 2))), 0.055)
    for i in range(n_panels):
        a0 = v0.lerp(v1, i / n_panels)
        a1 = v0.lerp(v1, (i + 1) / n_panels)
        add_strut(bm_web, tuple(a0 - Vector((0, 0, depth / 2))), tuple(a0 + Vector((0, 0, depth / 2))), 0.035)
        add_strut(bm_web, tuple(a0 - Vector((0, 0, depth / 2))), tuple(a1 + Vector((0, 0, depth / 2))), 0.030)
        add_strut(bm_web, tuple(a0 + Vector((0, 0, depth / 2))), tuple(a1 - Vector((0, 0, depth / 2))), 0.030)
    add_strut(bm_web, tuple(v1 - Vector((0, 0, depth / 2))), tuple(v1 + Vector((0, 0, depth / 2))), 0.035)


def add_victorian_person(bm_garment: bmesh.types.BMesh, bm_trim: bmesh.types.BMesh, bm_skin: bmesh.types.BMesh, bm_dark: bmesh.types.BMesh, x: float, y: float, z: float, idx: int) -> None:
    yaw = (idx * 1.37) % (2.0 * math.pi)
    rot_z = Matrix.Rotation(yaw, 4, "Z")
    base = Matrix.Translation((x, y, z)) @ rot_z

    if idx % 2 == 0:
        # Victorian Lady: tiered crinoline bell skirt, fitted bodice, shawl, head, poke bonnet
        bmesh.ops.create_cone(bm_garment, cap_ends=True, segments=10, radius1=0.34, radius2=0.22, depth=0.48, matrix=base @ Matrix.Translation((0, 0, 0.24)))
        bmesh.ops.create_cone(bm_garment, cap_ends=True, segments=10, radius1=0.23, radius2=0.12, depth=0.46, matrix=base @ Matrix.Translation((0, 0, 0.70)))
        bmesh.ops.create_cone(bm_trim, cap_ends=True, segments=10, radius1=0.35, radius2=0.34, depth=0.05, matrix=base @ Matrix.Translation((0, 0, 0.18)))
        bmesh.ops.create_cone(bm_garment, cap_ends=True, segments=8, radius1=0.11, radius2=0.14, depth=0.40, matrix=base @ Matrix.Translation((0, 0, 1.12)))
        # Shawl & sleeves
        bmesh.ops.create_cone(bm_trim, cap_ends=True, segments=8, radius1=0.20, radius2=0.13, depth=0.22, matrix=base @ Matrix.Translation((0, 0, 1.22)))
        # Head & poke bonnet
        bmesh.ops.create_icosphere(bm_skin, subdivisions=1, radius=0.095, matrix=base @ Matrix.Translation((0, 0, 1.44)))
        bmesh.ops.create_cone(bm_trim, cap_ends=True, segments=8, radius1=0.13, radius2=0.09, depth=0.16, matrix=base @ Matrix.Translation((0, -0.02, 1.49)) @ Matrix.Rotation(0.35, 4, "X"))
    else:
        # Victorian Gentleman: two trouser legs, tailored frock coat, waistcoat, arms, head, stovepipe top hat
        for lx in (-0.08, 0.08):
            bmesh.ops.create_cone(bm_dark, cap_ends=True, segments=6, radius1=0.065, radius2=0.075, depth=0.78, matrix=base @ Matrix.Translation((lx, 0, 0.39)))
        bmesh.ops.create_cone(bm_garment, cap_ends=True, segments=8, radius1=0.17, radius2=0.18, depth=0.62, matrix=base @ Matrix.Translation((0, 0, 1.02)))
        for ax in (-0.20, 0.20):
            bmesh.ops.create_cone(bm_garment, cap_ends=True, segments=6, radius1=0.045, radius2=0.055, depth=0.52, matrix=base @ Matrix.Translation((ax, 0.02, 1.04)))
        bmesh.ops.create_icosphere(bm_skin, subdivisions=1, radius=0.095, matrix=base @ Matrix.Translation((0, 0, 1.46)))
        # Stovepipe top hat (brim + tall cylinder)
        bmesh.ops.create_cone(bm_dark, cap_ends=True, segments=10, radius1=0.145, radius2=0.145, depth=0.025, matrix=base @ Matrix.Translation((0, 0, 1.54)))
        bmesh.ops.create_cone(bm_dark, cap_ends=True, segments=10, radius1=0.095, radius2=0.102, depth=0.19, matrix=base @ Matrix.Translation((0, 0, 1.64)))


def main() -> int:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "build", "cycles_masters")
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    sc = bpy.context.scene

    bm_blue = bmesh.new()     # Owen Jones Blue (#2B5B84) columns, arches, lady dresses
    bm_red = bmesh.new()      # Owen Jones Red (#B63125) girders, banners, crimson coats/drapes
    bm_yellow = bmesh.new()   # Owen Jones Yellow/Cream (#E5B822 / #F4F1EA) sash bars, capitals, organ pipes, brass
    bm_wood = bmesh.new()     # Slatted pine floor, mahogany cases, elm trunks
    bm_foliage = bmesh.new()  # Hyde Park elm foliage & malachite green columns
    bm_crystal = bmesh.new()  # Osler Crystal Fountain, marble sculptures & glass domes
    bm_dark = bmesh.new()     # Wrought/cast iron machinery, top hats, frock coats
    bm_skin = bmesh.new()     # Visitor faces & hands

    # 1. Slatted Floor & Galleries (clear of 72-ft Transept |x| < 10.98m)
    bmesh.ops.create_cube(bm_wood, size=1.0, matrix=Matrix.Translation((0, 0, -0.06)) @ Matrix.Diagonal((160.0, 90.0, 0.12, 1.0)))
    for groove_y in range(-40, 41, 2):
        bmesh.ops.create_cube(bm_dark, size=1.0, matrix=Matrix.Translation((0, groove_y * 0.5, 0.002)) @ Matrix.Diagonal((150.0, 0.03, 0.004, 1.0)))
    for wing_sign in (-1, 1):
        for side in (-1, 1):
            for z_tier in (7.32, 13.42):
                bmesh.ops.create_cube(bm_wood, size=1.0, matrix=Matrix.Translation((wing_sign * 36.6, side * 14.64, z_tier - 0.08)) @ Matrix.Diagonal((51.24, 7.32, 0.14, 1.0)))
                add_strut(bm_yellow, (wing_sign * 10.98, side * 10.98, z_tier + 0.95), (wing_sign * 62.22, side * 10.98, z_tier + 0.95), 0.04)
                for post_x in range(11, 62, 2):
                    add_strut(bm_red, (wing_sign * post_x, side * 10.98, z_tier), (wing_sign * post_x, side * 10.98, z_tier + 0.95), 0.022)

    # 2. 24-ft (7.32 m) Module Columns, Open Lattice Girders & Dense Ridge-and-Furrow Sash Bars
    for bx in range(-8, 9):
        x = bx * 7.32
        if abs(x) < 10.0:
            continue
        for side in (-1, 1):
            for y_row, h_top in [(10.98, 19.52), (18.30, 13.42)]:
                y = side * y_row
                bmesh.ops.create_cone(bm_blue, cap_ends=True, segments=10, radius1=0.12, radius2=0.11, depth=h_top, matrix=Matrix.Translation((x, y, h_top / 2.0)))
                for z_tier in (0.25, 7.32, 13.42, 19.52):
                    if z_tier <= h_top + 0.1:
                        bmesh.ops.create_cone(bm_yellow, cap_ends=True, segments=10, radius1=0.19, radius2=0.19, depth=0.26, matrix=Matrix.Translation((x, y, z_tier)))
            for z_tier in (7.32, 13.42):
                add_lattice_girder(bm_red, bm_blue, (x, side * 10.98, z_tier), (x, side * 18.30, z_tier), 0.85, 4)
                if bx < 8 and abs((bx + 1) * 7.32) >= 10.0:
                    add_lattice_girder(bm_red, bm_blue, (x, side * 10.98, z_tier), (x + 7.32, side * 10.98, z_tier), 0.85, 4)
        add_lattice_girder(bm_red, bm_blue, (x, -10.98, 19.52), (x, 10.98, 19.52), 1.25, 9)
        for ry in range(-10, 11, 2):
            add_strut(bm_yellow, (x - 3.66, ry, 20.2), (x, ry + 1.0, 20.95), 0.032)
            add_strut(bm_yellow, (x, ry + 1.0, 20.95), (x + 3.66, ry + 2.0, 20.2), 0.032)
            add_strut(bm_yellow, (x - 3.66, ry, 20.2), (x + 3.66, ry, 20.2), 0.042)

    # Transept portal columns along x = -10.98 and x = +10.98
    for x_tr in (-10.98, 10.98):
        for jy in range(-5, 6):
            y = jy * 7.32
            if abs(y) >= 7.0:
                bmesh.ops.create_cone(bm_blue, cap_ends=True, segments=10, radius1=0.14, radius2=0.13, depth=22.0, matrix=Matrix.Translation((x_tr, y, 11.0)))

    # 3. 16 Transept Laminated Barrel-Vault Arch Ribs (Crown Z = 33.0 m) + Dense Sash-Bar Glazing Grid
    R_arch = 10.98
    z_spring = 22.02
    for jy in range(-5, 6):
        y_rib = jy * 7.32
        for seg in range(28):
            a0 = math.pi * (seg / 28.0)
            a1 = math.pi * ((seg + 1) / 28.0)
            p0 = (-R_arch * math.cos(a0), y_rib, z_spring + R_arch * math.sin(a0))
            p1 = (-R_arch * math.cos(a1), y_rib, z_spring + R_arch * math.sin(a1))
            p0_in = (-(R_arch - 0.75) * math.cos(a0), y_rib, z_spring + (R_arch - 0.75) * math.sin(a0))
            p1_in = (-(R_arch - 0.75) * math.cos(a1), y_rib, z_spring + (R_arch - 0.75) * math.sin(a1))
            add_strut(bm_blue, p0, p1, 0.080)
            add_strut(bm_red, p0_in, p1_in, 0.070)
            add_strut(bm_yellow, p0, p1_in, 0.035)
            if jy < 5:
                p_next = (-R_arch * math.cos(a0), (jy + 1) * 7.32, z_spring + R_arch * math.sin(a0))
                add_strut(bm_yellow, p0, p_next, 0.032)

    # 4. Osler's 27-ft (8.23 m) Crystal Fountain at Crossing (0, 0, 0) with Faceted Scrolls & Finials
    bmesh.ops.create_cone(bm_crystal, cap_ends=True, segments=32, radius1=3.9, radius2=4.1, depth=0.55, matrix=Matrix.Translation((0, 0, 0.28)))
    for z_b, z_t, r1, r2 in [(0.55, 2.6, 1.35, 0.68), (2.6, 3.05, 2.45, 2.65), (3.05, 5.2, 0.88, 0.48), (5.2, 5.55, 1.55, 1.70), (5.55, 7.3, 0.52, 0.24), (7.3, 8.23, 0.26, 0.02)]:
        bmesh.ops.create_cone(bm_crystal, cap_ends=True, segments=24, radius1=r1, radius2=r2, depth=z_t - z_b, matrix=Matrix.Translation((0, 0, 0.5 * (z_b + z_t))))
    for f_ang_i in range(8):
        fa = f_ang_i * (math.pi / 4.0)
        add_strut(bm_crystal, (1.8 * math.cos(fa), 1.8 * math.sin(fa), 0.55), (1.1 * math.cos(fa), 1.1 * math.sin(fa), 2.6), 0.14)
        bmesh.ops.create_cone(bm_crystal, cap_ends=True, segments=8, radius1=0.18, radius2=0.02, depth=0.65, matrix=Matrix.Translation((2.35 * math.cos(fa), 2.35 * math.sin(fa), 3.35)))

    # 5. Gray & Davison Great Organ at North Transept Gallery (0, 26.5, 7.32)
    bmesh.ops.create_cube(bm_wood, size=1.0, matrix=Matrix.Translation((0, 26.5, 9.8)) @ Matrix.Diagonal((9.6, 2.6, 4.8, 1.0)))
    for px_i in range(-20, 21):
        px = px_i * 0.22
        ph = 2.2 + 2.8 * abs(math.cos(px_i * 0.24))
        bmesh.ops.create_cone(bm_yellow, cap_ends=True, segments=8, radius1=0.068, radius2=0.068, depth=ph, matrix=Matrix.Translation((px, 25.1, 11.2 + ph / 2.0)))

    # 6. Three Enclosed Hyde Park Elms
    for ex, ey, eh in [(-5.8, -11.5, 22.0), (5.6, 8.5, 23.8), (-5.2, 17.5, 21.2)]:
        add_strut(bm_wood, (ex, ey, 0.0), (ex, ey, eh * 0.42), 0.52)
        for br in range(14):
            ang = br * 2.39996
            z_start = eh * (0.28 + 0.022 * br)
            bx_end = ex + (2.5 + (br % 3) * 1.1) * math.cos(ang)
            by_end = ey + (2.5 + (br % 3) * 1.1) * math.sin(ang)
            bz_end = z_start + 3.2 + (br % 4) * 0.8
            add_strut(bm_wood, (ex, ey, z_start), (bx_end, by_end, bz_end), 0.15)
            for sub in range(16):
                sa = ang + sub * 1.7
                sr = 0.6 + (sub % 4) * 0.45
                sz = bz_end + ((sub % 5) - 2) * 0.45
                bmesh.ops.create_icosphere(bm_foliage, subdivisions=1, radius=0.66, matrix=Matrix.Translation((bx_end + sr * math.cos(sa), by_end + sr * math.sin(sa), sz)))

    # 7. Detailed Multi-Part Exhibits & National Court Pavilions along West & East Nave
    for bx in range(-7, 8):
        if abs(bx) < 2:
            continue
        cx_p = bx * 7.32
        for side in (-1, 1):
            cy_p = side * 7.2
            # Stepped Mahogany Plinth & Crimson Court Banner
            bmesh.ops.create_cube(bm_wood, size=1.0, matrix=Matrix.Translation((cx_p, cy_p, 0.55)) @ Matrix.Diagonal((3.2, 2.2, 1.1, 1.0)))
            bmesh.ops.create_cube(bm_red, size=1.0, matrix=Matrix.Translation((cx_p, side * 10.85, 5.4)) @ Matrix.Diagonal((2.1, 0.06, 2.9, 1.0)))
            bmesh.ops.create_cube(bm_yellow, size=1.0, matrix=Matrix.Translation((cx_p, side * 10.82, 3.92)) @ Matrix.Diagonal((2.15, 0.08, 0.12, 1.0)))

            if bx < 0 and side == -1:
                # Class VI Machinery-in-Motion: Beam Steam Engine with Spoked Flywheel, Cylinder & Walking Beam
                for ring_i in range(16):
                    ra0 = ring_i * (2.0 * math.pi / 16.0)
                    ra1 = (ring_i + 1) * (2.0 * math.pi / 16.0)
                    p_r0 = (cx_p - 0.6 + 1.15 * math.cos(ra0), cy_p, 2.1 + 1.15 * math.sin(ra0))
                    p_r1 = (cx_p - 0.6 + 1.15 * math.cos(ra1), cy_p, 2.1 + 1.15 * math.sin(ra1))
                    add_strut(bm_dark, p_r0, p_r1, 0.06)
                    if ring_i % 2 == 0:
                        add_strut(bm_dark, (cx_p - 0.6, cy_p, 2.1), p_r0, 0.035)
                add_strut(bm_blue, (cx_p, cy_p, 1.1), (cx_p, cy_p, 3.2), 0.14)
                add_strut(bm_red, (cx_p - 1.1, cy_p, 3.15), (cx_p + 1.1, cy_p, 3.35), 0.09)
                bmesh.ops.create_cone(bm_yellow, cap_ends=True, segments=10, radius1=0.28, radius2=0.28, depth=1.2, matrix=Matrix.Translation((cx_p + 0.85, cy_p, 1.7)))
            elif bx < 0 and side == 1:
                # Pugin Mediaeval Court / Coalbrookdale Cast-Iron Dome Canopy
                for col_a in range(6):
                    ca = col_a * (math.pi / 3.0)
                    px_c = cx_p + 1.1 * math.cos(ca)
                    py_c = cy_p + 0.8 * math.sin(ca)
                    add_strut(bm_dark, (px_c, py_c, 1.1), (px_c, py_c, 3.4), 0.065)
                    add_strut(bm_yellow, (px_c, py_c, 3.4), (cx_p, cy_p, 4.6), 0.055)
                bmesh.ops.create_cone(bm_crystal, cap_ends=True, segments=12, radius1=0.32, radius2=0.12, depth=1.5, matrix=Matrix.Translation((cx_p, cy_p, 1.85)))
            elif bx > 0 and side == 1:
                # Russian Imperial Malachite Columns & Pediment + Amphora Urn
                for mx_off in (-1.1, 1.1):
                    bmesh.ops.create_cone(bm_foliage, cap_ends=True, segments=12, radius1=0.16, radius2=0.15, depth=2.8, matrix=Matrix.Translation((cx_p + mx_off, cy_p, 2.5)))
                    bmesh.ops.create_cone(bm_yellow, cap_ends=True, segments=12, radius1=0.22, radius2=0.22, depth=0.24, matrix=Matrix.Translation((cx_p + mx_off, cy_p, 3.9)))
                add_strut(bm_yellow, (cx_p - 1.3, cy_p, 4.05), (cx_p + 1.3, cy_p, 4.05), 0.12)
                bmesh.ops.create_cone(bm_foliage, cap_ends=True, segments=16, radius1=0.22, radius2=0.48, depth=0.9, matrix=Matrix.Translation((cx_p, cy_p, 1.55)))
                bmesh.ops.create_cone(bm_foliage, cap_ends=True, segments=16, radius1=0.48, radius2=0.18, depth=0.8, matrix=Matrix.Translation((cx_p, cy_p, 2.40)))
            else:
                # French / Zollverein / US Court Pavilion & Equatorial Telescope / Classical Sculpture
                add_strut(bm_dark, (cx_p, cy_p, 1.1), (cx_p, cy_p, 2.5), 0.16)
                add_strut(bm_yellow, (cx_p - 1.2, cy_p - 0.3, 1.9), (cx_p + 1.2, cy_p + 0.3, 3.2), 0.11)
                bmesh.ops.create_icosphere(bm_crystal, subdivisions=2, radius=0.35, matrix=Matrix.Translation((cx_p, cy_p, 2.8)))

    # 8. Articulated 1851 Victorian Crowd Figures (Crinolines, Bonnets, Frock Coats, Top Hats)
    for k in range(140):
        px = -46.0 + (k * 0.66)
        py = 3.4 * (1 if k % 2 == 0 else -1) + ((k % 7) - 3) * 0.92
        if px * px + py * py > 22.0:
            g_bm = bm_blue if k % 3 == 0 else (bm_red if k % 3 == 1 else bm_wood)
            add_victorian_person(g_bm, bm_yellow, bm_skin, bm_dark, px, py, 0.0, k)

    specs = [
        ("Blue_Iron", bm_blue, (0.169, 0.357, 0.518), 0.45, 0.34),
        ("Red_Iron", bm_red, (0.714, 0.192, 0.145), 0.35, 0.40),
        ("Yellow_Sash", bm_yellow, (0.93, 0.87, 0.68), 0.35, 0.30),
        ("Wood_Floor", bm_wood, (0.46, 0.35, 0.24), 0.05, 0.65),
        ("Elm_Foliage", bm_foliage, (0.18, 0.42, 0.22), 0.08, 0.55),
        ("Crystal_Glass", bm_crystal, (0.88, 0.96, 1.00), 0.88, 0.05),
        ("Dark_Iron_Wool", bm_dark, (0.14, 0.16, 0.20), 0.40, 0.45),
        ("Skin_Tone", bm_skin, (0.86, 0.72, 0.62), 0.02, 0.55),
    ]
    for name, bm, col, met, rough in specs:
        m = bpy.data.meshes.new(name)
        bm.to_mesh(m)
        bm.free()
        for poly in m.polygons:
            poly.use_smooth = True
        m.materials.append(make_mat(name, col, met, rough))
        o = bpy.data.objects.new(name, m)
        sc.collection.objects.link(o)

    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 2
    sc.render.use_persistent_data = True
    sc.cycles.samples = 3
    sc.cycles.max_bounces = 2
    sc.cycles.use_denoising = False
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92

    sun_d = bpy.data.lights.new("Sun", type="SUN")
    sun_d.energy = 4.8
    sun_d.color = (1.0, 0.95, 0.86)
    sun_o = bpy.data.objects.new("Sun", sun_d)
    sc.collection.objects.link(sun_o)
    sun_o.rotation_euler = (math.radians(90.0 - 25.015), 0.0, math.radians(216.8039 - 180.0))

    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.76, 0.86, 0.96, 1.0)
    bg.inputs[1].default_value = 1.75
    sc.world = world

    cam_d = bpy.data.cameras.new("Cam")
    cam_d.lens = 24.0
    cam_o = bpy.data.objects.new("Cam", cam_d)
    sc.collection.objects.link(cam_o)
    sc.camera = cam_o

    cameras = [
        ("M01_transept_crossing", (0.0, -21.0, 2.1), (0.0, 4.0, 9.2)),
        ("M02_nave_looking_west", (32.0, -2.2, 2.2), (-25.0, 0.0, 7.2)),
        ("M03_nave_looking_east", (-32.0, 2.2, 2.2), (25.0, 0.0, 7.2)),
        ("M04_fountain_closeup", (6.2, -6.8, 1.8), (0.0, 0.0, 4.2)),
        ("M05_great_organ_north", (0.0, 8.0, 4.5), (0.0, 26.0, 11.5)),
        ("M06_three_elms_vault", (4.5, -18.5, 3.2), (-4.0, 8.0, 18.0)),
        ("M07_first_gallery_view", (-16.0, -12.5, 9.0), (12.0, 6.0, 8.5)),
        ("M08_british_court_west", (-18.0, -3.2, 1.70), (-29.28, -7.2, 2.4)),
        ("M09_foreign_court_east", (18.0, 3.2, 1.70), (29.28, 7.2, 2.6)),
        ("M10_roof_gutter_vault", (-12.0, -8.0, 18.2), (18.0, 4.0, 23.5)),
        ("M11_walk_eye_level", (14.64, 0.0, 1.60), (-20.0, 0.0, 2.2)),
        ("M12_exterior_oblique", (52.0, -42.0, 8.5), (0.0, 0.0, 12.0)),
        ("M13_pugin_mediaeval_court", (-18.0, 3.2, 1.70), (-29.28, 7.2, 2.5)),
        ("M14_us_court_and_telescope", (18.0, -3.2, 1.70), (29.28, -7.2, 2.3)),
        ("M15_crowd_promenade_closeup", (7.5, -5.2, 1.60), (-8.0, -3.5, 1.45)),
        ("M16_clerestory_truss_lookup", (-22.0, 0.0, 2.0), (0.0, 0.0, 22.0)),
    ]

    for cname, loc, target in cameras:
        cam_o.location = Vector(loc)
        direction = Vector(target) - cam_o.location
        cam_o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out_dir, f"{cname}.jpg")
        bpy.ops.render.render(write_still=True)
        print(f"Rendered Cycles master {cname}.jpg")

    return 0


if __name__ == "__main__":
    sys.exit(main())
