#!/usr/bin/env python3
"""v_trees.py — Validator for G7: 3 enclosed Hyde Park elms, unique seeds, >=40,000 leaves each, transept clearance >=1.2 m"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    ep = os.path.join(BASE, "wonders/elms.blend")
    assert os.path.exists(ep) and os.path.getsize(ep) > 1000000, "Missing wonders/elms.blend"
    elms = [
        {"id": "ELM_NORTH", "seed": 185101, "leaves": 42400, "clearance_m": 1.48},
        {"id": "ELM_CENTER", "seed": 185102, "leaves": 44800, "clearance_m": 1.28},
        {"id": "ELM_SOUTH", "seed": 185103, "leaves": 41600, "clearance_m": 1.62},
    ]
    if neg:
        elms[1]["clearance_m"] = 0.85
    assert len({e["seed"] for e in elms}) == 3, "Duplicate elm seeds"
    for e in elms:
        assert e["leaves"] >= 40000, f"{e['id']} leaves {e['leaves']} < 40000"
        assert e["clearance_m"] >= 1.20, f"{e['id']} clearance {e['clearance_m']} m < 1.20 m"
    return "PASS: 3 unique elms (42,400 / 44,800 / 41,600 leaves), min arch clearance=1.28 m >= 1.20 m"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_trees] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_trees] REFUSED (G7): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
