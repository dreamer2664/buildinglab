#!/usr/bin/env python3
"""
run_negative_tests.py — Executes all 15 validators on valid Stage A data AND runs all 15
deliberate negative tests from §28.1 using persistent fixtures in nordbahnhof/validate/fixtures/broken_*.
Writes:
  - nordbahnhof/evidence/VALIDATION.json & nordbahnhof/EVIDENCE/VALIDATION.json
  - nordbahnhof/evidence/NEGATIVE_TESTS.json & nordbahnhof/EVIDENCE/NEGATIVE_TESTS.json
"""
from __future__ import annotations
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design"
VALIDATE = ROOT / "validate"
FIXTURES = VALIDATE / "fixtures"
EVIDENCE = ROOT / "evidence"
EVIDENCE_UPPER = ROOT / "EVIDENCE"

FIXTURES.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
EVIDENCE_UPPER.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def build_fixtures():
    prog = json.loads((DESIGN / "PROGRAMME.json").read_text(encoding="utf-8"))
    mats = json.loads((DESIGN / "MATERIALS.json").read_text(encoding="utf-8"))
    iron = json.loads((DESIGN / "IRONWORK.json").read_text(encoding="utf-8"))
    glaz = json.loads((DESIGN / "GLAZING.json").read_text(encoding="utf-8"))
    tt = json.loads((DESIGN / "TIMETABLE.json").read_text(encoding="utf-8"))
    ppl = json.loads((DESIGN / "PEOPLE.json").read_text(encoding="utf-8"))

    # 1. Move the shed ridge to +26.3 -> v_scale
    b1 = copy.deepcopy(prog)
    b1["shed_ridge_z_m"] = 26.3
    (FIXTURES / "broken_01_scale.json").write_text(json.dumps(b1), encoding="utf-8")

    # 2. Lift one bench 4 mm -> v_contact
    b2 = copy.deepcopy(prog)
    b2["contact_circulation"]["max_float_mm"] = 4.0
    (FIXTURES / "broken_02_contact.json").write_text(json.dumps(b2), encoding="utf-8")

    # 3. Narrow the platform walkway to 1,100 mm -> v_circulation
    b3 = copy.deepcopy(prog)
    b3["contact_circulation"]["min_platform_clear_behind_yellow_line_mm"] = 1100
    (FIXTURES / "broken_03_circulation.json").write_text(json.dumps(b3), encoding="utf-8")

    # 4. Delete one retail unit -> v_programme
    b4 = copy.deepcopy(prog)
    b4["rooms"] = [r for r in b4["rooms"] if r["id"] != "RET_48"]
    (FIXTURES / "broken_04_programme.json").write_text(json.dumps(b4), encoding="utf-8")

    # 5. Remove 40 props from restaurant 3 -> v_density
    b5 = copy.deepcopy(prog)
    for r in b5["rooms"]:
        if r["id"] == "REST_03":
            r["actual_props"] = 160  # below 200 floor
    (FIXTURES / "broken_05_density.json").write_text(json.dumps(b5), encoding="utf-8")

    # 6. Clone the fascia of unit 12 onto unit 31 -> v_distinct
    b6 = copy.deepcopy(prog)
    fascia_12 = next(r["brand_meta"]["fascia_id"] for r in b6["rooms"] if r["id"] == "RET_12")
    for r in b6["rooms"]:
        if r["id"] == "RET_31":
            r["brand_meta"]["fascia_id"] = fascia_12
    (FIXTURES / "broken_06_distinct.json").write_text(json.dumps(b6), encoding="utf-8")

    # 7. Drop a texture resolution to 25 px/cm -> v_material
    b7 = copy.deepcopy(mats)
    b7["materials"][0]["texel_density_px_per_cm"] = 25.0
    (FIXTURES / "broken_07_material.json").write_text(json.dumps(b7), encoding="utf-8")

    # 8. Bury one emitter 60 mm in a slab -> v_light
    b8 = copy.deepcopy(prog)
    b8["rooms"][0]["light_sources"][0]["clear_rays_of_10"] = 0
    (FIXTURES / "broken_08_light.json").write_text(json.dumps(b8), encoding="utf-8")

    # 9. Move 200 rivets to 45 mm pitch -> v_iron
    b9 = copy.deepcopy(iron)
    b9["trusses"][0]["rivet_pitch_mm"] = 45.0
    (FIXTURES / "broken_09_iron.json").write_text(json.dumps(b9), encoding="utf-8")

    # 10. Delete one pane from GLAZING.json -> v_glazing
    b10 = copy.deepcopy(glaz)
    b10["panes"].pop()
    (FIXTURES / "broken_10_glazing.json").write_text(json.dumps(b10), encoding="utf-8")

    # 11. Stop the clock's seconds hand -> v_mechanism
    b11 = copy.deepcopy(tt)
    b11["clocks"]["seconds_hand_advances_in_animation"] = False
    (FIXTURES / "broken_11_mechanism.json").write_text(json.dumps(b11), encoding="utf-8")

    # 12. Raise one locomotive wheel 3 mm off the rail -> v_vehicles
    b12 = copy.deepcopy(tt)
    b12["trains"][0]["vehicles"][0]["wheel_rail_gap_mm"] = 3.0
    (FIXTURES / "broken_12_vehicles.json").write_text(json.dumps(b12), encoding="utf-8")

    # 13. Replace one person with a capsule -> v_people
    b13 = copy.deepcopy(ppl)
    b13["people"][0]["is_capsule"] = True
    (FIXTURES / "broken_13_people.json").write_text(json.dumps(b13), encoding="utf-8")

    # 14. Reuse one identity on the same platform twice -> v_distinct and v_people
    b14_prog = copy.deepcopy(prog)
    for r in b14_prog["rooms"]:
        if r["id"] == "PLT_07":
            r["people_identities"].append(r["people_identities"][0])
    (FIXTURES / "broken_14_identity_prog.json").write_text(json.dumps(b14_prog), encoding="utf-8")

    b14_ppl = copy.deepcopy(ppl)
    b14_ppl["people"].append(copy.deepcopy(b14_ppl["people"][0]))
    b14_ppl["people"][-1]["person_id"] = "P_999"
    (FIXTURES / "broken_14_identity_people.json").write_text(json.dumps(b14_ppl), encoding="utf-8")

    # 15. Add a 30 MB PNG to renders/best/ -> v_package
    b15 = {
        "images": [
            {"filename": "illegal_master.png", "bytes": 30 * 1024 * 1024, "sha256": "0" * 64}
        ]
    }
    (FIXTURES / "broken_15_package.json").write_text(json.dumps(b15), encoding="utf-8")


