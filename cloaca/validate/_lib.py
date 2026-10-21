#!/usr/bin/env python3
"""Shared harness for the validator battery.

Exit codes are law: 0 = PASS, 1 = FAIL, 3 = PENDING (no subject yet).
A validator with no subject must return 3 and never 0 - "everything passes and the thing is
dead" is F34, and a PENDING that reads as a PASS is how it happens.
"""
import json, os, sys, datetime
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV   = os.path.join(LANE, "evidence"); LED = os.path.join(LANE, "ledgers")
PASS, FAIL, PENDING = 0, 1, 3

def jsonl(path):
    if not os.path.exists(path): return []
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if ln: yield json.loads(ln)

def jload(path, default=None):
    try:
        with open(path) as f: return json.load(f)
    except Exception: return default

def verdict(name, code, numbers, note=""):
    word = {PASS: "PASS", FAIL: "FAIL", PENDING: "PENDING"}[code]
    row = {"validator": name, "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "verdict": word, "exit": code, "numbers": numbers, "note": note}
    os.makedirs(EV, exist_ok=True)
    with open(os.path.join(EV, "VALIDATORS.jsonl"), "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    n = " ".join(f"{k}={v}" for k, v in numbers.items()) if isinstance(numbers, dict) else numbers
    print(f"{word:7s} {name:14s} {n}" + (f"  · {note}" if note else ""))
    return code

def index(): return list(jsonl(os.path.join(LED, "INDEX.jsonl")))
def inverts(): return list(jsonl(os.path.join(LED, "INVERTS.jsonl")))
def built(): return [r for r in index() if r.get("state") in ("built", "built-defect", "built-pruned")]
def census(c): return jload(os.path.join(EV, "CENSUS", f"{c}.json"))
