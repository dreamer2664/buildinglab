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
    # brick census: sum of ledger rows across shards (the ledger is the monument).
    # C-020: the gz shard is the committed master; plain jsonl is transient (newer plain wins,
    # so a chunk is never counted twice). Line counts for gz masters are cached in
    # EV/.shard_cache.json keyed by (size, mtime) - a beat must not spend minutes recounting
    # 112 M rows every 7 minutes, and the cache is validated against the file stat each read.
    bricks = 0; brick_rows = 0; shards = 0
    per_chunk_ledger = {}
    bd = os.path.join(LANE, "ledgers", "BRICKS")
    cache_p = os.path.join(EV, ".shard_cache.json")
    cache = jload(cache_p)
    cache_dirty = False
    if os.path.isdir(bd):
        names = sorted(os.listdir(bd))
        plain = {fn[:-6] for fn in names if fn.endswith(".jsonl")}
        def count_lines_gz(path):
            import gzip
            n = 0
            with gzip.open(path, "rb") as f:
                for _ in f: n += 1
            return n
        for fn in names:
            if fn.endswith(".jsonl"):
                shards += 1
                rows = jsonl_rows(os.path.join(bd, fn))
                brick_rows += len(rows)
                per_chunk_ledger[fn[:-6]] = len(rows)
                for r in rows:
                    bricks += int(r.get("n", r.get("count", 1)))
            elif fn.endswith(".jsonl.gz") and fn[:-9] not in plain:
                p = os.path.join(bd, fn)
                st = os.stat(p)
                key = [st.st_size, int(st.st_mtime)]
                ent = cache.get(fn)
                if ent and ent.get("key") == key:
                    rows = ent["rows"]; nsum = ent["n"]
                else:
                    rows = count_lines_gz(p)
                    nsum = rows  # ledger rows carry no "n" field: one row == one brick (R5)
                    cache[fn] = {"key": key, "rows": rows, "n": nsum}
                    cache_dirty = True
                shards += 1
                brick_rows += rows
                per_chunk_ledger[fn[:-9]] = rows
                bricks += nsum
    if cache_dirty:
        with open(cache_p, "w") as f: json.dump(cache, f, sort_keys=True)
    # mesh census: what blender actually built (dump_chunk output)
    mesh = 0; chunks_built = 0
    per_chunk_mesh = {}
    cd = os.path.join(LANE, "evidence", "CENSUS")
    if os.path.isdir(cd):
        import re
        for fn in sorted(os.listdir(cd)):
            if fn.endswith(".json"):
                d = jload(os.path.join(cd, fn))
                b = int(d.get("brick_objects", 0))
                mesh += b
                m = re.fullmatch(r"(S\d{4})\.json", fn)
                if b and m:
                    chunks_built += 1
                    per_chunk_mesh[m.group(1)] = b
    eng = sorted(f for f in os.listdir(os.path.join(LANE, "engines")) if f.endswith(".blend")) if os.path.isdir(os.path.join(LANE, "engines")) else []
    stn = sorted(f for f in os.listdir(os.path.join(LANE, "stations")) if f.endswith(".blend")) if os.path.isdir(os.path.join(LANE, "stations")) else []
    defs_ = [d for d in jsonl_rows(os.path.join(EV, "DEFECTS.jsonl")) if d.get("state", "open") == "open"]
    ren  = jsonl_rows(os.path.join(EV, "RENDERS.jsonl"))
    try:
        commit = subprocess.check_output(["git", "-C", LANE, "rev-parse", "--short", "HEAD"],
                                         stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = "0000000"
    settled = set(per_chunk_mesh) & set(per_chunk_ledger)
    settled_n = len(settled)
    settled_mismatch = sum(1 for c in settled if per_chunk_mesh[c] != per_chunk_ledger[c])
    state = {
        "t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent": "bazalgette", "task": "t-20261021-8511",
        "commit": commit,
        "chunks_indexed": len(idx), "chunks_target": 1320,
        "chunks_built": chunks_built,
        "inverts_rows": len(inv),
        "brick_ledger_rows": brick_rows, "brick_census": bricks, "brick_mesh_objects": mesh,
        "brick_shards": shards, "brick_target": 61000000,
        "engines_done": len(eng), "engines_target": 22,
        "stations_done": len(stn), "stations_target": 4,
        "renders_done": len(ren), "renders_target": 1284,
        "defects_open": len(defs_),
        "census_equals_ledger": (settled_mismatch == 0) if settled_n else None,
        "census_settled_chunks": settled_n,
        "census_settled_mismatch": settled_mismatch,
        "census_racing_chunks": len(set(per_chunk_mesh) ^ set(per_chunk_ledger)),
    }
    # pct denominators are the PREDICTED totals, not the acceptance floors: C-001 predicts
    # 175,101,280 bricks for the 1,320-chunk network, so 61 M as a denominator would report
    # >100 % while 458 chunks are still unplaced. Floors gate acceptance; predictions gauge progress.
    PREDICTED_BRICKS = 175101280
    state["pct"] = round(100.0 * (0.55 * min(1.0, state["brick_census"] / PREDICTED_BRICKS)
                                  + 0.20 * min(1.0, state["chunks_built"] / state["chunks_target"])
                                  + 0.15 * state["engines_done"] / state["engines_target"]
                                  + 0.10 * state["renders_done"] / state["renders_target"]), 3)
    os.makedirs(EV, exist_ok=True)
    with open(os.path.join(EV, "STATE.json"), "w") as f:
        json.dump(state, f, indent=1, sort_keys=True)
    print(json.dumps(state, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
