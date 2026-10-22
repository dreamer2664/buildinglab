#!/usr/bin/env python3
"""Prepare one open-source human scan for the figures blend (C-023).

usage: bl.sh --python tools/scan_prepare.py -- --scan <scan_id> [--hero-tris 60000] [--bg-tris 8000]

Per source GLB, in its own Blender session (2 GB doctrine):
  import -> join -> dissolve loose debris -> merge by distance
  -> normalise: feet on z=0, standing height to the ledger target, centred on the origin
  -> period palette: skin and hair kept but calmed, clothing pushed toward the fustian /
     moleskin / wool / linen family, no metal, no emission, rough surfaces only (G8)
  -> decimate to two variants: hero (<=60k tris) and bg (<=8k tris)
  -> export people/scan_lib/<id>_hero.glb and _bg.glb
Writes its sidecar row into evidence/SCAN_LIB.json (upsert by scan_id).
Deterministic: same input file, same outputs; the source sha256 is carried in the sidecar.
"""
import bpy, bmesh, os, sys, json, math, hashlib, datetime

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
SCAN = arg("--scan")
if not SCAN:
    print("need --scan"); sys.exit(1)
HERO = int(arg("--hero-tris", 60000)); BG = int(arg("--bg-tris", 8000))
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(LANE, "people/scans", SCAN + ".glb")
LIB  = os.path.join(LANE, "people/scan_lib")
os.makedirs(LIB, exist_ok=True)

CHILD = "child" in SCAN
FEMALE = any(t in SCAN for t in ("woman", "female", "amara", "mei", "maya"))
TARGET_H = 1.25 if CHILD else (1.64 if FEMALE else 1.72)

# period palette targets (linear-ish sRGB triples): fustian brown-grey, moleskin tan,
# wool charcoal, linen off-white, leather boot brown
CLOTH_COLORS = [(0.32, 0.28, 0.23), (0.45, 0.38, 0.27), (0.16, 0.15, 0.14),
                (0.72, 0.68, 0.60), (0.22, 0.14, 0.09)]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

meshes = [o for o in bpy.data.objects if o.type == "MESH"]
if not meshes:
    print("no mesh in", SRC); sys.exit(1)
# join everything into one body mesh; keep the armature out (static figures only)
ctx_obj = max(meshes, key=lambda o: len(o.data.vertices))
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = ctx_obj
if len(meshes) > 1:
    bpy.ops.object.join()
