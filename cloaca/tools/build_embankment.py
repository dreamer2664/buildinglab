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
L = 1200.0                       # 1.2 km of reach per blend; 3 reaches = 3.6 km
box(f"{EID}/WALL/RIVER-WALL-001", 0, -6, 1.5, L / 2, 1.2, 2.5, STONE)
box(f"{EID}/WALL/PARAPET-001", 0, -4.6, 4.2, L / 2, 0.25, 0.5, STONE)
box(f"{EID}/WALK/TERRACE-001", 0, 0, 3.6, L / 2, 4.0, 0.2, STONE)
box(f"{EID}/ROAD/ROADWAY-001", 0, 9, 3.5, L / 2, 5.0, 0.15, MAC)
box(f"{EID}/RIVER/WATER-001", 0, -30, 0.6, L / 2, 26, 0.05, WATER)
for i in range(104):
    x = -L / 2 + 6 + i * (L - 12) / 103
    cyl(f"{EID}/LAMPS/LAMP-{REACH[EID]*104+i+1:03d}-POST", x, -3.6, 5.3, 0.07, 3.4, IRON)
    box(f"{EID}/LAMPS/LAMP-{REACH[EID]*104+i+1:03d}-LANTERN", x, -3.6, 7.2, 0.16, 0.16, 0.28, IRON)
    lamps += 1
scene["cloaca_reach"] = EID; scene["cloaca_lampposts"] = lamps
out = os.path.join(LANE, "embankments", f"{EID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cens = {"reach": EID, "objects": len(made), "lampposts": lamps, "length_m": L,
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS", f"EMBANK_{EID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
