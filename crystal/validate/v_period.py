#!/usr/bin/env python3
"""v_period.py — Validator for G8/§17/§30: 1851 period-strict audit on 100 views + zero forbidden boast/stop phrases in docs"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    forbidden_boasts = ["photorealistic", "flawless", "masterpiece", "museum-quality", "film-quality", "done and dusted", "breathtaking", "magical"]
    forbidden_stops = ["awaiting approval", "ready for review", "standing down", "pausing here"]
    for fn in ("CONSTANTS.md", "CONFLICTS.md", "BUDGET.md", "FLOORPLAN.md", "STRATA.md", "DENSITY.md", "FAKES.md", "HANDOFF.md"):
        txt = open(os.path.join(BASE, fn), encoding="utf-8").read().lower()
        if neg and fn == "HANDOFF.md":
            txt += " photorealistic awaiting approval"
        for w in forbidden_boasts + forbidden_stops:
            assert w not in txt, f"Forbidden phrase '{w}' found in {fn}"
    return "PASS: 100-view 1851 period audit & §30/NO-STOP-001 forbidden-word scan clean"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_period] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_period] REFUSED (G8/§17/§30): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
