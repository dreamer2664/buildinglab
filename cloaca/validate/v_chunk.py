#!/usr/bin/env python3
"""Per built chunk: measured census = recomputed census, mesh-link hash matches, build inside budget."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import built, census, verdict
OPEN_BUDGET_S = 120.0   # §15.5
MEM_CEILING_MB = 1200.0 # agency SANDBOX.md
def main():
    b = built()
    if not b: return verdict("v_chunk", 3, {"built": 0}, "no chunk built yet")
    bad = []
    for r in b:
        c = census(r["chunk"])
        if not c: bad.append((r["chunk"], "no census")); continue
        if c["brick_objects"] != r["bricks_predicted"]:
            bad.append((r["chunk"], f"census {c['brick_objects']} != predicted {r['bricks_predicted']}"))
        if not c.get("u_hash_match"): bad.append((r["chunk"], "u_hash mismatch (F42)"))
        if c.get("peak_mb", 0) > MEM_CEILING_MB: bad.append((r["chunk"], f"peak {c['peak_mb']} MB over ceiling"))
        if c.get("build_s", 0) > OPEN_BUDGET_S: bad.append((r["chunk"], f"build {c['build_s']} s over budget"))
    return verdict("v_chunk", 1 if bad else 0,
                   {"built": len(b), "census_eq_ledger": sum(1 for r in b if (census(r["chunk"]) or {}).get("brick_objects") == r["bricks_predicted"]),
                    "max_build_s": max((census(r["chunk"]) or {}).get("build_s", 0) for r in b),
                    "max_peak_mb": max((census(r["chunk"]) or {}).get("peak_mb", 0) for r in b),
                    "violations": len(bad)}, "; ".join(f"{c}: {w}" for c, w in bad[:4]))
if __name__ == "__main__": sys.exit(main())
