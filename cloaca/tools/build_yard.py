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
    vs = [(cx + dx * hx, cy + dy * hy, cz + dz * hz) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    fs = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(2,3,7,6),(0,2,6,4)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], [list(f) for f in fs]); me.update()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.rotation_euler = (0, ry, 0); ob["cloaca_part"] = name; made.append(name); return ob
rng = random.Random(int(YID[-1]))
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
scene["cloaca_yard"] = YID
out = os.path.join(LANE, "yards", f"{YID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cens = {"yard": YID, "objects": len(made), "centring_arches": 6,
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS", f"YARD_{YID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
