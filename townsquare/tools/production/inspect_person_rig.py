import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];bpy.context.view_layer.update();out=[]
for o in bpy.context.scene.objects:
 d={'name':o.name,'type':o.type,'location':list(o.location),'parent':o.parent.name if o.parent else None,'parent_bone':o.parent_bone,'properties':dict(o.items())}
 if o.type=='MESH':
  ps=[o.matrix_world@Vector(p) for p in o.bound_box];d['bounds']=[[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]];d['materials']=[m.name if m else None for m in o.data.materials]
 out.append(d)
(R/'evidence/production/rig-P01-actual-inventory.json').write_text(json.dumps(out,indent=2,default=str)+'\n');print('PERSON_RIG_INVENTORIED',len(out),flush=True)
