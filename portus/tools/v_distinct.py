#!/usr/bin/env python3
"""v_distinct.py — G4: 208 apartments that are not copies of each other.

    python3 portus/tools/v_distinct.py                      # machine half
    python3 portus/tools/v_distinct.py --pairs answers.json # the 10-pair human test

Machine half (from the design data, no bpy):
  1  every apartment has a unique arrangement signature (room rectangle set)
  2  identity law: no apartment's signature equals another's
  3  ≥10 plan archetypes · ≥8 palettes · ≥5 furnishing generations · ≥4 occupancy
     types, each actually used
  4  48 unique shop fascias
  5  48 unique (storey rhythm, window module, roof pitch) signatures
Human half, NEVER claimed here: the 10-pair discrimination test at 1024 px. This
script can score answers, but the answers must come from a person who has not
built the model. Self-scoring is not a vote (packet §17).
Exit 0 PASS, 2 FAIL, 3 BLOCKED (human half not supplied).
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, ROOT)


def machine():
    from build import planlib as P
    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, ok=bool(ok), detail=detail))

    apts = P.apartment_catalogue()
    sigs = collections.Counter()
    # the arrangement signature comes from the emitted rooms, not from the catalogue
    rows = list(csv.DictReader(open(os.path.join(ROOT, "design", "SCHEDULE.csv"))))
    by_apt = collections.defaultdict(list)
    for r in rows:
        if r.get("apartment"):
            by_apt[r["apartment"]].append(r)
    for apt, rs in by_apt.items():
        key = tuple(sorted((r["name"], round(float(r["x0"]), 3), round(float(r["y0"]), 3),
                            round(float(r["x1"]), 3), round(float(r["y1"]), 3)) for r in rs))
        sigs[hash(key) if False else str(key)] += 1
    uniq = len(sigs)
    dupes = sum(1 for k, v in sigs.items() if v > 1)
    check("208 unique arrangement signatures", uniq == 208 and dupes == 0,
          f"{uniq} unique over {len(by_apt)} apartments, {dupes} duplicated")

    arch = {a["archetype"] for a in apts}
    pal = {a["palette"] for a in apts}
    gen = {a["generation"] for a in apts}
    occ = {a["occupancy"] for a in apts}
    check("≥10 plan archetypes", len(arch) >= 10, f"{len(arch)}: {sorted(arch)}")
    check("≥8 palettes", len(pal) >= 8, f"{len(pal)}: {sorted(pal)}")
    check("≥5 furnishing generations", len(gen) >= 5, f"{len(gen)}: {sorted(gen)}")
    check("≥4 occupancy types", len(occ) >= 4, f"{len(occ)}: {sorted(occ)}")

    specs = P.building_specs()
    shops = {s["shop"] for s in specs}
    check("48 unique shop fascias", len(shops) == 48, f"{len(shops)} distinct of {len(specs)}")
    sig48 = {(tuple(s["storeys"][i]["h"] for i in range(len(s["storeys"]))), s["module"], s["pitch"])
             for s in specs}
    check("48 unique facade signatures", len(sig48) == 48, f"{len(sig48)} unique")

    ok = all(c["ok"] for c in checks)
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_distinct", mode="machine", ok=ok, checks=checks,
                   human_half="PENDING — 10-pair discrimination at 1024 px, non-owner judge",
                   fails=[c["name"] for c in checks if not c["ok"]]),
              open(os.path.join(ev, "v_distinct.json"), "w"), indent=1)
    for c in checks:
        print(f"  {'ok ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"v_distinct (machine): {sum(c['ok'] for c in checks)}/{len(checks)}")
    print("PASS" if ok else "FAIL")
    print("human half: PENDING (not claimed)")
    return 0 if ok else 2


def pairs(path):
    data = json.load(open(path))
    answers = data["answers"]
    key = data["key"]
    good = sum(1 for a, k in zip(answers, key) if str(a).upper() == str(k).upper())
    ev = os.path.join(ROOT, "evidence", "validation")
    os.makedirs(ev, exist_ok=True)
    json.dump(dict(validator="v_distinct", mode="pairs", ok=good >= 10, score=f"{good}/10",
                   judge=data.get("judge"), seed=data.get("seed")),
              open(os.path.join(ev, "v_distinct_pairs.json"), "w"), indent=1)
    print(f"10-pair discrimination: {good}/10 by {data.get('judge')}")
    print("PASS" if good >= 10 else "FAIL")
    return 0 if good >= 10 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default=None)
    args = ap.parse_args()
    if args.pairs:
        return pairs(args.pairs)
    return machine()


if __name__ == "__main__":
    sys.exit(main())
