#!/usr/bin/env python3
"""Prepare one open-source architectural scan for the station blends (C-024).

usage: bl.sh --python tools/building_scan_prepare.py -- --scan <scan_id>

Per source GLB, in its own Blender session: import -> join -> debris out -> rescale to the
surveyed real-world target (pump-hall columns 6 m, arcade arches 2.4 m span, chimney 24 m,
cornice/string-course/ridge runs kept at scanned length and tiled by the builder) -> put the
base on z=0 and the piece centred on the origin -> decimate to <=30k tris -> export to
stations/scan_lib_build/<id>.glb WITH its scanned PBR textures (the chimney and warehouse
carry real brick maps the station walls reuse). Sidecar row upserted into
evidence/BUILD_SCAN_LIB.json. Brick diffuse/normal images found in the source are also
written out as stations/scan_lib_build/tex_<id>_*.png for wall materials.
"""
import bpy, os, sys, json, math, hashlib, datetime

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
SCAN = arg("--scan")
if not SCAN: print("need --scan"); sys.exit(1)
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(LANE, "stations/scans", SCAN + ".glb")
LIB = os.path.join(LANE, "stations/scan_lib_build")
os.makedirs(LIB, exist_ok=True)

# surveyed targets: height in metres for upright pieces, span for arches, None = keep length
TARGET_H = {"arch_doric-column-original-exterior-model": 6.0,
            "arch_tuscan-column-original-exterior-model": 6.0,
            "arch_square-column-original-exterior-model": 5.0,
            "arch_pilaster-original-exterior-model": 5.0,
            "arch_keystone-arch-original-exterior-model": 3.2,
            "arch_brick-chimney-original-exterior-model": 24.0,
            "arch_window-surround-original-exterior-model": 3.0}
TRI_CAP = 30000

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
if not meshes: print("no mesh in", SRC); sys.exit(1)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
body = max(meshes, key=lambda o: len(o.data.vertices))
bpy.context.view_layer.objects.active = body
if len(meshes) > 1: bpy.ops.object.join()
for o in list(bpy.data.objects):
    if o.type in ("ARMATURE", "EMPTY", "CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)
    elif o.type == "MESH" and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
for m in list(body.modifiers): body.modifiers.remove(m)

# local-space extents (object.dimensions is stale pre-depsgraph; known trap)
mw = body.matrix_world
vs = [body.data.vertices[i].co for i in range(len(body.data.vertices))]
xs = [ (mw @ v).x for v in vs ]; ys = [ (mw @ v).y for v in vs ]; zs = [ (mw @ v).z for v in vs ]
dx, dy, dz = max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)
target = TARGET_H.get(SCAN)
if target:
    h = max(dx, dy, dz) if SCAN.endswith("keystone-arch-original-exterior-model") else dz
    s = target / h if h > 1e-6 else 1.0
else:
    s = 1.0
body.scale = (s, s, s)
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(scale=True)

# rebase: base plane on z=0, centred in x/y
mw = body.matrix_world
vs = [mw @ v.co for v in body.data.vertices]
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2
cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2
zmin = min(v.z for v in vs)
body.location = (-cx, -cy, -zmin)
bpy.ops.object.transform_apply(location=True)

tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
if tris > TRI_CAP:
    bpy.ops.object.modifier_add(type="DECIMATE")
    m = body.modifiers[-1]; m.ratio = TRI_CAP / tris
    bpy.ops.object.modifier_apply(modifier=m.name)
final_tris = sum(len(p.vertices) - 2 for p in body.data.polygons)

# write out the scanned brick/stone maps so wall materials can reuse them
tex_files = []
for img in bpy.data.images:
    if img.has_data and img.size[0] >= 512:
        low = (img.name or "").lower()
        if any(t in low for t in ("diff", "base", "col", "nor", "bump", "rough")) or len(tex_files) < 4:
            p = os.path.join(LIB, f"tex_{SCAN}_{len(tex_files)}.png")
            try:
                img.filepath_raw = p; img.file_format = "PNG"; img.save()
                tex_files.append(os.path.basename(p))
            except Exception:
                pass

out = os.path.join(LIB, SCAN + ".glb")
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.export_scene.gltf(filepath=out, use_selection=True, export_materials="EXPORT")

mw = body.matrix_world
vs = [mw @ v.co for v in body.data.vertices]
row = {"scan_id": SCAN, "source_file": os.path.basename(SRC),
       "source_sha256": hashlib.sha256(open(SRC, "rb").read()).hexdigest(),
       "imported_tris": tris, "tris": final_tris,
       "dims_m": [round(max(xs)-min(xs), 2), round(max(ys)-min(ys), 2), round(max(zs)-min(zs), 2)],
       "prepared_dims_m": [round(max(v.x for v in vs)-min(v.x for v in vs), 2),
                           round(max(v.y for v in vs)-min(v.y for v in vs), 2),
                           round(max(v.z for v in vs)-min(v.z for v in vs), 2)],
       "textures_written": tex_files, "bytes": os.path.getsize(out),
       "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest(),
       "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
libp = os.path.join(LANE, "evidence/BUILD_SCAN_LIB.json")
lib = json.load(open(libp)) if os.path.exists(libp) else {}
lib[SCAN] = row
json.dump(lib, open(libp, "w"), indent=1, sort_keys=True)
print(json.dumps({"scan_id": SCAN, "imported_tris": tris, "tris": final_tris,
                  "dims": row["prepared_dims_m"], "textures": len(tex_files)}))
