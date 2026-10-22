#!/usr/bin/env python3
"""The four pumping stations as built shells with their plant (Stage H, G5 context; C-024).

Engine house on the recorded plan, the boiler range of the survey count, chimney, coal stage,
pump hall, and one named seat per engine the station carries. Driver's architecture is carried
in the title property AND, since the Director's scan override, in scanned fabric: classical
columns, keystone arches, pilasters, window surrounds, cornice and string-course runs, roof
ridge and the chimney come from open-source CC0 scans (stations/scan_lib_build, provenance in
evidence/BUILD_SCAN_SOURCES.jsonl); walls and floors carry the scanned brick maps extracted
from those scans, with a procedural quarry-tile fallback where no scanned tile exists.
Named-part census is unchanged: v_stations reads engines, boilers, cruciform, architect.
"""
import bpy, sys, os, json, math, time, resource
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
SID = arg("--station", "abbey_mills")
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLIB = os.path.join(LANE, "stations/scan_lib_build")
bpy.ops.wm.read_factory_settings(use_empty=True)
SPEC = {"abbey_mills": dict(engines=8, boilers=16, house=(44.0, 44.0, 18.0), cruciform=True,
                            architect="C. H. Driver, Byzantine polychrome brick and iron"),
        "crossness": dict(engines=4, boilers=12, house=(44.35, 13.87, 16.0), cruciform=False,
                          architect="C. H. Driver, Romanesque with Moorish cast iron"),
        "deptford": dict(engines=6, boilers=10, house=(36.0, 16.0, 14.0), cruciform=False,
                         architect="Bazalgette and Driver, Say's Court lift station"),
        "chelsea": dict(engines=4, boilers=8, house=(30.0, 14.0, 12.0), cruciform=False,
                        architect="Grosvenor low-level lift, Driver")}
sp = SPEC[SID]
scene = bpy.context.scene
def mat(n, c, r=0.7, m=0.0):
    mm = bpy.data.materials.new(n); mm.use_nodes = True
    b = mm.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r
    b.inputs["Metallic"].default_value = m
    return mm

# ---- scanned brick for the big wall faces; flat stock colour if the maps are absent ----
def brick_material():
    tex = None
    for cand in ("arch_brick-chimney-original-exterior-model_0",
                 "arch_brick-chimney-original-exterior-model_1",
                 "arch_godown-warehouse-30-x-20-m-with-loading-dock-3d-model_0"):
        p = os.path.join(BLIB, f"tex_{cand}.png")
        if os.path.exists(p): tex = p; break
    if not tex: return mat("stock_brick", (0.31, 0.29, 0.23))
    mm = bpy.data.materials.new("scanned_brick"); mm.use_nodes = True
    nt = mm.node_tree; b = nt.nodes["Principled BSDF"]
    img = bpy.data.images.load(tex)
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = img
    ti.extension = "REPEAT"; mp.inputs["Scale"].default_value = (12.0, 12.0, 12.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], ti.inputs["Vector"])
    # the obtained maps are stone/concrete basecolour; tint them to stock brick so the
    # wall faces read as brick with scanned masonry grain (period palette, G8)
    mixn = nt.nodes.new("ShaderNodeMix"); mixn.data_type = "RGBA"; mixn.blend_type = "MULTIPLY"
    # RGBA sockets of ShaderNodeMix are inputs 6/7 and output 2; named lookup hits floats
    mixn.inputs[0].default_value = 1.0
    mixn.inputs[7].default_value = (0.36, 0.18, 0.14, 1)   # desaturated stock brick
    nt.links.new(ti.outputs["Color"], mixn.inputs[6])
    # scanned grain alone reads flat at hall scale: lay brick courses over it (230 x 75 mm
    # with a 12 mm mortar) and bump the mortar joints so raking lamp light catches them
    brk = nt.nodes.new("ShaderNodeTexBrick")
    brk.inputs["Color1"].default_value = (0.36, 0.17, 0.12, 1)
    brk.inputs["Color2"].default_value = (0.30, 0.14, 0.10, 1)
    brk.inputs["Mortar"].default_value = (0.35, 0.33, 0.30, 1)
    brk.inputs["Mortar Size"].default_value = 0.02
    brk.inputs["Brick Width"].default_value = 0.23
    brk.inputs["Row Height"].default_value = 0.075
    nt.links.new(tc.outputs["Object"], brk.inputs["Vector"])   # true 230 mm courses, not x12
    mix2 = nt.nodes.new("ShaderNodeMix"); mix2.data_type = "RGBA"; mix2.blend_type = "MULTIPLY"
    mix2.inputs[0].default_value = 0.55
    nt.links.new(mixn.outputs[2], mix2.inputs[6])
    nt.links.new(brk.outputs["Color"], mix2.inputs[7])
    nt.links.new(mix2.outputs[2], b.inputs["Base Color"])
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.5
    nt.links.new(brk.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.88
    return mm
BRICK = brick_material()
STONE = mat("portland_stone", (0.55, 0.53, 0.47))
IRON = mat("cast_iron", (0.06, 0.06, 0.065), 0.6, 0.8)
TIMB = mat("timber", (0.21, 0.14, 0.07))
SLATE = mat("slate_roof", (0.10, 0.11, 0.14), 0.5)   # Welsh slate, period roof covering
BRASS = mat("gilt_capital", (0.52, 0.40, 0.16), 0.4, 0.9)
GLASS = mat("crown_glass", (0.62, 0.68, 0.66), 0.15)
if "Transmission Weight" in GLASS.node_tree.nodes["Principled BSDF"].inputs:
    GLASS.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.7
# quarry tiles: procedural checker + grime noise (no scanned tile in the obtained set - recorded)
TILE = mat("quarry_tile", (0.30, 0.16, 0.12), 0.6)
nt = TILE.node_tree; b = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 1.2
tcq = nt.nodes.new("ShaderNodeTexCoord")
nt.links.new(tcq.outputs["Object"], ck.inputs["Vector"])   # object space: 0.8 m stone flags
ck.inputs["Color1"].default_value = (0.32, 0.30, 0.27, 1)
ck.inputs["Color2"].default_value = (0.26, 0.24, 0.21, 1)
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14.0
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs[0].default_value = 0.25
nt.links.new(ck.outputs["Color"], mix.inputs[6])
nt.links.new(nz.outputs["Fac"], mix.inputs[7])
nt.links.new(mix.outputs[2], b.inputs["Base Color"])

made = []; scan_parts = 0
def box(name, cx, cy, cz, hx, hy, hz, m):
    vs = [(cx + dx * hx, cy + dy * hy, cz + dz * hz) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    fs = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(2,3,7,6),(0,2,6,4)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], [list(f) for f in fs]); me.update()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob["cloaca_part"] = name; made.append(name); return ob
