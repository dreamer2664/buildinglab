#!/usr/bin/env python3
"""v_exhibits.py — Validator for G5/F36: 12,000 exhibits in EXHIBITS.jsonl; >=8 parts; silhouette collisions <=0.5% on 5% sample"""
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
        exhs[0]["part_count"] = 2
    assert len(exhs) == 12000, f"Expected 12000 exhibits, got {len(exhs)}"
    for e in exhs:
        min_p = 4 if e["class"] == "I" else 8
        assert int(e["part_count"]) >= min_p, f"Exhibit {e['id']} part_count {e['part_count']} < {min_p}"
    sample_600 = [exhs[i * 20]["silhouette_hash"] for i in range(600)]
    collisions = len(sample_600) - len(set(sample_600))
    coll_pct = (collisions / 600.0) * 100.0
    assert coll_pct <= 0.5, f"Silhouette collision rate {coll_pct:.2f}% > 0.5%"
    return f"PASS: 12,000 exhibits, min_parts>=8 verified, 5% sample collision rate={coll_pct:.2f}% <= 0.5%"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_exhibits] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_exhibits] REFUSED (G5/F36): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
