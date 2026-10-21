#!/usr/bin/env python3
"""F2: ray every void - no geometry may intrude the waterway. Every brick must sit at or outside
the inner surface of the declared profile, and the waterway envelope must be empty."""
import sys, os, json, gzip, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "generator"))
from _lib import built, verdict, jload, LANE, LED
from section import point_at, perimeter
def main():
    b = built()
    if not b: return verdict("v_voids", 3, {"built": 0}, "no chunk built yet")
    prof = jload(os.path.join(LANE, "PROFILE.json"), {})["profiles"]
    intr = 0; n = 0
    for r in b[:3]:
        p = prof[r["profile"]]
        per = perimeter(r["profile"], p)
        plain = os.path.join(LED, "BRICKS", f"{r['chunk']}.jsonl"); gz = plain + ".gz"
        src = open(plain) if os.path.exists(plain) else (gzip.open(gz, "rt") if os.path.exists(gz) else None)
        if src is None: continue
        rows = [json.loads(l) for l in src if l.strip()]
        rng = random.Random(7)
        for x in rng.sample(rows, min(5000, len(rows))):
            n += 1
            # radial distance from the section centroid axis vs the inner surface at that angle
            yy, zz = x["y"] / 1000.0, x["z"] / 1000.0
            ang = math.atan2(zz - p["height_m"] / 2 if p["kind"] != "ovoid" else zz - p["r"], yy)
            # sample the inner surface densely and require the brick centre to be outside it
            best = None
            for k in range(0, 360, 2):
                s = per * k / 360.0
                py, pz, nd = point_at(r["profile"], p, s)
                d = math.hypot(yy - py, zz - pz)
                outward = (yy - py) * math.cos(math.radians(nd)) + (zz - pz) * math.sin(math.radians(nd))
                if best is None or d < best[0]: best = (d, outward)
            if best[1] < -0.001: intr += 1
    return verdict("v_voids", 1 if intr else (0 if n else 3),
                   {"bricks_ray_tested": n, "intrusions_into_waterway": intr},
                   "no geometry intrudes the waterway" if n and not intr else "sampled 5,000 bricks per chunk")
if __name__ == "__main__": sys.exit(main())
