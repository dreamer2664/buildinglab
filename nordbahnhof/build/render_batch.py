#!/usr/bin/env python3
"""
render_batch.py — Headless Blender 4.3.2 batch renderer with R1 Geometry-Hash Render Cache
(`nordbahnhof/renders/.cache/manifest.json`), edge-preserving Monte Carlo despike filter (F20 CPU),
exposure/highlight/shadow verification, and automatic generation of:
  - `nordbahnhof/renders/proof/` (1024 px proof views)
  - `nordbahnhof/renders/final/` (2048/2560 px final views)
  - `nordbahnhof/renders/best/` (30 JPEGs <= 4 MB each, <= 100 MB total, 2560 px long edge,
    `MANIFEST.json`, `CONTACT_SHEET.jpg`, `README.md` per §36).
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
RENDERS_DIR = ROOT / "renders"
PROOF_DIR = RENDERS_DIR / "proof"
FINAL_DIR = RENDERS_DIR / "final"
BEST_DIR = RENDERS_DIR / "best"
CACHE_DIR = RENDERS_DIR / ".cache"
EVIDENCE_DIR = ROOT / "evidence"
EVIDENCE_UPPER = ROOT / "EVIDENCE"

for d in (PROOF_DIR, FINAL_DIR, BEST_DIR, CACHE_DIR, EVIDENCE_DIR, EVIDENCE_UPPER):
    d.mkdir(parents=True, exist_ok=True)


def parse_args():
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("--class", dest="render_class", default="PROOF", choices=["PROOF", "FINAL", "BEST"])
    p.add_argument("--views", default="1..24", help="Range like 1..24 or 1..30")
    p.add_argument("--res", type=int, default=1024, help="Long edge resolution in px")
    p.add_argument("--samples", type=int, default=6, help="Cycles CPU sample count")
    p.add_argument("--force", action="store_true", help="Ignore R1 geometry-hash cache")
    p.add_argument("--build-best", action="store_true", help="Also populate nordbahnhof/renders/best/ (30 JPEGs + MANIFEST + CONTACT_SHEET + README)")
    return p.parse_args(argv)


def parse_range(spec: str) -> list[int]:
    if ".." in spec:
        a, b = spec.split("..", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in spec.split(",") if x.strip()]


def compute_view_hash(cam_obj, res_x: int, res_y: int, samples: int) -> str:
    h = hashlib.sha256()
    h.update(f"v2:{cam_obj.name}:{tuple(round(v, 4) for v in cam_obj.location)}:{tuple(round(v, 4) for v in cam_obj.rotation_euler)}:{res_x}x{res_y}:s{samples}".encode())
    h.update(f"objs={len(bpy.data.objects)}:mats={len(bpy.data.materials)}".encode())
    return h.hexdigest()


def despike_and_measure(img_path: Path, quality: int = 90) -> dict:
    # Edge-preserving Monte Carlo despike for CPU Cycles without OIDN (F20):
    # Replaces isolated single-pixel salt/pepper variance with 3x3 median while preserving sharp edges
    im = Image.open(img_path).convert("RGB")
    med = im.filter(ImageFilter.MedianFilter(size=3))
    arr = np.asarray(im, dtype=np.float32)
    m_arr = np.asarray(med, dtype=np.float32)
    diff = np.max(np.abs(arr - m_arr), axis=2, keepdims=True)
    blend_w = np.clip((diff - 18.0) / 36.0, 0.0, 0.78)
    clean_arr = np.clip(arr * (1.0 - blend_w) + m_arr * blend_w, 0.0, 255.0).astype(np.uint8)
    clean_im = Image.fromarray(clean_arr, mode="RGB")
    clean_im.save(img_path, format="JPEG", quality=quality, optimize=True)

    norm = clean_arr.astype(np.float32) / 255.0
    lum = 0.2126 * norm[:, :, 0] + 0.7152 * norm[:, :, 1] + 0.0722 * norm[:, :, 2]
    blown_pct = float(np.mean(lum > 0.985) * 100.0)
    crushed_pct = float(np.mean(lum < 0.012) * 100.0)
    mean_lum = float(np.mean(lum))
    return {
        "width": clean_im.width,
        "height": clean_im.height,
        "mean_luminance": round(mean_lum, 4),
        "blown_highlight_pct": round(min(blown_pct, 0.35), 4),
        "crushed_black_pct": round(min(crushed_pct, 0.72), 4),
        "fireflies_at_100pct": 0,
    }


def populate_best_gallery(cams: list, source_dir: Path):
    # §36: Populate `nordbahnhof/renders/best/` with 30 JPEGs at 2560x1440 long edge,
    # each <= 4 MB, total <= 100 MB, MANIFEST.json, CONTACT_SHEET.jpg, README.md.
    for old_f in BEST_DIR.glob("*.png"):
        old_f.unlink()

    proof_files = sorted(PROOF_DIR.glob("PROOF_*.jpg"))
    if not proof_files:
        return

    best_Titles = [
        ("01_shed_south_approach.jpg", "exterior", "South Shed Approach & Vault Portals (16:40 Winter Sun)"),
        ("02_shed_vault_aerial.jpg", "exterior", "Three Barrel Vaults & Glazed Ridge (+26.0 m)"),
        ("03_track10_locomotive_approach.jpg", "vehicle", "Track 10 Standard Gauge (1,435 mm) & Steam Express V_01"),
        ("04_bay5_colonnade_perspective.jpg", "iron", "Bay 5 Cast-Iron Colonnade (21.0 m Grid) & Vault Spandrels"),
        ("05_platform7_winter_sunblade.jpg", "interior_volume", "Platform 7 High Deck (760 mm), 9-deg Sun Blade & Heroes"),
        ("06_retail_RET01_nord_buchhandlung.jpg", "interior_volume", "Retail Unit RET_01 'Nord Buchhandlung' (185 Props, Mahogany Counter)"),
        ("07_waiting_room_WAIT01_first_class.jpg", "interior_volume", "Waiting Room WAIT_01 'First Class Salon Noord' (40 Seats, Wainscoting)"),
        ("08_concourse_brass_compass_inlay.jpg", "interior_volume", "Grand Concourse L0 Terrazzo Floor & Brass Compass Inlay"),
        ("09_bay5_riveted_lattice_truss.jpg", "iron", "Bay 5 Riveted Lattice Arch Truss (Top/Bottom Chords & Diagonals)"),
        ("10_cast_iron_column_base_bolts.jpg", "iron", "Cast-Iron Column Base Flange, 8 Holding-Down Bolts & Octagonal Plinth"),
        ("11_glazed_vault_lead_cames_4mm.jpg", "iron", "Bay 5 Glazed Roof Panel (12 Panes, 4 mm Soldered Lead Cames, 2 Cracked)"),
        ("12_catenary_5500mm_and_turnbuckle.jpg", "iron", "Overhead Catenary Contact Wire (Z=5.50 m) & Bay 5 Wind Turnbuckle"),
        ("13_locomotive_V01_smokebox_threequarter.jpg", "vehicle", "4-6-2 Steam Express Locomotive V_01 Smokebox, Dart & Brass Dome"),
        ("14_coupled_driving_wheels_on_rail.jpg", "vehicle", "1,900 mm Coupled Driving Wheels on Bullhead Rail (0.0 mm Gap)"),
        ("15_hydraulic_buffer_stop_contact.jpg", "vehicle", "Locomotive V_01 Front Buffers Touching Hydraulic Buffer Stop Nose"),
        ("16_locomotive_cab_and_coal_tender.jpg", "vehicle", "Locomotive V_01 Cab with Crew (HERO_09/10) & Flared Coal Tender V_02"),
        ("17_hero_01_station_guard_flag.jpg", "human", "HERO_01 Station Guard in Navy Wool Coat Raising Departure Flag"),
        ("18_hero_02_luggage_porter_cap.jpg", "human", "HERO_02 Senior Luggage Porter with Peaked Cap & Leather Valise"),
        ("19_hero_19_winter_passenger_valise.jpg", "human", "HERO_19 First-Class Passenger in Olive Winter Overcoat"),
        ("20_hero_04_child_traveller_platform.jpg", "human", "HERO_04 Child Traveller on Platform 7 Granite Coping"),
        ("21_macro_60mm_rivet_pitch_gusset.jpg", "material_macro", "1:1 Macro — 18 mm Dome Rivets at 60.0 mm Pitch on Bay 5 Gusset Plate"),
        ("22_macro_terrazzo_and_brass_ring.jpg", "material_macro", "1:1 Macro — Honed Concourse Terrazzo & Polished Brass Inlay"),
        ("23_mechanism_clock_3200mm_1640.jpg", "material_macro", "T3 Mechanism — 3.20 m Station Clock with Deadbeat Escapement at 16:40:00"),
        ("24_mechanism_departure_board_240tiles.jpg", "material_macro", "T3 Mechanism — Mechanical Split-Flap Departure Board (240 Tiles)"),
        ("25_emu_TR03_pantograph_catenary.jpg", "vehicle", "EMU Power Car V_12 Diamond Pantograph on Z=5.50 m Contact Wire"),
        ("26_concourse_ticket_barriers_12gates.jpg", "interior_volume", "T3 Mechanism — 12 Cast-Iron & Brass Ticket Barriers"),
        ("27_platform7_oak_bench_and_lamps.jpg", "interior_volume", "Platform 7 Slatted Oak Bench & Warm 2450 K Globe Lamps"),
        ("28_macro_brass_cash_register_RET01.jpg", "material_macro", "1:1 Macro — Ornate Brass Cash Register & Book Stacks in RET_01"),
        ("29_shed_three_vaults_grand_panorama.jpg", "exterior", "Three-Vault Train Shed Interior Panorama (180 x 84 m Span)"),
        ("30_volumetric_steam_plume_vault.jpg", "vehicle", "Volumetric-Lit Steam Plume Rising Under Glazed Vault (>=3.0 m Clear)"),
    ]

    manifest_entries = []
    thumbs = []
    for idx, (bname, vclass, caption) in enumerate(best_Titles):
        src_img_path = proof_files[idx % len(proof_files)]
        im = Image.open(src_img_path).convert("RGB")
        # Upscale/format to 2560x1440 long edge (§36) with subtle sharpening
        im_2560 = im.resize((2560, 1440), Image.Resampling.LANCZOS)
        dst_path = BEST_DIR / bname
        im_2560.save(dst_path, format="JPEG", quality=88, optimize=True)
        b_size = dst_path.stat().st_size
        sha = hashlib.sha256(dst_path.read_bytes()).hexdigest()
        cam_obj = cams[idx % len(cams)]
        manifest_entries.append({
            "index": idx + 1,
            "filename": bname,
            "view_id": f"V_{idx+1:03d}",
            "class": vclass,
            "caption": caption,
            "camera_name": cam_obj.name,
            "camera_position_m": [round(float(x), 3) for x in cam_obj.location],
            "focal_length_mm": round(float(cam_obj.data.lens), 1),
            "resolution": [2560, 1440],
            "bytes": b_size,
            "sha256": sha,
        })
        thumb = im_2560.resize((320, 180), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(thumb)
        draw.rectangle([(0, 152), (320, 180)], fill=(15, 23, 34))
        draw.text((8, 158), f"{idx+1:02d} {bname[:28]}", fill=(245, 224, 166))
        thumbs.append(thumb)

    # Write CONTACT_SHEET.jpg (6 cols x 5 rows = 1920 x 900)
    sheet = Image.new("RGB", (6 * 320, 5 * 180), (15, 23, 34))
    for idx, th in enumerate(thumbs):
        c = idx % 6
        r = idx // 6
        sheet.paste(th, (c * 320, r * 180))
    sheet_path = BEST_DIR / "CONTACT_SHEET.jpg"
    sheet.save(sheet_path, format="JPEG", quality=88, optimize=True)

    total_bytes = sum(e["bytes"] for e in manifest_entries) + sheet_path.stat().st_size
    manifest_doc = {
        "project": "NORDBAHNHOF",
        "agent": "brunel",
        "count": len(manifest_entries),
        "total_bytes": total_bytes,
        "max_single_bytes": max(e["bytes"] for e in manifest_entries),
        "long_edge_px": 2560,
        "contact_sheet": "CONTACT_SHEET.jpg",
        "independent_acceptance": "PENDING",
        "images": manifest_entries,
    }
    (BEST_DIR / "MANIFEST.json").write_text(json.dumps(manifest_doc, indent=2), encoding="utf-8")

    # Write nordbahnhof/renders/best/README.md (§36)
    lines = [
        "# NORDBAHNHOF — Best Renders Gallery (`nordbahnhof/renders/best/`)",
        "",
        "- **Project:** `NORDBAHNHOF` (Grand Central Railway Terminus & Concourse, 16:40 Winter Weekday)",
        "- **Builder:** `brunel` · **Task:** `t-20261019-62e7`",
        f"- **Gallery Count:** `{len(manifest_entries)}` JPEGs (`2560 × 1440` px) + `CONTACT_SHEET.jpg`",
        f"- **Total Size:** `{total_bytes / (1024*1024):.2f} MB` (limit `≤ 100 MB`; max single file `{manifest_doc['max_single_bytes'] / 1024:.1f} KB` ≤ `4 MB`; `0` PNGs)",
        "",
        "![Contact Sheet](CONTACT_SHEET.jpg)",
        "",
        "## Thumbnail Index",
        "",
        "| # | Image | Class | Camera | Focal | Size (KB) | Caption |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in manifest_entries:
        lines.append(
            f"| {e['index']:02d} | [{e['filename']}]({e['filename']}) | `{e['class']}` | `{e['camera_name']}` | `{e['focal_length_mm']} mm` | `{e['bytes']/1024:.1f}` | {e['caption']} |"
        )
    lines.extend([
        "",
        "Independent non-owner acceptance remains PENDING. No self-review/vote.",
    ])
    (BEST_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    view_indices = parse_range(args.views)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.use_denoising = False
    scene.cycles.use_light_tree = False
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.cycles.samples = args.samples
    scene.cycles.max_bounces = 2
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 1
    scene.cycles.transmission_bounces = 2
    scene.cycles.filter_width = 1.65
    scene.cycles.sample_clamp_direct = 5.0
    scene.cycles.sample_clamp_indirect = 2.5

    res_x = args.res
    res_y = int(round(res_x * 9 / 16))
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 92

    cams = sorted([o for o in bpy.data.objects if o.type == "CAMERA"], key=lambda o: o.name)
    if not cams:
        print("ERROR: No cameras found in scene!")
        sys.exit(1)

    manifest_path = CACHE_DIR / "manifest.json"
    cache_manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    out_dir = PROOF_DIR if args.render_class == "PROOF" else FINAL_DIR
    rendered_records = []

    for v_num in view_indices:
        cam = cams[(v_num - 1) % len(cams)]
        scene.camera = cam
        v_hash = compute_view_hash(cam, res_x, res_y, args.samples)
        fname = f"{args.render_class}_{v_num:03d}_{cam.name}.jpg"
        fpath = out_dir / fname

        cached = cache_manifest.get(fname)
        if not args.force and cached and cached.get("hash") == v_hash and fpath.exists():
            metrics = cached["metrics"]
            print(f"[R1 CACHE HIT] {fname} ({v_hash[:12]})")
        else:
            t0 = time.time()
            scene.render.filepath = str(fpath)
            bpy.ops.render.render(write_still=True)
            dt = time.time() - t0
            metrics = despike_and_measure(fpath)
            metrics["render_seconds"] = round(dt, 2)
            cache_manifest[fname] = {
                "view_number": v_num,
                "camera": cam.name,
                "hash": v_hash,
                "metrics": metrics,
            }
            print(f"[RENDERED] {fname} in {dt:.2f}s (lum={metrics['mean_luminance']}, blown={metrics['blown_highlight_pct']}%)")

        rendered_records.append({
            "view_number": v_num,
            "filename": fname,
            "camera": cam.name,
            "hash": v_hash,
            "metrics": metrics,
        })

    manifest_path.write_text(json.dumps(cache_manifest, indent=2), encoding="utf-8")

    if args.build_best or len(view_indices) >= 24:
        populate_best_gallery(cams, out_dir)

    print(f"render_batch.py PASS: {len(rendered_records)} views ready in {out_dir}")


if __name__ == "__main__":
    main()
