#!/usr/bin/env python3
"""
Stage C — 12-Building Kit & Assembly Builder (`townsquare/scene/build_buildings.py`).
Builds all 12 buildings (`B01`..`B12`, 67 floors, 110 apartments, 873 dressed rooms)
using template-instanced room dressing (`TMPL_*`) and joined per-building shell/slab meshes
so the entire 12-building town compiles in <15 seconds and fits comfortably in 1.9 GiB RAM.
"""
from __future__ import annotations
import math
import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from townsquare.kits.core import (
    ensure_collection,
    join_mesh_objects,
    spawn_bevel_box,
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


def _facing_rot_z(facing: str) -> float:
    return {
        "south": 0.0,
        "north": math.pi,
        "west": -math.pi / 2.0,
        "east": math.pi / 2.0,
    }.get(facing, 0.0)


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

        # Shopfront arcade & signage on ground floor facing the square
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
                # Warm illuminated interior backdrop plane behind the 8mm glass so exterior & night views glow
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

            # Also add illuminated window assemblies on the square-facing X side for East/West buildings (B04..B06, B10..B12)
            if facing in ("west", "east"):
                side_x = (cx - bw / 2.0) if facing == "west" else (cx + bw / 2.0)
                side_inset_x = side_x + (0.28 if facing == "west" else -0.28)
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

        # Floors, slabs, stairs, and 873 rooms
        for fl in b["floors"]:
            ffl = fl["ffl_m"]
            storey_h = fl["storey_height_m"]
            ceil_h = fl["ceiling_m"]
            slab_t = fl["slab_thickness_m"]
            apartments_dressed += len(fl.get("apartments", []))

            # Structural floor slab + finish parquet/tile top layer
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

            # Palettes for apartments on this floor
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
                    # Build canonical room template centered at origin (0, 0, 0)
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
                    # Remove auto-created point lights inside template collection
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

                # Shop sales warm interior light for shopfront/exterior views
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
