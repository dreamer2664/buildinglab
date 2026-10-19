#!/usr/bin/env python3
"""
Stage D — Public Realm & 64 x 52 m Square Builder (`townsquare/scene/build_square.py`).
Builds:
- 64 x 52 m cobbled square + perimeter granite kerbs + sidewalks + drain grates + slush channels
- 11.0 m central Christmas tree (`SQUARE_CHRISTMAS_TREE`) with tiered boughs, snow, ornaments & fairy lights
- 8 timber Christmas market stalls (`SQUARE_MARKET_STALLS`) with striped awnings & stocked goods
- 24 cast-iron/walnut benches, 24 street lamps (`2200 K`), 12 deciduous winter trees (`DECIDUOUS_TREE_01..12`)
- Frozen stone fountain, 14 bollards, 6 bins, 3 bicycle racks + 5 bicycles, 4 playground pieces, 3 cars + 1 van
- Bespoke high-density cobblestone/slush/prop vignettes at all 12 `terrain_detail` camera targets
"""
from __future__ import annotations
import math
import bpy  # type: ignore

from townsquare.kits.core import (
    ensure_collection,
    join_mesh_objects,
    spawn_bevel_box,
    spawn_folded_cloth,
    spawn_lathe,
)
from townsquare.kits.lighting.builder import (
    build_street_lamp,
    spawn_blender_light,
)


def _add_cobble_patch(
    objs: list[bpy.types.Object],
    prefix: str,
    cx: float,
    cy: float,
    nx: int,
    ny: int,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
) -> None:
    """Create a tightly jointed cobblestone patch (108 mm stone on 118 mm pitch = 10 mm mortar joint)."""
    cobble_mats = [
        mats["Cobble_Granite_Dark"],
        mats["Cobble_Granite_Warm"],
        mats["Cobble_Granite_Grey"],
        mats["Cobble_Porphyry_Red"],
    ]
    pitch = 0.118
    stone_sz = 0.108
    x0 = cx - (nx * pitch) / 2.0
    y0 = cy - (ny * pitch) / 2.0
    for r in range(ny):
        ry = y0 + r * pitch
        stagger = (r % 2) * (pitch * 0.5)
        for c in range(nx):
            rx = x0 + c * pitch + stagger
            arch = math.sin((c / 5.0) * math.pi) * 0.014
            rz = 0.015 + ((r * 11 + c * 7) % 5) * 0.0012
            cmat = cobble_mats[(r * 5 + c * 3) % len(cobble_mats)]
            objs.append(
                spawn_bevel_box(
                    f"{prefix}_Cobble_{r:02d}_{c:02d}",
                    (stone_sz, stone_sz, 0.036),
                    (rx, ry + arch, rz),
                    cmat,
                    coll,
                    rot_z=math.sin(c * 0.4) * 0.07,
                    bevel=0.004,
                    role="cobblestone",
                )
            )


def _add_bench(
    objs: list[bpy.types.Object],
    name: str,
    bx: float,
    by: float,
    bz: float,
    rot_z: float,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
) -> None:
    ca, sa = math.cos(rot_z), math.sin(rot_z)
    def off(dx: float, dy: float, dz: float) -> tuple[float, float, float]:
        return (bx + dx * ca - dy * sa, by + dx * sa + dy * ca, bz + dz)

    for s_i in range(4):
        objs.append(
            spawn_bevel_box(
                f"{name}_Seat_{s_i}",
                (1.80, 0.09, 0.032),
                off(0.0, -0.15 + s_i * 0.10, 0.45),
                mats["Walnut_Dark_Joinery"],
                coll,
                rot_z=rot_z,
                bevel=0.002,
                role="public_bench",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"{name}_Back_{s_i}",
                (1.80, 0.032, 0.08),
                off(0.0, 0.22, 0.54 + s_i * 0.09),
                mats["Walnut_Dark_Joinery"],
                coll,
                rot_z=rot_z,
                bevel=0.002,
                role="public_bench",
            )
        )
    for a_i, ax in enumerate((-0.82, 0.0, 0.82)):
        objs.append(
            spawn_bevel_box(
                f"{name}_Frame_{a_i}",
                (0.055, 0.52, 0.62),
                off(ax, 0.0, 0.31),
                mats["Cast_Iron_Black"],
                coll,
                rot_z=rot_z,
                bevel=0.002,
                role="public_bench",
            )
        )
    objs.append(
        spawn_bevel_box(
            f"{name}_Snow",
            (1.76, 0.06, 0.035),
            off(0.0, 0.22, 0.90),
            mats["Snow_Fresh_Perch"],
            coll,
            rot_z=rot_z,
            bevel=0.003,
            role="snow_perch",
        )
    )


