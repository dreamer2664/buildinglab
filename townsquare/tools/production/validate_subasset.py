"""Actual fresh native reopen of a delivered full-map building/public/rig subasset."""
import bpy,os,json,sys,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'));from fingerprints import file_sha256
key=os.environ['SQUARE_ASSET'];isrig=key.startswith('P') and key!='PUBLIC';path=R/'.cache/fixed-people/rigs'/(key+'.blend') if isrig else R/'.cache/final-components/Native'/(key+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.context.view_layer.update();issues=[];meshes=[o for o in s.objects if o.type=='MESH'];missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
if not meshes:issues.append('No mesh geometry')
if missing:issues.append('Unpacked file images: '+str(missing))
metadata={};arms=[o for o in s.objects if o.type=='ARMATURE']
if isrig:
 if not arms or not all(len(o.data.bones)>20 for o in arms):issues.append('Editable anatomical armature missing/incomplete')
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.type=='MESH' and 'ANATOMICAL_BASE' in o.name:
   a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(o.name.encode()+a.tobytes())
  if o.type=='ARMATURE':
   for b in o.pose.bones:h.update((b.name+str(tuple(tuple(row) for row in b.matrix))).encode())
 fit=json.loads((R/'evidence/production'/('person-fit-'+key+'.json')).read_text())
 if h.hexdigest()!=fit['anatomy_and_pose_signature_after']:issues.append('Raw anatomical/rig-pose signature does not match inspected fit source')
 metadata['anatomical_and_pose_signature_actual']=h.hexdigest();metadata['hair_max_z_checks']=[]
 for fix in fit['fixes']:
  if fix.get('hair_below_cap_hem_regression')!='PASS':continue
  o=s.objects[fix['part']];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();z=max(((o.matrix_world@v.co).z for v in me.vertices),default=-999);ev.to_mesh_clear();ok=z<=fix['cut_plane_world_z_m']+.00002;metadata['hair_max_z_checks'].append({'hair':o.name,'actual_max_z':z,'limit':fix['cut_plane_world_z_m'],'pass':ok})
  if not ok:issues.append('Saved/reopened crown mask did not retain actual cap-hem clearance')
elif key.startswith('B'):
 programme=json.loads((R/'design/programme.json').read_text());building=next(b for b in programme['buildings'] if b['id']==key);fids=[f['id'] for f in building['floors']];actual=sorted({o.get('floor_id') for o in meshes if o.get('floor_id') in fids});metadata['occupied_floors']=actual
 if actual!=sorted(fids):issues.append('Occupied floors missing')
 for fid in fids:
  roomids={o.get('room_id') for o in meshes if o.get('floor_id')==fid and o.get('layer')=='finish'}
  for rid in roomids:
   if not any(o.get('floor_id')==fid and o.get('room_id')==rid and o.get('layer')=='furniture' for o in meshes):issues.append('No actual room furniture '+str(rid))
 if not all(t in bpy.data.texts for t in ['VIEW_TOOLS.py','VIEW_PRESETS.json']):issues.append('Offline component view helpers missing')
r={'asset':key,'status':'PASS' if not issues else 'FAIL','actual_factory_reopen':True,'path':str(path.relative_to(R)),'sha256':file_sha256(path),'blender_version':bpy.app.version_string,'mesh_objects':len(meshes),'armatures':len(arms),'packed_images':sum(bool(im.packed_file) for im in bpy.data.images),'unpacked_file_images':missing,'metadata':metadata,'issues':issues,'scope':'Actual saved subasset reopen/packed-image/geometry/editability/content consistency. No render-quality, animation-readiness or independent acceptance claim.'};(R/'evidence/production'/('native-subasset-'+key+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_NATIVE_SUBASSET_REOPEN',key,r['status'],flush=True);assert not issues,issues
