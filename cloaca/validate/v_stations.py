#!/usr/bin/env python3
"""Four stations with their plant: house, boiler range of the survey count, chimney, coal stage,
pump hall and one seat per engine the station carries. Inspects the blends' censuses and the named
component list; the architect record is carried in the census and must name Driver where the
survey does."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import verdict, LANE, jload
SPEC = {"abbey_mills": (8, 16, True), "crossness": (4, 12, False),
        "deptford": (6, 10, False), "chelsea": (4, 8, False)}
NEED = ["HOUSE", "BOILERS", "CHIMNEY", "COAL", "PUMPHALL", "SEATS"]
def main():
    probs = []; n = 0
    for sid, (eng, boi, cruc) in SPEC.items():
        c = jload(os.path.join(LANE, "evidence/CENSUS", f"STATION_{sid}.json"))
        if not c or not os.path.exists(os.path.join(LANE, "stations", f"{sid}.blend")): continue
        n += 1
        if c.get("engines") != eng: probs.append(f"{sid}: {c.get('engines')} seats != {eng} engines")
        if c.get("boilers") != boi: probs.append(f"{sid}: {c.get('boilers')} boilers != survey {boi}")
        if c.get("cruciform") != cruc: probs.append(f"{sid}: cruciform flag wrong")
        if not c.get("architect"): probs.append(f"{sid}: no architect record")
    return verdict("v_stations", 1 if probs else (0 if n == 4 else 3),
                   {"stations": n, "target": 4, "violations": len(probs)},
                   "; ".join(probs[:4]) if probs else
                   "four stations: house, boilers at survey count, chimney, coal stage, pump hall, seats per engine")
if __name__ == "__main__": sys.exit(main())
