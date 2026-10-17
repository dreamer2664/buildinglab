import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.get('building_id')!='B03' or o.get('floor_id') not in ['B03_L01','EXTERIOR','ROOF']:continue
 if o.get('layer') in ['furniture','fittings','branding']:continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];rows.append({'name':o.name,'props':dict(o.items()),'min':[round(min(x[i] for x in p),4) for i in range(3)],'max':[round(max(x[i] for x in p),4) for i in range(3)],'v':len(o.data.vertices),'faces':len(o.data.polygons)})
(R/'evidence/production/B03-envelope-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r)
