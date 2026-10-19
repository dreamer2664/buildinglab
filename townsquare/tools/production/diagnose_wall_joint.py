"""Read-only real mesh height distribution for the interior black-line investigation."""
import bpy,json,collections
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH'or o.get('floor_id')not in ['B11_L02','B04_L02','B02_L02']or o.get('layer')not in ['wall_low','wall_high','ceiling']:continue
 levels=collections.Counter(round((o.matrix_world@v.co).z,5)for v in o.data.vertices);rows.append({'object':o.name,'floor':o.get('floor_id'),'room':o.get('room_id'),'layer':o.get('layer'),'world_z_levels_most_common':levels.most_common(12),'min_world_z':min(levels),'max_world_z':max(levels)})
(R/'evidence/production/R12-actual-wall-joint-heights.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:
 if r['layer']!='ceiling':print('ACTUAL_WALL_Z',r,flush=True)
