#!/usr/bin/env python3
"""Render the §24 view schedule at proof resolution (R2), resume-safe.

Each view row names its class, scene, camera, lights in period terms and the primitives standing
for them, and for interiors the hydraulics row the water plane sits at. The register upserts by id
(C-017), so a re-run replaces rather than doubles. Proofs are 1024x576 by design; finals at class
resolution follow where the BUDGET.md envelope allows.
"""
import bpy, sys, os, json, math, hashlib, time, resource, datetime, random
from mathutils import Vector, Euler
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
ITEM = json.loads(arg("--item"))
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene = bpy.context.scene
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"
scene.cycles.samples = ITEM.get("samples", 16); scene.cycles.use_denoising = False
scene.cycles.max_bounces = 6
scene.render.resolution_x = ITEM["width"]; scene.render.resolution_y = ITEM["height"]
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"
scene.view_settings.view_transform = "Filmic"; scene.view_settings.look = "Medium High Contrast"

def world(strength, col=(0.30, 0.34, 0.42)):
    w = scene.world or bpy.data.worlds.new("w"); scene.world = w; w.use_nodes = True
    b = w.node_tree.nodes["Background"]; b.inputs[0].default_value = (*col, 1.0); b.inputs[1].default_value = strength

def lamp(pos, power=150.0, colour=(1.0, 0.70, 0.38), radius=0.045, name="gas flame in a wall lantern", prim="POINT"):
    li = bpy.data.lights.new("L", type=prim); li.energy = power; li.color = colour; li.shadow_soft_size = radius
    ob = bpy.data.objects.new("L", li); scene.collection.objects.link(ob); ob.location = Vector(pos)
    return {"primitive": prim, "power_w": power, "at_m": list(pos), "represents": name}

def sun(name="overcast daylight"):
    li = bpy.data.lights.new("S", type="SUN"); li.energy = 2.2; li.color = (0.9, 0.92, 1.0)
    li.angle = math.radians(12)
    ob = bpy.data.objects.new("S", li); scene.collection.objects.link(ob)
    ob.rotation_euler = Euler((math.radians(50), 0, math.radians(140)))
    return {"primitive": "SUN", "energy_irr_w_m2": 2.2, "represents": name}

def cam(at, rot, lens):
    cd = bpy.data.cameras.new("cam"); cd.lens = lens; cd.clip_start = 0.02; cd.clip_end = 600
    ob = bpy.data.objects.new("cam", cd); scene.collection.objects.link(ob)
    ob.location = Vector(at); ob.rotation_euler = Euler([math.radians(a) for a in rot])
    scene.camera = ob

def look_at(at, target, lens):
    d = Vector(target) - Vector(at)
    rot = d.to_track_quat("-Z", "Y").to_euler()
    cam(at, [math.degrees(a) for a in rot], lens)

def hyd(chunk):
    with open(os.path.join(LANE, "ledgers/HYDRAULICS.jsonl")) as f:
        for l in f:
            r = json.loads(l)
            if r["chunk"] == chunk: return r
    return {}

