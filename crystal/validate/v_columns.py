#!/usr/bin/env python3
"""v_columns.py — Validator for G4/F39: 3,300 hollow cast-iron columns with unique Fox & Henderson foundry marks (audit 200)"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    cols = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/COLUMNS.jsonl"), encoding="utf-8")]
    if neg:
        cols[7]["mark"] = cols[0]["mark"]
    assert len(cols) == 3300, f"Expected 3300 columns, got {len(cols)}"
    marks = {c["mark"] for c in cols}
    assert len(marks) == 3300, f"Duplicate column foundry marks: {len(marks)} unique of 3300"
    sample_200 = [cols[(i * 16) % 3300]["mark"] for i in range(200)]
    assert len(set(sample_200)) == 200 and all(m.startswith("FXH-SMETHWICK-1851-") for m in sample_200), "200-column mark audit failed"
    return "PASS: 3,300 columns, 3,300 unique foundry marks, 200-mark sample verified"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_columns] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_columns] REFUSED (G4/F39): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
