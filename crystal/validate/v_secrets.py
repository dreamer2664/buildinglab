#!/usr/bin/env python3
"""v_secrets.py — Validator for R3/§2.4/§41: Zero secrets, tokens, or ntfy topic literals in crystal/ or agents/paxton/"""
from __future__ import annotations
import json
import math
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_check(neg: bool = False) -> str:

    if neg:
        raise AssertionError("Simulated secret token leak caught by v_secrets")
    proc = subprocess.run(["bash", os.path.join(BASE, "tools/secret_scan.sh")], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, f"secret_scan failed: {proc.stdout} {proc.stderr}"
    return "PASS: secret_scan CLEAN across all files"


def main() -> int:
    neg = ("--inject-failure" in sys.argv) or (os.environ.get("CRYSTAL_NEGATIVE_TEST") == "1")
    try:
        msg = run_check(neg=neg)
        print(f"[v_secrets] {msg}")
        return 0
    except Exception as exc:
        print(f"[v_secrets] REFUSED (R3/§2.4/§41): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
