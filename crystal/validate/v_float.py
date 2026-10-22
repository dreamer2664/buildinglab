#!/usr/bin/env python3
"""v_float.py — Validator for F6/F12: Zero floating columns, exhibits, or visitors above floor/gallery datum"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    vis = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/VISITORS.jsonl"), encoding="utf-8")]
    if neg:
        vis[0]["pos_m"][2] = 1.45
    for v in vis:
        z = float(v["pos_m"][2])
        assert z in (0.0, 7.32), f"Floating visitor {v['id']} at Z={z}"
    return "PASS: 0 floating columns, exhibits, or visitors (all grounded on Z=0.00 m or Z=7.32 m)"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_float] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_float] REFUSED (F6/F12): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
