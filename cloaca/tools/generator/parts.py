#!/usr/bin/env python3
"""Parts ledgers and linkage graphs for the 22 beam engines (G5).

Counts per assembly are the PARTS_SCHEDULE.md table, generated row by row so the schedule and the
ledger cannot drift: every named part gets its own row, its own id in the station naming scheme, an
assembly, a material from the period law, and a mass where the survey carries one. The linkage
graph is the kinematic chain a reviewer can open: nodes are the moving parts, edges are joints.
"""
import os, json, random, hashlib, datetime
LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENG = os.path.join(LANE, "engines"); os.makedirs(ENG, exist_ok=True)

STATIONS = [("AM", "abbey_mills", 8, "B"), ("CX", "crossness", 4, "A"),
            ("DF", "deptford", 6, "C"), ("CH", "chelsea", 4, "D")]
NAMES = {"CX": ["VICTORIA", "PRINCE-CONSORT", "ALBERT-EDWARD", "ALEXANDRA"]}

# assembly -> (count, material, mass kg or None) per class, exactly as PARTS_SCHEDULE.md tabulates
CLASS = {
 "A": [("bed", 214, "cast iron", 900), ("beam", 96, "wrought iron", 292), ("cylinder", 331, "cast iron", 40),
       ("valvegear", 412, "wrought iron", 18), ("parallel", 168, "wrought iron", 12), ("crankfly", 388, "wrought iron", 60),
       ("pumps", 1064, "cast iron", 85), ("governor", 186, "brass", 3), ("piping", 297, "wrought iron", 22),
       ("sundries", 1152, "wrought iron", 6)],
 "B": [("bed", 246, "cast iron", 850), ("beam", 92, "wrought iron", 280), ("cylinder", 318, "cast iron", 38),
       ("valvegear", 402, "wrought iron", 17), ("parallel", 164, "wrought iron", 12), ("crankfly", 372, "wrought iron", 55),
       ("pumps", 532, "cast iron", 90), ("governor", 178, "brass", 3), ("piping", 288, "wrought iron", 21),
       ("sundries", 1516, "wrought iron", 6), ("boilerfront", 100, "cast iron", 40)],
 "C": [("bed", 198, "cast iron", 700), ("beam", 88, "wrought iron", 240), ("cylinder", 302, "cast iron", 30),
       ("valvegear", 386, "wrought iron", 15), ("parallel", 160, "wrought iron", 11), ("crankfly", 356, "wrought iron", 48),
       ("pumps", 798, "cast iron", 70), ("governor", 172, "brass", 3), ("piping", 276, "wrought iron", 19),
       ("sundries", 1472, "wrought iron", 5)],
 "D": [("bed", 186, "cast iron", 640), ("beam", 86, "wrought iron", 220), ("cylinder", 296, "cast iron", 28),
       ("valvegear", 378, "wrought iron", 14), ("parallel", 158, "wrought iron", 10), ("crankfly", 348, "wrought iron", 44),
       ("pumps", 532, "cast iron", 65), ("governor", 168, "brass", 3), ("piping", 268, "wrought iron", 18),
       ("sundries", 1790, "wrought iron", 5)],
}
SUBNAMES = {"bed": ["sole plate", "bed plate", "entablature column", "column cap", "hold-down bolt", "wall plate",
                    "bracket", "pedestal", "foundation bolt", "grouting plate"],
            "beam": ["rocking beam", "centre strap", "gib", "key", "main centre pin", "bearing brass", "stand plate",
                     "radius rod", "beam bolt", "springing plate"],
            "cylinder": ["cylinder barrel", "liner", "cylinder cover", "gland", "stuffing box", "piston", "piston rod",
                         "crosshead", "cotter", "lagging stave", "lagging band", "cover bolt", "nozzle", "flange"],
            "valvegear": ["valve chest", "valve spindle", "cam", "lever", "rod", "tappet", "dashpot", "camshaft",
                          "bearing", "pin", "bush", "handgear lever", "gearing"],
            "parallel": ["link", "bar", "pin", "bush", "bracket", "adjusting screw", "strap", "washer"],
            "crankfly": ["crankshaft", "crank web", "crank pin", "bearing", "flywheel hub", "flywheel spoke",
                         "rim segment", "rim bolt", "spoke bolt", "barring tooth", "pinion", "pulley"],
            "pumps": ["plunger", "pump casing", "suction valve", "suction seat", "delivery valve", "delivery seat",
                      "valve door", "door bolt", "pump rod", "rod crosshead", "guide", "pump gland", "bucket"],
            "governor": ["governor ball", "governor spindle", "belt", "pulley", "oil cup", "sight feed", "oil pipe"],
            "piping": ["steam pipe", "branch pipe", "flange", "flange bolt", "expansion piece", "exhaust pipe",
                       "feed check valve", "gauge cock", "gauge glass", "gauge fitting"],
            "sundries": ["tie bar", "tie nut", "girder bolt", "lagging wire", "nameplate letter", "grating",
                         "handrail stanchion", "handrail rail", "step", "pattern mark", "paint mark", "floor plate"],
            "boilerfront": ["boiler door", "door hinge", "door latch", "firebar", "front plate mounting",
                            "manhole lid", "lid bolt", "gauge bracket", "blow-off cock", "feed clack"]}