def water(depth):
    if not depth: return None
    bm = None
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * 100.0, v.co.y * 1.40, depth))
    me = bpy.data.meshes.new("water"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("water", me); scene.collection.objects.link(ob); ob.location = (50, 0, 0)
    m = bpy.data.materials.new("sewage"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.085, 0.095, 0.062, 1)
    b.inputs["Roughness"].default_value = 0.04; b.inputs["IOR"].default_value = 1.333
    if "Transmission Weight" in b.inputs: b.inputs["Transmission Weight"].default_value = 1.0
    ob.data.materials.append(m)
    return ob

prims = []; hrow = None
kind = ITEM["recipe"]
if kind in ("interior", "water", "macro"):
    chunk = ITEM["scene"][6:]
    h = hyd(chunk); depth = h.get("depth_m", 0.8)
    hrow = {"chunk": chunk, "depth_m": depth, "water_surface_m": h.get("water_surface_m"),
            "invert_in_m": h.get("invert_in_m"), "self_cleansing": h.get("self_cleansing")}
    world(0.0015)
    if kind == "interior":
        cam((30, 0, 1.45), (88, 0, -90), 24); prims.append(lamp((38, 0.42, 1.80))); prims.append(lamp((64, -0.42, 1.80)))
        water(depth)
    elif kind == "water":
        cam((62, 0, 1.60), (68, 0, -90), 28); prims.append(lamp((66, -0.42, 1.80))); water(depth)
    else:
        cam((44, -0.10, 1.25), (90, 0, 180), 35); prims.append(lamp((44.15, -0.28, 1.60), 18.0))
elif kind == "overflow":
    world(0.03); prims.append(sun())
    k = ITEM["k"]
    cam((-8 + k * 2, 5 - k, 3.2 + k * 0.4), (66, 0, -55), 30)
elif kind in ("engine_closeup", "mechanism_detail", "iron_macro"):
    world(0.004)
    frag = {"engine_closeup": ["ROCKING-BEAM", "CYLINDER-BARREL", "FLYWHEEL-HUB", "PLUNGER-001"][ITEM["k"] % 4],
            "mechanism_detail": ["VALVE-CHEST", "CAM-", "GOVERNOR-BALL", "PARALLEL"][ITEM["k"] % 4],
            "iron_macro": ["CRANK-WEB", "RIM-SEGMENT", "TIE-BAR", "HANDRAIL"][ITEM["k"] % 4]}[kind]
    tgt = None
    for o in scene.objects:
        if frag in o.name.upper(): tgt = o; break
    if tgt is None: tgt = scene.objects[10]
    c = sum((tgt.matrix_world @ Vector(cn) for cn in tgt.bound_box), Vector()) / 8.0
    look_at((c.x + 2.2, c.y - 2.2, c.z + 1.4), (c.x, c.y, c.z), 45)
    prims.append(lamp((c.x + 1.0, c.y - 1.0, c.z + 1.6), 90.0))
elif kind in ("station_hero", "engine_house"):
    if kind == "station_hero":
        world(0.05); prims.append(sun())
        look_at((70, -60, 26), (0, 0, 8), 35)
    else:
        world(0.004)
        cam((0, 0, 6), (80, 0, -90), 24)
        for x in (-14, 0, 14): prims.append(lamp((x, 2, 7), 220.0))
elif kind in ("construction_yard", "centring_arch"):
    world(0.05); prims.append(sun())
    if kind == "construction_yard":
        look_at((26, 26, 10), (0, 4, 1), 35)
    else:
        look_at((ITEM["k"] * 4 - 26, 9, 3.4), (ITEM["k"] * 12 - 30, 0, 0.8), 32)
elif kind == "embankment_walk":
    world(0.045); prims.append(sun("low daylight over the river"))
    x = ITEM["k"] * 50 - 550
    look_at((x, 2, 5.4), (x + 60, -3, 5.0), 32)
elif kind == "lamppost":
    world(0.035); prims.append(sun("evening daylight"))
    x = ITEM["k"] * 100 - 500
    look_at((x + 3, -1.4, 4.6), (x, -3.6, 6.4), 50)
elif kind == "people":
    world(0.05); prims.append(sun())
    rng = random.Random(ITEM["k"])
    look_at((rng.uniform(-18, 18), rng.uniform(-14, 14), 2.2), (rng.uniform(-6, 6), rng.uniform(-6, 6), 1.3), 35)
elif kind == "aerial":
    world(0.06); prims.append(sun())
    look_at((ITEM["k"] * 30 - 200, 40, 90), (ITEM["k"] * 30 - 200, 0, 0), 30)
t0 = time.time()
out = os.path.join(LANE, "renders/proofs", ITEM["id"] + "_1024.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
dt = time.time() - t0
row = {"id": ITEM["id"], "class": ITEM.get("class", ITEM.get("cls")), "kind": "proof", "width": ITEM["width"],
       "height": ITEM["height"], "samples": scene.cycles.samples, "engine": "CYCLES CPU",
       "denoising": False, "scene": ITEM["scene"], "recipe": kind,
       "light_sources": sorted({p["represents"] for p in prims}), "primitives": prims,
       "hydraulics_row": hrow, "file": os.path.relpath(out, LANE),
       "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest(), "bytes": os.path.getsize(out),
       "render_s": round(dt, 2), "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
       "upscaled": False, "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
reg = os.path.join(LANE, "evidence/RENDERS.jsonl")
old = []
if os.path.exists(reg):
    for l in open(reg):
        l = l.strip()
        if l and json.loads(l).get("id") == row["id"]: old.append(json.loads(l))
if old:
    row["superseded"] = old[0].get("superseded", []) + [{"sha256": o["sha256"], "t": o["t"]} for o in old]
kept = []
if os.path.exists(reg):
    for l in open(reg):
        l = l.strip()
        if l and json.loads(l).get("id") != row["id"]: kept.append(l)
kept.append(json.dumps(row, sort_keys=True))
with open(reg, "w") as f: f.write("\n".join(kept) + "\n")
print(json.dumps({"id": row["id"], "render_s": row["render_s"], "bytes": row["bytes"]}))
