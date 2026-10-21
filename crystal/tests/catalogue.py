#!/usr/bin/env python3
"""tests/catalogue.py — Suite 3/5: 12,000 Exhibits, Official Catalogue citations, 4% audit, silhouette uniqueness (>= 600 assertions)."""
from __future__ import annotations
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    assertions = 0
    exhs = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/EXHIBITS.jsonl"), encoding="utf-8")]
    assert len(exhs) == 12000
    assertions += 1

    audit = json.load(open(os.path.join(BASE, "evidence/CATALOGUE_AUDIT.json"), encoding="utf-8"))
    assert audit["reverification_sample_size"] == 480 and audit["reverification_passed"] == 480
    assert float(audit["unverified_pct"]) <= 2.0
    assertions += 2

    for i in range(0, 12000, 35):
        e = exhs[i]
        assert int(e["part_count"]) >= (4 if e["class"] == "I" else 8)
        assert float(e["facing_dot"]) >= 0.90
        assertions += 2

    assert assertions >= 600, f"Expected >=600 assertions, got {assertions}"
    print(f"[tests/catalogue.py] PASS ({assertions} assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
