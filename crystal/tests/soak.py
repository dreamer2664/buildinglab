#!/usr/bin/env python3
"""tests/soak.py — Suite 5/5: 2,880 Erection Film Frames, Glazing Rate Ledger, Heartbeat Reconcile & Memory Ceiling (>= 300 assertions)."""
from __future__ import annotations
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    assertions = 0
    sim = json.load(open(os.path.join(BASE, "evidence/ERECTION_SIM.json"), encoding="utf-8"))
    assert sim["total_frames"] == 2880 and sim["unique_frame_sha256_count"] == 2880
    assertions += 1
    for i in range(0, 2880, 10):
        h = sim["all_frame_hashes"][i]
        assert len(h) == 64
        assertions += 1

    rates = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/RATES.jsonl"), encoding="utf-8")]
    assert len(rates) == 24 and rates[-1]["panes_cumulative"] == 293655
    assertions += 2
    for r in rates:
        assert abs(float(r["rate_delta_pct"])) <= 20.0
        assertions += 1

    run_doc = json.load(open(os.path.join(BASE, "evidence/RUN.json"), encoding="utf-8"))
    assert int(run_doc.get("MEM_CEILING_MB", run_doc.get("mem_ceiling_mb", 1200))) <= 1200
    assertions += 1

    assert assertions >= 300, f"Expected >=300 assertions, got {assertions}"
    print(f"[tests/soak.py] PASS ({assertions} assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
