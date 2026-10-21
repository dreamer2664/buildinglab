#!/usr/bin/env python3
"""Census against the PROFILE.json schedule: recomputed from geometry, never declared (§15.2, F39)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "generator"))
from _lib import index, built, verdict, jload, LANE
from profile import chunk_census
def main():
    prof = jload(os.path.join(LANE, "PROFILE.json"), {})
    P = prof.get("profiles", {})
    if not P: return verdict("v_profile", 1, {}, "PROFILE.json has no profile schedule")
    idx = index(); b = built()
    bad = []; kinds = {}
    for r in idx:
        p = P[r["profile"]]; kinds[r["profile"]] = kinds.get(r["profile"], 0) + 1
        kw = ({"r": p["r"]} if p["kind"] == "ovoid" else {"d": p["d"]} if p["kind"] == "circle"
              else {"h": p["h"], "w": p["w"]})
        exp = chunk_census(100.0, p["kind"], p["wythes"], pid=r["profile"], prof=p, **kw)["census"]
        if exp != r["bricks_predicted"]: bad.append((r["chunk"], f"{exp} vs {r['bricks_predicted']}"))
    cited = [pid for pid, p in P.items() if p.get("cites")]
    return verdict("v_profile", 1 if (bad or len(cited) != len(P)) else 0,
                   {"profiles": len(P), "profiles_cited": len(cited), "rows_checked": len(idx),
                    "mismatches": len(bad), "built_chunks": len(b), "schedule": kinds},
                   "every profile carries a citation" if len(cited) == len(P) else "an uncited profile is F39")
if __name__ == "__main__": sys.exit(main())
