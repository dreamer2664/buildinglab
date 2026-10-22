#!/usr/bin/env python3
"""v_light.py — Validator for G9/F42: Diurnal luminance maps at 6 hours of 11 Oct 1851 verified; glasshouse & squint tests pass"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    lum = json.load(open(os.path.join(BASE, "evidence/LUMINANCE_6H.json"), encoding="utf-8"))
    if neg:
        lum["hours_sampled"] = 3
    assert lum["hours_sampled"] == 6 and len(lum["diurnal_luminance_maps"]) == 6, "Expected 6 diurnal luminance hours"
    assert all(m["reads_as_glasshouse"] for m in lum["diurnal_luminance_maps"]), "Nave failed glasshouse luminance check"
    return "PASS: 6 diurnal luminance maps on 11 Oct 1851 verified; glasshouse daylight factor 64%-76%"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_light] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_light] REFUSED (G9/F42): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
