#!/usr/bin/env python3
"""Cross-section parametrisation: arc length along the inner perimeter -> (y, z) + outward normal.

One dense polyline per profile, built once, interpolated for every brick. The same code path
serves ovoid, circle and rectangle, so `v_profile` can check the census against the schedule
without special cases (F39).
"""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

N_PTS = 4096

def _polyline(kind, p):
    pts = []
    if kind == "ovoid":
        r = p["r"]
        # lower semicircle: centre (0, r), from angle 180deg -> 360deg through the invert
        for i in range(N_PTS // 2 + 1):
            a = math.pi + math.pi * i / (N_PTS // 2)
            pts.append((r * math.cos(a), r + r * math.sin(a)))
        # upper half-ellipse: centre (0, r), a = r, b = 3r, from 0deg -> 180deg through the crown.
        # It must start where the semicircle ended (+r, r) and close at (-r, r): C1-continuous ovoid.
        a_, b_ = r, 3.0 * r
        for i in range(1, N_PTS // 2 + 1):
            t = math.pi * i / (N_PTS // 2)
            pts.append((a_ * math.cos(t), r + b_ * math.sin(t)))
    elif kind == "circle":
        R = p["d"] / 2.0
        for i in range(N_PTS + 1):
            a = math.pi / 2 + 2 * math.pi * i / N_PTS   # start at the crown, go clockwise
            pts.append((R * math.cos(a), R + R * math.sin(a)))
    elif kind == "rect":
        h, w = p["h"], p["w"]
        corners = [(-w/2, 0), (w/2, 0), (w/2, h), (-w/2, h)]
        per = 2*(h+w); n = N_PTS
        acc = 0.0
        pts.append(corners[0])
        for k in range(4):
            a, b = corners[k], corners[(k+1) % 4]
            seg = math.hypot(b[0]-a[0], b[1]-a[1])
            m = max(1, int(round(n * seg / per)))
            for i in range(1, m+1):
                t = i/m
                pts.append((a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t))
    else:
        raise ValueError(kind)
    # cumulative arc length
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]))
    return pts, cum

_CACHE = {}

def section(pid, p):
    if pid in _CACHE: return _CACHE[pid]
    pts, cum = _polyline(p["kind"], p)
    per = cum[-1]
    _CACHE[pid] = (pts, cum, per)
    return _CACHE[pid]

def point_at(pid, p, s):
    """Return (y, z, normal_deg) at arc length s (metres) measured along the inner perimeter."""
    pts, cum, per = section(pid, p)
    s = s % per
    lo, hi = 0, len(cum)-1
    while lo + 1 < hi:
        mid = (lo+hi)//2
        if cum[mid] <= s: lo = mid
        else: hi = mid
    seg = cum[hi]-cum[lo] or 1e-9
    t = (s-cum[lo])/seg
    y = pts[lo][0] + (pts[hi][0]-pts[lo][0])*t
    z = pts[lo][1] + (pts[hi][1]-pts[lo][1])*t
    # outward normal from the local tangent (tangent rotated -90deg for a clockwise profile)
    ty = pts[hi][0]-pts[lo][0]; tz = pts[hi][1]-pts[lo][1]
    nl = math.hypot(ty, tz) or 1e-9
    ny, nz = tz/nl, -ty/nl
    return y, z, math.degrees(math.atan2(nz, ny))

def perimeter(pid, p):
    return section(pid, p)[2]

def offset_perimeter(pid, p, off, n=2048):
    """Exact perimeter of the ring at radial offset `off` (metres outward), any profile kind."""
    pts, cum, per = section(pid, p)
    step = max(1, len(pts)//n)
    tot = 0.0; prev = None
    for i in range(0, len(pts), step):
        s = cum[i]
        y, z, nd = point_at(pid, p, s)
        a = math.radians(nd)
        q = (y + off*math.cos(a), z + off*math.sin(a))
        if prev is not None: tot += math.hypot(q[0]-prev[0], q[1]-prev[1])
        prev = q
    y0, z0, nd0 = point_at(pid, p, 0.0); a0 = math.radians(nd0)
    q0 = (y0 + off*math.cos(a0), z0 + off*math.sin(a0))
    tot += math.hypot(q0[0]-prev[0], q0[1]-prev[1])
    return tot


if __name__ == "__main__":
    from lines import PROFILES
    for pid, p in PROFILES.items():
        per = perimeter(pid, p)
        y0 = point_at(pid, p, 0.0); yq = point_at(pid, p, per/4)
        print(f"{pid:11s} {p['kind']:6s} perimeter {per:8.4f} m  (+0.114 wythe: {offset_perimeter(pid,p,0.114):8.4f})  s=0 -> y {y0[0]:+.4f} z {y0[1]:+.4f} n {y0[2]:+7.2f}deg   "
              f"s=per/4 -> y {yq[0]:+.4f} z {yq[1]:+.4f} n {yq[2]:+7.2f}deg")
