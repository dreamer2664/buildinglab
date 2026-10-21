#!/usr/bin/env python3
"""G5: 22 engines, >=4,200 named parts each, parts schedule complete, linkage graph published.

Inspects, rather than counting files: per engine the blend must exist, its objects must equal the
parts ledger row for row (measured in the engine census), every object name must follow the station
naming scheme, the materials must be period-lawful, and the linkage graph must be a graph over the
parts - nodes a subset of the ledger, edges joining parts that exist.
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import verdict, LANE, jload
EXPECT = [(f"AM-E{i}") for i in range(1, 9)] + [f"CX-E{i}" for i in range(1, 5)] + \
         [f"DF-E{i}" for i in range(1, 7)] + [f"CH-E{i}" for i in range(1, 5)]
FLOOR = 4200
NAME_RE = re.compile(r"^(AM|CX|DF|CH)-E\d+/[A-Z]+/[A-Z0-9-]+-\d{3}$")
MATERIALS = {"wrought iron", "cast iron", "brass", "timber", "leather"}
def main():
    probs = []; parts_total = 0; engines_ok = 0
    for eid in EXPECT:
        ledger = os.path.join(LANE, "engines", f"PARTS_{eid}.jsonl")
        blend = os.path.join(LANE, "engines", f"{eid}.blend")
        cens = jload(os.path.join(LANE, "evidence/CENSUS", f"ENGINE_{eid}.json"))
        graph = jload(os.path.join(LANE, "engines", f"GRAPH_{eid}.json"))
        if not os.path.exists(ledger): probs.append(f"{eid}: no parts ledger"); continue
        rows = [json.loads(l) for l in open(ledger) if l.strip()]
        parts_total += len(rows)
        if len(rows) < FLOOR: probs.append(f"{eid}: {len(rows)} named parts < {FLOOR}")
        if not os.path.exists(blend): probs.append(f"{eid}: no blend"); continue
        if not cens: probs.append(f"{eid}: no engine census"); continue
        if cens.get("part_objects") != len(rows):
            probs.append(f"{eid}: {cens.get('part_objects')} objects != {len(rows)} ledger rows")
        if not cens.get("match"): probs.append(f"{eid}: census match flag false")
        bad_names = [r["part"] for r in rows if not NAME_RE.match(r["part"])]
        if bad_names: probs.append(f"{eid}: {len(bad_names)} part ids outside the naming scheme")
        bad_mat = {r["material"] for r in rows} - MATERIALS
        if bad_mat: probs.append(f"{eid}: materials outside the period law: {sorted(bad_mat)}")
        if not graph: probs.append(f"{eid}: no linkage graph"); continue
        ids = {r["part"] for r in rows}
        if not set(graph.get("nodes", [])) <= ids: probs.append(f"{eid}: graph nodes outside the ledger")
        for e in graph.get("edges", []):
            if e["a"] not in ids or e["b"] not in ids: probs.append(f"{eid}: graph edge over a missing part")
        if len(graph.get("edges", [])) < 8: probs.append(f"{eid}: linkage graph too small to be a chain")
        engines_ok += 1
    return verdict("v_parts", 1 if probs else (0 if engines_ok == 22 else 3),
                   {"engines": engines_ok, "target": 22, "named_parts_total": parts_total,
                    "floor_per_engine": FLOOR, "violations": len(probs)},
                   "; ".join(probs[:4]) if probs else
                   f"22 engines, {parts_total} named parts, every object equal to its ledger row, graphs published")
if __name__ == "__main__": sys.exit(main())
