#!/usr/bin/env python3
"""
Expanded District 2 Builder — Schlosspark-Viertel & Lindenallee (`townsquare/scene/build_park_district.py`).
Builds the eastern urban neighbourhood (`X in [+44, +154 m]`, `Y in [-42, +42 m]`):
  1. Lindenallee dual carriageways, granite kerbs, wide flagstone sidewalks, 4 zebra crosswalks,
     and twin grooved steel tramway tracks (`PARK_GROUND_AND_PATHS`).
  2. Schlosspark wrought-iron perimeter fence, 4 rusticated stone entrance gateways, and serpentine
     granite-edged park pathways (`PARK_FENCE_AND_GATES`).
  3. Frozen ornamental duck pond (`18 x 11.5 m`) with shoreline boulders, winter reeds, and a `9.2 m`
     arched ashlar stone footbridge with carved balustrades and 4 bronze bridge lanterns (`PARK_POND_AND_BRIDGE`).
  4. Victorian octagonal cast-iron & patinated-copper park bandstand (`PARK_BANDSTAND`) with warm festoon lights.
  5. 36 additional trees: 20 multi-branched winter deciduous trees (`PARK_TREES_DECIDUOUS`) +
     16 snow-laden evergreen park spruces (`PARK_TREES_SPRUCE`).
  6. 18 cast-iron utility & tram catenary poles with continuous overhead contact wires, 28 street/park lamps,
     6 traffic signal posts, 10 street-name signs, 3 Litfaßsäulen poster columns, 2 glazed phone booths,
     1 tram shelter, 20 park benches, 8 waste bins, 10 bicycles, and 28 bollards (`BOULEVARD_POLES_AND_WIRES`).
  7. 10 detailed city vehicles (`CITY_VEHICLES`): 1 vintage electric streetcar tram (`TRAM_01`),
     6 detailed winter sedans/station wagons (`CAR_05..10`), 2 delivery vans (`VAN_02..03`),
     and 1 horse-drawn festive Landau carriage (`CARRIAGE_01`).
  8. 34 multi-part sculpted 3D animals (`CITY_ANIMALS`): 8 dogs, 2 harnessed draught horses,
     4 cats, 18 mallard ducks & city pigeons, and 2 park red squirrels.
"""
from __future__ import annotations
import math
import bpy  # type: ignore

from townsquare.kits.core import (
    ensure_collection,
    join_mesh_objects,
    spawn_bevel_box,
    spawn_lathe,
)
from townsquare.kits.lighting.builder import (
    build_street_lamp,
    spawn_blender_light,
)


def _add_park_bench(
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
                (1.85, 0.09, 0.034),
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
                (1.85, 0.032, 0.082),
                off(0.0, 0.22, 0.54 + s_i * 0.09),
                mats["Walnut_Dark_Joinery"],
                coll,
                rot_z=rot_z,
                bevel=0.002,
                role="public_bench",
            )
        )
    for a_i, ax in enumerate((-0.84, 0.0, 0.84)):
        objs.append(
            spawn_bevel_box(
                f"{name}_Frame_{a_i}",
                (0.055, 0.54, 0.64),
                off(ax, 0.0, 0.32),
                mats["Cast_Iron_Black"],
                coll,
                rot_z=rot_z,
                bevel=0.002,
                role="public_bench",
            )
        )
    objs.append(
        spawn_bevel_box(
            f"{name}_SnowCap",
            (1.78, 0.07, 0.028),
            off(0.0, 0.22, 0.86),
            mats["Snow_Fresh_Perch"],
            coll,
            rot_z=rot_z,
            bevel=0.003,
            role="snow_perch",
        )
    )


def _add_detailed_car(
    objs: list[bpy.types.Object],
    name: str,
    cx: float,
    cy: float,
    cz: float,
    rot_z: float,
    body_mat: bpy.types.Material,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
    is_van: bool = False,
    is_taxi: bool = False,
) -> None:
    """Build a multi-part European car or delivery van with wheels, arches, windows, bumpers, lights, mirrors & snow."""
    ca, sa = math.cos(rot_z), math.sin(rot_z)

    def off(dx: float, dy: float, dz: float) -> tuple[float, float, float]:
        return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca, cz + dz)

    length = 4.85 if is_van else 4.35
    width = 1.92 if is_van else 1.78
    lower_h = 0.72 if is_van else 0.58
    cabin_l = 3.35 if is_van else 2.25
    cabin_h = 1.08 if is_van else 0.56
    cabin_x = -0.35 if is_van else -0.18

    # Lower sculpted chassis body + front/rear fenders
    objs.append(
        spawn_bevel_box(
            f"{name}_LowerBody",
            (length, width, lower_h),
            off(0.0, 0.0, 0.30 + lower_h / 2.0),
            body_mat,
            coll,
            rot_z=rot_z,
            bevel=0.035,
            role="vehicle",
        )
    )
    # Cabin greenhouse
    objs.append(
        spawn_bevel_box(
            f"{name}_Cabin",
            (cabin_l, width - 0.16, cabin_h),
            off(cabin_x, 0.0, 0.30 + lower_h + cabin_h / 2.0 - 0.04),
            body_mat,
            coll,
            rot_z=rot_z,
            bevel=0.030,
            role="vehicle",
        )
    )
    # Windscreen, rear window, and side windows (Architectural_Glass)
    win_z = 0.30 + lower_h + cabin_h * 0.48
    objs.append(
        spawn_bevel_box(
            f"{name}_Windscreen",
            (0.08, width - 0.28, cabin_h * 0.72),
            off(cabin_x + cabin_l / 2.0 + 0.01, 0.0, win_z),
            mats["Architectural_Glass"],
            coll,
            rot_z=rot_z,
            bevel=0.005,
            role="vehicle",
        )
    )
    objs.append(
        spawn_bevel_box(
            f"{name}_RearGlass",
            (0.08, width - 0.30, cabin_h * 0.68),
            off(cabin_x - cabin_l / 2.0 - 0.01, 0.0, win_z),
            mats["Architectural_Glass"],
            coll,
            rot_z=rot_z,
            bevel=0.005,
            role="vehicle",
        )
    )
    for sy in (-width / 2.0 + 0.06, width / 2.0 - 0.06):
        objs.append(
            spawn_bevel_box(
                f"{name}_SideGlass_{sy:+.2f}",
                (cabin_l * 0.78, 0.06, cabin_h * 0.68),
                off(cabin_x, sy, win_z),
                mats["Architectural_Glass"],
                coll,
                rot_z=rot_z,
                bevel=0.004,
                role="vehicle",
            )
        )
        # Side wing mirrors
        objs.append(
            spawn_bevel_box(
                f"{name}_Mirror_{sy:+.2f}",
                (0.14, 0.18, 0.10),
                off(cabin_x + cabin_l * 0.42, sy * 1.08, 0.30 + lower_h + 0.06),
                mats["Chrome_Fixture"],
                coll,
                rot_z=rot_z,
                bevel=0.004,
                role="vehicle",
            )
        )

    # Roof snow blanket + optional taxi sign or luggage rack
    roof_z = 0.30 + lower_h + cabin_h - 0.02
    objs.append(
        spawn_bevel_box(
            f"{name}_RoofSnow",
            (cabin_l * 0.86, width - 0.28, 0.038),
            off(cabin_x, 0.0, roof_z),
            mats["Snow_Fresh_Perch"],
            coll,
            rot_z=rot_z,
            bevel=0.006,
            role="snow_perch",
        )
    )
    if is_taxi:
        objs.append(
            spawn_bevel_box(
                f"{name}_TaxiSign",
                (0.28, 0.62, 0.14),
                off(cabin_x + 0.35, 0.0, roof_z + 0.08),
                mats["Emitter_Festive_2400K"],
                coll,
                rot_z=rot_z,
                bevel=0.004,
                role="vehicle",
            )
        )

    # Chrome front & rear bumpers, radiator grille, glowing headlamps & red taillights
    for bx_sign, b_tag in ((1.0, "Front"), (-1.0, "Rear")):
        bx_pos = bx_sign * (length / 2.0 + 0.04)
        objs.append(
            spawn_bevel_box(
                f"{name}_Bumper_{b_tag}",
                (0.12, width + 0.04, 0.14),
                off(bx_pos, 0.0, 0.36),
                mats["Chrome_Fixture"],
                coll,
                rot_z=rot_z,
                bevel=0.005,
                role="vehicle",
            )
        )
        for ly in (-width * 0.36, width * 0.36):
            objs.append(
                spawn_bevel_box(
                    f"{name}_Lamp_{b_tag}_{ly:+.2f}",
                    (0.08, 0.24, 0.14),
                    off(bx_sign * (length / 2.0 + 0.01), ly, 0.62),
                    mats["Emitter_Warm_2700K" if bx_sign > 0 else "Painted_Metal_Burgundy"],
                    coll,
                    rot_z=rot_z,
                    bevel=0.004,
                    role="vehicle",
                )
            )
    objs.append(
        spawn_bevel_box(
            f"{name}_Grille",
            (0.06, width * 0.44, 0.22),
            off(length / 2.0 + 0.02, 0.0, 0.58),
            mats["Chrome_Fixture"],
            coll,
            rot_z=rot_z,
            bevel=0.003,
            role="vehicle",
        )
    )

    # 4 Wheels (tyre + brushed steel hubcap + wheel arch flare)
    wheel_x_offs = (-length * 0.32, length * 0.32)
    wheel_y_offs = (-width / 2.0 + 0.04, width / 2.0 - 0.04)
    for wx_i, wx in enumerate(wheel_x_offs):
        for wy_i, wy in enumerate(wheel_y_offs):
            objs.append(
                spawn_bevel_box(
                    f"{name}_Tyre_{wx_i}_{wy_i}",
                    (0.64, 0.22, 0.64),
                    off(wx, wy, 0.32),
                    mats["Cast_Iron_Black"],
                    coll,
                    rot_z=rot_z,
                    bevel=0.025,
                    role="vehicle",
                )
            )
            objs.append(
                spawn_bevel_box(
                    f"{name}_Hub_{wx_i}_{wy_i}",
                    (0.36, 0.25, 0.36),
                    off(wx, wy, 0.32),
                    mats["Brushed_Steel"],
                    coll,
                    rot_z=rot_z,
                    bevel=0.012,
                    role="vehicle",
                )
            )


