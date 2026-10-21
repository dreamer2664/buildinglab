#!/usr/bin/env python3
"""Build one chunk .blend FROM its ledger (R5). Run headless:

  blender --background --factory-startup --python tools/build_chunk.py --python-exit-code 1 -- \
      --chunk S0000 [--ledger path] [--proxy] [--save]

Mesh law (CONSTANTS.md §4, CONFLICTS.md C-009): one brick = one closed 8-vertex island with its
own +/-2 mm deviation; islands are carried in course-band objects (one per wythe per 100 courses).
The census is MEASURED from mesh connectivity (union-find over edges), never declared (F15).
Every command that runs this file carries --python-exit-code 1 (F21).
"""
import argparse, hashlib, json, math, os, resource, sys, time

def read_rows(path):
    rows = []
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if ln: rows.append(json.loads(ln))
    return rows

def box_verts(x, y, z, r_deg, hx, hy, hz):
    """8 corners of a brick: local axes -> sewer axis X, circumferential tangent, radial normal."""
    r = math.radians(r_deg)
    ry, rz = math.cos(r), math.sin(r)      # radial unit in (Y,Z)
    ty, tz = -math.sin(r), math.cos(r)     # tangential unit in (Y,Z)
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                out.append((x + sx * hx,
                            y + sy * hy * ty + sz * hz * ry,
                            z + sy * hy * tz + sz * hz * rz))
    return out

# cube faces over the (-1,1)^3 corner order produced above, wound outward
FACES = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(3,7,6,2),(2,6,4,0)]

def colour(g, cond, zone):
    """London stock brick: grey-yellow, drift +/-6% lightness, zone darkening (WEAR_SCHEDULE.md).
    Returns linear-ish RGBA 0..1. No brick leaves the stock family (G8)."""
    base = 0.42 + (g / 255.0 - 0.5) * 0.12
    r, gg, b = base * 1.00, base * 0.93, base * 0.74
    if zone == "invert":  r *= 0.62; gg *= 0.60; b *= 0.55
    elif zone == "flow":  r *= 0.72; gg *= 0.72; b *= 0.68
    elif zone == "splash":r *= 0.86; gg *= 0.87; b *= 0.86
    elif zone == "crown": r *= 1.06; gg *= 1.06; b *= 1.05
    if cond == 1: r += 0.16; gg += 0.15; b += 0.13          # lime bloom
    elif cond == 2: r *= 0.90; gg *= 0.88; b *= 0.85         # chipped arris
    elif cond == 3: r *= 0.80; gg *= 0.76; b *= 0.70         # repaired, different stock
    elif cond == 4: r *= 0.55; gg *= 0.52; b *= 0.45         # sediment-crusted
    elif cond == 5: r *= 0.45; gg *= 0.43; b *= 0.40         # sooted
    elif cond == 6: r *= 0.94; gg *= 0.94; b *= 0.93         # tool scar
    elif cond == 7: r *= 0.88; gg *= 0.87; b *= 0.86         # cracked
    return (min(1.0, max(0.0, r)), min(1.0, max(0.0, gg)), min(1.0, max(0.0, b)), 1.0)

