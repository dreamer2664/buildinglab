"""Read-only actual saved native camera/room geometry extraction; no artistic inspection inferred."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'));from fingerprints import file_sha256
views=json.loads(bpy.data.texts['VIEW_PRESETS.json'].as_string())['frames'];result={'source_native_sha256':file_sha256(bpy.data.filepath),'method':'Actual fresh native camera basis/orthographic scale and finished-room mesh world bounds. Labels/dimensions are technical overlays, not generated geometry.','plans':{}}
for f in views:
 if f['kind']!='plan':continue
 c=bpy.data.objects['VIEW|'+f['id']];rooms=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.get('floor_id')!=f['floor_id'] or o.get('layer')!='finish':continue
  ps=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(p[k] for p in ps) for k in range(3)];hi=[max(p[k] for p in ps) for k in range(3)];rooms.append({'room_id':o.get('room_id'),'world_centre':[(lo[k]+hi[k])/2 for k in range(3)],'world_bounds':[lo,hi]})
 mat=c.matrix_world;result['plans'][f['id']]={'floor_id':f['floor_id'],'building_id':f['building_id'],'camera_origin':list(mat.translation),'camera_right_world':list(mat.to_3x3()@Vector((1,0,0))),'camera_up_world':list(mat.to_3x3()@Vector((0,1,0))),'orthographic_scale_m':c.data.ortho_scale,'rooms':rooms}
assert len(result['plans'])==26;(R/'evidence/production/R11-plan-annotation-source.json').write_text(json.dumps(result,indent=2)+'\n');print('ACTUAL_NATIVE_PLAN_ANNOTATION_SOURCE26_EXTRACTED')
