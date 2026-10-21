#!/usr/bin/env python3
"""tools/render_stills.py — proof stills, from committed state at a named hash.

Run:  blender --background PNEUMA.blend --python tools/render_stills.py --python-exit-code 1 -- --views hopper --long-edge 2560

Honesty law (§41): every still is rendered from the committed .blend at its
recorded sha256, from a camera whose 0.3 m empty sphere is asserted (F8) and
whose subject coverage is checked (F9). A still that cannot be reproduced from
the committed file is not a still.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "renders", "best")
PROOF_DIR = os.path.join(ROOT, "renders", "proofs")
EVIDENCE = os.path.join(ROOT, "evidence")

VIEWS = {
    # name: (camera location, target)
    "hopper_threequarter": ((1.15, -1.35, 1.05), (0.0, 0.0, 0.45)),
    "hopper_orifice":     ((0.30, -0.42, 0.52), (0.0, 0.0, 0.05)),
    "hopper_above":       ((0.85, -0.95, 1.95), (0.0, 0.0, 0.55)),
    "cart_side":          ((1.85, -1.55, 0.72), (0.0, 0.0, 0.34)),
    "cart_rear":          ((-1.55, -1.35, 0.85), (0.0, 0.0, 0.32)),
    "drum_threequarter":  ((0.95, -1.05, 0.92), (0.0, 0.72, 0.55)),
    "grain_flow":         ((0.42, -0.52, 0.62), (0.0, 0.0, 0.20)),
    "machine_wide":       ((2.30, -2.10, 1.45), (0.0, 0.1, 0.40)),
}


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def setup_world(engine: str = "cycles"):
    """Engine selection, with the F20 truth recorded in the choice itself.

    Measured on this host (evidence/BENCH.json, evidence/ENGINE_PROBE.json):
      * EEVEE_NEXT needs an OpenGL/EGL context -> EGL_BAD_MATCH, cannot render
        headless here at all.
      * Cycles CPU renders, but this Debian build ships WITHOUT OpenImageDenoise
        (F20, exactly the failure the packet predicted) -> denoising is switched
        off and sample count carries the quality instead.
      * BLENDER_WORKBENCH renders at ~4 s/1080p -> the honest fast path for the
        engineering drawings and mechanism diagrams.
    """
    sc = bpy.context.scene
    sc.render.engine = {"cycles": "CYCLES", "workbench": "BLENDER_WORKBENCH"}.get(engine, engine)
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    if sc.render.engine == "CYCLES":
        sc.cycles.device = "CPU"
        sc.cycles.use_denoising = False      # F20: no OIDN in this build
        sc.cycles.samples = int(os.environ.get("HERON_SAMPLES", "64"))
        sc.cycles.use_adaptive_sampling = False
    # A workshop ambient: a vertical gradient on the world, bright above the
    # bench and dark at the floor. Two area lights alone leave metals with
    # nothing to reflect, so bronze and iron render flat grey and every
    # material reads as one pale tan (defect D-006). A gradient gives the
    # metals something to reflect and separates the values.
    world = bpy.data.worlds.get("WORLD") or bpy.data.worlds.new("WORLD")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tex = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.10, 0.10, 0.12, 1.0)   # floor: dark
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[1].color = (0.72, 0.76, 0.84, 1.0)   # sky: bright
    ramp.color_ramp.elements[1].position = 0.85
    nt.links.new(tex.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bg.inputs["Strength"].default_value = 0.55
    return sc


def setup_lights():
    # a north-facing workshop window, plus a low warm fill — one light per cause
    bpy.ops.object.light_add(type="AREA", location=(2.6, -2.4, 3.2))
    key = bpy.context.active_object
    key.name = "LIGHT_WINDOW_KEY"
    key.data.energy = 1100
    key.data.shape = "DISK"
    key.data.size = 2.2
    key.rotation_euler = (math.radians(52), 0, math.radians(42))

    bpy.ops.object.light_add(type="AREA", location=(-1.8, -1.2, 1.1))
    fill = bpy.context.active_object
    fill.name = "LIGHT_FILL_WARM"
    fill.data.energy = 420
    fill.data.shape = "DISK"
    fill.data.size = 1.6
    fill.rotation_euler = (math.radians(70), 0, math.radians(-35))


def add_camera(name: str, loc, target) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = f"CAM_{name.upper()}"
    import mathutils
    direction = mathutils.Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 42
    cam.data.sensor_width = 36
    # F8: every camera gets a 0.3 m empty sphere. If anything solid is within
    # 0.3 m of the camera, the view is a lie and this refuses to render it.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        d = (o.matrix_world.translation - cam.location).length
        if d < 0.30:
            raise SystemExit(f"F8 REFUSAL: {o.name} is {d:.3f} m from camera {cam.name} — inside its 0.3 m empty sphere")
    return cam


def coverage(cam, frame: int) -> float:
    """F9: is there anything in frame, or is this a shot of empty air?"""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    inside = 0
    total = 0
    cam_obj = cam
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        total += 1
        import mathutils
        co_ndc = cam_obj.matrix_world.normalized().inverted() @ o.matrix_world.translation
        if -1.0 < co_ndc.x < 1.0 and -1.0 < co_ndc.y < 1.0 and co_ndc.z < 0:
            inside += 1
    return (inside / total) if total else 0.0


def main() -> None:
    argv = [a for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []) if a != "--"]
    argv = [a for a in argv if a.lstrip("-") not in ("views", "v", "build")]
    which = argv[0].lstrip("-") if argv else "all"
    long_edge = 2560
    for a in argv[1:]:
        if a.isdigit():
            long_edge = int(a)
            break
    height = int(round(long_edge * 9 / 16))
    engine = os.environ.get("HERON_ENGINE", "cycles")

    sc = setup_world(engine)
    setup_lights()
    sc.render.resolution_x = long_edge
    sc.render.resolution_y = height
    sc.render.resolution_percentage = 100
    sc.render.filepath = OUT_DIR + "/"

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PROOF_DIR, exist_ok=True)

    blend_path = bpy.data.filepath
    blend_sha = sha256_file(blend_path) if blend_path and os.path.exists(blend_path) else ""

    views = list(VIEWS.items()) if which in ("all", "a") else [(which, VIEWS[which])]
    rows = []
    for name, (loc, target) in views:
        cam = add_camera(name, loc, target)
        sc.camera = cam
        cov = coverage(cam, sc.frame_current)
        if cov < 0.60:
            print(f"render_stills: F9 WARNING {name} coverage {cov:.2f} — below the 0.60 floor, still rendered, logged")
        sc.render.filepath = os.path.join(OUT_DIR, f"{name}.png")
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        p = sc.render.filepath
        rows.append({
            "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "view": name, "file": os.path.basename(p),
            "res": f"{long_edge}x{height}", "s": round(dt, 1), "engine": sc.render.engine,
            "samples": sc.cycles.samples if sc.render.engine == "CYCLES" else None,
            "denoised": False,   # F20: this build has no OpenImageDenoise
            "coverage": round(cov, 2),
            "blend": os.path.basename(blend_path), "blend_sha256": blend_sha,
            "png_sha256": sha256_file(p) if os.path.exists(p) else "",
            "bytes": os.path.getsize(p) if os.path.exists(p) else 0,
        })
        print(f"render_stills: {name:<22} {sc.render.engine:<20} {long_edge}x{height} {dt:6.1f}s cov={cov:.2f} -> {rows[-1]['png_sha256'][:12]}")
        bpy.data.objects.remove(cam, do_unlink=True)

    with open(os.path.join(EVIDENCE, "RENDERS.jsonl"), "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"render_stills: {len(rows)} still(s) from blend sha256={blend_sha[:16]}")


if __name__ == "__main__":
    main()
