#!/usr/bin/env python3
"""G12 blind battery: prepare 24 trials across 6 classes and score an independent runner's answers.

prepare:
  picks 4 compliant base views per class from evidence/RENDER_SCHEDULE.json, appends 24 control
  items (recipe blind_<class>, same scene/camera) to the schedule, and writes
  evidence/BLIND/trials.jsonl (public: the two image ids per trial, A/B order sealed by seed)
  plus evidence/BLIND/key.jsonl (which arm is the control). The runner sees only trials.jsonl
  and the rendered pairs; scoring needs the key, so the gate cannot be self-satisfied.
score:
  reads evidence/BLIND_ANSWERS.jsonl ({trial, pick: "A"|"B"}) and reports per-class accuracy
  against the key; a runner row only counts if the runner id is not this agent's.
"""
import json, os, random, sys, datetime
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20261022
CLASSES = {
    "light":   ("engine_house", "station_hero"),
    "palette": ("engine_house", "station_hero"),
    "bond":    ("engine_house", "station_hero"),
    "glazing": ("engine_house", "station_hero"),
    "tide":    ("overflow",),
    "dress":   ("people",),
}
def prepare():
    sched = json.load(open(os.path.join(LANE, "evidence/RENDER_SCHEDULE.json")))
    bycls = {}
    for it in sched:
        bycls.setdefault(it["recipe"], []).append(it)
    added, trials, key = [], [], []
    rng = random.Random(SEED)
    ti = 0
    for cls, bases in CLASSES.items():
        pool = [it for b in bases for it in bycls.get(b, [])]
        rng.shuffle(pool)
        for base in pool[:4]:
            ti += 1
            cid = "BL-" + base["id"]
            item = dict(base); item["id"] = cid; item["base_recipe"] = base["recipe"]
            item["recipe"] = "blind_" + cls; item["cls"] = base.get("cls", base["recipe"])
            added.append(item)
            flip = rng.random() < 0.5
            trials.append({"trial": ti, "class": cls,
                           "image_a": (cid if flip else base["id"]),
                           "image_b": (base["id"] if flip else cid)})
            key.append({"trial": ti, "class": cls, "control": "A" if flip else "B",
                        "control_id": cid, "compliant_id": base["id"]})
    ids = {it["id"] for it in sched}
    fresh = [a for a in added if a["id"] not in ids]
    sched.extend(fresh)
    tmp = os.path.join(LANE, "evidence/RENDER_SCHEDULE.json.tmp")
    with open(tmp, "w") as f:
        json.dump(sched, f, indent=0)
    os.replace(tmp, os.path.join(LANE, "evidence/RENDER_SCHEDULE.json"))   # atomic: loop reads concurrently
    os.makedirs(os.path.join(LANE, "evidence/BLIND"), exist_ok=True)
    with open(os.path.join(LANE, "evidence/BLIND/trials.jsonl"), "w") as f:
        for t in trials: f.write(json.dumps(t, sort_keys=True) + "\n")
    with open(os.path.join(LANE, "evidence/BLIND/key.jsonl"), "w") as f:
        for k in key: f.write(json.dumps(k, sort_keys=True) + "\n")
    print(f"prepared {len(trials)} trials ({len(fresh)} new control views scheduled); "
          f"classes: {sorted({t['class'] for t in trials})}")

def score():
    kp = os.path.join(LANE, "evidence/BLIND/key.jsonl")
    ap = os.path.join(LANE, "evidence/BLIND_ANSWERS.jsonl")
    if not os.path.exists(ap):
        print("no answers file yet: G12 awaits an independent runner"); return
    key = {json.loads(l)["trial"]: json.loads(l) for l in open(kp) if l.strip()}
    per = {}
    for l in open(ap):
        l = l.strip()
        if not l: continue
        a = json.loads(l)
        if a.get("runner", "") in ("bazalgette", "", None): continue   # own run does not count
        k = key.get(a.get("trial"))
        if not k: continue
        c = per.setdefault(k["class"], [0, 0])
        c[1] += 1
        if a.get("pick") == k["control"]: c[0] += 1
    tot = [0, 0]
    for cls in sorted(per):
        h, n = per[cls]; tot[0] += h; tot[1] += n
        print(f"class {cls}: {h}/{n} controls identified")
    print(f"battery: {tot[0]}/{tot[1]} trials correct by independent runners")

if __name__ == "__main__":
    (prepare if (sys.argv[1:] and sys.argv[1] == "prepare") else score)()
