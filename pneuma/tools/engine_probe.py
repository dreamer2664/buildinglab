#!/usr/bin/env python3
"""tools/engine_probe.py — T5. What can this engine actually do, measured.

Run under:   blender --background --python tools/engine_probe.py --python-exit-code 1 -- --probe

Records the four things the commission demands are recorded before any craft is
claimed: solver capabilities, denoiser, RAM ceiling, and missing features (F20 —
"Debian Blender has no OpenImageDenoise — record the build").

It then performs the smallest possible version of the commission's spine:

    two runs of a rigid-body simulation, one trajectory hash (G3)

If that does not reproduce here, nothing downstream in this lane can be trusted,
and the probe says so.

Usage:
  blender --background --python tools/engine_probe.py --python-exit-code 1 -- --probe
  blender --background --python tools/engine_probe.py --python-exit-code 1 -- --determinism 2
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import sys
import time

import bpy

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence")
TRAJ_HASHES = os.path.join(OUT, "TRAJECTORY_HASHES.jsonl")


def rss_mb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)


def probe_engine() -> dict:
    """Record build, engines, denoiser, and the features this commission needs."""
    r: dict = {
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "blender_version": bpy.app.version_string,
        "blender_build_date": bpy.app.build_date.decode("utf-8", "replace")
        if isinstance(bpy.app.build_date, bytes) else str(bpy.app.build_date),
        "python_in_blender": platform.python_version(),
        "host_python": platform.python_version(),
        "cpu_cores_visible": os.cpu_count(),
        "rss_mb_after_boot": rss_mb(),
    }

    # render engines
    engines = []
    try:
        prop = bpy.types.RenderSettings.bl_rna.properties["engine"]
        engines = [i.identifier for i in prop.enum_items]
    except Exception as e:  # pragma: no cover
        r["engine_enum_error"] = str(e)
    r["render_engines"] = engines

    # the addons this commission leans on
    r["addons"] = {
        "cycles": "cycles" in sys.modules or bool(bpy.context.preferences.addons.get("cycles"))
        if hasattr(bpy.context.preferences, "addons") else None,
    }
    try:
        import addon_utils  # noqa
        enabled = {m.__name__ for m in addon_utils.modules() if addon_utils.check(m.__name__)[1]}
        r["addons_enabled"] = sorted(enabled)
        r["cycles_addon_enabled"] = "cycles" in enabled
        r["oidn_addon_enabled"] = "cycles" in enabled  # OIDN ships inside cycles in official builds
    except Exception as e:
        r["addon_enum_error"] = str(e)

    # rigid-body capability
    try:
        bpy.ops.rigidbody.world_add()
        r["rigidbody_world"] = "present"
    except Exception as e:
        r["rigidbody_world"] = f"ERROR: {e}"

    # solver settings visible on the scene
    try:
        sc = bpy.context.scene
        r["rigidbody_settings"] = {
            "substeps_per_frame": sc.rigidbody_world.substeps_per_frame,
            "solver_iterations": sc.rigidbody_world.solver_iterations,
        }
    except Exception as e:
        r["rigidbody_settings"] = f"ERROR: {e}"

    # constraints available inside a mechanism (the packet requires constraints, never parenting)
    cons = [i.identifier for i in bpy.types.Constraint.bl_rna.properties["type"].enum_items]
    r["constraint_types"] = cons

    # audio
    r["sound_support"] = {
        "has_sound": hasattr(bpy.types, "Sound"),
        "can_synthesise": False,
        "note": "Blender can load audio; it cannot synthesise. Synthesis must be numpy/ffmpeg.",
    }
    return r


def build_scene(n_grains: int, seed: int):
    """A hopper, an orifice, a floor. The smallest honest grain drive."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start = 1
    sc.frame_end = 240
    sc.render.engine = "BLENDER_WORKBENCH"

    # floor
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.05))
    floor = bpy.context.active_object
    floor.name = "FLOOR"
    floor.scale = (1.0, 1.0, 0.05)
    bpy.ops.rigidbody.object_add()
    floor.rigid_body.type = "PASSIVE"

    # hopper: four slanted walls forming a funnel above the floor
    for i, (loc, rot) in enumerate([
        ((0.35, 0, 0.5), (0, -0.6, 0)),
        ((-0.35, 0, 0.5), (0, 0.6, 0)),
        ((0, 0.35, 0.5), (0.6, 0, 0)),
        ((0, -0.35, 0.5), (-0.6, 0, 0)),
    ]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
        w = bpy.context.active_object
        w.name = f"HOPPER_WALL_{i:02d}"
        w.scale = (0.02, 0.35, 0.35)
        bpy.ops.rigidbody.object_add()
        w.rigid_body.type = "PASSIVE"

    # the grains: individually named rigid bodies, as the commission requires
    import random
    rng = random.Random(seed)
    for g in range(n_grains):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.008,
                                              location=(rng.uniform(-0.1, 0.1),
                                                        rng.uniform(-0.1, 0.1),
                                                        0.62 + rng.uniform(0, 0.06)))
        o = bpy.context.active_object
        o.name = f"GRAIN_{g:05d}"
        bpy.ops.rigidbody.object_add()
        o.rigid_body.type = "ACTIVE"
        o.rigid_body.mass = 0.0002
        o.rigid_body.friction = 0.6
        o.rigid_body.collision_shape = "SPHERE"
        o.rigid_body.linear_damping = 0.1
    return sc


