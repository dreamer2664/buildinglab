#!/usr/bin/env python3
"""G10: gas, fire and daylight - and nothing else - in every render; each render lists its sources."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, jsonl, EV
ALLOWED = ("gas", "fire", "flame", "daylight", "sun", "sky", "overcast", "moonlight", "candle", "lantern", "oil lamp", "brazier", "forge")
FORBIDDEN = ("electric", "led", "area", "point", "sun lamp", "emission", "hdri", "studio", "softbox")
def main():
    ren = list(jsonl(os.path.join(EV, "RENDERS.jsonl")))
    if not ren: return verdict("v_light", 3, {"renders": 0}, "no render has been produced yet")
    bad = []
    drawings = [r for r in ren if r.get("kind") == "drawing"]
    ren = [r for r in ren if r.get("kind") != "drawing"]   # a sheet carries no lamps; counted, not lit
    for r in ren:
        srcs = r.get("light_sources") or []
        if not srcs: bad.append(f"{r.get('id')}: no sources listed"); continue
        for s in srcs:
            sl = s.lower()
            if any(f in sl for f in FORBIDDEN): bad.append(f"{r.get('id')}: '{s}'")
            elif not any(a in sl for a in ALLOWED): bad.append(f"{r.get('id')}: '{s}' is not gas, fire or daylight")
    return verdict("v_light", 1 if bad else 0, {"renders": len(ren), "drawings_exempt": len(drawings),
                   "sources_listed": sum(len(r.get('light_sources') or []) for r in ren),
                   "violations": len(bad)}, "; ".join(bad[:4]))
if __name__ == "__main__": sys.exit(main())
