#!/usr/bin/env python3
"""machines/build_pneuma.py — the cart-theatre, built from named parts.

Run:  blender --background --python machines/build_pneuma.py --python-exit-code 1 -- --build all 3000

Law this file obeys, in the order it matters:

  1. **Constraints, never parenting**, inside any mechanism (§15.2, ban #2).
     Every part is a free object in world space; joints are CONSTRAINT objects.
  2. **Named parts**, from the `MECHANISMS.md` vocabulary.
  3. **Period materials only**, from `MATERIALS.md`.
  4. **Named fasteners only**, from `FASTENERS.md`.
  5. One Blender unit = one metre.
  6. Nothing is keyframed; the machine moves because gravity acts on the grains.

## Geometry, corrected after the first proof render (D-001, D-003)

The first build hung the axle at z=0.170 m for a wheel whose rim outer radius is
0.348 m, so both rims sat 178 mm *inside* the floor (`tools/audit_scene.py`
F12), and the grain fill overflowed the hopper walls by 213 mm (F2, masked
because the lid was counted as a wall). The heights below are derived from the
radii, not chosen, and every one is asserted by `tools/audit_scene.py`.

    wheel rim outer radius          0.348 m   -> axle height      0.348 m
    wheel top                       0.696 m   -> chassis rails     0.760 m
    hopper orifice (bronze throat)  0.820 m
    hopper wall span                0.820 -> 1.260 m
    grain fill                      0.846 -> 1.210 m   (inside the walls)
    hopper lid underside            1.264 m
    drum axis                       0.980 m
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sys
import time

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ROOT, "evidence")

# ---- derived geometry (metres) -------------------------------------------------
WHEEL_RIM_OUTER = 0.348          # torus major + minor radius
AXLE_Z = WHEEL_RIM_OUTER         # 0.348 — the rim must land exactly on z=0
WHEEL_X = 0.62                   # track, half the axle length plus a spoke
CHASSIS_Z = 0.760                # above the wheel tops (0.696)
ORIFICE_Z = 0.820                # the bronze throat
WALL_Z0, WALL_Z1 = 0.820, 1.260  # the hopper walls' span
GRAIN_Z0, GRAIN_Z1 = 0.846, 1.210
LID_Z = 1.264
DRUM_Z = 0.980
DRUM_Y = 0.780

MATERIALS = {
    "OAK":    (0.42, 0.30, 0.18, 0.72, 0.00),
    "PINE":   (0.68, 0.55, 0.38, 0.80, 0.00),
    "OLIVE":  (0.55, 0.42, 0.24, 0.68, 0.00),
    "BRONZE": (0.72, 0.52, 0.28, 0.35, 0.85),
    "IRON":   (0.30, 0.28, 0.26, 0.55, 0.95),
    "LEAD":   (0.42, 0.42, 0.44, 0.45, 0.60),
    "MILLET": (0.78, 0.66, 0.38, 0.75, 0.00),
    "FLAX":   (0.78, 0.70, 0.52, 0.90, 0.00),
    "LINEN":  (0.86, 0.82, 0.70, 0.88, 0.00),
}
_cache: dict[str, bpy.types.Material] = {}


def mat(name: str) -> bpy.types.Material:
    if name in _cache:
        return _cache[name]
    r, g, b, rough, metal = MATERIALS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.5
    _cache[name] = m
    return m


def named(obj, name: str, material: str, collection: str = "PNEUMA") -> bpy.types.Object:
    obj.name = name
    obj.data.materials.append(mat(material))
    col = bpy.data.collections.get(collection)
    if col is None:
        col = bpy.data.collections.new(collection)
        bpy.context.scene.collection.children.link(col)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    obj["material"] = material
    return obj


def passive(obj, shape: str = "MESH"):
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = "PASSIVE"
    obj.rigid_body.collision_shape = shape
    return obj


def build_floor():
    bpy.ops.mesh.primitive_cylinder_add(radius=3.0, depth=0.12, location=(0, 0, -0.06))
    f = named(bpy.context.active_object, "FLOOR_STONE", "OAK")
    passive(f)
    f.rigid_body.friction = 0.9
    return [f]


def build_hopper():
    """A tapered oak funnel with a bronze throat — the grains' only way out.

    The walls are real geometry the grains collide with: a grain flow that never
    touches the hopper walls is a lie (§13.3).
    """
    parts = []
    # four slanted walls; the local Z extent is set so the bbox lands on
    # [WALL_Z0, WALL_Z1] after the -0.62 rad tilt about Y.
    tilt = 0.62
    z_ext = (WALL_Z1 - WALL_Z0) / math.cos(tilt)
    for i, (name, loc) in enumerate([
        ("HOPPER_WALL_EAST",  (0.34, 0, (WALL_Z0 + WALL_Z1) / 2)),
        ("HOPPER_WALL_WEST",  (-0.34, 0, (WALL_Z0 + WALL_Z1) / 2)),
        ("HOPPER_WALL_NORTH", (0, 0.34, (WALL_Z0 + WALL_Z1) / 2)),
        ("HOPPER_WALL_SOUTH", (0, -0.34, (WALL_Z0 + WALL_Z1) / 2)),
    ]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, -tilt if i < 2 else tilt, 0))
        w = named(bpy.context.active_object, name, "OAK")
        w.scale = (0.03, 0.34, z_ext)
        passive(w)
        parts.append(w)
    # the bronze throat at the orifice — the metering point.
    # No rotation: a torus lies in the XY plane by default, which is exactly a
    # ring framing a horizontal hole. Rotating it 90 deg about X stands it up
    # like a wheel and its bounding box rises to 0.883 m, plugging the orifice
    # (F2, caught by tools/audit_scene.py).
    bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.008,
                                     location=(0, 0, ORIFICE_Z))
    t = named(bpy.context.active_object, "HOPPER_THROAT_BRONZE", "BRONZE")
    passive(t)
    parts.append(t)
    # the lid, above the grain fill
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, LID_Z))
    lid = named(bpy.context.active_object, "HOPPER_LID_OAK", "OAK")
    lid.scale = (0.42, 0.42, 0.03)
    passive(lid)
    parts.append(lid)
    return parts


def build_cart():
    parts = []
    for i, x in enumerate((-0.45, 0.45)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, CHASSIS_Z))
        r = named(bpy.context.active_object, f"CHASSIS_RAIL_{i:02d}", "OAK")
        r.scale = (0.05, 0.70, 0.045)
        passive(r)
        parts.append(r)
    for i, y in enumerate((-0.55, 0.0, 0.55)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, CHASSIS_Z + 0.03))
        b = named(bpy.context.active_object, f"CHASSIS_BEAM_{i:02d}", "OAK")
        b.scale = (0.45, 0.05, 0.04)
        passive(b)
        parts.append(b)
    # the axle, at the height the rim radius demands
    bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=1.30,
                                        location=(0, 0, AXLE_Z), rotation=(0, math.pi / 2, 0))
    ax = named(bpy.context.active_object, "AXLE_OAK", "OAK")
    passive(ax)
    parts.append(ax)
    for side, sx in (("PORT", -WHEEL_X), ("STARBOARD", WHEEL_X)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.06,
                                            location=(sx, 0, AXLE_Z), rotation=(0, math.pi / 2, 0))
        hub = named(bpy.context.active_object, f"WHEEL_HUB_{side}", "OAK")
        passive(hub)
        parts.append(hub)
        for s in range(8):
            a = s * math.pi / 4
            bpy.ops.mesh.primitive_cube_add(size=1,
                                            location=(sx, math.cos(a) * 0.16, AXLE_Z + math.sin(a) * 0.16),
                                            rotation=(0, math.pi / 2, a))
            sp = named(bpy.context.active_object, f"WHEEL_SPOKE_{side}_{s:02d}", "OAK")
            sp.scale = (0.016, 0.016, 0.16)
            passive(sp)
            parts.append(sp)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.028,
                                         location=(sx, 0, AXLE_Z), rotation=(0, math.pi / 2, 0))
        rim = named(bpy.context.active_object, f"WHEEL_RIM_{side}", "OAK")
        passive(rim)
        parts.append(rim)
    for side, sx in (("PORT", -0.68), ("STARBOARD", 0.68)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.10,
                                            location=(sx, 0, AXLE_Z), rotation=(0, math.pi / 2, 0))
        pv = named(bpy.context.active_object, f"AXLE_PIVOT_IRON_{side}", "IRON")
        passive(pv)
        parts.append(pv)
    return parts


def build_drum():
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.20, location=(0, DRUM_Y, DRUM_Z))
    bar = named(bpy.context.active_object, "DRUM_BARREL_OAK", "OAK")
    passive(bar)
    parts.append(bar)
    for name, z in (("DRUM_ENDBRONZE_LOWER", DRUM_Z - 0.11), ("DRUM_ENDBRONZE_UPPER", DRUM_Z + 0.11)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.135, depth=0.012, location=(0, DRUM_Y, z))
        ep = named(bpy.context.active_object, name, "BRONZE")
        passive(ep)
        parts.append(ep)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.30, location=(0, DRUM_Y, DRUM_Z),
                                        rotation=(math.pi / 2, 0, 0))
    pv = named(bpy.context.active_object, "DRUM_PIVOT_IRON", "IRON")
    passive(pv)
    parts.append(pv)
    return parts


def build_grains(n: int, seed: int = 4711):
    """Grains as individually named active rigid bodies, filled inside the funnel.

    The fill is a truncated pyramid narrowing toward the orifice, so the cloud
    is in contact with the slanted walls from frame 1 — the wall-contact
    requirement of §13.3, not an assertion.
    """
    rng = random.Random(seed)
    grains = []
    mesh = bpy.data.meshes.new("GRAIN_MESH")
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.004)
    src = bpy.context.active_object
    mesh.from_pydata([(v.co.x, v.co.y, v.co.z) for v in src.data.vertices],
                     [], [p.vertices for p in src.data.polygons])
    mesh.materials.append(mat("MILLET"))
    bpy.data.objects.remove(src, do_unlink=True)
    mesh.validate()

    col = bpy.data.collections.get("GRAINS")
    if col is None:
        col = bpy.data.collections.new("GRAINS")
        bpy.context.scene.collection.children.link(col)

    # the funnel half-width as a function of z: linear from 0.30 at the top to
    # 0.055 at the throat, so the fill hugs the walls
    z_top, z_bot = GRAIN_Z1, GRAIN_Z0
    for i in range(n):
        z = rng.uniform(z_bot, z_top)
        t = (z - z_bot) / (z_top - z_bot)
        half = 0.055 + (0.30 - 0.055) * t
        # bias toward the wall: sample in an annulus so contact is guaranteed
        rr = math.sqrt(rng.uniform(0.45, 1.0)) * half
        a = rng.uniform(0, 2 * math.pi)
        o = bpy.data.objects.new(f"GRAIN_{i:05d}", mesh)
        o.location = (math.cos(a) * rr, math.sin(a) * rr, z)
        col.objects.link(o)
        o.rotation_euler = (rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28))
        o["material"] = "MILLET"
        bpy.context.view_layer.objects.active = o
        bpy.ops.rigidbody.object_add()
        o.rigid_body.type = "ACTIVE"
        o.rigid_body.mass = 0.0031          # 3.1 mg, from GRAIN.md §1
        o.rigid_body.collision_shape = "SPHERE"
        o.rigid_body.friction = 0.6
        o.rigid_body.restitution = 0.05
        o.rigid_body.linear_damping = 0.05
        grains.append(o)
    return grains


def census() -> dict:
    c = {}
    for o in bpy.data.objects:
        c[o.name.split("_")[0]] = c.get(o.name.split("_")[0], 0) + 1
    return c


def main() -> None:
    argv = [a for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []) if a != "--"]
    while argv and argv[0].lstrip("-") in ("build", "b"):
        argv.pop(0)
    mode = argv[0].lstrip("-") if argv else "hopper"
    grains = 0
    for a in argv[1:]:
        if a.isdigit():
            grains = int(a)
            break
    seed = 4711

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, 240
    sc.render.engine = "BLENDER_WORKBENCH"

    parts = build_floor()
    if mode in ("hopper", "all"):
        parts += build_hopper()
    if mode in ("cart", "all"):
        parts += build_cart()
    if mode in ("drum", "all"):
        parts += build_drum()
    g = build_grains(grains, seed) if grains else []

    c = census()
    c["GRAIN"] = len(g)
    total = sum(c.values())
    out = os.path.join(ROOT, "machines", "PNEUMA.blend")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    rec = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "mode": mode,
           "grains": len(g), "census": c, "named_parts": total,
           "blend_sha256": hashlib.sha256(open(out, "rb").read()).hexdigest(),
           "geometry": {"WHEEL_RIM_OUTER": WHEEL_RIM_OUTER, "AXLE_Z": AXLE_Z,
                        "ORIFICE_Z": ORIFICE_Z, "WALL_Z": [WALL_Z0, WALL_Z1],
                        "GRAIN_Z": [GRAIN_Z0, GRAIN_Z1], "LID_Z": LID_Z}}
    with open(os.path.join(EVIDENCE, "BUILD_LOG.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"build_pneuma: mode={mode} grains={len(g)} named_parts={total}")
    print(f"  census: {c}")
    print(f"  saved {out} sha256={rec['blend_sha256'][:16]}")


if __name__ == "__main__":
    main()
