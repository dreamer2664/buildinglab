#!/usr/bin/env python3
"""Invalidate register rows so the render loop re-renders them (C-017 upserts by id).
usage: tools/rerender.py --prefix PP --reason "..."
Removes matching rows from evidence/RENDERS.jsonl and journals the invalidation in
evidence/RERENDER.jsonl with reason and timestamp. Nothing is silently deleted: the
journal is the record of why the rows left the register.
"""
import json, sys, os, datetime
argv = sys.argv[1:]
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
prefix = arg("--prefix"); reason = arg("--reason", "")
if not prefix: print("need --prefix"); sys.exit(1)
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
reg = os.path.join(LANE, "evidence/RENDERS.jsonl")
keep = []; gone = []
for l in open(reg):
    l = l.strip()
    if not l: continue
    d = json.loads(l)
    (gone if str(d.get("id", "")).startswith(prefix) else keep).append(l)
with open(reg, "w") as f:
    for l in keep: f.write(l + "\n")
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open(os.path.join(LANE, "evidence/RERENDER.jsonl"), "a") as f:
    f.write(json.dumps({"t": now, "prefix": prefix, "ids": [json.loads(l)["id"] for l in gone],
                        "count": len(gone), "reason": reason}, sort_keys=True) + "\n")
print(f"invalidated {len(gone)} rows with prefix {prefix}; {len(keep)} rows remain")
