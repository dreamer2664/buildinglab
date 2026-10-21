#!/usr/bin/env python3
"""v_bays.py — Validator for G1/G2: All 85 bays in BAYS.jsonl & bays/B000..B084.blend exist with unique bay_key"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    bays = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/BAYS.jsonl"), encoding="utf-8")]
    if neg:
        bays.pop()
    assert len(bays) == 85, f"Expected 85 bays, got {len(bays)}"
    keys = {b["bay_key"] for b in bays}
    assert len(keys) == 85, "Duplicate bay_key detected"
    for b in bays:
        bp = os.path.join(BASE, "bays", f"{b['bay_id']}.blend")
        assert os.path.exists(bp) and os.path.getsize(bp) > 1000, f"Missing bay file {bp}"
    return "PASS: 85/85 bays indexed and present on disk with unique keys"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_bays] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_bays] REFUSED (G1/G2): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
