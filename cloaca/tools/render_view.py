#!/usr/bin/env python3
"""Proof renders (R2: proofs before finals) at 1024 px from a built chunk.

Light law: gas, fire and daylight, and nothing else. A gas flame is emitted with a POINT primitive
because that is the only small-source emitter Blender has; the ledger row declares the period-true
source in `light_sources` and the primitive that stands for it in `primitives`, so no reader has to
guess which is which. No denoiser is available in this build, so denoising stays off and the sample
count carries the noise.

Water law: the water plane sits at the depth in that chunk's HYDRAULICS row. It is not placed by eye.
"""
import bpy, bmesh, sys, os, json, math, hashlib, time, resource, datetime
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d

CHUNK   = arg("--chunk", "S0000")
VIEW    = arg("--view", "gaslight_interior")
OUT     = arg("--out")
WIDTH   = int(arg("--width", 1024))
HEIGHT  = int(arg("--height", 576))
SAMPLES = int(arg("--samples", 48))
LANE    = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def jload(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d

def hyd_row(chunk):
    with open(os.path.join(LANE, "ledgers/HYDRAULICS.jsonl")) as f:
        for l in f:
            r = json.loads(l)
            if r["chunk"] == chunk: return r
    return {}

def idx_row(chunk):
    with open(os.path.join(LANE, "ledgers/INDEX.jsonl")) as f:
        for l in f:
            r = json.loads(l)
            if r["chunk"] == chunk: return r
    return {}

HYD = hyd_row(CHUNK); IDX = idx_row(CHUNK)
DEPTH = float(HYD.get("depth_m", 0.0))

# ---------------------------------------------------------------- views -------------------------
VIEWS = {
  "gaslight_interior": dict(cls="sewer_interior",
     cam=(30.0, 0.0, 1.45), rot=(math.radians(88), 0.0, math.radians(-90)), lens=24,
     lights=[dict(kind="gas", pos=(38.0, 0.60, 2.05), power=150.0, colour=(1.0, 0.70, 0.38), radius=0.045,
                  name="gas flame in a wall lantern", primitive="POINT"),
             dict(kind="gas", pos=(64.0, -0.60, 2.05), power=150.0, colour=(1.0, 0.69, 0.36), radius=0.045,
                  name="gas flame in a wall lantern", primitive="POINT")],
     world=0.0015, water=True,
     note="camera at 30 m chainage, 1.45 m above the invert, looking downstream; one wall lantern"),
  "water_flow": dict(cls="water_flow",
     cam=(62.0, 0.0, 1.60), rot=(math.radians(68), 0.0, math.radians(-90)), lens=28,
     lights=[dict(kind="gas", pos=(66.0, -0.55, 2.10), power=150.0, colour=(1.0, 0.71, 0.40), radius=0.045,
                  name="gas flame in a wall lantern", primitive="POINT")],
     world=0.0006, water=True,
     note="camera tipped down onto the flow; the plane sits at the ledger depth for this chunk"),
  "brick_macro": dict(cls="brick_macro",
     cam=(44.0, -0.10, 1.25), rot=(math.radians(90), 0.0, math.radians(180)), lens=35,
     lights=[dict(kind="gas", pos=(44.15, -0.28, 1.60), power=18.0, colour=(1.0, 0.72, 0.42), radius=0.035,
                  name="gas flame held in a lantern at the wall", primitive="POINT")],
     world=0.0004, water=False,
     note="camera square onto the inner wythe at 44 m, 550 mm off the face, lantern raking across the "
          "bond so the joints cast shadow; the module, the stagger and the wear are the subject"),
  "wear_macro": dict(cls="brick_macro",
     cam=(52.0, 0.20, 1.30), rot=(math.radians(58), 0.0, math.radians(180)), lens=35,
     lights=[dict(kind="gas", pos=(52.3, 0.05, 1.80), power=30.0, colour=(1.0, 0.72, 0.42), radius=0.035,
                  name="gas flame held in a lantern at the wall", primitive="POINT")],
     world=0.0004, water=True,
     note="camera at 52 m looking down the inner wythe from 850 mm: the waterline at the ledger depth "
          "cuts the frame, flow-zone darkening and sediment below it, splash staining above"),
  "daylight_shaft": dict(cls="sewer_interior",
     cam=(80.0, 0.0, 1.30), rot=(math.radians(96), 0.0, math.radians(-90)), lens=26,
     lights=[dict(kind="daylight", pos=(88.0, 0.0, 2.60), power=150.0, colour=(0.86, 0.90, 1.0), radius=0.30,
                  name="daylight down an open shaft", primitive="POINT")],
     world=0.008, water=True,
     note="overcast daylight entering a shaft at 84 m; no artificial source in frame"),
}
V = VIEWS[VIEW]

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = False            # no OpenImageDenoise in this build
scene.cycles.max_bounces = 8
scene.cycles.transparent_max_bounces = 4
scene.render.resolution_x = WIDTH
scene.render.resolution_y = HEIGHT
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.film_transparent = False
scene.view_settings.view_transform = "Filmic"      # AgX bleaches a gas flame to grey and clips walls
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0.0

# ---------------------------------------------------------------- world -------------------------
w = scene.world or bpy.data.worlds.new("world"); scene.world = w
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.30, 0.34, 0.42, 1.0)
bg.inputs[1].default_value = V["world"]

