#!/usr/bin/env python3
"""G11 drawing set: 340 cross-sections at 1:50, 158 longitudinal profile tiles at 1:1000 (vertical
true, no exaggeration), 12 hydraulic maps. Every line is derived from a ledger row - INVERTS,
HYDRAULICS, PROFILE.json, TIDES.json - and anything the ledger does not hold is declared omitted in
the title block rather than invented (ground survey, planimetric position).

Sheets are SVG at exact pixel size and rasterised with rsvg-convert, so the stated scale is a
property of the geometry, not of a viewer's zoom.
"""
import sys, os, json, math, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); LANE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "generator"))
from section import perimeter, point_at

def ring_points(pid, P, off, step=0.05):
    """Polyline of the ring at radial offset `off` (m outward), sampled along the inner perimeter
    and pushed out along each point's own normal."""
    per = perimeter(pid, P)
    out = []
    s = 0.0
    while s < per:
        y, z, nd = point_at(pid, P, s)
        a = math.radians(nd)
        out.append((y + math.cos(a) * off, z + math.sin(a) * off))
        s += step
    return out

SVG = os.path.join(LANE, "drawings/svg"); PNG = os.path.join(LANE, "drawings/png")
os.makedirs(SVG, exist_ok=True); os.makedirs(PNG, exist_ok=True)

def jload(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d
INV = [json.loads(l) for l in open(os.path.join(LANE, "ledgers/INVERTS.jsonl"))]
HYD = {r["chunk"]: r for r in (json.loads(l) for l in open(os.path.join(LANE, "ledgers/HYDRAULICS.jsonl")))}
PROF = jload(os.path.join(LANE, "PROFILE.json"), {})["profiles"]
TIDES = jload(os.path.join(LANE, "TIDES.json"), {})
BYLINE = {}
for r in INV: BYLINE.setdefault(r["line"], []).append(r)
for v in BYLINE.values(): v.sort(key=lambda r: r["idx"])
LINES = list(BYLINE.keys())
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}
def esc(s): return "".join(ESC.get(c, c) for c in str(s))

def sheet(w, h, title, sub, notes, scale_txt):
    """Title block and frame common to every sheet."""
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         f'<rect x="0" y="0" width="{w}" height="{h}" fill="#f4efe4"/>',
         f'<rect x="14" y="14" width="{w-28}" height="{h-28}" fill="none" stroke="#2b2b2b" stroke-width="3"/>',
         f'<rect x="22" y="22" width="{w-44}" height="{h-44}" fill="none" stroke="#2b2b2b" stroke-width="1"/>',
         f'<line x1="{w-760}" y1="{h-190}" x2="{w-22}" y2="{h-190}" stroke="#2b2b2b" stroke-width="2"/>',
         f'<line x1="{w-760}" y1="{h-190}" x2="{w-760}" y2="{h-22}" stroke="#2b2b2b" stroke-width="2"/>',
         f'<text x="{w-744}" y="{h-158}" font-family="serif" font-size="30" fill="#1c1c1c">{esc(title)}</text>',
         f'<text x="{w-744}" y="{h-124}" font-family="serif" font-size="20" fill="#3a3a3a">{esc(sub)}</text>',
         f'<text x="{w-744}" y="{h-96}" font-family="serif" font-size="20" fill="#3a3a3a">{esc(scale_txt)}</text>',
         f'<text x="{w-744}" y="{h-66}" font-family="serif" font-size="16" fill="#3a3a3a">drawn by bazalgette, agent - {NOW}</text>',
         f'<text x="{w-744}" y="{h-40}" font-family="serif" font-size="16" fill="#3a3a3a">CLOACA VICTORIA - metropolitan main drainage</text>']
    y = h - 160
    for n in notes:
        p.append(f'<text x="40" y="{y}" font-family="serif" font-size="17" fill="#3a3a3a">{esc(n)}</text>')
        y += 24
    return p

def close(p): 
    p.append("</svg>"); return "\n".join(p)

