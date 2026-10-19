#!/usr/bin/env python3
"""test_validators.py — the validators must be able to fail.

For every validator, a deliberately broken copy of the design is built and the
validator is run against it; the test asserts a non-zero exit and a FAIL line.
A validator with no failing test is decoration (packet Part VII §28).

    python3 portus/tools/test_validators.py
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DESIGN = os.path.join(ROOT, "design")


def copy_design(tmp):
    dst = os.path.join(tmp, "design")
    shutil.copytree(DESIGN, dst)
    return dst


def run(script, design, extra=()):
    p = subprocess.run([sys.executable, os.path.join(TOOLS, script), "--design", design, *extra],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ── mutations ───────────────────────────────────────────────────────────────
def m_drop_room(d):
    j = json.load(open(os.path.join(d, "PROGRAMME.json")))
    j["rooms"].pop()
    json.dump(j, open(os.path.join(d, "PROGRAMME.json"), "w"))


def m_drop_apartment(d):
    p = os.path.join(d, "APARTMENTS.csv")
    rows = list(csv.reader(open(p)))
    open(p, "w", newline="").write("\n".join(",".join(r) for r in rows[:-1]) + "\n")


def m_room_without_door(d):
    j = json.load(open(os.path.join(d, "PROGRAMME.json")))
    for r in j["rooms"]:
        if r["kind"] == "apartment_room":
            r["doors"] = 0
            break
    json.dump(j, open(os.path.join(d, "PROGRAMME.json"), "w"))


def m_unreachable(d):
    j = json.load(open(os.path.join(d, "PROGRAMME.json")))
    for r in j["rooms"]:
        if r["kind"] == "apartment_room":
            r["reachable"] = False
            break
    json.dump(j, open(os.path.join(d, "PROGRAMME.json"), "w"))


def m_duplicate_rhythm(d):
    j = json.load(open(os.path.join(d, "PROGRAMME.json")))
    j["buildings"][1]["module"] = j["buildings"][0]["module"]
    j["buildings"][1]["pitch"] = j["buildings"][0]["pitch"]
    j["buildings"][1]["storeys"] = j["buildings"][0]["storeys"]
    json.dump(j, open(os.path.join(d, "PROGRAMME.json"), "w"))


def m_bad_storey(d):
    j = json.load(open(os.path.join(d, "PROGRAMME.json")))
    j["buildings"][0]["storeys"][0]["h"] = 3.55
    json.dump(j, open(os.path.join(d, "PROGRAMME.json"), "w"))


def m_bad_bollards(d):
    j = json.load(open(os.path.join(d, "SYSTEMS.json")))
    j["bollards"][1]["x"] = j["bollards"][0]["x"] + 9.4
    json.dump(j, open(os.path.join(d, "SYSTEMS.json"), "w"))


def m_loading_door(d):
    p = os.path.join(d, "SCHEDULE.csv")
    rows = list(csv.DictReader(open(p)))
    for r in rows:
        if float(r["area_m2"]) > 400:
            r["loading_door"] = "0"
            break
    w = csv.DictWriter(open(p, "w", newline=""), fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)


TESTS = [
    ("v_programme: one room removed (1607 != 1608)", "v_programme.py", m_drop_room),
    ("v_programme: one apartment removed (207 != 208)", "v_programme.py", m_drop_apartment),
    ("v_programme: a room with no door", "v_programme.py", m_room_without_door),
    ("v_programme: an unreachable room", "v_programme.py", m_unreachable),
    ("v_programme: two buildings share a rhythm triple", "v_programme.py", m_duplicate_rhythm),
    ("v_scale: undeclared 3.55 m storey", "v_scale.py", m_bad_storey),
    ("v_scale: bollard spacing 9.40 m", "v_scale.py", m_bad_bollards),
    ("v_scale: large hall loses its loading door", "v_scale.py", m_loading_door),
]


def main():
    ok = True
    rows = []
    for name, script, mutation in TESTS:
        with tempfile.TemporaryDirectory() as tmp:
            d = copy_design(tmp)
            mutation(d)
            extra = ["--design-only"] if script == "v_scale.py" else []
            code, out = run(script, d, extra)
            failed = code != 0 and "FAIL" in out
            ok &= failed
            first = next((ln for ln in out.splitlines() if ln.startswith("FAIL:")), out.strip().splitlines()[-1])
            print(f"{'ok  ' if failed else 'MISS'} {name}: exit={code} :: {first[:110]}")
            rows.append(dict(test=name, validator=script, exit=code, detected=failed, line=first))
    # and the unbroken design must still pass (a validator that fails everything is useless)
    for script in ("v_programme.py", "v_scale.py"):
        extra = ["--design-only"] if script == "v_scale.py" else []
        code, out = run(script, DESIGN, extra)
        good = code == 0 and out.strip().endswith("PASS")
        ok &= good
        print(f"{'ok  ' if good else 'MISS'} {script} on the clean design: exit={code}")
        rows.append(dict(test=f"{script} clean design", validator=script, exit=code, detected=good))
    json.dump(dict(ok=ok, tests=rows), open(os.path.join(ROOT, "evidence", "validation",
                                                         "negative_tests.json"), "w"), indent=1)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
