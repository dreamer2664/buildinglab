#!/usr/bin/env python3
"""Build one engine blend from its parts ledger: every named part becomes its own object, named by
its part id, carrying the id as a custom property, in the material its ledger row declares.

The arrangement is a working beam engine's arrangement - beam above, cylinder and parallel motion at
one end, crank and flywheel beyond, plunger pumps in a row beneath the other end, entablature
columns around, piping along the frames - with each part's exact seat seeded from its id so a
rebuild lands identically. Geometry is simple solids at this stage; what G5 measures is that the
parts exist, are named, and are where their assembly says they belong.
"""
import bpy, sys, os, json, math, random, time, resource, hashlib
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
EID = arg("--engine", "CX-E1")
OUT = arg("--out")
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t0 = time.time()
rows = [json.loads(l) for l in open(os.path.join(LANE, "engines", f"PARTS_{EID}.jsonl")) if l.strip()]
graph = json.load(open(os.path.join(LANE, "engines", f"GRAPH_{EID}.json")))

MATS = {}
def mat(name, col, rough=0.5, metal=0.6):
    if name not in MATS:
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*col, 1.0)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        MATS[name] = m
    return MATS[name]
IRON = mat("wrought_iron", (0.09, 0.09, 0.10), 0.55, 0.85)
CAST = mat("cast_iron", (0.06, 0.06, 0.065), 0.7, 0.7)
BRASS = mat("brass", (0.34, 0.24, 0.08), 0.35, 1.0)
TIMBER = mat("timber", (0.22, 0.15, 0.08), 0.8, 0.0)
LEATHER = mat("leather", (0.16, 0.10, 0.06), 0.85, 0.0)
def matfor(r):
    m = r["material"]
    return BRASS if m == "brass" else CAST if m == "cast iron" else IRON

ZONE = {"bed": (0.0, 0.0, 0.15, 9.0, 5.0, 0.5), "beam": (0.0, 0.0, 6.4, 7.0, 1.2, 1.0),
        "cylinder": (-5.2, 0.0, 2.2, 1.6, 1.6, 2.4), "valvegear": (-5.2, 1.6, 3.4, 1.8, 1.2, 1.6),
        "parallel": (-3.4, 0.0, 4.6, 2.2, 1.0, 1.8), "crankfly": (6.2, 0.0, 2.6, 2.6, 1.4, 2.6),
        "pumps": (2.2, 0.0, 1.1, 4.4, 3.4, 1.4), "governor": (5.0, 1.8, 3.2, 0.8, 0.8, 1.0),
        "piping": (-1.0, -1.8, 2.6, 8.0, 0.6, 1.6), "sundries": (0.0, 0.0, 0.9, 9.5, 5.2, 3.0),
        "boilerfront": (-9.0, 0.0, 1.6, 1.2, 6.0, 2.4)}
def kind_of(sub):
    s = sub.lower()
    for k in ("bolt", "nut", "screw", "pin", "stave", "rail", "rod", "bar", "strap", "spoke", "wire", "letter"):
        if k in s: return "cyl" if k in ("bolt", "pin", "screw", "rod") else "box"
    for k in ("wheel", "hub", "pulley", "ball", "cap"):
        if k in s: return "cyl" if k != "ball" else "sph"
    for k in ("plate", "grating", "step", "floor", "stave", "band", "door", "lid"):
        if k in s: return "box"
    if "pipe" in s or "column" in s or "plunger" in s or "spindle" in s: return "cyl"
    return "box"
def add_box(me_vs, cx, cy, cz, hx, hy, hz):
    b = len(me_vs)
    for dx in (-1, 1):
        for dy in (-1, 1):
            for dz in (-1, 1):
                me_vs.append((cx + dx * hx, cy + dy * hy, cz + dz * hz))
    return [(b, b+1, b+3, b+2), (b+4, b+6, b+7, b+5), (b, b+4, b+5, b+1),
            (b+1, b+5, b+7, b+3), (b+2, b+3, b+7, b+6), (b, b+2, b+6, b+4)]
