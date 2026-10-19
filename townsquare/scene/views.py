#!/usr/bin/env python3
"""271 required camera definitions for Winterlichtplatz II (§27)."""
import json
from pathlib import Path

VIEWS_PATH = Path(__file__).resolve().parents[1] / "design" / "VIEWS.json"

def load_views():
    return json.loads(VIEWS_PATH.read_text(encoding="utf-8"))

if __name__ == "__main__":
    v = load_views()
    print(f"Loaded {len(v)} views")
