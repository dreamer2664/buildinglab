#!/usr/bin/env python3
"""Embankment reaches (Stage G): river wall, terrace walk, roadway and the gas lampposts - 312 of
them across the three reaches, 104 per blend, each a named object so the lamppost count is a census
and not a claim. The river is a plane at the tide level TIDES.json gives for the reach."""
import bpy, sys, os, json, math, resource, time
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
EID = arg("--reach", "victoria")
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REACH = {"victoria": 0, "albert": 1, "chelsea": 2}
scene = bpy.context.scene
def mat(n, c, r=0.7, m=0.0):
    mm = bpy.data.materials.new(n); mm.use_nodes = True
    b = mm.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r
    b.inputs["Metallic"].default_value = m; return mm
STONE = mat("granite", (0.35, 0.34, 0.32)); IRON = mat("cast_iron", (0.05, 0.05, 0.055), 0.5, 0.85)
LANT = mat("lantern_glass", (1.0, 0.62, 0.28), 0.3)   # gas lantern glazing, lit
_lb = LANT.node_tree.nodes["Principled BSDF"]
_lb.inputs["Emission Color"].default_value = (1.0, 0.55, 0.22, 1)
_lb.inputs["Emission Strength"].default_value = 18.0
WATER = mat("river", (0.05, 0.06, 0.045), 0.04); MAC = mat("macadam", (0.22, 0.21, 0.19))
made = []; lamps = 0
def box(name, cx, cy, cz, hx, hy, hz, m):
    vs = [(cx + dx * hx, cy + dy * hy, cz + dz * hz) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    fs = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(2,3,7,6),(0,2,6,4)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], [list(f) for f in fs]); me.update()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob["cloaca_part"] = name; made.append(name); return ob
def cyl(name, cx, cy, cz, r, h, m, seg=8):
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
def import_scan(glob_base):
    """C-024: scanned CC0 architectural fabric (innerscene architecture tag) for the embankment."""
    import glob, re as _re
    path = glob.glob(os.path.join(LANE, "stations/scan_lib_build", glob_base + "*.glb"))
    if not path:
        return None, 0
    path = path[0]
    before = set(bpy.data.objects); before_img = set(bpy.data.images)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    texs = sorted(glob.glob(os.path.join(LANE, "stations/scan_lib_build",
                  "tex_" + glob_base + "*.png")), key=lambda p: int(_re.search(r"_(\d+)\.png$", p).group(1)))
    for img, tp in zip([i for i in bpy.data.images if i not in before_img], texs):
        img.filepath_raw = tp; img.source = 'FILE'; img.reload()
    meshes = [o for o in new if o.type == 'MESH']
    if not meshes:
        return None, 0
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in new:
        if o.type != 'MESH' and o.name in bpy.data.objects:
            try: bpy.data.objects.remove(o)
            except RuntimeError: pass
    ob.data.calc_loop_triangles()
    return ob, len(ob.data.loop_triangles)

L = 1200.0                       # 1.2 km of reach per blend; 3 reaches = 3.6 km
box(f"{EID}/WALL/RIVER-WALL-001", 0, -6, 1.5, L / 2, 1.2, 2.5, STONE)
box(f"{EID}/WALL/PARAPET-001", 0, -4.6, 4.2, L / 2, 0.25, 0.5, STONE)
box(f"{EID}/WALK/TERRACE-001", 0, 0, 3.6, L / 2, 4.0, 0.2, STONE)
box(f"{EID}/ROAD/ROADWAY-001", 0, 9, 3.5, L / 2, 5.0, 0.15, MAC)
box(f"{EID}/RIVER/WATER-001", 0, -30, 0.6, L / 2, 26, 0.05, WATER)
for i in range(104):
    x = -L / 2 + 6 + i * (L - 12) / 103
    cyl(f"{EID}/LAMPS/LAMP-{REACH[EID]*104+i+1:03d}-POST", x, -3.6, 5.3, 0.07, 3.4, IRON)
    box(f"{EID}/LAMPS/LAMP-{REACH[EID]*104+i+1:03d}-LANTERN", x, -3.6, 7.2, 0.16, 0.16, 0.28, LANT)
    lamps += 1
# ---- scanned stone fabric (C-024): cornice run along the parapet, pilasters to the river wall
scan_tris = 0; scan_objs = 0
corn, ct = import_scan("arch_cornice-run-original-exterior-model")
if corn is not None:
    corn.name = f"{EID}/WALL/CORNICE-001"; corn["cloaca_part"] = corn.name
    corn.location = (-L / 2, -4.6, 4.75)
    m = corn.modifiers.new("run", "ARRAY"); m.count = 1200
    m.use_relative_offset = False; m.use_constant_offset = True; m.constant_offset_displace = (1.0, 0, 0)
    made.append(corn.name); scan_tris += ct; scan_objs += 1
pil, pt = import_scan("arch_pilaster-original-exterior-model")
if pil is not None:
    for i in range(50):
        x = -L / 2 + 12 + i * 24.0
        ob = bpy.data.objects.new(f"{EID}/WALL/PILASTER-{i+1:02d}", pil.data)   # linked duplicates
        ob.location = (x, -7.35, 0.0)
        ob["cloaca_part"] = ob.name
        scene.collection.objects.link(ob); made.append(ob.name)
    bpy.data.objects.remove(pil)     # template itself never renders
    scan_tris += pt; scan_objs += 50
scene["cloaca_reach"] = EID; scene["cloaca_lampposts"] = lamps
out = os.path.join(LANE, "embankments", f"{EID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cens = {"reach": EID, "objects": len(made), "lampposts": lamps, "length_m": L,
        "scans": scan_objs, "scan_tris": scan_tris,
        "provenance": "stations/scan_lib_build arch_cornice-run + arch_pilaster (CC0, innerscene; REFERENCES R-151ff)",
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS", f"EMBANK_{EID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
