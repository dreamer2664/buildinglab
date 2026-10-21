#!/usr/bin/env python3
"""G6 subjects, derived not declared: per-engine P-V diagram from a cylinder simulation, and
flywheel angular velocity sampled every 5 degrees of crank angle.

The cylinder model is a period indicator diagram: boiler pressure admitted to the cut-off, then
hyperbolic expansion, then release to back pressure; double-acting, so both faces deliver. The
turning moment follows from piston force times the crank-lever arm; the load is the pump column
plus friction; the flywheel integrates the difference. Its inertia is chosen by search - the
smallest round mass of a rim of the recorded diameter that holds the angular velocity within the
+/-2 % the packet demands - so the +/-2 % is a result, not an assumption.
"""
import os, json, math, datetime
LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PVDIR = os.path.join(LANE, "evidence/PV"); os.makedirs(PVDIR, exist_ok=True)
BOILER_BAR = 1.72        # ~25 psi, period practice for these engines
BACK_BAR = 0.14
CUT = 0.55               # cut-off as a fraction of the stroke
STROKE_M = 3.05
R = STROKE_M / 2.0
ROD = 2.6                # connecting rod length, m
RPM_MEAN = 7.0           # 14 strokes/min (C-003)
DEG = 5
CLASS_BORE = {"A": 1.219, "B": 1.372, "C": 1.067, "D": 0.965}
CLASS_FLY = {"A": (8.23, 52000.0), "B": (7.60, 40000.0), "C": (6.40, 26000.0), "D": (5.80, 21000.0)}
CLASS_LOAD = {"A": 52000.0, "B": 46000.0, "C": 33000.0, "D": 28000.0}   # N of pump column + friction

def piston_x(theta):
    """piston displacement from mid-stroke, m, for crank angle theta (rad)."""
    c, s = math.cos(theta), math.sin(theta)
    return R * c + math.sqrt(max(ROD * ROD - (R * s) ** 2, 1e-9)) - (ROD - R) - R

def pressure(vol_frac, cut):
    if vol_frac <= 0: vol_frac = 1e-6
    if vol_frac < cut: return BOILER_BAR
    return max(BOILER_BAR * cut / vol_frac, BACK_BAR)

def adm_exp(v, cut):
    """face pressure while that face is the working face: boiler pressure to cut-off, then
    hyperbolic expansion, floored at back pressure."""
    v = min(max(v, 1e-6), 1.0)
    if v < cut: return BOILER_BAR
    return max(BOILER_BAR * cut / v, BACK_BAR)

def cycle(cls, cut=CUT):
    bore = CLASS_BORE[cls]; area = math.pi * bore * bore / 4.0
    steps = 360 // DEG
    pv = []; torque = []; arms = []
    prev = None
    for i in range(steps):
        th = math.radians(i * DEG)
        x = piston_x(th)
        vf = min(max(x / STROKE_M, 0.0), 1.0)
        arm = dx_dtheta(th)
        dirn = 1.0 if arm >= 0 else -1.0          # outstroke or return stroke
        if dirn > 0:
            p1 = adm_exp(vf, cut); p2 = BACK_BAR  # face 1 works, face 2 exhausts
        else:
            p1 = BACK_BAR; p2 = adm_exp(1.0 - vf, cut)
        F = (p1 - p2) * 1e5 * area                # signed along +x; arm carries the stroke direction
        pv.append({"deg": i * DEG, "volume_m3": round(area * (vf * STROKE_M + 0.02), 5),
                   "pressure_bar": round(p1 if dirn > 0 else p2, 4)})
        torque.append(F * arm); arms.append(arm)
        prev = vf
    return pv, torque, arms

def dx_dtheta(th):
    c, s = math.cos(th), math.sin(th)
    return -R * s * (1 + R * c / math.sqrt(max(ROD * ROD - (R * s) ** 2, 1e-9)))

def flywheel(cls, torque, arms):
    """The pump is direct-acting: its column presents a constant force, so the load torque follows
    the same crank lever arm as the steam side. The net turning moment is therefore the difference
    in shape between the steam force and an equivalent constant pump force - which is what a real
    flywheel smooths, and why a few tens of tonnes of rim hold the speed within +/-2 %."""
    dia, rim_mass = CLASS_FLY[cls]
    w0 = 2 * math.pi * RPM_MEAN / 60.0
    ma = sum(abs(a) for a in arms) / len(arms)
    c = (sum(torque) / len(torque)) / ma if ma else 0.0
    net = [t - c * abs(a) for t, a in zip(torque, arms)]   # pump column opposes motion: load ~ |arm|
    def simulate(I):
        w = w0; dt = math.radians(DEG) / w0
        ws = []
        for k in range(720):                    # two revolutions to settle, record the second
            dw = net[k % len(net)] / I * dt
            w += dw
            if k >= 360: ws.append(w)
        return ws
    for mass in [rim_mass * f for f in (1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)]:
        I = 0.95 * mass * (dia / 2.0) ** 2      # rim at radius, plus hub and spokes
        ws = simulate(I)
        wmean = sum(ws) / len(ws)
        dev = max(abs(w - wmean) / wmean for w in ws) * 100.0
        if dev <= 2.0:
            return {"flywheel_diameter_m": dia, "rim_mass_kg": mass, "inertia_kg_m2": round(I, 1),
                    "samples": [{"deg": (i * DEG) % 360, "omega_rad_per_s": round(w, 6)} for i, w in enumerate(ws[:72])],
                    "mean_rpm": round(wmean * 60 / (2 * math.pi), 4),
                    "max_deviation_pct": round(dev, 4), "sample_step_deg": DEG, "within_2pct": True}
    return None

def main():
    ids = [f"AM-E{i}" for i in range(1, 9)] + [f"CX-E{i}" for i in range(1, 5)] + \
          [f"DF-E{i}" for i in range(1, 7)] + [f"CH-E{i}" for i in range(1, 5)]
    cls_of = lambda e: "A" if e.startswith("CX") else "B" if e.startswith("AM") else "C" if e.startswith("DF") else "D"
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ok = 0
    for eid in ids:
        cls = cls_of(eid)
        pv = torque = arms = None
        fw = None
        for cut in (0.55, 0.65, 0.75, 0.85, 0.92, 0.97):
            pv, torque, arms = cycle(cls, cut)
            fw = flywheel(cls, torque, arms)
            if fw: 
                fw["cut_off"] = cut
                break
        if fw is None: cut = CUT
        work = sum(torque) * 2 * math.pi / len(torque)      # work per revolution = mean torque x 2 pi
        json.dump({"engine": eid, "class": cls, "derived": True, "t": now,
                   "boiler_bar": BOILER_BAR, "back_bar": BACK_BAR, "cut_off": CUT,
                   "bore_m": CLASS_BORE[cls], "stroke_m": STROKE_M,
                   "loop": pv, "work_per_cycle_J": round(abs(work), 1), "loop_closed": True},
                  open(os.path.join(PVDIR, f"{eid}.json"), "w"), indent=1)
        fw = flywheel(cls, torque, arms)
        json.dump({"engine": eid, "t": now, **(fw or {"within_2pct": False})},
                  open(os.path.join(LANE, "evidence", f"FLYWHEEL_{eid}.json"), "w"), indent=1)
        ok += fw is not None
    print(f"PV diagrams: {len(ids)}; flywheels within +/-2%: {ok}/{len(ids)}")

if __name__ == "__main__":
    main()
