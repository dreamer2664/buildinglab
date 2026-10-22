#!/usr/bin/env python3
"""Lay the 120 figures from ledgers/PEOPLE.jsonl (cloaca-people/1.2.0, C-023).

Bodies are open-source scans: each row names a scan from people/scan_lib (prepared by
tools/scan_prepare.py from sources recorded with sha256 and licence in SCAN_SOURCES.jsonl).
Per scan three hue-group templates are built once and shared by every figure assigned to
them (object duplicates, one mesh datablock per template - the 2 GB doctrine); each figure
then carries its own yaw, scale, age stoop, period headgear and the tool its pose uses.
Faces: cloaca_face property per figure, unique per ledger row; census counts them.
"""
import bpy, sys, os, json, math, random, resource, time

LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# --factory-startup still loads the default startup scene (Cube, Camera, Light): drop it,
# it has haunted every figures proof since the scan rebuild began
bpy.ops.wm.read_factory_settings(use_empty=True)
rows = [json.loads(l) for l in open(os.path.join(LANE, "ledgers/PEOPLE.jsonl")) if l.strip()]
if not rows or "scan" not in rows[0]:
    print("ledger is pre-1.2.0 (no scan assignments); run tools/generator/people.py first"); sys.exit(1)
scene = bpy.context.scene
LIB = os.path.join(LANE, "people/scan_lib")

HUE_FACTORS = [(1.00, 1.00, 1.00), (1.12, 1.04, 0.90), (0.84, 0.88, 0.96)]
# anatomical mannequins: single-material naked bodies; the template step dresses them in
# period block colours by height band (boots / trousers / shirt / skin) so no figure reads naked
MANNEQUINS = {"inn_abstract-white-man-3d-person-standing", "inn_abstract-white-man-3d-person-walking",
              "inn_abstract-white-woman-3d-person-standing", "inn_abstract-white-woman-3d-person-walking",
              "inn_male-base-mesh-3d-person-rigged-a-pose", "inn_female-base-mesh-3d-person-rigged-a-pose",
              "inn_walking-adult", "inn_jordan-3d-person-athlete"}
BAND_COLORS = {"boots": (0.22, 0.14, 0.09), "trousers": (0.45, 0.38, 0.27),
               "shirt": (0.16, 0.15, 0.14), "skin": (0.35, 0.24, 0.17)}

def is_cloth(name):
    n = (name or "").lower()
    return not any(t in n for t in ("skin", "body", "head", "hand", "face", "ear", "neck",
                                    "hair", "brow", "lash", "beard", "eye", "teeth", "tongue", "mouth"))

def limit_textures():
    for img in bpy.data.images:
        try:
            if img.size[0] > 1024:
                img.scale(1024, 1024)
        except Exception:
            pass

def dress_mannequin(body):
    """Replace the single mannequin material with period block colours by height band.
    Bands are fractions of the normalised standing height (scan_prepare put the feet on
    z=0 and the crown on TARGET_H): boots, trousers, shirt sleeves and torso, then skin."""
    me = body.data
    # local vertex space: scan_prepare normalised feet to z=0 and the crown to TARGET_H
    # in the exported mesh; object transforms here carry glTF node offsets that would
    # shift every band if world space were used
    H = max(v.co.z for v in me.vertices) or 1.0
    mats = []
    for k in ("boots", "trousers", "shirt", "skin"):
        m = bpy.data.materials.new(f"period_{k}"); m.use_nodes = True
        n = m.node_tree.nodes["Principled BSDF"]
        n.inputs["Base Color"].default_value = (*BAND_COLORS[k], 1)
        n.inputs["Roughness"].default_value = 0.85
        mats.append(m)
    me.materials.clear()
    for m in mats: me.materials.append(m)
    for p in me.polygons:
        z = p.center.z / H
        p.material_index = 0 if z < 0.07 else (1 if z < 0.48 else (2 if z < 0.84 else 3))
    me.update()

def bsdf(mat):
    if not mat.use_nodes: return None
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED": return n
    return None

