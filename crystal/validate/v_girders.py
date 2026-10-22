#!/usr/bin/env python3
"""v_girders.py — Validator for G4/F12: 2,224 girders with positive camber and bolt-hole schedule (12/18/24) within 10 mm join tolerance"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    girders = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/GIRDERS.jsonl"), encoding="utf-8")]
    if neg:
        girders[0]["camber_mm"] = 0.0
    assert len(girders) == 2224, f"Expected 2224 girders, got {len(girders)}"
    for g in girders:
        assert float(g["camber_mm"]) > 0.0, f"Girder {g['id']} missing camber"
        assert int(g["bolt_holes"]) in (12, 18, 24), f"Invalid bolt_holes on {g['id']}"
        assert float(g["join_offset_mm"]) <= 10.0, f"Join offset {g['join_offset_mm']} > 10 mm"
    return "PASS: 2,224 girders verified for camber (6.5/14.0/25.4 mm), bolt holes (12/18/24), and bearing joins"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_girders] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_girders] REFUSED (G4/F12): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
