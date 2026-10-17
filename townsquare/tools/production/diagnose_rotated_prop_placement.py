"""Read-only coordinates of actual rotated new props; no camera-based inference."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];rows=[]
for o in bpy.context.scene.objects:
 if any(k in o.name for k in ['B11_L02_BICYCLE_TYRE','B11_L02_SERVICE_BENCH_TOP','B12_L02_LIBRARY','B08_L02_TOY_CHEST']):
  pts=[o.matrix_world@Vector(v)for v in o.bound_box];rows.append({'name':o.name,'floor':o.get('floor_id'),'location':list(o.location),'world_bounds':[[min(p[a]for p in pts)for a in range(3)],[max(p[a]for p in pts)for a in range(3)]]})
(R/'evidence/production/R12-actual-rotated-prop-placement.json').write_text(json.dumps(rows,indent=2)+'\n');print('ACTUAL_ROTATED_PROP_POSITIONS',json.dumps(rows[:4]),flush=True)
