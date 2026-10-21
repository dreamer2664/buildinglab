#!/usr/bin/env python3
"""Reconcile evidence/HEARTBEATS.jsonl against the expected 7-minute tick.
Gap > 12 min -> HB-GAP row in evidence/HB_GAPS.jsonl. Never backfill (§1.5)."""
import json, os, datetime, sys
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(LANE, "evidence")
CADENCE = 7 * 60; TOL = 12 * 60
def rows(p):
    if not os.path.exists(p): return []
    return [json.loads(l) for l in open(p) if l.strip()]
def main():
    hb = rows(os.path.join(EV, "HEARTBEATS.jsonl"))
    got = sorted(datetime.datetime.strptime(r["t"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                 for r in hb if r.get("delivered"))
    gaps, out = [], rows(os.path.join(EV, "HB_GAPS.jsonl"))
    seen = {(r.get("a"), r.get("b")) for r in out}
    for a, b in zip(got, got[1:]):
        d = (b - a).total_seconds()
        if d > TOL:
            k = (a.isoformat(), b.isoformat())
            if k not in seen:
                gaps.append({"a": a.isoformat(), "b": b.isoformat(), "gap_min": round(d/60, 1),
                             "expected_beats_missed": int(d // CADENCE) - 1, "code": "HB-GAP"})
    now = datetime.datetime.now(datetime.timezone.utc)
    tail_gap = (now - got[-1]).total_seconds() / 60 if got else None
    if gaps:
        with open(os.path.join(EV, "HB_GAPS.jsonl"), "a") as f:
            for g in gaps: f.write(json.dumps(g) + "\n")
    exp_path = os.path.join(EV, "expected_ticks.jsonl")
    if got:
        with open(exp_path, "w") as f:
            t = got[0]
            while t <= now:
                f.write(json.dumps({"t": t.strftime("%Y-%m-%dT%H:%M:%SZ")}) + "\n"); t += datetime.timedelta(seconds=CADENCE)
    rep = {"t": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "beats_delivered": len(got), "beats_failed": len(hb) - len(got),
           "hb_gaps_new": len(gaps), "hb_gaps_total": len(out) + len(gaps),
           "last_beat_age_min": round(tail_gap, 1) if tail_gap is not None else None,
           "verdict": "OK" if not gaps and (tail_gap is None or tail_gap <= 12) else "HB-GAP"}
    with open(os.path.join(EV, "RECONCILE.jsonl"), "a") as f: f.write(json.dumps(rep) + "\n")
    print(json.dumps(rep))
    return 0
if __name__ == "__main__": sys.exit(main())