def cyl(name, cx, cy, cz, r, h, m, seg=12):
    vs = []; fs = []
    for z in (cz - h / 2, cz + h / 2):
        for i in range(seg):
            a = 2 * math.pi * i / seg; vs.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    for i in range(seg):
        j = (i + 1) % seg; fs.append((i, j, seg + j, seg + i))
    fs.append(tuple(range(seg))); fs.append(tuple(range(seg, 2 * seg)))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], [list(f) for f in fs]); me.update()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob["cloaca_part"] = name; made.append(name); return ob

def import_scan(fname):
    """Import a prepared scan, join to one object, return it (or None if the library lacks it)."""
    global scan_parts
    p = os.path.join(BLIB, fname + ".glb")
    if not os.path.exists(p): return None
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=p)
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    if not meshes: return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in new: o.select_set(True)
    body = max(meshes, key=lambda o: len(o.data.vertices))
    bpy.context.view_layer.objects.active = body
    if len(meshes) > 1: bpy.ops.object.join()
    for o in new:
        if o is not body and o.name in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)
    for m in list(body.modifiers): body.modifiers.remove(m)
    # the imported original is a template: copies share its mesh, it must never render
    body.name = "TPL_" + fname
    body.hide_render = True
    try: body.hide_set(True)
    except Exception: pass
    scan_parts += 1
    return body

def place(tpl, name, x, y, z=0.0, rot_z=0.0, scale=1.0):
    if tpl is None: return None
    ob = tpl.copy()                      # shares the scan mesh (2 GB doctrine)
    ob.hide_render = False               # copies of a hidden template render again
    try: ob.hide_set(False)
    except Exception: pass
    ob.name = name; ob.location = (x, y, z); ob.rotation_euler = (0, 0, rot_z); ob.scale = (scale,) * 3
    scene.collection.objects.link(ob)
    ob["cloaca_part"] = name; made.append(name)
    return ob

def iron_recolour(tpl):
    """Columns are scanned stone; Driver's pump-hall colonnade is cast iron with gilt capitals."""
    if tpl is None: return
    me = tpl.data
    H = max(v.co.z for v in me.vertices) or 1.0
    me.materials.clear()
    me.materials.append(IRON); me.materials.append(BRASS)
    for p in me.polygons:
        p.material_index = 1 if p.center.z / H > 0.86 else 0
    me.update()

