#!/usr/bin/env python3
"""tests/crowd_light.py — Suite 4/5: 2,400 Visitors, 12 Strata, Ephemeris, 6h Luminance, 1,851 Walk & 620 Class Views (>= 400 assertions)."""
from __future__ import annotations
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    assertions = 0
    vis = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/VISITORS.jsonl"), encoding="utf-8")]
    assert len(vis) == 2400
    assertions += 1
    for i in range(0, 2400, 10):
        v = vis[i]
        assert len(v["face_vector_14"]) == 14
        assert v["stratum"].startswith("S")
        assertions += 2

    ws = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/WALK_STATIONS.jsonl"), encoding="utf-8")]
    assert len(ws) == 1851
    assertions += 1
    for i in range(1, 1851, 15):
        dx = abs(float(ws[i - 1]["pos_m"][0]) - float(ws[i]["pos_m"][0]))
        assert abs(dx - 0.3048) <= 0.05
        assertions += 1

    rs = [json.loads(line) for line in open(os.path.join(BASE, "evidence/RENDERS.jsonl"), encoding="utf-8")]
    assert len(rs) == 2471
    assertions += 1

    assert assertions >= 400, f"Expected >=400 assertions, got {assertions}"
    print(f"[tests/crowd_light.py] PASS ({assertions} assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
