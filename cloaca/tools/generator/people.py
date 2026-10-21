#!/usr/bin/env python3
"""G9 subjects: 120 figures, 120 faces, occupation-true poses, wear law. The ledger comes first
(R5): occupation schedule, place of work, pose drawn from the occupation's own movements, dress
from PERIOD.md, and a face id that is unique by construction - a hash of the figure's seed, never
reused. The figures are laid from this ledger by tools/build_people.py.
"""
import os, json, random, hashlib, datetime
LANE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OCC = [("navvy", 54, ["barrow-run", "pick-swing", "shovel-stand", "rammer"]),
       ("bricklayer", 18, ["trowel-reach", "line-sight", "stoop-lay"]),
       ("engineman", 12, ["gauge-read", "oiler", "valve-turn"]),
       ("carpenter", 10, ["saw-stroke", "centring-fix", "plane"]),
       ("blacksmith", 6, ["hammer-blow", "bellows", "forge-stand"]),
       ("ganger", 6, ["point-shout", "book-check", "walk"]),
       ("horse-driver", 6, ["rein-hold", "load-guide"]),
       ("cook", 4, ["stir-pot", "bread-carry"]),
       ("seamstress", 4, ["needle-work", "cloth-fold"])]
DRESS = {"navvy": ["fustian shirt", "moleskin trousers", "cloth cap", "leather boots", "canvas apron"],
         "bricklayer": ["worsted jacket", "moleskin trousers", "felt hat", "leather boots", "wooden kneeler"],
         "engineman": ["wool jacket", "trousers", "cloth cap", "leather boots", "oil can at belt"],
         "carpenter": ["linen shirt", "corduroy trousers", "cloth cap", "leather boots", "tool belt"],
         "blacksmith": ["leather apron", "wool shirt", "trousers", "leather boots", "canvas gaiters"],
         "ganger": ["wool coat", "trousers", "felt hat", "leather boots", "brass whistle"],
         "horse-driver": ["wool coat", "trousers", "felt hat", "leather boots", "whip at shoulder"],
         "cook": ["cotton dress", "wool shawl", "cotton bonnet", "leather shoes"],
         "seamstress": ["cotton dress", "wool shawl", "cotton bonnet", "leather shoes"]}
WEAR = ["seat shine", "knee dust", "elbow polish", "hem mud", "shoulder fade", "cuff soot", "clean-best"]
PLACES = [("construction yard 1", 40), ("construction yard 2", 30), ("construction yard 3", 20),
          ("abbey_mills", 12), ("crossness", 8), ("deptford", 6), ("chelsea", 4)]
def main():
    rng = random.Random(20261021)
    rows = []; n = 0
    place_pool = []
    for pname, cnt in PLACES: place_pool += [pname] * cnt
    rng.shuffle(place_pool)
    for occ, cnt, poses in OCC:
        for i in range(cnt):
            n += 1
            fid = f"P-{n:03d}"
            seed = int(hashlib.sha256(fid.encode()).hexdigest()[:8], 16)
            face = hashlib.sha256(f"face-{seed}".encode()).hexdigest()[:16]
            rows.append({"id": fid, "face_id": face, "occupation": occ,
                         "pose": rng.choice(poses), "place": place_pool[(n - 1) % len(place_pool)],
                         "dress": DRESS[occ], "wear": rng.sample(WEAR, 2),
                         "sex": "female" if occ in ("cook", "seamstress") else "male",
                         "age_band": rng.choice(["16-20", "21-30", "31-45", "46-60"]),
                         "seed": seed})
    assert len({r["face_id"] for r in rows}) == 120
    with open(os.path.join(LANE, "ledgers/PEOPLE.jsonl"), "w") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    print("people ledger:", len(rows), "figures,", len({r['face_id'] for r in rows}), "distinct faces")
if __name__ == "__main__":
    main()
