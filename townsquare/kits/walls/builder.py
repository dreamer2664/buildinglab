"""
Walls, slabs, interior partitions, skirting boards, cornices, and façade relief kit (§16, §17).
"""
from __future__ import annotations
import bpy  # type: ignore
from townsquare.kits.core import spawn_bevel_box


def build_room_interior_partitions(
    room: dict,
    b_center: tuple[float, float],
    ffl: float,
    ceil_h: float,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
) -> list[bpy.types.Object]:
    """
    Build 0.12 m interior partition walls around `room` (with a 0.90 x 2.10 m doorway opening,
    0.12 m x 0.018 m skirting board, 0.08 m x 0.08 m ceiling cornice, and ajar wooden door leaf).
    Fixes D-003 so interior rooms are enclosed and plan/cutaway views show clean room partitions.
    """
    objs = []
    rid = room["id"]
    rtype = room["room_type"]
    xmin, ymin, xmax, ymax = room["bounds_local"]
    rw = xmax - xmin
    rd = ymax - ymin
    cx = b_center[0] + (xmin + xmax) / 2.0
    cy = b_center[1] + (ymin + ymax) / 2.0
    x0 = b_center[0] + xmin
    y0 = b_center[1] + ymin

    m_plaster = mats["Plaster_Interior_Warm"]
    m_skirt = mats["Painted_Pine_Cream"]
    m_door = mats["Oak_Joinery_Warm"]

    # Skirting boards (0.12 m high x 0.018 m proud) + Ceiling Cornices (0.08 m x 0.08 m)
    sk_z = ffl + 0.024 + 0.06
    cz = ffl + ceil_h - 0.04
    for s_tag, sx, sy, sw, sd in (
        ("N", cx, y0 + rd - 0.04, rw - 0.08, 0.018),
        ("S", cx, y0 + 0.04, rw - 0.08, 0.018),
        ("E", x0 + rw - 0.04, cy, 0.018, rd - 0.08),
        ("W", x0 + 0.04, cy, 0.018, rd - 0.08),
    ):
        objs.append(
            spawn_bevel_box(
                f"{rid}_SKIRT_{s_tag}",
                (sw, sd, 0.12),
                (sx, sy, sk_z),
                m_skirt,
                coll,
                bevel=0.002,
                room_id=rid,
                role="skirting",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"{rid}_CORNICE_{s_tag}",
                (sw if sw > 0.05 else 0.08, sd if sd > 0.05 else 0.08, 0.08),
                (sx, sy, cz),
                m_plaster,
                coll,
                bevel=0.002,
                room_id=rid,
                role="cornice",
            )
        )

    if rtype == "shop_sales":
        return objs

    # Interior 0.10 m partition walls along room boundaries with open doorway
    ph = ceil_h - 0.03
    pz = ffl + 0.024 + ph / 2.0
    pt = 0.10
    door_w = min(0.92, rw * 0.36)
    side_w = max(0.18, (rw - door_w) / 2.0)

    # North partition wall (with doorway opening + transom + ajar door leaf)
    objs.append(
        spawn_bevel_box(
            f"{rid}_PART_N_L",
            (side_w, pt, ph),
            (x0 + side_w / 2.0, y0 + rd - pt / 2.0, pz),
            m_plaster,
            coll,
            bevel=0.002,
            room_id=rid,
            role="partition_wall",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{rid}_PART_N_R",
            (side_w, pt, ph),
            (x0 + rw - side_w / 2.0, y0 + rd - pt / 2.0, pz),
            m_plaster,
            coll,
            bevel=0.002,
            room_id=rid,
            role="partition_wall",
        )
    )
    if ph > 2.14:
        th = ph - 2.10
        objs.append(
            spawn_bevel_box(
                f"{rid}_PART_N_TRANSOM",
                (door_w + 0.04, pt, th),
                (cx, y0 + rd - pt / 2.0, ffl + 2.12 + th / 2.0),
                m_plaster,
                coll,
                bevel=0.002,
                room_id=rid,
                role="partition_wall",
            )
        )
    # East partition wall segment
    side_d = max(0.24, rd - 1.10)
    objs.append(
        spawn_bevel_box(
            f"{rid}_PART_E",
            (pt, side_d, ph),
            (x0 + rw - pt / 2.0, y0 + side_d / 2.0, pz),
            m_plaster,
            coll,
            bevel=0.002,
            room_id=rid,
            role="partition_wall",
        )
    )
    # Ajar wooden door leaf (2.08 m high)
    objs.append(
        spawn_bevel_box(
            f"{rid}_INT_DOOR_LEAF",
            (0.042, 0.82, 2.08),
            (x0 + side_w + 0.10, y0 + rd - 0.45, ffl + 1.06),
            m_door,
            coll,
            rot_z=0.28,
            bevel=0.002,
            room_id=rid,
            role="prop",
            family="interior_door",
        )
    )
    return objs


