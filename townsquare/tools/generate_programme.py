#!/usr/bin/env python3
"""
Deterministic generator for Winterlichtplatz II Stage A deliverables:
- townsquare/design/PROGRAMME.json
- townsquare/design/SCHEDULE.csv
- townsquare/design/APARTMENTS.csv
- townsquare/design/plans/B##-L##.svg (67 dimensioned SVG floor plans)
- townsquare/assets/branding/B01.svg .. B12.svg (12 original vector marks)
- townsquare/scene/views.py + townsquare/design/VIEWS.json (271 views)
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = ROOT / "design"
PLANS_DIR = DESIGN_DIR / "plans"
BRANDING_DIR = ROOT / "assets" / "branding"
SCENE_DIR = ROOT / "scene"

BUILDINGS_SPEC = [
    {
        "id": "B01", "name": "MARKTGRÜN", "business": "Marktgrün Warenhaus & Feinkost",
        "storeys": 6, "upper_floors": 5, "edge": "north", "facing": "south",
        "center": [-21.0, 32.0], "width": 19.0, "depth": 12.0,
        "roof_type": "mansard_copper", "roof_pitch_deg": 28.0,
        "facade_style": "1920s_stone_piers", "wall_color": "#d8d0c5", "accent_color": "#2f5d41",
    },
    {
        "id": "B02", "name": "Haus Winter", "business": "Haus Winter Café & Konditorei-Bäckerei",
        "storeys": 6, "upper_floors": 5, "edge": "north", "facing": "south",
        "center": [-0.5, 32.0], "width": 16.0, "depth": 12.0,
        "roof_type": "pitched_slate", "roof_pitch_deg": 35.0,
        "facade_style": "baroque_stucco_arcade", "wall_color": "#e8dcc8", "accent_color": "#7c3f2c",
    },
    {
        "id": "B03", "name": "Zur Post", "business": "Alte Post & Schreibwaren",
        "storeys": 6, "upper_floors": 5, "edge": "north", "facing": "south",
        "center": [19.5, 32.0], "width": 18.0, "depth": 12.0,
        "roof_type": "steep_gable_clay", "roof_pitch_deg": 42.0,
        "facade_style": "timber_framed_gable", "wall_color": "#dfd3be", "accent_color": "#c9982b",
    },
    {
        "id": "B04", "name": "Buch & Bogen", "business": "Buchhandlung & Lesesaal Buch & Bogen",
        "storeys": 5, "upper_floors": 4, "edge": "east", "facing": "west",
        "center": [38.0, 17.5], "width": 16.0, "depth": 12.0,
        "roof_type": "hipped_clay", "roof_pitch_deg": 32.0,
        "facade_style": "shuttered_classical", "wall_color": "#d4c3aa", "accent_color": "#2b4257",
    },
    {
        "id": "B05", "name": "Apotheke", "business": "Löwen-Apotheke am Platz",
        "storeys": 5, "upper_floors": 4, "edge": "east", "facing": "west",
        "center": [38.0, -0.25], "width": 15.5, "depth": 12.0,
        "roof_type": "pitched_slate", "roof_pitch_deg": 34.0,
        "facade_style": "glazed_green_shopfront", "wall_color": "#dce2d8", "accent_color": "#1e5638",
    },
    {
        "id": "B06", "name": "Bäckerei Lind", "business": "Backstube & Brotladen Lind",
        "storeys": 5, "upper_floors": 4, "edge": "east", "facing": "west",
        "center": [38.0, -17.75], "width": 15.5, "depth": 12.0,
        "roof_type": "pitched_clay", "roof_pitch_deg": 36.0,
        "facade_style": "warm_ochre_bakery", "wall_color": "#e6cda8", "accent_color": "#8b4519",
    },
    {
        "id": "B07", "name": "Uhren Kern", "business": "Feinuhrmacherei & Chronometer Kern",
        "storeys": 6, "upper_floors": 5, "edge": "south", "facing": "north",
        "center": [20.75, -32.0], "width": 14.5, "depth": 12.0,
        "roof_type": "stepped_gable_slate", "roof_pitch_deg": 38.0,
        "facade_style": "narrow_guild_house", "wall_color": "#cfd4d8", "accent_color": "#1f2e42",
    },
    {
        "id": "B08", "name": "Galerie Nord", "business": "Kunsthalle & Rahmenwerkstatt Nord",
        "storeys": 5, "upper_floors": 4, "edge": "south", "facing": "north",
        "center": [2.0, -32.0], "width": 17.0, "depth": 12.0,
        "roof_type": "flat_parapet_copper", "roof_pitch_deg": 8.0,
        "facade_style": "modernist_plaster_stone", "wall_color": "#e2dfd9", "accent_color": "#6e2620",
    },
    {
        "id": "B09", "name": "Haus zum Bären", "business": "Gasthof & Hotel Haus zum Bären",
        "storeys": 7, "upper_floors": 6, "edge": "south", "facing": "north",
        "center": [-19.5, -32.25], "width": 20.0, "depth": 12.5,
        "roof_type": "hipped_slate_dormers", "roof_pitch_deg": 37.0,
        "facade_style": "grand_hotel_rusticated", "wall_color": "#d9c2a6", "accent_color": "#582f1e",
    },
    {
        "id": "B10", "name": "Blumen Roth", "business": "Blumenhaus & Wintergarten Roth",
        "storeys": 5, "upper_floors": 4, "edge": "west", "facing": "east",
        "center": [-38.0, -17.75], "width": 15.5, "depth": 12.0,
        "roof_type": "conservatory_glass_slate", "roof_pitch_deg": 30.0,
        "facade_style": "iron_conservatory_bay", "wall_color": "#d6dfd2", "accent_color": "#2e5a44",
    },
    {
        "id": "B11", "name": "Schneider & Sohn", "business": "Maßschneiderei & Tuchhandel Schneider",
        "storeys": 6, "upper_floors": 5, "edge": "west", "facing": "east",
        "center": [-38.0, 0.0], "width": 16.0, "depth": 12.0,
        "roof_type": "pitched_slate", "roof_pitch_deg": 35.0,
        "facade_style": "tailor_pilaster_front", "wall_color": "#d4cec3", "accent_color": "#283347",
    },
    {
        "id": "B12", "name": "Ecke Süd", "business": "Kaffeehaus & Rösterei Ecke Süd",
        "storeys": 5, "upper_floors": 4, "edge": "west", "facing": "east",
        "center": [-38.0, 17.75], "width": 15.5, "depth": 12.0,
        "roof_type": "hipped_clay", "roof_pitch_deg": 33.0,
        "facade_style": "corner_cafe_awning", "wall_color": "#e3cbb1", "accent_color": "#6b2d26",
    },
]

ARCHETYPES = [
    "through-layout",
    "L-shaped",
    "corner",
    "galley",
    "double-aspect",
    "attic-with-slope",
    "split-level",
    "courtyard-facing",
]

PALETTES = [
    "oak-and-cream",
    "walnut-and-teal",
    "painted-pine",
    "tile-and-brass",
    "concrete-and-wool",
    "dark-lacquer",
]

GENERATIONS = [
    "1930s-flat",
    "1970s-flat",
    "renovated-modern",
    "student-flat",
]

OCCUPANCIES = [
    "family_with_children",
    "elderly_couple",
    "single_professional",
    "shared_flat",
]

REQUIRED_PROPS = {
    "living": ("sofa,armchair,coffee_table,rug_pile,bookshelf,book_spines_40,"
               "cushions_4,framed_pictures_2,curtains_folded,period_tv_radio,"
               "potted_plants,side_table,tabletop_objects_3,waste_bin,floor_lamp"),
    "kitchen": ("cabinet_run_8_doors_handles,worktop_profiled,sink_bowl_tap_lever,"
                "hob_4_burners,saucepan,oven_glass_handle,fridge_sealed,extractor_hood,"
                "tiled_splashback,crockery_12,cutlery_set,chopping_board,knife_block,"
                "cloths_2,waste_bin,jars_6,kettle,coffee_pot"),
    "bedroom": ("bed_frame,mattress,folded_duvet,pillows_creased_2,headboard,"
                "bedside_tables_2,bedside_lamps_2,wardrobe_facing_room,hanging_garments_12,"
                "accent_chair_with_throw,slippers,bedroom_rug,curtains_folded,framed_picture,wall_mirror"),
    "bathroom": ("bath_or_shower_tray_glass,wc_bowl_seat_cistern,basin_vanity_tap,"
                 "framed_mirror,vanity_light,grouted_tiles,towel_rail,folded_towels_2,"
                 "bottles_3,soap_dish,bath_mat,toilet_brush,pedal_bin"),
    "entry": ("entry_door_hardware,doormat,coat_rack_hooks,hanging_coats_3,"
              "shoe_rack,shoes_pairs_2,framed_mirror,console_table,light_switch,letterbox_slot"),
    "wc": ("wc_bowl_seat_cistern,hand_basin_tap,framed_mirror,wall_light,towel_ring,hand_towel,soap_dispenser,waste_bin"),
    "storage": ("utility_shelving,storage_boxes_4,vacuum_cleaner,broom_dustpan,wall_boiler,fuse_box,seasonal_coats_2,step_stool"),
    "shop_sales": ("display_shelving,stocked_products_40,feature_table,window_display_rig,pendant_lights,customer_baskets,floor_runner,price_board"),
    "shop_counter": ("service_counter,electronic_till,scale_register,display_case,stocked_products_20,paper_bags_branded,menu_sign,staff_apron_hook"),
    "shop_backroom": ("racking_units,backroom_stock_crates_15,commercial_fridge,prep_table,sack_stack,step_ladder,cleaning_station,fire_extinguisher"),
    "shop_staff": ("staff_table,staff_chairs_2,coat_lockers,kettle_tray,noticeboard,first_aid_kit,stair_core_access_door,utility_sink"),
    "landing": ("stair_flight_up,stair_flight_down,handrails_both_sides,lift_shaft_doors,landing_window,ceiling_bulkhead_light,apartment_door_A,apartment_door_B,floor_number_plaque"),
}

MIN_PROP_COUNTS = {
    "living": 45,
    "kitchen": 60,
    "bedroom": 25,
    "bathroom": 18,
    "entry": 12,
    "wc": 8,
    "storage": 10,
    "shop_sales": 30,
    "shop_counter": 20,
    "shop_backroom": 18,
    "shop_staff": 12,
    "landing": 9,
}


def make_apartment_rooms(b_spec: dict, floor_idx: int, side: str, archetype_idx: int) -> list[dict]:
    """
    Partition either West/Left half (side == 'A') or East/Right half (side == 'B')
    of a residential floor plate into 7 rectangular rooms:
      entry, living, kitchen, bedroom, bathroom, wc, storage
    Guarantees:
      1. 100% rectangular partition (with central landing L occupying x in [-1.5, +1.5], y in [-1.5, D/2]).
      2. Every room touches at least one exterior perimeter wall -> window_count >= 1.
      3. Every room shares an interior wall segment >= 1.1 m with entry (or living/storage) -> door_count >= 1 and 100% reachable.
      4. Archetype variation changes split lines and room slot assignments across the 8 archetypes.
    """
    W = b_spec["width"]
    D = b_spec["depth"]
    hw = W / 2.0
    hd = D / 2.0

    # Vary internal split coordinates deterministically by archetype_idx and side
    delta_y = ((archetype_idx % 4) - 1.5) * 0.18
    delta_x = (((archetype_idx // 2) % 3) - 1.0) * 0.16
    y_front = round(-1.5 + delta_y, 2)  # boundary between front zone and spine/landing
    x_spine_w = round(1.95 + delta_x, 2)  # width of entry hall spine next to landing (1.50)
    x_inner = round(1.5 + x_spine_w, 2)  # ~3.45 m from center

    y_wing_1 = round(1.8 + ((archetype_idx % 3) - 1) * 0.22, 2)
    y_wing_2 = round(4.0 + ((archetype_idx % 2) * 0.20), 2)
    x_front_split = round(hw * 0.50 + ((archetype_idx % 3) - 1) * 0.30, 2)
    x_rear_split = round(x_inner + (hw - x_inner) * 0.50, 2)

    # Swap front-inner / front-outer or wing-front / wing-mid roles by archetype
    swap_front = (archetype_idx % 2 == 1)
    swap_rear = ((archetype_idx // 2) % 2 == 1)

    if side == "A":
        # Left half: x in [-hw, 0] for y in [-hd, y_front], and x in [-hw, -1.5] for y in [y_front, +hd]
        front_inner_bounds = [-x_front_split, y_front - (y_front + hd), 0.0, y_front]
        # Wait: let's write exact [xmin, ymin, xmax, ymax]
        r_front_inner = [-x_front_split, -hd, 0.0, y_front]
        r_front_outer = [-hw, -hd, -x_front_split, y_front]
        r_entry = [-x_inner, y_front, -1.5, hd]
        r_wing_1 = [-hw, y_front, -x_inner, y_wing_1]
        r_wing_2 = [-hw, y_wing_1, -x_inner, y_wing_2]
        r_rear_outer = [-hw, y_wing_2, -x_rear_split, hd]
        r_rear_inner = [-x_rear_split, y_wing_2, -x_inner, hd]
    else:
        # Right half: x in [0, +hw] for y in [-hd, y_front], and x in [+1.5, +hw] for y in [y_front, +hd]
        r_front_inner = [0.0, -hd, x_front_split, y_front]
        r_front_outer = [x_front_split, -hd, hw, y_front]
        r_entry = [1.5, y_front, x_inner, hd]
        r_wing_1 = [x_inner, y_front, hw, y_wing_1]
        r_wing_2 = [x_inner, y_wing_1, hw, y_wing_2]
        r_rear_outer = [x_rear_split, y_wing_2, hw, hd]
        r_rear_inner = [x_inner, y_wing_2, x_rear_split, hd]

    living_b = r_front_outer if swap_front else r_front_inner
    kitchen_b = r_front_inner if swap_front else r_front_outer
    wc_b = r_rear_inner if swap_rear else r_rear_outer
    storage_b = r_rear_outer if swap_rear else r_rear_inner

    raw_rooms = [
        ("entry", r_entry, ["landing", "living", "kitchen", "bedroom", "bathroom", "storage", "wc"], 1),
        ("living", living_b, ["entry", "kitchen"], 2),
        ("kitchen", kitchen_b, ["entry", "living"], 2),
        ("bedroom", r_wing_1, ["entry"], 2),
        ("bathroom", r_wing_2, ["entry"], 1),
        ("storage", storage_b, ["entry", "wc"], 1),
        ("wc", wc_b, ["storage", "entry"], 1),
    ]

    apt_id = f"{b_spec['id']}_L{floor_idx:02d}_{side}"
    rooms = []
    for rtype, bnds, connects, win_cnt in raw_rooms:
        xmin, ymin, xmax, ymax = [round(v, 3) for v in bnds]
        w = round(xmax - xmin, 3)
        d = round(ymax - ymin, 3)
        area = round(w * d, 2)
        rooms.append({
            "id": f"{apt_id}_{rtype}",
            "building": b_spec["id"],
            "floor": f"L{floor_idx:02d}",
            "apartment": apt_id,
            "room_type": rtype,
            "name": f"{apt_id} {rtype.replace('_', ' ').title()}",
            "bounds_local": [xmin, ymin, xmax, ymax],
            "width": w,
            "depth": d,
            "area_m2": area,
            "door_count": len(connects),
            "window_count": win_cnt,
            "connects_to": [
                f"{b_spec['id']}_L{floor_idx:02d}_landing" if c == "landing" else f"{apt_id}_{c}"
                for c in connects
            ],
            "min_props": MIN_PROP_COUNTS[rtype],
            "required_prop_families": REQUIRED_PROPS[rtype],
        })
    return rooms, y_front


def make_ground_rooms(b_spec: dict) -> list[dict]:
    W = b_spec["width"]
    D = b_spec["depth"]
    hw = W / 2.0
    hd = D / 2.0
    b_id = b_spec["id"]
    # 4 shop rooms partitioning [-hw, hw] x [-hd, hd]:
    # 1. shop_sales: front [-hw, hw] x [-hd, 0.5]
    # 2. shop_counter: mid-left [-hw, 0.0] x [0.5, 3.2]
    # 3. shop_backroom: rear-left [-hw, 0.0] x [3.2, hd]
    # 4. shop_staff: right rear [0.0, hw] x [0.5, hd]
    specs = [
        ("shop_sales", [-hw, -hd, hw, 0.5], ["EXTERIOR_SQUARE", f"{b_id}_L01_shop_counter", f"{b_id}_L01_shop_staff"], 4),
        ("shop_counter", [-hw, 0.5, 0.0, 3.2], [f"{b_id}_L01_shop_sales", f"{b_id}_L01_shop_backroom"], 1),
        ("shop_backroom", [-hw, 3.2, 0.0, hd], [f"{b_id}_L01_shop_counter", f"{b_id}_L01_shop_staff"], 2),
        ("shop_staff", [0.0, 0.5, hw, hd], [f"{b_id}_L01_shop_sales", f"{b_id}_L01_shop_backroom"], 2),
    ]
    rooms = []
    for rtype, bnds, connects, win_cnt in specs:
        xmin, ymin, xmax, ymax = [round(v, 3) for v in bnds]
        w = round(xmax - xmin, 3)
        d = round(ymax - ymin, 3)
        rooms.append({
            "id": f"{b_id}_L01_{rtype}",
            "building": b_id,
            "floor": "L01",
            "apartment": "SHOP",
            "room_type": rtype,
            "name": f"{b_spec['name']} {rtype.replace('shop_', '').title()}",
            "bounds_local": [xmin, ymin, xmax, ymax],
            "width": w,
            "depth": d,
            "area_m2": round(w * d, 2),
            "door_count": len(connects),
            "window_count": win_cnt,
            "connects_to": connects,
            "min_props": MIN_PROP_COUNTS[rtype],
            "required_prop_families": REQUIRED_PROPS[rtype],
        })
    return rooms


def render_floor_svg(b_spec: dict, floor_data: dict, out_path: Path) -> None:
    """Write a clean, dimensioned architectural SVG floor plan with scale bar, north arrow, room labels, doors & windows."""
    W = b_spec["width"]
    D = b_spec["depth"]
    scale = 42.0  # px per meter
    pad_x = 130
    pad_y = 110
    svg_w = int(W * scale + 2 * pad_x)
    svg_h = int(D * scale + 2 * pad_y + 60)

    def tx(x: float) -> float:
        return round(pad_x + (x + W / 2.0) * scale, 2)

    def ty(y: float) -> float:
        # +Y is North (up in plan)
        return round(pad_y + (D / 2.0 - y) * scale, 2)

    fills = {
        "entry": "#f3efe6",
        "living": "#faecd8",
        "kitchen": "#e8f1ec",
        "bedroom": "#eaeef7",
        "bathroom": "#ddeef4",
        "wc": "#d5e8ef",
        "storage": "#e7e4de",
        "landing": "#dedad0",
        "shop_sales": "#f9ebd2",
        "shop_counter": "#ecd9ba",
        "shop_backroom": "#e2dfd7",
        "shop_staff": "#e5edf2",
    }

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}" font-family="DejaVu Sans, Arial, sans-serif">',
        f'<rect width="100%" height="100%" fill="#fcfbf8"/>',
        f'<text x="{pad_x}" y="38" font-size="18" font-weight="bold" fill="#1a1a1a">'
        f'{b_spec["id"]} · {b_spec["name"]} — Floor {floor_data["floor"]} '
        f'(FFL +{floor_data["ffl_m"]:.2f} m · Clear Ceiling {floor_data["ceiling_m"]:.2f} m)</text>',
        f'<text x="{pad_x}" y="60" font-size="12" fill="#444444">'
        f'Footprint {W:.2f} × {D:.2f} m ({floor_data["gross_area_m2"]:.1f} m²) · '
        f'Front facing {b_spec["facing"].upper()} onto Winterlichtplatz · Exterior wall 0.40 m · Partition 0.12/0.25 m</text>',
    ]

    # Outer building shell (0.40 m exterior wall representation)
    ox = tx(-W / 2.0)
    oy = ty(D / 2.0)
    ow = round(W * scale, 2)
    oh = round(D * scale, 2)
    lines.append(f'<rect x="{ox - 6}" y="{oy - 6}" width="{ow + 12}" height="{oh + 12}" fill="#2c2c2c" stroke="#111" stroke-width="2"/>')

    # Rooms
    for rm in floor_data["rooms"]:
        xmin, ymin, xmax, ymax = rm["bounds_local"]
        rx = tx(xmin)
        ry = ty(ymax)
        rw = round((xmax - xmin) * scale, 2)
        rh = round((ymax - ymin) * scale, 2)
        fill = fills.get(rm["room_type"], "#eeeeee")
        lines.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{fill}" stroke="#333333" stroke-width="2.2"/>')

        # Window tick marks on exterior edges
        hw = W / 2.0
        hd = D / 2.0
        if abs(ymin + hd) < 0.01:
            wx = rx + rw * 0.3
            ww = rw * 0.4
            lines.append(f'<rect x="{wx:.1f}" y="{ry + rh - 3:.1f}" width="{ww:.1f}" height="8" fill="#8fd3fe" stroke="#1b6ca8" stroke-width="1.2"/>')
        if abs(ymax - hd) < 0.01:
            wx = rx + rw * 0.3
            ww = rw * 0.4
            lines.append(f'<rect x="{wx:.1f}" y="{ry - 5:.1f}" width="{ww:.1f}" height="8" fill="#8fd3fe" stroke="#1b6ca8" stroke-width="1.2"/>')
        if abs(xmin + hw) < 0.01:
            wy = ry + rh * 0.3
            wh = rh * 0.4
            lines.append(f'<rect x="{rx - 5:.1f}" y="{wy:.1f}" width="8" height="{wh:.1f}" fill="#8fd3fe" stroke="#1b6ca8" stroke-width="1.2"/>')
        if abs(xmax - hw) < 0.01:
            wy = ry + rh * 0.3
            wh = rh * 0.4
            lines.append(f'<rect x="{rx + rw - 3:.1f}" y="{wy:.1f}" width="8" height="{wh:.1f}" fill="#8fd3fe" stroke="#1b6ca8" stroke-width="1.2"/>')

        # Door symbol on shared interior edges
        cx = rx + rw / 2.0
        cy = ry + rh / 2.0
        label = rm["room_type"].replace("shop_", "").upper()
        apt_tag = "" if rm["apartment"] in ("COMMON", "SHOP") else f'[{rm["apartment"][-1]}] '
        lines.append(f'<text x="{cx:.1f}" y="{cy - 8:.1f}" font-size="10.5" font-weight="bold" text-anchor="middle" fill="#1b1b1b">{apt_tag}{label}</text>')
        lines.append(f'<text x="{cx:.1f}" y="{cy + 6:.1f}" font-size="9.5" text-anchor="middle" fill="#333333">{rm["width"]:.2f}×{rm["depth"]:.2f} m ({rm["area_m2"]:.1f} m²)</text>')
        lines.append(f'<text x="{cx:.1f}" y="{cy + 19:.1f}" font-size="8.5" text-anchor="middle" fill="#555555">D:{rm["door_count"]} W:{rm["window_count"]} P≥{rm["min_props"]}</text>')

    # Overall width & depth dimension lines
    dim_y = oy + oh + 32
    lines.append(f'<line x1="{ox}" y1="{dim_y}" x2="{ox + ow}" y2="{dim_y}" stroke="#222" stroke-width="1.5"/>')
    lines.append(f'<line x1="{ox}" y1="{dim_y - 6}" x2="{ox}" y2="{dim_y + 6}" stroke="#222" stroke-width="1.5"/>')
    lines.append(f'<line x1="{ox + ow}" y1="{dim_y - 6}" x2="{ox + ow}" y2="{dim_y + 6}" stroke="#222" stroke-width="1.5"/>')
    lines.append(f'<text x="{ox + ow / 2:.1f}" y="{dim_y - 6}" font-size="11" text-anchor="middle" fill="#111">{W:.2f} m overall width</text>')

    dim_x = ox - 32
    lines.append(f'<line x1="{dim_x}" y1="{oy}" x2="{dim_x}" y2="{oy + oh}" stroke="#222" stroke-width="1.5"/>')
    lines.append(f'<line x1="{dim_x - 6}" y1="{oy}" x2="{dim_x + 6}" y2="{oy}" stroke="#222" stroke-width="1.5"/>')
    lines.append(f'<line x1="{dim_x - 6}" y1="{oy + oh}" x2="{dim_x + 6}" y2="{oy + oh}" stroke="#222" stroke-width="1.5"/>')
    lines.append(f'<text x="{dim_x - 10}" y="{oy + oh / 2:.1f}" font-size="11" text-anchor="middle" transform="rotate(-90 {dim_x - 10} {oy + oh / 2:.1f})" fill="#111">{D:.2f} m overall depth</text>')

    # Scale bar (0 .. 5 m)
    sb_x = pad_x
    sb_y = svg_h - 32
    sb_w = 5.0 * scale
    lines.append(f'<rect x="{sb_x}" y="{sb_y}" width="{sb_w:.1f}" height="8" fill="none" stroke="#111" stroke-width="1.5"/>')
    for i in range(5):
        seg_x = sb_x + i * scale
        fill_c = "#111" if i % 2 == 0 else "#fff"
        lines.append(f'<rect x="{seg_x:.1f}" y="{sb_y}" width="{scale:.1f}" height="8" fill="{fill_c}" stroke="#111" stroke-width="1"/>')
        lines.append(f'<text x="{seg_x:.1f}" y="{sb_y - 4}" font-size="9" text-anchor="middle" fill="#111">{i}m</text>')
    lines.append(f'<text x="{sb_x + sb_w:.1f}" y="{sb_y - 4}" font-size="9" text-anchor="middle" fill="#111">5m</text>')

    # North arrow
    na_x = svg_w - 65
    na_y = 55
    lines.append(f'<circle cx="{na_x}" cy="{na_y}" r="22" fill="#fff" stroke="#222" stroke-width="1.5"/>')
    lines.append(f'<polygon points="{na_x},{na_y - 18} {na_x - 7},{na_y + 10} {na_x},{na_y + 4} {na_x + 7},{na_y + 10}" fill="#111"/>')
    lines.append(f'<text x="{na_x}" y="{na_y - 24}" font-size="11" font-weight="bold" text-anchor="middle" fill="#111">N (+Y)</text>')

    lines.append('</svg>\n')
    out_path.write_text("\n".join(lines), encoding="utf-8")


def generate_branding_svgs() -> None:
    BRANDING_DIR.mkdir(parents=True, exist_ok=True)
    for b in BUILDINGS_SPEC:
        bid = b["id"]
        name = b["name"]
        sub = b["business"]
        bg = b["accent_color"]
        fg = "#f8f3e8"
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 220" width="600" height="220">
  <rect x="4" y="4" width="592" height="212" rx="14" fill="{bg}" stroke="{fg}" stroke-width="4"/>
  <rect x="16" y="16" width="568" height="188" rx="8" fill="none" stroke="{fg}" stroke-width="1.8" stroke-dasharray="8,4"/>
  <circle cx="88" cy="110" r="48" fill="none" stroke="{fg}" stroke-width="3"/>
  <path d="M 60 128 L 88 72 L 116 128 Z" fill="none" stroke="{fg}" stroke-width="3"/>
  <text x="88" y="122" font-family="DejaVu Serif, Georgia, serif" font-size="22" font-weight="bold" text-anchor="middle" fill="{fg}">{bid}</text>
  <text x="345" y="102" font-family="DejaVu Serif, Georgia, serif" font-size="34" font-weight="bold" text-anchor="middle" fill="{fg}" letter-spacing="2">{name.upper()}</text>
  <line x1="170" y1="122" x2="520" y2="122" stroke="{fg}" stroke-width="2"/>
  <text x="345" y="152" font-family="DejaVu Sans, Arial, sans-serif" font-size="15" text-anchor="middle" fill="{fg}" letter-spacing="1">{sub}</text>
  <text x="345" y="178" font-family="DejaVu Sans, Arial, sans-serif" font-size="11" text-anchor="middle" fill="{fg}">WINTERLICHTPLATZ · GEGR. TRADITIONSBETRIEB</text>
</svg>
"""
        (BRANDING_DIR / f"{bid}.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    DESIGN_DIR.mkdir(parents=True, exist_ok=True)
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    generate_branding_svgs()

    buildings_out = []
    schedule_rows = []
    apartments_rows = []

    apt_global_idx = 0
    for b_idx, b_spec in enumerate(BUILDINGS_SPEC):
        b_id = b_spec["id"]
        W = b_spec["width"]
        D = b_spec["depth"]
        gross_area = round(W * D, 2)
        floors_out = []

        for f_num in range(1, b_spec["storeys"] + 1):
            f_code = f"L{f_num:02d}"
            if f_num == 1:
                ffl = 0.0
                storey_h = 4.20
                ceil_h = 3.60
                rooms = make_ground_rooms(b_spec)
                apts_on_floor = []
            else:
                ffl = round(4.20 + (f_num - 2) * 3.20, 2)
                storey_h = 3.20
                ceil_h = 2.70
                arch_a_idx = (apt_global_idx) % len(ARCHETYPES)
                arch_b_idx = (apt_global_idx + 3) % len(ARCHETYPES)
                rooms_a, y_front_a = make_apartment_rooms(b_spec, f_num, "A", arch_a_idx)
                rooms_b, y_front_b = make_apartment_rooms(b_spec, f_num, "B", arch_b_idx)

                # Central landing connecting both apartments and touching rear exterior wall (+D/2)
                y_land_min = min(y_front_a, y_front_b)
                hd = D / 2.0
                land_w = 3.0
                land_d = round(hd - y_land_min, 3)
                landing_room = {
                    "id": f"{b_id}_{f_code}_landing",
                    "building": b_id,
                    "floor": f_code,
                    "apartment": "COMMON",
                    "room_type": "landing",
                    "name": f"{b_id} {f_code} Stair & Lift Landing",
                    "bounds_local": [-1.5, y_land_min, 1.5, hd],
                    "width": land_w,
                    "depth": land_d,
                    "area_m2": round(land_w * land_d, 2),
                    "door_count": 3,
                    "window_count": 1,
                    "connects_to": [
                        f"{b_id}_{f_code}_A_entry",
                        f"{b_id}_{f_code}_B_entry",
                        f"{b_id}_L01_shop_staff" if f_num == 2 else f"{b_id}_L{f_num-1:02d}_landing",
                    ],
                    "min_props": MIN_PROP_COUNTS["landing"],
                    "required_prop_families": REQUIRED_PROPS["landing"],
                }
                rooms = [landing_room] + rooms_a + rooms_b
                apts_on_floor = []

                for side, rm_list, arch_i in [("A", rooms_a, arch_a_idx), ("B", rooms_b, arch_b_idx)]:
                    apt_id = f"{b_id}_{f_code}_{side}"
                    archetype = ARCHETYPES[arch_i]
                    palette = PALETTES[(apt_global_idx * 5 + b_idx) % len(PALETTES)]
                    generation = GENERATIONS[(apt_global_idx * 3 + f_num) % len(GENERATIONS)]
                    # Explicit Stage B occupancy law on B02_L02: one family, one elderly couple
                    if apt_id == "B02_L02_A":
                        occupancy = "family_with_children"
                    elif apt_id == "B02_L02_B":
                        occupancy = "elderly_couple"
                    else:
                        occupancy = OCCUPANCIES[(apt_global_idx + b_idx) % len(OCCUPANCIES)]

                    seed = int(hashlib.sha256(apt_id.encode("utf-8")).hexdigest()[:8], 16)
                    # Deterministic arrangement signature input
                    sig_items = []
                    for r in rm_list:
                        sig_items.append(
                            f"{r['room_type']}:{palette}:{generation}:{occupancy}:"
                            f"{r['bounds_local'][0]:.2f},{r['bounds_local'][1]:.2f}:{seed % 360}"
                        )
                    arr_sig = hashlib.sha256("|".join(sorted(sig_items)).encode("utf-8")).hexdigest()
                    apt_rec = {
                        "id": apt_id,
                        "building": b_id,
                        "floor": f_code,
                        "side": side,
                        "archetype": archetype,
                        "palette": palette,
                        "generation": generation,
                        "occupancy": occupancy,
                        "seed": seed,
                        "arrangement_signature": arr_sig,
                        "room_count": len(rm_list),
                        "area_m2": round(sum(r["area_m2"] for r in rm_list), 2),
                    }
                    apts_on_floor.append(apt_rec)
                    apartments_rows.append(apt_rec)
                    apt_global_idx += 1

            occ_area = round(sum(r["area_m2"] for r in rooms), 2)
            occ_ratio = round(occ_area / gross_area, 4)
            floor_obj = {
                "id": f"{b_id}_{f_code}",
                "building": b_id,
                "floor": f_code,
                "level_index": f_num, "level": f_num,
                "use": "commercial" if f_num == 1 else "residential",
                "ffl_m": ffl, "elevation_m": ffl,
                "storey_height_m": storey_h,
                "ceiling_m": ceil_h,
                "slab_thickness_m": 0.22,
                "gross_area_m2": gross_area,
                "occupied_area_m2": occ_area,
                "occupied_ratio": occ_ratio,
                "apartments": apts_on_floor,
                "rooms": rooms,
            }
            floors_out.append(floor_obj)

            for r in rooms:
                schedule_rows.append({
                    "id": r["id"],
                    "building": r["building"],
                    "floor": r["floor"],
                    "apartment": r["apartment"],
                    "room_type": r["room_type"],
                    "name": r["name"],
                    "area_m2": r["area_m2"],
                    "door_count": r["door_count"],
                    "window_count": r["window_count"],
                    "min_props": r["min_props"],
                    "required_prop_families": r["required_prop_families"],
                })

            render_floor_svg(b_spec, floor_obj, PLANS_DIR / f"{b_id}-{f_code}.svg")

        buildings_out.append({
            **b_spec,
            "gross_floor_area_m2": gross_area,
            "total_height_m": round(4.20 + b_spec["upper_floors"] * 3.20, 2),
            "floors": floors_out,
        })

    programme = {
        "project": "Winterlichtplatz II",
        "agent": "vitruvius",
        "created_utc": "2026-10-19T14:25:00Z",
        "square": {
            "clear_width_m": 64.0,
            "clear_depth_m": 52.0,
            "origin": [0.0, 0.0, 0.0],
            "axes": {"+X": "east", "+Y": "north", "+Z": "up"},
            "market_stalls": 8,
            "christmas_tree_height_m": 11.0,
            "benches": 24,
            "lamps": 24,
            "deciduous_trees": 12,
            "bollards": 14,
            "bins": 6,
            "bicycle_racks": 3,
            "bicycles": 5,
            "playground_equipment": 4,
            "fountain": 1,
            "parked_vehicles": 3,
            "delivery_van": 1,
        },
        "people_programme": {
            "total_people": 220,
            "indoors": 110,
            "outdoors": 110,
            "public_realm_target": 120,
            "distinct_identities": 40,
            "hero_figures": 12,
            "poses": 40,
            "capsules_or_billboards": 0,
        },
        "buildings": buildings_out,
    }

    (DESIGN_DIR / "PROGRAMME.json").write_text(json.dumps(programme, indent=2), encoding="utf-8")

    with (DESIGN_DIR / "SCHEDULE.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "building", "floor", "apartment", "room_type",
            "name", "area_m2", "door_count", "window_count", "min_props", "required_prop_families"
        ])
        writer.writeheader()
        writer.writerows(schedule_rows)

    with (DESIGN_DIR / "APARTMENTS.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "building", "floor", "side", "archetype",
            "palette", "generation", "occupancy", "seed", "arrangement_signature", "room_count", "area_m2"
        ])
        writer.writeheader()
        writer.writerows(apartments_rows)

    # Generate the 271 required camera definitions (§27)
    views = []
    # 1. Square heroes (4 @ 3840x2160)
    for vid, state, loc, target in [
        ("hero_01_square_blue_hour", "blue_hour", [-24.0, -20.0, 1.62], [6.0, 14.0, 4.5]),
        ("hero_02_square_day", "day", [24.0, -20.0, 1.62], [-6.0, 14.0, 4.5]),
        ("hero_03_square_night", "night", [1.85, -21.2, 1.62], [0.0, 18.0, 5.0]),
        ("hero_04_square_oblique", "blue_hour", [-29.0, -24.0, 22.0], [4.0, 6.0, 2.0]),
    ]:
        views.append({"id": vid, "class": "square_hero", "resolution": [3840, 2160], "lighting": state, "location": loc, "target": target})

    # 2. Building exteriors (12 @ 3840x2160, blue_hour)
    # 3. Building sections (12 @ 2560x1440, day)
    # 4. Shopfronts (12 @ 2560x1440, blue_hour)
    # 10. Night alternates (12 @ 3840x2160, night)
    for b in buildings_out:
        bid = b["id"]
        cx, cy = b["center"]
        f_dir = b["facing"][0].upper()
        # Outward unit normal from building's square-facing facade toward the square
        if f_dir == "S":
            nx, ny = 0.0, -1.0
        elif f_dir == "N":
            nx, ny = 0.0, 1.0
        elif f_dir == "E":
            nx, ny = 1.0, 0.0
        else:
            nx, ny = -1.0, 0.0
        front_x = cx + nx * (b["depth"] / 2.0)
        front_y = cy + ny * (b["depth"] / 2.0)
        th = b["total_height_m"]
        views.append({"id": f"ext_{bid}_blue_hour", "class": "building_exterior", "building": bid, "resolution": [3840, 2160], "lighting": "blue_hour", "lens_mm": 24.0, "location": [round(front_x + nx * 16.5 + ny * 1.5, 2), round(front_y + ny * 16.5 - nx * 1.5, 2), 1.70], "target": [round(front_x, 2), round(front_y, 2), round(th * 0.42, 2)]})
        views.append({"id": f"sec_{bid}_cutaway", "class": "building_section", "building": bid, "resolution": [2560, 1440], "lighting": "day", "lens_mm": 28.0, "location": [round(front_x + nx * 14.5, 2), round(front_y + ny * 14.5, 2), round(th * 0.48, 2)], "target": [round(cx, 2), round(cy, 2), round(th * 0.45, 2)]})
        views.append({"id": f"shop_{bid}_front", "class": "shopfront", "building": bid, "resolution": [2560, 1440], "lighting": "blue_hour", "lens_mm": 28.0, "location": [round(front_x + nx * 7.2 + ny * 0.8, 2), round(front_y + ny * 7.2 - nx * 0.8, 2), 1.62], "target": [round(front_x, 2), round(front_y, 2), 1.95]})
        views.append({"id": f"night_{bid}_exterior", "class": "night_alternate", "building": bid, "resolution": [3840, 2160], "lighting": "night", "lens_mm": 24.0, "location": [round(front_x + nx * 17.2 - ny * 1.8, 2), round(front_y + ny * 17.2 + nx * 1.8, 2), 1.70], "target": [round(front_x, 2), round(front_y, 2), round(th * 0.42, 2)]})

    # Build lookup of living rooms per apartment for exact interior camera placement
    living_room_lookup = {}
    for b in buildings_out:
        bcx, bcy = b["center"]
        for fl in b["floors"]:
            ffl = fl.get("ffl_m", fl.get("elevation_m", 0.0))
            for rm in fl["rooms"]:
                if rm.get("apartment") and rm["room_type"] == "living":
                    xmin, ymin, xmax, ymax = rm["bounds_local"]
                    rw, rd = xmax - xmin, ymax - ymin
                    rcx = bcx + (xmin + xmax) / 2.0
                    rcy = bcy + (ymin + ymax) / 2.0
                    living_room_lookup[rm["apartment"]] = (rcx, rcy, rw, rd, ffl)

    # 5. Apartment interiors (110 @ 1920x1080) — placed inside each apartment's living room
    for apt in apartments_rows:
        rcx, rcy, rw, rd, ffl = living_room_lookup[apt["id"]]
        views.append({
            "id": f"int_{apt['id']}",
            "class": "apartment_interior",
            "building": apt["building"],
            "floor": apt["floor"],
            "apartment": apt["id"],
            "resolution": [1920, 1080],
            "lighting": "blue_hour",
            "lens_mm": 26.0,
            "location": [round(rcx + 0.34 * rw, 3), round(rcy - 0.26 * rd, 3), round(ffl + 1.42, 3)],
            "target": [round(rcx - 0.16 * rw, 3), round(rcy + 0.22 * rd, 3), round(ffl + 1.05, 3)],
        })

    # 6. Plans (67 @ 1920x1080)
    for b in buildings_out:
        for fl in b["floors"]:
            views.append({
                "id": f"plan_{b['id']}_{fl['floor']}",
                "class": "plan",
                "building": b["id"],
                "floor": fl["floor"],
                "svg": f"townsquare/design/plans/{b['id']}-{fl['floor']}.svg",
                "resolution": [1920, 1080],
                "lighting": "day",
                "location": [b["center"][0], b["center"][1], fl["ffl_m"] + 18.0],
                "target": [b["center"][0], b["center"][1], fl["ffl_m"]],
            })

    # 7. Human close-ups (24 @ 2560x1440 = 12 HSRD-100 photogrammetry heroes x 2 angles)
    hero_coords = [
        (-2.10, 23.60, 0.12),   # H01: B02 bakery sidewalk
        (1.30, 24.40, 0.12),    # H02: B02 bakery warm window
        (-19.50, 23.60, 0.12),  # H03: B01 apothecary sidewalk
        (18.50, 23.60, 0.12),   # H04: B03 bookshop sidewalk
        (-9.50, 8.80, 0.00),    # H05: Stall 01 Glühwein
        (9.50, 8.80, 0.00),     # H06: Stall 02 Maroni
        (-9.50, -8.80, 0.00),   # H07: Stall 05 Holzkunst
        (9.50, -8.80, 0.00),    # H08: Stall 06 Kerzen
        (-3.80, -4.20, 0.00),   # H09: Christmas tree southwest
        (3.80, -4.20, 0.00),    # H10: Christmas tree southeast
        (-18.50, -23.60, 0.12), # H11: B04 Konditorei sidewalk
        (18.50, -23.60, 0.12),  # H12: B06 Spielzeug sidewalk
    ]
    for h_idx, (hx, hy, hz) in enumerate(hero_coords, 1):
        for ang in ("A", "B"):
            dx = 0.0 if ang == "A" else 0.58
            dy = -1.35 if ang == "A" else -1.24
            views.append({
                "id": f"human_{h_idx:02d}_{ang}",
                "class": "human_closeup",
                "hero_id": f"H{h_idx:02d}",
                "angle": ang,
                "resolution": [2560, 1440],
                "lighting": "day" if ang == "A" else "blue_hour",
                "lens_mm": 52.0,
                "location": [round(hx + dx, 3), round(hy + dy, 3), round(hz + 1.32, 3)],
                "target": [round(hx, 3), round(hy, 3), round(hz + 1.24, 3)],
            })

    # 8. Terrain / public detail (12 @ 2560x1440)
    terrain_subjects = [
        "cobbles_wet_puddle", "kerb_snow_slush", "bench_bolted_01", "market_stall_01",
        "fountain_frozen_edge", "street_lamp_01", "tree_pit_grate", "christmas_tree_base",
        "gully_grating_drain", "bicycle_rack_snow", "playground_gate", "bakery_threshold_slush",
    ]
    for idx, subj in enumerate(terrain_subjects, 1):
        ang = 2.0 * math.pi * (idx - 1) / 12.0 + 0.39
        cx = round(8.4 * math.cos(ang), 2)
        cy = round(6.8 * math.sin(ang), 2)
        tx = round(5.6 * math.cos(ang), 2)
        ty = round(4.6 * math.sin(ang), 2)
        views.append({
            "id": f"terrain_{idx:02d}_{subj}",
            "class": "terrain_detail",
            "subject": subj,
            "resolution": [2560, 1440],
            "lighting": "day" if idx % 2 == 1 else "blue_hour",
            "location": [cx, cy, 1.15],
            "target": [tx, ty, 0.08],
        })

    # 9. Technical (6 @ 2560x1440)
    tech_subjects = [
        "structure_wireframe", "facade_material_scales", "lighting_plan",
        "master_section", "terrain_wireframe", "kit_index",
    ]
    tech_locs = [
        ([0.0, -21.5, 14.5], [0.0, 10.0, 5.0]),
        ([-22.0, -17.5, 12.5], [10.0, 14.0, 5.5]),
        ([22.0, 17.5, 16.0], [0.0, 0.0, 2.5]),
        ([2.2, -20.5, 9.5], [0.0, 26.0, 8.5]),
        ([-14.5, 11.5, 6.5], [0.0, 0.0, 1.0]),
        ([21.5, -16.5, 13.5], [-8.0, 10.0, 4.5]),
    ]
    for idx, subj in enumerate(tech_subjects, 1):
        loc, tgt = tech_locs[idx - 1]
        views.append({
            "id": f"tech_{idx:02d}_{subj}",
            "class": "technical",
            "subject": subj,
            "resolution": [2560, 1440],
            "lighting": "day",
            "location": loc,
            "target": tgt,
        })

    assert len(views) == 271, f"Expected 271 views, got {len(views)}"
    (DESIGN_DIR / "VIEWS.json").write_text(json.dumps(views, indent=2), encoding="utf-8")

    views_py = f'''#!/usr/bin/env python3
"""271 required camera definitions for Winterlichtplatz II (§27)."""
import json
from pathlib import Path

VIEWS_PATH = Path(__file__).resolve().parents[1] / "design" / "VIEWS.json"

def load_views():
    return json.loads(VIEWS_PATH.read_text(encoding="utf-8"))

if __name__ == "__main__":
    v = load_views()
    print(f"Loaded {{len(v)}} views")
'''
    (SCENE_DIR / "views.py").write_text(views_py, encoding="utf-8")
    print(f"Generated PROGRAMME.json ({len(buildings_out)} buildings, {len(apartments_rows)} apartments, {len(schedule_rows)} rooms, 67 SVG plans, 12 branding SVGs, 271 views).")


if __name__ == "__main__":
    main()
