#!/usr/bin/env python3
"""Fold a built chunk's measured census + sha256 into INDEX.jsonl (R3: save -> sha -> ledger).
Rewrites the index atomically; keys are untouched (R4: the key is a function of the geometry
inputs, not of the census columns)."""
import json, os, sys, tempfile, time
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX  = os.path.join(LANE, "ledgers", "INDEX.jsonl")
def main(chunks):
    rows = [json.loads(l) for l in open(IDX) if l.strip()]
    by = {r["chunk"]: r for r in rows}
    changed = 0
    for c in chunks:
        p = os.path.join(LANE, "evidence", "CENSUS", f"{c}.json")
        if not os.path.exists(p): print(f"  {c}: no census, skipped"); continue
        cen = json.load(open(p))
        r = by[c]
        r.update({"sha256": cen["sha256_blend"], "census": cen["brick_objects"],
                  "census_hash": cen["census_hash"], "ledger_u_hash": cen["ledger_u_hash"],
                  "build_u_hash": cen["build_u_hash"], "u_hash_match": cen["u_hash_match"],
                  "verts": cen["verts"], "faces": cen["faces"], "objects": cen["objects"],
                  "bounds_m": cen["bounds_m"], "file_bytes": cen["file_bytes"],
                  "build_s": cen["build_s"], "peak_mb": cen["peak_mb"],
                  "state": "built" if cen["u_hash_match"] and cen["brick_objects"] == r["bricks_predicted"] else "built-defect",
                  "built_ts": cen["t"], "chunk_file": f"chunks/{c}.blend"})
        changed += 1
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(IDX))
    with os.fdopen(fd, "w") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, IDX)
    built = sum(1 for r in rows if r.get("state") == "built")
    bricks = sum(r.get("census") or 0 for r in rows)
    print(f"INDEX.jsonl: {len(rows)} rows · {changed} updated · {built} built · measured census {bricks:,}")
if __name__ == "__main__": main(sys.argv[1:])
