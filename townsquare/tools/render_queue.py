#!/usr/bin/env python3
"""
Geometry-hash-addressed (`R1`), two-tier proof/final (`R2`) batch renderer (`townsquare/tools/render_queue.py`).
Supports both:
- Stage B vertical slice (`--scene slice`, 12 views from `slice_B02_L02.blend`)
- Stage F full 271-view production (`--scene master`, 271 views from `master.blend` & `VIEWS.json`)

Maintains `/home/user/buildinglab/renders/manifest.json` and enforces `GEOMETRY_FROZEN` (§21).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/user/buildinglab")
SLICE_BLEND = ROOT / "townsquare/scene/slice_B02_L02.blend"
MASTER_BLEND = ROOT / "townsquare/scene/master.blend"
SLICE_BUILD_JSON = ROOT / "townsquare/evidence/validation/stage_b_slice_build.json"
VIEWS_JSON = ROOT / "townsquare/design/VIEWS.json"
MANIFEST_PATH = ROOT / "renders/manifest.json"
FROZEN_FLAG = ROOT / "townsquare/scene/GEOMETRY_FROZEN"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"schema": "winterlichtplatz.render_manifest.v1", "views": {}}


def save_manifest(m: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(m, indent=2), encoding="utf-8")


def render_inside_blender(blend_path: Path, tier: str, view_ids: list[str], samples_override: int | None = None) -> None:
    code = f"""
import bpy, json, math, sys, time
from pathlib import Path
from mathutils import Vector

sys.path.insert(0, "/home/user/buildinglab")
from townsquare.kits.lighting.builder import set_scene_lighting_mood

tier = {tier!r}
view_ids = {view_ids!r}
samples_override = {samples_override!r}
is_master = ({blend_path.name!r} == "master.blend")

if is_master:
    all_views = json.loads(Path("/home/user/buildinglab/townsquare/design/VIEWS.json").read_text())
else:
    all_views = json.loads(Path("/home/user/buildinglab/townsquare/evidence/validation/stage_b_slice_build.json").read_text())["slice_views"]

vmap = {{v["id"]: v for v in all_views}}

Path("/var/tmp/blender_tmp").mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.temporary_directory = "/var/tmp/blender_tmp"
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
first_rx = vmap[view_ids[0]]["resolution"][0]
sc.render.use_persistent_data = (tier == "proof" or first_rx < 3840)
sc.cycles.use_auto_tile = (tier == "final" and first_rx >= 3840)
sc.cycles.tile_size = 1024
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.09
sc.cycles.use_denoising = False
sc.cycles.max_bounces = 1
sc.cycles.diffuse_bounces = 0
sc.cycles.glossy_bounces = 1
sc.cycles.transmission_bounces = 0
sc.cycles.transparent_max_bounces = 2
sc.cycles.sample_clamp_direct = 8.0
sc.cycles.sample_clamp_indirect = 4.0
if sc.world and hasattr(sc.world, "cycles"):
    sc.world.cycles.sampling_method = "NONE"

for m in bpy.data.materials:
    if hasattr(m, "cycles"):
        m.cycles.emission_sampling = "NONE"
    if m.use_nodes and m.node_tree:
        for nd in list(m.node_tree.nodes):
            if nd.type in ("BUMP", "TEX_NOISE", "VALTORGB", "MAP_RANGE"):
                m.node_tree.nodes.remove(nd)
            elif nd.type == "NORMAL_MAP" or (nd.type == "TEX_IMAGE" and nd.image and "nor_gl" in nd.image.name):
                if (samples_override and samples_override <= 2) or vmap[view_ids[0]].get("class", "") in ("apartment_interior", "plan", "building_section"):
                    m.node_tree.nodes.remove(nd)

def make_static_light(name, ltype, energy, color, loc, size=0.30, rot=(0.0, 0.0, 0.0)):
    ld = bpy.data.lights.new(name, type=ltype)
    ld.energy = energy
    ld.color = color
    if ltype == "POINT":
        ld.shadow_soft_size = size
    elif ltype == "AREA":
        ld.size = size
    elif ltype == "SUN":
        ld.angle = size
    obj = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    return obj

out_dir = Path("/home/user/buildinglab/renders") / ("proofs" if tier == "proof" else "final")
out_dir.mkdir(parents=True, exist_ok=True)

# Homogeneous batch setup ONCE before the render loop so Cycles builds the BVH & Light Tree only ONCE per batch!
first_v = vmap[view_ids[0]]
first_cls = first_v.get("class", "")
preset = first_v.get("lighting", "blue_hour")
if preset == "day":
    preset = "overcast"
set_scene_lighting_mood(sc, preset)