def _add_electric_tram(
    objs: list[bpy.types.Object],
    cx: float,
    cy: float,
    cz: float,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
) -> None:
    """Build `TRAM_01_LINDENALLEE`, an 11.2 m vintage European electric streetcar with pantograph & glowing windows."""
    L, W = 11.20, 2.36
    # Steel bogies & 8 rail wheels
    for bx in (-3.40, 3.40):
        objs.append(
            spawn_bevel_box(
                f"TRAM_Bogie_{bx:+.1f}",
                (2.20, 1.85, 0.38),
                (cx + bx, cy, cz + 0.28),
                mats["Cast_Iron_Black"],
                coll,
                bevel=0.008,
                role="vehicle",
            )
        )
        for wx in (bx - 0.72, bx + 0.72):
            for wy in (-0.70, 0.70):
                objs.append(
                    spawn_bevel_box(
                        f"TRAM_Wheel_{wx:+.1f}_{wy:+.1f}",
                        (0.68, 0.14, 0.68),
                        (cx + wx, cy + wy, cz + 0.34),
                        mats["Brushed_Steel"],
                        coll,
                        bevel=0.02,
                        role="vehicle",
                    )
                )
    # Lower pine-green apron + cream window belt + brass waist rail
    objs.append(
        spawn_bevel_box(
            "TRAM_LowerApron",
            (L, W, 1.05),
            (cx, cy, cz + 1.02),
            mats["Painted_Metal_Green"],
            coll,
            bevel=0.03,
            role="vehicle",
        )
    )
    objs.append(
        spawn_bevel_box(
            "TRAM_BrassBelt",
            (L + 0.06, W + 0.04, 0.08),
            (cx, cy, cz + 1.56),
            mats["Aged_Brass"],
            coll,
            bevel=0.004,
            role="vehicle",
        )
    )
    objs.append(
        spawn_bevel_box(
            "TRAM_UpperBody",
            (L - 0.10, W - 0.04, 1.38),
            (cx, cy, cz + 2.26),
            mats["Painted_Pine_Cream"],
            coll,
            bevel=0.03,
            role="vehicle",
        )
    )
    # Warm glowing interior passenger compartment core + 7 side windows per side
    objs.append(
        spawn_bevel_box(
            "TRAM_InteriorGlowCore",
            (L - 1.20, W - 0.28, 1.12),
            (cx, cy, cz + 2.26),
            mats["Window_Warm_Interior_Glow"],
            coll,
            bevel=0.005,
            role="window_glow_backdrop",
        )
    )
    for w_i in range(-3, 4):
        wx = cx + w_i * 1.32
        for sy in (-W / 2.0 - 0.01, W / 2.0 + 0.01):
            objs.append(
                spawn_bevel_box(
                    f"TRAM_PassWin_{w_i}_{sy:+.1f}",
                    (1.04, 0.03, 0.96),
                    (wx, cy + sy, cz + 2.28),
                    mats["Architectural_Glass"],
                    coll,
                    bevel=0.003,
                    role="vehicle",
                )
            )
            objs.append(
                spawn_bevel_box(
                    f"TRAM_WinFrame_{w_i}_{sy:+.1f}",
                    (1.12, 0.05, 0.06),
                    (wx, cy + sy, cz + 1.78),
                    mats["Walnut_Dark_Joinery"],
                    coll,
                    bevel=0.002,
                    role="vehicle",
                )
            )
    # Front & rear 3-pane driver windscreens + destination boards + brass headlamps + bumpers
    for end_s in (-1.0, 1.0):
        ex = cx + end_s * (L / 2.0 + 0.02)
        for wy_off in (-0.68, 0.0, 0.68):
            objs.append(
                spawn_bevel_box(
                    f"TRAM_DriverGlass_{end_s:+.0f}_{wy_off:+.2f}",
                    (0.05, 0.56, 0.92),
                    (ex, cy + wy_off, cz + 2.26),
                    mats["Architectural_Glass"],
                    coll,
                    bevel=0.003,
                    role="vehicle",
                )
            )
            objs.append(
                spawn_bevel_box(
                    f"TRAM_DriverGlow_{end_s:+.0f}_{wy_off:+.2f}",
                    (0.03, 0.50, 0.84),
                    (ex - end_s * 0.04, cy + wy_off, cz + 2.26),
                    mats["Window_Warm_Interior_Glow"],
                    coll,
                    bevel=0.002,
                    role="window_glow_backdrop",
                )
            )
        objs.append(
            spawn_bevel_box(
                f"TRAM_Bumper_{end_s:+.0f}",
                (0.18, W + 0.06, 0.16),
                (ex + end_s * 0.05, cy, cz + 0.52),
                mats["Cast_Iron_Black"],
                coll,
                bevel=0.006,
                role="vehicle",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"TRAM_Headlamp_{end_s:+.0f}",
                (0.14, 0.32, 0.32),
                (ex + end_s * 0.02, cy, cz + 1.08),
                mats["Emitter_Festive_2400K"],
                coll,
                bevel=0.008,
                role="vehicle",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"TRAM_DestSign_{end_s:+.0f}",
                (0.08, 1.25, 0.26),
                (ex + end_s * 0.02, cy, cz + 2.86),
                mats["Emitter_Warm_2700K"],
                coll,
                bevel=0.004,
                role="vehicle",
            )
        )
    # Clerestory roof + snow layer + diamond pantograph reaching overhead wire at Z=5.65 m
    objs.append(
        spawn_bevel_box(
            "TRAM_Roof",
            (L - 0.30, W - 0.12, 0.22),
            (cx, cy, cz + 3.04),
            mats["Roof_Slate_Dark"],
            coll,
            bevel=0.015,
            role="vehicle",
        )
    )
    objs.append(
        spawn_bevel_box(
            "TRAM_Clerestory",
            (L - 2.40, 1.32, 0.28),
            (cx, cy, cz + 3.28),
            mats["Walnut_Dark_Joinery"],
            coll,
            bevel=0.010,
            role="vehicle",
        )
    )
    objs.append(
        spawn_bevel_box(
            "TRAM_RoofSnow",
            (L - 2.50, 1.24, 0.042),
            (cx, cy, cz + 3.44),
            mats["Snow_Fresh_Perch"],
            coll,
            bevel=0.006,
            role="snow_perch",
        )
    )
    # Diamond pantograph assembly (Z = 3.45 m .. 5.65 m)
    for py in (-0.42, 0.42):
        objs.append(
            spawn_bevel_box(
                f"TRAM_PantoLower_{py:+.2f}",
                (1.65, 0.045, 1.10),
                (cx - 1.20, cy + py, cz + 4.00),
                mats["Brushed_Steel"],
                coll,
                bevel=0.003,
                role="vehicle",
            )
        )
        objs.append(
            spawn_bevel_box(
                f"TRAM_PantoUpper_{py:+.2f}",
                (1.45, 0.040, 1.10),
                (cx - 1.20, cy + py, cz + 5.05),
                mats["Brushed_Steel"],
                coll,
                bevel=0.003,
                role="vehicle",
            )
        )
    objs.append(
        spawn_bevel_box(
            "TRAM_PantoContactShoe",
            (0.24, 1.35, 0.06),
            (cx - 1.20, cy, cz + 5.62),
            mats["Aged_Brass"],
            coll,
            bevel=0.003,
            role="vehicle",
        )
    )


