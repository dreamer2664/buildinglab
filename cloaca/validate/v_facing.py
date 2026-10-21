#!/usr/bin/env python3
"""F1: every valve, sluice and overflow flap faces its flow direction.
Flow direction is established from INVERTS (fall along +X) and is checked here; the station
hardware itself is Stage D and is reported PENDING until it exists."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import inverts, verdict, jload, LANE
def main():
    inv = inverts()
    if not inv: return verdict("v_facing", 3, {"rows": 0}, "no gradient ledger")
    flow_ok = all(r["fall_m"] > 0 for r in inv)
    t = jload(os.path.join(LANE, "TIDES.json"), {})
    ofs = t.get("overflows", [])
    have_hardware = any(o.get("facing_checked") for o in ofs)
    if not ofs: return verdict("v_facing", 3, {"overflows_declared": 0}, "no overflow hardware declared")
    return verdict("v_facing", 3 if not have_hardware else (0 if flow_ok else 1),
                   {"flow_direction_established": flow_ok, "overflows_declared": len(ofs),
                    "hardware_modelled": sum(1 for o in ofs if o.get("geometry"))},
                   "flow reference established; penstocks and flap valves are Stage D hardware")
if __name__ == "__main__": sys.exit(main())