body = ctx_obj
for o in list(bpy.data.objects):
    if o.type in ("ARMATURE", "EMPTY", "CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)

# cleanup: loose debris and coincident vertices
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="DESELECT")
bpy.ops.mesh.select_loose(extend=True)
bpy.ops.mesh.delete(type="VERT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0005)
bpy.ops.object.mode_set(mode="OBJECT")

me = body.data
tris = sum(len(p.vertices) - 2 for p in me.polygons)

# ---- palette pass (before decimation so material slots survive) ----
def bsdf(mat):
    if not mat.use_nodes: return None
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED": return n
    return None

def luminance(c): return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

palette_log = []
h = int(hashlib.sha256(SCAN.encode()).hexdigest()[:8], 16)
for i, mat in enumerate(bpy.data.materials):
    n = bsdf(mat)
    if n is None: continue
    base = list(n.inputs["Base Color"].default_value)
    name = (mat.name or "").lower()
    lum = luminance(base[:3])
    sat = max(base[:3]) - min(base[:3])
    kind = "cloth"
    if any(t in name for t in ("skin", "body", "head", "hand", "face", "ear", "neck")):
        kind = "skin"
    elif any(t in name for t in ("hair", "brow", "lash", "beard")):
        kind = "hair"
    elif any(t in name for t in ("eye", "teeth", "tongue", "mouth")):
        kind = "eye"
    if kind == "skin":
        n.inputs["Roughness"].default_value = 0.62
        if "Specular IOR Level" in n.inputs: n.inputs["Specular IOR Level"].default_value = 0.3
    elif kind == "hair":
        n.inputs["Base Color"].default_value = (0.09 + (h % 7) * 0.012, 0.06 + (h % 5) * 0.010,
                                                0.04 + (h % 3) * 0.008, 1.0)
        n.inputs["Roughness"].default_value = 0.78
    elif kind == "eye":
        n.inputs["Roughness"].default_value = 0.25
    else:  # cloth: assign a deterministic period colour; abstract-white bodies are canvases
        c = CLOTH_COLORS[(h + i) % len(CLOTH_COLORS)]
        if "foot" in name or "shoe" in name or "boot" in name: c = CLOTH_COLORS[4]
        n.inputs["Base Color"].default_value = (*c, 1.0)
        n.inputs["Roughness"].default_value = 0.82
        if "Metallic" in n.inputs: n.inputs["Metallic"].default_value = 0.0
    if "Emission Strength" in n.inputs:
        n.inputs["Emission Strength"].default_value = 0.0
    palette_log.append({"material": mat.name, "kind": kind})

# ---- normalise: feet on z=0, height TARGET_H, centred ----
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bb = [body.matrix_world @ mathutils.Vector(c) for c in body.bound_box] if False else None
import mathutils
bb = [body.matrix_world @ mathutils.Vector(c) for c in body.bound_box]
zmin = min(v.z for v in bb); zmax = max(v.z for v in bb)
xmin = min(v.x for v in bb); xmax = max(v.x for v in bb)
ymin = min(v.y for v in bb); ymax = max(v.y for v in bb)
height = zmax - zmin
s = TARGET_H / height if height > 1e-6 else 1.0
body.scale = (s, s, s)
bpy.ops.object.transform_apply(scale=True)
bb = [body.matrix_world @ mathutils.Vector(c) for c in body.bound_box]
cx = (min(v.x for v in bb) + max(v.x for v in bb)) / 2
cy = (min(v.y for v in bb) + max(v.y for v in bb)) / 2
cz = min(v.z for v in bb)
body.location = (-cx, -cy, -cz)
bpy.ops.object.transform_apply(location=True)

def make_variant(tag, tri_budget):
    vname = f"{SCAN}_{tag}"
    bpy.ops.object.select_all(action="DESELECT")
    dup = body.copy(); dup.data = body.data.copy(); dup.name = vname
    bpy.context.collection.objects.link(dup)
    bpy.context.view_layer.objects.active = dup; dup.select_set(True)
    # decimate refuses meshes carrying shape keys; the figures are static, drop them
    while dup.data.shape_keys and dup.data.shape_keys.key_blocks:
        kb = dup.data.shape_keys.key_blocks[-1]
        if kb.name == "Basis":
            bpy.ops.object.shape_key_remove(all=True)
        else:
            dup.shape_key_remove(kb)
    cur = sum(len(p.vertices) - 2 for p in dup.data.polygons)
    if cur > tri_budget:
        bpy.ops.object.modifier_add(type="DECIMATE")
        m = dup.modifiers[-1]; m.ratio = max(0.005, tri_budget / cur)
        bpy.ops.object.modifier_apply(modifier=m.name)
    final = sum(len(p.vertices) - 2 for p in dup.data.polygons)
    out = os.path.join(LIB, vname + ".glb")
    bpy.ops.object.select_all(action="DESELECT")
    dup.select_set(True); bpy.context.view_layer.objects.active = dup
    bpy.ops.export_scene.gltf(filepath=out, use_selection=True, export_materials="EXPORT")
    bpy.data.objects.remove(dup, do_unlink=True)
    return final, os.path.getsize(out), hashlib.sha256(open(out, "rb").read()).hexdigest()

hero_t, hero_b, hero_h = make_variant("hero", HERO)
bg_t, bg_b, bg_h = make_variant("bg", BG)

row = {"scan_id": SCAN, "source_file": os.path.basename(SRC),
       "source_sha256": hashlib.sha256(open(SRC, "rb").read()).hexdigest(),
       "imported_tris": tris, "height_m": TARGET_H, "class": "child" if CHILD else ("female" if FEMALE else "male"),
       "hero": {"tris": hero_t, "bytes": hero_b, "sha256": hero_h, "file": f"people/scan_lib/{SCAN}_hero.glb"},
       "bg":   {"tris": bg_t, "bytes": bg_b, "sha256": bg_h, "file": f"people/scan_lib/{SCAN}_bg.glb"},
       "materials": palette_log,
       "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

libp = os.path.join(LANE, "evidence/SCAN_LIB.json")
lib = {}
if os.path.exists(libp):
    lib = json.load(open(libp))
lib[SCAN] = row
with open(libp, "w") as f:
    json.dump(lib, f, indent=1, sort_keys=True)
print(json.dumps({"scan_id": SCAN, "imported_tris": tris, "hero_tris": hero_t, "bg_tris": bg_t,
                  "hero_bytes": hero_b, "bg_bytes": bg_b}))
