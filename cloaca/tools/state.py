#!/usr/bin/env python3
"""Recompute cloaca/evidence/STATE.json from what is actually on disk.

A beat whose numbers do not match the committed census is a false beat (§32),
so nothing here is declared: every field is measured from the lane.
"""
import json, os, sys, hashlib, subprocess, datetime

LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV   = os.path.join(LANE, "evidence")

def jload(p):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return {}

def jsonl_rows(p):
    if not os.path.exists(p): return []
    out = []
    with open(p) as f:
        for ln in f:
            ln = ln.strip()
            if not ln: continue
            try: out.append(json.loads(ln))
            except Exception: pass
    return out

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def main():
    idx  = jsonl_rows(os.path.join(LANE, "ledgers", "INDEX.jsonl"))
    inv  = jsonl_rows(os.path.join(LANE, "ledgers", "INVERTS.jsonl"))
    # brick census: sum of ledger rows across shards (the ledger is the monument)
    bricks = 0; brick_rows = 0; shards = 0
    bd = os.path.join(LANE, "ledgers", "BRICKS")
    if os.path.isdir(bd):
        for fn in sorted(os.listdir(bd)):
            if fn.endswith(".jsonl"):
                shards += 1
                rows = jsonl_rows(os.path.join(bd, fn))
                brick_rows += len(rows)
                for r in rows:
                    bricks += int(r.get("n", r.get("count", 1)))
    # mesh census: what blender actually built (dump_chunk output)
    mesh = 0
    cd = os.path.join(LANE, "evidence", "CENSUS")
    if os.path.isdir(cd):
        for fn in sorted(os.listdir(cd)):
            if fn.endswith(".json"):
                mesh += int(jload(os.path.join(cd, fn)).get("brick_objects", 0))
    eng = sorted(f for f in os.listdir(os.path.join(LANE, "engines")) if f.endswith(".blend")) if os.path.isdir(os.path.join(LANE, "engines")) else []
    stn = sorted(f for f in os.listdir(os.path.join(LANE, "stations")) if f.endswith(".blend")) if os.path.isdir(os.path.join(LANE, "stations")) else []
    defs_ = [d for d in jsonl_rows(os.path.join(EV, "DEFECTS.jsonl")) if d.get("state", "open") == "open"]
    ren  = jsonl_rows(os.path.join(EV, "RENDERS.jsonl"))
    try:
        commit = subprocess.check_output(["git", "-C", LANE, "rev-parse", "--short", "HEAD"],
                                         stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = "0000000"
    state = {
        "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent": "bazalgette", "task": "t-20261021-8511",
        "commit": commit,
        "chunks_indexed": len(idx), "chunks_target": 1320,
        "inverts_rows": len(inv),
        "brick_ledger_rows": brick_rows, "brick_census": bricks, "brick_mesh_objects": mesh,
        "brick_shards": shards, "brick_target": 61000000,
        "engines_done": len(eng), "engines_target": 22,
        "stations_done": len(stn), "stations_target": 4,
        "renders_done": len(ren), "renders_target": 1284,
        "defects_open": len(defs_),
        "census_equals_ledger": (bricks == mesh) if (bricks or mesh) else None,
    }
    state["pct"] = round(100.0 * (0.55 * state["brick_census"] / state["brick_target"]
                                  + 0.20 * state["chunks_indexed"] / state["chunks_target"]
                                  + 0.15 * state["engines_done"] / state["engines_target"]
                                  + 0.10 * state["renders_done"] / state["renders_target"]), 3)
    os.makedirs(EV, exist_ok=True)
    with open(os.path.join(EV, "STATE.json"), "w") as f:
        json.dump(state, f, indent=1, sort_keys=True)
    print(json.dumps(state, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
