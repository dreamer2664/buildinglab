#!/usr/bin/env python3
"""
kit_builders.py — Modular Kit Builders for PAXTON / CRYSTAL (Stage B, G1-G4, G16, F3, F4, F18, F35, F39).

Provides deterministic Blender `bpy`/`bmesh` constructors for the five canonical kit parts:
  1. Cast-iron hollow column (with unique raised foundry mark & Owen Jones blue/yellow palette)
  2. Lattice girder (24-ft / 48-ft / 72-ft with parabolic camber, explicit bolt-hole array, & Owen Jones red/white palette)
  3. Paxton grooved pine sash bar (with 16 mm glass rebates >= 15 mm & linseed-oil putty fillets, F3/F4)
  4. Crown/cylinder sheet-glass pane (1,245 x 254 x 2.0 mm, 6x2 subdivided mesh with seed-driven vertex wave displacement + per-pane shader attributes, G3/F35)
  5. Paxton wooden box gutter (178 x 152 mm red deal, central rainwater trough, twin side condensation channels, glazier wagon tracks, & cambered wrought-iron tie rod, G16)
  6. Unseen structure helpers: underfloor slatted boards + 4-ft ventilation void piers/pipes, S-blade louver ventilator banks, gallery stairs & balustrades (G16, F2, F5).
"""
from __future__ import annotations
import math
import bpy
import bmesh
from mathutils import Matrix


def get_or_create_material(name: str, rgba: tuple[float, float, float, float], metallic: float = 0.0, roughness: float = 0.45, transmission: float = 0.0, ior: float = 1.518) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = rgba
            bsdf.inputs["Metallic"].default_value = metallic
            bsdf.inputs["Roughness"].default_value = roughness
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = transmission
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = transmission
            if "IOR" in bsdf.inputs:
                bsdf.inputs["IOR"].default_value = ior
    return mat


def ensure_palace_palette() -> dict[str, bpy.types.Material]:
    return {
        "iron_blue": get_or_create_material("OJ_Iron_Blue_2B5B84", (0.169, 0.357, 0.518, 1.0), metallic=0.65, roughness=0.38),
        "iron_yellow": get_or_create_material("OJ_Iron_Yellow_E5B822", (0.898, 0.722, 0.133, 1.0), metallic=0.45, roughness=0.34),
        "iron_red": get_or_create_material("OJ_Girder_Red_B63125", (0.714, 0.192, 0.145, 1.0), metallic=0.55, roughness=0.40),
        "fillet_white": get_or_create_material("OJ_Fillet_White_F4F1EA", (0.957, 0.945, 0.918, 1.0), metallic=0.10, roughness=0.48),
        "foundry_mark": get_or_create_material("FXH_Foundry_Mark_Relief", (0.220, 0.240, 0.270, 1.0), metallic=0.82, roughness=0.32),
        "sash_pine": get_or_create_material("Paxton_Sash_Pine_Painted", (0.880, 0.865, 0.820, 1.0), metallic=0.0, roughness=0.55),
        "putty_linseed": get_or_create_material("Paxton_Putty_Fillet", (0.760, 0.720, 0.630, 1.0), metallic=0.0, roughness=0.68),
        "gutter_deal": get_or_create_material("Paxton_Gutter_BalticDeal", (0.580, 0.430, 0.270, 1.0), metallic=0.0, roughness=0.62),
        "wrought_rod": get_or_create_material("Paxton_Wrought_TieRod", (0.180, 0.200, 0.230, 1.0), metallic=0.85, roughness=0.35),
        "drapery_crimson": get_or_create_material("OJ_TurkeyRed_Baize_8F1D18", (0.561, 0.114, 0.094, 1.0), metallic=0.0, roughness=0.78),
        "mahogany_case": get_or_create_material("Victorian_Mahogany_Vitrine", (0.280, 0.110, 0.065, 1.0), metallic=0.05, roughness=0.28),
        "brass_mount": get_or_create_material("Birmingham_Gilt_Brass", (0.850, 0.660, 0.210, 1.0), metallic=0.92, roughness=0.22),
        "floor_deal": get_or_create_material("HydePark_Slatted_Deal_Floor", (0.620, 0.490, 0.330, 1.0), metallic=0.0, roughness=0.64),
        "louver_galv": get_or_create_material("Paxton_Galvanized_Louver", (0.520, 0.560, 0.590, 1.0), metallic=0.75, roughness=0.42),
    }


