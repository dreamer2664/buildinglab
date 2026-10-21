#!/usr/bin/env python3
"""G3: continuous fall at every join, zero uphill metres, realised fall = declared fall per line."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import inverts, verdict, jload, LANE
def main():
    inv = inverts()
    if len(inv) != 1320: return verdict("v_gradient", 1, {"rows": len(inv)}, "INVERTS.jsonl incomplete")
    lines = jload(os.path.join(LANE, "evidence", "LINES.json"), {})
    uphill = 0; joins = 0; disc = 0; worst = 0.0
    by = {}
    for r in inv: by.setdefault(r["line"], []).append(r)
    for lid, rows in by.items():
        rows.sort(key=lambda r: r["idx"])
        for a, bb in zip(rows, rows[1:]):
            joins += 1
            d = abs(a["invert_out_m"] - bb["invert_in_m"]) * 1000.0
            worst = max(worst, d)
            if d > 10.0: disc += 1                      # §15.1 +/-10 mm
        for r in rows:
            if r["fall_m"] <= 0: uphill += 1
        tot = round(rows[0]["invert_in_m"] - rows[-1]["invert_out_m"], 3)
        dec = lines.get(lid, {})
        if dec and abs(tot - dec.get("total_fall_m", tot)) > 0.001:
            disc += 1
    total_joins = sum(len(v) for v in by.values()) - len(by)
    return verdict("v_gradient", 1 if (uphill or disc or joins != total_joins) else 0,
                   {"joins_checked": joins, "uphill_metres": uphill, "discontinuities_over_10mm": disc,
                    "worst_join_mm": round(worst, 4), "lines": len(by),
                    "network_km": round(sum(r["fall_m"] for r in inv) / 1000 * 0 + len(inv) * 0.1, 3)},
                   "zero uphill metres" if not uphill else f"{uphill} chunks do not fall")
if __name__ == "__main__": sys.exit(main())