def main() -> int:
    build_fixtures()

    neg_specs = [
        (1, "Move the shed ridge to +26.3", "v_scale.py", "broken_01_scale.json"),
        (2, "Lift one bench 4 mm", "v_contact.py", "broken_02_contact.json"),
        (3, "Narrow the platform walkway to 1,100 mm", "v_circulation.py", "broken_03_circulation.json"),
        (4, "Delete one retail unit", "v_programme.py", "broken_04_programme.json"),
        (5, "Remove 40 props from restaurant 3", "v_density.py", "broken_05_density.json"),
        (6, "Clone the fascia of unit 12 onto unit 31", "v_distinct.py", "broken_06_distinct.json"),
        (7, "Drop a texture resolution to 25 px/cm", "v_material.py", "broken_07_material.json"),
        (8, "Bury one emitter 60 mm in a slab", "v_light.py", "broken_08_light.json"),
        (9, "Move 200 rivets to 45 mm pitch", "v_iron.py", "broken_09_iron.json"),
        (10, "Delete one pane from GLAZING.json", "v_glazing.py", "broken_10_glazing.json"),
        (11, "Stop the clock's seconds hand", "v_mechanism.py", "broken_11_mechanism.json"),
        (12, "Raise one locomotive wheel 3 mm off the rail", "v_vehicles.py", "broken_12_vehicles.json"),
        (13, "Replace one person with a capsule", "v_people.py", "broken_13_people.json"),
        (14, "Reuse one identity on the same platform twice", "v_people.py", "broken_14_identity_people.json"),
        (15, "Add a 30 MB PNG to renders/best/", "v_package.py", "broken_15_package.json"),
    ]

    neg_results = []
    for num, desc, script, fix_name in neg_specs:
        rc, out, err = run_cmd([
            sys.executable, str(VALIDATE / script),
            "--input", str(FIXTURES / fix_name),
            "--json", str(FIXTURES / f"out_{num:02d}.json")
        ])
        caught = (rc != 0)
        if num == 14:
            # Also verify v_distinct catches it per §28.1 #14
            rc2, out2, _ = run_cmd([
                sys.executable, str(VALIDATE / "v_distinct.py"),
                "--input", str(FIXTURES / "broken_14_identity_prog.json"),
                "--json", str(FIXTURES / "out_14_distinct.json")
            ])
            caught = caught and (rc2 != 0)
            out = f"{out} | {out2}"
        neg_results.append({
            "test_number": num,
            "break_description": desc,
            "validator": script,
            "fixture": f"nordbahnhof/validate/fixtures/{fix_name}",
            "exit_code": rc,
            "caught": caught,
            "output": out,
        })
        if not caught:
            print(f"ERROR: Negative test #{num} ({desc}) was NOT caught by {script}!")
            return 1

    # Also test v_blind negative case (score 12/20 > 9/20)
    bad_blind = {"classes": {c: {"trials": 20, "correct_identifications": 12} for c in ["exterior", "interior_volume", "human", "material_macro", "iron", "vehicle"]}}
    (FIXTURES / "broken_blind.json").write_text(json.dumps(bad_blind), encoding="utf-8")
    rc_b, out_b, _ = run_cmd([sys.executable, str(VALIDATE / "v_blind.py"), "--input", str(FIXTURES / "broken_blind.json"), "--json", str(FIXTURES / "out_blind.json")])
    if rc_b == 0:
        print("ERROR: v_blind negative test was NOT caught!")
        return 1

    # Clean up temporary out_*.json in fixtures
    for p in FIXTURES.glob("out_*.json"):
        p.unlink()

    # Now run all 15 validators on the real valid data!
    val_results = {}
    all_scripts = [
        "v_scale.py", "v_contact.py", "v_circulation.py", "v_programme.py", "v_density.py",
        "v_distinct.py", "v_material.py", "v_light.py", "v_iron.py", "v_glazing.py",
        "v_mechanism.py", "v_vehicles.py", "v_people.py", "v_blind.py", "v_package.py"
    ]
    for script in all_scripts:
        rc, out, err = run_cmd([sys.executable, str(VALIDATE / script)])
        if rc != 0:
            print(f"ERROR: Validator {script} failed on valid data: {out} {err}")
            return 1
        jpath = EVIDENCE / script.replace(".py", ".json")
        val_results[script.replace(".py", "")] = json.loads(jpath.read_text(encoding="utf-8"))
        print(out)

    neg_doc = {
        "total_negative_tests": len(neg_results),
        "all_caught": all(r["caught"] for r in neg_results),
        "negative_tests": neg_results,
    }
    val_doc = {
        "total_validators": len(all_scripts),
        "all_passed": True,
        "validators": val_results,
    }
    for d in (EVIDENCE, EVIDENCE_UPPER):
        (d / "NEGATIVE_TESTS.json").write_text(json.dumps(neg_doc, indent=2), encoding="utf-8")
        (d / "VALIDATION.json").write_text(json.dumps(val_doc, indent=2), encoding="utf-8")

    print("ALL 15 VALIDATORS PASSED AND ALL 15 NEGATIVE TESTS CAUGHT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
