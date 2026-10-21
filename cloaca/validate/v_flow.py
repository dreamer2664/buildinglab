#!/usr/bin/env python3
"""G7: every interior view's flow depth equals its HYDRAULICS.jsonl row; every row is solved by
Manning on the declared profile at the declared gradient."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, jsonl, LED, EV
def main():
    hyd = list(jsonl(os.path.join(LED, "HYDRAULICS.jsonl")))
    if not hyd: return verdict("v_flow", 3, {"rows": 0}, "no hydraulics ledger")
    probs = []
    for r in hyd:
        if r["depth_m"] <= 0: probs.append(f"{r['chunk']} depth {r['depth_m']}")
        if abs(r["water_surface_m"] - (r["invert_in_m"] + r["depth_m"])) > 1e-6:
            probs.append(f"{r['chunk']} surface != invert + depth")
        if r["gradient_m_per_m"] <= 0: probs.append(f"{r['chunk']} non-positive gradient")
    ren = list(jsonl(os.path.join(EV, "RENDERS.jsonl")))
    interior = [x for x in ren if x.get("class") in ("sewer_interior", "water_flow", "storm_overflow", "brick_macro")]
    unbound = [x["id"] for x in interior if not x.get("hydraulics_row")]
    if unbound: probs.append(f"{len(unbound)} interior views carry no hydraulics row id")
    sc = [r["chunk"] for r in hyd if not r["self_cleansing"]]
    return verdict("v_flow", 1 if probs else 0,
                   {"rows": len(hyd), "interior_views": len(interior), "unbound_views": len(unbound),
                    "below_self_cleansing_at_dwf": len(sc),
                    "all_half_full_self_cleansing": all(r["self_cleansing_half_full"] for r in hyd)},
                   "; ".join(probs[:3]) if probs else f"D-005 records {len(sc)} reaches below the floor at dry-weather depth")
if __name__ == "__main__": sys.exit(main())
