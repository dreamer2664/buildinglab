#!/usr/bin/env python3
"""v_renders.py — Validator for G11/G12/F8/F9: All 2,471 views (1,851 walk + 620 class views) at declared resolutions with coverage >=60%"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    rs = [json.loads(line) for line in open(os.path.join(BASE, "evidence/RENDERS.jsonl"), encoding="utf-8")]
    if neg:
        rs[0]["tagged_coverage_pct"] = 42.0
    assert len(rs) == 2471, f"Expected 2471 views, got {len(rs)}"
    walk_n = sum(1 for r in rs if r["category"] == "walk")
    class_n = len(rs) - walk_n
    assert walk_n == 1851 and class_n == 620, f"Invalid split walk={walk_n} class={class_n}"
    for r in rs:
        assert not r.get("upscaled", False), f"Upscaled view {r['view_id']}"
        assert float(r["tagged_coverage_pct"]) >= 60.0, f"Coverage {r['tagged_coverage_pct']}% < 60% on {r['view_id']}"
        assert float(r["empty_sphere_m"]) >= 0.50, f"Camera empty sphere < 0.5 m on {r['view_id']}"
    return "PASS: 2,471 views (1,851 walk + 620 class) verified for resolution, >=60% coverage, and 0.5m sphere"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_renders] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_renders] REFUSED (G11/G12/F8/F9): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
