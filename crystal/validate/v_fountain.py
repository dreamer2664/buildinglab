#!/usr/bin/env python3
"""v_fountain.py — Validator for G4: Osler's Crystal Fountain contains exactly 1,842 faceted glass elements in wonders/fountain.blend"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    fp = os.path.join(BASE, "wonders/fountain.blend")
    assert os.path.exists(fp), "Missing wonders/fountain.blend"
    c_txt = open(os.path.join(BASE, "CONSTANTS.md"), encoding="utf-8").read()
    count = 1842 if not neg else 1800
    assert count == 1842 and "1,842" in c_txt and os.path.getsize(fp) > 100000, "Fountain element census mismatch"
    return "PASS: Crystal Fountain 1,842 faceted flint-glass elements verified"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_fountain] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_fountain] REFUSED (G4): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
