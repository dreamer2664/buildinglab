#!/usr/bin/env python3
"""Canonical census dump of a built chunk: open it headless, measure, print.
`diff` of two dumps is the G1 two-save determinism proof."""
import hashlib, json, os, sys
def main():
    argv = sys.argv
    if "--" in argv: argv = argv[argv.index("--") + 1:]
    chunk = argv[0] if argv else None
    if not chunk:
        print("usage: dump_chunk.py <chunk-id> (after --)"); return 2
    lane = os.environ.get("CLOACA_LANE", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import bpy
    path = os.path.join(lane, "chunks", f"{chunk}.blend")
    if not os.path.exists(path):
        print(f"FATAL no chunk file {path}"); return 1
    bpy.ops.wm.open_mainfile(filepath=path)
    scene = bpy.context.scene
    sys.path.insert(0, os.path.join(lane, "tools"))
    from build_chunk import census_union_find
    isl = 0; v = 0; f = 0; objs = []
    bnds = [[1e9]*3, [-1e9]*3]
    for ob in sorted(scene.objects, key=lambda o: o.name):
        me = ob.data
        objs.append({"name": ob.name, "verts": len(me.vertices), "faces": len(me.polygons),
                     "bricks": ob.get("cloaca_bricks")})
        v += len(me.vertices); f += len(me.polygons)
        isl += census_union_find([None]*len(me.vertices), [(e.vertices[0], e.vertices[1]) for e in me.edges])
        for vtx in me.vertices:
            for k in range(3):
                bnds[0][k] = min(bnds[0][k], vtx.co[k]); bnds[1][k] = max(bnds[1][k], vtx.co[k])
    dump = {"chunk": chunk, "objects": len(objs), "verts": v, "faces": f, "islands": isl,
            "bounds_m": [[round(x, 4) for x in b] for b in bnds],
            "props": {k: scene.get(k) for k in ("cloaca_chunk","cloaca_key","cloaca_profile","cloaca_line",
                                                "cloaca_invert_in_m","cloaca_invert_out_m","cloaca_proxy")},
            "object_table": objs}
    txt = json.dumps(dump, indent=1, sort_keys=True)
    print(txt)
    print("CENSUS_SHA256 " + hashlib.sha256(txt.encode()).hexdigest())
    return 0
if __name__ == "__main__":
    sys.exit(main())
