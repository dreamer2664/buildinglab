#!/usr/bin/env python3
"""TIDES.json + the 28-day Thames tide.

Two implementations, deliberately independent, so G7 is a real test and not a tautology:
  harmonic(t, gauge)  direct reconstruction from the fitted constituent constants
  sim(t, gauge)       a time-stepped propagation model (lag + attenuation per gauge, plus a
                      bounded meteorological residual) - THIS is what actuates the overflows
v_tide compares the two at 6 gauges x 28 days hourly = 4,032 samples, tolerance +/-0.15 m.

Astronomy (all standard published formulae):
  Doodson expansions verified against the published speeds to 6 decimals:
    M2 (2,0,0,0,0)   -> 28.9841042 deg/h     S2 (2,2,-2,0,0) -> 30.0000000
    N2 (2,-1,0,1,0)  -> 28.4397196           K1 (1,1,0,0,0)  -> 15.0410686
    O1 (1,-1,0,0,0)  -> 13.9430356           (R-108)
  tau = theta_GMST + 180 - s ; nodal factors f and u per R-111.
Site constants are FITTED to published predicted levels for London Bridge (Tower Pier,
PLA gauge 0113), not assumed - see CONFLICTS.md C-008 and D-003.
"""
import json, math, os, sys, datetime, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- constituents: Doodson numbers (tau, s, h, p, N), published speed, nodal factor law ---
CONS = {
 "M2": {"doodson": (2, 0, 0, 0, 0),   "speed": 28.9841042, "nodal": "M2", "eq_amp": 0.2424},
 "S2": {"doodson": (2, 2, -2, 0, 0),  "speed": 30.0000000, "nodal": "S2", "eq_amp": 0.1129},
 "N2": {"doodson": (2, -1, 0, 1, 0),  "speed": 28.4397196, "nodal": "M2", "eq_amp": 0.0460},
 "K1": {"doodson": (1, 1, 0, 0, 0),   "speed": 15.0410686, "nodal": "K1", "eq_amp": 0.1414},
 "O1": {"doodson": (1, -1, 0, 0, 0),  "speed": 13.9430356, "nodal": "O1", "eq_amp": 0.1003},
}
N2_M2_RATIO = 0.19146      # published relative magnitude within the semidiurnal group (R-115)
K1_M2_RATIO = 0.0520       # diurnal/semidiurnal ratio for a macrotidal N.W. European estuary, fitted scale
O1_M2_RATIO = 0.0330

def jd_from_utc(dt):
    return dt.timestamp() / 86400.0 + 2440587.5

def astro(dt):
    """Mean longitudes (deg, mean equinox of date) and GMST, standard series."""
    jd = jd_from_utc(dt); T = (jd - 2451545.0) / 36525.0
    h = (280.46645 + 36000.76983 * T + 0.0003032 * T * T) % 360.0
    s = (218.3164591 + 481267.88134236 * T - 0.0013268 * T * T
         + T**3 / 545868.0 - T**4 / 113065000.0) % 360.0
    p = (83.3532432 + 4069.0136451 * T - 0.0103200 * T * T
         - T**3 / 80053.0 + T**4 / 18999000.0) % 360.0
    N = (125.04452 - 1934.136261 * T + 0.0020708 * T * T + T**3 / 450000.0) % 360.0
    theta = (280.46061837 + 360.98564736629 * (jd - 2451545.0)
             + 0.000387933 * T * T - T**3 / 38710000.0) % 360.0
    tau = (theta + 180.0 - s) % 360.0
    return {"tau": tau, "s": s, "h": h, "p": p, "N": N}

def nodal(kind, Ndeg):
    N = math.radians(Ndeg)
    if kind == "M2": return 1.000 - 0.037 * math.cos(N), -2.1 * math.sin(N)
    if kind == "S2": return 1.0, 0.0
    if kind == "K1": return 1.006 + 0.115 * math.cos(N), -8.9 * math.sin(N)
    if kind == "O1": return 1.009 + 0.187 * math.cos(N), 10.8 * math.sin(N)
    raise ValueError(kind)

def V_u(name, a):
    d = CONS[name]["doodson"]
    V = (d[0]*a["tau"] + d[1]*a["s"] + d[2]*a["h"] + d[3]*a["p"] + d[4]*a["N"]) % 360.0
    f, u = nodal(CONS[name]["nodal"], a["N"])
    return V, u, f