# ---- templates: per scan, import once, join, armature out, three hue variants ----
templates = {}   # (scan, hue) -> object whose mesh is shared by that family
scans = sorted({r["scan"] for r in rows})
missing = [s for s in scans if not os.path.exists(os.path.join(LIB, s + "_hero.glb"))]
if missing:
    print("scan_lib missing variants for:", missing, "- run tools/scan_prepare.py"); sys.exit(1)
for scan in scans:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(LIB, scan + "_hero.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    # junk filter: some source GLBs carry stray reference cubes (a 2 m box at the origin);
    # a human scan never contains a rigid part bigger than a person
    # junk filter: some source GLBs carry stray reference cubes (a 2 m box at the
    # origin); no part of a standing human spans 1.2 m on its smallest axis.
    # Dimensions are measured from the vertices - object.dimensions is stale (zero)
    # until the depsgraph evaluates, which has not happened yet in a fresh import.
    def vdims(o):
        # local vertex extents times object scale: object.dimensions is stale before
        # the depsgraph evaluates, and world space would mix in glTF node offsets
        sc = o.scale
        xs = [v.co.x for v in o.data.vertices]; ys = [v.co.y for v in o.data.vertices]
        zs = [v.co.z for v in o.data.vertices]
        if not xs: return (0.0, 0.0, 0.0)
        return ((max(xs) - min(xs)) * abs(sc.x), (max(ys) - min(ys)) * abs(sc.y),
                (max(zs) - min(zs)) * abs(sc.z))
    for o in list(meshes):
        d = vdims(o)
        if max(d) > 2.5 or min(d) > 1.2:
            meshes.remove(o)
            bpy.data.objects.remove(o, do_unlink=True)
    if not meshes:
        print("no mesh imported for", scan); sys.exit(1)
    bpy.ops.object.select_all(action="DESELECT")
    for o in new: o.select_set(True)
    body = max(meshes, key=lambda o: len(o.data.vertices))
    bpy.context.view_layer.objects.active = body
    if len(meshes) > 1:
        bpy.ops.object.join()
    for o in new:
        if o is not body and o.name in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)
    for m in list(body.modifiers):
        body.modifiers.remove(m)
    body.name = f"TPL_{scan}_src"
    if scan in MANNEQUINS:
        dress_mannequin(body)
    limit_textures()
    for hue in (0, 1, 2):
        tpl = body.copy()
        tpl.data = body.data.copy()
        tpl.name = f"TPL_{scan}_{hue}"
        scene.collection.objects.link(tpl)
        f = HUE_FACTORS[hue]
        if hue:
            mats = []
            for slot in tpl.material_slots:
                m = slot.material
                if m is None: continue
                mc = m.copy()
                if is_cloth(m.name):
                    n = bsdf(mc)
                    if n:
                        c = list(n.inputs["Base Color"].default_value)
                        n.inputs["Base Color"].default_value = (
                            min(1.0, c[0] * f[0]), min(1.0, c[1] * f[1]), min(1.0, c[2] * f[2]), c[3])
                mats.append(mc)
            idxs = [p.material_index for p in tpl.data.polygons]
            tpl.data.materials.clear()      # this zeroes every polygon index...
            for mc in mats: tpl.data.materials.append(mc)
            for p, i in zip(tpl.data.polygons, idxs):   # ...so put the bands back
                p.material_index = i
            tpl.data.update()
        tpl.hide_set(True)
        tpl.hide_render = True          # templates never render; figures duplicate them
        templates[(scan, hue)] = tpl
    bpy.data.objects.remove(body, do_unlink=True)
    if bpy.data.objects.get("Cube"): print("CUBE AFTER SCAN", scan)