def array_along(ob, count, dx):
    if ob is None or count < 2: return
    m = ob.modifiers.new("run", "ARRAY")
    m.count = int(count); m.use_relative_offset = False; m.use_constant_offset = True
    m.constant_offset_displace = (dx, 0, 0)

W, D, H = sp["house"]
# ---- scanned templates, imported once per station session ----
t_col  = import_scan("arch_doric-column-original-exterior-model"); iron_recolour(t_col)
t_col2 = import_scan("arch_tuscan-column-original-exterior-model"); iron_recolour(t_col2)
t_arch = import_scan("arch_keystone-arch-original-exterior-model")
t_pil  = import_scan("arch_pilaster-original-exterior-model")
t_wind = import_scan("arch_window-surround-original-exterior-model")
t_corn = import_scan("arch_cornice-run-original-exterior-model")
t_strg = import_scan("arch_string-course-original-exterior-model")
t_ridg = import_scan("arch_roof-ridge-original-exterior-model")
t_chim = import_scan("arch_brick-chimney-original-exterior-model")
COL_H = 6.0

# ---- engine house shell ----
box(f"{SID}/HOUSE/FLOOR-001", 0, 0, -0.2, W / 2, D / 2, 0.2, TILE)
box(f"{SID}/HOUSE/WALL-N-001", 0, D / 2, H / 2, W / 2, 0.6, H / 2, BRICK)
box(f"{SID}/HOUSE/WALL-S-001", 0, -D / 2, H / 2, W / 2, 0.6, H / 2, BRICK)
box(f"{SID}/HOUSE/WALL-E-001", W / 2, 0, H / 2, 0.6, D / 2, H / 2, BRICK)
box(f"{SID}/HOUSE/WALL-W-001", -W / 2, 0, H / 2, 0.6, D / 2, H / 2, BRICK)
box(f"{SID}/HOUSE/ROOF-001", 0, 0, H + 0.5, W / 2 + 0.6, D / 2 + 0.6, 0.35, SLATE)
# scanned cornice and string-course runs along the four eaves and at first-floor level
for tag, y, ln in (("N", D / 2 + 0.62, W), ("S", -D / 2 - 0.62, W)):
    c = place(t_corn, f"{SID}/HOUSE/CORNICE-{tag}", -ln / 2, y, H - 0.4)
    array_along(c, ln, 1.0)
    s = place(t_strg, f"{SID}/HOUSE/STRING-{tag}", -ln / 2, y, 4.2)
    array_along(s, ln, 1.0)
for tag, x, ln in (("E", W / 2 + 0.62, D), ("W", -W / 2 - 0.62, D)):
    c = place(t_corn, f"{SID}/HOUSE/CORNICE-{tag}", x, -ln / 2, H - 0.4, rot_z=math.pi / 2)
    array_along(c, ln, 1.0)
    s = place(t_strg, f"{SID}/HOUSE/STRING-{tag}", x, -ln / 2, 4.2, rot_z=math.pi / 2)
    array_along(s, ln, 1.0)