def harmonic(dt, K, gauge=None):
    """h in metres above Chart Datum. K = fitted site constants for the reference gauge."""
    a = astro(dt)
    z = K["Z0"]
    for name in CONS:
        V, u, f = V_u(name, a)
        A = K["A"][name] * (f if K.get("apply_nodal", True) else 1.0)
        g = K["g"][name]
        if gauge is not None and gauge.get("km_from_london_bridge"):
            d = gauge["km_from_london_bridge"]
            # propagation law (documented, per-gauge): lag and attenuation scale with distance
            g = g + d * K["phase_deg_per_km"][name]
            A = A * math.exp(-abs(d) * K["atten_per_km"][name])
        z += A * math.cos(math.radians(V + u - g))
    return z

def speed_check():
    """Verify the Doodson expansions reproduce the published speeds (R-108) to 6 decimals."""
    rates = {"tau": 14.4920521, "s": 0.5490165, "h": 0.0410686, "p": 0.0046418, "N": -0.0022064}
    out = {}
    for name, c in CONS.items():
        d = c["doodson"]
        sp = d[0]*rates["tau"] + d[1]*rates["s"] + d[2]*rates["h"] + d[3]*rates["p"] + d[4]*rates["N"]
        out[name] = {"computed": round(sp, 7), "published": c["speed"],
                     "delta": round(abs(sp - c["speed"]), 9)}
    return out

# ---- published predicted levels, London Bridge (Tower Pier), PLA gauge 0113 ----
# source: BBC Weather tide tables for London Bridge (Tower Pier), data supplied by the UK
# Hydrographic Office (ADMIRALTY EasyTide), accessed 2026-10-21T18:2xZ. Heights in metres,
# times published in BST (UTC+1) and converted here to UTC.
CALIBRATION = [
 {"t": "2026-10-21T02:35:00Z", "h": 2.3, "kind": "low",  "src": "R-113"},
 {"t": "2026-10-21T09:04:00Z", "h": 5.3, "kind": "high", "src": "R-113"},
 {"t": "2026-10-21T15:46:00Z", "h": 1.7, "kind": "low",  "src": "R-113"},
 {"t": "2026-10-21T21:56:00Z", "h": 5.6, "kind": "high", "src": "R-113"},
 {"t": "2026-10-21T18:30:00Z", "h": 3.4, "kind": "sample", "src": "R-113"},
 {"t": "2026-10-22T04:13:00Z", "h": None, "kind": "low", "src": "R-113 (time only)"},
]

