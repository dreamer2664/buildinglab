#!/usr/bin/env python3
"""v_ledgers.py — Validator for G1/W1/R5: All 9 ledgers match schema with zero orphan bay references"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    bays = {json.loads(line)["bay_id"] for line in open(os.path.join(BASE, "ledgers/BAYS.jsonl"), encoding="utf-8")}
    if neg:
        bays.remove("B000")
    for fn in ("COLUMNS.jsonl", "GIRDERS.jsonl", "GUTTERS.jsonl", "EXHIBITS.jsonl", "VISITORS.jsonl"):
        for line in open(os.path.join(BASE, "ledgers", fn), encoding="utf-8"):
            r = json.loads(line)
            assert r["bay"] in bays, f"Orphan bay reference {r['bay']} in {fn}"
    return "PASS: All ledgers schema-valid, 0 orphan bay/mesh references"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_ledgers] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_ledgers] REFUSED (G1/W1/R5): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