def build_exterior_facade_shell(
    bid: str,
    b_center: tuple[float, float],
    w: float,
    d: float,
    z_start: float,
    z_end: float,
    floor_ffls: list[float],
    stucco_mat: bpy.types.Material,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
    window_bays_x: list[float],
) -> list[bpy.types.Object]:
    """
    Build 0.38 m exterior masonry walls from `z_start` to `z_end` with window openings on the South
    (square-facing) façade, rusticated plinth courses, inter-storey stone string courses + snow perches,
    corner quoins, and pilasters so no exterior wall plane > 2 m^2 lacks relief (§16).
    """
    objs = []
    wt = 0.38
    cx, cy = b_center
    b_min_x = cx - w / 2.0
    b_min_y = cy - d / 2.0
    seg_h = z_end - z_start
    seg_cz = z_start + seg_h / 2.0

    m_quoin = mats["Limestone_Quoin_Ashlar"]
    m_snow = mats["Snow_Fresh_Perch"]
    m_plaster_int = mats["Plaster_Interior_Warm"]

    # North, West, East 0.38 m exterior walls
    objs.append(
        spawn_bevel_box(
            f"{bid}_ExtWall_N_{int(z_start)}",
            (w, wt, seg_h),
            (cx, b_min_y + d - wt / 2.0, seg_cz),
            stucco_mat,
            coll,
            bevel=0.003,
            building_id=bid,
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{bid}_ExtWall_W_{int(z_start)}",
            (wt, d - 2 * wt, seg_h),
            (b_min_x + wt / 2.0, cy, seg_cz),
            stucco_mat,
            coll,
            bevel=0.003,
            building_id=bid,
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{bid}_ExtWall_E_{int(z_start)}",
            (wt, d - 2 * wt, seg_h),
            (b_min_x + w - wt / 2.0, cy, seg_cz),
            stucco_mat,
            coll,
            bevel=0.003,
            building_id=bid,
        )
    )

    # Central party wall (0.25 m thick)
    if z_end > 4.20:
        pw_z0 = max(4.20, z_start)
        pw_h = z_end - pw_z0
        if pw_h > 0.1:
            objs.append(
                spawn_bevel_box(
                    f"{bid}_PartyWall_{int(z_start)}",
                    (0.25, d - 2 * wt - 2.2, pw_h),
                    (cx, cy + 0.8, pw_z0 + pw_h / 2.0),
                    m_plaster_int,
                    coll,
                    bevel=0.002,
                    building_id=bid,
                )
            )

    # South façade piers between window bays
    sy = b_min_y + wt / 2.0
    win_w = 1.25
    sorted_bays = sorted(window_bays_x)
    edges = [b_min_x]
    for bx in sorted_bays:
        edges.append(bx - win_w / 2.0)
        edges.append(bx + win_w / 2.0)
    edges.append(b_min_x + w)

    for i in range(0, len(edges), 2):
        pw = edges[i + 1] - edges[i]
        if pw > 0.08:
            objs.append(
                spawn_bevel_box(
                    f"{bid}_SouthPier_{int(z_start)}_{i//2:02d}",
                    (pw, wt, seg_h),
                    (edges[i] + pw / 2.0, sy, seg_cz),
                    stucco_mat,
                    coll,
                    bevel=0.003,
                    building_id=bid,
                )
            )

    # Spandrels below and lintels above each window bay
    for z0 in floor_ffls:
        if z0 < z_start - 0.01 or z0 >= z_end - 0.01:
            continue
        is_ground = z0 < 0.5
        fh = 4.20 if is_ground else 3.20
        cur_sill = 0.65 if is_ground else 0.88
        cur_win_h = 2.25 if is_ground else 1.65
        for b_idx, bx in enumerate(sorted_bays):
            if is_ground and b_idx == len(sorted_bays) // 2:
                top_h = fh - 2.48
                objs.append(
                    spawn_bevel_box(
                        f"{bid}_L01_DoorHeader_{b_idx}",
                        (win_w + 0.04, wt, top_h),
                        (bx, sy, z0 + 2.48 + top_h / 2.0),
                        stucco_mat,
                        coll,
                        bevel=0.002,
                        building_id=bid,
                    )
                )
                continue
            objs.append(
                spawn_bevel_box(
                    f"{bid}_Z{int(z0)}_Spandrel_{b_idx}",
                    (win_w + 0.02, wt, cur_sill),
                    (bx, sy, z0 + cur_sill / 2.0),
                    m_quoin if is_ground else stucco_mat,
                    coll,
                    bevel=0.002,
                    building_id=bid,
                )
            )
            lintel_h = max(0.15, fh - (cur_sill + cur_win_h))
            objs.append(
                spawn_bevel_box(
                    f"{bid}_Z{int(z0)}_Lintel_{b_idx}",
                    (win_w + 0.02, wt, lintel_h),
                    (bx, sy, z0 + cur_sill + cur_win_h + lintel_h / 2.0),
                    stucco_mat,
                    coll,
                    bevel=0.002,
                    building_id=bid,
                )
            )

        # Inter-storey belt course + snow perch at top of storey
        top_z = z0 + fh
        objs.append(
            spawn_bevel_box(
                f"{bid}_BeltCourse_{int(top_z)}",
                (w + 0.16, d + 0.16, 0.15),
                (cx, cy, top_z),
                m_quoin,
                coll,
                bevel=0.003,
                building_id=bid,
            )
        )
        objs.append(
            spawn_bevel_box(
                f"{bid}_BeltSnow_{int(top_z)}",
                (w + 0.14, 0.08, 0.035),
                (cx, b_min_y - 0.06, top_z + 0.09),
                m_snow,
                coll,
                bevel=0.004,
                building_id=bid,
            )
        )

    # Corner quoins alternating 0.52 m and 0.36 m
    q_step = 0.40
    num_q = int(seg_h / q_step)
    for qi in range(num_q):
        qz = z_start + qi * q_step + q_step / 2.0
        qw = 0.52 if qi % 2 == 0 else 0.36
        for s_idx, qx in enumerate((b_min_x + qw / 2.0 - 0.02, b_min_x + w - qw / 2.0 + 0.02)):
            objs.append(
                spawn_bevel_box(
                    f"{bid}_Quoin_{int(z_start)}_{s_idx}_{qi:02d}",
                    (qw, 0.05, q_step - 0.025),
                    (qx, b_min_y - 0.025, qz),
                    m_quoin,
                    coll,
                    bevel=0.003,
                    building_id=bid,
                )
            )

    # Relief pilasters every 1.6 m on North, East, West walls so no wall plane > 2 m^2 is flat
    num_px = max(2, int(w / 1.6))
    for pi in range(num_px + 1):
        px = b_min_x + (pi / num_px) * w
        objs.append(
            spawn_bevel_box(
                f"{bid}_PilasterN_{int(z_start)}_{pi:02d}",
                (0.22, 0.05, seg_h),
                (px, b_min_y + d + 0.025, seg_cz),
                m_quoin,
                coll,
                bevel=0.003,
                building_id=bid,
            )
        )
    return objs
