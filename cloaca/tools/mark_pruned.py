#!/usr/bin/env python3
"""C-018: a chunk whose blend has been pruned from the lane is not 'built' in the file sense - its
census, hashes and ledger live on and the blend rebuilds bit-identical from them. The index row is
upserted to state built-pruned so no validator mistakes a pruned binary for a missing one."""
import sys, os, json
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def main(chunks):
    path = os.path.join(LANE, "ledgers/INDEX.jsonl")
    rows = [json.loads(l) for l in open(path) if l.strip()]
    n = 0
    for r in rows:
        if r["chunk"] in chunks and r.get("state") == "built":
            cens = os.path.join(LANE, "evidence/CENSUS", r["chunk"] + ".json")
            if not os.path.exists(os.path.join(LANE, "chunks", r["chunk"] + ".blend")) and os.path.exists(cens):
                r["state"] = "built-pruned"; n += 1
    with open(path, "w") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"INDEX: {n} rows upserted to built-pruned")
if __name__ == "__main__":
    if sys.argv[1:]:
        main(sys.argv[1:])
    else:
        import os as _os
        chunks = []
        for l in open(_os.path.join(LANE, "ledgers/INDEX.jsonl")):
            r = json.loads(l)
            if r.get("state") == "built" and not _os.path.exists(_os.path.join(LANE, "chunks", r["chunk"] + ".blend")):
                chunks.append(r["chunk"])
        main(chunks) if chunks else print("INDEX: nothing to mark")
