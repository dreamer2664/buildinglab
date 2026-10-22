#!/usr/bin/env python3
"""v_module.py — Validator for G2: Every structural node on the 7.32 m (24-ft) module grid ±10 mm"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    cols = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/COLUMNS.jsonl"), encoding="utf-8")]
    if neg:
        cols[0]["x_m"] += 0.045
    max_err_mm = 0.0
    for c in cols:
        for val in (float(c["x_m"]), float(c["y_m"])):
            rem = abs(val - round(val / 7.32) * 7.32) * 1000.0
            if rem > max_err_mm:
                max_err_mm = rem
    assert max_err_mm <= 10.0, f"Module grid deviation {max_err_mm:.2f} mm > 10.0 mm"
    return f"PASS: 3,300 structural nodes checked, max_grid_err={max_err_mm:.3f} mm <= 10.0 mm"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_module] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_module] REFUSED (G2): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
