from __future__ import annotations
from townsquare.kits.core import spawn_bevel_box, spawn_lathe

def build_roof_and_drainage(name, cx, cy, z_eaves, width, depth, pitch_deg, mat_roof, mat_copper, mat_snow, coll, **tags):
    objs = []
    # Main pitched roof blocks + snow layer (45mm thick) + copper gutter + downpipe
    objs.append(spawn_bevel_box(f"{name}_ROOF_DECK", (width + 0.40, depth + 0.40, 1.85), (cx, cy, z_eaves + 0.92), mat_roof, coll, bevel=0.005, role="roof", family="roof", **tags))
    objs.append(spawn_bevel_box(f"{name}_ROOF_SNOW", (width + 0.32, depth + 0.32, 0.045), (cx, cy, z_eaves + 1.86), mat_snow, coll, bevel=0.010, role="snow_perch", family="snow", **tags))
    objs.append(spawn_bevel_box(f"{name}_GUTTER_FRONT", (width + 0.30, 0.14, 0.10), (cx, cy - depth/2 - 0.18, z_eaves + 0.05), mat_copper, coll, role="gutter", family="roof", **tags))
    objs.append(spawn_lathe(f"{name}_DOWNPIPE", [(0.055, 0.0), (0.055, z_eaves)], (cx + width/2 - 0.22, cy - depth/2 - 0.08, 0.0), mat_copper, coll, segments=18, role="downpipe", family="roof", **tags))
    return objs