# ---------------------------------------------------------------- water -------------------------
water_sha = None
if V["water"] and DEPTH > 0:
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    for v in bm.verts:
        # wide enough to intersect the inner wythe at the flow depth, so the waterline is drawn on
        # the brickwork where it would be; hw(0.833 m) is 0.673 m for the canonical ovoid
        v.co = Vector((v.co.x * 100.0, v.co.y * 1.40, DEPTH))     # 100 m of length, 1.40 m of width
    me = bpy.data.meshes.new(f"WATER_{CHUNK}_{VIEW}"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(me.name, me); scene.collection.objects.link(ob)
    ob.location = (50.0, 0.0, 0.0)
    mat = bpy.data.materials.new("sewage"); mat.use_nodes = True
    nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.085, 0.095, 0.062, 1.0)
    bs.inputs["Roughness"].default_value = 0.04
    bs.inputs["IOR"].default_value = 1.333
    bs.inputs["Metallic"].default_value = 0.0
    # an opaque sheet puts everything under the waterline in shadow (the first wear proof came out
    # black for exactly that reason): sewage is dark but it transmits
    if "Transmission Weight" in bs.inputs: bs.inputs["Transmission Weight"].default_value = 1.0
    if "Specular IOR Level" in bs.inputs: bs.inputs["Specular IOR Level"].default_value = 0.6
    ob.data.materials.append(mat)
    water_sha = f"{DEPTH:.4f}"

def inner_half_width(z, r=0.675):
    """The ovoid's inner half-width at height z: lower semicircle below the springing, half-ellipse
    above. A lamp must hang in the void, not in the brickwork (the first proofs were black because
    two lanterns were buried 10 cm inside the inner wythe)."""
    if z <= r: return math.sqrt(max(r * r - (z - r) ** 2, 0.0))
    return r * math.sqrt(max(1.0 - ((z - r) / (3.0 * r)) ** 2, 0.0))

def place(pos):
    x, y, z = pos
    hw = inner_half_width(z)
    if abs(y) > hw - 0.08:
        y = (hw - 0.10) * (1.0 if y >= 0 else -1.0)
    return (x, y, z)