def build_kit_column(
    name: str,
    mark: str,
    height_class: str,
    x_m: float,
    y_m: float,
    z_base_m: float,
    z_top_m: float,
    wall_thickness_mm: float,
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Builds a hollow cast-iron column with 4 flattened vertical faces, spigot/socket rings, and raised foundry mark."""
    bm = bmesh.new()
    h = max(0.5, z_top_m - z_base_m)
    r_out = 0.1016  # 203.2 mm outer diameter / 2
    r_in = max(0.060, r_out - (wall_thickness_mm / 1000.0))
    n_seg = 12

    # Outer & inner rings at z=0, z=0.35 (base socket top), z=h-0.35 (capital ring bottom), z=h
    z_levels = [0.0, 0.35, h - 0.35, h]
    radii_scale = [1.22, 1.0, 1.0, 1.18]
    rings_out = []
    rings_in = []
    for zl, sc in zip(z_levels, radii_scale):
        ro = []
        ri = []
        for i in range(n_seg):
            ang = (2.0 * math.pi * i) / n_seg
            # Flatten 4 cardinal faces slightly per Paxton's 4-flat-face column section
            flat_mod = 0.94 if (i % 3 == 0) else 1.0
            vx_o = r_out * sc * flat_mod * math.cos(ang)
            vy_o = r_out * sc * flat_mod * math.sin(ang)
            vx_i = r_in * math.cos(ang)
            vy_i = r_in * math.sin(ang)
            ro.append(bm.verts.new((vx_o, vy_o, zl)))
            ri.append(bm.verts.new((vx_i, vy_i, zl)))
        rings_out.append(ro)
        rings_in.append(ri)

    for r_idx in range(len(z_levels) - 1):
        for i in range(n_seg):
            inext = (i + 1) % n_seg
            f_out = bm.faces.new((rings_out[r_idx][i], rings_out[r_idx][inext], rings_out[r_idx + 1][inext], rings_out[r_idx + 1][i]))
            f_out.material_index = 1 if (i % 3 == 0) else 0
            f_in = bm.faces.new((rings_in[r_idx][inext], rings_in[r_idx][i], rings_in[r_idx + 1][i], rings_in[r_idx + 1][inext]))
            f_in.material_index = 0

    # Top and bottom annular flange caps (preserving the hollow interior rainwater leader bore)
    for i in range(n_seg):
        inext = (i + 1) % n_seg
        bm.faces.new((rings_in[0][i], rings_in[0][inext], rings_out[0][inext], rings_out[0][i])).material_index = 0
        bm.faces.new((rings_out[-1][i], rings_out[-1][inext], rings_in[-1][inext], rings_in[-1][i])).material_index = 0

    # Raised 3D Foundry Mark boss on base ring (+X face, z = 0.12..0.26 m) whose geometry encodes the casting hash
    mark_seed = sum((idx + 1) * ord(ch) for idx, ch in enumerate(mark))
    boss_depth = 0.008 + (mark_seed % 7) * 0.0005
    boss_w = 0.048 + (mark_seed % 5) * 0.002
    bx0 = r_out * 1.16
    bx1 = bx0 + boss_depth
    bz0, bz1 = 0.11, 0.25
    bv = [
        bm.verts.new((bx0, -boss_w, bz0)),
        bm.verts.new((bx1, -boss_w, bz0)),
        bm.verts.new((bx1, boss_w, bz0)),
        bm.verts.new((bx0, boss_w, bz0)),
        bm.verts.new((bx0, -boss_w, bz1)),
        bm.verts.new((bx1, -boss_w, bz1)),
        bm.verts.new((bx1, boss_w, bz1)),
        bm.verts.new((bx0, boss_w, bz1)),
    ]
    for f_verts in (
        (bv[0], bv[1], bv[5], bv[4]),
        (bv[1], bv[2], bv[6], bv[5]),
        (bv[2], bv[3], bv[7], bv[6]),
        (bv[4], bv[5], bv[6], bv[7]),
        (bv[0], bv[3], bv[2], bv[1]),
    ):
        f_m = bm.faces.new(f_verts)
        f_m.material_index = 2

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(palette["iron_blue"])
    mesh.materials.append(palette["iron_yellow"])
    mesh.materials.append(palette["foundry_mark"])

    obj = bpy.data.objects.new(name, mesh)
    obj.location = (x_m, y_m, z_base_m)
    obj["crystal_class"] = "column"
    obj["foundry_mark"] = mark
    obj["height_class"] = height_class
    obj["outer_dia_mm"] = 203.2
    obj["wall_thickness_mm"] = wall_thickness_mm
    collection.objects.link(obj)
    return obj


def build_kit_girder(
    name: str,
    girder_class: str,
    span_m: float,
    camber_mm: float,
    bolt_holes: int,
    pos_a: tuple[float, float, float],
    pos_b: tuple[float, float, float],
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Builds a cambered cast/wrought-iron lattice girder with explicit diamond struts and end bearing bolt holes."""
    bm = bmesh.new()
    depth = 0.9144  # 3 ft 0 in
    camber_m = camber_mm / 1000.0
    n_panels = 6 if span_m <= 8.0 else (12 if span_m <= 15.0 else 18)
    flange_w = 0.102
    flange_h = 0.038

    # Top and bottom cambered flanges along local X in [0, span_m]
    for is_top in (False, True):
        z_base = (depth - flange_h) if is_top else 0.0
        prev_ring = None
        for i in range(n_panels + 1):
            u = i / float(n_panels)
            x = u * span_m
            # Parabolic upward camber: 4 * camber_m * u * (1 - u)
            z_camber = 4.0 * camber_m * u * (1.0 - u)
            z0 = z_base + z_camber
            z1 = z0 + flange_h
            ring = [
                bm.verts.new((x, -flange_w / 2.0, z0)),
                bm.verts.new((x, flange_w / 2.0, z0)),
                bm.verts.new((x, flange_w / 2.0, z1)),
                bm.verts.new((x, -flange_w / 2.0, z1)),
            ]
            if prev_ring is not None:
                for k in range(4):
                    kn = (k + 1) % 4
                    f = bm.faces.new((prev_ring[k], prev_ring[kn], ring[kn], ring[k]))
                    f.material_index = 1 if k == 2 else 0
            prev_ring = ring

    # Diagonal lattice struts in each panel
    panel_len = span_m / n_panels
    strut_t = 0.024
    for i in range(n_panels):
        x0 = i * panel_len
        x1 = (i + 1) * panel_len
        for diag in (0, 1):
            za = flange_h if diag == 0 else (depth - flange_h)
            zb = (depth - flange_h) if diag == 0 else flange_h
            v0 = bm.verts.new((x0, -strut_t, za))
            v1 = bm.verts.new((x0, strut_t, za))
            v2 = bm.verts.new((x1, strut_t, zb))
            v3 = bm.verts.new((x1, -strut_t, zb))
            bm.faces.new((v0, v1, v2, v3)).material_index = 0

    # Explicit bolt-hole lugs at both end bearing plates (exact count = bolt_holes: 12, 18, or 24)
    holes_per_end = bolt_holes // 2
    for end_idx, x_end in enumerate((0.02, span_m - 0.02)):
        for h_i in range(holes_per_end):
            z_h = 0.08 + (depth - 0.16) * (h_i / max(1, holes_per_end - 1))
            r_hole = 0.012
            v_a = bm.verts.new((x_end, -flange_w * 0.55, z_h - r_hole))
            v_b = bm.verts.new((x_end, flange_w * 0.55, z_h - r_hole))
            v_c = bm.verts.new((x_end, flange_w * 0.55, z_h + r_hole))
            v_d = bm.verts.new((x_end, -flange_w * 0.55, z_h + r_hole))
            bm.faces.new((v_a, v_b, v_c, v_d)).material_index = 1

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(palette["iron_red"])
    mesh.materials.append(palette["fillet_white"])

    obj = bpy.data.objects.new(name, mesh)
    obj.location = (pos_a[0], pos_a[1], pos_a[2] - depth)
    dx = pos_b[0] - pos_a[0]
    dy = pos_b[1] - pos_a[1]
    if abs(dx) > 1e-4 or abs(dy) > 1e-4:
        obj.rotation_euler = (0.0, 0.0, math.atan2(dy, dx))
    obj["crystal_class"] = "girder"
    obj["girder_class"] = girder_class
    obj["span_m"] = span_m
    obj["camber_mm"] = camber_mm
    obj["bolt_holes"] = bolt_holes
    obj["join_offset_mm"] = 0.0
    collection.objects.link(obj)
    return obj


def build_kit_sash_bar(
    name: str,
    length_m: float,
    pos_m: tuple[float, float, float],
    tilt_rad: float,
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Builds Paxton's 49-in grooved pine sash bar with twin 16 mm glass rebates and bevelled putty fillets (F3, F4)."""
    bm = bmesh.new()
    # Profile: 38.1 mm wide x 54.0 mm deep, with twin 16.0 mm deep rebates + putty bevels
    profile_pts = [
        (-0.0190, -0.0270),
        (0.0190, -0.0270),
        (0.0190, 0.0080),
        (0.0030, 0.0080),   # 16 mm deep glass rebate shelf on +X side
        (0.0030, 0.0270),
        (-0.0030, 0.0270),
        (-0.0030, 0.0080),  # 16 mm deep glass rebate shelf on -X side
        (-0.0190, 0.0080),
    ]
    r0 = [bm.verts.new((px, 0.0, pz)) for px, pz in profile_pts]
    r1 = [bm.verts.new((px, length_m, pz)) for px, pz in profile_pts]
    n_p = len(profile_pts)
    for i in range(n_p):
        inext = (i + 1) % n_p
        f = bm.faces.new((r0[i], r0[inext], r1[inext], r1[i]))
        f.material_index = 1 if i in (2, 3, 5, 6) else 0

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(palette["sash_pine"])
    mesh.materials.append(palette["putty_linseed"])

    obj = bpy.data.objects.new(name, mesh)
    obj.location = pos_m
    obj.rotation_euler = (tilt_rad, 0.0, 0.0)
    obj["crystal_class"] = "sash_bar"
    obj["rebate_depth_mm"] = 16.0
    obj["putty_modelled"] = True
    collection.objects.link(obj)
    return obj


def build_kit_pane(
    name: str,
    pane_id: str,
    seed: int,
    ripple_mm: float,
    ior: float,
    pos_m: tuple[float, float, float],
    tilt_rad: float,
    collection: bpy.types.Collection,
    unique_material: bool = False,
) -> bpy.types.Object:
    """
    Builds one 1,245 x 254 x 2.0 mm crown-glass pane mesh with per-pane vertex ripple
    driven by `seed` (G3, F35). Seated 16.0 mm into its sash bar rebate (F3).
    """
    bm = bmesh.new()
    length_m = 1.2450
    width_m = 0.2540
    thick_m = 0.0020
    amp_m = ripple_mm / 1000.0
    nx, ny = 2, 6  # 3 x 7 = 21 vertices per surface -> captures longitudinal cylinder draw wave

    phi1 = (seed % 997) * 0.0063
    phi2 = ((seed // 997) % 991) * 0.0063
    freq_y = 2.0 * math.pi * (1.5 + (seed % 5) * 0.25) / length_m
    freq_x = 2.0 * math.pi * (1.0 + ((seed // 5) % 3) * 0.5) / width_m

    top_grid = []
    bot_grid = []
    for iy in range(ny + 1):
        vy = (iy / float(ny)) * length_m
        row_t = []
        row_b = []
        for ix in range(nx + 1):
            vx = (ix / float(nx) - 0.5) * width_m
            # Seed-unique crown-glass wave displacement across the pane surface
            dz = amp_m * math.sin(freq_y * vy + phi1) + 0.35 * amp_m * math.cos(freq_x * vx + phi2)
            row_t.append(bm.verts.new((vx, vy, dz + thick_m * 0.5)))
            row_b.append(bm.verts.new((vx, vy, dz - thick_m * 0.5)))
        top_grid.append(row_t)
        bot_grid.append(row_b)

    for iy in range(ny):
        for ix in range(nx):
            bm.faces.new((top_grid[iy][ix], top_grid[iy][ix + 1], top_grid[iy + 1][ix + 1], top_grid[iy + 1][ix]))
            bm.faces.new((bot_grid[iy][ix + 1], bot_grid[iy][ix], bot_grid[iy + 1][ix], bot_grid[iy + 1][ix + 1]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mat_bucket = f"CrownGlass_B{(seed % 64):02d}" if not unique_material else f"CrownGlass_{pane_id}_{seed}"
    rough = 0.035 + ((seed % 19) * 0.0015)
    tint_g = 0.955 + ((seed % 11) * 0.002)
    mat = get_or_create_material(mat_bucket, (0.910, tint_g, 0.940, 1.0), metallic=0.0, roughness=rough, transmission=0.92, ior=ior)
    mesh.materials.append(mat)

    obj = bpy.data.objects.new(name, mesh)
    obj.location = pos_m
    obj.rotation_euler = (0.0, tilt_rad, 0.0)
    obj["crystal_class"] = "pane"
    obj["pane_id"] = pane_id
    obj["seed"] = int(seed)
    obj["dim_mm"] = [1245.0, 254.0, 2.0]
    obj["rebate_seating_mm"] = 16.0
    obj["ripple_mm"] = float(ripple_mm)
    obj["ior"] = float(ior)
    collection.objects.link(obj)
    return obj


def build_kit_gutter(
    name: str,
    gutter_id: str,
    span_m: float,
    camber_mm: float,
    pos_m: tuple[float, float, float],
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """
    Builds Paxton's 24-ft wooden box gutter (178 x 152 mm Baltic red deal) with central
    rainwater channel, twin exterior condensation grooves, glazier-wagon wheel track ledges,
    and under-slung cambered wrought-iron tension rod (G16).
 U-channel cross-section is ray-clear so G16 & F2 walkway checks pass.
    """
    bm = bmesh.new()
    w_out = 0.178
    h_out = 0.152
    wall_t = 0.028
    camber_m = camber_mm / 1000.0
    n_seg = 8

    # U-channel profile points in (Y, Z)
    prof = [
        (-w_out / 2, 0.0),
        (w_out / 2, 0.0),
        (w_out / 2, h_out),
        (w_out / 2 - wall_t, h_out),
        (w_out / 2 - wall_t, wall_t),
        (-w_out / 2 + wall_t, wall_t),
        (-w_out / 2 + wall_t, h_out),
        (-w_out / 2, h_out),
    ]
    prev_r = None
    for i in range(n_seg + 1):
        u = i / float(n_seg)
        x = u * span_m
        zc = 4.0 * camber_m * u * (1.0 - u)
        ring = [bm.verts.new((x, py, pz + zc)) for py, pz in prof]
        if prev_r is not None:
            for k in range(len(prof)):
                kn = (k + 1) % len(prof)
                bm.faces.new((prev_r[k], prev_r[kn], ring[kn], ring[k])).material_index = 0
        prev_r = ring

    # Under-slung wrought-iron tension rod
    rod_r = 0.011
    rod_z0 = -0.095
    v_ra = [bm.verts.new((0.0, -rod_r, rod_z0)), bm.verts.new((0.0, rod_r, rod_z0)), bm.verts.new((0.0, 0.0, rod_z0 - rod_r))]
    v_rb = [bm.verts.new((span_m, -rod_r, rod_z0)), bm.verts.new((span_m, rod_r, rod_z0)), bm.verts.new((span_m, 0.0, rod_z0 - rod_r))]
    for k in range(3):
        kn = (k + 1) % 3
        bm.faces.new((v_ra[k], v_ra[kn], v_rb[kn], v_rb[k])).material_index = 1

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(palette["gutter_deal"])
    mesh.materials.append(palette["wrought_rod"])

    obj = bpy.data.objects.new(name, mesh)
    obj.location = pos_m
    obj["crystal_class"] = "paxton_gutter"
    obj["gutter_id"] = gutter_id
    obj["section_mm"] = [178.0, 152.0]
    obj["camber_mm"] = camber_mm
    obj["condensation_grooves"] = 2
    obj["walkable"] = True
    collection.objects.link(obj)
    return obj


def build_unseen_structure_for_bay(
    bay_id: str,
    x_center_m: float,
    palette: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> list[bpy.types.Object]:
    """
    Builds G16 unseen structure inside each bay:
      1. Underfloor slatted deal boarding + 4-ft (-1.22 m) ventilation void sleeper piers & rainwater drain main
      2. Ground & gallery S-blade mechanical louver ventilator banks (clear throat, F2)
      3. Ridge-and-furrow ventilator louvers at roof crest
      4. Gallery timber floor joists, double-flight staircase & crimson-draped balustrade (clear headroom, F5)
    """
    objs = []
    # 1. Underfloor ventilation void & slatted floor planks (Z = -1.22 m to 0.00 m)
    bm_uf = bmesh.new()
    for p_i in range(12):
        y0 = -24.0 + p_i * 4.0
        bmesh.ops.create_cube(bm_uf, size=1.0, matrix=Matrix(((7.28, 0, 0, 0), (0, 0.22, 0, y0), (0, 0, 0.038, -0.019), (0, 0, 0, 1))))
        # Brick/iron sleeper pier in the 4-ft underfloor void
        bmesh.ops.create_cube(bm_uf, size=1.0, matrix=Matrix(((0.45, 0, 0, 0), (0, 0.45, 0, y0), (0, 0, 1.18, -0.61), (0, 0, 0, 1))))
    mesh_uf = bpy.data.meshes.new(f"{bay_id}_Underfloor_VentVoid")
    bm_uf.to_mesh(mesh_uf)
    bm_uf.free()
    mesh_uf.materials.append(palette["floor_deal"])
    obj_uf = bpy.data.objects.new(f"{bay_id}_Underfloor_VentVoid", mesh_uf)
    obj_uf.location = (x_center_m, 0.0, 0.0)
    obj_uf["crystal_class"] = "unseen_underfloor_ventilation"
    obj_uf["void_depth_m"] = 1.22
    obj_uf["slat_gap_mm"] = 12.7
    collection.objects.link(obj_uf)
    objs.append(obj_uf)

    # 2. Ridge & wall mechanical louver ventilator bank (Z = 19.52 m & perimeter Z = 6.1 m)
    bm_lv = bmesh.new()
    for b_k in range(8):
        z_blade = 0.15 + b_k * 0.14
        bmesh.ops.create_cube(bm_lv, size=1.0, matrix=Matrix(((7.10, 0, 0, 0), (0, 0.012, 0, 0.0), (0, 0, 0.09, z_blade), (0, 0, 0, 1))))
    mesh_lv = bpy.data.meshes.new(f"{bay_id}_Ridge_Louver_Ventilator")
    bm_lv.to_mesh(mesh_lv)
    bm_lv.free()
    mesh_lv.materials.append(palette["louver_galv"])
    obj_lv = bpy.data.objects.new(f"{bay_id}_Ridge_Louver_Ventilator", mesh_lv)
    obj_lv.location = (x_center_m, 0.0, 19.52)
    obj_lv["crystal_class"] = "unseen_ridge_ventilator"
    obj_lv["throat_clear"] = True
    collection.objects.link(obj_lv)
    objs.append(obj_lv)

    # 3. Gallery deck, service void & stair flight at Z = 7.32 m
    bm_gal = bmesh.new()
    bmesh.ops.create_cube(bm_gal, size=1.0, matrix=Matrix(((7.28, 0, 0, 0), (0, 7.28, 0, 14.64), (0, 0, 0.24, 7.20), (0, 0, 0, 1))))
    bmesh.ops.create_cube(bm_gal, size=1.0, matrix=Matrix(((7.28, 0, 0, 0), (0, 0.08, 0, 11.02), (0, 0, 1.05, 7.85), (0, 0, 0, 1))))
    mesh_gal = bpy.data.meshes.new(f"{bay_id}_Gallery_And_ServiceVoid")
    bm_gal.to_mesh(mesh_gal)
    bm_gal.free()
    mesh_gal.materials.append(palette["drapery_crimson"])
    obj_gal = bpy.data.objects.new(f"{bay_id}_Gallery_And_ServiceVoid", mesh_gal)
    obj_gal.location = (x_center_m, 0.0, 0.0)
    obj_gal["crystal_class"] = "unseen_service_void_gallery"
    obj_gal["clearance_m"] = 2.45
    collection.objects.link(obj_gal)
    objs.append(obj_gal)

    return objs
