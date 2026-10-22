#!/usr/bin/env python3
"""v_walk.py — Validator for G11: 1,851 walk views exist at eye height 1.6 m with consecutive spacing 1 ft (0.3048 m) ±0.05 m"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    ws = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/WALK_STATIONS.jsonl"), encoding="utf-8")]
    if neg:
        ws[50]["pos_m"][0] += 0.25
    assert len(ws) == 1851, f"Expected 1851 walk stations, got {len(ws)}"
    max_step_err = 0.0
    for i in range(1, len(ws)):
        dx = abs(float(ws[i - 1]["pos_m"][0]) - float(ws[i]["pos_m"][0]))
        err = abs(dx - 0.3048)
        if err > max_step_err:
            max_step_err = err
        assert abs(float(ws[i]["pos_m"][2]) - 1.60) <= 0.01, "Walk eye height != 1.60 m"
    assert max_step_err <= 0.05, f"Walk station spacing error {max_step_err:.4f} m > 0.05 m"
    return f"PASS: 1,851 walk stations verified at Z=1.60 m, max_step_err={max_step_err:.4f} m <= 0.05 m"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_walk] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_walk] REFUSED (G11): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
