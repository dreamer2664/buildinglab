#!/usr/bin/env python3
"""G11: the drawing set must exist at count, at size, at scale and annotated - and the station
numbers must run continuous. An index with no sheets behind it is a fail, not a pass."""
import sys, os, json, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import verdict, jload, LANE
SPEC = {"cross_section": (340, (2560, 1440), "1:50"), "profile_tile": (158, (1920, 1080), "1:1000"),
        "hydraulic_map": (12, (3840, 2160), "schematic")}
def px_of(path):
    try:
        with open(path, "rb") as f: d = f.read(33)
        return struct.unpack(">II", d[16:24])
    except Exception: return None
def main():
    idx = jload(os.path.join(LANE, "drawings/DRAWINGS_INDEX.json"), {})
    sheets = idx.get("sheets", [])
    if not sheets: return verdict("v_drawings", 3, {"subject_files": 0, "target": 510},
                                  "no drawing index in the lane yet - Stage H")
    probs = []
    byclass = {}
    for s in sheets: byclass.setdefault(s["class"], []).append(s)
    for cls, (want, dims, scale) in SPEC.items():
        got = byclass.get(cls, [])
        if len(got) != want: probs.append(f"{cls}: {len(got)} sheets != {want}")
        for s in got:
            if tuple(s.get("px", ())) != dims: probs.append(f"{s['id']}: px {s.get('px')} != {dims}")
            if s.get("scale") != scale: probs.append(f"{s['id']}: scale {s.get('scale')} != {scale}")
            if not s.get("annotations"): probs.append(f"{s['id']}: no annotations")
            gotpx = px_of(os.path.join(LANE, s.get("png", "")))
            if gotpx != dims: probs.append(f"{s['id']}: raster {gotpx} != {dims}")
            if not os.path.exists(os.path.join(LANE, s.get("svg", ""))): probs.append(f"{s['id']}: no svg")
    cs = sorted(byclass.get("cross_section", []), key=lambda s: s["id"])
    ids = [s["id"] for s in cs]
    if ids != [f"CS-{i:03d}" for i in range(1, len(cs) + 1)]: probs.append("cross-section ids not continuous")
    byline = {}
    for s in cs: byline.setdefault(s["line"], []).append(s)
    for line, rows in byline.items():
        st = [r["station_m"] for r in sorted(rows, key=lambda r: r["station_m"])]
        if any(b <= a for a, b in zip(st, st[1:])): probs.append(f"{line}: section stations not strictly rising")
    lp = sorted(byclass.get("profile_tile", []), key=lambda s: s["id"])
    byline = {}
    for s in lp: byline.setdefault(s["line"], []).append(s)
    for line, rows in byline.items():
        rows.sort(key=lambda r: r["chainage_from_m"])
        for a, b in zip(rows, rows[1:]):
            if abs(a["chainage_to_m"] - b["chainage_from_m"]) > 1e-6:
                probs.append(f"{line}: tile gap {a['id']}->{b['id']}")
    return verdict("v_drawings", 1 if probs else 0,
                   {"sheets": len(sheets), "cross_section": len(byclass.get("cross_section", [])),
                    "profile_tile": len(byclass.get("profile_tile", [])),
                    "hydraulic_map": len(byclass.get("hydraulic_map", [])),
                    "violations": len(probs)}, "; ".join(probs[:4]) if probs else
                   "510 sheets at count, size, scale and annotation; stations continuous; tiles gapless")
if __name__ == "__main__": sys.exit(main())
