#!/usr/bin/env python3
"""v_panes.py — Validator for G3: 293,655 panes in PANES.jsonl; unique seeds; 1,245x254 mm; 100-pane sample"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    cnt = 0
    seeds = set()
    with open(os.path.join(BASE, "ledgers/PANES.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            cnt += 1
            row = json.loads(line)
            s = row["seed"]
            if neg and cnt == 500:
                s = next(iter(seeds))
            assert s not in seeds, f"Duplicate pane seed {s} at row {cnt}"
            seeds.add(s)
            d = row["dim"]
            assert abs(d[0] - 1245.0) <= 0.5 and abs(d[1] - 254.0) <= 0.5, f"Invalid pane dim {d}"
    assert cnt == 293655, f"Expected 293655 panes, got {cnt}"
    pt = json.load(open(os.path.join(BASE, "evidence/PANETEST.json"), encoding="utf-8"))
    assert pt["sample_size"] == 100 and pt["repeating_ripples_found"] == 0, "PANETEST failed"
    return f"PASS: panes={cnt}, unique_seeds={len(seeds)}, sample_100_repeats=0"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_panes] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_panes] REFUSED (G3): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