def census_union_find(verts, edges):
    """verts: an int count or any sized sequence. Returns the number of connected components."""
    n = verts if isinstance(verts, int) else len(verts)
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    return len({find(i) for i in range(n)})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk", required=True)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--lane", default=None)
    ap.add_argument("--proxy", action="store_true")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)

    LANE = a.lane or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ledger = a.ledger or os.path.join(LANE, "ledgers", "BRICKS", f"{a.chunk}.jsonl")
    idxrow = None
    with open(os.path.join(LANE, "ledgers", "INDEX.jsonl")) as f:
        for ln in f:
            r = json.loads(ln)
            if r["chunk"] == a.chunk: idxrow = r; break
    if idxrow is None:
        print(f"FATAL orphan chunk: no INDEX.jsonl row for {a.chunk}"); return 1
    tag = "_PROXY" if a.proxy else ""
    lmeta = json.load(open(os.path.join(LANE, "evidence", "CENSUS", f"{a.chunk}{tag}_LEDGER.json")))
    rows = read_rows(ledger)
    if len(rows) != lmeta["census"] and not a.proxy:
        print(f"FATAL ledger row count {len(rows)} != ledger meta census {lmeta['census']}"); return 1

    import bpy
    t0 = time.time()
    # clean slate
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"; scene.unit_settings.scale_length = 1.0  # 1 unit = 1 m (§15.1)
    scene["cloaca_chunk"] = a.chunk; scene["cloaca_key"] = idxrow["key"]
    scene["cloaca_profile"] = idxrow["profile"]; scene["cloaca_line"] = idxrow["line"]
    scene["cloaca_invert_in_m"] = idxrow["invert_in_m"]; scene["cloaca_invert_out_m"] = idxrow["invert_out_m"]
    scene["cloaca_proxy"] = bool(a.proxy)
    if scene.cycles is not None:
        scene.cycles.use_denoising = False      # Debian Blender has no OpenImageDenoise (SANDBOX trap 1)

    bands = {}
    for r in rows:
        bands.setdefault((r["w"], r["c"] // 100), []).append(r)
    built = 0; ukeys = []
    for (w, b) in sorted(bands):
        vs, fs, cs = [], [], []
        for r in bands[(w, b)]:
            x = r["x"] / 1000.0; y = r["y"] / 1000.0; z = r["z"] / 1000.0
            dl, dw, dh = r["d"]
            hx = (0.076 + dh / 10000.0) / 2.0            # axial   76 mm +/-2
            hy = (r["l"] + dl / 10.0) / 2000.0           # circumferential (closure bricks are cut)
            hz = (0.114 + dw / 10000.0) / 2.0            # radial  114 mm +/-2
            base = len(vs)
            vs.extend(box_verts(x, y, z, r["r"] / 100.0, hx, hy, hz))
            col = colour(r["g"], r["k"], r["z_"])
            for f in FACES:
                fs.append(tuple(base + i for i in f)); cs.extend([col] * 4)
            ukeys.append((r["w"], r["c"], r["j"], r["u"])); built += 1
        me = bpy.data.meshes.new(f"{a.chunk}_w{w}_b{b:02d}")
        me.from_pydata(vs, [], [list(f) for f in fs])
        attr = me.color_attributes.new("brick", type="FLOAT_COLOR", domain="CORNER")
        attr.data.foreach_set("color", [c for col in cs for c in col])
        me.update(); me.validate(verbose=False)
        ob = bpy.data.objects.new(me.name, me)
        ob["cloaca_band"] = b; ob["cloaca_wythe"] = w; ob["cloaca_bricks"] = len(bands[(w, b)])
        scene.collection.objects.link(ob)
    build_s = time.time() - t0

    # ---- measured census: connected components per object, summed ----
    t1 = time.time(); islands = 0; tot_v = 0; tot_f = 0
    bounds = [[1e9]*3, [-1e9]*3]
    for ob in scene.objects:
        me = ob.data
        tot_v += len(me.vertices); tot_f += len(me.polygons)
        islands += census_union_find(len(me.vertices), [(e.vertices[0], e.vertices[1]) for e in me.edges])
        for v in me.vertices:
            for k in range(3):
                if v.co[k] < bounds[0][k]: bounds[0][k] = v.co[k]
                if v.co[k] > bounds[1][k]: bounds[1][k] = v.co[k]
    census_s = time.time() - t1
    u_hash = hashlib.sha256("\n".join(u for _,_,_,u in sorted(ukeys)).encode()).hexdigest()
    census_hash = hashlib.sha256(json.dumps(
        {"chunk": a.chunk, "key": idxrow["key"], "islands": islands, "u_hash": u_hash,
         "verts": tot_v, "faces": tot_f, "bounds_mm": [[int(round(x*1000)) for x in b] for b in bounds]},
        sort_keys=True).encode()).hexdigest()
    out = a.out or os.path.join(LANE, "chunks", f"{a.chunk}.blend")
    sha = None
    if a.save:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=out)
        h = hashlib.sha256()
        with open(out, "rb") as f:
            for blk in iter(lambda: f.read(1 << 20), b""): h.update(blk)
        sha = h.hexdigest()
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    census = {"chunk": a.chunk, "key": idxrow["key"], "profile": idxrow["profile"], "line": idxrow["line"],
              "proxy": bool(a.proxy), "brick_objects": islands, "bricks_laid": built,
              "ledger_rows": len(rows), "ledger_u_hash": lmeta["u_hash"], "build_u_hash": u_hash,
              "u_hash_match": u_hash == lmeta["u_hash"],
              "verts": tot_v, "faces": tot_f, "objects": len(scene.objects),
              "bounds_m": [[round(x, 3) for x in b] for b in bounds],
              "census_hash": census_hash, "sha256_blend": sha, "file_bytes": os.path.getsize(out) if sha else None,
              "build_s": round(build_s, 2), "census_s": round(census_s, 2), "peak_mb": round(peak_mb, 1),
              "invert_in_m": idxrow["invert_in_m"], "invert_out_m": idxrow["invert_out_m"],
              "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    cd = os.path.join(LANE, "evidence", "CENSUS"); os.makedirs(cd, exist_ok=True)
    json.dump(census, open(os.path.join(cd, f"{a.chunk}{'_PROXY' if a.proxy else ''}.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps({k: census[k] for k in ("chunk","proxy","brick_objects","ledger_rows","u_hash_match",
                                             "verts","faces","objects","build_s","census_s","peak_mb",
                                             "file_bytes","sha256_blend","census_hash")}, indent=1))
    if not census["u_hash_match"]:
        print("FATAL: build order u_hash != ledger u_hash (F42 mesh-link failure)"); return 1
    if islands != built:
        print(f"FATAL: measured islands {islands} != bricks laid {built}"); return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
