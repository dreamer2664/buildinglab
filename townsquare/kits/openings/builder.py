from __future__ import annotations
import math
from townsquare.kits.core import spawn_bevel_box
import bpy  # type: ignore

def build_window_assembly(name, loc, width, height, mat_frame, mat_glass, mat_stone, mat_snow, coll, rot_z=0.0, with_shutters=True, **tags):
    objs = []
    cx, cy, cz = loc
    ca, sa = math.cos(rot_z), math.sin(rot_z)
    def off(dx, dy, dz):
        return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca, cz + dz)

    # Stone sill (projecting 60mm) + snow perch on sill (35mm thick, §16)
    objs.append(spawn_bevel_box(f"{name}_SILL", (width + 0.16, 0.24, 0.09), off(0, -0.06, -height/2 - 0.045), mat_stone, coll, rot_z=rot_z, bevel=0.004, role="window_sill", family="window", **tags))
    objs.append(spawn_bevel_box(f"{name}_SILL_SNOW", (width + 0.12, 0.18, 0.035), off(0, -0.07, -height/2 + 0.015), mat_snow, coll, rot_z=rot_z, bevel=0.008, role="snow_perch", family="snow", **tags))
    # Outer frame & central mullion + transom
    objs.append(spawn_bevel_box(f"{name}_FRAME_TOP", (width, 0.12, 0.07), off(0, 0, height/2 - 0.035), mat_frame, coll, rot_z=rot_z, role="window_frame", family="window", **tags))
    objs.append(spawn_bevel_box(f"{name}_MULLION", (0.06, 0.10, height - 0.08), off(0, 0, 0), mat_frame, coll, rot_z=rot_z, role="window_mullion", family="window", **tags))
    objs.append(spawn_bevel_box(f"{name}_TRANSOM", (width - 0.08, 0.09, 0.05), off(0, 0, height * 0.12), mat_frame, coll, rot_z=rot_z, role="window_transom", family="window", **tags))
    # Real 8mm thick glass pane (no zero-thickness plane, §18 rule 9)
    objs.append(spawn_bevel_box(f"{name}_GLASS", (width - 0.10, 0.008, height - 0.10), off(0, 0.01, 0), mat_glass, coll, rot_z=rot_z, bevel=0.001, role="window_glass", family="window", **tags))
    if with_shutters:
        for side_s, sx in (("L", -width/2 - 0.24), ("R", width/2 + 0.24)):
            objs.append(spawn_bevel_box(f"{name}_SHUTTER_{side_s}", (0.42, 0.04, height - 0.04), off(sx, -0.05, 0), mat_frame, coll, rot_z=rot_z, bevel=0.003, role="shutter", family="window", **tags))
    return objs

def build_door_assembly(name, loc, mat_frame, mat_leaf, mat_metal, coll, rot_z=0.0, width=0.90, height=2.10, **tags):
    cx, cy, cz = loc
    ca, sa = math.cos(rot_z), math.sin(rot_z)
    def off(dx, dy, dz):
        return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca, cz + dz)
    objs = [
        spawn_bevel_box(f"{name}_FRAME", (width + 0.12, 0.16, height + 0.06), off(0, 0, height/2), mat_frame, coll, rot_z=rot_z, role="door_frame", family="door", **tags),
        spawn_bevel_box(f"{name}_LEAF", (width - 0.02, 0.045, height - 0.02), off(0, 0.01, height/2), mat_leaf, coll, rot_z=rot_z, role="door_leaf", family="door", **tags),
        spawn_bevel_box(f"{name}_HANDLE_F", (0.14, 0.06, 0.03), off(width * 0.36, -0.04, 1.02), mat_metal, coll, rot_z=rot_z, role="door_handle", family="door", **tags),
        spawn_bevel_box(f"{name}_HANDLE_B", (0.14, 0.06, 0.03), off(width * 0.36, 0.06, 1.02), mat_metal, coll, rot_z=rot_z, role="door_handle", family="door", **tags),
    ]
    return objs


def build_shopfront_arcade(
    bid: str,
    b_min_x: float,
    b_min_y: float,
    bw: float,
    ground_h: float,
    mats: dict,
    coll,
) -> list:
    objs = []
    cx = b_min_x + bw / 2.0
    sy = b_min_y + 0.16
    objs.append(
        spawn_bevel_box(
            f"{bid}_ShopFascia",
            (bw - 1.2, 0.18, 0.42),
            (cx, sy - 0.14, 3.25),
            mats["Painted_Pine_Teal"],
            coll,
            bevel=0.003,
            building_id=bid,
            role="shop_fascia",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{bid}_ShopSignPlaque",
            (4.2, 0.05, 0.28),
            (cx, sy - 0.24, 3.25),
            mats["Gold_Sign_Leaf"],
            coll,
            bevel=0.002,
            building_id=bid,
            role="shop_sign",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{bid}_GuildBracket",
            (0.06, 0.85, 0.06),
            (b_min_x + 2.2, sy - 0.50, 3.45),
            mats["Cast_Iron_Black"],
            coll,
            bevel=0.002,
            building_id=bid,
            role="guild_sign_bracket",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{bid}_GuildEmblem",
            (0.04, 0.48, 0.48),
            (b_min_x + 2.2, sy - 0.65, 3.12),
            mats["Gold_Sign_Leaf"],
            coll,
            bevel=0.003,
            building_id=bid,
            role="guild_sign_emblem",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{bid}_ShopAwning",
            (bw - 1.6, 0.95, 0.12),
            (cx, sy - 0.52, 2.95),
            mats["Fabric_Canvas_Awning"],
            coll,
            bevel=0.004,
            building_id=bid,
            role="shop_awning",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{bid}_ShopAwningSnow",
            (bw - 1.68, 0.88, 0.035),
            (cx, sy - 0.52, 3.03),
            mats["Snow_Fresh_Perch"],
            coll,
            bevel=0.005,
            building_id=bid,
            role="snow_perch",
        )
    )
    return objs
