#!/usr/bin/env python3
"""The brick layer. R5: the ledger is generated FIRST and the bricks are laid FROM it.

Deterministic: (chunk key, seed, profile row, gradient row) -> rows, in canonical order
(wythe, course, position). A hand-placed brick does not exist here; there is no code path
that adds one. Positions are integer millimetres, deviations integer tenths of a millimetre,
so a rebuild from the same ledger row is bit-for-bit identical (G13 reproduction gate).
"""
import hashlib, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lines import PROFILES
from section import point_at, perimeter
from profile import BRICK, JOINT

LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LED  = os.path.join(LANE, "ledgers")
EV   = os.path.join(LANE, "evidence")

MOD_C = BRICK["L"] + JOINT      # 239 mm circumferential
MOD_A = BRICK["H"] + JOINT      #  86 mm axial (course height)
WYTHE = BRICK["W"]              # 114 mm radial per wythe

def index_row(chunk):
    with open(os.path.join(LED, "INDEX.jsonl")) as f:
        for ln in f:
            r = json.loads(ln)
            if r["chunk"] == chunk: return r
    raise SystemExit(f"no INDEX row for {chunk} (orphan chunk is a defect, §1.6)")

def deviation_set(row):
    """Per-chunk deviation set, seeded from the chunk key (F35: no two chunks are twins)."""
    rng = random.Random(int(row["key"][:16], 16))
    return {"chunk": row["chunk"], "key": row["key"],
            "stain_density":  round(rng.uniform(0.55, 1.45), 4),
            "bloom_density":  round(rng.uniform(0.60, 1.40), 4),
            "repair_clusters": rng.randint(1, 7),
            "sediment_mm":    rng.randint(6, 55),
            "tide_mark_m":    round(rng.uniform(0.30, 1.05), 3),
            "soot_bands":     rng.randint(0, 4),
            "tool_scar_bias": round(rng.uniform(-0.4, 0.4), 3),
            "settlement_zone": [rng.randint(0, 900), rng.randint(60, 300)],
            "grit_seed":      rng.randint(0, 2**31 - 1),
            "colour_drift":   round(rng.uniform(-0.06, 0.06), 4),
            "bond_offset_mm": rng.choice([0, 60, 119, 180])}

def condition(rng, zone, dev, y_frac):
    """Seeded condition code from the wear schedule; zone rates +/-25% per chunk."""
    r = rng.random()
    j = 1.0 + dev["tool_scar_bias"]
    if zone == "invert":
        if r < 0.09 * dev["stain_density"]: return 4
        if r < 0.13 * dev["stain_density"]: return 2
    elif zone == "crown":
        if r < 0.07 * dev["bloom_density"]: return 1
        if r < 0.076 * dev["bloom_density"]: return 7
    elif zone == "wall":
        if r < 0.012 * dev["stain_density"]: return 3
        if r < 0.042 * dev["stain_density"]: return 2
        if r < 0.042 + 0.02 * j: return 6
        if r < 0.072 * dev["stain_density"]: return 5
    elif zone in ("splash", "flow"):
        if r < 0.07 * dev["bloom_density"]: return 1
        if r < 0.09 * dev["stain_density"]: return 2
    return 0

def zone_of(z, height, dwf_depth):
    if z <= 0.15: return "invert"
    if z <= dwf_depth: return "flow"
    if z <= dwf_depth + 0.45: return "splash"
    if z <= height * 0.52: return "wall"      # springing of the ovoid is at 25% of height
    return "crown"