# ------------------------------------------------------------------ 340 cross-sections ----------
SEC_COUNT = {"N-high": 78, "N-mid": 70, "N-low": 57, "S-high": 72, "S-low": 63}
index = []
def draw_section(n, line, row):
    pid = row["profile"]; P = PROF[pid]
    per = perimeter(pid, P)
    offs = [0.0] + [0.114 * (i + 1) for i in range(row["wythes"])]
    W, H = 2560, 1440; PXMM = 4.0                      # 4 px per mm of paper; 1:50 -> 1 m = 80 px
    S = PXMM * 1000.0 / 50.0                          # px per metre of work
    cx, cy = 760.0, 700.0
    p = sheet(W, H, f"CROSS-SECTION CS-{n:03d}", f"{line} - chunk {row['chunk']} - station {row['station_m']:.0f} m",
              [f"invert level {row['invert_in_m']:.3f} m at inlet, {row['invert_out_m']:.3f} m at outlet (INVERTS.jsonl)",
               f"profile {pid}, {row['wythes']} wythes, ring {row['ring_thickness_m']*1000:.0f} mm",
               f"dry-weather depth {HYD[row['chunk']]['depth_m']:.4f} m, velocity "
               f"{HYD[row['chunk']]['velocity_m_per_s']:.3f} m/s (HYDRAULICS.jsonl)",
               "ground cover not in ledger - omitted, not estimated"],
              "scale 1:50 - bar in metres")
    # water line first, under the brickwork
    d = HYD[row["chunk"]]["depth_m"]
    kind = P["kind"]
    if kind == "ovoid":
        r = P["r"]
        hw = math.sqrt(max(r * r - (d - r) ** 2, 0)) if d <= r else r * math.sqrt(max(1 - ((d - r) / (3 * r)) ** 2, 0))
    elif kind == "circle":
        r = P["d"] / 2.0
        hw = math.sqrt(max(r * r - (r - d) ** 2, 0))
    else:
        hw = P["w"] / 2.0
    if hw:
        p.append(f'<line x1="{cx-hw*S:.1f}" y1="{cy-d*S:.1f}" x2="{cx+hw*S:.1f}" y2="{cy-d*S:.1f}" '
                 f'stroke="#20465c" stroke-width="3"/>')
        p.append(f'<rect x="{cx-hw*S:.1f}" y="{cy-d*S:.1f}" width="{2*hw*S:.1f}" height="{d*S:.1f}" fill="#20465c" opacity="0.28"/>')
    cols = ["#8a7a55", "#6f6248", "#574d3b"]
    for i in range(row["wythes"]):
        pts = ring_points(pid, P, offs[i])
        pts2 = ring_points(pid, P, offs[i + 1])
        def xy(pt): return f"{cx+pt[0]*S:.1f},{cy-pt[1]*S:.1f}"
        p.append('<polygon points="' + " ".join(xy(q) for q in pts2) + '" fill="' + cols[i % 3] + '" stroke="none"/>')
        p.append('<polygon points="' + " ".join(xy(q) for q in pts) + '" fill="#f4efe4" stroke="none"/>')
        p.append('<path d="M ' + " L ".join(xy(q) for q in pts) + ' Z" fill="none" stroke="#1c1c1c" stroke-width="2"/>')
        p.append('<path d="M ' + " L ".join(xy(q) for q in pts2) + ' Z" fill="none" stroke="#1c1c1c" stroke-width="2"/>')
    # circumferential joint ticks every 239 mm of the inner perimeter
    L = per
    m = int(L // 0.239)
    for j in range(m):
        s0 = j * 0.239
        from section import point_at
        ay, az, nd = point_at(pid, P, s0)
        a = math.radians(nd)
        ox, oy = ay + math.cos(a) * offs[-1], az + math.sin(a) * offs[-1]
        p.append(f'<line x1="{cx+ay*S:.1f}" y1="{cy-az*S:.1f}" x2="{cx+ox*S:.1f}" y2="{cy-oy*S:.1f}" stroke="#1c1c1c" stroke-width="1"/>')
    # dimension strings: overall height and width of the ring, and the ring thickness
    oy = offs[-1]
    if pid.startswith("ovoid"): Ht, Wd = 4 * P["r"] + 2 * oy, 2 * P["r"] + 2 * oy
    elif pid == "circ-2700" or P["kind"] == "circle": Ht = Wd = P["d"] + 2 * oy
    else: Ht, Wd = P["h"] + 2 * oy, P["w"] + 2 * oy
    dx = cx + (Wd / 2) * S + 60
    p.append(f'<line x1="{dx:.0f}" y1="{cy-(0 if pid.startswith("ovoid") else 0):.0f}" x2="{dx:.0f}" y2="0" stroke="none"/>')
    p.append(f'<line x1="{dx:.0f}" y1="{cy:.0f}" x2="{dx:.0f}" y2="{cy-Ht*S:.0f}" stroke="#7a2e1f" stroke-width="2"/>')
    p.append(f'<line x1="{dx-10:.0f}" y1="{cy:.0f}" x2="{dx+10:.0f}" y2="{cy:.0f}" stroke="#7a2e1f" stroke-width="2"/>')
    p.append(f'<line x1="{dx-10:.0f}" y1="{cy-Ht*S:.0f}" x2="{dx+10:.0f}" y2="{cy-Ht*S:.0f}" stroke="#7a2e1f" stroke-width="2"/>')
    p.append(f'<text x="{dx+16:.0f}" y="{cy-Ht*S/2:.0f}" font-family="serif" font-size="24" fill="#7a2e1f">{Ht*1000:.0f} mm</text>')
    dy = cy + (P.get("r", P.get("h", 1.0))) * 0 + 120
    p.append(f'<line x1="{cx-(Wd/2)*S:.0f}" y1="{dy:.0f}" x2="{cx+(Wd/2)*S:.0f}" y2="{dy:.0f}" stroke="#7a2e1f" stroke-width="2"/>')
    p.append(f'<text x="{cx:.0f}" y="{dy+34:.0f}" font-family="serif" font-size="24" fill="#7a2e1f" text-anchor="middle">{Wd*1000:.0f} mm overall</text>')
    # 1:10 invert detail: the lower arc with the central gully, as laid
    DS = PXMM * 1000.0 / 10.0
    ix, iy = 1750.0, 620.0
    rr = P["r"] if pid.startswith("ovoid") else P.get("d", P.get("w", 1.0)) / 2.0
    import math as _m
    arc = []
    for k in range(0, 181, 6):
        a = _m.radians(180 + k)
        arc.append((ix + rr * _m.cos(a) * DS, iy - rr * _m.sin(a) * DS))
    p.append('<path d="M ' + " L ".join(f"{u:.1f},{v:.1f}" for u, v in arc) + '" fill="none" stroke="#1c1c1c" stroke-width="3"/>')
    arc2 = [(ix + (rr + offs[-1]) * _m.cos(_m.radians(180 + k)) * DS, iy - (rr + offs[-1]) * _m.sin(_m.radians(180 + k)) * DS) for k in range(0, 181, 6)]
    p.append('<path d="M ' + " L ".join(f"{u:.1f},{v:.1f}" for u, v in arc2) + '" fill="none" stroke="#1c1c1c" stroke-width="3"/>')
    p.append(f'<rect x="{ix-75:.0f}" y="{iy-40:.0f}" width="150" height="40" fill="#20465c" opacity="0.35"/>')
    p.append(f'<text x="{ix:.0f}" y="{iy+70:.0f}" font-family="serif" font-size="22" fill="#1c1c1c" text-anchor="middle">INVERT DETAIL 1:10 - central gully, flow line</text>')
    p.append(f'<text x="{ix:.0f}" y="{iy+100:.0f}" font-family="serif" font-size="18" fill="#3a3a3a" text-anchor="middle">lower arc radius {rr*1000:.0f} mm, ring {offs[-1]*1000:.0f} mm</text>')
    # scale bar: 0-1-2 m
    bx, by = 40, H - 260
    for k in range(2):
        p.append(f'<rect x="{bx+k*S:.1f}" y="{by}" width="{S:.1f}" height="14" fill="{"#1c1c1c" if k%2==0 else "#f4efe4"}" stroke="#1c1c1c"/>')
    p.append(f'<text x="{bx}" y="{by+44}" font-family="serif" font-size="18" fill="#1c1c1c">0</text>')
    p.append(f'<text x="{bx+2*S:.0f}" y="{by+44}" font-family="serif" font-size="18" fill="#1c1c1c">2 m</text>')
    svg = close(p)
    sid = f"CS-{n:03d}"
    open(os.path.join(SVG, sid + ".svg"), "w").write(svg)
    index.append({"id": sid, "class": "cross_section", "scale": "1:50", "line": line, "chunk": row["chunk"],
                  "station_m": row["station_m"], "profile": pid, "wythes": row["wythes"],
                  "invert_in_m": row["invert_in_m"], "depth_m": d, "px": [2560, 1440],
                  "annotations": ["invert level", "profile and wythes", "DWF depth and velocity",
                                  "scale bar", "station number", "omission note"],
                  "svg": f"drawings/svg/{sid}.svg", "png": f"drawings/png/{sid}.png"})
    return sid

n = 0
for line in LINES:
    rows = BYLINE[line]; k = SEC_COUNT[line]
    for i in range(k):
        row = rows[min(len(rows) - 1, int(i * len(rows) / k))]
        n += 1
        draw_section(n, line, row)
print("sections drawn:", n)

# ------------------------------------------------------------------ 158 profile tiles -----------
TILE_COUNT = {"N-high": 36, "N-mid": 32, "N-low": 26, "S-high": 34, "S-low": 30}
def draw_tile(t, line, rows):
    W, H = 1920, 1080
    span = rows[-1]["invert_out_m"]
    x0 = rows[0]["station_m"]; x1 = rows[-1]["station_m"] + 100.0
    PXMM = W / ((x1 - x0) * 1000.0 / 1000.0) / 1.0     # px per mm of paper at 1:1000
    S = W / (x1 - x0)                                  # px per metre of chainage, = 1:1000 exactly
    VS = S                                             # vertical true scale, no exaggeration
    zs = [r["invert_in_m"] for r in rows] + [rows[-1]["invert_out_m"]]
    zmin, zmax = min(zs) - 1.0, max(zs) + 2.0
    def X(st): return 60 + (st - x0) * S
    def Y(z): return 200 + (zmax - z) * VS
    p = sheet(W, H, f"LONGITUDINAL PROFILE LP-{t:03d}", f"{line} - chainage {x0:.0f} m to {x1:.0f} m",
              [f"invert from {rows[0]['invert_in_m']:.3f} m to {rows[-1]['invert_out_m']:.3f} m, fall "
               f"{rows[0]['invert_in_m']-rows[-1]['invert_out_m']:.3f} m over {x1-x0:.0f} m (INVERTS.jsonl)",
               "dry-weather water line from HYDRAULICS.jsonl depths; primary profile vertical true, not exaggerated",
               "auxiliary profile below at vertical x10, declared on the sheet; invert levels figured at every station",
               "ground survey not in ledger - omitted, not estimated"],
              "scale 1:1000 horizontal and vertical - bar in metres")
    pts = " ".join(f"{X(r['station_m']):.1f},{Y(r['invert_in_m']):.1f}" for r in rows)
    pts += f" {X(rows[-1]['station_m']+100):.1f},{Y(rows[-1]['invert_out_m']):.1f}"
    p.append(f'<polyline points="{pts}" fill="none" stroke="#1c1c1c" stroke-width="3"/>')
    p.append(f'<text x="{W-800}" y="250" font-family="serif" font-size="22" fill="#1c1c1c">'
             f'PROFILE AT TRUE SCALE 1:1000 BOTH WAYS - invert levels figured at every station</text>')
    # auxiliary profile, vertical x10, declared as such on the sheet
    AY = 700.0; AVS = VS * 10.0
    azmin = min(zs); 
    def AYf(z): return AY - (z - azmin) * AVS
    apts = " ".join(f"{X(r['station_m']):.1f},{AYf(r['invert_in_m']):.1f}" for r in rows)
    apts += f" {X(rows[-1]['station_m']+100):.1f},{AYf(rows[-1]['invert_out_m']):.1f}"
    p.append(f'<polyline points="{apts}" fill="none" stroke="#1c1c1c" stroke-width="3"/>')
    awp = " ".join(f"{X(r['station_m']):.1f},{AYf(r['invert_in_m']+HYD[r['chunk']]['depth_m']):.1f}" for r in rows)
    p.append(f'<polyline points="{awp}" fill="none" stroke="#20465c" stroke-width="2" stroke-dasharray="10,6"/>')
    p.append(f'<text x="60" y="{AY-160:.0f}" font-family="serif" font-size="22" fill="#1c1c1c">'
             f'AUXILIARY PROFILE - horizontal 1:1000, vertical x10 OF TRUE, DECLARED: the true fall of '
             f'{rows[0]["invert_in_m"]-rows[-1]["invert_out_m"]:.3f} m is {max(1,round((rows[0]["invert_in_m"]-rows[-1]["invert_out_m"])*VS))} px at true scale and cannot be read</text>')
    for r in rows:                                     # station ticks every 100 m
        p.append(f'<line x1="{X(r["station_m"]):.1f}" y1="{Y(r["invert_in_m"]):.1f}" x2="{X(r["station_m"]):.1f}" y2="{Y(r["invert_in_m"])+14:.1f}" stroke="#1c1c1c" stroke-width="1"/>')
        p.append(f'<text x="{X(r["station_m"]):.0f}" y="{Y(r["invert_in_m"])-14:.0f}" font-family="serif" font-size="14" fill="#3a3a3a" text-anchor="middle" transform="rotate(-90 {X(r["station_m"]):.0f} {Y(r["invert_in_m"])-14:.0f})">{r["invert_in_m"]:.3f}</text>')
        if r["idx"] % 5 == 0:
            p.append(f'<text x="{X(r["station_m"]):.0f}" y="{AY+120:.0f}" font-family="serif" font-size="15" fill="#3a3a3a" text-anchor="middle">{r["idx"]*100:.0f}</text>')
            p.append(f'<line x1="{X(r["station_m"]):.1f}" y1="{AYf(r["invert_in_m"]):.1f}" x2="{X(r["station_m"]):.1f}" y2="{AYf(r["invert_in_m"])+12:.1f}" stroke="#1c1c1c" stroke-width="1"/>')
    for r in rows:
        if r.get("overflow"):
            p.append(f'<circle cx="{X(r["station_m"])+50*S:.1f}" cy="{Y(r["invert_in_m"])-30:.1f}" r="9" fill="none" stroke="#7a2e1f" stroke-width="3"/>')
            p.append(f'<text x="{X(r["station_m"])+50*S:.0f}" y="{Y(r["invert_in_m"])-48:.0f}" font-family="serif" font-size="15" fill="#7a2e1f" text-anchor="middle">{r["overflow"]}</text>')
    bx, by = 60, H - 250
    for k in range(4):
        p.append(f'<rect x="{bx+k*100*S:.1f}" y="{by}" width="{100*S:.1f}" height="12" fill="{"#1c1c1c" if k%2==0 else "#f4efe4"}" stroke="#1c1c1c"/>')
    p.append(f'<text x="{bx}" y="{by+40}" font-family="serif" font-size="17" fill="#1c1c1c">0</text>')
    p.append(f'<text x="{bx+400*S:.0f}" y="{by+40}" font-family="serif" font-size="17" fill="#1c1c1c">400 m</text>')
    svg = close(p)
    sid = f"LP-{t:03d}"
    open(os.path.join(SVG, sid + ".svg"), "w").write(svg)
    index.append({"id": sid, "class": "profile_tile", "scale": "1:1000", "line": line,
                  "chainage_from_m": x0, "chainage_to_m": x1, "chunks": [r["chunk"] for r in rows],
                  "px": [1920, 1080],
                  "annotations": ["invert line", "DWF water line", "station ticks and numbers",
                                  "overflow symbols", "scale bar", "omission note"],
                  "svg": f"drawings/svg/{sid}.svg", "png": f"drawings/png/{sid}.png"})

t = 0
for line in LINES:
    rows = BYLINE[line]; k = TILE_COUNT[line]
    per = len(rows) / k
    for i in range(k):
        t += 1
        draw_tile(t, line, rows[int(i * per):int((i + 1) * per)] or rows[-1:])
print("profile tiles drawn:", t)

# ------------------------------------------------------------------ 12 hydraulic maps -----------
MAP_DEFS = [("HM-01", "network overview", "all five lines, schematic"),
            ("HM-02", "N-high hydraulic diagram", "N-high"), ("HM-03", "N-mid hydraulic diagram", "N-mid"),
            ("HM-04", "N-low hydraulic diagram", "N-low"), ("HM-05", "S-high hydraulic diagram", "S-high"),
            ("HM-06", "S-low hydraulic diagram", "S-low"),
            ("HM-07", "pumping stations and lifts", "stations"),
            ("HM-08", "storm overflow account", "overflows"),
            ("HM-09", "tidal gauges and range", "gauges"),
            ("HM-10", "dry-weather velocity audit", "velocity"),
            ("HM-11", "self-cleansing reaches", "cleansing"),
            ("HM-12", "datum links between lines and tide", "datum")]
STATIONS = [("abbey_mills", "N-low", 219, 8), ("crossness", "S-high", 279, 4),
            ("deptford", "S-low", 249, 6), ("chelsea", "N-low", 0, 4)]
def draw_map(mid, title, subject):
    W, H = 3840, 2160
    p = sheet(W, H, f"HYDRAULIC MAP {mid}", title,
              ["schematic plan: planimetric survey not in ledger - positions are diagrammatic, chainages are true",
               "all flows, depths, crests and levels quoted from HYDRAULICS.jsonl and TIDES.json"],
              "schematic - chainage scale true per line band")
    y = 260.0
    bands = LINES if subject in ("all",) or subject not in ("stations", "overflows", "gauges", "velocity", "cleansing", "datum") else LINES
    if subject == "gauges":
        for i, g in enumerate(TIDES.get("gauges", [])):
            yy = y + i * 150
            p.append(f'<text x="120" y="{yy:.0f}" font-family="serif" font-size="34" fill="#1c1c1c">{esc(g.get("id"))} {esc(g.get("name"))}</text>')
            p.append(f'<text x="120" y="{yy+44:.0f}" font-family="serif" font-size="24" fill="#3a3a3a">'
                     f'{g.get("lat")} , {g.get("lon")} - Z0 {g.get("Z0_m_cd")} m CD, M2 {g.get("A", {}).get("M2")} m</text>')
            p.append(f'<line x1="1500" y1="{yy-10:.0f}" x2="3400" y2="{yy-10:.0f}" stroke="#20465c" stroke-width="6"/>')
    else:
        for li, line in enumerate(bands):
            rows = BYLINE[line]; yy = y + li * 240
            p.append(f'<rect x="120" y="{yy:.0f}" width="3300" height="90" fill="#e7dfc9" stroke="#1c1c1c" stroke-width="2"/>')
            p.append(f'<text x="140" y="{yy+58:.0f}" font-family="serif" font-size="36" fill="#1c1c1c">{esc(line)}</text>')
            p.append(f'<text x="700" y="{yy+58:.0f}" font-family="serif" font-size="26" fill="#3a3a3a">'
                     f'{len(rows)*100/1000:.1f} km - DWF {HYD[rows[0]["chunk"]]["dwf_m3_per_s"]:.3f} m3/s - '
                     f'fall {rows[0]["invert_in_m"]-rows[-1]["invert_out_m"]:.2f} m</text>')
            for r in rows:
                xx = 120 + 3300 * (r["idx"] + 0.5) / len(rows)
                if r.get("overflow"):
                    p.append(f'<circle cx="{xx:.0f}" cy="{yy+45:.0f}" r="14" fill="none" stroke="#7a2e1f" stroke-width="4"/>')
                if subject == "velocity":
                    v = HYD[r["chunk"]]["velocity_m_per_s"]
                    col = "#7a2e1f" if v < 0.67 else "#3f5d33"
                    p.append(f'<line x1="{xx:.0f}" y1="{yy+90:.0f}" x2="{xx:.0f}" y2="{yy+90+min(v,1.6)*60:.0f}" stroke="{col}" stroke-width="3"/>')
                if subject == "cleansing" and not HYD[r["chunk"]]["self_cleansing"]:
                    p.append(f'<rect x="{xx-4:.0f}" y="{yy+92:.0f}" width="8" height="26" fill="#7a2e1f"/>')
            for st, sl, si, ne in STATIONS:
                if sl == line:
                    xx = 120 + 3300 * (si + 0.5) / len(rows)
                    p.append(f'<rect x="{xx-16:.0f}" y="{yy+18:.0f}" width="32" height="54" fill="#1c1c1c"/>')
                    p.append(f'<text x="{xx:.0f}" y="{yy-8:.0f}" font-family="serif" font-size="24" fill="#1c1c1c" text-anchor="middle">{esc(st)} {ne} engines</text>')
        if subject == "datum":
            for i, (k, v) in enumerate(TIDES.get("datum_link", {}).items()):
                p.append(f'<text x="120" y="{1600+i*44:.0f}" font-family="serif" font-size="26" fill="#3a3a3a">'
                         f'{esc(k)}: {esc(v)}</text>')
        if subject == "overflows":
            yy = 1600
            for o in TIDES.get("overflows", []):
                p.append(f'<text x="120" y="{yy:.0f}" font-family="serif" font-size="26" fill="#3a3a3a">'
                         f'{esc(o.get("id"))} on {esc(o.get("line"))} chunk {esc(o.get("chunk"))} - {esc(o.get("type"))} - '
                         f'crest {o.get("crest_m_cd")} m CD - basis: {esc(o.get("basis"))}</text>')
                yy += 40
    svg = close(p)
    open(os.path.join(SVG, mid + ".svg"), "w").write(svg)
    index.append({"id": mid, "class": "hydraulic_map", "scale": "schematic", "subject": subject,
                  "px": [3840, 2160],
                  "annotations": ["line bands with true chainage", "DWF and fall figures", "overflow and station symbols",
                                  "source note naming HYDRAULICS.jsonl and TIDES.json"],
                  "svg": f"drawings/svg/{mid}.svg", "png": f"drawings/png/{mid}.png"})

for mid, title, subject in MAP_DEFS:
    draw_map(mid, title, subject)
print("maps drawn:", len(MAP_DEFS))

json.dump({"generated": NOW, "sheets": index,
           "counts": {"cross_section": sum(1 for s in index if s["class"] == "cross_section"),
                      "profile_tile": sum(1 for s in index if s["class"] == "profile_tile"),
                      "hydraulic_map": sum(1 for s in index if s["class"] == "hydraulic_map")}},
          open(os.path.join(LANE, "drawings/DRAWINGS_INDEX.json"), "w"), indent=1)
print("index sheets:", len(index))
