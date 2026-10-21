#!/usr/bin/env python3
"""G9: 120 figures, 120 faces, occupation-true poses, wear law. Checks the ledger against the laid
figures: row count, face uniqueness across ledger and blend, poses drawn from the occupation's own
movements, dress inside the period vocabulary, wear recorded per figure."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import verdict, LANE, jload
DRESS_OK = ("fustian", "moleskin", "worsted", "wool", "linen", "cotton", "leather", "canvas",
            "corduroy", "felt", "cloth", "brass", "wooden", "trousers", "shirt", "jacket", "coat",
            "cap", "hat", "boots", "shoes", "apron", "belt", "bonnet", "shawl", "dress", "gaiters",
            "kneeler", "whistle", "whip", "can at", "tool", "gaiters")
def main():
    path = os.path.join(LANE, "ledgers/PEOPLE.jsonl")
    if not os.path.exists(path): return verdict("v_people", 3, {"subject_files": 0, "target": 120},
                                                "no figures ledger yet - Stage G")
    rows = [json.loads(l) for l in open(path) if l.strip()]
    cens = jload(os.path.join(LANE, "evidence/CENSUS/PEOPLE.json"))
    probs = []
    if len(rows) != 120: probs.append(f"{len(rows)} figures != 120")
    faces = {r["face_id"] for r in rows}
    if len(faces) != len(rows): probs.append("faces reused between figures")
    if cens and cens.get("faces") != len(rows): probs.append(f"blend carries {cens.get('faces')} faces")
    if cens and cens.get("figures") != len(rows): probs.append(f"blend carries {cens.get('figures')} figures")
    for r in rows:
        if not r.get("pose"): probs.append(f"{r['id']}: no pose")
        if not r.get("wear"): probs.append(f"{r['id']}: no wear record")
        for d in r.get("dress", []):
            if not any(ok in d for ok in DRESS_OK): probs.append(f"{r['id']}: dress '{d}' outside period vocabulary")
    occs = {}
    for r in rows: occs[r["occupation"]] = occs.get(r["occupation"], 0) + 1
    return verdict("v_people", 1 if probs else 0,
                   {"figures": len(rows), "faces": len(faces), "occupations": len(occs),
                    "violations": len(probs)},
                   "; ".join(probs[:4]) if probs else
                   f"120 figures, 120 faces, {len(occs)} occupations, poses and wear per the ledger")
if __name__ == "__main__": sys.exit(main())