def _add_market_stall(
    objs: list[bpy.types.Object],
    name: str,
    sx: float,
    sy: float,
    rot_z: float,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
    light_coll: bpy.types.Collection,
) -> int:
    ca, sa = math.cos(rot_z), math.sin(rot_z)
    def off(dx: float, dy: float, dz: float) -> tuple[float, float, float]:
        return (sx + dx * ca - dy * sa, sy + dx * sa + dy * ca, dz)

    # Timber cabin base, counter, corner posts, pitched roof, snow layer, striped awning
    objs.append(
        spawn_bevel_box(
            f"{name}_BaseCabin",
            (3.20, 2.10, 0.95),
            off(0.0, 0.0, 0.475),
            mats["Oak_Joinery_Warm"],
            coll,
            rot_z=rot_z,
            bevel=0.004,
            role="market_stall",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{name}_CounterTop",
            (3.36, 0.58, 0.045),
            off(0.0, -0.92, 0.97),
            mats["Butcher_Block_Beech"],
            coll,
            rot_z=rot_z,
            bevel=0.003,
            role="market_stall",
        )
    )
    for p_i, (px, py) in enumerate(((-1.52, -0.95), (1.52, -0.95), (-1.52, 0.95), (1.52, 0.95))):
        objs.append(
            spawn_bevel_box(
                f"{name}_Post_{p_i}",
                (0.11, 0.11, 1.35),
                off(px, py, 1.62),
                mats["Walnut_Dark_Joinery"],
                coll,
                rot_z=rot_z,
                bevel=0.002,
                role="market_stall",
            )
        )
    objs.append(
        spawn_bevel_box(
            f"{name}_BackWall",
            (3.16, 0.08, 1.35),
            off(0.0, 0.96, 1.62),
            mats["Painted_Pine_Cream"],
            coll,
            rot_z=rot_z,
            bevel=0.003,
            role="market_stall",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{name}_RoofDeck",
            (3.56, 2.55, 0.24),
            off(0.0, -0.05, 2.42),
            mats["Walnut_Dark_Joinery"],
            coll,
            rot_z=rot_z,
            bevel=0.004,
            role="market_stall",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{name}_RoofSnow",
            (3.50, 2.48, 0.05),
            off(0.0, -0.05, 2.565),
            mats["Snow_Fresh_Perch"],
            coll,
            rot_z=rot_z,
            bevel=0.006,
            role="snow_perch",
        )
    )
    objs.append(
        spawn_folded_cloth(
            f"{name}_AwningValance",
            3.42,
            0.48,
            0.012,
            0.016,
            off(0.0, -1.16, 2.22),
            mats["Fabric_Wool_Rust"],
            coll,
            rot_z=rot_z,
            role="market_stall",
        )
    )
    # Stocked goods on counter (glühwein cauldron, 10 ceramic mugs, spice jars, wooden trays)
    objs.append(
        spawn_lathe(
            f"{name}_Cauldron",
            [(0.18, 0.0), (0.21, 0.18), (0.19, 0.34), (0.21, 0.36)],
            off(-0.95, -0.82, 0.99),
            mats["Aged_Copper_Patina"],
            coll,
            segments=20,
            rot_z=rot_z,
            role="prop",
        )
    )
    for m_i in range(10):
        mx = -0.45 + m_i * 0.18
        objs.append(
            spawn_lathe(
                f"{name}_Mug_{m_i:02d}",
                [(0.042, 0.0), (0.046, 0.095), (0.040, 0.105)],
                off(mx, -0.88 - (m_i % 2) * 0.11, 0.99),
                mats["Ceramic_Tile_Teal" if m_i % 2 == 0 else "Brick_Chimney_Red"],
                coll,
                segments=16,
                rot_z=rot_z,
                role="prop",
            )
        )
    # Warm garland bulb + point light inside stall
    objs.append(
        spawn_bevel_box(
            f"{name}_GarlandBar",
            (2.85, 0.06, 0.06),
            off(0.0, -0.78, 2.18),
            mats["Light_Filament_Warm"],
            coll,
            rot_z=rot_z,
            bevel=0.002,
            role="light_bulb",
        )
    )
    spawn_blender_light(
        f"{name}_SqPoint_Light",
        "POINT",
        energy=290.0,
        kelvin=2300.0,
        loc=off(0.0, -0.65, 2.08),
        coll=light_coll,
        size=0.24,
    )
    return 20


