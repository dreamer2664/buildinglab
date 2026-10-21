#!/usr/bin/env python3
"""HYDRAULICS.jsonl — dry-weather flow depth per reach, solved by Manning on the REAL section.

G7: every interior view's flow depth equals its catchment ledger row. The row is computed, not
composed: population -> allowance (R-094) -> discharge -> Manning depth on the declared profile
at the declared gradient (INVERTS.jsonl) -> velocity, checked against the self-cleansing floor
(R-016, R-017). A water surface that disagrees with this file fails G7.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lines import PROFILES, LINES
from section import section

LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LED  = os.path.join(LANE, "ledgers")

GAL_PER_HEAD_DAY = 25.0            # R-094 Bazalgette's allowance, imperial gallons
GAL_TO_M3        = 0.00454609
N_BRICK_CEMENT   = 0.013           # Manning n, brickwork in Portland cement mortar (R-040)
SELF_CLEANSE_MS  = 0.67            # R-016: >=1.5 mph half full
CATCHMENT_POP = {"N-high": 900000, "N-mid": 750000, "N-low": 450000,
                 "S-high": 400000, "S-low": 300000}   # sums to the ~2.8M of R-094

def wetted(pid, p, depth, nsamp=600):
    """A(d) [m2] and P(d) [m] on the true section, by walking the inner perimeter polyline."""
    pts, cum, per = section(pid, p)
    # collect boundary points below the water surface, ordered
    xs, zs, ss = [], [], []
    for i, (y, z) in enumerate(pts):
        if z <= depth + 1e-9:
            xs.append(y); zs.append(z); ss.append(cum[i])
    if len(xs) < 2: return 0.0, 0.0
    # wetted perimeter = arc length along the boundary below the surface
    P = 0.0
    for i in range(1, len(ss)):
        if ss[i] - ss[i-1] < per / 2:            # skip the wrap across the crown
            P += math.hypot(xs[i]-xs[i-1], zs[i]-zs[i-1])
    # area by the shoelace on the waterline closure
    A = 0.0
    for i in range(len(xs)-1):
        A += (xs[i] + xs[i+1]) / 2.0 * (zs[i] - zs[i+1]) * -1.0
    A = abs(A)
    # trapezoid on (y,z) ordered along the boundary, closed by the waterline
    A2 = 0.0
    for i in range(len(xs)-1):
        A2 += xs[i]*zs[i+1] - xs[i+1]*zs[i]
    A2 = abs(A2)/2.0
    return A2, P

def solve_depth(Q, S, pid, p, lo=0.005, hi=None):
    """Depth whose Manning discharge equals Q at gradient S. Bisection on a monotone A*R^(2/3)."""
    hi = hi or p["height_m"] * 0.95
    def q_at(d):
        A, P = wetted(pid, p, d)
        if A <= 0 or P <= 0: return 0.0
        R = A / P
        return (1.0 / N_BRICK_CEMENT) * A * R ** (2.0/3.0) * math.sqrt(S)
    if q_at(hi) < Q: return hi, q_at(hi), True
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if q_at(mid) < Q: lo = mid
        else: hi = mid
    d = 0.5*(lo+hi); A, P = wetted(pid, p, d)
    return d, Q, False

def main():
    inv = [json.loads(l) for l in open(os.path.join(LED, "INVERTS.jsonl")) if l.strip()]
    out, capped = [], []
    for lid, name, km, fmpk, z0, segs, basis in LINES:
        pop = CATCHMENT_POP[lid]
        Q = pop * GAL_PER_HEAD_DAY * GAL_TO_M3 / 86400.0
        rows = [r for r in inv if r["line"] == lid]
        S = fmpk / 1000.0
        for r in rows:
            p = PROFILES[r["profile"]]
            d, q, cap = solve_depth(Q, S, r["profile"], p)
            A, P = wetted(r["profile"], p, d)
            v = (Q / A) if A > 0 else 0.0
            # R-016 states the self-cleansing floor "when half full": evaluate the reference
            # condition as published, alongside the dry-weather condition actually rendered.
            Ah, Ph = wetted(r["profile"], p, p["height_m"] / 2.0)
            Rh = (Ah / Ph) if Ph else 0.0
            v_half = (1.0 / N_BRICK_CEMENT) * Rh ** (2.0/3.0) * math.sqrt(S)
            Q_half = v_half * Ah
            row = {"chunk": r["chunk"], "line": lid, "station_m": r["station_m"],
                   "profile": r["profile"], "catchment_population": pop,
                   "allowance_gal_per_head_day": GAL_PER_HEAD_DAY,
                   "dwf_m3_per_day": round(pop * GAL_PER_HEAD_DAY * GAL_TO_M3, 1),
                   "dwf_m3_per_s": round(Q, 4), "gradient_m_per_m": S,
                   "manning_n": N_BRICK_CEMENT,
                   "depth_m": round(d, 4), "wetted_area_m2": round(A, 4),
                   "wetted_perimeter_m": round(P, 4),
                   "hydraulic_radius_m": round(A/P, 4) if P else 0.0,
                   "velocity_m_per_s": round(v, 4),
                   "velocity_half_full_m_per_s": round(v_half, 4),
                   "discharge_half_full_m3_per_s": round(Q_half, 4),
                   "self_cleansing_half_full": bool(v_half >= SELF_CLEANSE_MS),
                   "self_cleansing": bool(v >= SELF_CLEANSE_MS),
                   "section_full": bool(cap), "invert_in_m": r["invert_in_m"],
                   "water_surface_m": round(r["invert_in_m"] + d, 4),
                   "cites": ["R-094", "R-016", "R-017", "R-040", "R-012"]}
            out.append(row)
            if cap: capped.append(r["chunk"])
            if not row["self_cleansing"]: capped.append("SC:"+r["chunk"])
    with open(os.path.join(LED, "HYDRAULICS.jsonl"), "w") as f:
        for r in out: f.write(json.dumps(r, sort_keys=True) + "\n")
    d0 = out[0]
    print(f"HYDRAULICS.jsonl rows: {len(out)}")
    for lid in CATCHMENT_POP:
        rows = [r for r in out if r["line"] == lid]
        print(f"  {lid:7s} pop {rows[0]['catchment_population']:>9,} DWF {rows[0]['dwf_m3_per_s']:.3f} m3/s "
              f"S=1:{1/rows[0]['gradient_m_per_m']:.0f} depth {min(r['depth_m'] for r in rows):.3f}-{max(r['depth_m'] for r in rows):.3f} m "
              f"v {min(r['velocity_m_per_s'] for r in rows):.2f}-{max(r['velocity_m_per_s'] for r in rows):.2f} m/s "
              f"self-cleansing {all(r['self_cleansing'] for r in rows)}")
    print(f"  section-full (capacity-limited) chunks: {len([c for c in capped if not c.startswith('SC')])}")
    print(f"  below self-cleansing floor: {len([c for c in capped if c.startswith('SC')])}")
    if capped[:6]: print("  first exceptions:", capped[:6])
if __name__ == "__main__": main()