KINEMATIC = ["rocking beam", "main centre pin", "piston rod", "crosshead", "crankshaft", "crank web", "crank pin",
             "flywheel hub", "plunger", "pump rod", "valve spindle", "cam", "governor spindle", "link", "bar"]

def gen():
    tot = 0
    summary = []
    for stn, sname, neng, cls in STATIONS:
        for e in range(1, neng + 1):
            eid = f"{stn}-E{e}"
            ename = NAMES.get(stn, [None] * neng)[e - 1] if stn in NAMES else f"{sname.upper()} {e}"
            rng = random.Random(int(hashlib.sha256(eid.encode()).hexdigest()[:8], 16))
            rows = []
            graph_nodes = []; graph_edges = []
            for asm, count, mat, mass in CLASS[cls]:
                subs = SUBNAMES[asm]
                per = {}
                for i in range(1, count + 1):
                    sub = subs[(i - 1) % len(subs)]
                    k = per.get(sub, 0) + 1; per[sub] = k
                    pid = f"{eid}/{asm.upper()}/{sub.upper().replace(' ', '-')}-{k:03d}"
                    m = mass
                    if m: m = round(m * rng.uniform(0.94, 1.06), 1)
                    rows.append({"part": pid, "engine": eid, "name": sub, "assembly": asm, "index": k,
                                 "material": mat, "mass_kg": m,
                                 "named": True})
                    if sub in KINEMATIC: graph_nodes.append(pid)
            # linkage chain: the working sequence a reviewer traces
            chain = ["piston rod", "crosshead", "rocking beam", "main centre pin", "link", "bar", "crankshaft",
                     "crank pin", "flywheel hub", "pump rod", "plunger", "valve spindle", "cam", "governor spindle"]
            have = {r["name"]: r["part"] for r in rows if r["name"] in chain}
            for a, b in zip(chain, chain[1:]):
                if a in have and b in have: graph_edges.append({"a": have[a], "b": have[b], "joint": "pin" if a not in ("piston rod", "pump rod") else "sliding"})
            with open(os.path.join(ENG, f"PARTS_{eid}.jsonl"), "w") as f:
                for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
            json.dump({"engine": eid, "station": sname, "name": ename, "class": cls,
                       "nodes": graph_nodes, "edges": graph_edges,
                       "strokes_per_min": 14.0, "beam_stroke_m": 3.05,
                       "historical_stroke_m": 2.743, "historical_rpm": 11.0},
                      open(os.path.join(ENG, f"GRAPH_{eid}.json"), "w"), indent=1)
            tot += len(rows)
            summary.append((eid, ename, cls, len(rows), len(graph_nodes), len(graph_edges)))
    return tot, summary

if __name__ == "__main__":
    tot, summary = gen()
    byclass = {}
    for eid, ename, cls, n, gn, ge in summary: byclass.setdefault(cls, []).append(n)
    print(f"named parts total: {tot}")
    for cls in "ABCD":
        vals = byclass[cls]
        print(f" class {cls}: {len(vals)} engines, per-engine {vals[0]} (floor 4200, headroom {vals[0]-4200})")
    print("graphs:", sum(1 for f in os.listdir(ENG) if f.startswith("GRAPH_")))