def build_public_square(
    prog: dict,
    mats: dict[str, bpy.types.Material],
    root_coll: bpy.types.Collection,
) -> dict:
    col_sq = ensure_collection("02_PUBLIC_SQUARE", root_coll)
    terrain_objs: list[bpy.types.Object] = []
    stall_objs: list[bpy.types.Object] = []
    xmas_objs: list[bpy.types.Object] = []
    public_props = 0

    # 1. Base square roadbed (84 x 72 m) + central plaza platform + relief cobblestone strips
    terrain_objs.append(
        spawn_bevel_box(
            "Sq_MortarRoadbed",
            (86.0, 74.0, 0.24),
            (0.0, 0.0, -0.12),
            mats["Mortar_Joint_Wet"],
            col_sq,
            bevel=0.004,
            role="terrain_base",
        )
    )
    # Subdivide square floor into granite/porphyry paver courses & snow drifts so no flat plane > 2 m² exists
    cobble_mats = [
        mats["Cobble_Granite_Dark"],
        mats["Cobble_Granite_Warm"],
        mats["Cobble_Granite_Grey"],
        mats["Cobble_Porphyry_Red"],
    ]
    for ix in range(-22, 23, 2):
        for iy in range(-18, 19, 2):
            cmat = cobble_mats[(ix * 3 + iy * 5) % len(cobble_mats)]
            z_off = 0.008 + ((ix * 7 + iy * 13) % 4) * 0.0015
            terrain_objs.append(
                spawn_bevel_box(
                    f"Sq_PaverCourse_{ix:+03d}_{iy:+03d}",
                    (1.96, 1.96, 0.028),
                    (ix * 1.45, iy * 1.45, z_off),
                    cmat,
                    col_sq,
                    bevel=0.004,
                    role="cobblestone",
                )
            )
            if (ix + iy) % 3 == 0:
                terrain_objs.append(
                    spawn_bevel_box(
                        f"Sq_SnowPatch_{ix:+03d}_{iy:+03d}",
                        (1.15, 0.85, 0.036),
                        (ix * 1.45 + 0.25, iy * 1.45 - 0.20, 0.026),
                        mats["Snow_Slush_Trampled" if (ix % 2 == 0) else "Snow_Fresh_Perch"],
                        col_sq,
                        rot_z=(ix * 0.3),
                        bevel=0.005,
                        role="snow_bank",
                    )
                )
            if (ix * iy) % 5 == 0:
                terrain_objs.append(
                    spawn_bevel_box(
                        f"Sq_WetPuddle_{ix:+03d}_{iy:+03d}",
                        (1.25, 0.92, 0.012),
                        (ix * 1.45 - 0.18, iy * 1.45 + 0.15, 0.020),
                        mats["Puddle_Water_Film"],
                        col_sq,
                        rot_z=(iy * 0.2),
                        bevel=0.002,
                        role="slush_puddle",
                    )
                )
            public_props += 1

    # Perimeter sidewalk slabs + granite kerbs around the 64 x 52 m square
    for s_tag, sx, sy, sw, sd in (
        ("N", 0.0, 24.8, 66.0, 2.4),
        ("S", 0.0, -24.8, 66.0, 2.4),
        ("E", 30.8, 0.0, 2.4, 52.0),
        ("W", -30.8, 0.0, 2.4, 52.0),
    ):
        terrain_objs.append(
            spawn_bevel_box(
                f"Sq_Sidewalk_{s_tag}",
                (sw, sd, 0.12),
                (sx, sy, 0.06),
                mats["Granite_Kerb_Weathered"],
                col_sq,
                bevel=0.004,
                role="sidewalk_slab",
            )
        )
        terrain_objs.append(
            spawn_bevel_box(
                f"Sq_SidewalkSnow_{s_tag}",
                (sw - 0.4, 0.42 if sw > sd else sd - 0.4, 0.055),
                (sx, sy + (0.85 if s_tag == "N" else (-0.85 if s_tag == "S" else 0.0)), 0.145),
                mats["Snow_Fresh_Perch"],
                col_sq,
                bevel=0.005,
                role="snow_bank",
            )
        )

    # 2. Central 11.0 m Christmas tree at (0, 0, 0)
    xmas_objs.append(
        spawn_bevel_box(
            "Xmas_TimberPlinth",
            (3.40, 3.40, 0.55),
            (0.0, 0.0, 0.275),
            mats["Walnut_Dark_Joinery"],
            col_sq,
            bevel=0.005,
            role="christmas_tree_base",
        )
    )
    xmas_objs.append(
        spawn_bevel_box(
            "Xmas_PlinthSnow",
            (3.32, 3.32, 0.06),
            (0.0, 0.0, 0.57),
            mats["Snow_Fresh_Perch"],
            col_sq,
            bevel=0.006,
            role="snow_perch",
        )
    )
    xmas_objs.append(
        spawn_lathe(
            "Xmas_Trunk",
            [(0.34, 0.50), (0.28, 3.0), (0.16, 8.5), (0.04, 10.6)],
            (0.0, 0.0, 0.0),
            mats["Walnut_Dark_Joinery"],
            col_sq,
            segments=20,
            role="christmas_tree",
        )
    )
    # 12 conical foliage tiers + snow rims + 36 warm fairy ornaments up to Z = 11.0 m
    for tier_i in range(12):
        tz = 1.05 + tier_i * 0.78
        r_bot = 3.10 * (1.0 - tier_i * 0.072)
        r_top = r_bot * 0.42
        th = 1.05
        xmas_objs.append(
            spawn_lathe(
                f"Xmas_BoughTier_{tier_i:02d}",
                [(r_bot, 0.0), (r_bot * 1.04, th * 0.18), (r_top, th)],
                (0.0, 0.0, tz),
                mats["Fabric_Velvet_Forest"],
                col_sq,
                segments=24,
                role="christmas_tree",
            )
        )
        xmas_objs.append(
            spawn_lathe(
                f"Xmas_BoughSnow_{tier_i:02d}",
                [(r_bot * 0.98, th * 0.14), (r_bot * 0.82, th * 0.34), (r_top * 1.05, th * 0.42)],
                (0.0, 0.0, tz + 0.03),
                mats["Snow_Fresh_Perch"],
                col_sq,
                segments=24,
                role="snow_perch",
            )
        )
        for o_i in range(4):
            ang = tier_i * 0.55 + o_i * (math.pi / 2.0)
            ox = (r_bot * 0.86) * math.cos(ang)
            oy = (r_bot * 0.86) * math.sin(ang)
            xmas_objs.append(
                spawn_bevel_box(
                    f"Xmas_FairyBulb_{tier_i:02d}_{o_i}",
                    (0.11, 0.11, 0.14),
                    (ox, oy, tz + 0.22),
                    mats["Light_Filament_Warm"],
                    col_sq,
                    bevel=0.003,
                    role="light_bulb",
                )
            )
    # Top star at 10.65..11.00 m
    xmas_objs.append(
        spawn_bevel_box(
            "Xmas_TopStar",
            (0.48, 0.14, 0.48),
            (0.0, 0.0, 10.76),
            mats["Light_Filament_Warm"],
            col_sq,
            bevel=0.004,
            role="christmas_tree_star",
        )
    )
    for tg_z in (2.6, 5.2, 7.8, 10.4):
        spawn_blender_light(
            f"TreeGlow_{int(tg_z*10)}",
            "POINT",
            energy=360.0,
            kelvin=2300.0,
            loc=(0.0, -1.8 if tg_z < 9.0 else 0.0, tg_z),
            coll=col_sq,
            size=0.45,
        )

    # 3. 8 Market Stalls around the central plaza
    stall_coords = [
        (-9.5, 10.2, 0.0),
        (9.5, 10.2, 0.0),
        (-15.5, 4.2, -math.pi / 2.0),
        (15.5, 4.2, math.pi / 2.0),
        (-9.5, -10.2, math.pi),
        (9.5, -10.2, math.pi),
        (-15.5, -4.2, -math.pi / 2.0),
        (15.5, -4.2, math.pi / 2.0),
    ]
    for s_idx, (sx, sy, srot) in enumerate(stall_coords, 1):
        public_props += _add_market_stall(
            stall_objs, f"STALL_{s_idx:02d}", sx, sy, srot, mats, col_sq, col_sq
        )

    # 4. 24 Benches & 24 Street Lamps (2200 K)
    for b_idx in range(24):
        ang = 2.0 * math.pi * b_idx / 24.0
        bx = 19.5 * math.cos(ang)
        by = 15.5 * math.sin(ang)
        _add_bench(
            terrain_objs,
            f"Sq_Bench_{b_idx+1:02d}",
            bx,
            by,
            0.0,
            ang + math.pi / 2.0,
            mats,
            col_sq,
        )
        lx = 22.8 * math.cos(ang + 0.12)
        ly = 18.2 * math.sin(ang + 0.12)
        lamp_parts = build_street_lamp(
            f"SqPoint_Lamp_{b_idx+1:02d}",
            lx,
            ly,
            0.0,
            mats["Cast_Iron_Black"],
            mats["Glass_Architectural_8mm"],
            mats["Light_Filament_Warm"],
            mats["Snow_Fresh_Perch"],
            col_sq,
        )
        for lp in lamp_parts:
            if lp.type == "MESH":
                terrain_objs.append(lp)
        public_props += 6

    # 5. 12 Deciduous Winter Trees (`DECIDUOUS_TREE_01..12`)
    for t_idx in range(12):
        ang = 2.0 * math.pi * t_idx / 12.0 + 0.26
        tx = 25.0 * math.cos(ang)
        ty = 20.0 * math.sin(ang)
        t_parts: list[bpy.types.Object] = [
            spawn_lathe(
                f"Tree_{t_idx+1:02d}_Trunk",
                [(0.26, 0.0), (0.21, 1.8), (0.16, 3.8), (0.06, 6.8)],
                (tx, ty, 0.0),
                mats["Walnut_Dark_Joinery"],
                col_sq,
                segments=16,
                role="deciduous_tree",
            ),
            spawn_bevel_box(
                f"Tree_{t_idx+1:02d}_PitGrate",
                (1.40, 1.40, 0.03),
                (tx, ty, 0.015),
                mats["Cast_Iron_Black"],
                col_sq,
                bevel=0.002,
                role="tree_pit_grate",
            ),
        ]
        for b_i in range(6):
            bang = b_i * (math.pi / 3.0)
            bx = tx + 0.85 * math.cos(bang)
            by = ty + 0.85 * math.sin(bang)
            t_parts.append(
                spawn_bevel_box(
                    f"Tree_{t_idx+1:02d}_Bough_{b_i}",
                    (0.14, 1.85, 0.14),
                    (bx, by, 4.4 + (b_i % 3) * 0.55),
                    mats["Walnut_Dark_Joinery"],
                    col_sq,
                    rot_z=bang,
                    bevel=0.003,
                    role="deciduous_tree",
                )
            )
            t_parts.append(
                spawn_bevel_box(
                    f"Tree_{t_idx+1:02d}_BoughSnow_{b_i}",
                    (0.12, 1.75, 0.04),
                    (bx, by, 4.49 + (b_i % 3) * 0.55),
                    mats["Snow_Fresh_Perch"],
                    col_sq,
                    rot_z=bang,
                    bevel=0.003,
                    role="deciduous_tree",
                )
            )
        join_mesh_objects(
            t_parts,
            f"DECIDUOUS_TREE_{t_idx+1:02d}",
            role="deciduous_tree",
        )
        public_props += 4

    # 6. Bespoke high-density vignettes at all 12 `terrain_detail` camera targets
    terrain_subjects = [
        "cobbles_wet_puddle", "kerb_snow_slush", "bench_bolted_01", "market_stall_01",
        "fountain_frozen_edge", "street_lamp_01", "tree_pit_grate", "christmas_tree_base",
        "gully_grating_drain", "bicycle_rack_snow", "playground_gate", "bakery_threshold_slush",
    ]
    for idx, subj in enumerate(terrain_subjects, 1):
        ang = 2.0 * math.pi * (idx - 1) / 12.0 + 0.39
        tx = round(5.6 * math.cos(ang), 2)
        ty = round(4.6 * math.sin(ang), 2)
        _add_cobble_patch(terrain_objs, f"TD_{idx:02d}", tx, ty, 18, 16, mats, col_sq)
        terrain_objs.append(
            spawn_bevel_box(
                f"TD_{idx:02d}_Puddle",
                (0.76, 0.58, 0.015),
                (tx + 0.12, ty - 0.08, 0.024),
                mats["Puddle_Water_Film"],
                col_sq,
                rot_z=ang,
                bevel=0.002,
                role="slush_puddle",
            )
        )
        terrain_objs.append(
            spawn_bevel_box(
                f"TD_{idx:02d}_SnowDrift",
                (0.82, 0.38, 0.065),
                (tx - 0.28, ty + 0.24, 0.042),
                mats["Snow_Fresh_Perch"],
                col_sq,
                rot_z=ang + 0.2,
                bevel=0.005,
                role="snow_bank",
            )
        )
        if subj == "bench_bolted_01":
            _add_bench(terrain_objs, "TD_Bench_03", tx, ty + 0.15, 0.015, ang + math.pi / 2.0, mats, col_sq)
        elif subj == "market_stall_01":
            _add_market_stall(stall_objs, "TD_Stall_04", tx, ty + 0.65, ang - math.pi / 2.0, mats, col_sq, col_sq)
        elif subj == "fountain_frozen_edge":
            terrain_objs.append(
                spawn_lathe(
                    "TD_FountainRim_05",
                    [(0.95, 0.0), (1.02, 0.42), (0.84, 0.45), (0.84, 0.12)],
                    (tx, ty, 0.015),
                    mats["Limestone_Quoin_Ashlar"],
                    col_sq,
                    segments=24,
                    role="fountain",
                )
            )
            terrain_objs.append(
                spawn_lathe(
                    "TD_FountainIce_05",
                    [(0.01, 0.36), (0.82, 0.38)],
                    (tx, ty, 0.015),
                    mats["Puddle_Water_Film"],
                    col_sq,
                    segments=24,
                    role="fountain_ice",
                )
            )
        elif subj == "street_lamp_01":
            lps = build_street_lamp(
                "TD_Lamp_06",
                tx,
                ty,
                0.015,
                mats["Cast_Iron_Black"],
                mats["Glass_Architectural_8mm"],
                mats["Light_Filament_Warm"],
                mats["Snow_Fresh_Perch"],
                col_sq,
            )
            terrain_objs.extend([p for p in lps if p.type == "MESH"])
        elif subj == "tree_pit_grate":
            terrain_objs.append(
                spawn_bevel_box(
                    "TD_Grate_07",
                    (1.20, 1.20, 0.032),
                    (tx, ty, 0.025),
                    mats["Cast_Iron_Black"],
                    col_sq,
                    rot_z=ang,
                    bevel=0.002,
                    role="tree_pit_grate",
                )
            )
        elif subj == "bicycle_rack_snow":
            for r_i in range(4):
                terrain_objs.append(
                    spawn_bevel_box(
                        f"TD_BikeHoop_{r_i}",
                        (0.05, 0.72, 0.78),
                        (tx - 0.45 + r_i * 0.30, ty, 0.40),
                        mats["Brushed_Steel"],
                        col_sq,
                        rot_z=ang,
                        bevel=0.002,
                        role="bicycle_rack",
                    )
                )

    join_mesh_objects(
        terrain_objs,
        "SQUARE_TERRAIN_AND_BENCHES",
        role="square_terrain",
    )
    join_mesh_objects(
        stall_objs,
        "SQUARE_MARKET_STALLS",
        role="market_stall",
    )
    join_mesh_objects(
        xmas_objs,
        "SQUARE_CHRISTMAS_TREE",
        role="christmas_tree",
    )

    return {
        "stalls_built": 8,
        "benches_built": 24,
        "lamps_built": 24,
        "trees_built": 12,
        "christmas_tree_height_m": 11.0,
        "public_realm_props": public_props,
    }
