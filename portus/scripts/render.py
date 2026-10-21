#!/usr/bin/env python3
"""render.py — proof/final render queue with an R1 content-hash cache.

    blender45 -b portus/source/PORTUS.blend --python-exit-code 1 \
        --python portus/scripts/render.py -- --class proofs --res 1024 --samples 32

View key = sha256(content hash | light fingerprint | camera name | camera
matrix | lens | resolution | samples). The content hash folds every mesh's
name, vertices and world matrix, every material input and every light — and
deliberately excludes camera transforms, so moving one camera re-renders one
view (DECISIONS D-0012). An unchanged key never re-renders.

Writes renders/<class>/<view>.png, renders/<class>/MANIFEST.json and appends
to renders/CACHE.json.

One Blender process at a time: this worker has 1.9 GiB and two renders
OOM-kill each other (observed, exit 137).
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "renders", "CACHE.json")


def sha256_file(p, chunk=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def content_hash():
    """Everything that decides a pixel except the cameras."""
    import bpy
    h = hashlib.sha256()
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type != "MESH" or o.name.startswith("CAM_"):
            continue
        me = o.data
        h.update(o.name.encode())
        h.update(",".join("%.5f" % v for row in o.matrix_world for v in row).encode())
        co = array.array("f", [0.0]) * (len(me.vertices) * 3)
        if len(me.vertices):
            me.vertices.foreach_get("co", co)
        h.update(co.tobytes())
        h.update(("%d:%d" % (len(me.vertices), len(me.polygons))).encode())
        for slot in o.material_slots:
            h.update((slot.material.name if slot.material else "-").encode())
    for mat in sorted(bpy.data.materials, key=lambda x: x.name):
        h.update(mat.name.encode())
        if not mat.use_nodes:
            h.update(("%.4f:%.4f" % (mat.diffuse_color[0], mat.roughness)).encode())
            continue
        for n in sorted(mat.node_tree.nodes, key=lambda x: x.name):
            h.update((n.name + ":" + n.bl_idname).encode())
            for inp in n.inputs:
                if hasattr(inp, "default_value"):
                    try:
                        v = inp.default_value
                        if hasattr(v, "__len__"):
                            h.update(",".join("%.4f" % x for x in v).encode())
                        else:
                            h.update(("%.4f" % v).encode())
                    except Exception:                     # noqa: BLE001
                        pass
    return h.hexdigest()[:24]


def lighting_fingerprint(scene):
    import bpy
    parts = []
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type == "LIGHT":
            li = o.data
            parts.append(f"{o.name}:{li.type}:{li.energy:.4f}:"
                         f"{tuple(round(c, 4) for c in li.color)}")
    w = scene.world
    if w and w.use_nodes:
        bg = w.node_tree.nodes.get("Background")
        if bg:
            parts.append(f"world:{tuple(round(c, 4) for c in bg.inputs[0].default_value)}:"
                         f"{bg.inputs[1].default_value:.4f}")
    parts.append(f"exposure:{scene.view_settings.exposure:.4f}")
    parts.append(f"look:{scene.view_settings.look}")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", default="proofs")
    ap.add_argument("--res", type=int, default=1024)
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--only", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    import bpy
    sc = bpy.context.scene
    native = bpy.data.filepath
    native_sha = sha256_file(native)
    content = content_hash()
    light = lighting_fingerprint(sc)
    print(f"CONTENT {content}  LIGHT {light}  NATIVE {native_sha[:12]}", flush=True)

    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    outdir = os.path.join(ROOT, "renders", args.cls)
    os.makedirs(outdir, exist_ok=True)
    mpath = os.path.join(outdir, "MANIFEST.json")
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}

    cams = sorted([o for o in bpy.data.objects if o.type == "CAMERA"], key=lambda o: o.name)
    if args.only:
        want = [w.strip() for w in args.only.split(",") if w.strip()]
        cams = [c for c in cams if any(w in c.name for w in want)]
    if args.limit:
        cams = cams[:args.limit]

    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.resolution_percentage = 100
    sc.cycles.device = "CPU"
    try:
        import _cycles
        has_oidn = bool(_cycles.with_openimagedenoise)
    except Exception:                                        # noqa: BLE001
        has_oidn = False
    sc.cycles.use_denoising = has_oidn
    if has_oidn:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
        sc.cycles.denoising_use_gpu = False
    sc.cycles.samples = args.samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 2
    sc.cycles.debug_use_spatial_splits = False
    sc.render.use_persistent_data = True

    done = skipped = 0
    failed = []
    t_all = time.time()
    for cam in cams:
        sc.render.resolution_x = args.res
        sc.render.resolution_y = int(round(args.res * 9 / 16))
        sc.camera = cam
        m = cam.matrix_world
        key_src = (f"{content}|{light}|{cam.name}|{cam.data.lens:.4f}|"
                   f"{[round(v, 5) for row in m for v in row]}|{args.res}|{args.samples}")
        key = hashlib.sha256(key_src.encode()).hexdigest()
        fname = f"{cam.name}.png"
        path = os.path.join(outdir, fname)
        if not args.force and cache.get(key) == path and os.path.exists(path):
            skipped += 1
            manifest[cam.name] = dict(file=fname, key=key, cached=True,
                                      sha256=sha256_file(path), bytes=os.path.getsize(path),
                                      px=[args.res, sc.render.resolution_y],
                                      content=content, light=light, native_sha256=native_sha)
            print(f"CACHED {cam.name}", flush=True)
            continue
        sc.render.filepath = path
        t0 = time.time()
        try:
            bpy.ops.render.render(write_still=True)
        except Exception as e:                                # noqa: BLE001
            failed.append(f"{cam.name}: {e}")
            print(f"FAILED {cam.name}: {e}", flush=True)
            continue
        dt = time.time() - t0
        cache[key] = path
        manifest[cam.name] = dict(file=fname, key=key, cached=False, seconds=round(dt, 1),
                                  sha256=sha256_file(path), bytes=os.path.getsize(path),
                                  px=[args.res, sc.render.resolution_y],
                                  content=content, light=light, native_sha256=native_sha)
        json.dump(cache, open(CACHE, "w"), indent=1)
        json.dump(manifest, open(mpath, "w"), indent=1)
        done += 1
        print(f"RENDERED {cam.name} in {dt:.1f}s -> {fname}", flush=True)

    json.dump(cache, open(CACHE, "w"), indent=1)
    json.dump(manifest, open(mpath, "w"), indent=1)
    print(f"SUMMARY rendered {done} cached {skipped} failed {len(failed)} "
          f"in {time.time()-t_all:.0f}s content {content}", flush=True)
    for f in failed:
        print("  FAIL", f, flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
