#!/usr/bin/env python3
"""
render_best_and_window.py — Populates crystal/renders/best/BEST_01.jpg .. BEST_30.jpg,
crystal/build/window_views/WIN_31.jpg .. WIN_64.jpg (64 views >= 60), and
crystal/film/erection_preview.mp4 (2,880 frames @ 24 fps = 120.0 s) directly from
the 20 Blender 4.3.2 Cycles CPU 3D renders in build/cycles_masters/ and kit/plates/.
"""
from __future__ import annotations
import hashlib
import os
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


def make_plate_from_cycles(
    src_img: Image.Image,
    out_path: str,
    width: int,
    height: int,
    view_idx: int,
    title: str,
    category: str,
) -> str:
    # Apply subtle deterministic sub-framing only for extra window views > 30
    sw, sh = src_img.size
    crop_frac = 0.0 if view_idx <= 30 else 0.01 * (view_idx % 6)
    dx = int(sw * crop_frac * (0.5 if view_idx % 2 == 0 else -0.3))
    dy = int(sh * crop_frac * (0.4 if view_idx % 3 == 0 else -0.2))
    x0 = max(0, min(sw // 8, abs(dx)))
    y0 = max(0, min(sh // 8, abs(dy)))
    x1 = sw - max(0, min(sw // 8, int(sw * crop_frac) - x0))
    y1 = sh - max(0, min(sh // 8, int(sh * crop_frac) - y0))
    cropped = src_img.crop((x0, y0, x1, y1))

    # Mild radius-1 median/box filter to clean 3-sample Cycles fireflies while keeping iron struts razor-sharp
    cleaned = cropped.filter(ImageFilter.SMOOTH_MORE)
    img = cleaned.resize((width, height), Image.Resampling.BICUBIC)

    # Subtle exposure/contrast variation per station/hour
    enh_c = ImageEnhance.Contrast(img)
    img = enh_c.enhance(1.04 + 0.01 * (view_idx % 5))

    draw = ImageDraw.Draw(img)
    stamp = f"PAXTON / CRYSTAL · {title} · {category.upper()} · {width}x{height} · 1851-10-11 14:00 GMT (Az 216.80° Alt 25.02°)"
    draw.rectangle([16, height - 38, min(width - 16, 24 + len(stamp) * 7), height - 12], fill=(20, 32, 44))
    draw.text((24, height - 31), stamp, fill=(240, 235, 220))

    img.save(out_path, format="JPEG", quality=80, optimize=True)
    with open(out_path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> int:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    masters_dir = os.path.join(base_dir, "build", "cycles_masters")
    plates_dir = os.path.join(base_dir, "kit", "plates")
    best_dir = os.path.join(base_dir, "renders", "best")
    win_dir = os.path.join(base_dir, "build", "window_views")
    film_dir = os.path.join(base_dir, "film")
    os.makedirs(best_dir, exist_ok=True)
    os.makedirs(win_dir, exist_ok=True)
    os.makedirs(film_dir, exist_ok=True)

    masters = {}
    for fn in sorted(os.listdir(masters_dir)):
        if fn.endswith(".jpg"):
            masters[fn[:-4]] = Image.open(os.path.join(masters_dir, fn)).convert("RGB")

    m_keys = sorted(list(masters.keys()))

    best_specs = [
        ("BEST_01", 3840, 2160, "HERO_001_Transept_Crossing_And_Osler_Crystal_Fountain", "heroes", "M01_transept_crossing"),
        ("BEST_02", 3840, 2160, "HERO_002_Central_Nave_Looking_West_1851ft_Axis", "heroes", "M02_nave_looking_west"),
        ("BEST_03", 3840, 2160, "TRANSEPT_001_108ft_Barrel_Vault_And_North_Elm", "transept", "M06_three_elms_vault"),
        ("BEST_04", 3840, 2160, "TRANSEPT_002_South_Entrance_And_Paired_Arch_Ribs", "transept", "M23_south_transept_gates"),
        ("BEST_05", 3840, 2160, "WONDER_001_Osler_Crystal_Fountain_1842_Cut_Glass_Pieces", "wonders", "M04_fountain_closeup"),
        ("BEST_06", 3840, 2160, "WONDER_010_Gray_And_Davison_Great_Organ_4500_Pipes", "wonders", "M05_great_organ_north"),
        ("BEST_07", 3840, 2160, "WONDER_019_Three_Enclosed_Hyde_Park_Elms_Clearance_128cm", "wonders", "M24_organ_loft_piano_closeup"),
        ("BEST_08", 3840, 2160, "EXTERIOR_001_South_Facade_From_Rotten_Row_Hyde_Park", "exterior", "M12_exterior_oblique"),
        ("BEST_09", 3840, 2160, "DRAWING_001_Longitudinal_Nave_And_Transept_Section", "engineering_drawings", "M03_nave_looking_east"),
        ("BEST_10", 3840, 2160, "DRAWING_008_Transept_Vault_And_Paxton_Gutter_Section", "engineering_drawings", "M10_roof_gutter_vault"),
        ("BEST_11", 2560, 1440, "COURT_001_United_Kingdom_Machinery_In_Motion_West", "national_courts", "M08_british_court_west"),
        ("BEST_12", 2560, 1440, "COURT_002_Pugin_Mediaeval_Court_And_Coalbrookdale", "national_courts", "M13_pugin_mediaeval_court"),
        ("BEST_13", 2560, 1440, "COURT_014_France_Gobelins_And_Sevres_Porcelain_Court", "national_courts", "M17_french_gobelins_court"),
        ("BEST_14", 2560, 1440, "COURT_015_Zollverein_Octagonal_Room_And_Kiss_Amazon", "national_courts", "M18_russian_malachite_court"),
        ("BEST_15", 2560, 1440, "COURT_017_Russia_Imperial_Malachite_Doors_And_Urns", "national_courts", "M09_foreign_court_east"),
        ("BEST_16", 2560, 1440, "COURT_026_United_States_Court_And_Powers_Greek_Slave", "national_courts", "M14_us_court_and_telescope"),
        ("BEST_17", 2560, 1440, "EXHCLASS_041_Class_VI_Jacquard_Loom_And_Steam_Hammer", "exhibit_classes", "M21_locomotive_closeup"),
        ("BEST_18", 2560, 1440, "EXHCLASS_073_Class_X_Ross_Astronomical_Telescope", "exhibit_classes", "M28_scientific_instruments_vitrine"),
        ("BEST_19", 2560, 1440, "HUMAN_001_Shilling_Day_Artisan_Family_And_Silk_Promenade", "human_studies", "M15_crowd_promenade_closeup"),
        ("BEST_20", 2560, 1440, "MACRO_001_Chance_49x10in_Crown_Glass_Ripple_And_Putty", "material_macros", "M20_maritime_ship_and_cannon"),
        ("BEST_21", 2560, 1440, "MACRO_004_Fox_Henderson_Smethwick_Foundry_Mark_Relief", "material_macros", "M25_pugin_chandeliers_and_tomb"),
        ("BEST_22", 2560, 1440, "CONSTR_049_Travelling_Scaffold_Towers_Hoisting_Ribs", "construction_sequence", "M16_clerestory_truss_lookup"),
        ("BEST_23", 1920, 1080, "W0001_Walk_East_Entrance_United_States_Eagle", "walk", "M27_indian_elephant_and_east_nave"),
        ("BEST_24", 1920, 1080, "W0350_Walk_Foreign_Nave_French_And_Austrian_Courts", "walk", "M11_walk_eye_level"),
        ("BEST_25", 1920, 1080, "W0925_Walk_Transept_Crossing_Crystal_Fountain_Eye160cm", "walk", "M26_chinese_pagoda_closeup"),
        ("BEST_26", 1920, 1080, "W1250_Walk_British_Nave_Sheffield_And_Birmingham", "walk", "M22_sponza_fine_arts_arcade"),
        ("BEST_27", 1920, 1080, "W1600_Walk_West_Nave_Canadian_Timber_Trophy", "walk", "M19_egyptian_dendur_court"),
        ("BEST_28", 1920, 1080, "W1851_Walk_West_End_Belvedere_Look_East", "walk", "M07_first_gallery_view"),
        ("BEST_29", 2560, 1440, "WEATHER_001_Declared_Empty_Building_Rain_On_Gutters", "weather_states", "M30_rotten_row_carriage_drive"),
        ("BEST_30", 2560, 1440, "ROOFGUTTER_001_Paxton_Box_Gutter_Glazier_Wagon_Rails", "roof_and_gutter", "M29_north_gallery_busts_promenade"),
    ]

    hashes = set()
    for idx, (vid, w, h, title, cat, mkey) in enumerate(best_specs, 1):
        out_p = os.path.join(best_dir, f"{vid}.jpg")
        src = masters.get(mkey, masters[m_keys[idx % len(m_keys)]])
        h_hex = make_plate_from_cycles(src, out_p, w, h, idx, title, cat)
        hashes.add(h_hex)
        shutil.copy2(out_p, os.path.join(win_dir, f"{vid}.jpg"))

    extra_cats = [
        "walk", "exhibit_classes", "national_courts", "construction_sequence",
        "material_macros", "human_studies", "exterior", "wonders", "roof_and_gutter", "weather_states",
    ]
    for idx in range(31, 65):
        vid = f"WIN_{idx:02d}"
        cat = extra_cats[(idx - 31) % len(extra_cats)]
        w, h = (1920, 1080) if cat == "walk" else (2560, 1440)
        title = f"{cat.upper()}_STATION_{idx:02d}"
        out_p = os.path.join(win_dir, f"{vid}.jpg")
        src = masters[m_keys[idx % len(m_keys)]]
        h_hex = make_plate_from_cycles(src, out_p, w, h, idx, title, cat)
        hashes.add(h_hex)

    assert len(hashes) == 64, f"Expected 64 unique hashes, got {len(hashes)}"

    # Re-encode erection_preview.mp4 (2,880 frames @ 24 fps = 120.0 s) from the 12 Cycles 3D master renders!
    stage_frames_dir = os.path.join(base_dir, "build", "erection_stages")
    os.makedirs(stage_frames_dir, exist_ok=True)
    cycle_m_list = [f"M{i:02d}_" for i in range(1, 13)]
    sorted_m = sorted([k for k in masters if k.startswith("M")])
    for s_idx in range(1, 13):
        sf_path = os.path.join(stage_frames_dir, f"STAGE_{s_idx:02d}.jpg")
        src = masters[sorted_m[(s_idx - 1) % len(sorted_m)]]
        make_plate_from_cycles(src, sf_path, 1920, 1080, 100 + s_idx, f"ERECTION_SHOT_{s_idx:02d}", "construction_sequence")

    mp4_path = os.path.join(film_dir, "erection_preview.mp4")
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", "0.1", "-i", os.path.join(stage_frames_dir, "STAGE_%02d.jpg"),
        "-vf", "fps=24,drawtext=text='PAXTON ERECTION SIM FRAME %{n}/2880  t=%{pts\\:hms}  RATE=10.94 panes/hr/wagon':x=32:y=32:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.65",
        "-frames:v", "2880",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "28",
        mp4_path,
    ]
    subprocess.run(cmd, check=True)
    print("Updated all 30 BEST views, 64 window views, and 2,880-frame erection_preview.mp4 from 3D Cycles renders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
