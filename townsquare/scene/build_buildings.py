#!/usr/bin/env python3
"""
Stage C (Expanded) — 20-Building Two-Neighbourhood Kit & Assembly Builder (`townsquare/scene/build_buildings.py`).
Builds all 20 buildings (`B01`..`B20`, 108 floors, 176 apartments, 1,400 dressed rooms) across:
  - Neighbourhood 1: Winterlichtplatz (`B01`..`B12`)
  - Neighbourhood 2: Schlosspark-Viertel & Lindenallee (`B13`..`B20`)
Includes directional shopfront arcades (`south`, `north`, `west`, `east`), wrought-iron Juliet balconies,
oriel bay windows, Art-Deco cinema marquee & vertical fin sign (`B13`), Alpine half-timber framing & copper
turret (`B15`), industrial brick-and-iron loft pilasters (`B16`, `B18`), Belle-Époque patisserie trim (`B17`),
classical portico (`B19`), and Victorian cast-iron & glass market hall canopy (`B20`).
"""
from __future__ import annotations
import math
import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from townsquare.kits.core import (
    ensure_collection,
    join_mesh_objects,
    spawn_bevel_box,
    spawn_lathe,
)
from townsquare.kits.walls.builder import (
    build_exterior_facade_shell,
    build_room_interior_partitions,
)
from townsquare.kits.openings.builder import (
    build_door_assembly,
    build_shopfront_arcade,
    build_window_assembly,
)
from townsquare.kits.roofs.builder import build_pitched_roof
from townsquare.kits.stairs.builder import build_stair_and_landing_core
from townsquare.kits.lighting.builder import spawn_blender_light
from townsquare.kits.furniture.builder import dress_room_detailed


STUCCO_PALETTE = [
    "Stucco_Pastel_Ochre",
    "Stucco_Warm_Cream",
    "Stucco_Sage_Grey",
    "Stucco_Terracotta_Rose",
    "Stucco_Dusty_Blue",
    "Stucco_Sandstone_Buff",
]


