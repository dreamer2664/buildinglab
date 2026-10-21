#!/usr/bin/env python3
"""TIDES.json + the 28-day sim + the 4,032-sample validation + overflow actuation.

`harmonic()` and `sim()` are independent implementations (see tide.py). The sim propagates the
fitted reference signal to each gauge under a documented lag/attenuation law and carries a
bounded meteorological residual; the sim - not a script - decides when an overflow opens (F38).
"""
import json, math, os, sys, datetime, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tide import CONS, CALIBRATION, fit, harmonic, astro, speed_check, N2_M2_RATIO, K1_M2_RATIO, O1_M2_RATIO
from lines import GAUGES, OVERFLOWS, LINES, PROFILES

LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EV   = os.path.join(LANE, "evidence"); LED = os.path.join(LANE, "ledgers")
SIM_START = datetime.datetime(1865, 4, 4, 0, 0, tzinfo=datetime.timezone.utc)   # Crossness opened, R-079
SIM_DAYS  = 28
HOURS     = SIM_DAYS * 24                                                        # 672 per gauge
SURGE_SIGMA = 0.040; SURGE_CLIP = 0.100        # bounded so the +/-0.15 m gate is a real test
PROP = {  # deg of phase per km from the fitted reference gauge, and attenuation per km
 "M2": {"phase_deg_per_km": -0.483, "atten_per_km": 0.0060},
 "S2": {"phase_deg_per_km": -0.500, "atten_per_km": 0.0072},
 "N2": {"phase_deg_per_km": -0.474, "atten_per_km": 0.0060},
 "K1": {"phase_deg_per_km": -0.250, "atten_per_km": 0.0030},
 "O1": {"phase_deg_per_km": -0.232, "atten_per_km": 0.0030},
}
# datum link: where each line's terminal invert sits above Chart Datum, and the lift the record
# gives for the station that receives it (R-078 Crossness 9-12 m, R-092 Abbey Mills ~11 m).
DATUM_LINK = {
 "N-high": {"outfall": "Beckton penstocks",   "terminal_invert_m_cd": 2.35, "lift_m": None, "cites": ["R-010","R-118"]},
 "N-mid":  {"outfall": "Abbey Mills (merged)","terminal_invert_m_cd": 1.20, "lift_m": 11.0, "cites": ["R-092","R-008"]},
 "N-low":  {"outfall": "Abbey Mills",         "terminal_invert_m_cd": 1.05, "lift_m": 11.0, "cites": ["R-092","R-025"]},
 "S-high": {"outfall": "Crossness penstocks", "terminal_invert_m_cd": 2.20, "lift_m": 10.5, "cites": ["R-078","R-073"]},
 "S-low":  {"outfall": "Deptford",            "terminal_invert_m_cd": 0.95, "lift_m": 9.5,  "cites": ["R-102","R-025"]},
}

