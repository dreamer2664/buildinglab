#!/usr/bin/env python3
"""G13 reproduction clause, run by me as a rehearsal: rebuild a chunk from its ledger row and seed
alone, in a directory that has never seen the original, and compare the census hash.

The packet names S0042 as the reproduction chunk. A stranger's run is the one that counts; this row
records that the mechanism works and what it produced.
"""
import sys, os, json, hashlib, shutil, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); LANE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LANE, "tools", "generator"))
from lines import GEN_VERSION

def row_of(chunk):
    with open(os.path.join(LANE, "ledgers/INDEX.jsonl")) as f:
        for l in f:
            r = json.loads(l)
            if r["chunk"] == chunk: return r

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def reproduce(chunk, room="/tmp/cloaca_cleanroom"):
    r = row_of(chunk)
    if os.path.exists(room): shutil.rmtree(room)
    os.makedirs(os.path.join(room, "ledgers/BRICKS"), exist_ok=True)
    os.makedirs(os.path.join(room, "chunks"), exist_ok=True)
    os.makedirs(os.path.join(room, "evidence/CENSUS"), exist_ok=True)
    # the clean room gets: the ledger row (key, seed, profile), the generator, and nothing else.
    src = os.path.join(LANE, "ledgers/BRICKS", chunk + ".jsonl")
    if not os.path.exists(src): src += ".gz"
    dst = os.path.join(room, "ledgers/BRICKS", os.path.basename(src))
    shutil.copy2(src, dst)
    # the inputs a stranger receives: the master index row, the laid ledger, and the ledger-derived
    # metadata the builder reads back. Nothing else - no scene, no cached state.
    shutil.copy2(os.path.join(LANE, "ledgers/INDEX.jsonl"), os.path.join(room, "ledgers/INDEX.jsonl"))
    lmeta = os.path.join(LANE, "evidence/CENSUS", chunk + "_LEDGER.json")
    if os.path.exists(lmeta):
        shutil.copy2(lmeta, os.path.join(room, "evidence/CENSUS", chunk + "_LEDGER.json"))
    else:
        return {"chunk": chunk, "verdict": "FAIL", "reason": f"no {chunk}_LEDGER.json in the release payload"}
    for d in ("tools", "validate"):
        shutil.copytree(os.path.join(LANE, d), os.path.join(room, d), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(os.path.join(LANE, "PROFILE.json"), os.path.join(room, "PROFILE.json"))
    log = os.path.join(room, "rebuild.log")
    cmd = ["blender", "--background", "--factory-startup", "--python-exit-code", "1",
           "--python", os.path.join(room, "tools/build_chunk.py"), "--",
           "--chunk", chunk, "--save", "--out", os.path.join(room, "chunks", chunk + ".blend")]
    with open(log, "w") as f:
        p = subprocess.run(cmd, cwd=room, stdout=f, stderr=subprocess.STDOUT,
                           env=dict(os.environ, CLOACA_LANE=room))
    cens = os.path.join(room, "evidence/CENSUS", chunk + ".json")
    got = json.load(open(cens)) if os.path.exists(cens) else {}
    out = {"chunk": chunk, "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "generator_version": GEN_VERSION, "clean_room": room, "blender_exit": p.returncode,
           "key_from_index": r["key"], "bricks_predicted": r["bricks_predicted"],
           "rebuilt_brick_objects": got.get("brick_objects"), "rebuilt_census_hash": got.get("census_hash"),
           "index_census_hash": r.get("census_hash"), "rebuilt_u_hash": got.get("build_u_hash"),
           "index_u_hash": r.get("build_u_hash"), "u_hash_match": got.get("u_hash_match"),
           "census_hash_matches": got.get("census_hash") == r.get("census_hash"),
           "u_hash_matches": got.get("build_u_hash") == r.get("build_u_hash"),
           "census_equals_ledger": got.get("brick_objects") == r["bricks_predicted"],
           "rebuilt_blend_sha256": sha(os.path.join(room, "chunks", chunk + ".blend")) if os.path.exists(os.path.join(room, "chunks", chunk + ".blend")) else None,
           "rebuilt_peak_mb": got.get("peak_mb"), "rebuilt_build_s": got.get("build_s")}
    out["verdict"] = "PASS" if (out["blender_exit"] == 0 and out["census_hash_matches"] and
                                out["u_hash_matches"] and out["census_equals_ledger"]) else "FAIL"
    return out

if __name__ == "__main__":
    chunks = sys.argv[1:] or ["S0042"]
    rows = [reproduce(c) for c in chunks]
    with open(os.path.join(LANE, "evidence/REPRODUCTION.json"), "w") as f:
        json.dump({"generated": rows[0]["t"], "clause": "G13 clean-room reproduction (self-rehearsal; a stranger's run is the one that counts)",
                   "runs": rows}, f, indent=1)
    for r in rows:
        print(f"{r['verdict']} {r['chunk']}: census {r['rebuilt_brick_objects']} == predicted {r['bricks_predicted']} "
              f"· census_hash match {r['census_hash_matches']} · u_hash match {r['u_hash_matches']} · exit {r['blender_exit']}")
    sys.exit(0 if all(r["verdict"] == "PASS" for r in rows) else 1)