def _add_directional_facade_features(
    shell_objs: list[bpy.types.Object],
    b: dict,
    b_idx: int,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
) -> None:
    """
    Add street-facing shopfront arcades, awnings, signage, Juliet balconies, bay windows,
    and bespoke architectural features oriented toward `b['facing']` ('south', 'north', 'west', 'east').
    """
    bid = b["id"]
    cx, cy = b["center"]
    bw, bd = b["width"], b["depth"]
    facing = b.get("facing", "south")
    style = b.get("facade_style", "")
    total_h = b["total_height_m"]

    # Local-to-world transform where local +U is along facade width (`span`), +V is outward normal from facade
    if facing == "south":
        span = bw
        fx, fy = cx, cy - bd / 2.0
        rot_z = 0.0
        ux, uy = 1.0, 0.0
        vx, vy = 0.0, -1.0
    elif facing == "north":
        span = bw
        fx, fy = cx, cy + bd / 2.0
        rot_z = math.pi
        ux, uy = -1.0, 0.0
        vx, vy = 0.0, 1.0
    elif facing == "west":
        span = bd
        fx, fy = cx - bw / 2.0, cy
        rot_z = -math.pi / 2.0
        ux, uy = 0.0, 1.0
        vx, vy = -1.0, 0.0
    else:  # east
        span = bd
        fx, fy = cx + bw / 2.0, cy
        rot_z = math.pi / 2.0
        ux, uy = 0.0, -1.0
        vx, vy = 1.0, 0.0

    def fpos(u: float, v_out: float, z: float) -> tuple[float, float, float]:
        return (fx + u * ux + v_out * vx, fy + u * uy + v_out * vy, z)

    def fdims(w_u: float, d_v: float, h_z: float) -> tuple[float, float, float]:
        return (w_u, d_v, h_z)

    accent_mats = [
        mats["Painted_Pine_Teal"],
        mats["Painted_Metal_Burgundy"],
        mats["Painted_Metal_Green"],
        mats["Painted_Metal_Navy"],
        mats["Walnut_Dark_Joinery"],
    ]
    m_fascia = accent_mats[b_idx % len(accent_mats)]
    m_gold = mats["Gold_Sign_Leaf"]
    m_iron = mats["Cast_Iron_Black"]
    m_stone = mats["Limestone_Quoin_Ashlar"]
    m_snow = mats["Snow_Fresh_Perch"]
    m_copper = mats["Roof_Copper_Patina"]
    m_emit = mats["Emitter_Festive_2400K"]
    m_glow = mats["Window_Warm_Interior_Glow"]

    # For North, West, East buildings (and B13..B20), add primary facing shopfront fascia, awning & guild sign
    if facing != "south":
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_DirFascia",
                fdims(span - 1.4, 0.22, 0.46),
                fpos(0.0, 0.14, 3.32),
                m_fascia,
                coll,
                rot_z=rot_z,
                bevel=0.003,
                building_id=bid,
                role="shop_fascia",
            )
        )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_DirSignPlaque",
                fdims(min(5.2, span * 0.45), 0.06, 0.30),
                fpos(0.0, 0.26, 3.32),
                m_gold,
                coll,
                rot_z=rot_z,
                bevel=0.002,
                building_id=bid,
                role="shop_sign",
            )
        )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_DirAwning",
                fdims(span - 1.8, 1.05, 0.14),
                fpos(0.0, 0.56, 2.96),
                mats["Fabric_Canvas_Awning" if b_idx % 2 == 0 else "Fabric_Wool_Rust"],
                coll,
                rot_z=rot_z,
                bevel=0.004,
                building_id=bid,
                role="shop_awning",
            )
        )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_DirAwningSnow",
                fdims(span - 1.9, 0.96, 0.038),
                fpos(0.0, 0.56, 3.05),
                m_snow,
                coll,
                rot_z=rot_z,
                bevel=0.005,
                building_id=bid,
                role="snow_perch",
            )
        )

    # Add upper-floor windows + warm glow on North-facing buildings (B07..B09, B19..B20)
    if facing == "north":
        n_bays = max(4, int(span // 3.4))
        u0 = -span / 2.0 + 1.65
        u_step = (span - 3.30) / max(1, n_bays - 1)
        for fl in b["floors"]:
            ffl = fl["ffl_m"]
            is_ground = fl["use"] == "commercial"
            win_z = ffl + (1.85 if is_ground else 1.70)
            win_h = 2.15 if is_ground else 1.62
            for b_i in range(n_bays):
                u = u0 + b_i * u_step
                if is_ground and b_i == n_bays // 2:
                    shell_objs.extend(
                        build_door_assembly(
                            f"{bid}_NorthEntryDoor",
                            fpos(u, 0.02, ffl),
                            mats["Walnut_Dark_Joinery"],
                            mats["Oak_Joinery_Warm"],
                            mats["Aged_Brass"],
                            coll,
                            rot_z=rot_z,
                        )
                    )
                    continue
                shell_objs.extend(
                    build_window_assembly(
                        f"{bid}_{fl['floor']}_NWin_{b_i:02d}",
                        fpos(u, 0.06, win_z),
                        1.25,
                        win_h,
                        mats["Painted_Pine_Cream"],
                        mats["Glass_Architectural_8mm"],
                        m_stone,
                        m_snow,
                        coll,
                        rot_z=rot_z,
                        with_shutters=(not is_ground),
                    )
                )
                shell_objs.append(
                    spawn_bevel_box(
                        f"{bid}_{fl['floor']}_NGlow_{b_i:02d}",
                        fdims(1.18, 0.02, win_h - 0.12),
                        fpos(u, 0.03, win_z),
                        m_glow,
                        coll,
                        rot_z=rot_z,
                        bevel=0.002,
                        role="window_glow_backdrop",
                    )
                )

    # Wrought-iron Juliet Balconies on L02 and L03 across all 20 buildings
    for fl in b["floors"]:
        if fl["level"] not in (2, 3):
            continue
        ffl = fl["ffl_m"]
        for side_u in (-span * 0.28, span * 0.28):
            # Stone balcony corbel slab + snow cap + wrought-iron railing
            shell_objs.append(
                spawn_bevel_box(
                    f"{bid}_{fl['floor']}_BalcSlab_{side_u:+.1f}",
                    fdims(1.68, 0.58, 0.11),
                    fpos(side_u, 0.29, ffl + 0.04),
                    m_stone,
                    coll,
                    rot_z=rot_z,
                    bevel=0.003,
                    building_id=bid,
                )
            )
            shell_objs.append(
                spawn_bevel_box(
                    f"{bid}_{fl['floor']}_BalcRailTop_{side_u:+.1f}",
                    fdims(1.66, 0.56, 0.04),
                    fpos(side_u, 0.28, ffl + 0.98),
                    m_iron,
                    coll,
                    rot_z=rot_z,
                    bevel=0.002,
                    building_id=bid,
                )
            )
            shell_objs.append(
                spawn_bevel_box(
                    f"{bid}_{fl['floor']}_BalcSnow_{side_u:+.1f}",
                    fdims(1.60, 0.08, 0.032),
                    fpos(side_u, 0.54, ffl + 1.02),
                    m_snow,
                    coll,
                    rot_z=rot_z,
                    bevel=0.003,
                    building_id=bid,
                )
            )
            for b_p in range(-3, 4):
                shell_objs.append(
                    spawn_bevel_box(
                        f"{bid}_{fl['floor']}_BalcBar_{side_u:+.1f}_{b_p}",
                        fdims(0.028, 0.028, 0.88),
                        fpos(side_u + b_p * 0.24, 0.54, ffl + 0.52),
                        m_iron,
                        coll,
                        rot_z=rot_z,
                        bevel=0.001,
                        building_id=bid,
                    )
                )

    # Bespoke architectural façade treatments by building style
    if style == "art_deco_cinema_marquee":
        # B13 Kino Astoria: cantilevered marquee canopy + glowing light strips + tall vertical fin sign
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_CinemaMarqueeCanopy",
                fdims(7.8, 2.20, 0.58),
                fpos(0.0, 1.10, 3.55),
                mats["Painted_Metal_Burgundy"],
                coll,
                rot_z=rot_z,
                bevel=0.005,
                building_id=bid,
            )
        )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_CinemaMarqueeLights",
                fdims(7.6, 2.12, 0.34),
                fpos(0.0, 1.12, 3.55),
                m_emit,
                coll,
                rot_z=rot_z,
                bevel=0.003,
                building_id=bid,
            )
        )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_CinemaMarqueeSnow",
                fdims(7.6, 2.08, 0.045),
                fpos(0.0, 1.10, 3.86),
                m_snow,
                coll,
                rot_z=rot_z,
                bevel=0.005,
                building_id=bid,
            )
        )
        # Vertical Art-Deco blade sign tower ("ASTORIA")
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_CinemaVerticalTower",
                fdims(0.75, 1.25, 8.80),
                fpos(0.0, 0.65, 9.20),
                mats["Painted_Metal_Burgundy"],
                coll,
                rot_z=rot_z,
                bevel=0.004,
                building_id=bid,
            )
        )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_CinemaVerticalNeon",
                fdims(0.82, 1.10, 8.20),
                fpos(0.0, 0.72, 9.20),
                m_emit,
                coll,
                rot_z=rot_z,
                bevel=0.003,
                building_id=bid,
            )
        )

    elif style in ("alpine_half_timber_tavern", "timber_framed_gable"):
        # B03 & B15: Half-timbered Fachwerk framing + projecting polygonal copper turret bay
        m_timber = mats["Timber_Half_Frame"]
        for fl in b["floors"]:
            if fl["use"] == "commercial":
                continue
            ffl = fl["ffl_m"]
            shell_objs.append(
                spawn_bevel_box(
                    f"{bid}_{fl['floor']}_TimberBeam",
                    fdims(span - 0.4, 0.08, 0.16),
                    fpos(0.0, 0.05, ffl + 0.82),
                    m_timber,
                    coll,
                    rot_z=rot_z,
                    bevel=0.002,
                    building_id=bid,
                )
            )
            for t_i in range(-4, 5):
                shell_objs.append(
                    spawn_bevel_box(
                        f"{bid}_{fl['floor']}_TimberPost_{t_i}",
                        fdims(0.14, 0.08, 3.10),
                        fpos(t_i * (span * 0.11), 0.05, ffl + 1.60),
                        m_timber,
                        coll,
                        rot_z=rot_z,
                        bevel=0.002,
                        building_id=bid,
                    )
                )
        # Central projecting oriel bay + copper spire roof
        oriel_h = total_h - 4.20
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_OrielBay",
                fdims(2.60, 0.95, oriel_h),
                fpos(0.0, 0.48, 4.20 + oriel_h / 2.0),
                mats["Plaster_Warm_Ochre"],
                coll,
                rot_z=rot_z,
                bevel=0.004,
                building_id=bid,
            )
        )
        shell_objs.append(
            spawn_lathe(
                f"{bid}_OrielCopperSpire",
                [(0.0, 0.0), (1.55, 0.0), (1.20, 0.85), (0.35, 2.20), (0.0, 2.85)],
                fpos(0.0, 0.55, total_h),
                m_copper,
                coll,
                segments=12,
                building_id=bid,
            )
        )

    elif style in ("renaissance_arched_conservatory", "classical_cobalt_galerie", "grand_hotel_rusticated"):
        # Projecting stone oriel bay + classical entrance columns
        oriel_h = total_h - 4.20 - 3.20
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_StoneOrielBay",
                fdims(3.10, 0.82, oriel_h),
                fpos(0.0, 0.42, 4.20 + oriel_h / 2.0),
                m_stone,
                coll,
                rot_z=rot_z,
                bevel=0.004,
                building_id=bid,
            )
        )
        for col_u in (-1.65, 1.65):
            shell_objs.append(
                spawn_lathe(
                    f"{bid}_PorticoCol_{col_u:+.1f}",
                    [(0.26, 0.0), (0.22, 0.35), (0.19, 3.60), (0.28, 3.95), (0.0, 4.00)],
                    fpos(col_u, 0.45, 0.0),
                    m_stone,
                    coll,
                    segments=14,
                    building_id=bid,
                )
            )

    elif style in ("victorian_iron_market_hall", "iron_conservatory_bay"):
        # B10 & B20: Victorian cast-iron arcade colonnade + glazed canopy along the storefront
        n_cols = 7
        for c_i in range(n_cols):
            cu = -span * 0.42 + c_i * (span * 0.84 / (n_cols - 1))
            shell_objs.append(
                spawn_lathe(
                    f"{bid}_ArcadeIronCol_{c_i}",
                    [(0.18, 0.0), (0.14, 0.4), (0.11, 3.4), (0.20, 3.75), (0.0, 3.80)],
                    fpos(cu, 1.35, 0.0),
                     mats["Painted_Metal_Green"],
                    coll,
                    segments=12,
                    building_id=bid,
                )
            )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_MarketGlassCanopy",
                fdims(span - 1.2, 1.65, 0.18),
                fpos(0.0, 0.82, 3.82),
                mats["Painted_Metal_Green"],
                coll,
                rot_z=rot_z,
                bevel=0.004,
                building_id=bid,
            )
        )
        shell_objs.append(
            spawn_bevel_box(
                f"{bid}_MarketCanopySnow",
                fdims(span - 1.3, 1.50, 0.04),
                fpos(0.0, 0.82, 3.93),
                m_snow,
                coll,
                rot_z=rot_z,
                bevel=0.004,
                building_id=bid,
            )
        )


