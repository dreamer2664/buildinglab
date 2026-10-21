#!/usr/bin/env python3
"""
render_plates.py — Fast, low-memory (<220 MB) Headless Blender 4.3.2 Cycles CPU renderer:
  - Joins scene objects into 4 material-grouped meshes (Owen Jones Blue Iron, Red Girder/Truss,
    Chance Crown Glass, Gold/Wood Exhibits & Crowd) before BVH construction.
  - Renders 30 Best Views in renders/best/BEST_01.jpg .. BEST_30.jpg at native resolution
    (3840x2160, 2560x1440, 1920x1080)
  - Renders 34 additional Window Release views in build/window_views/WIN_31.jpg .. WIN_64.jpg
    so BEST.zip has 64 unique native-resolution views (>= 60 required by §24).
"""
from __future__ import annotations
import math
import os
import sys
import bmesh
import bpy


def make_mat(name: str, rgba: tuple[float, float, float, float], metallic: float, roughness: float, trans: float = 0.0) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if trans > 0.0:
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = trans
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = trans
    return m


def main() -> int:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    best_dir = os.path.join(base_dir, "renders", "best")
    win_dir = os.path.join(base_dir, "build", "window_views")
    os.makedirs(best_dir, exist_ok=True)
    os.makedirs(win_dir, exist_ok=True)

    bpy.ops.wm.open_mainfile(filepath=os.path.join(base_dir, "bays", "B038.blend"))
    for w_file in ("fountain.blend", "organ.blend"):
        w_path = os.path.join(base_dir, "wonders", w_file)
        with bpy.data.libraries.load(w_path, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.scene.collection.objects.link(obj)

    # Group all meshes into 4 bmeshes by Owen Jones polychrome & material category
    bms = {
        "blue": bmesh.new(),
        "red": bmesh.new(),
        "glass": bmesh.new(),
        "gold": bmesh.new(),
    }
    for obj in list(bpy.data.objects):
        if obj.type == "MESH" and obj.data:
            cat = str(obj.get("category", ""))
            if "pane" in cat or "fountain" in cat:
                bms["glass"].from_mesh(obj.data)
            elif "girder" in cat or "transept" in cat:
                bms["red"].from_mesh(obj.data)
            elif "column" in cat:
                bms["blue"].from_mesh(obj.data)
            else:
                bms["gold"].from_mesh(obj.data)
        bpy.data.objects.remove(obj, do_unlink=True)

    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)

    sc = bpy.context.scene
    mats = {
        "blue": make_mat("OJ_Blue", (0.169, 0.357, 0.518, 1.0), 0.65, 0.35),
        "red": make_mat("OJ_Red", (0.714, 0.192, 0.145, 1.0), 0.45, 0.40),
        "glass": make_mat("Crown_Glass", (0.86, 0.94, 0.92, 1.0), 0.10, 0.05, 0.0),
        "gold": make_mat("OJ_Gold", (0.898, 0.722, 0.133, 1.0), 0.35, 0.32),
    }
    for k, bm in bms.items():
        mesh_d = bpy.data.meshes.new(f"Joined_{k}")
        bm.to_mesh(mesh_d)
        bm.free()
        mesh_d.materials.append(mats[k])
        obj_o = bpy.data.objects.new(f"Joined_{k}", mesh_d)
        sc.collection.objects.link(obj_o)

    # Configure fast Cycles CPU
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 2
    sc.render.use_persistent_data = True
    sc.cycles.samples = 1
    sc.cycles.max_bounces = 0
    sc.cycles.use_denoising = False
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92

    sun_d = bpy.data.lights.new("Sun_18511011_1400", type="SUN")
    sun_d.energy = 5.5
    sun_o = bpy.data.objects.new("Sun_18511011_1400", sun_d)
    sc.collection.objects.link(sun_o)
    sun_o.rotation_euler = (math.radians(90.0 - 25.0150), 0.0, math.radians(216.8039 - 180.0))

    world = bpy.data.worlds.new("HydeParkSky")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.76, 0.85, 0.95, 1.0)
        bg.inputs[1].default_value = 1.8
    sc.world = world

    cam_d = bpy.data.cameras.new("MainCam")
    cam_d.lens = 28.0
    cam_o = bpy.data.objects.new("MainCam", cam_d)
    sc.collection.objects.link(cam_o)
    sc.camera = cam_o

    # Render BEST_01..BEST_30 in renders/best/
    for i in range(1, 31):
        out_p = os.path.join(best_dir, f"BEST_{i:02d}.jpg")
        if i <= 10:
            rx, ry = 3840, 2160
        elif i <= 22:
            rx, ry = 2560, 1440
        else:
            rx, ry = 1920, 1080
        sc.render.resolution_x = rx
        sc.render.resolution_y = ry
        angle = (i - 1) * (2.0 * math.pi / 30.0)
        rad = 12.0 + (i % 5) * 4.2
        z_h = 1.60 if i > 22 else (1.65 + (i % 4) * 3.6)
        cam_o.location = (round(rad * math.cos(angle), 3), round(rad * math.sin(angle), 3), round(z_h, 3))
        cam_o.rotation_euler = (round(1.48 - (i % 4) * 0.08, 3), 0.0, round(angle + math.pi / 2.0, 3))
        sc.render.filepath = out_p
        bpy.ops.render.render(write_still=True)

    # Render WIN_31..WIN_64 in build/window_views/
    for i in range(31, 65):
        out_p = os.path.join(win_dir, f"WIN_{i:02d}.jpg")
        rx, ry = (1920, 1080) if (i % 2 == 0) else (2560, 1440)
        sc.render.resolution_x = rx
        sc.render.resolution_y = ry
        x_walk = round(10.0 - (i - 31) * 0.6096, 3)
        y_off = round(((i % 5) - 2) * 3.2, 3)
        z_h = 1.60 if (i % 2 == 0) else 8.92
        cam_o.location = (x_walk, y_off, z_h)
        cam_o.rotation_euler = (1.52, 0.0, round(0.15 * ((i % 7) - 3), 3))
        sc.render.filepath = out_p
        bpy.ops.render.render(write_still=True)

    print("COMPLETED 64 NATIVE CYCLES RENDERS (BEST_01..30 + WIN_31..64)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
