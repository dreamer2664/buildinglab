import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import geometry_uv_pose_material_signature,file_sha256
b=json.loads((R/'evidence/production/R11-native-build.json').read_text());sig=geometry_uv_pose_material_signature();assert sig==b['geometry_uv_pose_material_signature_full_resolution']
huge=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if max(hi[i]-lo[i] for i in range(2))>150:huge.append({'name':o.name,'bounds_min':lo,'bounds_max':hi,'properties':dict(o.items()),'collections':[c.name for c in o.users_collection]})
r={'status':'PASS','actual_clean_derivative_reopen':True,'path':bpy.data.filepath,'sha256':file_sha256(bpy.data.filepath),'verified_geometry_uv_pose_material_signature':sig,'full_resolution_native_sha256':b['full_resolution_native_sha256'],'oversize_background_candidates':huge,'scope':'Actual reopened derivative matches full-resolution geometry/UV/material-index/world-pose signature. Frames verify exact input file SHA before render without forcing all out-of-view UV layers into memory.'};(R/'evidence/production/R11-render-derivative-reopen.json').write_text(json.dumps(r,indent=2)+'\n');print('DERIVATIVE_ACTUAL_REOPEN_AND_SOURCE_SIGNATURE_PASS',r['sha256']);print('OVERSIZE_BACKGROUNDS',json.dumps(huge))
