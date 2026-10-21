#!/usr/bin/env python3
"""PROFILE — the egg, the circle and the rectangle, in metres, from the ledger side.

Geometry law (CONSTANTS.md §2):
  ovoid 2:1  = lower semicircle radius r  +  upper half-ellipse (a=r, b=3r)
               -> overall height 4r, overall width 2r, tangent-continuous at the springing.
               Cited: Baldwin Latham, Sanitary Engineering (1873) ovoid proportioning [REFERENCES R-022];
               commission declares ~2.7 m high x ~1.4 m wide +/-20 mm [R-142].
  brick      = 229 x 114 x 76 mm London stock, 10 mm nominal mortar joint [R-041,R-042]
  ring       = transverse courses; within a course bricks are laid 229 mm circumferentially,
               course height 76 mm axially; the ring is 2 or 3 wythes deep radially,
               each wythe 114 mm -> 228 mm (9 in) or 342 mm (13.5 in) [R-043,R-143]

Nothing here is declared: every count is recomputed from the geometry, per G4/15.2.
"""
import math

BRICK = {"L": 0.229, "W": 0.114, "H": 0.076}
JOINT = 0.010

def ovoid(r):
    """Return (height, width, inner_perimeter_metres). r = half the invert width."""
    h, w = 4.0 * r, 2.0 * r
    # lower semicircle
    p_lo = math.pi * r
    # upper half-ellipse a=r, b=3r  (Ramanujan II, error < 1e-5 for these axes)
    a, b = r, 3.0 * r
    p_up = 0.5 * math.pi * (3.0 * (a + b) - math.sqrt((3.0 * a + b) * (a + 3.0 * b)))
    return h, w, p_lo + p_up

def circle(d):
    return d, d, math.pi * d

def rectangle(h, w):
    return h, w, 2.0 * (h + w)

def inner_perimeter(kind, **kw):
    if kind == "ovoid":  return ovoid(kw["r"])[2]
    if kind == "circle": return circle(kw["d"])[2]
    if kind == "rect":   return rectangle(kw["h"], kw["w"])[2]
    raise ValueError(kind)

def course_geometry(kind, wythes, pid=None, prof=None, **kw):
    """Bricks in one transverse course at the ring's mid-radius, and the axial module.
    Mid-ring perimeter is measured on the offset section (exact for ovoid, circle and rect)."""
    pin = inner_perimeter(kind, **kw)
    ring_thk = wythes * BRICK["W"]
    if prof is not None:
        from section import offset_perimeter
        pmid = offset_perimeter(pid, prof, ring_thk / 2.0)
    else:
        pmid = pin + 2.0 * math.pi * (ring_thk / 2.0) if kind != "rect" else pin + 4.0 * (ring_thk / 2.0)
    mod_c = BRICK["L"] + JOINT            # 239 mm circumferentially
    n_full = int(math.floor(pmid / mod_c))
    gap = pmid - n_full * mod_c           # closure: the ring is closed by adjusting one joint
    return {"inner_perimeter_m": round(pin, 4), "mid_perimeter_m": round(pmid, 4),
            "ring_thickness_m": round(ring_thk, 4),
            "bricks_per_course": n_full + 1,      # +1 closure brick (cut), see CONFLICTS C-006
            "closure_gap_m": round(gap, 4),
            "axial_module_m": BRICK["H"] + JOINT} # 86 mm

def chunk_census(chunk_len_m, kind, wythes, pid=None, prof=None, **kw):
    g = course_geometry(kind, wythes, pid=pid, prof=prof, **kw)
    courses = int(math.floor(chunk_len_m / g["axial_module_m"]))
    per_course = g["bricks_per_course"] * wythes
    return {"courses": courses, "bricks_per_course_all_wythes": per_course,
            "census": courses * per_course, **g}

if __name__ == "__main__":
    import json, sys
    r = 0.675
    h, w, p = ovoid(r)
    print(f"ovoid r={r} -> height {h:.3f} m x width {w:.3f} m, inner perimeter {p:.4f} m")
    for wy in (2, 3):
        c = chunk_census(100.0, "ovoid", wy, r=r)
        print(f"  wythes={wy}: ring {c['ring_thickness_m']*1000:.0f} mm · {c['bricks_per_course']} bricks/course/wythe · "
              f"{c['courses']} courses/100 m · CENSUS {c['census']:,} bricks/100 m chunk · "
              f"x1320 = {c['census']*1320/1e6:.1f} M")
