"""Read-only diagnostic for actual native furnishing/material coordinates."""
import bpy,json,math
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[2];report={'actual_native':bpy.data.filepath,'floors':{}}
for fid,room in [('B02_L02','LIVING'),('B03_L02','FRONT_A'),('B03_L01','SALES'),('B07_L02',None),('B04_L01','SERVICE_A')]:
 rows=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH'or o.get('floor_id')!=fid:continue
  if fid!='B03_L01'and room is not None and o.get('room_id')!=fid+'_'+room:continue
  row={'name':o.name,'room':o.get('room_id'),'layer':o.get('layer'),'vertices':len(o.data.vertices),'materials':[]}
  if o.get('layer')=='furniture':
   for i,m in enumerate(o.data.materials):
    if not m:continue
    ids={v for p in o.data.polygons if p.material_index==i for v in p.vertices}
    if not ids:continue
    a=np.array([tuple(o.matrix_world@o.data.vertices[v].co)for v in ids]);row['materials'].append({'name':m.name,'actual_world_bounds':[a.min(axis=0).tolist(),a.max(axis=0).tolist()],'vertices':len(ids)})
  rows.append(row)
 report['floors'][fid]=rows
p=R/'evidence/production/R12-actual-clearance-source-coordinates.json';p.write_text(json.dumps(report,indent=2)+'\n');print('ACTUAL_NATIVE_CLEARANCE_SOURCE_COORDINATES_RECORDED',p)