r = place(t_ridg, f"{SID}/HOUSE/RIDGE-001", -W / 2, 0, H + 0.8)
array_along(r, W, 1.0)
# window surrounds with crown glass on both long walls
nw = max(int(W // 6), 3)
for i in range(nw):
    x = -W / 2 + 3 + i * (W - 6) / max(nw - 1, 1)
    for tag, y, rz in (("N", D / 2 + 0.35, 0.0), ("S", -D / 2 - 0.35, math.pi)):
        place(t_wind, f"{SID}/HOUSE/WINDOW-{tag}{i+1:02d}", x, y, 2.6, rot_z=rz)
        box(f"{SID}/HOUSE/GLASS-{tag}{i+1:02d}", x, y - (0.1 if tag == "N" else -0.1), 3.4, 1.0, 0.04, 1.3, GLASS)
# pilasters at the four corners and flanking the ends
for i, (px, py, rz) in enumerate([(-W/2-0.4, -D/2, math.pi/2), (-W/2-0.4, D/2, math.pi/2),
                                  (W/2+0.4, -D/2, -math.pi/2), (W/2+0.4, D/2, -math.pi/2)]):
    place(t_pil, f"{SID}/HOUSE/PILASTER-{i+1:02d}", px, py, 0.0, rot_z=rz)
if sp["cruciform"]:
    box(f"{SID}/HOUSE/TRANEPT-N-001", 0, D / 2 + 8, H / 2, 10, 8, H / 2, BRICK)
    box(f"{SID}/HOUSE/TRANEPT-S-001", 0, -D / 2 - 8, H / 2, 10, 8, H / 2, BRICK)
    cyl(f"{SID}/HOUSE/DOME-001", 0, 0, H + 3.0, 7.0, 4.0, IRON)
# ---- interior colonnade and arcade: the pump-hall showcase ----
nc = sp["engines"] + 2
for i in range(nc):
    x = -W / 2 + 4 + i * (W - 8) / max(nc - 1, 1)
    for tag, y in (("N", D / 2 - 3.0), ("S", -D / 2 + 3.0)):
        tpl = t_col if (i % 2 == 0) else t_col2
        place(tpl, f"{SID}/COLONNADE/COLUMN-{tag}{i+1:02d}", x, y, 0.0)
        place(t_arch, f"{SID}/COLONNADE/ARCH-{tag}{i+1:02d}", x, y, COL_H - 0.4,
              rot_z=0.0 if tag == "N" else math.pi)
# timber roof trusses every five metres (procedural: no truss scan obtained)
for i in range(max(int(W // 5), 2)):
    x = -W / 2 + 2.5 + i * 5.0
    if x > W / 2 - 1: break
    box(f"{SID}/HOUSE/TRUSS-{i+1:02d}-TIE", x, 0, H - 0.4, 0.12, D / 2 - 1, 0.18, TIMB)
    box(f"{SID}/HOUSE/TRUSS-{i+1:02d}-RAFTER-N", x, D / 4, H + 0.2, 0.10, D / 4, 0.14, TIMB)
    box(f"{SID}/HOUSE/TRUSS-{i+1:02d}-RAFTER-S", x, -D / 4, H + 0.2, 0.10, D / 4, 0.14, TIMB)
# ---- boiler range, scanned chimney, coal stage ----
for i in range(sp["boilers"]):
    x = -W / 2 + 4 + i * (W - 8) / max(sp["boilers"] - 1, 1)
    cyl(f"{SID}/BOILERS/BOILER-{i+1:03d}", x, -D / 2 - 8, 1.6, 1.2, 3.2, IRON)
    box(f"{SID}/BOILERS/FRONT-{i+1:03d}", x, -D / 2 - 6.3, 1.4, 1.0, 0.15, 1.4, IRON)
if t_chim is not None:
    ch = place(t_chim, f"{SID}/CHIMNEY/STACK-001", W / 2 + 6, -D / 2 - 8, 0.0)
else:
    cyl(f"{SID}/CHIMNEY/STACK-001", W / 2 + 6, -D / 2 - 8, 20, 1.8, 40, BRICK)
box(f"{SID}/COAL/STAGE-001", W / 2 + 6, -D / 2 - 14, 4, 6, 4, 0.4, TIMB)
box(f"{SID}/COAL/RAMP-001", W / 2 + 12, -D / 2 - 14, 2, 6, 2, 0.3, TIMB)
# ---- pump hall and engine seats ----
box(f"{SID}/PUMPHALL/FLOOR-001", 0, D / 2 + 6, -0.15, W / 2, 8, 0.15, TILE)
for i in range(sp["engines"]):
    x = -W / 2 + 6 + i * (W - 12) / max(sp["engines"] - 1, 1)
    box(f"{SID}/SEATS/ENGINE-SEAT-{i+1:03d}", x, 0, 0.6, 2.2, 3.0, 0.6, STONE)
    box(f"{SID}/SEATS/BEAM-PEDESTAL-{i+1:03d}", x, 0, 2.4, 0.8, 1.2, 1.8, IRON)
scene["cloaca_station"] = SID
scene["cloaca_architect"] = sp["architect"]
scene["cloaca_engines"] = sp["engines"]; scene["cloaca_boilers"] = sp["boilers"]
out = os.path.join(LANE, "stations", f"{SID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in scene.objects
           if o.type == "MESH" and o.data)
cens = {"station": SID, "objects": len(made), "engines": sp["engines"], "boilers": sp["boilers"],
        "cruciform": bool(sp["cruciform"]), "architect": sp["architect"],
        "scan_parts": scan_parts, "tris": tris,
        "scans": sorted({s for s in ("arch_doric-column-original-exterior-model",
          "arch_tuscan-column-original-exterior-model", "arch_keystone-arch-original-exterior-model",
          "arch_pilaster-original-exterior-model", "arch_window-surround-original-exterior-model",
          "arch_cornice-run-original-exterior-model", "arch_string-course-original-exterior-model",
          "arch_roof-ridge-original-exterior-model", "arch_brick-chimney-original-exterior-model")}),
        "provenance": "open-source CC0 architectural scans per evidence/BUILD_SCAN_SOURCES.jsonl",
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS", f"STATION_{SID}.json"), "w"),
          indent=1, sort_keys=True)
print(json.dumps(cens))
