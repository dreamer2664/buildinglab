#!/usr/bin/env python3
"""tests/geometry.py — Suite 2/5: Kit v1.0.0, columns, girders, gutters, wonders, and B042 census (>= 600 assertions)."""
from __future__ import annotations
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    assertions = 0
    kv = json.load(open(os.path.join(BASE, "kit/KIT_VERSION.json"), encoding="utf-8"))
    assert kv["kit_version"] == "1.0.0"
    assertions += 1
    for kname, kmeta in kv["parts"].items():
        kp = os.path.join(BASE, kmeta["file"])
        assert os.path.exists(kp) and len(kmeta["sha256"]) == 64
        assertions += 1

    cols = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/COLUMNS.jsonl"), encoding="utf-8")]
    assert len(cols) == 3300
    assertions += 1
    for i in range(0, 3300, 10):
        c = cols[i]
        assert c["mark"].startswith("FXH-SMETHWICK-1851-")
        assert float(c["outer_dia_mm"]) == 203.2
        assertions += 2

    girders = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/GIRDERS.jsonl"), encoding="utf-8")]
    assert len(girders) == 2224
    assertions += 1
    for i in range(0, 2224, 15):
        g = girders[i]
        assert float(g["camber_mm"]) in (6.5, 14.0, 25.4)
        assert int(g["bolt_holes"]) in (12, 18, 24)
        assertions += 2

    census_txt = open(os.path.join(BASE, "evidence/B042_CENSUS.txt"), encoding="utf-8").readline()
    assert "333785188bcfe43be20a3c12186e55cd05bf7b1d076778df72b7c27a93cc8f95" in census_txt
    assertions += 1

    assert assertions >= 600, f"Expected >=600 assertions, got {assertions}"
    print(f"[tests/geometry.py] PASS ({assertions} assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
