#!/usr/bin/env python3
"""G7: 4,032 samples at 6 gauges x 28 days hourly, +/-0.15 m; plus the fit against published levels."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, jload, LANE, EV
def main():
    v = jload(os.path.join(EV, "TIDE_VALIDATION.json"))
    if not v: return verdict("v_tide", 3, {"samples": 0}, "the 28-day sim has not been run")
    probs = []
    if v.get("samples") != 4032: probs.append(f"samples {v.get('samples')} != 4032")
    if v.get("max_abs_delta_m", 9) > 0.15: probs.append(f"max delta {v.get('max_abs_delta_m')} m > 0.15")
    if v.get("fit_max_abs_residual_m", 9) > 0.15: probs.append(f"fit residual {v.get('fit_max_abs_residual_m')} m > 0.15")
    pg = v.get("per_gauge", {})
    if len(pg) != 6: probs.append(f"gauges {len(pg)} != 6")
    if not all(g.get("within_0p15") for g in pg.values()): probs.append("a gauge is out of tolerance")
    return verdict("v_tide", 1 if probs else 0,
                   {"samples": v.get("samples"), "gauges": len(pg), "max_delta_m": v.get("max_abs_delta_m"),
                    "fit_rms_m": v.get("fit_rms_m"), "fit_max_m": v.get("fit_max_abs_residual_m")},
                   "; ".join(probs) if probs else "sim within tolerance of the harmonic reconstruction AND of published levels")
if __name__ == "__main__": sys.exit(main())
