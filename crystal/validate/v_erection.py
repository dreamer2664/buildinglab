#!/usr/bin/env python3
"""v_erection.py — Validator for G10/F41: Zero keyframed machinery in erection film; simulated glazing rate within ±20% of documented rate"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    shots = [json.loads(line) for line in open(os.path.join(BASE, "film/SHOTS.jsonl"), encoding="utf-8")]
    rates = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/RATES.jsonl"), encoding="utf-8")]
    if neg:
        shots[0]["keyframed_fcurves"] = 4
    assert len(shots) == 12, "Expected 12 erection shots"
    assert all(int(s["keyframed_fcurves"]) == 0 for s in shots), "Keyframed machinery FCurve detected!"
    mean_rate = sum(float(r["sim_wagon_rate_panes_per_hr"]) for r in rates) / len(rates)
    delta_pct = abs(mean_rate - 10.80) / 10.80 * 100.0
    assert delta_pct <= 20.0, f"Glazing rate delta {delta_pct:.2f}% > 20.0%"
    return f"PASS: 0 keyframed machinery FCurves, sim glazing rate={mean_rate:.3f} panes/hr/wagon (delta={delta_pct:.2f}% <= 20%)"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_erection] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_erection] REFUSED (G10/F41): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
