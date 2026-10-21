#!/usr/bin/env python3
"""Lay the 120 figures from ledgers/PEOPLE.jsonl: one articulated figure object set per row, pose
taken from the row, face id carried as a property. Figures are simple period silhouettes - torso,
head, limbs - at this stage; G9 measures count, faces, occupation-true pose and the wear record.
"""
import bpy, sys, os, json, math, random, resource, time
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = [json.loads(l) for l in open(os.path.join(LANE, "ledgers/PEOPLE.jsonl")) if l.strip()]
scene = bpy.context.scene
WOOL = bpy.data.materials.new("wool"); WOOL.use_nodes = True
WOOL.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.16, 0.14, 0.11, 1)
LINEN = bpy.data.materials.new("linen"); LINEN.use_nodes = True
LINEN.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.39, 0.32, 1)
SKIN = bpy.data.materials.new("skin"); SKIN.use_nodes = True
SKIN.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.24, 0.17, 1)
POSE_ANG = {"barrow-run": 12, "pick-swing": 38, "shovel-stand": 4, "rammer": 20, "trowel-reach": 30,
            "line-sight": 2, "stoop-lay": 45, "gauge-read": 15, "oiler": 25, "valve-turn": 35,
            "saw-stroke": 28, "centring-fix": 40, "plane": 22, "hammer-blow": 50, "bellows": 18,
            "forge-stand": 6, "point-shout": 33, "book-check": 10, "walk": 8, "rein-hold": 16,
            "load-guide": 14, "stir-pot": 20, "bread-carry": 5, "needle-work": 42, "cloth-fold": 24}
def limb(name, x, y, z, ln, ang, m):
    vs = [(x - 0.05, y - 0.05, z), (x + 0.05, y - 0.05, z), (x + 0.05, y + 0.05, z), (x - 0.05, y + 0.05, z)]
    a = math.radians(ang)
    top = (x + ln * math.sin(a), y, z + ln * math.cos(a))
    vs += [(top[0] - 0.04, top[1] - 0.04, top[2]), (top[0] + 0.04, top[1] - 0.04, top[2]),
           (top[0] + 0.04, top[1] + 0.04, top[2]), (top[0] - 0.04, top[1] + 0.04, top[2])]
    fs = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], [list(f) for f in fs]); me.update()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob["cloaca_part"] = name; return ob
made = 0
for r in rows:
    rng = random.Random(r["seed"])
    gx = rng.uniform(-30, 30); gy = rng.uniform(-20, 20)
    ang = POSE_ANG.get(r["pose"], 10)
    limb(f"{r['id']}/TORSO", gx, gy, 1.15, 0.62, 0, WOOL)
    limb(f"{r['id']}/HEAD", gx, gy, 1.62, 0.24, 0, SKIN)
    limb(f"{r['id']}/ARM-L", gx - 0.22, gy, 1.35, 0.6, ang, WOOL)
    limb(f"{r['id']}/ARM-R", gx + 0.22, gy, 1.35, 0.6, -ang, WOOL)
    limb(f"{r['id']}/LEG-L", gx - 0.11, gy, 0.45, 0.9, 3, WOOL)
    limb(f"{r['id']}/LEG-R", gx + 0.11, gy, 0.45, 0.9, -3, WOOL)
    for o in scene.objects:
        if o.name.startswith(r["id"] + "/"):
            o["cloaca_face"] = r["face_id"]; o["cloaca_occupation"] = r["occupation"]; o["cloaca_pose"] = r["pose"]
    made += 1
out = os.path.join(LANE, "people/FIGURES.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cens = {"figures": made, "objects": len([o for o in scene.objects if 'cloaca_part' in o]),
        "faces": len({o['cloaca_face'] for o in scene.objects if 'cloaca_face' in o}),
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS/PEOPLE.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