def _add_dog(
    objs: list[bpy.types.Object],
    name: str,
    dx: float,
    dy: float,
    dz: float,
    rot_z: float,
    coat_mat: bpy.types.Material,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
    scale: float = 1.0,
) -> None:
    """Build an articulated 3D dog (torso, chest, neck, head, snout, 2 ears, 4 legs, 4 paws, collar, tail)."""
    ca, sa = math.cos(rot_z), math.sin(rot_z)

    def off(lx: float, ly: float, lz: float) -> tuple[float, float, float]:
        return (dx + (lx * ca - ly * sa) * scale, dy + (lx * sa + ly * ca) * scale, dz + lz * scale)

    def sc(w: float, d: float, h: float) -> tuple[float, float, float]:
        return (w * scale, d * scale, h * scale)

    objs.append(spawn_bevel_box(f"{name}_Torso", sc(0.60, 0.26, 0.28), off(0.0, 0.0, 0.42), coat_mat, coll, rot_z=rot_z, bevel=0.045 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Chest", sc(0.28, 0.28, 0.30), off(0.22, 0.0, 0.44), coat_mat, coll, rot_z=rot_z, bevel=0.045 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Haunch", sc(0.24, 0.27, 0.27), off(-0.20, 0.0, 0.43), coat_mat, coll, rot_z=rot_z, bevel=0.042 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Neck", sc(0.18, 0.20, 0.24), off(0.32, 0.0, 0.58), coat_mat, coll, rot_z=rot_z, bevel=0.032 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Collar", sc(0.20, 0.22, 0.055), off(0.32, 0.0, 0.54), mats["Painted_Metal_Burgundy"], coll, rot_z=rot_z, bevel=0.008 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Head", sc(0.24, 0.21, 0.20), off(0.42, 0.0, 0.68), coat_mat, coll, rot_z=rot_z, bevel=0.038 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Snout", sc(0.18, 0.12, 0.11), off(0.54, 0.0, 0.65), coat_mat, coll, rot_z=rot_z, bevel=0.022 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Nose", sc(0.05, 0.06, 0.05), off(0.62, 0.0, 0.67), mats["Cast_Iron_Black"], coll, rot_z=rot_z, bevel=0.008 * scale, role="animal"))
    for ey in (-0.08, 0.08):
        objs.append(spawn_bevel_box(f"{name}_Ear_{ey:+.2f}", sc(0.08, 0.06, 0.14), off(0.38, ey, 0.77), coat_mat, coll, rot_z=rot_z, bevel=0.012 * scale, role="animal"))
        objs.append(spawn_bevel_box(f"{name}_Eye_{ey:+.2f}", sc(0.035, 0.035, 0.035), off(0.49, ey * 0.82, 0.71), mats["Cast_Iron_Black"], coll, rot_z=rot_z, bevel=0.006 * scale, role="animal"))
    for lx_i, lx in enumerate((-0.22, 0.22)):
        for ly_i, ly in enumerate((-0.09, 0.09)):
            objs.append(spawn_bevel_box(f"{name}_Thigh_{lx_i}_{ly_i}", sc(0.12, 0.10, 0.22), off(lx, ly, 0.28), coat_mat, coll, rot_z=rot_z, bevel=0.020 * scale, role="animal"))
            objs.append(spawn_bevel_box(f"{name}_Leg_{lx_i}_{ly_i}", sc(0.09, 0.09, 0.24), off(lx, ly, 0.12), coat_mat, coll, rot_z=rot_z, bevel=0.016 * scale, role="animal"))
            objs.append(spawn_bevel_box(f"{name}_Paw_{lx_i}_{ly_i}", sc(0.12, 0.10, 0.06), off(lx + 0.02, ly, 0.020), coat_mat, coll, rot_z=rot_z, bevel=0.010 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Tail", sc(0.26, 0.08, 0.09), off(-0.36, 0.0, 0.54), coat_mat, coll, rot_z=rot_z, bevel=0.016 * scale, role="animal"))


def _add_draught_horse(
    objs: list[bpy.types.Object],
    name: str,
    hx: float,
    hy: float,
    hz: float,
    rot_z: float,
    coat_mat: bpy.types.Material,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
) -> None:
    """Build a 1.65 m shoulder-height sculpted draught horse with harness, mane, legs, hooves & tail."""
    ca, sa = math.cos(rot_z), math.sin(rot_z)

    def off(lx: float, ly: float, lz: float) -> tuple[float, float, float]:
        return (hx + lx * ca - ly * sa, hy + lx * sa + ly * ca, hz + lz)

    objs.append(spawn_bevel_box(f"{name}_Barrel", (1.52, 0.66, 0.72), off(0.0, 0.0, 1.24), coat_mat, coll, rot_z=rot_z, bevel=0.12, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Chest", (0.64, 0.68, 0.76), off(0.56, 0.0, 1.28), coat_mat, coll, rot_z=rot_z, bevel=0.12, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Croup", (0.62, 0.66, 0.72), off(-0.52, 0.0, 1.26), coat_mat, coll, rot_z=rot_z, bevel=0.12, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Neck", (0.52, 0.38, 0.72), off(0.84, 0.0, 1.66), coat_mat, coll, rot_z=rot_z, bevel=0.08, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Mane", (0.54, 0.14, 0.66), off(0.76, 0.0, 1.72), mats["Cast_Iron_Black"], coll, rot_z=rot_z, bevel=0.03, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Head", (0.54, 0.32, 0.36), off(1.12, 0.0, 1.92), coat_mat, coll, rot_z=rot_z, bevel=0.06, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Muzzle", (0.32, 0.24, 0.24), off(1.36, 0.0, 1.82), coat_mat, coll, rot_z=rot_z, bevel=0.045, role="animal"))
    for ey in (-0.11, 0.11):
        objs.append(spawn_bevel_box(f"{name}_Ear_{ey:+.2f}", (0.10, 0.08, 0.20), off(0.98, ey, 2.12), coat_mat, coll, rot_z=rot_z, bevel=0.015, role="animal"))
        objs.append(spawn_bevel_box(f"{name}_Eye_{ey:+.2f}", (0.06, 0.06, 0.06), off(1.18, ey * 1.25, 1.96), mats["Cast_Iron_Black"], coll, rot_z=rot_z, bevel=0.010, role="animal"))
    # Leather collar & brass harness
    objs.append(spawn_bevel_box(f"{name}_HarnessCollar", (0.22, 0.72, 0.80), off(0.68, 0.0, 1.34), mats["Leather_Saddle_Brown"], coll, rot_z=rot_z, bevel=0.035, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_HarnessBrass", (0.88, 0.70, 0.10), off(0.15, 0.0, 1.38), mats["Aged_Brass"], coll, rot_z=rot_z, bevel=0.018, role="animal"))
    # 4 legs + hooves
    for lx_i, lx in enumerate((-0.54, 0.54)):
        for ly_i, ly in enumerate((-0.22, 0.22)):
            objs.append(spawn_bevel_box(f"{name}_UpperLeg_{lx_i}_{ly_i}", (0.22, 0.20, 0.60), off(lx, ly, 0.74), coat_mat, coll, rot_z=rot_z, bevel=0.038, role="animal"))
            objs.append(spawn_bevel_box(f"{name}_LowerLeg_{lx_i}_{ly_i}", (0.16, 0.16, 0.48), off(lx, ly, 0.28), coat_mat, coll, rot_z=rot_z, bevel=0.028, role="animal"))
            objs.append(spawn_bevel_box(f"{name}_Hoof_{lx_i}_{ly_i}", (0.19, 0.18, 0.12), off(lx + 0.02, ly, 0.045), mats["Cast_Iron_Black"], coll, rot_z=rot_z, bevel=0.020, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Tail", (0.22, 0.20, 0.78), off(-0.82, 0.0, 0.96), mats["Cast_Iron_Black"], coll, rot_z=rot_z, bevel=0.038, role="animal"))


def _add_waterfowl_or_pigeon(
    objs: list[bpy.types.Object],
    name: str,
    bx: float,
    by: float,
    bz: float,
    rot_z: float,
    is_duck: bool,
    mats: dict[str, bpy.types.Material],
    coll: bpy.types.Collection,
) -> None:
    ca, sa = math.cos(rot_z), math.sin(rot_z)

    def off(lx: float, ly: float, lz: float) -> tuple[float, float, float]:
        return (bx + lx * ca - ly * sa, by + lx * sa + ly * ca, bz + lz)

    body_m = mats["Walnut_Dark_Joinery" if is_duck else "Plaster_Guild_Grey"]
    head_m = mats["Painted_Metal_Green" if is_duck else "Cast_Iron_Black"]
    scale = 1.25 if is_duck else 0.85
    objs.append(spawn_bevel_box(f"{name}_Body", (0.28 * scale, 0.18 * scale, 0.15 * scale), off(0.0, 0.0, 0.095 * scale), body_m, coll, rot_z=rot_z, bevel=0.028 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Head", (0.12 * scale, 0.11 * scale, 0.13 * scale), off(0.14 * scale, 0.0, 0.19 * scale), head_m, coll, rot_z=rot_z, bevel=0.020 * scale, role="animal"))
    objs.append(spawn_bevel_box(f"{name}_Beak", (0.09 * scale, 0.06 * scale, 0.05 * scale), off(0.22 * scale, 0.0, 0.18 * scale), mats["Gold_Sign_Leaf"], coll, rot_z=rot_z, bevel=0.008 * scale, role="animal"))
    for ly_s in (-1.0, 1.0):
        objs.append(spawn_bevel_box(f"{name}_Leg_{ly_s:+.0f}", (0.035 * scale, 0.035 * scale, 0.07 * scale), off(-0.01 * scale, ly_s * 0.045 * scale, 0.035 * scale), mats["Gold_Sign_Leaf"], coll, rot_z=rot_z, bevel=0.005 * scale, role="animal"))
        objs.append(spawn_bevel_box(f"{name}_Foot_{ly_s:+.0f}", (0.07 * scale, 0.05 * scale, 0.022 * scale), off(0.01 * scale, ly_s * 0.045 * scale, 0.008 * scale), mats["Gold_Sign_Leaf"], coll, rot_z=rot_z, bevel=0.004 * scale, role="animal"))


def build_park_district(
    prog: dict,
    mats: dict[str, bpy.types.Material],
    col_pub: bpy.types.Collection,
) -> dict:
    """Build the entire Schlosspark-Viertel & Lindenallee expansion inside `02_PUBLIC_REALM`."""
    ground_objs: list[bpy.types.Object] = []
    fence_objs: list[bpy.types.Object] = []
    pond_bridge_objs: list[bpy.types.Object] = []
    bandstand_objs: list[bpy.types.Object] = []
    decid_tree_objs: list[bpy.types.Object] = []
    spruce_tree_objs: list[bpy.types.Object] = []
    pole_wire_objs: list[bpy.types.Object] = []
    vehicle_objs: list[bpy.types.Object] = []
    animal_objs: list[bpy.types.Object] = []

    # =========================================================================
    # 1. LINDENALLEE BOULEVARD, SIDEWALKS, CROSSWALKS, TRAM RAILS & PARK PATHS
    # =========================================================================
    # Continuous dark basalt / wet-mortar base under District 2 (X = +36 .. +154 m, Y = -42 .. +42 m)
    ground_objs.append(
        spawn_bevel_box(
            "D2_Subbase_Mortar",
            (118.0, 84.0, 0.06),
            (95.0, 0.0, -0.032),
            mats["Mortar_Joint_Wet"],
            col_pub,
            bevel=0.003,
            role="mortar_bed",
        )
    )

    # North & South Lindenallee Carriageways (Y = +19.5 m and Y = -19.5 m, X = +36..+134 m)
    cobble_mats = [
        mats["Cobble_Granite_Dark"],
        mats["Cobble_Granite_Grey"],
        mats["Cobble_Granite_Warm"],
        mats["Cobble_Porphyry_Red"],
    ]
    for gx in range(25, 92):
        slab_x = gx * 1.45
        for gy in range(-26, 27):
            slab_y = gy * 1.45
            # Skip interior of Schlosspark lawn (X in [52, 122], Y in [-15.0, +15.0]) so park snow/paths sit cleanly
            if 52.0 <= slab_x <= 122.0 and -15.0 <= slab_y <= 15.0:
                continue
            mat_i = (gx * 5 + gy * 3) % len(cobble_mats)
            ground_objs.append(
                spawn_bevel_box(
                    f"D2_Paver_{gx}_{gy}",
                    (1.438, 1.438, 0.028),
                    (slab_x, slab_y, -0.002),
                    cobble_mats[mat_i],
                    col_pub,
                    bevel=0.003,
                    role="square_paver",
                )
            )

    # Raised Granite Sidewalks in front of B13..B15 (North), B19..B20 (South), B16..B18 (East)
    for sw_name, sw_dims, sw_loc in (
        ("Sidewalk_North_Allee", (84.0, 4.4, 0.14), (88.0, 24.2, 0.06)),
        ("Sidewalk_South_Allee", (84.0, 4.4, 0.14), (88.0, -24.2, 0.06)),
        ("Sidewalk_East_Park", (4.4, 62.0, 0.14), (131.5, 0.0, 0.06)),
        ("Sidewalk_Park_NorthProm", (72.0, 2.2, 0.12), (87.0, 16.2, 0.05)),
        ("Sidewalk_Park_SouthProm", (72.0, 2.2, 0.12), (87.0, -16.2, 0.05)),
    ):
        ground_objs.append(
            spawn_bevel_box(
                sw_name,
                sw_dims,
                sw_loc,
                mats["Granite_Kerb_Weathered"],
                col_pub,
                bevel=0.004,
                role="kerbstone",
            )
        )

    # 4 Zebra Pedestrian Crosswalks across Lindenallee
    for cw_idx, (cwx, cwy) in enumerate(((50.0, 19.5), (88.0, 19.5), (124.0, 19.5), (88.0, -19.5)), 1):
        for st_i in range(-4, 5):
            ground_objs.append(
                spawn_bevel_box(
                    f"ZebraStripe_{cw_idx}_{st_i}",
                    (2.80, 0.36, 0.016),
                    (cwx, cwy + st_i * 0.62, 0.014),
                    mats["Painted_Pine_Cream"],
                    col_pub,
                    bevel=0.002,
                    role="crosswalk",
                )
            )

    # Twin Grooved Steel Tramway Rails + Timber/Stone Sleepers along North Lindenallee (Y = +18.8 & +20.2 m)
    for rail_y in (18.82, 20.18):
        ground_objs.append(
            spawn_bevel_box(
                f"TramRail_North_{rail_y:.2f}",
                (98.0, 0.09, 0.045),
                (84.0, rail_y, 0.022),
                mats["Brushed_Steel"],
                col_pub,
                bevel=0.003,
                role="tram_rail",
            )
        )
    for sl_i in range(60):
        sl_x = 38.0 + sl_i * 1.55
        ground_objs.append(
            spawn_bevel_box(
                f"TramSleeper_{sl_i:02d}",
                (0.28, 1.95, 0.022),
                (sl_x, 19.50, 0.011),
                mats["Walnut_Dark_Joinery"],
                col_pub,
                bevel=0.002,
                role="tram_sleeper",
            )
        )

    # Schlosspark Snow-Covered Lawns (X in [52, 122], Y in [-15.2, +15.2]) + Serpentine Granite-Edged Pathways
    ground_objs.append(
        spawn_bevel_box(
            "Schlosspark_SnowLawn_Base",
            (70.0, 30.4, 0.08),
            (87.0, 0.0, 0.035),
            mats["Snow_Fresh_Perch"],
            col_pub,
            bevel=0.012,
            role="snow_perch",
        )
    )
    #Gentle snow drift mounds across the park lawn
    for md_i in range(18):
        mx = 56.0 + (md_i % 6) * 11.2
        my = -11.5 + (md_i // 6) * 11.5
        if abs(my) < 3.5 or (92.0 <= mx <= 116.0 and abs(my) < 8.5):
            continue
        ground_objs.append(
            spawn_bevel_box(
                f"ParkSnowDrift_{md_i:02d}",
                (6.8, 5.2, 0.16),
                (mx, my, 0.09),
                mats["Snow_Fresh_Perch"],
                col_pub,
                rot_z=md_i * 0.35,
                bevel=0.035,
                role="snow_perch",
            )
        )

    # Park Pathways: Octagonal Central Compass Plaza at (85.0, 0.0) + East-West & North-South Promenades
    ground_objs.append(
        spawn_lathe(
            "ParkPlaza_Center_Compass",
            [(0.0, 0.0), (3.85, 0.0), (3.85, 0.068), (0.0, 0.068)],
            (85.0, 0.0, 0.022),
            mats["Cobble_Granite_Warm"],
            col_pub,
            segments=16,
            role="park_pathway",
        )
    )
    for p_i in range(48):
        px = 50.5 + p_i * 1.52
        # Over the pond (96..112), the arched stone bridge carries the path
        if 96.5 <= px <= 111.5:
            continue
        ground_objs.append(
            spawn_bevel_box(
                f"ParkPath_EW_{p_i:02d}",
                (1.54, 3.10, 0.065),
                (px, 0.0, 0.055),
                mats["Cobble_Granite_Warm"],
                col_pub,
                bevel=0.004,
                role="park_pathway",
            )
        )
        if abs(px - 85.0) > 2.2:
            for edge_y in (-1.62, 1.62):
                ground_objs.append(
                    spawn_bevel_box(
                        f"ParkPath_EW_Edge_{p_i:02d}_{edge_y:+.1f}",
                        (1.52, 0.16, 0.095),
                        (px, edge_y, 0.068),
                        mats["Granite_Kerb_Weathered"],
                        col_pub,
                        bevel=0.003,
                        role="kerbstone",
                    )
                )
    for py_i in range(-10, 11):
        py = py_i * 1.45
        if abs(py) < 1.8:
            continue
        ground_objs.append(
            spawn_bevel_box(
                f"ParkPath_NS_{py_i:+03d}",
                (2.85, 1.48, 0.065),
                (85.0, py, 0.055),
                mats["Cobble_Granite_Warm"],
                col_pub,
                bevel=0.004,
                role="park_pathway",
            )
        )

    # Wet puddles & slush channels along Lindenallee
    for pd_i, (pdx, pdy, pdw, pdd) in enumerate((
        (58.0, 17.8, 3.8, 2.1),
        (76.0, 17.6, 4.2, 2.2),
        (96.0, 18.2, 3.5, 1.9),
        (64.0, -18.0, 4.0, 2.2),
        (92.0, -18.4, 3.6, 2.0),
    )):
        ground_objs.append(
            spawn_bevel_box(
                f"D2_Puddle_{pd_i:02d}",
                (pdw, pdd, 0.008),
                (pdx, pdy, 0.013),
                mats["Puddle_Water_Film"],
                col_pub,
                bevel=0.002,
                role="puddle",
            )
        )

    # =========================================================================
    # 2. SCHLOSSPARK WROUGHT-IRON FENCE & 4 MONUMENTAL STONE GATEWAYS
    # =========================================================================
    # Perimeter: X in [51.5, 122.5], Y in [-15.2, +15.2]
    for side_y in (-15.2, 15.2):
        for fx_i in range(28):
            fx = 52.8 + fx_i * 2.52
            if abs(fx - 85.0) < 2.6:  # North/South Gate opening
                continue
            fence_objs.append(
                spawn_bevel_box(
                    f"ParkFencePlinth_Y_{side_y:+.0f}_{fx_i:02d}",
                    (2.44, 0.28, 0.38),
                    (fx, side_y, 0.19),
                    mats["Limestone_Quoin_Ashlar"],
                    col_pub,
                    bevel=0.004,
                    role="park_fence",
                )
            )
            fence_objs.append(
                spawn_bevel_box(
                    f"ParkFenceTopRail_Y_{side_y:+.0f}_{fx_i:02d}",
                    (2.48, 0.06, 0.05),
                    (fx, side_y, 1.48),
                    mats["Cast_Iron_Black"],
                    col_pub,
                    bevel=0.002,
                    role="park_fence",
                )
            )
            for p_k in range(-4, 5):
                fence_objs.append(
                    spawn_bevel_box(
                        f"ParkPicket_Y_{side_y:+.0f}_{fx_i:02d}_{p_k}",
                        (0.032, 0.032, 1.16),
                        (fx + p_k * 0.26, side_y, 0.94),
                        mats["Cast_Iron_Black"],
                        col_pub,
                        bevel=0.001,
                        role="park_fence",
                    )
                )

    # 4 Rusticated Stone Gateways (West, East, North, South) with spherical finials
    gate_coords = [
        ("WestGate_L", 51.5, -2.2), ("WestGate_R", 51.5, 2.2),
        ("EastGate_L", 122.5, -2.2), ("EastGate_R", 122.5, 2.2),
        ("NorthGate_L", 82.8, 15.2), ("NorthGate_R", 87.2, 15.2),
        ("SouthGate_L", 82.8, -15.2), ("SouthGate_R", 87.2, -15.2),
    ]
    for g_name, gx, gy in gate_coords:
        fence_objs.append(
            spawn_bevel_box(
                f"ParkPier_{g_name}",
                (0.88, 0.88, 2.65),
                (gx, gy, 1.325),
                mats["Limestone_Quoin_Ashlar"],
                col_pub,
                bevel=0.006,
                role="park_gateway",
            )
        )
        fence_objs.append(
            spawn_bevel_box(
                f"ParkPierCap_{g_name}",
                (1.04, 1.04, 0.18),
                (gx, gy, 2.74),
                mats["Limestone_Quoin_Ashlar"],
                col_pub,
                bevel=0.005,
                role="park_gateway",
            )
        )
        fence_objs.append(
            spawn_lathe(
                f"ParkPierFinial_{g_name}",
                [(0.0, 0.0), (0.28, 0.0), (0.18, 0.14), (0.32, 0.36), (0.24, 0.56), (0.0, 0.66)],
                (gx, gy, 2.83),
                mats["Limestone_Quoin_Ashlar"],
                col_pub,
                segments=14,
                role="park_gateway",
            )
        )

    # =========================================================================
    # 3. FROZEN DUCK POND & ARCHED ASHLAR STONE FOOTBRIDGE (X = 104.0, Y = 0.0)
    # =========================================================================
    pond_cx, pond_cy = 104.0, 0.0
    # Dark mirror-specular frozen pond ice sheet (16.5 x 11.2 m)
    pond_bridge_objs.append(
        spawn_bevel_box(
            "Schlosspark_FrozenPond_Ice",
            (16.5, 11.2, 0.04),
            (pond_cx, pond_cy, 0.025),
            mats["Puddle_Water_Film"],
            col_pub,
            bevel=0.005,
            role="pond_ice",
        )
    )
    # Stone pond coping ring & snow-crusted shoreline boulders + winter reeds
    for b_i in range(28):
        ang = 2.0 * math.pi * b_i / 28.0
        bx = pond_cx + 8.3 * math.cos(ang)
        by = pond_cy + 5.6 * math.sin(ang)
        pond_bridge_objs.append(
            spawn_bevel_box(
                f"PondShoreStone_{b_i:02d}",
                (1.65, 0.95, 0.28),
                (bx, by, 0.12),
                mats["Granite_Kerb_Weathered"],
                col_pub,
                rot_z=ang + math.pi / 2.0,
                bevel=0.025,
                role="pond_coping",
            )
        )
        pond_bridge_objs.append(
            spawn_bevel_box(
                f"PondShoreSnow_{b_i:02d}",
                (1.45, 0.78, 0.065),
                (bx, by, 0.28),
                mats["Snow_Fresh_Perch"],
                col_pub,
                rot_z=ang + math.pi / 2.0,
                bevel=0.015,
                role="snow_perch",
            )
        )
        if b_i % 2 == 0:
            for r_k in range(4):
                pond_bridge_objs.append(
                    spawn_bevel_box(
                        f"PondReed_{b_i:02d}_{r_k}",
                        (0.035, 0.035, 0.78 + (r_k % 2) * 0.18),
                        (bx * 0.98 + r_k * 0.08, by * 0.96, 0.42),
                        mats["Bark_Deciduous_Winter"],
                        col_pub,
                        bevel=0.002,
                        role="reed",
                    )
                )

    # Arched Ashlar Stone Footbridge spanning East-West across the pond narrows (X = 96.0 .. 112.0, Y = 0.0)
    n_arch_segs = 17
    for a_i in range(n_arch_segs):
        t = (a_i / (n_arch_segs - 1)) * 2.0 - 1.0  # -1.0 .. +1.0
        ax = pond_cx + t * 7.6
        arch_z = 0.12 + (1.0 - t * t) * 1.08  # rises to +1.20 m at center crown
        # Deck stone slab + snow strip
        pond_bridge_objs.append(
            spawn_bevel_box(
                f"BridgeDeckSeg_{a_i:02d}",
                (1.02, 3.20, 0.24),
                (ax, pond_cy, arch_z),
                mats["Limestone_Quoin_Ashlar"],
                col_pub,
                bevel=0.006,
                role="stone_bridge",
            )
        )
        # Arch spandrel wall & voussoir stones on North & South bridge faces
        for sy in (-1.52, 1.52):
            pond_bridge_objs.append(
                spawn_bevel_box(
                    f"BridgeParapetPlinth_{a_i:02d}_{sy:+.1f}",
                    (1.00, 0.24, 0.36),
                    (ax, pond_cy + sy, arch_z + 0.22),
                    mats["Limestone_Quoin_Ashlar"],
                    col_pub,
                    bevel=0.004,
                    role="stone_bridge",
                )
            )
            # Turned stone balusters + top coping rail + snow cap
            for bal_sub in (-0.24, 0.24):
                pond_bridge_objs.append(
                    spawn_lathe(
                        f"BridgeBaluster_{a_i:02d}_{sy:+.1f}_{bal_sub:+.2f}",
                        [(0.07, 0.0), (0.05, 0.12), (0.08, 0.32), (0.05, 0.52), (0.07, 0.64), (0.0, 0.65)],
                        (ax + bal_sub, pond_cy + sy, arch_z + 0.38),
                        mats["Limestone_Quoin_Ashlar"],
                        col_pub,
                        segments=10,
                        role="stone_bridge",
                    )
                )
            pond_bridge_objs.append(
                spawn_bevel_box(
                    f"BridgeHandrail_{a_i:02d}_{sy:+.1f}",
                    (1.02, 0.28, 0.11),
                    (ax, pond_cy + sy, arch_z + 1.06),
                    mats["Limestone_Quoin_Ashlar"],
                    col_pub,
                    bevel=0.004,
                    role="stone_bridge",
                )
            )
            pond_bridge_objs.append(
                spawn_bevel_box(
                    f"BridgeRailSnow_{a_i:02d}_{sy:+.1f}",
                    (0.98, 0.22, 0.036),
                    (ax, pond_cy + sy, arch_z + 1.13),
                    mats["Snow_Fresh_Perch"],
                    col_pub,
                    bevel=0.004,
                    role="snow_perch",
                )
            )

    # =========================================================================
    # 4. VICTORIAN OCTAGONAL CAST-IRON & COPPER PARK BANDSTAND (X = 68.0, Y = 1.5)
    # =========================================================================
    bs_x, bs_y = 68.0, 1.5
    # 3-step octagonal stone plinth
    for st_i, (r_st, z_st) in enumerate(((4.20, 0.10), (3.85, 0.28), (3.55, 0.46))):
        bandstand_objs.append(
            spawn_lathe(
                f"Bandstand_Plinth_{st_i}",
                [(0.0, 0.0), (r_st, 0.0), (r_st, 0.18), (0.0, 0.18)],
                (bs_x, bs_y, z_st - 0.09),
                mats["Limestone_Quoin_Ashlar"],
                col_pub,
                segments=8,
                role="bandstand",
            )
        )
    # 8 Fluted Cast-Iron Columns + Ornate Railing Panels + Festoon Lights
    for c_i in range(8):
        ang = 2.0 * math.pi * c_i / 8.0 + math.pi / 8.0
        col_x = bs_x + 3.15 * math.cos(ang)
        col_y = bs_y + 3.15 * math.sin(ang)
        bandstand_objs.append(
            spawn_lathe(
                f"Bandstand_Col_{c_i}",
                [(0.18, 0.0), (0.13, 0.35), (0.11, 3.15), (0.20, 3.45), (0.0, 3.50)],
                (col_x, col_y, 0.55),
                mats["Cast_Iron_Black"],
                col_pub,
                segments=12,
                role="bandstand",
            )
        )
        # Warm festoon bulb under each eave corner
        bandstand_objs.append(
            spawn_bevel_box(
                f"Bandstand_Bulb_{c_i}",
                (0.11, 0.11, 0.14),
                (bs_x + 2.85 * math.cos(ang), bs_y + 2.85 * math.sin(ang), 3.82),
                mats["Emitter_Festive_2400K"],
                col_pub,
                bevel=0.004,
                role="festoon_bulb",
            )
        )
        if c_i != 4:  # Leave West bay open for stairs
            nxt_ang = ang + math.pi / 4.0
            mx = bs_x + 2.92 * math.cos(ang + math.pi / 8.0)
            my = bs_y + 2.92 * math.sin(ang + math.pi / 8.0)
            bandstand_objs.append(
                spawn_bevel_box(
                    f"Bandstand_Railing_{c_i}",
                    (2.25, 0.07, 0.88),
                    (mx, my, 1.00),
                    mats["Cast_Iron_Black"],
                    col_pub,
                    rot_z=ang + math.pi / 8.0 + math.pi / 2.0,
                    bevel=0.003,
                    role="bandstand",
                )
            )
    # Patinated Copper Domed Roof + Snow Cap + Gold Finial Spire
    bandstand_objs.append(
        spawn_lathe(
            "Bandstand_CopperDome",
            [(0.0, 0.0), (3.75, 0.0), (3.40, 0.35), (2.45, 1.15), (1.10, 1.85), (0.22, 2.35), (0.0, 2.45)],
            (bs_x, bs_y, 4.02),
            mats["Roof_Copper_Patina"],
            col_pub,
            segments=16,
            role="bandstand",
        )
    )
    bandstand_objs.append(
        spawn_lathe(
            "Bandstand_RoofSnow",
            [(0.25, 2.36), (1.15, 1.88), (2.48, 1.18), (3.35, 0.39), (2.40, 1.24), (1.10, 1.94), (0.20, 2.40)],
            (bs_x, bs_y, 4.02),
            mats["Snow_Fresh_Perch"],
            col_pub,
            segments=16,
            role="snow_perch",
        )
    )
    bandstand_objs.append(
        spawn_lathe(
            "Bandstand_GoldFinial",
            [(0.06, 0.0), (0.04, 0.45), (0.14, 0.65), (0.03, 0.95), (0.0, 1.15)],
            (bs_x, bs_y, 6.42),
            mats["Gold_Sign_Leaf"],
            col_pub,
            segments=12,
            role="bandstand",
        )
    )
    spawn_blender_light(
        "Bandstand_WarmLight",
        "POINT",
        energy=420.0,
        kelvin=2400.0,
        loc=(bs_x, bs_y, 3.65),
        coll=col_pub,
        size=0.45,
    )

    # =========================================================================
    # 5. 36 ADDITIONAL PARK & BOULEVARD TREES (20 Deciduous + 16 Snow Spruces)
    # =========================================================================
    decid_coords = [
        # North & South Lindenallee Boulevard Avenues
        (54.0, 21.8), (66.0, 21.8), (78.0, 21.8), (90.0, 21.8), (102.0, 21.8), (114.0, 21.8),
        (54.0, -21.8), (66.0, -21.8), (78.0, -21.8), (90.0, -21.8), (102.0, -21.8), (114.0, -21.8),
        # Inside Schlosspark along pathways
        (58.0, 6.5), (76.0, 6.5), (91.0, 7.5), (115.0, 7.5),
        (58.0, -6.5), (76.0, -6.5), (91.0, -7.5), (115.0, -7.5),
    ]
    for dt_i, (tx, ty) in enumerate(decid_coords, 13):
        t_objs: list[bpy.types.Object] = []
        t_objs.append(
            spawn_bevel_box(
                f"ParkTreeGrate_{dt_i:02d}",
                (1.45, 1.45, 0.03),
                (tx, ty, 0.025),
                mats["Cast_Iron_Black"],
                col_pub,
                bevel=0.002,
                role="tree_grate",
            )
        )
        t_objs.append(
            spawn_lathe(
                f"ParkTreeTrunk_{dt_i:02d}",
                [(0.32, 0.0), (0.24, 0.45), (0.20, 1.8), (0.17, 3.4), (0.12, 5.2), (0.06, 6.6), (0.0, 6.8)],
                (tx, ty, 0.02),
                mats["Bark_Deciduous_Winter"],
                col_pub,
                segments=12,
                role="deciduous_tree",
            )
        )
        # Connected winter branch crown tiers centered on the trunk axis (no floating vertical sticks)
        for c_tier, (cz_off, r_in, r_out, ch_t) in enumerate((
            (3.20, 0.16, 1.45, 0.85),
            (4.15, 0.14, 1.85, 0.95),
            (5.10, 0.11, 1.55, 0.85),
            (5.95, 0.07, 1.05, 0.65),
        )):
            t_objs.append(
                spawn_lathe(
                    f"ParkTreeCrown_{dt_i:02d}_{c_tier}",
                    [(r_in, 0.0), (r_out * 0.65, ch_t * 0.45), (r_out, ch_t * 0.82), (r_out * 0.88, ch_t), (r_in * 0.7, ch_t * 0.35)],
                    (tx, ty, cz_off),
                    mats["Bark_Deciduous_Winter"],
                    col_pub,
                    segments=10,
                    role="deciduous_tree",
                )
            )
            t_objs.append(
                spawn_lathe(
                    f"ParkTreeCrownSnow_{dt_i:02d}_{c_tier}",
                    [(r_out * 0.55, ch_t * 0.48), (r_out * 0.96, ch_t * 0.85), (r_out * 0.84, ch_t * 1.03), (r_out * 0.50, ch_t * 0.54)],
                    (tx, ty, cz_off + 0.02),
                    mats["Snow_Fresh_Perch"],
                    col_pub,
                    segments=10,
                    role="snow_perch",
                )
            )
        join_mesh_objects(t_objs, f"DECIDUOUS_TREE_{dt_i:02d}", role="deciduous_tree")

    spruce_coords = [
        (61.5, 11.0, 6.8), (64.5, -10.5, 7.4), (72.5, 11.5, 6.2), (74.0, -11.0, 8.0),
        (80.5, 9.5, 5.8), (81.0, -9.5, 6.6), (95.0, 10.5, 7.6), (96.0, -10.5, 7.2),
        (104.0, 11.8, 8.4), (104.0, -11.8, 7.8), (112.5, 10.2, 6.5), (113.0, -10.2, 7.0),
        (119.0, 6.0, 6.2), (119.0, -6.0, 6.8), (126.5, 11.5, 7.5), (126.5, -11.5, 7.2),
    ]
    for sp_i, (sx, sy, sh) in enumerate(spruce_coords, 1):
        spruce_tree_objs.append(
            spawn_lathe(
                f"ParkSpruceTrunk_{sp_i:02d}",
                [(0.22, 0.0), (0.16, sh * 0.85), (0.0, sh)],
                (sx, sy, 0.02),
                mats["Bark_Deciduous_Winter"],
                col_pub,
                segments=10,
                role="park_spruce",
            )
        )
        for tier in range(7):
            tz = 0.75 + tier * ((sh - 1.1) / 7.0)
            tr = (1.95 - tier * 0.22) * (sh / 7.0)
            th = (0.95 - tier * 0.06) * (sh / 7.0)
            spruce_tree_objs.append(
                spawn_lathe(
                    f"ParkSpruceBough_{sp_i:02d}_{tier}",
                    [(0.0, 0.0), (tr, 0.0), (tr * 0.62, th * 0.55), (0.12, th), (0.0, th)],
                    (sx, sy, tz),
                    mats["Needles_Fir_Green"],
                    col_pub,
                    segments=12,
                    role="park_spruce",
                )
            )
            spruce_tree_objs.append(
                spawn_lathe(
                    f"ParkSpruceSnow_{sp_i:02d}_{tier}",
                    [(0.18, th * 0.86), (tr * 0.76, th * 0.22), (tr * 0.84, th * 0.28), (0.18, th * 0.92)],
                    (sx, sy, tz + 0.03),
                    mats["Snow_Fresh_Perch"],
                    col_pub,
                    segments=12,
                    role="snow_perch",
                )
            )

    # =========================================================================
    # 6. UTILITY POLES, TRAM CATENARY WIRES, STREET LAMPS, PHONES & FURNITURE
    # =========================================================================
    # 18 Cast-Iron Tram Catenary & Utility Poles (X = +42..+127 m along Y = +22.2 m and Y = +16.8 m)
    catenary_x = [42.0 + i * 10.5 for i in range(9)]
    for p_idx, px in enumerate(catenary_x):
        for side_i, py in enumerate((22.2, 16.8)):
            pole_num = p_idx * 2 + side_i + 1
            pole_wire_objs.append(
                spawn_lathe(
                    f"UtilityPole_{pole_num:02d}",
                    [(0.20, 0.0), (0.16, 0.65), (0.12, 1.2), (0.09, 5.8), (0.07, 6.8), (0.0, 6.9)],
                    (px, py, 0.05),
                    mats["Cast_Iron_Black"],
                    col_pub,
                    segments=12,
                    role="utility_pole",
                )
            )
            # Cross-arm + white ceramic insulators
            pole_wire_objs.append(
                spawn_bevel_box(
                    f"UtilityCrossArm_{pole_num:02d}",
                    (0.10, 1.45, 0.10),
                    (px, py, 6.35),
                    mats["Cast_Iron_Black"],
                    col_pub,
                    bevel=0.003,
                    role="utility_pole",
                )
            )
            for ins_y in (-0.55, 0.0, 0.55):
                pole_wire_objs.append(
                    spawn_bevel_box(
                        f"Insulator_{pole_num:02d}_{ins_y:+.2f}",
                        (0.08, 0.08, 0.16),
                        (px, py + ins_y, 6.48),
                        mats["Porcelain_Sanitary"],
                        col_pub,
                        bevel=0.004,
                        role="utility_pole",
                    )
                )
        # Span wire across the tramway at Z = 5.85 m + contact wire drop
        pole_wire_objs.append(
            spawn_bevel_box(
                f"CatenaryCrossSpan_{p_idx:02d}",
                (0.04, 5.40, 0.04),
                (px, 19.50, 5.85),
                mats["Brushed_Steel"],
                col_pub,
                bevel=0.002,
                role="catenary_wire",
            )
        )
    # Continuous overhead contact wire + messenger cable + utility lines from X = 38 to 130 m
    pole_wire_objs.append(
        spawn_bevel_box(
            "TramContactWire_Main",
            (92.0, 0.035, 0.035),
            (84.0, 19.50, 5.65),
            mats["Aged_Brass"],
            col_pub,
            bevel=0.002,
            role="catenary_wire",
        )
    )
    pole_wire_objs.append(
        spawn_bevel_box(
            "TramMessengerWire_Main",
            (92.0, 0.030, 0.030),
            (84.0, 19.50, 6.15),
            mats["Brushed_Steel"],
            col_pub,
            bevel=0.002,
            role="catenary_wire",
        )
    )
    for u_line_y in (21.65, 22.75):
        pole_wire_objs.append(
            spawn_bevel_box(
                f"UtilityPowerLine_{u_line_y:.2f}",
                (92.0, 0.028, 0.028),
                (84.0, u_line_y, 6.48),
                mats["Cast_Iron_Black"],
                col_pub,
                bevel=0.001,
                role="catenary_wire",
            )
        )

    # Glazed Cast-Iron Tram Stop Shelter (`TRAM_STOP_01`) at (74.0, 21.6, 0.12)
    ts_x, ts_y, ts_z = 74.0, 21.55, 0.12
    pole_wire_objs.append(
        spawn_bevel_box("TramShelter_Roof", (4.60, 1.65, 0.14), (ts_x, ts_y, ts_z + 2.65), mats["Painted_Metal_Green"], col_pub, bevel=0.006, role="tram_shelter")
    )
    pole_wire_objs.append(
        spawn_bevel_box("TramShelter_RoofSnow", (4.48, 1.54, 0.04), (ts_x, ts_y, ts_z + 2.74), mats["Snow_Fresh_Perch"], col_pub, bevel=0.005, role="snow_perch")
    )
    pole_wire_objs.append(
        spawn_bevel_box("TramShelter_BackGlass", (4.30, 0.04, 2.25), (ts_x, ts_y + 0.72, ts_z + 1.35), mats["Architectural_Glass"], col_pub, bevel=0.003, role="tram_shelter")
    )
    for post_dx in (-2.15, 0.0, 2.15):
        pole_wire_objs.append(
            spawn_bevel_box(f"TramShelter_Post_{post_dx:+.2f}", (0.09, 0.09, 2.60), (ts_x + post_dx, ts_y + 0.72, ts_z + 1.30), mats["Painted_Metal_Green"], col_pub, bevel=0.003, role="tram_shelter")
        )
    pole_wire_objs.append(
        spawn_bevel_box("TramShelter_SignBoard", (0.45, 0.45, 0.55), (ts_x - 2.55, ts_y - 0.35, ts_z + 2.35), mats["Emitter_Warm_2700K"], col_pub, bevel=0.004, role="tram_shelter")
    )
    pole_wire_objs.append(
        spawn_bevel_box("TramShelter_SignPole", (0.07, 0.07, 2.35), (ts_x - 2.55, ts_y - 0.35, ts_z + 1.18), mats["Painted_Metal_Green"], col_pub, bevel=0.002, role="tram_shelter")
    )

    # 2 Classic Glazed Red/Green Cast-Iron Telephone Booths & 3 Litfaßsäulen Poster Columns
    for pb_i, (pbx, pby, pb_mat) in enumerate(((89.5, -22.2, mats["Painted_Metal_Burgundy"]), (60.5, 22.4, mats["Painted_Metal_Green"])), 1):
        pole_wire_objs.append(spawn_bevel_box(f"PhoneBooth_{pb_i}_Base", (1.02, 1.02, 0.85), (pbx, pby, 0.55), pb_mat, col_pub, bevel=0.006, role="phone_booth"))
        pole_wire_objs.append(spawn_bevel_box(f"PhoneBooth_{pb_i}_Glass", (0.94, 0.94, 1.25), (pbx, pby, 1.60), mats["Architectural_Glass"], col_pub, bevel=0.004, role="phone_booth"))
        pole_wire_objs.append(spawn_bevel_box(f"PhoneBooth_{pb_i}_Crown", (1.06, 1.06, 0.28), (pbx, pby, 2.36), pb_mat, col_pub, bevel=0.010, role="phone_booth"))
        pole_wire_objs.append(spawn_bevel_box(f"PhoneBooth_{pb_i}_Snow", (0.98, 0.98, 0.04), (pbx, pby, 2.52), mats["Snow_Fresh_Perch"], col_pub, bevel=0.005, role="snow_perch"))
        pole_wire_objs.append(spawn_bevel_box(f"PhoneBooth_{pb_i}_Light", (0.65, 0.65, 0.12), (pbx, pby, 2.15), mats["Emitter_Warm_2700K"], col_pub, bevel=0.003, role="phone_booth"))

    for lf_i, (lfx, lfy) in enumerate(((52.5, 22.5), (93.5, -22.4), (128.5, 10.5)), 1):
        pole_wire_objs.append(
            spawn_lathe(
                f"LitfassColumn_{lf_i}",
                [(0.68, 0.0), (0.62, 0.45), (0.58, 2.85), (0.66, 3.05), (0.42, 3.45), (0.0, 3.65)],
                (lfx, lfy, 0.12),
                mats["Plaster_Warm_Ochre"],
                col_pub,
                segments=16,
                role="poster_column",
            )
        )
        pole_wire_objs.append(
            spawn_lathe(
                f"LitfassRoof_{lf_i}",
                [(0.66, 3.00), (0.42, 3.45), (0.08, 3.68), (0.0, 3.75)],
                (lfx, lfy, 0.12),
                mats["Roof_Copper_Patina"],
                col_pub,
                segments=16,
                role="poster_column",
            )
        )

    # 6 Traffic Signal Posts at the Crosswalks
    for tl_i, (tlx, tly) in enumerate(((48.2, 22.0), (51.8, 17.0), (86.2, 22.0), (89.8, 17.0), (86.2, -17.0), (89.8, -22.0)), 1):
        pole_wire_objs.append(spawn_bevel_box(f"TrafficPost_{tl_i}", (0.10, 0.10, 3.20), (tlx, tly, 1.65), mats["Cast_Iron_Black"], col_pub, bevel=0.003, role="traffic_light"))
        pole_wire_objs.append(spawn_bevel_box(f"TrafficHead_{tl_i}", (0.26, 0.26, 0.78), (tlx, tly, 2.95), mats["Cast_Iron_Black"], col_pub, bevel=0.005, role="traffic_light"))
        pole_wire_objs.append(spawn_bevel_box(f"TrafficLens_{tl_i}", (0.28, 0.18, 0.18), (tlx, tly, 3.15), mats["Emitter_Festive_2400K"], col_pub, bevel=0.003, role="traffic_light"))

    # 20 Park & Boulevard Benches + 8 Waste Bins + 10 Parked Bicycles + 28 Bollards
    bench_locs = [
        (56.0, 2.4, 0.0), (62.0, 2.4, 0.0), (74.0, 2.4, 0.0), (80.0, 2.4, 0.0), (91.0, 2.4, 0.0), (116.0, 2.4, 0.0),
        (56.0, -2.4, math.pi), (62.0, -2.4, math.pi), (74.0, -2.4, math.pi), (80.0, -2.4, math.pi), (91.0, -2.4, math.pi), (116.0, -2.4, math.pi),
        (82.6, 6.5, -math.pi / 2.0), (82.6, 11.5, -math.pi / 2.0), (87.4, -6.5, math.pi / 2.0), (87.4, -11.5, math.pi / 2.0),
        (68.0, 22.8, 0.0), (92.0, 22.8, 0.0), (72.0, -22.8, math.pi), (98.0, -22.8, math.pi),
    ]
    for b_idx, (bx, by, brot) in enumerate(bench_locs, 25):
        _add_park_bench(pole_wire_objs, f"BENCH_{b_idx:02d}", bx, by, 0.06, brot, mats, col_pub)
        if b_idx % 3 == 0:
            pole_wire_objs.append(
                spawn_lathe(
                    f"ParkBin_{b_idx:02d}",
                    [(0.22, 0.0), (0.24, 0.78), (0.26, 0.85), (0.0, 0.85)],
                    (bx + 1.35, by, 0.06),
                    mats["Cast_Iron_Black"],
                    col_pub,
                    segments=12,
                    role="waste_bin",
                )
            )

    for bk_i in range(10):
        bkx = 91.5 + (bk_i % 5) * 0.65
        bky = -22.2 if bk_i < 5 else 22.2
        pole_wire_objs.append(spawn_bevel_box(f"D2_BikeRear_{bk_i}", (0.05, 0.64, 0.64), (bkx, bky - 0.35, 0.44), mats["Brushed_Steel"], col_pub, bevel=0.004, role="bicycle"))
        pole_wire_objs.append(spawn_bevel_box(f"D2_BikeFront_{bk_i}", (0.05, 0.64, 0.64), (bkx, bky + 0.35, 0.44), mats["Brushed_Steel"], col_pub, bevel=0.004, role="bicycle"))
        pole_wire_objs.append(spawn_bevel_box(f"D2_BikeFrame_{bk_i}", (0.05, 0.72, 0.42), (bkx, bky, 0.65), mats["Painted_Metal_Burgundy" if bk_i % 2 == 0 else "Painted_Metal_Navy"], col_pub, bevel=0.003, role="bicycle"))
        pole_wire_objs.append(spawn_bevel_box(f"D2_BikeBar_{bk_i}", (0.48, 0.05, 0.05), (bkx, bky + 0.30, 0.98), mats["Chrome_Fixture"], col_pub, bevel=0.002, role="bicycle"))

    for bol_i in range(28):
        bol_x = 48.0 + (bol_i % 14) * 6.0
        bol_y = 22.0 if bol_i < 14 else -22.0
        pole_wire_objs.append(
            spawn_lathe(
                f"D2_Bollard_{bol_i:02d}",
                [(0.12, 0.0), (0.10, 0.15), (0.09, 0.78), (0.11, 0.86), (0.07, 0.95), (0.0, 0.98)],
                (bol_x, bol_y, 0.12),
                mats["Cast_Iron_Black"],
                col_pub,
                segments=10,
                role="bollard",
            )
        )

    # 28 Additional Boulevard & Park Street Lamps (`LAMP_25..52`)
    lamp_coords = [
        # North & South Lindenallee
        (48.0, 22.2), (60.0, 22.2), (72.0, 22.2), (84.0, 22.2), (96.0, 22.2), (108.0, 22.2), (120.0, 22.2),
        (48.0, -22.2), (60.0, -22.2), (72.0, -22.2), (84.0, -22.2), (96.0, -22.2), (108.0, -22.2), (120.0, -22.2),
        # Schlosspark Pathways & Stone Bridge Approaches
        (55.0, 2.2), (64.0, -2.2), (76.0, 2.2), (84.0, -2.2), (94.5, 2.2), (94.5, -2.2),
        (113.5, 2.2), (113.5, -2.2), (83.0, 10.5), (87.0, -10.5),
        # East Cross-Street
        (130.5, 16.0), (130.5, 5.0), (130.5, -5.0), (130.5, -16.0),
    ]
    for l_idx, (lx, ly) in enumerate(lamp_coords, 25):
        l_objs = build_street_lamp(
            f"LAMP_{l_idx:02d}",
            lx,
            ly,
            0.06,
            mats["Cast_Iron_Black"],
            mats["Architectural_Glass"],
            mats["Emitter_Warm_2700K"],
            mats["Snow_Fresh_Perch"],
            col_pub,
        )
        for o in l_objs:
            if o.type == "MESH":
                pole_wire_objs.append(o)

    # =========================================================================
    # 7. VEHICLES: ELECTRIC TRAM, 8 CARS & VANS, AND HORSE-DRAWN LANDAU CARRIAGE
    # =========================================================================
    _add_electric_tram(vehicle_objs, 74.0, 19.50, 0.02, mats, col_pub)

    car_specs = [
        ("CAR_05_SEDAN_NAVY", 56.5, 17.4, 0.02, 0.0, mats["Painted_Metal_Navy"], False, False),
        ("CAR_06_TAXI_CREAM", 88.5, 17.4, 0.02, 0.0, mats["Painted_Pine_Cream"], False, True),
        ("CAR_07_WAGON_BURGUNDY", 104.5, 17.4, 0.02, 0.0, mats["Painted_Metal_Burgundy"], False, False),
        ("CAR_08_COUPE_GREEN", 88.0, -19.2, 0.02, math.pi, mats["Painted_Metal_Green"], False, False),
        ("CAR_09_SEDAN_TEAL", 96.5, -19.2, 0.02, math.pi, mats["Painted_Pine_Teal"], False, False),
        ("CAR_10_SEDAN_ANTHR", 112.0, -19.2, 0.02, math.pi, mats["Cast_Iron_Black"], False, False),
        ("VAN_02_POST_DELIVERY", 62.0, 23.0, 0.12, 0.0, mats["Gold_Sign_Leaf"], True, False),
        ("VAN_03_MARKTHALLE", 78.0, -23.0, 0.12, math.pi, mats["Painted_Metal_Green"], True, False),
    ]
    for cname, vx, vy, vz, vrot, vmat, is_van, is_taxi in car_specs:
        _add_detailed_car(vehicle_objs, cname, vx, vy, vz, vrot, vmat, mats, col_pub, is_van=is_van, is_taxi=is_taxi)

    # Festive Horse-Drawn Landau Carriage (`CARRIAGE_01`) at (58.2, -18.8, 0.02) facing West (-X -> rot_z=pi)
    car_x, car_y, car_z = 58.2, -18.8, 0.02
    vehicle_objs.append(
        spawn_bevel_box("Carriage_Body", (2.85, 1.56, 0.72), (car_x, car_y, car_z + 0.88), mats["Painted_Metal_Burgundy"], col_pub, bevel=0.025, role="vehicle")
    )
    vehicle_objs.append(
        spawn_bevel_box("Carriage_GoldTrim", (2.90, 1.60, 0.08), (car_x, car_y, car_z + 1.18), mats["Gold_Sign_Leaf"], col_pub, bevel=0.005, role="vehicle")
    )
    vehicle_objs.append(
        spawn_bevel_box("Carriage_Seats", (1.65, 1.38, 0.36), (car_x + 0.15, car_y, car_z + 1.28), mats["Fabric_Velvet_Forest"], col_pub, bevel=0.015, role="vehicle")
    )
    vehicle_objs.append(
        spawn_bevel_box("Carriage_DriverBox", (0.72, 1.36, 0.52), (car_x - 1.05, car_y, car_z + 1.42), mats["Leather_Saddle_Brown"], col_pub, bevel=0.012, role="vehicle")
    )
    vehicle_objs.append(
        spawn_bevel_box("Carriage_FoldedHood", (0.95, 1.52, 0.68), (car_x + 1.02, car_y, car_z + 1.54), mats["Leather_Saddle_Brown"], col_pub, bevel=0.020, role="vehicle")
    )
    for c_wy in (-0.78, 0.78):
        # Coach lanterns
        vehicle_objs.append(
            spawn_bevel_box(f"Carriage_Lantern_{c_wy:+.2f}", (0.16, 0.16, 0.28), (car_x - 1.25, car_y + c_wy, car_z + 1.58), mats["Emitter_Festive_2400K"], col_pub, bevel=0.005, role="vehicle")
        )
        # Spoked front & rear wheels
        for c_wx, w_rad in ((-1.05, 0.44), (1.05, 0.56)):
            vehicle_objs.append(
                spawn_bevel_box(
                    f"Carriage_Wheel_{c_wx:+.2f}_{c_wy:+.2f}",
                    (w_rad * 2.0, 0.09, w_rad * 2.0),
                    (car_x + c_wx, car_y + c_wy, car_z + w_rad),
                    mats["Walnut_Dark_Joinery"],
                    col_pub,
                    bevel=0.015,
                    role="vehicle",
                )
            )
            vehicle_objs.append(
                spawn_bevel_box(
                    f"Carriage_Hub_{c_wx:+.2f}_{c_wy:+.2f}",
                    (0.24, 0.14, 0.24),
                    (car_x + c_wx, car_y + c_wy, car_z + w_rad),
                    mats["Aged_Brass"],
                    col_pub,
                    bevel=0.006,
                    role="vehicle",
                )
            )
        # Wooden draw shafts extending to the 2 draught horses
        vehicle_objs.append(
            spawn_bevel_box(f"Carriage_Shaft_{c_wy:+.2f}", (2.60, 0.07, 0.07), (car_x - 2.45, car_y + c_wy * 0.75, car_z + 1.05), mats["Walnut_Dark_Joinery"], col_pub, bevel=0.003, role="vehicle")
        )

    # =========================================================================
    # 8. 34 SCULPTED 3D ANIMALS (Dogs, Horses, Cats, Ducks, Pigeons, Squirrels)
    # =========================================================================
    # 2 Harnessed Draught Horses pulling `CARRIAGE_01` at (54.6, -18.25) and (54.6, -19.35)
    _add_draught_horse(animal_objs, "ANIMAL_HORSE_01", 54.6, -18.25, 0.02, math.pi, mats["Walnut_Dark_Joinery"], mats, col_pub)
    _add_draught_horse(animal_objs, "ANIMAL_HORSE_02", 54.6, -19.35, 0.02, math.pi, mats["Oak_Joinery_Warm"], mats, col_pub)

    # 8 Dogs along Schlosspark pathways, footbridge, bandstand, and Winterlichtplatz
    dog_specs = [
        ("ANIMAL_DOG_01", 78.2, 0.15, 0.08, -0.35, mats["Bakery_Bread_Crust"], 1.15),
        ("ANIMAL_DOG_02", 79.4, -0.38, 0.08, 0.25, mats["Walnut_Dark_Joinery"], 1.05),
        ("ANIMAL_DOG_03", 80.8, 0.32, 0.08, 2.75, mats["Painted_Pine_Cream"], 1.00),
        ("ANIMAL_DOG_04", 65.5, -2.8, 0.08, 0.85, mats["Oak_Joinery_Warm"], 1.00),
        ("ANIMAL_DOG_05", 71.5, 22.4, 0.12, 0.05, mats["Cast_Iron_Black"], 0.85),
        ("ANIMAL_DOG_06", 86.5, -22.2, 0.12, math.pi, mats["Bakery_Bread_Crust"], 1.00),
        ("ANIMAL_DOG_07", -6.5, 11.2, 0.015, 0.65, mats["Walnut_Dark_Joinery"], 0.95),
        ("ANIMAL_DOG_08", 11.5, -9.5, 0.015, -1.10, mats["Oak_Joinery_Warm"], 0.90),
    ]
    for dname, dx, dy, dz, drot, dmat, dsc in dog_specs:
        _add_dog(animal_objs, dname, dx, dy, dz, drot, dmat, mats, col_pub, scale=dsc)

    # 4 Cats perched on park piers & warm shopfront steps
    cat_specs = [
        ("ANIMAL_CAT_01", 82.8, -14.5, 0.42, 1.57, mats["Terracotta_Pot"]),
        ("ANIMAL_CAT_02", 51.5, -1.4, 0.42, 0.0, mats["Cast_Iron_Black"]),
        ("ANIMAL_CAT_03", 68.5, 25.4, 0.14, -1.57, mats["Painted_Pine_Cream"]),
        ("ANIMAL_CAT_04", 133.2, -1.2, 0.14, 3.14, mats["Plaster_Guild_Grey"]),
    ]
    for cname, cx, cy, cz, crot, cmat in cat_specs:
        _add_dog(animal_objs, cname, cx, cy, cz, crot, cmat, mats, col_pub, scale=0.52)

    # 18 Winter Birds: 10 Mallard Ducks by the Frozen Pond & Bridge + 8 City Pigeons
    for b_i in range(18):
        is_duck = b_i < 10
        if is_duck:
            ang = -1.2 + b_i * 0.24
            bx = 104.0 + 6.4 * math.cos(ang)
            by = 0.0 + 4.2 * math.sin(ang)
            bz = 0.06
        else:
            bx = 64.0 + (b_i - 10) * 3.2
            by = 1.15 if b_i % 2 == 0 else -1.15
            bz = 0.08
        _add_waterfowl_or_pigeon(animal_objs, f"ANIMAL_BIRD_{b_i+1:02d}", bx, by, bz, b_i * 0.75, is_duck, mats, col_pub)

    # 2 Red Squirrels on Park Benches
    for sq_i, (sqx, sqy) in enumerate(((62.4, 2.4), (74.4, -2.4)), 1):
        _add_dog(animal_objs, f"ANIMAL_SQUIRREL_{sq_i:02d}", sqx, sqy, 0.48, sq_i * 1.2, mats["Terracotta_Pot"], mats, col_pub, scale=0.34)

    # =========================================================================
    # 9. JOIN GROUPS INTO CONSOLIDATED MESH OBJECTS FOR FAST MEMORY-SAFE RENDERS
    # =========================================================================
    join_mesh_objects(ground_objs, "PARK_GROUND_AND_PATHS", role="park_terrain")
    join_mesh_objects(fence_objs, "PARK_FENCE_AND_GATES", role="park_fence")
    join_mesh_objects(pond_bridge_objs, "PARK_POND_AND_BRIDGE", role="stone_bridge")
    join_mesh_objects(bandstand_objs, "PARK_BANDSTAND", role="bandstand")
    join_mesh_objects(spruce_tree_objs, "PARK_TREES_SPRUCE", role="park_spruce")
    join_mesh_objects(pole_wire_objs, "BOULEVARD_POLES_AND_WIRES", role="utility_pole")
    join_mesh_objects(vehicle_objs, "CITY_VEHICLES_D2", role="vehicle")
    anim_joined = join_mesh_objects(animal_objs, "CITY_ANIMALS", role="animal")
    if anim_joined is not None and anim_joined.data is not None:
        import bmesh
        bpy.context.view_layer.objects.active = anim_joined
        mod = anim_joined.modifiers.new(name="AnimalSmooth", type="SUBSURF")
        mod.levels = 2
        mod.render_levels = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bm = bmesh.new()
        bm.from_mesh(anim_joined.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        deg = [f for f in bm.faces if f.calc_area() < 1e-8]
        if deg:
            bmesh.ops.delete(bm, geom=deg, context="FACES")
        for f in bm.faces:
            f.smooth = True
        bm.to_mesh(anim_joined.data)
        bm.free()
        anim_joined.data.update()

    return {
        "deciduous_trees_added": 20,
        "spruce_trees_added": 16,
        "utility_poles_added": 18,
        "lamps_added": 28,
        "benches_added": 20,
        "vehicles_added": 10,
        "animals_added": 34,
    }
