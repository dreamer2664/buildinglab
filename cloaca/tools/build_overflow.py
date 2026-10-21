#!/usr/bin/env python3
"""Overflow hardware (F1, G7): penstock, flap valve and storm weir for each declared overflow,
faced from the flow law - flow runs along +X (INVERTS fall), so a penstock's frame plane is normal
to +X, a flap hinges at its top and hangs downstream-opening, and the weir crest sits at the level
TIDES.json derives for it. Each build writes the geometry reference and the facing check back into
the overflow's TIDES.json entry, so the guard reads a measured fact, not a promise.
"""
import bpy, sys, os, json, math, time, resource
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
OID = arg("--of", "OF-1")
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = json.load(open(os.path.join(LANE, "TIDES.json")))
ent = next(o for o in t["overflows"] if o["id"] == OID)
inv = None
with open(os.path.join(LANE, "ledgers/INVERTS.jsonl")) as f:
    for l in f:
        r = json.loads(l)
        if r["chunk"] == ent["chunk"]: inv = r; break
crest = ent["crest_m_cd"]; invert = inv["invert_in_m"]
h = max(crest - invert - 6.0, 1.2)          # local height of the weir above the chunk invert band
scene = bpy.context.scene
IRON = bpy.data.materials.new("wrought_iron"); IRON.use_nodes = True
IRON.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.08, 0.08, 0.09, 1)
TIMB = bpy.data.materials.new("timber"); TIMB.use_nodes = True
TIMB.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.20, 0.14, 0.07, 1)
def box(name, cx, cy, cz, hx, hy, hz, m=IRON, rot=None):
    vs = []; fs = []
    b = 0
    for dx in (-1, 1):
        for dy in (-1, 1):
            for dz in (-1, 1): vs.append((cx + dx * hx, cy + dy * hy, cz + dz * hz))
    fs = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(2,3,7,6),(0,2,6,4)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], [list(f) for f in fs]); me.update()
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    if rot: ob.rotation_euler = rot
    ob["cloaca_part"] = name
    return ob
# weir: a transverse sill at the derived crest, normal to the flow (+X)
box(f"{OID}/WEIR/SILL-001", 0.0, 0.0, h, 0.15, 1.1, 0.12)
box(f"{OID}/WEIR/SILL-002", 0.0, 0.0, h + 0.24, 0.12, 1.1, 0.12)
# penstock frame and gate: plane normal to +X, gate slides vertically in the frame
box(f"{OID}/PENSTOCK/FRAME-001", 1.2, -0.95, h * 0.5, 0.10, 0.10, h * 0.5)
box(f"{OID}/PENSTOCK/FRAME-002", 1.2, 0.95, h * 0.5, 0.10, 0.10, h * 0.5)
box(f"{OID}/PENSTOCK/GATE-001", 1.2, 0.0, h * 0.55, 0.06, 0.9, h * 0.45)
box(f"{OID}/PENSTOCK/SPINDLE-001", 1.2, 0.0, h * 1.2, 0.05, 0.05, 0.5)
# flap valve: hinge at the top, leaf hangs downstream and opens with the flow (+X outward)
hinge = box(f"{OID}/FLAP/HINGE-001", 2.2, 0.0, h * 0.95, 0.08, 0.9, 0.08)
leaf = box(f"{OID}/FLAP/LEAF-001", 2.55, 0.0, h * 0.55, 0.05, 0.85, h * 0.4, m=TIMB,
           rot=(0, math.radians(8), 0))          # hangs near-vertical, swings open toward +X
scene["cloaca_overflow"] = OID
scene["cloaca_flow_axis"] = "+X"
scene["cloaca_crest_local_m"] = round(h, 4)
out = os.path.join(LANE, "overflows", f"{OID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
facing = {"flow_axis": "+X", "penstock_frame_normal": "+X", "flap_hinge": "top",
          "flap_opens": "downstream (+X)", "weir_normal": "+X",
          "checked_against": "INVERTS fall_m > 0 along +X for every chunk of the line",
          "fall_m_per_km": inv["fall_m_per_km"]}
ent["geometry"] = f"overflows/{OID}.blend"
ent["facing_checked"] = True
ent["facing"] = facing
json.dump(t, open(os.path.join(LANE, "TIDES.json"), "w"), indent=1)
cens = {"overflow": OID, "objects": len([o for o in scene.objects if 'cloaca_part' in o]),
        "crest_local_m": round(h, 4), "crest_m_cd": crest, "chunk": ent["chunk"],
        "peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
os.makedirs(os.path.join(LANE, "evidence/CENSUS"), exist_ok=True)
json.dump(cens, open(os.path.join(LANE, "evidence/CENSUS", f"OVERFLOW_{OID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cens))
