#!/usr/bin/env python3
"""v_people.py — Validator for G8/F16: 2,400 visitors, 2,400 unique faces, 12 social strata per STRATA.md, zero identity swaps"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    vis = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/VISITORS.jsonl"), encoding="utf-8")]
    if neg:
        vis[10]["face_id"] = vis[0]["face_id"]
    assert len(vis) == 2400, f"Expected 2400 visitors, got {len(vis)}"
    faces = {v["face_id"] for v in vis}
    face_vecs = {tuple(v["face_vector_14"]) for v in vis}
    strata = {v["stratum"] for v in vis}
    assert len(faces) == 2400 and len(face_vecs) == 2400, "Duplicate visitor face identity detected"
    assert len(strata) == 12, f"Expected 12 strata, got {len(strata)}"
    return "PASS: 2,400 visitors, 2,400 unique faces/vectors across 12 Victorian social strata"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_people] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_people] REFUSED (G8/F16): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
