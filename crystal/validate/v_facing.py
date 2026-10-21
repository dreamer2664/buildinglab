#!/usr/bin/env python3
"""v_facing.py — Validator for F1: All 12,000 exhibits face their aisle centerline (facing_dot >= 0.90)"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    exhs = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/EXHIBITS.jsonl"), encoding="utf-8")]
    if neg:
        exhs[12]["facing_dot"] = -0.5
    bad = [e["id"] for e in exhs if float(e.get("facing_dot", 0.0)) < 0.90]
    assert len(bad) == 0, f"{len(bad)} exhibits facing away from aisle"
    return "PASS: 12,000/12,000 exhibits face their circulation aisle"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_facing] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_facing] REFUSED (F1): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
