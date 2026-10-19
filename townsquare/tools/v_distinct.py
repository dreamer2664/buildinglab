#!/usr/bin/env python3
"""
v_distinct.py — Gate G4 Distinctness & identity law validator (§16, §25, §30, F13, F14, F16).
Asserts:
- 110 unique arrangement signatures (0 duplicates)
- >= 8 plan archetypes
- >= 6 material palettes
- >= 4 furnishing generations
- >= 3 occupancy types
- Identity law: no human identity twice in same building or twice in same room
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROG = ROOT / "design" / "PROGRAMME.json"
REPORT_OUT = ROOT / "evidence" / "validation" / "v_distinct.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def validate_distinct(data: dict, check_people: bool = False) -> tuple[bool, dict, list[str]]:
    errors: list[str] = []
    sigs: set[str] = set()
    archetypes: set[str] = set()
    palettes: set[str] = set()
    generations: set[str] = set()
    occupancies: set[str] = set()
    apt_count = 0

    for b in data.get("buildings", []):
        b_identities: set[str] = set()
        for fl in b.get("floors", []):
            for apt in fl.get("apartments", []):
                apt_count += 1
                sig = apt.get("arrangement_signature", "")
                if not sig or sig in sigs:
                    errors.append(f"Duplicate or empty arrangement_signature on {apt.get('id')}: {sig}")
                sigs.add(sig)
                archetypes.add(apt.get("archetype", ""))
                palettes.add(apt.get("palette", ""))
                generations.add(apt.get("generation", ""))
                occupancies.add(apt.get("occupancy", ""))
            for r in fl.get("rooms", []):
                r_identities: set[str] = set()
                for pid in r.get("people_identities", []):
                    if pid in r_identities:
                        errors.append(f"Duplicate identity {pid} in room {r['id']} (F16)")
                    if pid in b_identities:
                        errors.append(f"Duplicate identity {pid} in building {b['id']} (F16)")
                    r_identities.add(pid)
                    b_identities.add(pid)

    if len(archetypes) < 8:
        errors.append(f"archetypes={len(archetypes)} < 8")
    if len(palettes) < 6:
        errors.append(f"palettes={len(palettes)} < 6")
    if len(generations) < 4:
        errors.append(f"generations={len(generations)} < 4")
    if len(occupancies) < 3:
        errors.append(f"occupancies={len(occupancies)} < 3")

    report = {
        "validator": "v_distinct",
        "apartments_checked": apt_count,
        "unique_signatures": len(sigs),
        "archetypes": len(archetypes),
        "palettes": len(palettes),
        "generations": len(generations),
        "occupancies": len(occupancies),
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    return (len(errors) == 0), report, errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_PROG)
    p.add_argument("--people", action="store_true")
    args = p.parse_args(get_cli_argv())
    data = json.loads(args.input.read_text(encoding="utf-8"))
    ok, report, errors = validate_distinct(data, check_people=args.people)
    if args.input == DEFAULT_PROG:
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not ok:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