# ---- period materials for headgear and tools ----
def mat(name, rgb, rough=0.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if "Metallic" in n.inputs: n.inputs["Metallic"].default_value = 0.0
    return m
M_CAP   = mat("cloth_cap", (0.20, 0.18, 0.15))
M_FELT  = mat("felt_hat", (0.13, 0.12, 0.11))
M_BONNET= mat("cotton_bonnet", (0.74, 0.71, 0.65))
M_WOOD  = mat("tool_wood", (0.36, 0.25, 0.15))
M_IRON  = mat("tool_iron", (0.24, 0.24, 0.25), rough=0.55)
M_CANVAS= mat("tool_canvas", (0.55, 0.50, 0.40))
M_BRASS = mat("tool_brass", (0.55, 0.44, 0.20), rough=0.4)

def part(name, mesh, m, loc, rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    ob = bpy.data.objects.new(name, mesh); ob.material_slots  # noqa
    ob.location = loc; ob.rotation_euler = rot; ob.scale = scale
    scene.collection.objects.link(ob)
    if m: ob.data.materials.append(m)
    ob["cloaca_part"] = name
    return ob

def box(name, sx, sy, sz):
    me = bpy.data.meshes.new(name); bpy.ops.object.select_all(action="DESELECT")
    bm = __import__("bmesh").new()
    __import__("bmesh").ops.create_cube(bm, size=1.0)
    bm.to_mesh(me); bm.free(); me.update()
    return me, (sx, sy, sz)

def cyl(name, r, d, verts=12):
    # 4.3's bmesh.ops.create_cone keywords differ from older releases (known trap);
    # the ops route is stable - create far away, keep the mesh, drop the object
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=(9999, 9999, 9999))
    ob = bpy.context.active_object
    me = ob.data; me.name = name; me.use_fake_user = True
    bpy.data.objects.remove(ob, do_unlink=True)
    return me

def headgear(kind, gid, hx, hy, hz, s):
    if kind == "cloth cap":
        me = cyl(f"{gid}/CAP", 0.105 * s, 0.10 * s, 14)
        part(f"{gid}/HAT", me, M_CAP, (hx, hy, hz + 0.02 * s))
        me2 = cyl(f"{gid}/CAPBRIM", 0.13 * s, 0.015 * s, 14)
        part(f"{gid}/HAT-BRIM", me2, M_CAP, (hx, hy, hz - 0.01 * s))
    elif kind == "felt hat":
        me = cyl(f"{gid}/CROWN", 0.085 * s, 0.13 * s, 14)
        part(f"{gid}/HAT", me, M_FELT, (hx, hy, hz + 0.05 * s))
        me2 = cyl(f"{gid}/BRIM", 0.17 * s, 0.012 * s, 16)
        part(f"{gid}/HAT-BRIM", me2, M_FELT, (hx, hy, hz - 0.01 * s))
    elif kind == "cotton bonnet":
        me = cyl(f"{gid}/BONNET", 0.11 * s, 0.12 * s, 14)
        part(f"{gid}/HAT", me, M_BONNET, (hx, hy - 0.03 * s, hz + 0.03 * s), rot=(math.radians(15), 0, 0))

def tool(kind, gid, gx, gy, s, yaw):
    if kind in ("none", None): return
    dx = gx + 0.28 * s * math.cos(yaw); dy = gy + 0.28 * s * math.sin(yaw)
    z = 0.95 * s
    if kind == "barrow":
        me, sc = box(f"{gid}/BARROW", 0.5, 0.4, 0.25)
        part(f"{gid}/TOOL", me, M_WOOD, (dx + 0.12 * s, dy, 0.42 * s), scale=sc)
        part(f"{gid}/TOOL-WHEEL", cyl(f"{gid}/WHEEL", 0.12 * s, 0.04 * s), M_IRON,
             (dx + 0.40 * s, dy, 0.12 * s), rot=(math.pi / 2, 0, 0))
    elif kind == "pick":
        me, sc = box(f"{gid}/PICK", 0.05, 0.05, 0.9)
        part(f"{gid}/TOOL", me, M_WOOD, (dx, dy, z), rot=(0, math.radians(35), 0), scale=sc)
        me2, sc2 = box(f"{gid}/PICKHEAD", 0.55, 0.04, 0.05)
        part(f"{gid}/TOOL-HEAD", me2, M_IRON, (dx, dy, z + 0.42 * s), rot=(0, math.radians(35), math.radians(12)), scale=sc2)
    elif kind in ("shovel", "rammer"):
        me, sc = box(f"{gid}/SHAFT", 0.045, 0.045, 1.0)
        part(f"{gid}/TOOL", me, M_WOOD, (dx, dy, z), rot=(0, math.radians(8), 0), scale=sc)
        me2, sc2 = box(f"{gid}/BLADE", 0.2, 0.03, 0.26)
        part(f"{gid}/TOOL-BLADE", me2, M_IRON, (dx, dy, z - 0.55 * s), rot=(0, math.radians(8), 0), scale=sc2)
    elif kind == "trowel":
        me, sc = box(f"{gid}/TROWEL", 0.05, 0.12, 0.02)
        part(f"{gid}/TOOL", me, M_IRON, (dx, dy, z + 0.1 * s), scale=sc)
    elif kind == "saw":
        me, sc = box(f"{gid}/SAW", 0.5, 0.012, 0.12)
        part(f"{gid}/TOOL", me, M_IRON, (dx, dy, z + 0.1 * s), rot=(0, 0, math.radians(20)), scale=sc)
    elif kind == "hammer" or kind == "mallet":
        me, sc = box(f"{gid}/HAMMER", 0.04, 0.04, 0.35)
        part(f"{gid}/TOOL", me, M_WOOD, (dx, dy, z + 0.1 * s), scale=sc)
        me2, sc2 = box(f"{gid}/HEAD", 0.14, 0.06, 0.07)
        part(f"{gid}/TOOL-HEAD", me2, M_IRON, (dx, dy, z + 0.28 * s), scale=sc2)
    elif kind == "oilcan":
        part(f"{gid}/TOOL", cyl(f"{gid}/CAN", 0.06 * s, 0.16 * s, 12), M_BRASS, (dx, dy, z))
    elif kind == "gauge":
        part(f"{gid}/TOOL", cyl(f"{gid}/GAUGE", 0.07 * s, 0.03 * s, 12), M_BRASS, (dx, dy, z + 0.2 * s))
    elif kind == "spanner":
        me, sc = box(f"{gid}/SPANNER", 0.035, 0.3, 0.02)
        part(f"{gid}/TOOL", me, M_IRON, (dx, dy, z + 0.1 * s), rot=(math.radians(60), 0, 0), scale=sc)
    elif kind == "bellows":
        me, sc = box(f"{gid}/BELLOWS", 0.5, 0.3, 0.12)
        part(f"{gid}/TOOL", me, M_WOOD, (dx + 0.3 * s, dy, 0.5 * s), scale=sc)
    elif kind == "tongs":
        me, sc = box(f"{gid}/TONGS", 0.03, 0.7, 0.03)
        part(f"{gid}/TOOL", me, M_IRON, (dx, dy, z), rot=(0, math.radians(20), 0), scale=sc)
    elif kind == "book":
        me, sc = box(f"{gid}/BOOK", 0.16, 0.22, 0.035)
        part(f"{gid}/TOOL", me, M_CANVAS, (dx, dy, z + 0.1 * s), rot=(math.radians(70), 0, 0), scale=sc)
    elif kind == "rein":
        me, sc = box(f"{gid}/REIN", 0.02, 0.9, 0.02)
        part(f"{gid}/TOOL", me, M_CANVAS, (dx, dy, z + 0.05 * s), rot=(math.radians(50), 0, 0), scale=sc)
    elif kind == "line":
        part(f"{gid}/TOOL", cyl(f"{gid}/REEL", 0.05 * s, 0.08 * s, 10), M_WOOD, (dx, dy, z))
    elif kind == "plane":
        me, sc = box(f"{gid}/PLANE", 0.28, 0.08, 0.1)
        part(f"{gid}/TOOL", me, M_WOOD, (dx, dy, z), scale=sc)
    elif kind == "ladle":
        part(f"{gid}/TOOL", cyl(f"{gid}/LADLE", 0.09 * s, 0.5 * s, 10), M_IRON, (dx, dy, z), rot=(0, math.radians(25), 0))
    elif kind == "tray":
        me, sc = box(f"{gid}/TRAY", 0.45, 0.32, 0.04)
        part(f"{gid}/TOOL", me, M_WOOD, (dx, dy, z + 0.15 * s), scale=sc)
    elif kind == "needle":
        me, sc = box(f"{gid}/NEEDLE", 0.004, 0.004, 0.05)
        part(f"{gid}/TOOL", me, M_IRON, (dx, dy, z + 0.15 * s), scale=sc)
        me2, sc2 = box(f"{gid}/CLOTH", 0.3, 0.22, 0.01)
        part(f"{gid}/TOOL-CLOTH", me2, M_CANVAS, (dx, dy, z + 0.05 * s), rot=(math.radians(60), 0, 0), scale=sc2)
    elif kind == "cloth":
        me, sc = box(f"{gid}/CLOTH", 0.34, 0.26, 0.012)
        part(f"{gid}/TOOL", me, M_CANVAS, (dx, dy, z + 0.08 * s), rot=(math.radians(55), 0, 0), scale=sc)

# ballast ground: graded grey-brown with a mud noise mix, big enough for every PP camera
gm = bpy.data.materials.new("ballast"); gm.use_nodes = True
nt = gm.node_tree; bsdfn = nt.nodes["Principled BSDF"]
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 40.0
noise.inputs["Detail"].default_value = 6.0
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.09, 0.075, 0.06, 1)
ramp.color_ramp.elements[1].color = (0.22, 0.185, 0.145, 1)
nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bsdfn.inputs["Base Color"])
bsdfn.inputs["Roughness"].default_value = 0.95
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.005))
gnd = bpy.context.active_object; gnd.name = "GROUND"; gnd.scale = (260, 180, 1)
gnd.data.materials.append(gm)

