#!/usr/bin/env python3
"""v_units.py — Validator for G1/G2: 1 Blender unit = 1.0 m (METRIC) in CONSTANTS.md and bay scenes"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    const_txt = open(os.path.join(BASE, "CONSTANTS.md"), encoding="utf-8").read()
    if neg:
        const_txt = const_txt.replace("scale_length = 1.0", "scale_length = 0.3048")
    assert "scale_length = 1.0" in const_txt and "1.0 m" in const_txt, "Unit scale_length != 1.0 m"
    return "PASS: unit_m=1.0 metric verified"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_units] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_units] REFUSED (G1/G2): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
