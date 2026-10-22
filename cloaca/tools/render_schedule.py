#!/usr/bin/env python3
"""The §24 view schedule as a machine list: one entry per view to render, with its class, scene and
recipe. Counts follow validate/v_renders.py SPEC; classes already delivered as drawings are not
repeated here."""
import json, os, sys
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def built_chunks():
    out = []
    for l in open(os.path.join(LANE, "ledgers/INDEX.jsonl")):
        r = json.loads(l)
        if r.get("state") in ("built", "built-defect", "built-pruned"): out.append(r["chunk"])
    return out
def main():
    ch = built_chunks()
    step = max(1, len(ch) // 560)
    pick = ch[::step][:560]
    S = []
    for i, c in enumerate(pick): S.append(dict(id=f"SI-{c}", cls="sewer_interior", scene=f"chunk:{c}", recipe="interior", k=i))
    for i, c in enumerate(pick[:96]): S.append(dict(id=f"WF-{c}", cls="water_flow", scene=f"chunk:{c}", recipe="water", k=i))
    for i, c in enumerate(pick[:80]): S.append(dict(id=f"BM-{c}", cls="brick_macro", scene=f"chunk:{c}", recipe="macro", k=i))
    for o in range(1, 7):
        for k in range(6): S.append(dict(id=f"SO-OF{o}-{k}", cls="storm_overflow", scene=f"overflows/OF-{o}.blend", recipe="overflow", k=k))
    E = [f"AM-E{i}" for i in range(1, 9)] + [f"CX-E{i}" for i in range(1, 5)] + [f"DF-E{i}" for i in range(1, 7)] + [f"CH-E{i}" for i in range(1, 5)]
    for e in E:
        for k in range(4): S.append(dict(id=f"EC-{e}-{k}", cls="engine_closeup", scene=f"engines/{e}.blend", recipe="engine_closeup", k=k))
    for e in E[:16]:
        for k in range(3): S.append(dict(id=f"MD-{e}-{k}", cls="mechanism_detail", scene=f"engines/{e}.blend", recipe="mechanism_detail", k=k))
    for e in E[:15]:
        for k in range(2): S.append(dict(id=f"IM-{e}-{k}", cls="iron_macro", scene=f"engines/{e}.blend", recipe="iron_macro", k=k))
    for s in ("abbey_mills", "crossness", "deptford", "chelsea"):
        for k in range(4): S.append(dict(id=f"SH-{s}-{k}", cls="station_hero", scene=f"stations/{s}.blend", recipe="station_hero", k=k))
        for k in range(12): S.append(dict(id=f"EH-{s}-{k}", cls="engine_house", scene=f"stations/{s}.blend", recipe="engine_house", k=k))
    for y in ("yard-1", "yard-2", "yard-3"):
        for k in range(20): S.append(dict(id=f"CY-{y}-{k}", cls="construction_yard", scene=f"yards/{y}.blend", recipe="construction_yard", k=k))
        for k in range(6): S.append(dict(id=f"CA-{y}-{k}", cls="centring_arch", scene=f"yards/{y}.blend", recipe="centring_arch", k=k))
    for r in ("victoria", "albert", "chelsea"):
        for k in range(22): S.append(dict(id=f"EW-{r}-{k}", cls="embankment_walk", scene=f"embankments/{r}.blend", recipe="embankment_walk", k=k))
        for k in range(8): S.append(dict(id=f"LP-{r}-{k}", cls="lamppost", scene=f"embankments/{r}.blend", recipe="lamppost", k=k))
    for k in range(72): S.append(dict(id=f"PP-{k:03d}", cls="people", scene="people/FIGURES.blend", recipe="people", k=k))
    for k in range(42): S.append(dict(id=f"AE-{k:03d}", cls="aerial", scene=("stations/abbey_mills.blend" if k % 3 == 0 else "yards/yard-1.blend" if k % 3 == 1 else "embankments/victoria.blend"), recipe="aerial", k=k))
    for i, s in enumerate(S):
        s["width"], s["height"], s["samples"] = 1024, 576, 16
    json.dump(S, open(os.path.join(LANE, "evidence/RENDER_SCHEDULE.json"), "w"), indent=0)
    from collections import Counter
    print(len(S), "views:", dict(Counter(s["cls"] for s in S)))
if __name__ == "__main__":
    main()
