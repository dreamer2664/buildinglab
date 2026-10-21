#!/usr/bin/env python3
"""INVERTS.jsonl + INDEX.jsonl — the whole network's gradient and keys, computed once.

G3: continuous fall at all 1,319 joins, zero uphill metres, declared fall per line within tolerance.
R1: chunk_key = sha256(GEN_VERSION || seed || profile_row_json || gradient_row_json)
Arithmetic is integer millimetres so continuity is exact, not near-exact.
"""
import hashlib, json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from lines import GEN_VERSION, MASTER_SEED, LINES, PROFILES, STATIONS, OVERFLOWS
from profile import course_geometry, chunk_census

LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LED  = os.path.join(LANE, "ledgers")
os.makedirs(LED, exist_ok=True)

def seed_for(chunk_id):
    return hashlib.sha256(f"{MASTER_SEED}|{chunk_id}".encode()).hexdigest()[:32]

def profile_for(line_segs, idx):
    for a, b, pid in line_segs:
        if a <= idx <= b: return pid
    raise ValueError(f"no profile segment covers chunk {idx}")

def falls_mm(n, total_mm, nom_mm, lo=0.6, hi=1.4):
    """Seeded per-chunk falls in mm: each inside [lo,hi] x nominal, all > 0, summing exactly to total_mm."""
    rng = random.Random(hashlib.sha256(f"falls|{n}|{total_mm}|{nom_mm}".encode()).hexdigest())
    f = [max(1, int(round(nom_mm * (lo + (hi - lo) * rng.random())))) for _ in range(n)]
    lo_i, hi_i = int(round(nom_mm * lo)), int(round(nom_mm * hi))
    f = [min(max(x, lo_i), hi_i) for x in f]
    resid = total_mm - sum(f)
    step = 1 if resid > 0 else -1
    i = 0
    while resid != 0 and i < 200 * n:
        j = i % n
        if (step > 0 and f[j] < hi_i) or (step < 0 and f[j] > lo_i):
            f[j] += step; resid -= step
        i += 1
    assert sum(f) == total_mm and all(x > 0 for x in f), "gradient law broken"
    return f

def main():
    inv_rows, idx_rows, gidx = [], [], 0
    per_line = {}
    for lid, name, km, fmpk, z0, segs, basis in LINES:
        n = int(round(km * 10))
        total_mm = int(round(fmpk * km * 1000.0))
        nom_mm = total_mm / n
        f = falls_mm(n, total_mm, nom_mm)
        zin = int(round(z0 * 1000))
        for i in range(n):
            cid = f"S{gidx:04d}"
            pid = profile_for(segs, i)
            p = PROFILES[pid]
            cg = chunk_census(100.0, p["kind"], p["wythes"], pid=pid, prof=p,
                              **({"r": p["r"]} if p["kind"] == "ovoid" else
                                 {"d": p["d"]} if p["kind"] == "circle" else {"h": p["h"], "w": p["w"]}))
            zout = zin - f[i]
            grad_row = {"chunk": cid, "line": lid, "idx": i, "station_in_m": round(gidx * 100.0, 1) if False else round(i * 100.0, 1),
                        "invert_in_mm": zin, "invert_out_mm": zout, "fall_mm": f[i]}
            sd = seed_for(cid)
            key = hashlib.sha256(("\n".join([GEN_VERSION, sd, json.dumps(p, sort_keys=True),
                                             json.dumps(grad_row, sort_keys=True)])).encode()).hexdigest()
            stn = [k for k, v in STATIONS.items() if v["line"] == lid and v["chunk"] == i]
            ofs = [o["id"] for o in OVERFLOWS if o["line"] == lid and o["chunk"] == i]
            inv_rows.append({"chunk": cid, "line": lid, "idx": i, "station_m": round(i * 100.0, 1),
                             "invert_in_m": round(zin / 1000.0, 3), "invert_out_m": round(zout / 1000.0, 3),
                             "fall_m": round(f[i] / 1000.0, 3), "fall_m_per_km": round(f[i] / 1000.0 * 10, 3),
                             "profile": pid, "wythes": p["wythes"], "ring_thickness_m": cg["ring_thickness_m"],
                             "courses": cg["courses"], "bricks_predicted": cg["census"],
                             "station_name": stn[0] if stn else None, "overflow": ofs or None})
            idx_rows.append({"row": gidx, "chunk": cid, "line": lid, "idx": i, "key": key, "seed": sd,
                             "generator": GEN_VERSION, "profile": pid, "wythes": p["wythes"],
                             "station_in_m": round(i * 100.0, 1), "station_out_m": round((i + 1) * 100.0, 1),
                             "invert_in_m": round(zin / 1000.0, 3), "invert_out_m": round(zout / 1000.0, 3),
                             "bricks_predicted": cg["census"], "sha256": None, "state": "keyed",
                             "chunk_file": None, "census": None, "built_ts": None,
                             "station_name": stn[0] if stn else None, "overflow": ofs or None})
            zin = zout; gidx += 1
        per_line[lid] = {"chunks": n, "length_km": km, "declared_fall_m_per_km": fmpk,
                         "total_fall_m": round(total_mm / 1000.0, 3),
                         "invert_start_m": round(z0, 3), "invert_end_m": round(zin / 1000.0, 3),
                         "realised_fall_m_per_km": round(total_mm / 1000.0 / km, 4), "basis": basis}
    with open(os.path.join(LED, "INVERTS.jsonl"), "w") as fh:
        for r in inv_rows: fh.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(LED, "INDEX.jsonl"), "w") as fh:
        for r in idx_rows: fh.write(json.dumps(r, sort_keys=True) + "\n")
    prof = {"generator_version": GEN_VERSION, "master_seed": MASTER_SEED,
            "brick": {"L_mm": 229, "W_mm": 114, "H_mm": 76, "joint_mm": 10, "cites": ["R-041", "R-042"]},
            "ring": {"wythe_mm": 114, "cites": ["R-043"], "adjudication": "C-006 closure brick per course"},
            "profiles": PROFILES, "lines": per_line,
            "line_order": [l[0] for l in LINES],
            "stations": STATIONS, "overflows": OVERFLOWS, "gauges": None,
            "cites": ["R-012", "R-013", "R-014", "R-015", "R-022", "R-142", "C-002", "C-012"]}
    json.dump(prof, open(os.path.join(LANE, "PROFILE.json"), "w"), indent=1, sort_keys=True)
    tot_bricks = sum(r["bricks_predicted"] for r in inv_rows)
    print(f"INVERTS.jsonl rows : {len(inv_rows)}")
    print(f"INDEX.jsonl rows   : {len(idx_rows)}  (all keyed, sha256 pending build)")
    print(f"network length     : {sum(l['length_km'] for l in per_line.values()):.1f} km")
    print(f"predicted census   : {tot_bricks:,} bricks  (floor 61,000,000 -> {'PASS' if tot_bricks>=61_000_000 else 'FAIL'})")
    for lid, d in per_line.items():
        print(f"  {lid:7s} {d['chunks']:4d} chunks  {d['invert_start_m']:6.2f} -> {d['invert_end_m']:6.2f} m  "
              f"fall {d['realised_fall_m_per_km']:.3f} m/km (declared {d['declared_fall_m_per_km']:.2f})")
    json.dump(per_line, open(os.path.join(LANE, "evidence", "LINES.json"), "w"), indent=1, sort_keys=True)
if __name__ == "__main__": main()
