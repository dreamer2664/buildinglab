#!/usr/bin/env python3
"""The four pumping stations as built shells with their plant (Stage H, G5 context): engine house
on the recorded plan, the boiler range of the survey count, chimney, coal stage, pump hall, and one
named seat per engine the station carries. Driver's architecture is declared in the title property,
not faked in geometry at this stage - the shell is brick, stone and iron, and the record says what
it is.
"""
import bpy, sys, os, json, math, time, resource
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
SID = arg("--station", "abbey_mills")
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
BRICK = mat("stock_brick", (0.31, 0.29, 0.23)); STONE = mat("portland_stone", (0.55, 0.53, 0.47))
IRON = mat("cast_iron", (0.06, 0.06, 0.065), 0.6, 0.8); TIMB = mat("timber", (0.21, 0.14, 0.07))
made = []
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
W, D, H = sp["house"]
# engine house: four walls, floor, roof ridge; cruciform adds two transepts at Abbey Mills
box(f"{SID}/HOUSE/FLOOR-001", 0, 0, -0.2, W / 2, D / 2, 0.2, STONE)
box(f"{SID}/HOUSE/WALL-N-001", 0, D / 2, H / 2, W / 2, 0.6, H / 2, BRICK)
box(f"{SID}/HOUSE/WALL-S-001", 0, -D / 2, H / 2, W / 2, 0.6, H / 2, BRICK)
box(f"{SID}/HOUSE/WALL-E-001", W / 2, 0, H / 2, 0.6, D / 2, H / 2, BRICK)
box(f"{SID}/HOUSE/WALL-W-001", -W / 2, 0, H / 2, 0.6, D / 2, H / 2, BRICK)
box(f"{SID}/HOUSE/ROOF-001", 0, 0, H + 0.5, W / 2 + 0.6, D / 2 + 0.6, 0.35, TIMB)
if sp["cruciform"]:
    box(f"{SID}/HOUSE/TRANEPT-N-001", 0, D / 2 + 8, H / 2, 10, 8, H / 2, BRICK)
    box(f"{SID}/HOUSE/TRANEPT-S-001", 0, -D / 2 - 8, H / 2, 10, 8, H / 2, BRICK)
    cyl(f"{SID}/HOUSE/DOME-001", 0, 0, H + 3.0, 7.0, 4.0, IRON)
# boiler range, chimney, coal stage
for i in range(sp["boilers"]):
    x = -W / 2 + 4 + i * (W - 8) / max(sp["boilers"] - 1, 1)
    cyl(f"{SID}/BOILERS/BOILER-{i+1:03d}", x, -D / 2 - 8, 1.6, 1.2, 3.2, IRON)
    box(f"{SID}/BOILERS/FRONT-{i+1:03d}", x, -D / 2 - 6.3, 1.4, 1.0, 0.15, 1.4, IRON)
cyl(f"{SID}/CHIMNEY/STACK-001", W / 2 + 6, -D / 2 - 8, 20, 1.8, 40, BRICK)
box(f"{SID}/COAL/STAGE-001", W / 2 + 6, -D / 2 - 14, 4, 6, 4, 0.4, TIMB)
box(f"{SID}/COAL/RAMP-001", W / 2 + 12, -D / 2 - 14, 2, 6, 2, 0.3, TIMB)
# pump hall and engine seats
box(f"{SID}/PUMPHALL/FLOOR-001", 0, D / 2 + 6, -0.15, W / 2, 8, 0.15, STONE)
for i in range(sp["engines"]):
    x = -W / 2 + 6 + i * (W - 12) / max(sp["engines"] - 1, 1)
    box(f"{SID}/SEATS/ENGINE-SEAT-{i+1:03d}", x, D / 2 + 6, 0.6, 2.2, 3.0, 0.6, STONE)
    box(f"{SID}/SEATS/BEAM-PEDESTAL-{i+1:03d}", x, D / 2 + 6, 2.4, 0.8, 1.2, 1.8, IRON)
scene["cloaca_station"] = SID
scene["cloaca_architect"] = sp["architect"]
scene["cloaca_engines"] = sp["engines"]; scene["cloaca_boilers"] = sp["boilers"]
out = os.path.join(LANE, "stations", f"{SID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cens = {"station": SID, "objects": len(made), "engines": sp["engines"], "boilers": sp["boilers"],
        "architect": sp["architect"], "cruciform": sp["cruciform"],
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS", f"STATION_{SID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
