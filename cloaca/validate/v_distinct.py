#!/usr/bin/env python3
"""F13/F35: no two chunks are twins. Keys unique across all 1,320; census hashes unique across
built chunks; per-chunk deviation sets differ pairwise on a sample of up to 100."""
import sys, os, json, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import index, built, census, verdict, jsonl, LED
def main():
    idx = index(); b = built()
    keys = [r["key"] for r in idx]
    devs = list(jsonl(os.path.join(LED, "DEVIATIONS.jsonl")))
    probs = []
    if len(set(keys)) != len(keys): probs.append("duplicate chunk keys")
    hashes = [(r["chunk"], (census(r["chunk"]) or {}).get("census_hash")) for r in b]
    hh = [h for _, h in hashes if h]
    if len(set(hh)) != len(hh): probs.append("duplicate census hashes among built chunks")
    seen = {}
    bychunk = {}
    for d in devs: bychunk[d["chunk"]] = d          # one row per chunk; a re-lay is not a twin
    devs = [bychunk[k] for k in sorted(bychunk)]
    for d in devs:
        sig = json.dumps({k: v for k, v in sorted(d.items()) if k not in ("chunk", "key")})
        seen.setdefault(sig, []).append(d["chunk"])
    twins = [v for v in seen.values() if len(v) > 1]
    if twins: probs.append(f"deviation-set twins: {twins[:2]}")
    samp = devs[:100]
    pairs = sum(1 for a, c in itertools.combinations(samp, 2)
                if json.dumps(a, sort_keys=True) != json.dumps(c, sort_keys=True))
    return verdict("v_distinct", 1 if probs else (0 if b else 3),
                   {"keys": len(keys), "keys_unique": len(set(keys)) == len(keys),
                    "built_census_hashes": len(hh), "census_hashes_unique": len(set(hh)) == len(hh),
                    "deviation_rows": len(devs), "deviation_sample": len(samp),
                    "distinct_pairs_in_sample": pairs, "twin_groups": len(twins)},
                   "; ".join(probs) if probs else "no twins")
if __name__ == "__main__": sys.exit(main())