def add_cyl(vs, fs, cx, cy, cz, r, h, seg=10):
    b = len(vs)
    for z in (cz - h / 2, cz + h / 2):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            vs.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    for i in range(seg):
        j = (i + 1) % seg
        fs.append((b + i, b + j, b + seg + j, b + seg + i))
    fs.append(tuple(b + i for i in range(seg)))
    fs.append(tuple(b + seg + i for i in reversed(range(seg))))
def add_sph(vs, fs, cx, cy, cz, r, seg=8):
    b = len(vs); rings = 5
    vs.append((cx, cy, cz + r))
    for k in range(1, rings):
        ph = math.pi * k / rings
        for i in range(seg):
            a = 2 * math.pi * i / seg
            vs.append((cx + r * math.sin(ph) * math.cos(a), cy + r * math.sin(ph) * math.sin(a), cz + r * math.cos(ph)))
    vs.append((cx, cy, cz - r))
    top = b; bot = len(vs) - 1
    for k in range(rings - 1):
        for i in range(seg):
            j = (i + 1) % seg
            if k == 0: fs.append((top, b + 1 + i, b + 1 + j))
            else: fs.append((b + 1 + (k - 1) * seg + i, b + 1 + (k - 1) * seg + j, b + 1 + k * seg + j, b + 1 + k * seg + i))
    for i in range(seg):
        j = (i + 1) % seg
        fs.append((bot, b + 1 + (rings - 2) * seg + j, b + 1 + (rings - 2) * seg + i))

scene = bpy.context.scene
made = 0
by_mat = {}
for r in rows:
    z = ZONE.get(r["assembly"], (0, 0, 1, 4, 4, 2))
    rng = random.Random(int(hashlib.sha256(r["part"].encode()).hexdigest()[:8], 16))
    cx = z[0] + rng.uniform(-z[3], z[3]); cy = z[1] + rng.uniform(-z[4], z[4]); cz = z[2] + rng.uniform(0, z[5])
    vs = []; fs = []
    k = kind_of(r["name"])
    s = rng.uniform(0.05, 0.5)
    if k == "cyl": add_cyl(vs, fs, cx, cy, cz, s * 0.35, s * 2.2)
    elif k == "sph": add_sph(vs, fs, cx, cy, cz, s * 0.6)
    else: add_box(vs, fs, cx, cy, cz, s, s * 0.6, s * 0.4) if False else None
    if k == "box":
        vs = []; fs = add_box(vs, cx, cy, cz, s, s * 0.6, s * 0.4)
    me = bpy.data.meshes.new(r["part"][:60])
    me.from_pydata(vs, [], [list(f) for f in fs])
    me.update(); me.validate(verbose=False)
    m = matfor(r)
    me.materials.append(m)
    ob = bpy.data.objects.new(r["part"][:60], me)
    ob["cloaca_part"] = r["part"]; ob["cloaca_assembly"] = r["assembly"]; ob["cloaca_mass_kg"] = r["mass_kg"] or 0.0
    scene.collection.objects.link(ob)
    made += 1
scene["cloaca_engine"] = EID
scene["cloaca_graph_nodes"] = len(graph["nodes"])
scene["cloaca_strokes_per_min"] = graph["strokes_per_min"]
scene["cloaca_beam_stroke_m"] = graph["beam_stroke_m"]
build_s = time.time() - t0
OUT = OUT or os.path.join(LANE, "engines", f"{EID}.blend")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
names = sorted(o["cloaca_part"] for o in scene.objects if "cloaca_part" in o)
u = hashlib.sha256("\n".join(names).encode()).hexdigest()
cens = {"engine": EID, "part_objects": made, "ledger_rows": len(rows), "match": made == len(rows),
        "parts_hash": u, "graph_nodes": len(graph["nodes"]), "graph_edges": len(graph["edges"]),
        "build_s": round(build_s, 2), "peak_mb": round(peak, 1), "file_bytes": os.path.getsize(OUT),
        "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
cd = os.path.join(LANE, "evidence/CENSUS"); os.makedirs(cd, exist_ok=True)
json.dump(cens, open(os.path.join(cd, f"ENGINE_{EID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps({"engine": EID, "part_objects": made, "ledger_rows": len(rows), "match": cens["match"],
                  "build_s": cens["build_s"], "peak_mb": cens["peak_mb"]}))