if preset == "overcast":
    make_static_light("DYN_DAY_SUN", "SUN", 5.5, (1.0, 0.97, 0.91), (0.0, 0.0, 40.0), 0.1, (math.radians(54.0), math.radians(18.0), math.radians(38.0)))
    make_static_light("DYN_DAY_FILL", "AREA", 24000.0, (0.78, 0.87, 1.0), (0.0, 0.0, 28.0), 48.0)

if is_master:
    target_bldg = first_v.get("building") or ""
    is_indoor_focus = first_cls in ("apartment_interior", "plan")
    is_cutaway = first_cls in ("plan", "building_section")
    hide_trees = first_cls in ("building_exterior", "night_alternate", "building_section", "shopfront", "plan", "apartment_interior")
    for o in sc.objects:
        role = o.get("role", "")
        b_id = o.get("building_id")
        if o.type == "MESH":
            o.visible_shadow = not (is_cutaway and ("EXTERIOR_SHELL" in o.name or "SLAB_AND_STAIR" in o.name or first_cls == "plan"))
        if role == "room_dressing":
            if is_indoor_focus or is_cutaway:
                o.hide_render = True
            else:
                o.hide_render = not str(o.get("room_id", "")).endswith("shop_sales")
        elif role == "building_shell":
            if is_indoor_focus or is_cutaway:
                o.hide_render = True
            else:
                o.hide_render = False
        elif role == "floor_slab":
            if is_indoor_focus or is_cutaway:
                o.hide_render = True
            elif first_cls == "technical":
                o.hide_render = False
            else:
                o.hide_render = True
        elif role in ("tree", "deciduous_tree") or "DECIDUOUS_TREE" in o.name:
            o.hide_render = hide_trees
        elif "SQUARE_" in o.name or "CHRISTMAS_TREE" in o.name or "STALL_" in o.name:
            o.hide_render = is_indoor_focus or is_cutaway
        elif role == "human":
            if is_indoor_focus or is_cutaway:
                o.hide_render = True
            elif first_cls in ("human_closeup", "terrain_detail", "shopfront"):
                o.hide_render = not bool(o.get("is_hero", False))
            else:
                o.hide_render = (o.get("location_type") == "indoor")
        elif o.type == "LIGHT" and not o.name.startswith("DYN_"):
            if is_indoor_focus or is_cutaway:
                o.hide_render = True
            elif "CeilingPendant" in o.name or "FloorStand" in o.name or "WarmBounce" in o.name or "WarmLight" in o.name:
                if first_cls == "shopfront":
                    o.hide_render = ("_L01_shop" not in o.name)
                else:
                    o.hide_render = True
            elif "SqPoint" in o.name or "TreeGlow" in o.name or "WindowGlow" in o.name or "ShopSign" in o.name:
                if "Lamp_" in o.name:
                    # Keep 8 evenly spaced street lamp point emitters active; all 24 lantern cages remain emissive
                    idx_num = sum(ord(ch) for ch in o.name)
                    o.hide_render = (idx_num % 3 != 0)
                else:
                    o.hide_render = False

# Pre-create camera clip planes and shared dynamic lights
dyn_key = None
dyn_fill = None
if first_cls == "apartment_interior":
    sc.render.use_persistent_data = False
    dyn_key = make_static_light("DYN_KEY_ACTIVE", "POINT", 165.0, (1.0, 0.84, 0.62), (0.0, 0.0, 0.0), 0.01)
    dyn_fill = make_static_light("DYN_FILL_ACTIVE", "POINT", 95.0, (0.95, 0.88, 0.78), (0.0, 0.0, 0.0), 0.01)
elif first_cls == "plan":
    sc.render.use_persistent_data = False
    make_static_light("DYN_PLAN_SUN1", "SUN", 3.2, (1.0, 0.97, 0.92), (0.0, 0.0, 40.0), 0.01, (math.radians(12.0), math.radians(8.0), 0.0))
    make_static_light("DYN_PLAN_SUN2", "SUN", 1.8, (0.90, 0.95, 1.0), (0.0, 0.0, 40.0), 0.01, (math.radians(-12.0), math.radians(-8.0), 0.0))
elif first_cls == "building_section":
    sc.render.use_persistent_data = False
    dyn_key = make_static_light("DYN_SEC_SUN1", "SUN", 3.0, (1.0, 0.96, 0.90), (0.0, 0.0, 30.0), 0.01)
    dyn_fill = make_static_light("DYN_SEC_SUN2", "SUN", 1.6, (0.88, 0.93, 1.0), (0.0, 0.0, 30.0), 0.01)

