#!/usr/bin/env python3
"""28 tide charts (section 24 class tide_chart): six gauges x four weekly windows of the 28-day
simulation, plus four summary sheets. Every curve is the TIDE_SERIES ledger itself; the harmonic
reconstruction is drawn beneath it so the reader sees the residual the validation measured."""
import os, json, datetime
from collections import defaultdict
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(LANE, "drawings/svg"); PNG = os.path.join(LANE, "drawings/png")
series = defaultdict(list)
for l in open(os.path.join(LANE, "ledgers/TIDE_SERIES.jsonl")):
    r = json.loads(l); series[r["gauge"]].append((r["t"], r["sim_m"], r.get("harmonic_m")))
VAL = json.load(open(os.path.join(LANE, "evidence/TIDE_VALIDATION.json")))
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
W, H = 2560, 1440
index = []
def frame(title, sub):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            f'<rect width="{W}" height="{H}" fill="#f4efe4"/>',
            f'<rect x="14" y="14" width="{W-28}" height="{H-28}" fill="none" stroke="#2b2b2b" stroke-width="3"/>',
            f'<text x="60" y="90" font-family="serif" font-size="44" fill="#1c1c1c">{title}</text>',
            f'<text x="60" y="130" font-family="serif" font-size="24" fill="#3a3a3a">{sub}</text>',
            f'<text x="60" y="{H-40}" font-family="serif" font-size="18" fill="#3a3a3a">CLOACA VICTORIA - drawn by bazalgette, agent - {NOW} - curves from ledgers/TIDE_SERIES.jsonl</text>']
def chart(g, week):
    rows = series[g]
    t0 = 1865 * 10000 + (week * 7 * 24)
    sel = rows[week * 7 * 24:(week + 1) * 7 * 24]
    p = frame(f"TIDE CHART TC-{g}-W{week+1}", f"gauge {g} - days {week*7+1}-{(week+1)*7} of the 28-day window - levels in metres above chart datum")
    xs0, xs1, ys0, ys1 = 120, W - 120, 220, H - 160
    zs = [r[1] for r in sel] + [r[2] for r in sel if r[2] is not None]
    zmin, zmax = min(zs) - 0.3, max(zs) + 0.3
    def X(i): return xs0 + (xs1 - xs0) * i / max(len(sel) - 1, 1)
    def Y(z): return ys1 - (ys1 - ys0) * (z - zmin) / (zmax - zmin)
    for k in range(8):
        zz = zmin + (zmax - zmin) * k / 7
        p.append(f'<line x1="{xs0}" y1="{Y(zz):.0f}" x2="{xs1}" y2="{Y(zz):.0f}" stroke="#d8d0bc" stroke-width="1"/>')
        p.append(f'<text x="{xs0-14}" y="{Y(zz)+6:.0f}" font-family="serif" font-size="18" fill="#3a3a3a" text-anchor="end">{zz:.1f}</text>')
    sim = " ".join(f"{X(i):.1f},{Y(r[1]):.1f}" for i, r in enumerate(sel))
    p.append(f'<polyline points="{sim}" fill="none" stroke="#20465c" stroke-width="3"/>')
    har = " ".join(f"{X(i):.1f},{Y(r[2]):.1f}" for i, r in enumerate(sel) if r[2] is not None)
    if har: p.append(f'<polyline points="{har}" fill="none" stroke="#7a2e1f" stroke-width="1.5" stroke-dasharray="8,6"/>')
    p.append(f'<text x="{xs1-400}" y="{ys0-20}" font-family="serif" font-size="22" fill="#20465c">simulation</text>')
    p.append(f'<text x="{xs1-180}" y="{ys0-20}" font-family="serif" font-size="22" fill="#7a2e1f">harmonic fit</text>')
    return p
def summary(k):
    if k == 0:
        p = frame("TIDE CHART TC-SUM-1", "max abs residual per gauge, metres, against the 0.15 m tolerance")
        gs = VAL.get("per_gauge", {})
        for i, (g, v) in enumerate(sorted(gs.items())):
            x = 300 + i * 340; hpx = v["max_abs_delta_m"] / 0.15 * 700
            p.append(f'<rect x="{x}" y="{1100-hpx:.0f}" width="180" height="{hpx:.0f}" fill="#20465c"/>')
            p.append(f'<text x="{x+90}" y="1140" font-family="serif" font-size="26" text-anchor="middle" fill="#1c1c1c">{g}</text>')
            p.append(f'<text x="{x+90}" y="{1080-hpx:.0f}" font-family="serif" font-size="22" text-anchor="middle" fill="#1c1c1c">{v["max_abs_delta_m"]}</text>')
        p.append(f'<line x1="240" y1="{1100-700:.0f}" x2="{W-240}" y2="{1100-700:.0f}" stroke="#7a2e1f" stroke-width="3"/>')
        p.append(f'<text x="{W-240}" y="{1080-700:.0f}" font-family="serif" font-size="22" fill="#7a2e1f" text-anchor="end">tolerance 0.15 m</text>')
    elif k == 1:
        p = frame("TIDE CHART TC-SUM-2", "samples per gauge and within-tolerance flag, 4,032 samples total")
        for i, (g, v) in enumerate(sorted(VAL.get("per_gauge", {}).items())):
            p.append(f'<text x="300" y="{320+i*120}" font-family="serif" font-size="30" fill="#1c1c1c">{g}: {v["samples"]} samples, max delta {v["max_abs_delta_m"]} m, within 0.15 m: {"yes" if v["within_0p15"] else "NO"}</text>')
    elif k == 2:
        p = frame("TIDE CHART TC-SUM-3", "constituent amplitudes and phases of the fitted London Bridge set")
        T = json.load(open(os.path.join(LANE, "TIDES.json")))
        for i, (k2, a) in enumerate(sorted(T.get("amplitudes_m", {}).items())):
            g2 = T.get("phases_deg", {}).get(k2)
            p.append(f'<text x="300" y="{300+i*110}" font-family="serif" font-size="30" fill="#1c1c1c">{k2}: A {a} m, g {g2} deg</text>')
    else:
        p = frame("TIDE CHART TC-SUM-4", "storm surge series and the overflow actuation hours")
        acts = [json.loads(l) for l in open(os.path.join(LANE, "evidence/OVERFLOWS.jsonl"))]
        for i, a in enumerate(acts[:24]):
            p.append(f'<text x="300" y="{300+i*44}" font-family="serif" font-size="24" fill="#1c1c1c">{a["opened"]} {a["overflow"]} {a["type"]} crest {a["crest_m_cd"]} m CD - {a["driver"][:80]}</text>')
    return p
n = 0
for g in sorted(series):
    for week in range(4):
        p = chart(g, week); sid = f"TC-{g}-W{week+1}"
        open(os.path.join(SVG, sid + ".svg"), "w").write("\n".join(p) + "\n</svg>")
        index.append({"id": sid, "gauge": g, "week": week + 1}); n += 1
for k in range(4):
    p = summary(k); sid = f"TC-SUM-{k+1}"
    open(os.path.join(SVG, sid + ".svg"), "w").write("\n".join(p) + "\n</svg>")
    index.append({"id": sid, "summary": True}); n += 1
print("tide charts:", n)
with open("build/tc_raster.sh", "w") as f:
    for e in index:
        f.write(f'rsvg-convert -w 2560 -h 1440 drawings/svg/{e["id"]}.svg -o drawings/png/{e["id"]}.png || echo FAIL {e["id"]}\n')
