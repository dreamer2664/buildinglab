#!/usr/bin/env python3
"""v_organ.py — Validator for G6: Great Organ >=4,000 pipes (4,500 law); every pipe length recomputed from note & scale within ±2%"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    pipes = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/ORGAN_PIPES.jsonl"), encoding="utf-8")]
    if neg:
        pipes[0]["mesh_length_m"] *= 1.15
    assert len(pipes) == 4500 and len(pipes) >= 4000, f"Expected 4500 organ pipes, got {len(pipes)}"
    max_pct_err = 0.0
    for p in pipes:
        T = float(p["hall_temp_c"])
        c = 331.3 * math.sqrt(1.0 + T / 273.15)
        f = 440.0 * (2.0 ** ((int(p["midi_note"]) - 69.0) / 12.0)) * (8.0 / float(p["footage_ft"]))
        d = float(p["diameter_m"])
        wl = c / f
        if p["pipe_type"] == "open_flue":
            recomp = max(0.035, 0.5 * wl - 1.65 * d)
        elif p["pipe_type"] == "stopped_flue":
            recomp = max(0.025, 0.25 * wl - 0.82 * d)
        else:
            recomp = max(0.045, 0.36 * wl)
        err_pct = abs(float(p["mesh_length_m"]) - recomp) / recomp * 100.0
        if err_pct > max_pct_err:
            max_pct_err = err_pct
    assert max_pct_err <= 2.0, f"Organ pipe length error {max_pct_err:.3f}% > 2.0%"
    return f"PASS: 4,500 organ pipes recomputed, max_length_error={max_pct_err:.4f}% <= 2.0%"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_organ] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_organ] REFUSED (G6): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