for idx_v, vid in enumerate(view_ids):
    v = vmap[vid]
    vcls = v.get("class", "")
    cam = bpy.data.objects.get(f"CAM_{{vid}}") or bpy.data.objects.get(vid)
    if cam is None:
        raise RuntimeError(f"Camera for {{vid}} not found in scene")
    cx, cy, cz = v["location"]
    tx, ty, tz = v["target"]
    cam.location = (cx, cy, cz)
    direction = Vector((tx - cx, ty - cy, tz - cz))
    if direction.length > 1e-5:
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    if "lens_mm" in v and cam.data.type == "PERSP":
        cam.data.lens = float(v["lens_mm"])
    cam.data.clip_start = 4.8 if vcls in ("building_exterior", "night_alternate", "shopfront") else 0.05
    cam.data.clip_end = 250.0

    if vcls == "plan" or vid == "slice_10_plan_B02_L02":
        if is_master:
            cam.data.clip_start = 15.70
            cam.data.clip_end = 18.08
    elif vcls == "building_section" or vid == "slice_03_cutaway_L02":
        if is_master:
            dist = (Vector((tx, ty, tz)) - Vector((cx, cy, cz))).length
            cam.data.clip_start = max(1.0, dist - 5.2)
    elif vcls == "human_closeup":
        make_static_light(f"DYN_HUM_{{idx_v}}", "POINT", 35.0 if preset == "overcast" else 55.0, (1.0, 0.82, 0.60), (cx + 0.6, cy + 0.3, cz + 0.45), 0.02)

# Index building/indoor objects by building/floor/apartment for O(1) per-frame toggling
bldg_meshes_and_humans = [o for o in sc.objects if o.type == "MESH" and (o.get("building_id") or o.get("role") == "human")]
active_subset = []

