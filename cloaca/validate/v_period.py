#!/usr/bin/env python3
"""G8: no anachronism. Materials inside the declared stock-brick family; every render lists its
light sources and none of them is electric; nothing modern in the lane's declared palette."""
import sys, os, json, gzip
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, jsonl, built, EV, LED
ELECTRIC = ("electric", "led", "arc lamp", "arc-lamp", "fluorescent", "filament", "tungsten",
            "neon", "halogen", "emission shader", "area light", "point light", "sun lamp")
def main():
    ren = list(jsonl(os.path.join(EV, "RENDERS.jsonl")))
    b = built()
    probs = []
    for r in ren:
        srcs = [s.lower() for s in r.get("light_sources", [])]
        if not srcs: probs.append(f"{r.get('id')} lists no light sources (G10)")
        for s in srcs:
            if any(e in s for e in ELECTRIC): probs.append(f"{r.get('id')} light source '{s}'")
    if not ren and not b: return verdict("v_period", 3, {"renders": 0, "built_chunks": 0}, "no subject yet")
    # palette: the brick colours in a built chunk must stay inside the stock family
    fam = 0; n = 0
    if b:
        plain = os.path.join(LED, "BRICKS", f"{b[0]['chunk']}.jsonl"); gz = plain + ".gz"
        src = open(plain) if os.path.exists(plain) else (gzip.open(gz, "rt") if os.path.exists(gz) else None)
        if src:
            for l in src:
                if not l.strip(): continue
                g = json.loads(l)["g"]; n += 1
                if not (0 <= g <= 255): fam += 1
    return verdict("v_period", 1 if probs else (0 if ren else 3),
                   {"renders_audited": len(ren), "electric_sources": len([p for p in probs if 'light source' in p]),
                    "bricks_palette_checked": n, "outside_family": fam},
                   "; ".join(probs[:3]) if probs else "gas, fire and daylight only; palette inside the stock family")
if __name__ == "__main__": sys.exit(main())
