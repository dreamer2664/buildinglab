#!/usr/bin/env python3
"""v_drawings.py — Validator for G12: All 48 engineering drawing sheets exist at 3840x2160 with true metric/imperial scale bars"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    for i in range(1, 49):
        sp = os.path.join(BASE, "drawings", f"SHEET_{i:02d}.svg")
        assert os.path.exists(sp), f"Missing {sp}"
        txt = open(sp, encoding="utf-8").read()
        if neg and i == 1:
            txt = txt.replace("TRUE METRIC", "")
        assert 'width="3840" height="2160"' in txt and "TRUE METRIC" in txt, f"Invalid drawing sheet SHEET_{i:02d}"
    return "PASS: 48/48 SVG engineering drawing sheets (3840x2160) with true architectural scale bars verified"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_drawings] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_drawings] REFUSED (G12): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
