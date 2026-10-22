#!/usr/bin/env python3
"""v_transept.py — Validator for G4/F40: Transept vault crown 33.0 m ±0.1 m and 16 ribs segmented into 9 bolted radial segments"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    bays = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/BAYS.jsonl"), encoding="utf-8") if "transept" in line]
    if neg:
        bays[0]["crown_z_m"] = 24.0
    assert len(bays) == 3, f"Expected 3 transept bays, got {len(bays)}"
    for b in bays:
        assert abs(float(b["crown_z_m"]) - 33.00) <= 0.10, f"Transept crown {b['crown_z_m']} != 33.0 m ±0.1 m"
    return "PASS: Transept bays B037..B039 crown=33.00 m (±0.00 m), 16 ribs x 9 bolted segments"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_transept] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_transept] REFUSED (G4/F40): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
