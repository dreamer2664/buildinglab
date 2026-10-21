#!/usr/bin/env python3
"""tools/bench.py — measure the ceiling before promising anything (F24, R3).

The packet says "achievable is proven with the campaign ledger, not with
optimism". This measures the two things that decide whether PNEUMA can be built
on this host:

  1. grain scaling   — rigid-body bake time and RAM at 250 / 500 / 1000 / 2000
                       grains, extrapolated against the commission's 48,000
  2. render scaling  — 3840x2160 at EEVEE_NEXT and Cycles, frames per hour

Usage:
  blender --background --python tools/bench.py --python-exit-code 1 -- --bench
"""
from __future__ import annotations

import json
import os
import resource
import sys
import time

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "evidence")
COMMISSION_GRAINS = 48000
COMMISSION_FRAMES = 10800


def rss_mb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)


def grains_scene(n: int, seed: int = 4711, frames: int = 120):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.05))
    f = bpy.context.active_object
    f.name = "FLOOR"
    f.scale = (1, 1, 0.05)
    bpy.ops.rigidbody.object_add()
    f.rigid_body.type = "PASSIVE"
    import random
    rng = random.Random(seed)
    for g in range(n):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.008,
                                              location=(rng.uniform(-0.1, 0.1),
                                                        rng.uniform(-0.1, 0.1),
                                                        0.55 + rng.uniform(0, 0.08)))
        o = bpy.context.active_object
        o.name = f"GRAIN_{g:05d}"
        bpy.ops.rigidbody.object_add()
        o.rigid_body.type = "ACTIVE"
        o.rigid_body.mass = 0.0002
        o.rigid_body.collision_shape = "SPHERE"
    return sc


def render_scene(engine: str, x: int, y: int, samples: int | None = None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = engine
    sc.render.resolution_x, sc.render.resolution_y = x, y
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = f"/tmp/_bench_{engine}_{x}x{y}.png"
    if samples is not None and engine == "CYCLES":
        sc.cycles.samples = samples
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -1))
    bpy.ops.object.light_add(type="AREA", location=(3, -3, 4))
    bpy.ops.object.camera_add(location=(4, -4, 2.5))
    cam = bpy.context.active_object
    import mathutils
    direction = mathutils.Vector((0, 0, 0)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return sc


def bench() -> dict:
    res = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "grain": [], "render": []}
    print("=== grain scaling (120 frames baked) ===")
    for n in (250, 500, 1000, 2000):
        sc = grains_scene(n)
        t0 = time.time()
        bpy.ops.ptcache.bake_all(bake=True)
        dt = time.time() - t0
        r = rss_mb()
        per_frame = dt / 120.0
        res["grain"].append({
            "grains": n, "frames": 120, "bake_s": round(dt, 2),
            "s_per_frame": round(per_frame, 4), "rss_mb": r,
            "hours_for_10800_frames": round(per_frame * COMMISSION_FRAMES / 3600, 1),
        })
        print(f"  {n:>6} grains · {dt:6.1f}s / 120 fr · {per_frame*1000:7.1f} ms/frame · "
              f"RSS {r} MB · extrapolated {per_frame*COMMISSION_FRAMES/3600:8.1f} h for 10,800 frames")

    print("\n=== render scaling ===")
    for engine, samples in (("BLENDER_EEVEE_NEXT", None), ("CYCLES", 16)):
        try:
            sc = render_scene(engine, 3840, 2160, samples)
            t0 = time.time()
            bpy.ops.render.render(write_still=False)
            dt = time.time() - t0
            res["render"].append({
                "engine": engine, "res": "3840x2160", "samples": samples,
                "s_per_frame": round(dt, 2),
                "hours_for_10800_frames": round(dt * COMMISSION_FRAMES / 3600, 1),
                "rss_mb": rss_mb(),
            })
            print(f"  {engine:<20} 3840x2160 samples={samples} · {dt:6.1f}s/frame · "
                  f"RSS {rss_mb()} MB · extrapolated {dt*COMMISSION_FRAMES/3600:8.1f} h for 10,800 frames")
        except Exception as e:
            res["render"].append({"engine": engine, "error": str(e)})
            print(f"  {engine:<20} FAILED: {e}")

    with open(os.path.join(OUT, "BENCH.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nbench: recorded to evidence/BENCH.json")
    return res


def main() -> None:
    argv = [a for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []) if a != "--"]
    os.makedirs(OUT, exist_ok=True)
    mode = argv[0].lstrip("-") if argv else "bench"
    if mode == "bench":
        bench()
    else:
        print(f"bench: unknown mode {mode}")


if __name__ == "__main__":
    main()
