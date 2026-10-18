"""Two separate actual file opens verify unchanged human geometry/UV/material assignment/world poses.
This does not rebind any old full-scene image acceptance to a changed town.
"""
import bpy,os,json,array,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
phase=os.environ['SQUARE_PEOPLE_COMPARE'];assert phase in ['latest','frozen'];E=R/'evidence/production';latest=json.loads((E/'R12-wall-corrected-interiors.json').read_text());frozen=json.loads((E/'R11-native-build.json').read_text());actual=file_sha256(bpy.data.filepath);assert actual==(latest['native_sha256']if phase=='latest'else frozen['render_derivative_sha256'])
rows=[];total=hashlib.sha256()
for o in sorted((o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('person_id')),key=lambda x:x.name):
 h=hashlib.sha256();h.update(o.name.encode());h.update(repr(tuple(tuple(row)for row in o.matrix_world)).encode());h.update(repr([m.name if m else None for m in o.data.materials]).encode())
 for seq,field,k,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'material_index',1,'i')]:
  a=array.array(typ,[0])*(len(seq)*k);seq.foreach_get(field,a);h.update(a.tobytes())
 for uv in o.data.uv_layers:
  a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
 digest=h.hexdigest();total.update(digest.encode());rows.append({'object':o.name,'person_id':o['person_id'],'geometry_uv_material_names_world_pose_sha256':digest})
r={'actual_opened_file_sha256':actual,'phase':phase,'people_mesh_objects':len(rows),'geometry_uv_material_names_world_pose_sha256':total.hexdigest(),'objects':rows,'scope':'Geometry/UV/material indices+names/world poses only, no pixel texture equivalence claim between resampled derivative/full source; old full-town image acceptance is not rebound.'};assert len(rows)==36;path=E/('R12-people-conservation-'+phase+'.json')
if phase=='frozen':
 other=json.loads((E/'R12-people-conservation-latest.json').read_text());assert other['geometry_uv_material_names_world_pose_sha256']==r['geometry_uv_material_names_world_pose_sha256'];r['comparison_status']='PASS';r['compared_latest_native_sha256']=other['actual_opened_file_sha256']
path.write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_PEOPLE_GEOMETRY_CONSERVATION',phase,r.get('comparison_status','CAPTURED'),r['geometry_uv_material_names_world_pose_sha256'],flush=True)
