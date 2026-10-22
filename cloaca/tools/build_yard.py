#!/usr/bin/env python3
"""Three construction yards (Stage G): timber centring arches standing over an open trench, brick
stacks, a gantry crane, shaft headgear, forge shed and navvy bothy. Named objects, period materials
only; the centring is timber on trestles as the centring schedule requires."""
import bpy, sys, os, json, math, resource, time, random
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
YID = arg("--yard", "yard-1")
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene = bpy.context.scene
def mat(n, c, r=0.75, m=0.0):
    mm = bpy.data.materials.new(n); mm.use_nodes = True
    b = mm.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r
    b.inputs["Metallic"].default_value = m; return mm
TIMB = mat("timber", (0.24, 0.16, 0.08)); BRICK = mat("stock_brick", (0.31, 0.29, 0.23))
IRON = mat("wrought_iron", (0.08, 0.08, 0.09), 0.55, 0.8); EARTH = mat("earth", (0.19, 0.15, 0.10))
made = []
def box(name, cx, cy, cz, hx, hy, hz, m, ry=0.0):
    # local verts + object transform: rotating must spin the box about its OWN centre,
    # not the world origin (the old world-baked variant flung the centring lags skyward)
    vs = [(dx * hx, dy * hy, dz * hz) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    fs = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(2,3,7,6),(0,2,6,4)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], [list(f) for f in fs]); me.update()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.location = (cx, cy, cz); ob.rotation_euler = (0, ry, 0)
    ob["cloaca_part"] = name; made.append(name); return ob
def import_godown():
    """C-024: the yard store is a scanned CC0 godown shell (innerscene architecture tag), not a box."""
    path = os.path.join(LANE, "stations/scan_lib_build",
                        "arch_godown-warehouse-30-x-20-m-with-loading-dock-3d-model.glb")
    if not os.path.exists(path):
        return None, 0
    before = set(bpy.data.objects)
    before_img = set(bpy.data.images)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    # the prepared GLB names its images but carries no pixels: point each at the extracted
    # tex_<base>_<i>.png in import order (prepare wrote them in glTF image-array order)
    import glob, re as _re
    texs = sorted(glob.glob(os.path.join(os.path.dirname(path), "tex_arch_godown*_*.png")),
                  key=lambda p: int(_re.search(r"_(\d+)\.png$", p).group(1)))
    fresh = [i for i in bpy.data.images if i not in before_img]
    for img, tp in zip(fresh, texs):
        img.filepath_raw = tp; img.source = 'FILE'; img.reload()
    meshes = [o for o in new if o.type == 'MESH']
    if not meshes:
        return None, 0
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in new:
        if o.type != 'MESH' and o.name in bpy.data.objects:
            try: bpy.data.objects.remove(o)
            except RuntimeError: pass
    # period pass: the scan is a whitewashed godown (plausible) but its teal accent and
    # bare aluminium are not 1860s yard vocabulary - recolour those slots only
    for slot in ob.data.materials:
        if not slot or not slot.use_nodes: continue
        b = slot.node_tree.nodes.get("Principled BSDF")
        if not b: continue
        n = slot.name.lower()
        if "teal" in n or "accent" in n:
            b.inputs["Base Color"].default_value = (0.30, 0.22, 0.14, 1)   # tarred timber
        elif "aluminum" in n or "aluminium" in n:
            b.inputs["Base Color"].default_value = (0.08, 0.08, 0.09, 1)
            b.inputs["Metallic"].default_value = 0.8
    ob.data.calc_loop_triangles()
    return ob, len(ob.data.loop_triangles)

rng = random.Random(int(YID[-1]))
box(f"{YID}/GROUND/YARD-N-001", 0, 14.25, -0.2, 45, 10.75, 0.2, EARTH)   # working ground either side
box(f"{YID}/GROUND/YARD-S-001", 0, -14.25, -0.2, 45, 10.75, 0.2, EARTH)  # of the open trench
box(f"{YID}/GROUND/TRENCH-FLOOR-001", 0, 0, -2.2, 40, 3, 0.2, EARTH)
box(f"{YID}/GROUND/TRENCH-WALL-N-001", 0, 3.2, -1.0, 40, 0.3, 1.2, EARTH)
box(f"{YID}/GROUND/TRENCH-WALL-S-001", 0, -3.2, -1.0, 40, 0.3, 1.2, EARTH)
for i in range(6):                      # timber centring arches over the trench
    x = -30 + i * 12
    for sgn in (-1, 1):
        box(f"{YID}/CENTRING/TRESTLE-{i+1:02d}{'N' if sgn>0 else 'S'}", x, sgn * 2.2, -0.6, 0.12, 0.12, 1.4, TIMB)
    for k in range(9):
        a = math.pi * k / 8
        box(f"{YID}/CENTRING/LAG-{i+1:02d}-{k:02d}", x, 2.4 * math.cos(a), -0.4 + 2.4 * math.sin(a) * 0.9,
            0.10, 0.35, 0.06, TIMB, ry=-a + math.pi / 2)
    box(f"{YID}/CENTRING/STRIP-{i+1:02d}", x, 0, 2.1, 0.08, 2.4, 0.07, TIMB)
for i in range(10):                     # brick stacks
    x = rng.uniform(-35, 35); y = rng.uniform(6, 12)
    for layer in range(5):
        box(f"{YID}/STACKS/STACK-{i+1:02d}-L{layer+1}", x, y, 0.1 + layer * 0.16, 1.2, 0.6, 0.08, BRICK)
box(f"{YID}/CRANE/GANTRY-001", 0, 14, 4.0, 18, 0.25, 0.25, IRON)
for sgn in (-1, 1):
    box(f"{YID}/CRANE/LEG-{ 'E' if sgn>0 else 'W'}", sgn * 17, 14, 2.0, 0.25, 0.25, 2.0, IRON)
box(f"{YID}/CRANE/CRAB-001", 3, 14, 3.4, 0.6, 0.5, 0.5, IRON)
box(f"{YID}/HEADGEAR/FRAME-001", -36, 0, 3.0, 0.3, 2.0, 3.0, TIMB)
box(f"{YID}/HEADGEAR/WHEEL-001", -36, 0, 6.2, 0.15, 1.2, 1.2, IRON)
box(f"{YID}/FORGE/SHED-001", 30, 10, 1.4, 4, 3, 1.4, TIMB)
box(f"{YID}/FORGE/HEARTH-001", 30, 10, 0.5, 1.0, 1.0, 0.5, BRICK)
box(f"{YID}/BOTHY/HUT-001", -28, 10, 1.1, 3, 2.5, 1.1, TIMB)
god, god_tris = import_godown()          # scanned store shed, loading dock facing the trench
if god is not None:
    god.name = f"{YID}/STORE/GODOWN-001"
    god["cloaca_part"] = god.name
    god.location = (6.0, -16.0, 0.0)
    made.append(god.name)
scene["cloaca_yard"] = YID
out = os.path.join(LANE, "yards", f"{YID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cens = {"yard": YID, "objects": len(made), "centring_arches": 6,
        "scans": 1 if god is not None else 0, "scan_tris": god_tris,
        "provenance": "stations/scan_lib_build/arch_godown-warehouse... (CC0, innerscene; REFERENCES R-159ff)",
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS", f"YARD_{YID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
