#!/usr/bin/env python3
"""F12: chunk joins invert-continuous within +/-10 mm AND courses aligned across the join."""
import sys, os, json, gzip
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import index, built, census, verdict, inverts, LED
def first_last_x(chunk):
    plain = os.path.join(LED, "BRICKS", f"{chunk}.jsonl"); gz = plain + ".gz"
    src = open(plain) if os.path.exists(plain) else (gzip.open(gz, "rt") if os.path.exists(gz) else None)
    if src is None: return None
    lo = hi = None
    for l in src:
        if not l.strip(): continue
        x = json.loads(l)["x"]
        lo = x if lo is None else min(lo, x); hi = x if hi is None else max(hi, x)
    return lo, hi
def main():
    inv = {r["chunk"]: r for r in inverts()}
    b = sorted(built(), key=lambda r: r["row"])
    adj = [(p, q) for p, q in zip(b, b[1:]) if q["row"] == p["row"] + 1 and q["line"] == p["line"]]
    if not adj: return verdict("v_joins", 3, {"adjacent_built_pairs": 0}, "no adjacent built pair to test")
    bad = []; worst = 0.0; worst_gap = 0.0
    for p, q in adj:
        d = abs(inv[p["chunk"]]["invert_out_m"] - inv[q["chunk"]]["invert_in_m"]) * 1000.0
        worst = max(worst, d)
        if d > 10.0: bad.append(f"{p['chunk']}->{q['chunk']} invert {d:.1f} mm")
        # chunks carry their own local origin (each .blend opens standalone, §15.5), so the
        # join is measured ACROSS the boundary: the run out of chunk p plus the run into chunk q
        # must equal one course module, 86 mm, within +/-10 mm (F12).
        fp, fq = first_last_x(p["chunk"]), first_last_x(q["chunk"])
        if fp and fq:
            MODULE_MM = 86.0
            gap = (100000.0 - fp[1]) + fq[0]
            worst_gap = max(worst_gap, abs(gap - MODULE_MM))
            if abs(gap - MODULE_MM) > 10.0:
                bad.append(f"{p['chunk']}->{q['chunk']} course pitch across the join {gap:.1f} mm vs {MODULE_MM:.0f}")
    return verdict("v_joins", 1 if bad else 0, {"adjacent_built_pairs": len(adj),
                   "worst_invert_delta_mm": round(worst, 4),
                   "worst_course_pitch_error_mm": round(worst_gap, 3), "violations": len(bad)},
                   "; ".join(bad[:3]) if bad else "invert continuous and courses aligned across every join")
if __name__ == "__main__": sys.exit(main())