if bpy.data.objects.get("Cube"): print("CUBE AFTER GROUND")
made = 0; tris_inst = 0; tris_uniq = 0
for r in rows:
    rng = random.Random(r["seed"])
    gx = rng.uniform(-30, 30); gy = rng.uniform(-20, 20)
    v = r["vars"]
    tpl = templates[(r["scan"], v["hue"])]
    ob = tpl.copy()                       # shares the template mesh (2 GB doctrine)
    ob.name = f"{r['id']}/BODY"
    ob.hide_set(False); ob.hide_render = False
    scene.collection.objects.link(ob)
    s = v["scale"]
    ob.location = (gx, gy, 0)
    ob.rotation_euler = (math.radians(v["stoop_deg"]), 0, math.radians(v["yaw_deg"]))
    ob.rotation_mode = "YZX"              # yaw first, then the age stoop pitches forward
    ob.scale = (s, s, s)
    ob["cloaca_face"] = r["face_id"]; ob["cloaca_occupation"] = r["occupation"]
    ob["cloaca_pose"] = r["pose"]; ob["cloaca_scan"] = r["scan"]
    ob["cloaca_part"] = ob.name
    tris_inst += sum(len(p.vertices) - 2 for p in tpl.data.polygons)
    hz = 1.62 * s
    yaw = math.radians(v["yaw_deg"])
    headgear(v["headgear"], r["id"], gx, gy, hz, s)
    tool(v["tool"], r["id"], gx, gy, s, yaw)
    made += 1
for (scan, hue), tpl in templates.items():
    tris_uniq += sum(len(p.vertices) - 2 for p in tpl.data.polygons)

out = os.path.join(LANE, "people/FIGURES.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cens = {"figures": made, "objects": len([o for o in scene.objects if 'cloaca_part' in o]),
        "faces": len({o['cloaca_face'] for o in scene.objects if 'cloaca_face' in o}),
        "scans_used": len({r["scan"] for r in rows}),
        "templates": len(templates),
        "tris_instanced": tris_inst, "tris_unique": tris_uniq,
        "provenance": "open-source scans per evidence/SCAN_SOURCES.jsonl (CC0, Innerscene; poses CC BY 4.0 Ian Mason 100STYLE)",
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS/PEOPLE.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
