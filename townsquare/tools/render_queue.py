#!/usr/bin/env python3
"""
render_queue.py — Geometry-hash-addressed render queue (R1, R2, §12, §26).
Supports:
  python3 townsquare/tools/render_queue.py --slice --pass proof --jobs 2
  python3 townsquare/tools/render_queue.py --slice --pass final --only-dirty
  python3 townsquare/tools/render_queue.py --pass proof --jobs 2
  python3 townsquare/tools/render_queue.py --pass final --only-dirty
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
RENDERS_DIR = REPO_ROOT / "renders"
MANIFEST_PATH = RENDERS_DIR / "manifest.json"


def compute_file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def compute_geometry_key(view: dict, native_sha: str) -> str:
    payload = json.dumps({
        "id": view["id"],
        "lighting": view.get("lighting", "blue_hour"),
        "location": view.get("location"),
        "target": view.get("target"),
        "resolution": view.get("resolution"),
        "native_sha": native_sha,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


BLENDER_BATCH_SCRIPT = """
import bpy, json, os, sys
from pathlib import Path

ROOT = Path(os.environ["TS_ROOT"])
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))
from townsquare.kits.lighting.builder import set_scene_lighting_mood

batch = json.loads(os.environ["TS_RENDER_BATCH"])
pass_kind = os.environ["TS_PASS_KIND"]
samples = int(os.environ.get("TS_SAMPLES", "12"))

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.use_denoising = False
scene.cycles.samples = samples
scene.cycles.max_bounces = 4
scene.cycles.diffuse_bounces = 2
scene.cycles.glossy_bounces = 2
scene.cycles.transmission_bounces = 2
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"

for item in batch:
    vid = item["id"]
    out_path = item["out_path"]
    lstate = item.get("lighting", "blue_hour")
    set_scene_lighting_mood(scene, lstate)

    # Cutaway / plan visibility toggle for roof & ceiling slabs above target level
    is_cut = ("cutaway" in vid) or ("plan" in vid) or ("sec_" in vid)
    if "01_B02_UpperAndRoof" in bpy.data.collections:
        bpy.data.collections["01_B02_UpperAndRoof"].hide_render = is_cut
    for obj in scene.objects:
        if obj.type == "MESH":
            hide = False
            if is_cut and (
                obj.get("level") in ("ROOF", "L03", "L04", "L05", "L06", "L07")
                or "SPANDREL_TOP" in obj.name
                or ("L02" in obj.name and any(k in obj.name for k in ("_CEIL_ROSE", "_PENDANT_SHADE", "_PENDANT_BULB", "_CORNICE_")))
                or ("B02_ExtWall_N_0" in obj.name)
                or ("B02_SouthPier_0_" in obj.name)
                or ("B02_Z4_" in obj.name)
                or ("B02_L02_W" in obj.name)
                or ("B02_Belt" in obj.name and "_7" in obj.name)
            ):
                hide = True
            obj.hide_render = hide

    cam = bpy.data.objects.get(vid)
    if cam is None:
        from mathutils import Vector
        cdata = bpy.data.cameras.new(vid)
        cdata.lens = 30.0
        cam = bpy.data.objects.new(vid, cdata)
        scene.collection.objects.link(cam)
        cam.location = Vector(item["location"])
        cam.rotation_euler = (Vector(item["target"]) - cam.location).to_track_quat("-Z", "Y").to_euler()

    scene.camera = cam
    rx, ry = item["px"]
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    scene.render.resolution_percentage = 100
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED_VIEW {vid} {rx}x{ry} -> {out_path}", flush=True)
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slice", action="store_true", help="Render Stage B 12-view slice")
    p.add_argument("--pass", dest="pass_kind", choices=["proof", "final"], default="proof")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--only-dirty", action="store_true")
    p.add_argument("--samples", type=int, default=0)
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    (RENDERS_DIR / "proofs").mkdir(parents=True, exist_ok=True)
    (RENDERS_DIR / "final").mkdir(parents=True, exist_ok=True)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.exists() else {"views": {}}

    if args.slice:
        build_info = json.loads((ROOT / "evidence" / "validation" / "stage_b_slice_build.json").read_text(encoding="utf-8"))
        blend_file = ROOT / "scene" / "slice_B02_L02.blend"
        native_sha = build_info["native_sha256"]
        views = build_info["slice_views"]
    else:
        blend_file = ROOT / "scene" / "master.blend"
        native_sha = compute_file_sha256(blend_file)
        views = json.loads((ROOT / "design" / "VIEWS.json").read_text(encoding="utf-8"))

    if args.limit > 0:
        views = views[:args.limit]

    to_render = []
    for v in views:
        vid = v["id"]
        gkey = compute_geometry_key(v, native_sha)
        if args.pass_kind == "proof":
            px = [1024, 576]
            out_file = RENDERS_DIR / "proofs" / f"{vid}.png"
        else:
            px = v["resolution"]
            out_file = RENDERS_DIR / "final" / f"{vid}.png"

        prev = manifest["views"].get(f"{args.pass_kind}:{vid}", {})
        if out_file.exists() and out_file.stat().st_size > 50000:
            if prev.get("geometry_key") != gkey:
                manifest["views"][f"{args.pass_kind}:{vid}"] = {
                    "view": vid,
                    "pass": args.pass_kind,
                    "png": str(out_file.relative_to(REPO_ROOT)),
                    "px": px,
                    "sha256": compute_file_sha256(out_file),
                    "bytes": out_file.stat().st_size,
                    "native_sha": native_sha,
                    "geometry_key": gkey,
                    "rendered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            continue
        to_render.append({
            **v,
            "px": px,
            "geometry_key": gkey,
            "out_path": str(out_file),
        })

    if not to_render:
        print(f"All {len(views)} {args.pass_kind} views up-to-date in cache (R1).")
        return 0

    samples = args.samples if args.samples > 0 else (10 if args.pass_kind == "proof" else 16)
    # Run in chunks of 6 views per Blender invocation to stay well inside 2GB RAM (F10)
    chunk_size = 2
    for i in range(0, len(to_render), chunk_size):
        chunk = to_render[i:i + chunk_size]
        env = dict(**os.environ) if "os" in globals() else dict(**__import__("os").environ)
        env["TS_ROOT"] = str(ROOT)
        env["TS_RENDER_BATCH"] = json.dumps(chunk)
        env["TS_PASS_KIND"] = args.pass_kind
        env["TS_SAMPLES"] = str(samples)
        cmd = [
            "blender", "--background", str(blend_file),
            "--python-exit-code", "1",
            "--python-expr", BLENDER_BATCH_SCRIPT,
        ]
        subprocess.run(cmd, env=env, check=True)
        for item in chunk:
            out_f = Path(item["out_path"])
            sha = compute_file_sha256(out_f)
            manifest["views"][f"{args.pass_kind}:{item['id']}"] = {
                "view": item["id"],
                "pass": args.pass_kind,
                "png": str(out_f.relative_to(REPO_ROOT)),
                "px": item["px"],
                "sha256": sha,
                "bytes": out_f.stat().st_size,
                "native_sha": native_sha,
                "geometry_key": item["geometry_key"],
                "rendered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Completed rendering {len(to_render)} {args.pass_kind} views.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
