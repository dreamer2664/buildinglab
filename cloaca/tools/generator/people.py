#!/usr/bin/env python3
"""G9 subjects: 120 figures, 120 faces, occupation-true poses, wear law. The ledger comes first
(R5): occupation schedule, place of work, pose drawn from the occupation's own movements, dress
from PERIOD.md, and a face id that is unique by construction - a hash of the figure's seed, never
reused. The figures are laid from this ledger by tools/build_people.py.

cloaca-people/1.2.0 (C-023, Director's instruction 2026-10-22): bodies are open-source scans,
not boxes. Each row carries a scan assignment from people/scan_lib (13 CC0 realistic humans,
provenance in evidence/SCAN_SOURCES.jsonl) plus deterministic per-figure variation: hue group,
yaw, scale jitter, stoop by age band, headgear and the tool the pose actually uses. The scans
are modern-clothed; the build recolours cloth to the period palette and adds period headgear,
so dress in this ledger remains the period truth the validator checks.
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

# scan pools from people/scan_lib (children leo/maya are held in the library but not assigned:
# the 120 are working adults; age_band 16-20 is carried by scale, not by child geometry)
MALE_SCANS = ["inn_abstract-white-man-3d-person-standing", "inn_abstract-white-man-3d-person-walking",
              "inn_daniel-3d-person-standing-casual", "inn_jordan-3d-person-athlete",
              "inn_male-base-mesh-3d-person-rigged-a-pose", "inn_walking-adult"]
FEMALE_SCANS = ["inn_abstract-white-woman-3d-person-standing", "inn_abstract-white-woman-3d-person-walking",
                "inn_amara-3d-person-standing-office", "inn_female-base-mesh-3d-person-rigged-a-pose",
                "inn_mei-3d-person-receptionist"]
WALKING_POSES = {"barrow-run", "walk", "load-guide", "rein-hold", "bread-carry"}
# the tool each pose actually puts in the hands (period-correct, from PARTS_SCHEDULE vocabulary)
TOOL = {"barrow-run": "barrow", "pick-swing": "pick", "shovel-stand": "shovel", "rammer": "rammer",
        "trowel-reach": "trowel", "line-sight": "line", "stoop-lay": "trowel", "gauge-read": "gauge",
        "oiler": "oilcan", "valve-turn": "spanner", "saw-stroke": "saw", "centring-fix": "mallet",
        "plane": "plane", "hammer-blow": "hammer", "bellows": "bellows", "forge-stand": "tongs",
        "point-shout": "none", "book-check": "book", "walk": "none", "rein-hold": "rein",
        "load-guide": "none", "stir-pot": "ladle", "bread-carry": "tray", "needle-work": "needle",
        "cloth-fold": "cloth"}
HEADGEAR = {"navvy": "cloth cap", "bricklayer": "felt hat", "engineman": "cloth cap",
            "carpenter": "cloth cap", "blacksmith": "bare", "ganger": "felt hat",
            "horse-driver": "felt hat", "cook": "cotton bonnet", "seamstress": "cotton bonnet"}

def main():
    rng = random.Random(20261022)
    rows = []; n = 0
    place_pool = []
    for pname, cnt in PLACES: place_pool += [pname] * cnt
    rng.shuffle(place_pool)
    for occ, cnt, poses in OCC:
        for i in range(cnt):
            n += 1
            fid = f"P-{n:03d}"
            seed = int(hashlib.sha256(fid.encode()).hexdigest()[:8], 16)
            sex = "female" if occ in ("cook", "seamstress") else "male"
            pose = rng.choice(poses)
            # scan choice: sex pool, walking scans for moving poses, deterministic by seed
            pool = FEMALE_SCANS if sex == "female" else MALE_SCANS
            walking = [s for s in pool if "walking" in s or "walk" in s]
            standing = [s for s in pool if s not in walking]
            if pose in WALKING_POSES and walking:
                scan = walking[seed % len(walking)]
            else:
                scan = standing[seed % len(standing)]
            age = rng.choice(["16-20", "21-30", "31-45", "46-60"])
            # per-figure variation, all deterministic from the seed
            vars_ = {"hue": seed % 3,                                  # three period hue groups per scan
                     "yaw_deg": round((seed >> 2) % 360, 1),
                     "scale": round(0.94 + ((seed >> 5) % 13) / 100.0, 3),  # 0.94..1.06, younger smaller
                     "stoop_deg": round(((seed >> 9) % 7), 1) if age == "46-60" else round(((seed >> 9) % 3), 1),
                     "tool": TOOL[pose], "headgear": HEADGEAR[occ]}
            if age == "16-20": vars_["scale"] = round(vars_["scale"] * 0.955, 3)
            face = hashlib.sha256(f"face-{seed}-{scan}-{vars_['hue']}".encode()).hexdigest()[:16]
            rows.append({"id": fid, "face_id": face, "occupation": occ, "gen": "cloaca-people/1.2.0",
                         "pose": pose, "place": place_pool[(n - 1) % len(place_pool)],
                         "dress": DRESS[occ], "wear": rng.sample(WEAR, 2),
                         "sex": sex, "age_band": age, "scan": scan, "vars": vars_, "seed": seed})
    assert len({r["face_id"] for r in rows}) == 120
    assert len({r["id"] for r in rows}) == 120
    with open(os.path.join(LANE, "ledgers/PEOPLE.jsonl"), "w") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    scans = len({r["scan"] for r in rows})
    print("people ledger:", len(rows), "figures,", len({r['face_id'] for r in rows}),
          "distinct faces,", scans, "scan sources, gen cloaca-people/1.2.0")

if __name__ == "__main__":
    main()