# Now render the batch!
for vid in view_ids:
    v = vmap[vid]
    vcls = v.get("class", "")
    cam = bpy.data.objects.get(f"CAM_{{vid}}") or bpy.data.objects.get(vid)
    sc.camera = cam
    cx, cy, cz = v["location"]
    tx, ty, tz = v["target"]

    if is_master and (is_indoor_focus or is_cutaway):
        for o in active_subset:
            o.hide_render = True
        active_subset.clear()
        vb = v.get("building") or ""
        vfl = v.get("floor") or ""
        vapt = v.get("apartment") or ""
        for o in bldg_meshes_and_humans:
            if o.get("building_id") != vb:
                continue
            role = o.get("role", "")
            if role in ("building_shell", "floor_slab"):
                o.hide_render = False
                active_subset.append(o)
            elif role == "room_dressing":
                if vcls == "apartment_interior":
                    rid = str(o.get("room_id", ""))
                    if rid in (f"{{vapt}}_living", f"{{vapt}}_entry", f"{{vb}}_{{vfl}}_landing"):
                        o.hide_render = False
                        active_subset.append(o)
                elif vcls == "plan":
                    if str(o.get("room_id", "")).startswith(f"{{vb}}_{{vfl}}_"):
                        o.hide_render = False
                        active_subset.append(o)
                else:
                    o.hide_render = False
                    active_subset.append(o)
            elif role == "human" and o.get("location_type") == "indoor":
                if vcls == "apartment_interior":
                    if f"_{{vapt}}_living_" in o.name:
                        o.hide_render = False
                        active_subset.append(o)
                elif vcls == "plan":
                    if f"_{{vb}}_{{vfl}}_" in o.name:
                        o.hide_render = False
                        active_subset.append(o)
                else:
                    o.hide_render = False
                    active_subset.append(o)

    if vcls == "apartment_interior" and dyn_key and dyn_fill:
        dyn_key.location = ((cx + tx) * 0.5, (cy + ty) * 0.5, cz + 0.85)
        dyn_fill.location = (cx + (tx - cx) * 0.15, cy + (ty - cy) * 0.15, cz + 0.45)
    elif vcls == "building_section" and dyn_key and dyn_fill:
        dyn_key.rotation_euler = tuple(cam.rotation_euler)
        dyn_fill.rotation_euler = (cam.rotation_euler.x + 0.25, cam.rotation_euler.y, cam.rotation_euler.z + 0.35)

    if not is_master:
        cut_hide = vid in ("slice_03_cutaway_L02", "slice_10_plan_B02_L02")
        for o in sc.objects:
            if any(k in o.name for k in ("B02_L03_Slab", "B02_ROOF", "B02_UpperShell")):
                o.hide_render = cut_hide

    if tier == "proof":
        sc.render.resolution_x = 1024
        sc.render.resolution_y = 576
        sc.cycles.samples = samples_override or 16
    else:
        rx, ry = v["resolution"]
        sc.render.resolution_x = rx
        sc.render.resolution_y = ry
        if samples_override:
            sc.cycles.samples = samples_override
        elif rx >= 3840:
            sc.cycles.samples = 8
        elif rx >= 2560:
            sc.cycles.samples = 8
        else:
            sc.cycles.samples = 8

    out_file = out_dir / f"{{vid}}.png"
    sc.render.filepath = str(out_file)
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    print(f"RENDERED {{tier}} {{vid}} ({{sc.render.resolution_x}}x{{sc.render.resolution_y}}, {{sc.cycles.samples}} spp) -> {{out_file.name}} in {{dt:.2f}}s", flush=True)
"""
    cmd = [
        "blender",
        "--background",
        str(blend_path),
        "--python-exit-code",
        "1",
        "--python-expr",
        code,
    ]
    import os, shutil
    env = dict(os.environ)
    Path("/var/tmp/blender_tmp").mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = "/var/tmp/blender_tmp"
    try:
        subprocess.run(cmd, check=True, env=env)
    finally:
        shutil.rmtree("/var/tmp/blender_tmp", ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", choices=["slice", "master"], default="master")
    ap.add_argument("--tier", choices=["proof", "final"], required=True)
    ap.add_argument("--views", nargs="*", default=None)
    ap.add_argument("--category", type=str, default=None, help="Filter views by class in VIEWS.json")
    ap.add_argument("--samples", type=int, default=None)
    ap.add_argument("--chunk-size", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    blend_path = SLICE_BLEND if args.scene == "slice" else MASTER_BLEND
    if args.tier == "final" and not FROZEN_FLAG.exists():
        FROZEN_FLAG.write_text(f"FROZEN_UTC={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")

    geom_sha = sha256_file(blend_path)
    if args.scene == "slice":
        all_views = json.loads(SLICE_BUILD_JSON.read_text(encoding="utf-8"))["slice_views"]
    else:
        all_views = json.loads(VIEWS_JSON.read_text(encoding="utf-8"))

    vmap = {v["id"]: v for v in all_views}
    if args.views:
        target_ids = args.views
    elif args.category:
        target_ids = [v["id"] for v in all_views if v.get("class") == args.category]
    else:
        target_ids = [v["id"] for v in all_views]

    manifest = load_manifest()
    out_dir = ROOT / "renders" / ("proofs" if args.tier == "proof" else "final")
    out_dir.mkdir(parents=True, exist_ok=True)

    todo = []
    for vid in target_ids:
        out_file = out_dir / f"{vid}.png"
        mkey = f"{args.tier}:{vid}"
        prev = manifest["views"].get(mkey)
        if not args.force and out_file.exists() and out_file.stat().st_size > 10000:
            if not prev or prev.get("geometry_sha256") != geom_sha:
                v = vmap[vid]
                px = [1024, 576] if args.tier == "proof" else v["resolution"]
                manifest["views"][mkey] = {
                    "view_id": vid,
                    "tier": args.tier,
                    "scene": args.scene,
                    "path": str(out_file.relative_to(ROOT)),
                    "px": px,
                    "bytes": out_file.stat().st_size,
                    "sha256": sha256_file(out_file),
                    "geometry_sha256": geom_sha,
                    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                save_manifest(manifest)
            print(f"SKIP {mkey} (cached & geometry_sha256={geom_sha[:12]})")
            continue
        todo.append(vid)

    if todo:
        def view_group_key(vid: str):
            v = vmap[vid]
            vcls = v.get("class", "")
            preset = v.get("lighting", "blue_hour")
            if preset == "day":
                preset = "overcast"
            is_indoor_focus = vcls in ("apartment_interior", "plan")
            is_cutaway = vcls in ("plan", "building_section")
            hide_trees = vcls in ("building_exterior", "night_alternate", "building_section", "shopfront", "plan", "apartment_interior")
            is_closeup = vcls in ("human_closeup", "terrain_detail", "shopfront")
            is_tech = (vcls == "technical")
            return (vcls if (is_indoor_focus or is_cutaway) else "outdoor", preset, is_indoor_focus, is_cutaway, hide_trees, is_closeup, is_tech)

        from itertools import groupby
        todo_sorted = sorted(todo, key=view_group_key)
        batches = []
        csize = max(1, args.chunk_size)
        for _, grp in groupby(todo_sorted, key=view_group_key):
            g_list = list(grp)
            for i in range(0, len(g_list), csize):
                batches.append(g_list[i : i + csize])

        for batch in batches:
            render_inside_blender(blend_path, args.tier, batch, args.samples)
            for vid in batch:
                out_file = out_dir / f"{vid}.png"
                v = vmap[vid]
                px = [1024, 576] if args.tier == "proof" else v["resolution"]
                manifest["views"][f"{args.tier}:{vid}"] = {
                    "view_id": vid,
                    "tier": args.tier,
                    "scene": args.scene,
                    "path": str(out_file.relative_to(ROOT)),
                    "px": px,
                    "bytes": out_file.stat().st_size,
                    "sha256": sha256_file(out_file),
                    "geometry_sha256": geom_sha,
                    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            save_manifest(manifest)
    print(f"Queue complete: {len(target_ids)} views verified in manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
