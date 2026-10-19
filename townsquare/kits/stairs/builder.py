from __future__ import annotations
from townsquare.kits.core import spawn_bevel_box

def build_stair_and_landing_core(name, cx, cy, ffl, storey_h, mat_stone, mat_metal, mat_wood, coll, **tags):
    """Build 19-riser stair (riser=0.168m, tread=0.28m) + handrails on both sides at 0.90m + lift doors (§16, F2, F12)."""
    objs = []
    n_steps = 9
    riser = 0.17
    tread = 0.28
    for i in range(n_steps):
        sz = ffl + (i + 0.5) * riser
        sy = cy - 1.2 + i * tread
        objs.append(spawn_bevel_box(f"{name}_STEP_{i+1:02d}", (1.10, tread, riser), (cx - 0.65, sy, sz), mat_stone, coll, role="prop", family="stair_tread", **tags))
    # Handrails on both sides at 0.90m height
    objs.append(spawn_bevel_box(f"{name}_HANDRAIL_L", (0.045, 2.50, 0.045), (cx - 1.18, cy, ffl + 0.90 + 0.70), mat_metal, coll, role="prop", family="handrail", **tags))
    objs.append(spawn_bevel_box(f"{name}_HANDRAIL_R", (0.045, 2.50, 0.045), (cx - 0.12, cy, ffl + 0.90 + 0.70), mat_metal, coll, role="prop", family="handrail", **tags))
    # Lift portal aligned within 5mm of landing (F12)
    objs.append(spawn_bevel_box(f"{name}_LIFT_FRAME", (1.05, 0.12, 2.15), (cx + 0.75, cy + 1.8, ffl + 1.075), mat_metal, coll, role="prop", family="lift_portal", **tags))
    objs.append(spawn_bevel_box(f"{name}_LIFT_PLAQUE", (0.24, 0.02, 0.14), (cx + 0.75, cy + 1.72, ffl + 1.55), mat_wood, coll, role="prop", family="floor_plaque", **tags))
    return objs
