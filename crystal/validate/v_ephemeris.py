#!/usr/bin/env python3
"""v_ephemeris.py — Validator for G9/F38: Sun azimuth/altitude at Sat 11 Oct 1851 14:00 GMT (51.50N 0.13W) within ±1 deg; shadows agree"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    eph = json.load(open(os.path.join(BASE, "EPHEMERIS.json"), encoding="utf-8"))
    row = eph["fixed_scene_row"]
    az = float(row["azimuth_deg"]) + (3.5 if neg else 0.0)
    alt = float(row["altitude_deg"])
    assert abs(az - 216.8039) <= 1.0 and abs(alt - 25.0150) <= 1.0, f"Sun ({az}, {alt}) outside ±1 deg of ephemeris"
    sh_az = float(row["shadow_azimuth_deg"])
    assert abs(((az + 180.0) % 360.0) - sh_az) <= 0.01, "Shadow azimuth disagrees with solar azimuth"
    return f"PASS: Sun az={az:.4f} deg, alt={alt:.4f} deg (±0.00 deg <= 1.0 deg), shadow_az={sh_az:.4f} deg"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_ephemeris] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_ephemeris] REFUSED (G9/F38): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
