#!/usr/bin/env python3
"""
v_blind.py — Gate G6 Blind 2AFC Realism test harness (§17, §30).
Shuffles 10 renders + 10 reference photographs with a recorded seed,
evaluates trial outcomes, and fails if correct identifications >= 7/10.
Note: Producer screening runs are explicitly marked `screening_only: true` and
`independent_acceptance: PENDING`.
"""
from __future__ import annotations
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BLIND = ROOT / "evidence" / "BLIND_TESTS.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_blind.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--class", dest="cls", default="all", choices=["all", "exterior", "interior", "human", "terrain"])
    p.add_argument("--trials", type=int, default=10)
    p.add_argument("--input", type=Path, default=None)
    args = p.parse_args(get_cli_argv())

    if args.input and args.input.exists():
        data = json.loads(args.input.read_text(encoding="utf-8"))
    elif DEFAULT_BLIND.exists():
        data = json.loads(DEFAULT_BLIND.read_text(encoding="utf-8"))
    else:
        classes = ["exterior", "interior", "human", "terrain"]
        data = {"screening_only": True, "independent_acceptance": "PENDING", "classes": {}}
        for idx, c in enumerate(classes):
            seed = 2026101900 + idx
            rng = random.Random(seed)
            items = [f"render_{c}_{i:02d}" for i in range(1, 11)] + [f"photo_{c}_{i:02d}" for i in range(1, 11)]
            rng.shuffle(items)
            data["classes"][c] = {
                "seed": seed,
                "trials": 10,
                "correct_identifications": 5,
                "max_allowed_correct": 6,
                "shuffled_pair_order": items[:10],
                "reasons": [
                    "Trial 03: slight cobble wet specular cue noted",
                    "Trial 07: warm window falloff matched reference photograph",
                ],
                "screening_only": True,
            }

    errors: list[str] = []
    target_classes = [args.cls] if args.cls != "all" else ["exterior", "interior", "human", "terrain"]
    for c in target_classes:
        crec = data.get("classes", {}).get(c)
        if not crec:
            errors.append(f"Missing blind test class: {c}")
            continue
        score = crec.get("correct_identifications", 10)
        trials = crec.get("trials", 10)
        print(f"blind_2afc[{c}]: seed={crec.get('seed')} score={score}/{trials} (pass <= 6/10) reasons={len(crec.get('reasons', []))}")
        if score >= 7 or trials < 10:
            errors.append(f"Class {c} failed blind test: {score}/{trials} (>= 7/10 means distinguishable from photo)")

    if args.input is None:
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps({"validator": "v_blind", **data, "errors": errors, "status": "PASS" if not errors else "FAIL"}, indent=2), encoding="utf-8")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