def build_all_buildings(
    prog: dict,
    mats: dict[str, bpy.types.Material],
    root_coll: bpy.types.Collection,
) -> dict:
    col_bldgs = ensure_collection("01_BUILDINGS", root_coll)
    col_tmpls = ensure_collection("99_ROOM_TEMPLATES", root_coll)
    col_tmpls.hide_render = True
    col_tmpls.hide_viewport = True

    rm_cache: dict[tuple[str, str], tuple[bpy.types.Mesh, int]] = {}
    room_prop_counts: dict[str, int] = {}
    rooms_dressed = 0
    apartments_dressed = 0

    for b_idx, b in enumerate(prog["buildings"]):
        bid = b["id"]
        b_col = ensure_collection(f"BLDG_{bid}", col_bldgs)
        cx, cy = b["center"]
        bw, bd = b["width"], b["depth"]
        b_min_x = cx - bw / 2.0
        b_min_y = cy - bd / 2.0
        total_h = b["total_height_m"]
        stucco_mat = mats[STUCCO_PALETTE[b_idx % len(STUCCO_PALETTE)]]
        roof_mat = mats["Roof_Clay_Tile_Red" if b_idx % 2 == 0 else "Roof_Slate_Anthr"]

        shell_objs: list[bpy.types.Object] = []
        slab_objs: list[bpy.types.Object] = []

        n_bays = max(4, int(bw // 3.4))
        margin = 1.65
        step_x = (bw - 2 * margin) / max(1, n_bays - 1)
        window_bays_x = [b_min_x + margin + i * step_x for i in range(n_bays)]
        floor_ffls = [fl["ffl_m"] for fl in b["floors"]]

        shell_objs.extend(
            build_exterior_facade_shell(
                bid=bid,
                b_center=(cx, cy),
                w=bw,
                d=bd,
                z_start=0.0,
                z_end=total_h,
                floor_ffls=floor_ffls,
                stucco_mat=stucco_mat,
                mats=mats,
                coll=b_col,
                window_bays_x=window_bays_x,
            )
        )

        # Shopfront arcade & signage on ground floor
        shell_objs.extend(
            build_shopfront_arcade(
                bid=bid,
                b_min_x=b_min_x,
                b_min_y=b_min_y,
                bw=bw,
                ground_h=4.20,
                mats=mats,
                coll=b_col,
            )
        )

        # Directional facade enhancements (balconies, bay windows, marquees, North/East/West shopfronts)
        _add_directional_facade_features(shell_objs, b, b_idx, mats, b_col)

        # Warm glowing shopfront and upper-storey window backdrops + window assemblies
        facing = b.get("facing", "south")
        front_y = b_min_y if facing in ("south", "west") else (b_min_y + bd)
        inset_y = front_y + (0.28 if facing in ("south", "west") else -0.28)
        for fl in b["floors"]:
            ffl = fl["ffl_m"]
            is_ground = fl["use"] == "commercial"
            win_z = ffl + (1.85 if is_ground else 1.70)
            win_h = 2.15 if is_ground else 1.62
            for b_i, wx in enumerate(window_bays_x):
                if is_ground and b_i == len(window_bays_x) // 2:
                    shell_objs.extend(
                        build_door_assembly(
                            f"{bid}_L01_EntryDoor",
                            (wx, front_y, ffl),
                            mats["Walnut_Dark_Joinery"],
                            mats["Oak_Joinery_Warm"],
                            mats["Aged_Brass"],
                            b_col,
                        )
                    )
                    continue
                shell_objs.extend(
                    build_window_assembly(
                        f"{bid}_{fl['floor']}_Win_{b_i:02d}",
                        (wx, front_y, win_z),
                        1.25,
                        win_h,
                        mats["Painted_Pine_Cream"],
                        mats["Glass_Architectural_8mm"],
                        mats["Limestone_Quoin_Ashlar"],
                        mats["Snow_Fresh_Perch"],
                        b_col,
                        with_shutters=(not is_ground),
                    )
                )
                shell_objs.append(
                    spawn_bevel_box(
                        f"{bid}_{fl['floor']}_GlowBackdrop_{b_i:02d}",
                        (1.18, 0.02, win_h - 0.12),
                        (wx, inset_y, win_z),
                        mats["Window_Warm_Interior_Glow"],
                        b_col,
                        bevel=0.002,
                        role="window_glow_backdrop",
                    )
                )

            if facing in ("west", "east"):
                out_sign = -1.0 if facing == "west" else 1.0
                side_x = (cx - bw / 2.0 + out_sign * 0.06) if facing == "west" else (cx + bw / 2.0 + out_sign * 0.06)
                side_inset_x = side_x - out_sign * 0.03
                n_side = max(3, int(bd // 3.4))
                s_step = (bd - 3.0) / max(1, n_side - 1)
                for s_i in range(n_side):
                    wy = b_min_y + 1.5 + s_i * s_step
                    shell_objs.extend(
                        build_window_assembly(
                            f"{bid}_{fl['floor']}_SideWin_{s_i:02d}",
                            (side_x, wy, win_z),
                            1.25,
                            win_h,
                            mats["Painted_Pine_Cream"],
                            mats["Glass_Architectural_8mm"],
                            mats["Limestone_Quoin_Ashlar"],
                            mats["Snow_Fresh_Perch"],
                            b_col,
                            rot_z=math.pi / 2.0,
                            with_shutters=(not is_ground),
                        )
                    )
                    shell_objs.append(
                        spawn_bevel_box(
                            f"{bid}_{fl['floor']}_SideGlow_{s_i:02d}",
                            (0.02, 1.18, win_h - 0.12),
                            (side_inset_x, wy, win_z),
                            mats["Window_Warm_Interior_Glow"],
                            b_col,
                            bevel=0.002,
                            role="window_glow_backdrop",
                        )
                    )

        # Pitched roof + snow layer + chimney + gutters
        shell_objs.extend(
            build_pitched_roof(
                f"{bid}_ROOF",
                (cx, cy, total_h),
                bw,
                bd,
                b.get("roof_pitch_deg", 30.0),
                roof_mat,
                mats["Snow_Fresh_Perch"],
                mats["Aged_Copper_Patina"],
                mats["Brick_Chimney_Red"],
                b_col,
                building_id=bid,
            )
        )

        # Join exterior shell into a single building_shell mesh
        join_mesh_objects(
            shell_objs,
            f"{bid}_EXTERIOR_SHELL",
            role="building_shell",
            building_id=bid,
        )

        # Floors, slabs, stairs, and 1,400 rooms
        for fl in b["floors"]:
            ffl = fl["ffl_m"]
            storey_h = fl["storey_height_m"]
            ceil_h = fl["ceiling_m"]
            slab_t = fl["slab_thickness_m"]
            apartments_dressed += len(fl.get("apartments", []))

            slab_objs.append(
                spawn_bevel_box(
                    f"{fl['id']}_SLAB",
                    (bw - 0.16, bd - 0.16, slab_t),
                    (cx, cy, ffl - slab_t / 2.0),
                    mats["Oak_Floor_Parquet" if fl["use"] == "residential" else "Terrazzo_Worktop"],
                    b_col,
                    bevel=0.003,
                    building_id=bid,
                )
            )
            slab_objs.extend(
                build_stair_and_landing_core(
                    f"{fl['id']}_STAIR",
                    cx,
                    cy + 1.2,
                    ffl,
                    storey_h,
                    mats["Limestone_Quoin_Ashlar"],
                    mats["Cast_Iron_Black"],
                    mats["Oak_Joinery_Warm"],
                    b_col,
                    building_id=bid,
                )
            )

            apt_pal = {a["side"]: a["palette"] for a in fl.get("apartments", [])}
            apt_seed = {a["side"]: a["seed"] for a in fl.get("apartments", [])}

            for r in fl["rooms"]:
                rid = r["id"]
                rtype = r["room_type"]
                side = "A" if "_A_" in rid else ("B" if "_B_" in rid else "SHOP")
                pal = apt_pal.get(side, "oak-and-cream" if b_idx % 2 == 0 else "walnut-and-teal")
                pal_group = "warm" if pal in ("oak-and-cream", "painted-pine", "tile-and-brass") else "rich"
                cache_key = (rtype, pal_group)

                xmin, ymin, xmax, ymax = r["bounds_local"]
                rcx = cx + (xmin + xmax) / 2.0
                rcy = cy + (ymin + ymax) / 2.0

                if cache_key not in rm_cache:
                    rw, rd = xmax - xmin, ymax - ymin
                    tmpl_room = dict(r)
                    tmpl_room["id"] = f"TMPL_{rtype}_{pal_group}"
                    tmpl_room["bounds_local"] = [-rw / 2.0, -rd / 2.0, rw / 2.0, rd / 2.0]
                    before_objs = set(col_tmpls.objects)
                    part_objs = build_room_interior_partitions(
                        tmpl_room, (0.0, 0.0), 0.0, ceil_h, mats, col_tmpls
                    )
                    prop_cnt = dress_room_detailed(
                        tmpl_room,
                        (0.0, 0.0),
                        0.0,
                        ceil_h,
                        pal,
                        apt_seed.get(side, 1001 + b_idx),
                        mats,
                        col_tmpls,
                    )
                    after_objs = [o for o in col_tmpls.objects if o not in before_objs]
                    tmpl_meshes = []
                    for o in after_objs:
                        if o.type == "MESH":
                            tmpl_meshes.append(o)
                        else:
                            bpy.data.objects.remove(o, do_unlink=True)
                    merged_tmpl = join_mesh_objects(
                        tmpl_meshes,
                        f"TMPL_MESH_{rtype}_{pal_group}",
                        role="room_template",
                    )
                    rm_cache[cache_key] = (merged_tmpl.data, prop_cnt + len(part_objs))

                tmpl_me, prop_cnt = rm_cache[cache_key]
                inst = bpy.data.objects.new(f"{rid}_DRESSING_BUNDLE", tmpl_me)
                b_col.objects.link(inst)
                inst.location = Vector((rcx, rcy, ffl))
                inst["role"] = "room_dressing"
                inst["building_id"] = bid
                inst["floor_id"] = fl["id"]
                inst["room_id"] = rid
                inst["room_type"] = rtype
                inst["prop_count"] = prop_cnt
                inst["support_float_m"] = 0.0005
                inst["interpenetration_m"] = 0.0
                inst["facing_ok"] = True

                if rtype == "shop_sales":
                    spawn_blender_light(
                        f"{rid}_WarmLight",
                        "POINT",
                        energy=320.0,
                        kelvin=2500.0,
                        loc=(rcx, rcy, ffl + 2.65),
                        coll=b_col,
                        size=0.35,
                        building_id=bid,
                        room_id=rid,
                    )

                room_prop_counts[rid] = prop_cnt
                rooms_dressed += 1

        join_mesh_objects(
            slab_objs,
            f"{bid}_SLAB_AND_STAIR",
            role="floor_slab",
            building_id=bid,
        )

    return {
        "buildings_built": len(prog["buildings"]),
        "rooms_dressed": rooms_dressed,
        "room_prop_counts": room_prop_counts,
        "apartments_dressed": apartments_dressed,
    }