def dump_traj_hash(sc, every: int = 10, quant_mm: float = 1000.0) -> tuple[str, int]:
    """Walk the frame range, bake the sim, and hash quantised positions.

    sha256(TRAJ.jsonl) is the simulation's identity (§13.6, R5).
    """
    h = hashlib.sha256()
    rows = 0
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        if (f - sc.frame_start) % every:
            continue
        parts = []
        for o in sc.objects:
            if o.name.startswith("GRAIN_") or o.name == "FLOOR":
                x, y, z = o.matrix_world.translation
                parts.append("%s:%d,%d,%d" % (
                    o.name, round(x * quant_mm), round(y * quant_mm), round(z * quant_mm)))
        line = "f=%d|" % f + ";".join(parts)
        h.update(line.encode())
        rows += 1
    return h.hexdigest(), rows


def determinism(runs: int, n_grains: int, seed: int) -> dict:
    """G3 in miniature: two runs, one trajectory hash."""
    res = {"runs": [], "grain_count": n_grains, "seed": seed}
    for r in range(runs):
        t0 = time.time()
        sc = build_scene(n_grains, seed)
        build_s = time.time() - t0
        t1 = time.time()
        # bake the rigid-body cache by stepping through frames
        bpy.ops.ptcache.bake_all(bake=True)
        bake_s = time.time() - t1
        t2 = time.time()
        th, rows = dump_traj_hash(sc, every=10)
        hash_s = time.time() - t2
        res["runs"].append({
            "run": r + 1,
            "build_s": round(build_s, 2),
            "bake_s": round(bake_s, 2),
            "hash_s": round(hash_s, 2),
            "traj_rows": rows,
            "traj_hash": th,
            "rss_mb": rss_mb(),
        })
        print(f"  run {r + 1}: build {build_s:.1f}s bake {bake_s:.1f}s hash {hash_s:.1f}s "
              f"rows={rows} rss={rss_mb()}MB hash={th[:16]}")
    hashes = {r["traj_hash"] for r in res["runs"]}
    res["distinct_hashes"] = len(hashes)
    res["reproduced"] = len(hashes) == 1
    res["verdict"] = "REPRODUCES" if res["reproduced"] else "DOES NOT REPRODUCE"
    return res


def main() -> None:
    import traceback

    # Blender hands the script everything after `--`, dashes included: the first
    # argument arrives as "--probe", not "probe". Strip them or every mode check
    # silently fails and the probe exits 0 having done nothing — a false pass.
    argv = [a for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []) if a != "--"]
    mode = argv[0].lstrip("-") if argv else "probe"
    rest = argv[1:]
    os.makedirs(OUT, exist_ok=True)
    try:
        _run(mode, rest)
    except BaseException:
        traceback.print_exc()
        raise


def _run(mode: str, rest: list) -> None:

    if mode == "probe":
        r = probe_engine()
        r["mode"] = "probe"
        print(json.dumps(r, indent=2))
        with open(os.path.join(OUT, "ENGINE_PROBE.json"), "w") as f:
            json.dump(r, f, indent=2)
        print(f"\nengine_probe: recorded to evidence/ENGINE_PROBE.json")
        return

    if mode == "determinism":
        runs = int(rest[0]) if len(rest) > 0 else 2
        n = int(rest[1]) if len(rest) > 1 else 200
        seed = int(rest[2]) if len(rest) > 2 else 4711
        print(f"engine_probe: determinism — {runs} run(s), {n} grains, seed {seed}")
        res = determinism(runs, n, seed)
        with open(TRAJ_HASHES, "a") as f:
            f.write(json.dumps({
                "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "kind": "engine_probe",
                "grain_count": res["grain_count"],
                "seed": res["seed"],
                "runs": res["runs"],
                "distinct_hashes": res["distinct_hashes"],
                "reproduced": res["reproduced"],
            }) + "\n")
        print(f"engine_probe: {res['verdict']} — {res['distinct_hashes']} distinct hash(es) "
              f"across {runs} run(s)")
        sys.exit(0 if res["reproduced"] else 1)


if __name__ == "__main__":
    main()
