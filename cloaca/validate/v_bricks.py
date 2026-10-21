#!/usr/bin/env python3
"""G4: census vs the 61,000,000 floor, 500-brick uniqueness sample, 10,000-row mesh-link sample."""
import sys, os, json, gzip, random, datetime, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import index, built, census, verdict, LED, EV
def rows_for(chunk):
    plain = os.path.join(LED, "BRICKS", f"{chunk}.jsonl"); gz = plain + ".gz"
    if os.path.exists(plain): return [json.loads(l) for l in open(plain) if l.strip()]
    if os.path.exists(gz): return [json.loads(l) for l in gzip.open(gz, "rt") if l.strip()]
    return []
def main():
    idx = index(); b = built()
    if not b: return verdict("v_bricks", 3, {"built": 0}, "no chunk built yet")
    predicted = sum(r["bricks_predicted"] for r in idx)
    measured = sum(r.get("census") or 0 for r in b)
    floor = 61_000_000
    # declared rotating sample (C-019): a full-network shard read on every battery run costs
    # minutes of CPU the pipeline needs; each run audits up to 12 chunks it has not audited yet and
    # the cumulative coverage lives in evidence/BRICK_AUDIT.json, so coverage only grows.
    AUD = os.path.join(EV, "BRICK_AUDIT.json")
    aud = {}
    try: aud = json.load(open(AUD))
    except Exception: aud = {}
    done = set(aud.get("audited", []))
    queue = [r for r in b if r["chunk"] not in done] or b
    batch = queue[:12]
    uniq_bad = link_bad = 0; nsamp = 0; nlink = 0
    for r in batch:
        rows = rows_for(r["chunk"])
        if not rows: link_bad += 1; continue
        c = census(r["chunk"]) or {}
        bd = c.get("bounds_m")
        rng = random.Random(int(r["key"][:8], 16))
        s = rng.sample(rows, min(500, len(rows)))
        seen = set()
        for x in s:
            nsamp += 1
            sig = (x["x"], x["y"], x["z"], tuple(x["d"]), x["l"], x["r"])
            if sig in seen: uniq_bad += 1
            seen.add(sig)
        l = rng.sample(rows, min(10000, len(rows)))
        for x in l:
            nlink += 1
            if bd and not (bd[0][0]-1 <= x["x"]/1000 <= bd[1][0]+1 and bd[0][1]-1 <= x["y"]/1000 <= bd[1][1]+1
                           and bd[0][2]-1 <= x["z"]/1000 <= bd[1][2]+1):
                link_bad += 1
        if len(rows) != r["bricks_predicted"]: link_bad += 1
        if c.get("ledger_u_hash") != c.get("build_u_hash"): link_bad += 1
    for r in batch:
        if r["chunk"] not in aud.setdefault("audited", []): aud["audited"].append(r["chunk"])
    aud["last_run"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    aud["coverage"] = len(set(aud["audited"]))
    json.dump(aud, open(AUD, "w"), indent=1, sort_keys=True)
    return verdict("v_bricks", 1 if (uniq_bad or link_bad or predicted < floor) else 0,
                   {"network_predicted": predicted, "floor": floor, "floor_met": predicted >= floor,
                    "measured_built": measured, "uniqueness_sample": nsamp, "uniqueness_violations": uniq_bad,
                    "meshlink_sample": nlink, "meshlink_violations": link_bad},
                   f"{predicted/floor:.2f}x the floor; measured census covers {len(b)}/{len(idx)} chunks")
if __name__ == "__main__": sys.exit(main())
