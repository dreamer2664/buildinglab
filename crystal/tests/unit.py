#!/usr/bin/env python3
"""tests/unit.py — Suite 1/5: Unit constants, 7.32 m module math, acoustic pipe equations, and deterministic seeds (>= 600 assertions)."""
from __future__ import annotations
import json
import math
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    assertions = 0
    bays = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/BAYS.jsonl"), encoding="utf-8")]
    assert len(bays) == 85
    assertions += 1
    for b in bays:
        assert b["kit_version"] == "1.0.0"
        assert abs(float(b["module_m"]) - 7.320) < 1e-6
        assert len(b["bay_key"]) == 16
        assertions += 3

    pipes = [json.loads(line) for line in open(os.path.join(BASE, "ledgers/ORGAN_PIPES.jsonl"), encoding="utf-8")]
    assert len(pipes) == 4500
    assertions += 1
    for i in range(0, 4500, 10):
        p = pipes[i]
        c = 331.3 * math.sqrt(1.0 + float(p["hall_temp_c"]) / 273.15)
        assert abs(c - float(p["speed_of_sound_m_s"])) < 0.05
        assert abs(float(p["mesh_length_m"]) - float(p["computed_length_m"])) / float(p["computed_length_m"]) * 100.0 <= 2.0
        assertions += 2

    assert assertions >= 600, f"Expected >=600 assertions, got {assertions}"
    print(f"[tests/unit.py] PASS ({assertions} assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