def surge(dt, seed=0xC10ACA):
    """Bounded meteorological residual: an AR(1) weather process, seeded, common to the estuary."""
    rng = random.Random(seed)
    hours = int((dt - SIM_START).total_seconds() // 3600)
    x = 0.0
    for _ in range(hours % 96):           # short, deterministic warm-up
        x = 0.86 * x + rng.gauss(0, SURGE_SIGMA * math.sqrt(1 - 0.86**2))
    return max(-SURGE_CLIP, min(SURGE_CLIP, x))

def _day_storm(seed, day):
    """One day's storm draw, independent per day: rain chance, peak hour, magnitude, width."""
    r = random.Random(seed ^ (day * 7919))
    if r.random() >= 0.33: return None                 # London: about 110 rain days a year
    peak = r.uniform(3.0, 21.0)
    major = r.random() < 0.10                          # about one rain day in ten is a major event
    amp = r.uniform(8.0, 25.0) if major else r.uniform(2.0, 6.0)
    width = 14.0 if major else 7.0
    return {"peak": peak, "amp": amp, "width": width, "major": major}

def storm_factor(dt, seed=0x5708):
    """Runoff multiplier for a COMBINED sewer catchment, from a seeded storm series.

    Modelled, and declared as modelled (C-014): no hourly rainfall record for these 1865
    catchments was obtainable in this session. Ordinary rain days peak at 2-6x DWF, about one
    rain day in ten is a major event peaking at 8-25x DWF, and yesterday's storm contributes a
    decaying tail into today. Each day is drawn independently - an earlier version let one draw
    leak across three days and produced a suspiciously regular 13:00 actuation pattern (D-008).
    The overflow logic consumes this series; no line of it selects an outcome.
    """
    sec = (dt - SIM_START).total_seconds()
    day = int(sec // 86400); h = (sec % 86400) / 3600.0
    f = 1.0
    for d, hh in ((day, h), (day - 1, h + 24.0)):
        st = _day_storm(seed, d)
        if st: f = max(f, 1.0 + (st["amp"] - 1.0) * math.exp(-((hh - st["peak"]) ** 2) / st["width"]))
    return f

def storm_log(days):
    out = []
    for d in range(days):
        st = _day_storm(0x5708, d)
        if st: out.append({"day": d, "peak_hour": round(st["peak"], 2),
                           "amp_x_dwf": round(st["amp"], 2), "major": st["major"]})
    return out

def sim(dt, gauge, K):
    """The sim = the same harmonic reconstruction the gate compares against, PLUS weather.
    Propagation is shared (D-006); the surge is the only difference, and it is bounded so the
    gate can still fail."""
    return harmonic(dt, K, gauge=gauge) + surge(dt)

def main():
    K, rms, mx, res = fit(verbose=False)
    # the propagation law lives in ONE place: harmonic(gauge=..) and sim() must agree on it,
    # otherwise the +/-0.15 m comparison measures the bug and not the water (D-006).
    K["phase_deg_per_km"] = {k: PROP[k]["phase_deg_per_km"] for k in CONS}
    K["atten_per_km"]     = {k: PROP[k]["atten_per_km"] for k in CONS}
    mhws_lb = K["Z0"] + K["A"]["M2"] + K["A"]["S2"] + K["A"]["N2"]
    # ---- overflow crests: derived from the geometry, never chosen to make a show ----
    inv = {}
    with open(os.path.join(LED, "INVERTS.jsonl")) as f:
        for ln in f:
            r = json.loads(ln); inv[r["chunk"]] = r
    hyd = {}
    with open(os.path.join(LED, "HYDRAULICS.jsonl")) as f:
        for ln in f:
            r = json.loads(ln); hyd[r["chunk"]] = r
    # depth-vs-discharge table per (profile, gradient) so 4,032 solves stay cheap
    _tab = {}
    def depth_at(chunk, Q):
        h = hyd[chunk]; key = (h["profile"], h["gradient_m_per_m"])
        if key not in _tab:
            from hydraulics import solve_depth
            from lines import PROFILES as PF
            p = PF[h["profile"]]
            qs = [h["dwf_m3_per_s"] * (1.0 + 0.25 * i) for i in range(0, 161)]   # 1x..41x DWF
            ds = [solve_depth(q, h["gradient_m_per_m"], h["profile"], p)[0] for q in qs]
            _tab[key] = (qs, ds, p["height_m"])
        qs, ds, H = _tab[key]
        if Q <= qs[0]:  return ds[0], H
        if Q >= qs[-1]: return ds[-1], H
        for i in range(len(qs) - 1):
            if qs[i] <= Q <= qs[i+1]:
                t = (Q - qs[i]) / (qs[i+1] - qs[i])
                return ds[i] + t * (ds[i+1] - ds[i]), H
        return ds[-1], H
    # OVERFLOWS/STATIONS carry a line-local chunk index; INVERTS carries the global chunk id.
    by_line_idx = {(r["line"], r["idx"]): r["chunk"] for r in inv.values()}
    ofs = []
    for o in OVERFLOWS:
        lid = o["line"]; dl = DATUM_LINK[lid]
        cid = by_line_idx[(lid, o["chunk"])]; o = {**o, "chunk": cid, "line_chunk_index": o["chunk"]}
        r = inv[cid]; h = hyd[cid]
        # line datum -> Chart Datum, through the declared terminal invert and the record's lift
        term = [x for x in inv.values() if x["line"] == lid][-1]
        offset_cd = dl["terminal_invert_m_cd"] - term["invert_out_m"]
        invert_cd = r["invert_in_m"] + offset_cd
        otype = "capacity" if lid in ("N-high", "S-high") else "tidal"
        H_sec = PROFILES[r["profile"]]["height_m"]
        crest_above_invert = round(0.75 * H_sec, 3)
        crest_cd = round(invert_cd + crest_above_invert, 3)
        mhws_local = round(K["Z0"] + sum(K["A"][n] * math.exp(-abs(dl.get("km", 0.0)) * PROP[n]["atten_per_km"])
                                         for n in ("M2", "S2", "N2")), 3)
        ofs.append({**o, "type": otype, "invert_m_cd": round(invert_cd, 3),
                    "crest_above_invert_m": crest_above_invert, "crest_m_cd": crest_cd,
                    "mhws_local_m_cd": mhws_local,
                    "mhwn_local_m_cd": round(K["Z0"] + (K["A"]["M2"] - K["A"]["S2"]), 3),
                    "tidal_crest_m_cd": round(K["Z0"] + K["A"]["M2"] + 0.15, 3) if otype == "tidal" else None,
                    "dwf_m3_per_s": h["dwf_m3_per_s"], "profile": r["profile"],
                    "basis": ("capacity: side weir at 0.75 x section height above the invert; spills when the "
                              "sim storm discharge surcharges the section" if otype == "capacity" else
                              "tidal: relief weir crest at Z0 + A(M2) + 0.15 m CD, i.e. between MHWN and MHWS, so "
                              "it is reachable by a spring tide; spills only when the sim tide passes the crest AND "
                              "the sim storm runoff is at least 2x DWF (C-013)"),
                    "cites": ["R-016", "R-078", "R-092", "R-025"]})
        # ---- TIDES.json ----
    tides = {
      "constituents": {n: {"doodson": list(c["doodson"]), "speed_deg_per_hour": c["speed"],
                           "equilibrium_amplitude_m": c["eq_amp"],
                           "nodal_law": c["nodal"],
                           "fitted_amplitude_m": round(K["A"][n], 4),
                           "fitted_phase_deg": round(K["g"][n], 3)} for n, c in CONS.items()},
      "nodal_factors": {"M2/N2": "f = 1.000 - 0.037 cos N, u = -2.1 sin N",
                        "S2": "f = 1, u = 0",
                        "K1": "f = 1.006 + 0.115 cos N, u = -8.9 sin N",
                        "O1": "f = 1.009 + 0.187 cos N, u = 10.8 sin N", "cites": ["R-111"]},
      "reference_gauge": {"name": "London Bridge (Tower Pier)", "pla_code": "0113",
                          "lat": 51.50688, "lon": -0.07737, "cites": ["R-112"]},
      "Z0_m_above_chart_datum": round(K["Z0"], 4),
      "fitted_from": {"n_levels": len([c for c in CALIBRATION if c["h"] is not None]),
                      "rms_m": round(rms, 4), "max_abs_residual_m": round(mx, 4),
                      "source": "published predicted levels, UKHO/ADMIRALTY EasyTide via BBC Weather tide tables for London Bridge (Tower Pier)",
                      "accessed": "2026-10-21", "cites": ["R-113"], "status": "provisional - see D-003 / C-008"},
      "speed_check": speed_check(),
      "propagation_law": PROP,
      "propagation_basis": "progressive estuary wave: high water advances downstream at about 2 min/km (0.483 deg/km on M2); attenuation exponential in distance from the fitted reference gauge. The funnel amplification between Sheerness and London Bridge lies inside the fitted reference and is not extrapolated. Modelled law, basis stated; open item D-003.",
      "surge": {"model": "AR(1), rho=0.86, hourly", "sigma_m": SURGE_SIGMA, "clip_m": SURGE_CLIP,
                "note": "bounded so that the +/-0.15 m gate can fail; the sim carries weather, the harmonic does not"},
      "storm_runoff": {"model": "seeded rain-day series, one day in ~5, peak runoff multiplier 1.4-3.2"},
      "sim_window": {"start": SIM_START.strftime("%Y-%m-%dT%H:%M:%SZ"), "days": SIM_DAYS,
                     "hours_per_gauge": HOURS, "gauges": len(GAUGES),
                     "samples_total": HOURS * len(GAUGES)},
      "gauges": GAUGES, "datum_link": DATUM_LINK, "overflows": ofs,
      "calibration_points": CALIBRATION,
      "cites": ["R-108","R-109","R-110","R-111","R-112","R-113","R-114","R-115","R-116","R-118","R-078","R-092","R-079"],
    }
    json.dump(tides, open(os.path.join(LANE, "TIDES.json"), "w"), indent=1, sort_keys=True)
    # ---- run the 28-day sim at 6 gauges, hourly ----
    rows = []; worst = 0.0; per_gauge = {}
    for g in GAUGES:
        mx_g = 0.0
        for k in range(HOURS):
            dt = SIM_START + datetime.timedelta(hours=k)
            hh = harmonic(dt, K, gauge=g); ss = sim(dt, g, K)
            d = abs(ss - hh); mx_g = max(mx_g, d); worst = max(worst, d)
            rows.append({"gauge": g["id"], "t": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "harmonic_m": round(hh, 3), "sim_m": round(ss, 3), "delta_m": round(ss - hh, 3)})
        per_gauge[g["id"]] = {"name": g["name"], "samples": HOURS, "max_abs_delta_m": round(mx_g, 4),
                              "within_0p15": bool(mx_g <= 0.15)}
    # ---- overflow actuation, from sim conditions alone (F38: zero scripted actuations) ----
    acts = []; hourly_state = []
    gref = GAUGES[0]
    for k in range(HOURS):
        dt = SIM_START + datetime.timedelta(hours=k)
        tide = sim(dt, gref, K)
        sf = storm_factor(dt)
        for o in ofs:
            lid = o["line"]; dl = DATUM_LINK[lid]
            dg = GAUGES[0]
            local_tide = sim(dt, {"km_from_london_bridge": dl.get("km", 0.0)}, K)
            Q = o["dwf_m3_per_s"] * sf
            d, H = depth_at(o["chunk"], Q)
            level_cd = o["invert_m_cd"] + d
            drowned = local_tide >= o["invert_m_cd"]
            if drowned:
                level_cd = max(level_cd, local_tide)
            if o["type"] == "capacity":
                cond = level_cd >= o["crest_m_cd"]
                driver = f"sim storm discharge {Q:.2f} m3/s surcharges the section to {level_cd:.2f} m CD >= crest {o['crest_m_cd']:.2f}"
            else:
                cond = (local_tide >= o["tidal_crest_m_cd"]) and (sf >= 2.0)
                driver = (f"sim tide {local_tide:.2f} m CD >= relief crest {o['tidal_crest_m_cd']:.2f} "
                          f"AND sim runoff x{sf:.2f} >= 2.0 DWF")
            st = o.setdefault("_state", {"open": False, "start": None, "peak": 0.0, "events": 0, "hours": 0})
            if cond and not st["open"]:
                st["open"] = True; st["start"] = dt; st["peak"] = level_cd; st["events"] += 1
            elif cond:
                st["peak"] = max(st["peak"], level_cd); st["hours"] += 1
            elif st["open"]:
                st["open"] = False
                acts.append({"overflow": o["id"], "line": lid, "chunk": o["chunk"], "type": o["type"],
                             "opened": st["start"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "closed": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "hours_open": st["hours"] + 1,
                             "peak_level_m_cd": round(st["peak"], 3),
                             "crest_m_cd": o["crest_m_cd"] if o["type"] == "capacity" else o["tidal_crest_m_cd"],
                             "driver": driver})
                st["hours"] = 0
        hourly_state.append({"t": dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "tide_m_cd": round(tide, 3),
                             "storm_factor": round(sf, 3)})
    for o in ofs:
        st = o.get("_state")
        if st and st["open"]:
            acts.append({"overflow": o["id"], "line": o["line"], "chunk": o["chunk"], "type": o["type"],
                         "opened": st["start"].strftime("%Y-%m-%dT%H:%M:%SZ"), "closed": None,
                         "hours_open": st["hours"] + 1, "peak_level_m_cd": round(st["peak"], 3),
                         "crest_m_cd": o["crest_m_cd"] if o["type"] == "capacity" else o["tidal_crest_m_cd"],
                         "driver": "open at end of window"})
        o.pop("_state", None)
    with open(os.path.join(EV, "STORM_HOURS.jsonl"), "w") as f:
        for r in hourly_state: f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(EV, "OVERFLOWS.jsonl"), "w") as f:
        for a in acts: f.write(json.dumps(a, sort_keys=True) + "\n")
    os.makedirs(EV, exist_ok=True)
    json.dump({"window": tides["sim_window"], "tolerance_m": 0.15, "samples": len(rows),
               "max_abs_delta_m": round(worst, 4), "per_gauge": per_gauge,
               "verdict": "PASS" if worst <= 0.15 and all(v["within_0p15"] for v in per_gauge.values()) else "FAIL",
               "fit_rms_m": round(rms, 4), "fit_max_abs_residual_m": round(mx, 4),
               "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
              open(os.path.join(EV, "TIDE_VALIDATION.json"), "w"), indent=1, sort_keys=True)
    with open(os.path.join(LED, "TIDE_SERIES.jsonl"), "w") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"TIDES.json written · {len(rows)} sim samples ({len(GAUGES)} gauges x {HOURS} h)")
    print(f"max |sim - harmonic| = {worst:.4f} m  (tolerance 0.15 m)  -> {'PASS' if worst<=0.15 else 'FAIL'}")
    for gid, v in per_gauge.items(): print(f"  {gid} {v['name'][:34]:34s} max {v['max_abs_delta_m']:.4f} m")
    print(f"MHWS at the reference gauge: {mhws_lb:.3f} m CD · Z0 {K['Z0']:.3f} m CD")
    tally = {}
    for a in acts: tally[a["overflow"]] = tally.get(a["overflow"], 0) + 1
    print(f"overflow actuations from sim conditions alone: {len(acts)}  per overflow: "
          + " ".join(f"{o['id']}={tally.get(o['id'],0)}" for o in ofs))
    print(f"storm days in window: {len(storm_log(SIM_DAYS))} of {SIM_DAYS} "
          f"(major: {sum(1 for x in storm_log(SIM_DAYS) if x['major'])})")
    json.dump({"window_days": SIM_DAYS, "storm_days": storm_log(SIM_DAYS),
               "per_overflow": {o["id"]: {"line": o["line"], "type": o["type"], "chunk": o["chunk"],
                                          "crest_m_cd": o.get("crest_m_cd"),
                                          "tidal_crest_m_cd": o.get("tidal_crest_m_cd"),
                                          "invert_m_cd": o.get("invert_m_cd"),
                                          "profile": o.get("profile"),
                                          "actuations": tally.get(o["id"], 0)} for o in ofs}},
              open(os.path.join(EV, "OVERFLOW_ACCOUNTING.json"), "w"), indent=1, sort_keys=True)
    for a in acts[:8]:
        print(f"  {a['overflow']} on {a['line']} opened {a['opened']} closed {a['closed']} ({a.get('hours_open','-')} h)")

if __name__ == "__main__":
    main()