def lay(chunk, out=None, density=1.0, dwf_depth=0.28):
    row = index_row(chunk)
    pid = row["profile"]; p = PROFILES[pid]
    dev = deviation_set(row)
    per_in = perimeter(pid, p)
    wythes = row["wythes"]
    rng = random.Random(int(row["seed"][:16], 16) ^ 0xC10ACA)
    courses = row["bricks_predicted"]  # recomputed below; kept for the assert
    # ---- geometry counts, recomputed here (never declared) ----
    ring_thk = wythes * WYTHE
    from section import offset_perimeter
    pmid = offset_perimeter(pid, p, ring_thk / 2.0)
    n_full = int(math.floor(pmid / MOD_C)); gap = pmid - n_full * MOD_C
    per_course = n_full + 1                                  # + closure brick (C-006)
    n_courses = int(math.floor(100.0 / MOD_A))
    total = n_courses * per_course * wythes
    assert total == courses, f"census recomputation disagrees with INDEX for {chunk}: {total} vs {courses}"
    # ---- proxy density (R2): thin the courses, never the deviations ----
    c_step = 1 if density >= 1.0 else max(1, int(round(1.0 / density)))
    # repairs cluster: pick cluster centres along the chainage
    clusters = [(rng.randint(0, n_courses - 1), rng.randint(8, 40)) for _ in range(dev["repair_clusters"])]
    rows, ukeys = [], []
    band_rows = {}
    for c in range(0, n_courses, c_step):
        x = c * MOD_A + BRICK["H"] / 2.0
        bond = (dev["bond_offset_mm"] / 1000.0) if (c % 2 == 0) else ((dev["bond_offset_mm"] / 1000.0) + MOD_C / 2.0)
        for w in range(wythes):
            off = (w + 0.5) * WYTHE
            for j in range(per_course):
                s = (j * MOD_C + bond) % per_in
                cut = (j == per_course - 1)
                s_mid = (s + (gap / 2.0 if cut else MOD_C / 2.0)) % per_in
                y0, z0, nd = point_at(pid, p, s_mid)
                a = math.radians(nd)
                # seeded deviations: position +/-2 mm (axial, circumferential, radial), dims +/-2 mm
                dx = rng.randint(-20, 20) / 10.0; ds = rng.randint(-20, 20) / 10.0; dr = rng.randint(-20, 20) / 10.0
                dl = rng.randint(-20, 20) / 10.0; dw = rng.randint(-20, 20) / 10.0; dh = rng.randint(-20, 20) / 10.0
                yy, zz, nd2 = point_at(pid, p, (s_mid + ds / 1000.0) % per_in)
                a2 = math.radians(nd2)
                ro = off + dr / 1000.0
                y = yy + ro * math.cos(a2); z = zz + ro * math.sin(a2)
                zz_rel = z                                     # z above the invert (invert at z=0)
                zone = zone_of(zz_rel, p["height_m"], dwf_depth)
                cond = condition(rng, zone, dev, zz_rel / p["height_m"])
                in_cluster = any(abs(c - cc) < ln for cc, ln in clusters)
                if in_cluster and cond == 0 and rng.random() < 0.35: cond = 3
                bl = MOD_C + (gap if cut else 0.0)
                u = hashlib.sha256(f"{row['key']}|{w}|{c}|{j}".encode()).hexdigest()[:16]
                rec = {"u": u, "w": w, "c": c, "j": j,
                       "x": int(round((x + dx / 1000.0) * 1000)),
                       "y": int(round(y * 1000)), "z": int(round(z * 1000)),
                       "r": int(round(nd2 * 100)),
                       "d": [int(round(dl)), int(round(dw)), int(round(dh))],
                       "l": int(round(bl * 1000)), "g": rng.randint(0, 255), "k": cond,
                       "z_": zone}
                rows.append(rec); ukeys.append((w, c, j, u))
                band = c // 100
                band_rows[band] = band_rows.get(band, 0) + 1
    u_hash = hashlib.sha256("\n".join(u for _,_,_,u in sorted(ukeys)).encode()).hexdigest()
    xs = [r["x"] for r in rows]; ys = [r["y"] for r in rows]; zs = [r["z"] for r in rows]
    meta = {"chunk": chunk, "key": row["key"], "profile": pid, "wythes": wythes,
            "courses": n_courses, "bricks_per_course": per_course, "closure_gap_mm": round(gap * 1000, 1),
            "mid_perimeter_mm": int(round(pmid * 1000)), "inner_perimeter_mm": int(round(per_in * 1000)),
            "census": len(rows), "predicted_census": total, "density": density,
            "u_hash": u_hash,
            "bounds_mm": {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)], "z": [min(zs), max(zs)]},
            "deviation_set": dev,
            "condition_histogram": {str(k): sum(1 for r in rows if r["k"] == k) for k in range(8)},
            "zone_histogram": {z: sum(1 for r in rows if r["z_"] == z) for z in ("invert","flow","splash","wall","crown")},
            "bands": {f"band_{b:02d}": n for b, n in sorted(band_rows.items())}}
    os.makedirs(os.path.join(LED, "BRICKS"), exist_ok=True); os.makedirs(EV, exist_ok=True)
    out = out or os.path.join(LED, "BRICKS", f"{chunk}.jsonl")
    with open(out, "w") as f:
        for r in rows: f.write(json.dumps(r, separators=(",", ":")) + "\n")
    os.makedirs(os.path.join(EV, "CENSUS"), exist_ok=True)
    tag = "" if density >= 1.0 else "_PROXY"
    json.dump(meta, open(os.path.join(EV, "CENSUS", f"{chunk}{tag}_LEDGER.json"), "w"), indent=1, sort_keys=True)
    with open(os.path.join(LED, "DEVIATIONS.jsonl"), "a") as f:
        f.write(json.dumps(dev, sort_keys=True) + "\n")
    return meta

if __name__ == "__main__":
    import argparse, time
    ap = argparse.ArgumentParser()
    ap.add_argument("chunk"); ap.add_argument("--density", type=float, default=1.0)
    ap.add_argument("--dwf-depth", type=float, default=0.28)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    t0 = time.time(); m = lay(a.chunk, out=a.out, density=a.density, dwf_depth=a.dwf_depth)
    sz = os.path.getsize(a.out or os.path.join(LED, "BRICKS", f"{a.chunk}.jsonl"))
    print(f"{a.chunk}: census {m['census']:,} (predicted {m['predicted_census']:,}) · courses {m['courses']} · "
          f"{m['bricks_per_course']}/course · closure gap {m['closure_gap_mm']} mm · u_hash {m['u_hash'][:16]}…")
    print(f"  ledger {sz/1e6:.2f} MB · {sz/max(1,m['census']):.0f} B/row · {time.time()-t0:.1f} s · density {a.density}")
    print(f"  conditions {m['condition_histogram']}")
    print(f"  zones      {m['zone_histogram']}")
