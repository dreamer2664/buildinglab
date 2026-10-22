#!/usr/bin/env python3
"""v_glass.py — Validator for G3/F35: Per-pane crown-glass wave displacement and distinct IOR/roughness, not one flat shader"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    pt = json.load(open(os.path.join(BASE, "evidence/PANETEST.json"), encoding="utf-8"))
    if neg:
        pt["unique_ripple_profiles_in_sample"] = 1
    assert pt["unique_ripple_profiles_in_sample"] == 100, f"Expected 100 unique ripple profiles, got {pt['unique_ripple_profiles_in_sample']}"
    iors = {p["ior"] for p in pt["sampled_panes"]}
    assert len(iors) >= 25, "Insufficient IOR variation across sampled crown-glass panes"
    return f"PASS: 100/100 distinct per-pane vertex wave profiles, {len(iors)} IOR buckets"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_glass] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_glass] REFUSED (G3/F35): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
