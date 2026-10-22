#!/usr/bin/env python3
"""v_frames.py — Validator for G10: Erection film has exactly 2,880 unique 4K (3840x2160) frames (120.0 s at 24 fps), zero duplicates"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    sim = json.load(open(os.path.join(BASE, "evidence/ERECTION_SIM.json"), encoding="utf-8"))
    hashes = list(sim["all_frame_hashes"])
    if neg:
        hashes[100] = hashes[99]
    assert len(hashes) == 2880, f"Expected 2880 frames, got {len(hashes)}"
    assert len(set(hashes)) == 2880, f"Duplicate film frames found: {2880 - len(set(hashes))}"
    assert sim["resolution"] == [3840, 2160] and not sim["upscaled"], "Film resolution/upscale violation"
    return "PASS: 2,880/2,880 unique 3840x2160 frame SHA-256 hashes verified"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_frames] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_frames] REFUSED (G10): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