# ---------------------------------------------------------------- lights ------------------------
prims = []
for L in V["lights"]:
    li = bpy.data.lights.new(f"L_{L['name'][:18]}", type=L["primitive"])
    li.energy = L["power"]; li.color = L["colour"]; li.shadow_soft_size = L["radius"]
    li.use_shadow = True
    ob = bpy.data.objects.new(li.name, li); scene.collection.objects.link(ob)
    L["pos"] = place(L["pos"])
    ob.location = Vector(L["pos"]); ob.data = li
    prims.append({"primitive": L["primitive"], "power_w": L["power"], "colour": list(L["colour"]),
                  "at_m": list(L["pos"]), "represents": L["name"]})
    if L["kind"] == "gas":                     # lantern body and a flame cone, so the source reads
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        me = bpy.data.meshes.new("lantern_body"); bm.to_mesh(me); bm.free()
        lb = bpy.data.objects.new("lantern_body", me); scene.collection.objects.link(lb)
        lb.location = Vector(L["pos"]) + Vector((0, 0, 0.12)); lb.scale = (0.09, 0.09, 0.16)
        iron = bpy.data.materials.new("lantern_iron"); iron.use_nodes = True
        iron.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.045, 0.040, 0.035, 1)
        iron.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.62
        lb.data.materials.append(iron)
        # bmesh.ops.create_cone's keyword set differs in this build; the operator is stable, so use it
        # and re-parent the result into the scene collection we are working in.
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.025, radius2=0.0, depth=0.11,
                                        location=Vector(L["pos"]), enter_editmode=False)
        fl = bpy.context.active_object; fl.name = "flame"
        fm = bpy.data.materials.new("flame"); fm.use_nodes = True
        nt = fm.node_tree                                   # a new material has no Emission node: add one
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs[0].default_value = (1.0, 0.62, 0.24, 1.0); e.inputs[1].default_value = 26.0
        nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
        fl.data.materials.append(fm)
        prims.append({"primitive": "flame mesh, emission 26 W", "represents": "the gas flame itself"})

# ---------------------------------------------------------------- camera ------------------------
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = V["lens"]; cam_d.sensor_width = 36.0
cam_d.clip_start = 0.02; cam_d.clip_end = 400.0
cam = bpy.data.objects.new("cam", cam_d); scene.collection.objects.link(cam)
cam.location = Vector(V["cam"]); cam.rotation_euler = Euler(V["rot"], "XYZ")
scene.camera = cam

# ---------------------------------------------------------------- render ------------------------
OUT = OUT or os.path.join(LANE, "renders/proofs", f"{CHUNK}_{VIEW}_{WIDTH}.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
scene.render.filepath = OUT
t0 = time.time()
bpy.ops.render.render(write_still=True)
dt = time.time() - t0
peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
row = {"id": f"PF-{CHUNK}-{VIEW}", "class": V["cls"], "kind": "proof", "chunk": CHUNK,
       "view": VIEW, "width": WIDTH, "height": HEIGHT, "samples": SAMPLES,
       "engine": "CYCLES CPU", "denoising": False,
       "light_sources": [L["name"] for L in V["lights"]], "primitives": prims,
       "hydraulics_row": {"chunk": CHUNK, "depth_m": DEPTH,
                          "water_surface_m": HYD.get("water_surface_m"), "invert_in_m": HYD.get("invert_in_m"),
                          "self_cleansing": HYD.get("self_cleansing"), "discharge_m3_per_s": HYD.get("discharge_m3_per_s")},
       "water_plane_at_ledger_depth_m": DEPTH if V["water"] else None,
       "index_key": IDX.get("key"), "generator_version": IDX.get("generator_version"),
       "file": os.path.relpath(OUT, LANE), "sha256": h, "bytes": os.path.getsize(OUT),
       "render_s": round(dt, 2), "peak_mb": round(peak, 1), "camera": {"at_m": list(V["cam"]),
       "lens_mm": V["lens"], "euler_deg": [round(math.degrees(a), 2) for a in V["rot"]]},
       "note": V["note"], "upscaled": False,
       "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
# C-017: the register upserts by id; superseded renders keep their sha256, time and reason in-row
reg = os.path.join(LANE, "evidence/RENDERS.jsonl")
old = []
if os.path.exists(reg):
    for l in open(reg):
        l = l.strip()
        if not l: continue
        r = json.loads(l)
        if r.get("id") == row["id"]: old.append(r)
if old:
    row["superseded"] = old[0].get("superseded", []) + [
        {"sha256": o["sha256"], "render_s": o["render_s"], "t": o["t"],
         "reason": "re-rendered: " + row.get("note", "")[:80]} for o in old]
kept = []
if os.path.exists(reg):
    for l in open(reg):
        l = l.strip()
        if l and json.loads(l).get("id") != row["id"]: kept.append(l)
kept.append(json.dumps(row, sort_keys=True))
with open(reg, "w") as f:
    f.write("\n".join(kept) + "\n")
print(json.dumps({"rendered": row["file"], "sha256": h[:16], "render_s": row["render_s"],
                  "peak_mb": row["peak_mb"], "depth_m": DEPTH, "class": V["cls"], "bytes": row["bytes"]}))