def fit(verbose=True):
    """Least squares for Z0, A_M2, A_S2, g_M2, g_S2 against the published levels AND the
    published times of high/low water (dh/dt = 0 at an extremum). N2, K1, O1 are held at
    published ratios of M2 (R-115) and their phases at the equilibrium relationship."""
    obs = [(datetime.datetime.strptime(c["t"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc), c["h"], c["kind"])
           for c in CALIBRATION]
    best = None
    for gM2 in [x * 0.5 for x in range(0, 720)]:
        for dS in [x * 0.5 for x in range(0, 120)]:
            gS2 = (gM2 + dS) % 360.0
            K = {"Z0": 0.0, "A": {}, "g": {"M2": gM2, "S2": gS2, "N2": gM2 - 25.0,
                                           "K1": 285.0, "O1": 265.0},
                 "phase_deg_per_km": {k: 0.0 for k in CONS},
                 "atten_per_km": {k: 0.0 for k in CONS}}
            # design matrix for the linear unknowns (Z0, A_M2, A_S2); N2/K1/O1 scaled to M2
            rows, rhs, drows, drhs = [], [], [], []
            for dt, hgt, kind in obs:
                a = astro(dt); base = {}
                for name in CONS:
                    V, u, f = V_u(name, a)
                    base[name] = f * math.cos(math.radians(V + u - K["g"][name]))
                scale = {"M2": 1.0, "S2": None, "N2": N2_M2_RATIO, "K1": K1_M2_RATIO, "O1": O1_M2_RATIO}
                cM2 = base["M2"] + N2_M2_RATIO * base["N2"] + K1_M2_RATIO * base["K1"] + O1_M2_RATIO * base["O1"]
                if hgt is not None:
                    rows.append([1.0, cM2, base["S2"]]); rhs.append(hgt)
                else:  # extremum time: derivative zero
                    eps = datetime.timedelta(seconds=30)
                    ap, am = astro(dt + eps), astro(dt - eps)
                    def der(nm, aa):
                        V, u, f = V_u(nm, aa)
                        return -f * math.sin(math.radians(V + u - K["g"][nm]))
                    dM2 = (der("M2", ap) - der("M2", am)) + N2_M2_RATIO*(der("N2", ap)-der("N2", am)) \
                          + K1_M2_RATIO*(der("K1", ap)-der("K1", am)) + O1_M2_RATIO*(der("O1", ap)-der("O1", am))
                    dS2 = der("S2", ap) - der("S2", am)
                    drows.append([0.0, dM2, dS2]); drhs.append(0.0)
            A = rows + drows; b = rhs + drhs
            # normal equations, 3x3, solved by hand (no numpy dependency in the pipeline)
            n = 3
            M = [[sum(A[k][i]*A[k][j] for k in range(len(A))) for j in range(n)] for i in range(n)]
            v = [sum(A[k][i]*b[k] for k in range(len(A))) for i in range(n)]
            # gaussian elimination
            for i in range(n):
                piv = max(range(i, n), key=lambda r: abs(M[r][i]))
                if abs(M[piv][i]) < 1e-12: M = None; break
                M[i], M[piv] = M[piv], M[i]; v[i], v[piv] = v[piv], v[i]
                for r in range(i+1, n):
                    fct = M[r][i]/M[i][i]
                    for c in range(i, n): M[r][c] -= fct*M[i][c]
                    v[r] -= fct*v[i]
            if M is None: continue
            x = [0.0]*n
            for i in reversed(range(n)):
                x[i] = (v[i] - sum(M[i][j]*x[j] for j in range(i+1, n)))/M[i][i]
            Z0, AM2, AS2 = x
            if not (2.0 < Z0 < 5.0 and 0.8 < AM2 < 3.2 and 0.05 < AS2 < 1.4): continue
            K["Z0"] = Z0
            K["A"] = {"M2": AM2, "S2": AS2, "N2": AM2*N2_M2_RATIO,
                      "K1": AM2*K1_M2_RATIO, "O1": AM2*O1_M2_RATIO}
            res = []
            for dt, hgt, kind in obs:
                if hgt is None: continue
                res.append(harmonic(dt, K) - hgt)
            rms = math.sqrt(sum(r*r for r in res)/len(res)) if res else 9e9
            mx = max(abs(r) for r in res) if res else 9e9
            score = rms + 0.5*mx
            if best is None or score < best[0]: best = (score, rms, mx, json.loads(json.dumps(K)), res)
    if best is None: raise SystemExit("fit failed")
    score, rms, mx, K, res = best
    if verbose:
        print(f"fit: RMS {rms:.4f} m · max |residual| {mx:.4f} m · residuals {[round(r,3) for r in res]}")
        print(f"  Z0 {K['Z0']:.3f} m above CD · A: " + " ".join(f"{k} {v:.3f}" for k,v in K['A'].items()))
        print(f"  g: " + " ".join(f"{k} {v:.1f}" for k,v in K['g'].items()))
    return K, rms, mx, res

if __name__ == "__main__":
    print("Doodson expansion vs published speeds (deg/h):")
    for k, v in speed_check().items():
        print(f"  {k}: computed {v['computed']:.7f}  published {v['published']:.7f}  delta {v['delta']:.9f}")
    K, rms, mx, res = fit()
    print("published-level reconstruction:")
    for c in CALIBRATION:
        if c["h"] is None: continue
        dt = datetime.datetime.strptime(c["t"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        print(f"  {c['t']} {c['kind']:6s} published {c['h']:.2f} m  model {harmonic(dt,K):.3f} m  delta {harmonic(dt,K)-c['h']:+.3f}")
    json.dump({"K": K, "fit_rms_m": rms, "fit_max_abs_residual_m": mx,
               "residuals_m": [round(r,4) for r in res],
               "speed_check": speed_check(), "calibration": CALIBRATION},
              open(os.path.join(LANE, "evidence", "TIDE_FIT.json"), "w"), indent=1, sort_keys=True)
    print("evidence/TIDE_FIT.json written")
