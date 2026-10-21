#!/usr/bin/env python3
"""1 Blender unit = 1 metre (§15.1), checked on measured bounds, not on a declaration."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import built, census, verdict
def main():
    b = built()
    if not b: return verdict("v_units", 3, {"built_chunks": 0}, "no chunk built yet")
    bad = []
    for r in b:
        c = census(r["chunk"])
        if not c: bad.append((r["chunk"], "no census")); continue
        (x0, y0, z0), (x1, y1, z1) = c["bounds_m"]
        if not (99.0 <= x1 - x0 <= 101.0): bad.append((r["chunk"], f"length {x1-x0:.3f} m"))
        if abs(z0) > 1.0 or z1 > 6.0: bad.append((r["chunk"], f"vertical extent {z0:.2f}..{z1:.2f} m"))
    return verdict("v_units", 1 if bad else 0, {"chunks": len(b), "violations": len(bad)},
                   "; ".join(f"{c}: {w}" for c, w in bad[:4]))
if __name__ == "__main__": sys.exit(main())
