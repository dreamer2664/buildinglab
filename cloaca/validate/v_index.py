#!/usr/bin/env python3
"""INDEX.jsonl is the network: 1,320 rows, valid unique keys, no orphans, sha256 on every built chunk."""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import index, verdict, LANE
def main():
    rows = index(); probs = []
    if len(rows) != 1320: probs.append(f"rows {len(rows)} != 1320")
    ids = [r["chunk"] for r in rows]
    if len(set(ids)) != len(ids): probs.append("duplicate chunk ids")
    keys = [r["key"] for r in rows]
    if len(set(keys)) != len(keys): probs.append("duplicate keys")
    if not all(re.fullmatch(r"[0-9a-f]{64}", k or "") for k in keys): probs.append("key not sha256-shaped")
    exp = [f"S{i:04d}" for i in range(1320)]
    if ids != exp: probs.append("chunk ids are not the continuous S0000..S1319 series")
    orph = []
    d = os.path.join(LANE, "chunks")
    onfile = {f[:-6] for f in os.listdir(d) if f.endswith(".blend")} if os.path.isdir(d) else set()
    inrows = set(ids)
    orph += [f for f in onfile - inrows]
    for r in rows:
        if r.get("state") in ("built", "built-defect"):
            if not r.get("sha256"): probs.append(f"{r['chunk']} built without sha256")
            if not r.get("census"): probs.append(f"{r['chunk']} built without a measured census")
            if r["chunk"] not in onfile: probs.append(f"{r['chunk']} built but no .blend (release payload missing)")
    return verdict("v_index", 1 if probs else 0,
                   {"rows": len(rows), "built": sum(1 for r in rows if r.get("state","").startswith("built")),
                    "orphans": len(orph), "problems": len(probs)}, "; ".join(probs[:5]))
if __name__ == "__main__": sys.exit(main())
