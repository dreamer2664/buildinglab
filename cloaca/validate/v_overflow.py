#!/usr/bin/env python3
"""G7/F38: six overflows, actuated on sim conditions alone. An actuation without a recorded driver
is a scripted actuation and fails."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, jsonl, jload, EV, LANE
def main():
    acts = list(jsonl(os.path.join(EV, "OVERFLOWS.jsonl")))
    acc = jload(os.path.join(EV, "OVERFLOW_ACCOUNTING.json"), {})
    t = jload(os.path.join(LANE, "TIDES.json"), {})
    decl = t.get("overflows", [])
    if not decl: return verdict("v_overflow", 3, {"declared": 0}, "no overflows declared in TIDES.json")
    probs = []
    if len(decl) != 6: probs.append(f"declared {len(decl)} != 6")
    nodriver = [a for a in acts if not a.get("driver")]
    if nodriver: probs.append(f"{len(nodriver)} actuations carry no driver (scripted actuation)")
    fired = {a["overflow"] for a in acts}
    long = list(jsonl(os.path.join(EV, "OVERFLOWS_LONG.jsonl")))
    fired |= {a["overflow"] for a in long}
    dead = [o["id"] for o in decl if o["id"] not in fired]
    if dead: probs.append(f"never actuated in the window or the 180-day run: {dead}")
    return verdict("v_overflow", 1 if probs else 0,
                   {"declared": len(decl), "actuations_28d": len(acts), "actuations_180d": len(long),
                    "overflows_actuated": len(fired), "scripted": len(nodriver), "dead": len(dead)},
                   "; ".join(probs) if probs else "every overflow opened on sim level and sim discharge")
if __name__ == "__main__": sys.exit(main())
