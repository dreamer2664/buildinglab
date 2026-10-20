#!/usr/bin/env python3
"""
Stage B — Vertical Slice Builder (`townsquare/scene/build_slice.py`).
Builds `townsquare/scene/slice_B02_L02.blend` containing:
- Building `B02` (Haus Winter, 5 storeys, ground-floor Bäckerei + L02 residential floor)
  with 15 m flanking context shells of `B01` and `B03` and >= 2.0 m freestanding alleys.
- Floor `B02_L02` with 2 distinct apartments (`B02_L02_A` and `B02_L02_B`), all 7 rooms each
  100% dressed (>=45 living, >=60 kitchen, >=25 bedroom, >=18 bathroom, >=12 entry props, >=40 tris each),
  with 0.10 m interior partition walls, doorways, skirting boards, and cornices.
- Ground-floor shop `B02_L01` (4 shop rooms: sales, counter, backroom, staff) with >= 80 props.
- 20 m^2 of tightly jointed cobbled square terrain (`8-12 mm` mortar joints) with wet slush channel,
  snow bank, footprints, bench, and 2 cast-iron street lamps (`2200 K`).
- 4 distinct licensed `HSRD-100` photogrammetry people (`HSR0015`, `HSR0027`, `HSR0023`, `HSR0028`)
  oriented with their faces toward the cameras.
- 12 camera setups matching the 12 mandatory Stage B views (§17).
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

ROOT = Path("/home/user/buildinglab")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from townsquare.kits.core import spawn_bevel_box
from townsquare.kits.materials.library import build_material_library
from townsquare.kits.walls.builder import (
    build_exterior_facade_shell,
    build_room_interior_partitions,
)
from townsquare.kits.openings.builder import (
    build_door_assembly,
    build_shopfront_arcade,
    build_window_assembly,
)
from townsquare.kits.roofs.builder import build_roof_and_drainage
from townsquare.kits.stairs.builder import build_stair_and_landing_core
from townsquare.kits.lighting.builder import (
    build_room_lighting,
    build_street_lamp,
    configure_world_and_color_management,
    spawn_blender_light,
)
from townsquare.kits.furniture.builder import dress_room_detailed
from townsquare.kits.people.builder import load_licensed_scan_person

PROG_PATH = ROOT / "townsquare/design/PROGRAMME.json"
BLEND_OUT = ROOT / "townsquare/scene/slice_B02_L02.blend"


def get_or_create_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def point_camera_at(cam_obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - cam_obj.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()


def build_cobbled_terrain_20m2(
    cx: float,
    y_front: float,
    mats: dict[str, bpy.types.Material],
    col: bpy.types.Collection,
) -> list[bpy.types.Object]:
    """
    Build tightly jointed cobbled street & sidewalk in front of B02 (`8-12 mm` mortar joints, fixes D-005).
    """
    objs = []
    objs.append(
        spawn_bevel_box(
            "Terrain_Roadbed_Base",
            (36.0, 22.0, 0.20),
            (cx, y_front - 10.5, -0.105),
            mats["Mortar_Joint_Wet"],
            col,
            bevel=0.004,
            role="terrain_base",
        )
    )
    objs.append(
        spawn_bevel_box(
            "Terrain_Sidewalk_Slab",
            (24.0, 1.80, 0.12),
            (cx, y_front - 0.90, 0.06),
            mats["Granite_Kerb_Weathered"],
            col,
            bevel=0.004,
            role="sidewalk_slab",
        )
    )
    for ki in range(18):
        kx = cx - 8.5 + ki * 1.0
        objs.append(
            spawn_bevel_box(
                f"Terrain_KerbStone_{ki:02d}",
                (0.985, 0.24, 0.14),
                (kx, y_front - 1.80, 0.07),
                mats["Limestone_Quoin_Ashlar"],
                col,
                bevel=0.004,
                role="kerb_stone",
            )
        )
    for gi in range(6):
        objs.append(
            spawn_bevel_box(
                f"Terrain_DrainGrate_{gi}",
                (0.48, 0.32, 0.025),
                (cx - 2.2 + gi * 0.90, y_front - 2.02, 0.012),
                mats["Cast_Iron_Black"],
                col,
                bevel=0.002,
                role="drain_grate",
            )
        )

    # Tightly jointed cobblestone field: 108 mm stone on 118 mm pitch = 10 mm mortar joint (fixes D-005)
    cobble_mats = [
        mats["Cobble_Granite_Dark"],
        mats["Cobble_Granite_Warm"],
        mats["Cobble_Granite_Grey"],
        mats["Cobble_Porphyry_Red"],
    ]
    pitch_x, pitch_y = 0.118, 0.118
    stone_w, stone_d = 0.108, 0.108
    for row in range(26):
        ry = y_front - 1.96 - row * pitch_y
        row_stagger = (row % 2) * (pitch_x * 0.5)
        for col_i in range(46):
            rx = cx - 2.70 + col_i * pitch_x + row_stagger
            arch = math.sin((col_i / 6.0) * math.pi) * 0.018
            rz = 0.014 + ((row * 13 + col_i * 7) % 5) * 0.0012
            cmat = cobble_mats[(row * 5 + col_i * 3) % len(cobble_mats)]
            objs.append(
                spawn_bevel_box(
                    f"Terrain_Cobble_{row:02d}_{col_i:02d}",
                    (stone_w, stone_d, 0.036),
                    (rx, ry + arch, rz),
                    cmat,
                    col,
                    rot_z=math.sin(col_i * 0.45) * 0.08,
                    bevel=0.004,
                    role="cobblestone",
                )
            )

    for pi in range(8):
        px = cx - 2.2 + pi * 0.62
        objs.append(
            spawn_bevel_box(
                f"Terrain_SlushPuddle_{pi}",
                (0.58, 0.46, 0.014),
                (px, y_front - 2.25 - (pi % 2) * 0.18, 0.024),
                mats["Puddle_Water_Film"],
                col,
                rot_z=pi * 0.25,
                bevel=0.003,
                role="slush_puddle",
            )
        )

    for si in range(12):
        sx = cx - 4.8 + si * 0.88
        objs.append(
            spawn_bevel_box(
                f"Terrain_SnowBank_Plinth_{si}",
                (0.84, 0.34, 0.065 + (si % 3) * 0.015),
                (sx, y_front - 0.22, 0.14),
                mats["Snow_Fresh_Perch"],
                col,
                bevel=0.006,
                role="snow_bank",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"Terrain_SnowBank_Kerb_{si}",
                (0.78, 0.30, 0.048),
                (sx + 0.10, y_front - 1.84, 0.032),
                mats["Snow_Slush_Trampled"],
                col,
                bevel=0.005,
                role="snow_bank_kerb",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"Terrain_BootPrint_{si}",
                (0.12, 0.28, 0.018),
                (sx + 0.15, y_front - 1.05 - (si % 2) * 0.22, 0.128),
                mats["Puddle_Water_Film"],
                col,
                rot_z=0.14 if si % 2 == 0 else -0.10,
                bevel=0.002,
                role="boot_footprint",
            )
        )

    bx, by, bz = cx - 3.6, y_front - 1.25, 0.12
    for sl_i in range(5):
        objs.append(
            spawn_bevel_box(
                f"PublicBench_SeatSlat_{sl_i}",
                (1.80, 0.08, 0.032),
                (bx, by - 0.18 + sl_i * 0.09, bz + 0.45),
                mats["Walnut_Dark_Joinery"],
                col,
                bevel=0.002,
                role="public_bench",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"PublicBench_BackSlat_{sl_i}",
                (1.80, 0.032, 0.075),
                (bx, by + 0.22, bz + 0.52 + sl_i * 0.085),
                mats["Walnut_Dark_Joinery"],
                col,
                bevel=0.002,
                role="public_bench",
            )
        )
    for arm_i, ax in enumerate((bx - 0.82, bx, bx + 0.82)):
        objs.append(
            spawn_bevel_box(
                f"PublicBench_CastIronFrame_{arm_i}",
                (0.055, 0.52, 0.62),
                (ax, by, bz + 0.31),
                mats["Cast_Iron_Black"],
                col,
                bevel=0.002,
                role="public_bench_arm",
            )
        )
    objs.append(
        spawn_bevel_box(
            "PublicBench_SnowCrest",
            (1.76, 0.06, 0.032),
            (bx, by + 0.22, bz + 0.90),
            mats["Snow_Fresh_Perch"],
            col,
            bevel=0.003,
            role="snow_perch",
        )
    )
    return objs


def setup_slice_cameras(
    b02: dict,
    col_cam: bpy.types.Collection,
) -> list[dict]:
    cx, cy = b02["center"]
    bw, bd = b02["width"], b02["depth"]
    b_min_x = cx - bw / 2.0
    cy_front = cy - bd / 2.0
    z_l02 = 4.20

    cam_specs = [
        {
            "view_id": "slice_01_ext_blue_hour",
            "category": "slice_exterior",
            "preset": "blue_hour",
            "lens": 26.0,
            "loc": (cx - 1.2, cy_front - 22.0, 2.30),
            "target": (cx, cy_front, 7.20),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_02_ext_day",
            "category": "slice_exterior",
            "preset": "overcast",
            "lens": 26.0,
            "loc": (cx + 1.8, cy_front - 22.0, 2.30),
            "target": (cx, cy_front, 7.20),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_03_cutaway_L02",
            "category": "slice_cutaway",
            "preset": "overcast",
            "lens": 35.0,
            "loc": (cx - 8.5, cy - 13.5, z_l02 + 12.0),
            "target": (cx, cy, z_l02 + 1.1),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_04_int_B02_L02_A",
            "category": "slice_interior",
            "preset": "blue_hour",
            "lens": 22.0,
            "loc": (-1.05, 26.65, z_l02 + 1.42),
            "target": (-3.05, 29.15, z_l02 + 0.92),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_05_int_B02_L02_B",
            "category": "slice_interior",
            "preset": "blue_hour",
            "lens": 22.0,
            "loc": (7.05, 26.65, z_l02 + 1.42),
            "target": (5.05, 29.10, z_l02 + 0.92),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_06_shop_bakery",
            "category": "slice_shop",
            "preset": "blue_hour",
            "lens": 24.0,
            "loc": (-4.60, 27.10, 1.52),
            "target": (-0.20, 30.10, 1.05),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_07_human_daylight_close",
            "category": "slice_human",
            "preset": "overcast",
            "lens": 55.0,
            "loc": (cx - 1.20, cy_front - 3.45, 1.48),
            "target": (cx - 1.20, cy_front - 2.15, 1.40),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_08_human_bakery_warm",
            "category": "slice_human",
            "preset": "blue_hour",
            "lens": 52.0,
            "loc": (cx + 1.38, cy_front - 2.40, 1.60),
            "target": (cx + 1.60, cy_front - 0.95, 1.56),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_09_terrain_cobbles_slush",
            "category": "slice_terrain",
            "preset": "blue_hour",
            "lens": 38.0,
            "loc": (cx - 1.60, cy_front - 3.45, 0.72),
            "target": (cx + 0.20, cy_front - 2.15, 0.04),
            "ortho_scale": None,
        },
        {
            "view_id": "slice_10_plan_B02_L02",
            "category": "slice_plan",
            "preset": "overcast",
            "lens": 50.0,
            "loc": (cx, cy, z_l02 + 18.0),
            "target": (cx, cy, z_l02 + 0.5),
            "ortho_scale": 17.5,
        },
        {
            "view_id": "slice_11_technical_facade",
            "category": "slice_technical",
            "preset": "overcast",
            "lens": 50.0,
            "loc": (cx, cy_front - 22.0, 9.5),
            "target": (cx, cy_front, 9.5),
            "ortho_scale": 24.0,
        },
        {
            "view_id": "slice_12_ext_night",
            "category": "slice_exterior",
            "preset": "night",
            "lens": 26.0,
            "loc": (cx - 1.2, cy_front - 22.0, 2.30),
            "target": (cx, cy_front, 7.20),
            "ortho_scale": None,
        },
    ]

    for spec in cam_specs:
        cdata = bpy.data.cameras.new(spec["view_id"])
        if spec["ortho_scale"] is not None:
            cdata.type = "ORTHO"
            cdata.ortho_scale = spec["ortho_scale"]
        else:
            cdata.type = "PERSP"
            cdata.lens = spec["lens"]
        cdata.clip_start = 0.05
        cdata.clip_end = 250.0
        cobj = bpy.data.objects.new(spec["view_id"], cdata)
        col_cam.objects.link(cobj)
        cobj.location = Vector(spec["loc"])
        point_camera_at(cobj, spec["target"])
        cobj["view_id"] = spec["view_id"]
        cobj["category"] = spec["category"]
        cobj["preset"] = spec["preset"]
    return cam_specs


def main() -> int:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    prog = json.loads(PROG_PATH.read_text())
    b02 = next(b for b in prog["buildings"] if b["id"] == "B02")
    b01 = next(b for b in prog["buildings"] if b["id"] == "B01")
    b03 = next(b for b in prog["buildings"] if b["id"] == "B03")

    mats = build_material_library()

    col_env = get_or_create_collection("00_Environment")
    col_b02 = get_or_create_collection("01_B02_Architecture")
    col_b02_roof = get_or_create_collection("01_B02_UpperAndRoof")
    col_l01 = get_or_create_collection("02_B02_L01_Bakery")
    col_l02 = get_or_create_collection("03_B02_L02_Apartments")
    col_adj = get_or_create_collection("04_Adjacent_B01_B03")
    col_ter = get_or_create_collection("05_Terrain_20m2")
    col_ppl = get_or_create_collection("06_People")
    col_cam = get_or_create_collection("07_Cameras")

    cx, cy = b02["center"]
    bw, bd = b02["width"], b02["depth"]
    b_min_x = cx - bw / 2.0
    b_min_y = cy - bd / 2.0
    cy_front = b_min_y

    floor_ffls = [fl["ffl_m"] for fl in b02["floors"]]
    total_h = b02["total_height_m"]
    ground_h = 4.20
    window_bays_x = [b_min_x + 2.0, b_min_x + 5.0, cx, b_min_x + bw - 5.0, b_min_x + bw - 2.0]

    # 1. Build B02 exterior shell: L01-L02 in col_b02, L03-L05 + roof in col_b02_roof (so cutaway/plan views can hide upper floors cleanly)
    build_exterior_facade_shell(
        "B02",
        (cx, cy),
        bw,
        bd,
        0.0,
        7.40,
        floor_ffls[:2],
        mats["Plaster_Warm_Ochre"],
        mats,
        col_b02,
        window_bays_x,
    )
    build_exterior_facade_shell(
        "B02_Upper",
        (cx, cy),
        bw,
        bd,
        7.40,
        total_h,
        floor_ffls[2:],
        mats["Plaster_Warm_Ochre"],
        mats,
        col_b02_roof,
        window_bays_x,
    )
    build_roof_and_drainage(
        "B02",
        cx,
        cy,
        total_h,
        bw,
        bd,
        b02["roof_pitch_deg"],
        mats["Roof_Slate_Dark"],
        mats["Copper_Gutter_Aged"],
        mats["Snow_Fresh_Perch"],
        col_b02_roof,
        building_id="B02",
    )

    # 2. Build Windows, Shutters, Shopfront Arcade & Upper-Floor Warm Emitters
    build_shopfront_arcade("B02", b_min_x, b_min_y, bw, ground_h, mats, col_b02)
    for fl in b02["floors"]:
        fidx = fl["level_index"]
        z0 = fl["ffl_m"]
        target_col = col_b02 if fidx <= 1 else col_b02_roof
        spawn_bevel_box(
            f"{fl['id']}_StructuralSlab",
            (bw, bd, fl["slab_thickness_m"]),
            (cx, cy, z0 - fl["slab_thickness_m"] / 2.0),
            mats["Plaster_Interior_Warm"],
            target_col,
            bevel=0.003,
            floor_id=fl["id"],
        )
        for b_i, bx in enumerate(window_bays_x):
            if fidx == 0 and b_i == 2:
                build_door_assembly(
                    "B02_L01_ShopEntryDoor",
                    (bx, b_min_y + 0.19, 0.0),
                    mats["Painted_Pine_Teal"],
                    mats["Walnut_Dark_Joinery"],
                    mats["Aged_Brass"],
                    col_b02,
                    width=1.20,
                    height=2.45,
                    building_id="B02",
                )
                continue
            win_h = 2.25 if fidx == 0 else 1.65
            sill_z = 0.65 if fidx == 0 else 0.88
            build_window_assembly(
                f"B02_L{fidx+1:02d}_W{b_i:02d}",
                (bx, b_min_y + 0.19, z0 + sill_z + win_h / 2.0),
                1.25,
                win_h,
                mats["Painted_Pine_Teal"] if fidx == 0 else mats["Painted_Pine_Cream"],
                mats["Architectural_Glass"],
                mats["Limestone_Quoin_Ashlar"],
                mats["Snow_Fresh_Perch"],
                target_col,
                with_shutters=(fidx >= 1),
                building_id="B02",
                floor_id=fl["id"],
            )
            if fidx >= 2:
                spawn_bevel_box(
                    f"B02_L{fidx+1:02d}_WinGlowPanel_{b_i:02d}",
                    (1.16, 0.04, 1.50),
                    (bx, b_min_y + 0.58, z0 + sill_z + win_h / 2.0),
                    mats["Emitter_Warm_2700K"] if (fidx + b_i) % 3 != 0 else mats["Curtain_Drape_Warm"],
                    target_col,
                    bevel=0.002,
                    building_id="B02",
                )
                if (fidx + b_i) % 3 != 0:
                    spawn_blender_light(
                        f"B02_L{fidx+1:02d}_WinLight_{b_i:02d}",
                        "POINT",
                        energy=115.0,
                        kelvin=2650.0,
                        loc=(bx, b_min_y + 0.42, z0 + 1.70),
                        coll=target_col,
                        size=0.35,
                        clear_rays=8,
                    )

    # 3. Build Central Stair Flights & Landings for L01 -> L02 -> L03
    fl_l01 = b02["floors"][0]
    fl_l02 = b02["floors"][1]
    stair_room_l02 = next(r for r in fl_l02["rooms"] if r["room_type"] == "landing")
    sxmin, symin, sxmax, symax = stair_room_l02["bounds_local"]
    scx = cx + (sxmin + sxmax) / 2.0
    scy = cy + (symin + symax) / 2.0
    build_stair_and_landing_core(
        "B02_Stair_L01_L02",
        scx,
        scy,
        0.0,
        4.20,
        mats["Limestone_Quoin_Ashlar"],
        mats["Cast_Iron_Black"],
        mats["Walnut_Dark_Joinery"],
        col_b02,
        building_id="B02",
    )
    build_stair_and_landing_core(
        "B02_Stair_L02_L03",
        scx,
        scy,
        4.20,
        3.20,
        mats["Limestone_Quoin_Ashlar"],
        mats["Cast_Iron_Black"],
        mats["Walnut_Dark_Joinery"],
        col_b02_roof,
        building_id="B02",
    )
    build_room_interior_partitions(stair_room_l02, (cx, cy), 4.20, 2.70, mats, col_l02)
    build_room_lighting(
        stair_room_l02["id"],
        scx,
        scy,
        4.20,
        2.70,
        sxmax - sxmin,
        symax - symin,
        mats["Aged_Brass"],
        mats["Emitter_Warm_2700K"],
        col_l02,
        building_id="B02",
    )

    # 4. Dress All 14 Apartment Rooms on B02_L02 (7 rooms in B02_L02_A + 7 rooms in B02_L02_B)
    for room in fl_l02["rooms"]:
        if room["room_type"] == "landing":
            continue
        build_room_interior_partitions(room, (cx, cy), 4.20, 2.70, mats, col_l02)
        apt_id = room["apartment"]
        pal = "oak-and-cream" if apt_id.endswith("_A") else "walnut-and-teal"
        seed = 101 if apt_id.endswith("_A") else 202
        dress_room_detailed(room, (cx, cy), 4.20, 2.70, pal, seed, mats, col_l02)

    # 5. Dress All 4 Shop Rooms on B02_L01 (`Haus Winter` Bakery)
    for room in fl_l01["rooms"]:
        build_room_interior_partitions(room, (cx, cy), 0.0, 3.60, mats, col_l01)
        dress_room_detailed(room, (cx, cy), 0.0, 3.60, "painted-pine", 303, mats, col_l01)

    # 6. Build Flanking Context Facades (`B01` and `B03`) with >= 2.0 m freestanding gaps
    for adj_b, stucco_key in ((b01, "Plaster_Rose_Stone"), (b03, "Plaster_Sage_Green")):
        acx, acy = adj_b["center"]
        aw, ad = adj_b["width"], adj_b["depth"]
        ah = adj_b["total_height_m"]
        amin_x = acx - aw / 2.0
        amin_y = acy - ad / 2.0
        af_ffls = [fl["ffl_m"] for fl in adj_b["floors"]]
        abays = [amin_x + 2.2, amin_x + 5.5, acx, amin_x + aw - 5.5, amin_x + aw - 2.2]
        build_exterior_facade_shell(
            adj_b["id"],
            (acx, acy),
            aw,
            ad,
            0.0,
            ah,
            af_ffls,
            mats[stucco_key],
            mats,
            col_adj,
            abays,
        )
        build_roof_and_drainage(
            adj_b["id"],
            acx,
            acy,
            ah,
            aw,
            ad,
            adj_b["roof_pitch_deg"],
            mats["Roof_Clay_Tile"],
            mats["Copper_Gutter_Aged"],
            mats["Snow_Fresh_Perch"],
            col_adj,
            building_id=adj_b["id"],
        )
        for afl in adj_b["floors"][1:]:
            az0 = afl["ffl_m"]
            for bi, abx in enumerate(abays):
                build_window_assembly(
                    f"{adj_b['id']}_L{afl['level_index']+1:02d}_W{bi}",
                    (abx, amin_y + 0.19, az0 + 1.70),
                    1.20,
                    1.60,
                    mats["Painted_Pine_Cream"],
                    mats["Architectural_Glass"],
                    mats["Limestone_Quoin_Ashlar"],
                    mats["Snow_Fresh_Perch"],
                    col_adj,
                    with_shutters=True,
                )
                spawn_bevel_box(
                    f"{adj_b['id']}_L{afl['level_index']+1:02d}_Glow_{bi}",
                    (1.12, 0.04, 1.48),
                    (abx, amin_y + 0.55, az0 + 1.70),
                    mats["Emitter_Warm_2700K"],
                    col_adj,
                    bevel=0.002,
                )

    # 7. Build 20 m^2 Cobbled Square Terrain, Slush Channel, Bench & 2 Street Lamps
    build_cobbled_terrain_20m2(cx, cy_front, mats, col_ter)
    build_street_lamp(
        "LAMP_B02_W",
        b_min_x + 1.2,
        cy_front - 1.55,
        0.12,
        mats["Cast_Iron_Black"],
        mats["Architectural_Glass"],
        mats["Emitter_Festive_2400K"],
        mats["Snow_Fresh_Perch"],
        col_ter,
    )
    build_street_lamp(
        "LAMP_B02_E",
        b_min_x + bw - 1.2,
        cy_front - 1.55,
        0.12,
        mats["Cast_Iron_Black"],
        mats["Architectural_Glass"],
        mats["Emitter_Festive_2400K"],
        mats["Snow_Fresh_Perch"],
        col_ter,
    )

    # 8. Place 4 Distinct Licensed HSRD-100 Photogrammetry People (§17, §19)
    # Fixes D-002: HSRD-100 scans face +Y at rot_z=0, so rot_z=math.pi faces -Y (directly toward cameras at smaller Y).
    load_licensed_scan_person(
        "HUMAN_01_HERO_DAYLIGHT",
        "HSR0015-Body-009",
        "ID_01_HSR0015",
        (cx - 1.20, cy_front - 2.15, 0.015),
        rot_z=math.pi - 0.12,
        coll=col_ppl,
        wardrobe_palette="winter_coat_A",
        location_zone="outdoor_square",
    )
    load_licensed_scan_person(
        "HUMAN_02_HERO_BAKERY",
        "HSR0027-Body-004",
        "ID_03_HSR0027",
        (cx + 1.60, cy_front - 0.95, 0.125),
        rot_z=math.pi + 0.10,
        coll=col_ppl,
        wardrobe_palette="winter_coat_B",
        location_zone="bakery_arcade",
    )
    load_licensed_scan_person(
        "HUMAN_03_APT_A_RESIDENT",
        "HSR0023-Body-017",
        "ID_02_HSR0023",
        (-1.55, 28.05, 4.225),
        rot_z=math.pi + 0.55,
        coll=col_ppl,
        building_id="B02",
        room_id="B02_L02_A_living",
        wardrobe_palette="indoor_knit_C",
    )
    load_licensed_scan_person(
        "HUMAN_04_APT_B_RESIDENT",
        "HSR0028-Body-010",
        "ID_04_HSR0028",
        (6.45, 28.05, 4.225),
        rot_z=math.pi + 0.55,
        coll=col_ppl,
        building_id="B02",
        room_id="B02_L02_B_living",
        wardrobe_palette="indoor_knit_D",
    )

    # 9. Outdoor Sun + Twilight Sky Fill + Portrait & Cobble Fill Lights
    sun_data = bpy.data.lights.new(name="Sun_Key", type="SUN")
    sun_data.energy = 1.35
    sun_data.angle = math.radians(11.0)
    sun_obj = bpy.data.objects.new(name="Sun_Key", object_data=sun_data)
    col_env.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(68.0), math.radians(15.0), math.radians(32.0))
    sun_obj["clear_rays"] = 8

    spawn_blender_light(
        "SkyBounce_FacadeFill",
        "AREA",
        energy=1250.0,
        kelvin=6500.0,
        loc=(cx, cy_front - 14.0, 11.0),
        coll=col_env,
        size=16.0,
        rot_euler=(math.radians(72.0), 0.0, 0.0),
        clear_rays=8,
    )
    spawn_blender_light(
        "Bakery_Arcade_WarmSpill",
        "AREA",
        energy=220.0,
        kelvin=2650.0,
        loc=(cx + 1.60, cy_front - 1.75, 2.05),
        coll=col_env,
        size=1.80,
        rot_euler=(math.radians(-35.0), 0.0, 0.0),
        clear_rays=8,
    )
    spawn_blender_light(
        "AptA_Living_Fill",
        "AREA",
        energy=180.0,
        kelvin=2750.0,
        loc=(-2.65, 27.80, 6.65),
        coll=col_l02,
        size=2.20,
        clear_rays=8,
    )
    spawn_blender_light(
        "AptB_Living_Fill",
        "AREA",
        energy=180.0,
        kelvin=2750.0,
        loc=(5.65, 27.80, 6.65),
        coll=col_l02,
        size=2.20,
        clear_rays=8,
    )
    spawn_blender_light(
        "Bakery_Sales_WarmFill",
        "AREA",
        energy=320.0,
        kelvin=2700.0,
        loc=(-1.50, 29.20, 3.35),
        coll=col_l01,
        size=3.50,
        clear_rays=8,
    )
    spawn_blender_light(
        "Square_Foreground_Fill",
        "AREA",
        energy=180.0,
        kelvin=5400.0,
        loc=(cx - 1.20, cy_front - 3.80, 2.20),
        coll=col_env,
        size=2.20,
        rot_euler=(math.radians(45.0), 0.0, 0.0),
        clear_rays=8,
    )

    configure_world_and_color_management(scene, preset="blue_hour")

    # 10. Setup 12 Stage B Cameras
    cam_specs = setup_slice_cameras(b02, col_cam)
    scene.camera = bpy.data.objects.get("slice_01_ext_blue_hour")

    try:
        bpy.ops.file.pack_all()
    except Exception as exc:
        print(f"pack_all note: {exc}")

    BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))

    mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
    total_tris = sum(int(o.get("tri_count", 0)) for o in mesh_objs)
    apt_a_props = [o for o in mesh_objs if o.get("home") == "B02_L02_A" and o.get("role") == "prop"]
    apt_b_props = [o for o in mesh_objs if o.get("home") == "B02_L02_B" and o.get("role") == "prop"]
    shop_props = [o for o in mesh_objs if o.get("home") == "SHOP" and o.get("role") == "prop"]

    sha = hashlib.sha256(BLEND_OUT.read_bytes()).hexdigest()
    slice_views = [
        {
            "id": s["view_id"],
            "lighting": s["preset"],
            "location": list(s["loc"]),
            "target": list(s["target"]),
            "resolution": [3840, 2160] if s["view_id"] in ("slice_01_ext_blue_hour", "slice_04_int_B02_L02_A", "slice_07_human_daylight_close", "slice_09_terrain_cobbles_slush") else [2560, 1440],
        }
        for s in cam_specs
    ]
    summary = {
        "blend_path": str(BLEND_OUT),
        "blend_sha256": sha,
        "native_sha256": sha,
        "mesh_objects": len(mesh_objs),
        "total_triangles": total_tris,
        "apt_A_props": len(apt_a_props),
        "apt_B_props": len(apt_b_props),
        "shop_props": len(shop_props),
        "cameras": len([o for o in bpy.data.objects if o.type == "CAMERA"]),
        "lights": len([o for o in bpy.data.objects if o.type == "LIGHT"]),
        "slice_views": slice_views,
    }
    (ROOT / "townsquare/evidence/validation/stage_b_slice_build.json").write_text(json.dumps(summary, indent=2))
    print(f"STAGE_B_SLICE_BUILT objects={len(mesh_objs)} tris={total_tris} aptA_props={len(apt_a_props)} aptB_props={len(apt_b_props)} shop_props={len(shop_props)} sha={sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
