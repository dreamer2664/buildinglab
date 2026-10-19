"""Measured UV-correspondence similarity fit and real head-bone parenting on NEW editable rig copy.
Original recovered rig immutable; skin/body/clothes/morphs/weights untouched, original hair object replaced.
"""
import bpy,sys,os,json,math
import numpy as np
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
from prototype_scalp_groom import non_hair_signature
pid=os.environ['SQUARE_GROOM_PID'];recovery=json.loads((R/'evidence/production/R12-actual-editable-rig-recovery.json').read_text());old=next(x for x in recovery['recovered_editable_rigs']if x['rig']==pid);assert file_sha256(bpy.data.filepath)==old['sha256'];a=json.loads((R/'evidence/production'/('R12-groom-accessory-'+pid+'.json')).read_text());assert file_sha256(R/a['native'])==a['native_sha256'];s=bpy.context.scene;bpy.context.view_layer.update();body=next(o for o in s.objects if o.type=='MESH'and any(m and m.name.endswith('.body')for m in o.data.materials));armatures=[o for o in s.objects if o.type=='ARMATURE'];assert len(armatures)==1;arm=armatures[0];head=next((p for p in arm.pose.bones if p.name.lower()=='head'),None);assert head is not None
nonhair_before={o.name:non_hair_signature(o.data,set())for o in s.objects if o.type=='MESH'and not any(m and'braid01'in m.name.lower()for m in o.data.materials)};oldhair=[o for o in s.objects if o.type=='MESH'and any(m and'braid01'in m.name.lower()for m in o.data.materials)];assert len(oldhair)==1
# Current evaluated skin in actual original rig world, matched by retained original skin UV coordinates.
deps=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(deps);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps);uv=me.uv_layers.active;mapping={}
for p in me.polygons:
 for li in p.loop_indices:
  t=uv.data[li].uv;key=(round(t.x,7),round(t.y,7));v=ev.matrix_world@me.vertices[me.loops[li].vertex_index].co;mapping.setdefault(key,[]).append(np.array(v,dtype=float))
X=[];Y=[]
for ref in a['head_skin_uv_correspondences']:
 candidates=mapping.get(tuple(ref['uv']),[])
 if not candidates:continue
 pts=np.array(candidates);mean=pts.mean(axis=0)
 if np.max(np.linalg.norm(pts-mean,axis=1))>1e-5:continue
 X.append(mean);Y.append(ref['co'])
ev.to_mesh_clear();assert len(X)>300,('Too few unambiguous measured UV correspondences',pid,len(X));X=np.array(X);Y=np.array(Y);mx=X.mean(axis=0);my=Y.mean(axis=0);xx=X-mx;yy=Y-my;U,D,Vt=np.linalg.svd(xx.T@yy);rot=U@Vt
if np.linalg.det(rot)<0:U[:,-1]*=-1;D[-1]*=-1;rot=U@Vt
scale=float(D.sum()/(xx*xx).sum());translation=my-scale*mx@rot;pred=scale*X@rot+translation;errors=np.linalg.norm(pred-Y,axis=1);rms=float(np.sqrt(np.mean(errors*errors)));maxerr=float(errors.max());assert rms<.0005 and maxerr<.003,('Measured head UV similarity fit fails',pid,len(X),rms,maxerr);T=np.eye(4);T[:3,:3]=scale*rot.T;T[:3,3]=translation;accessory_to_rig_world=Matrix(np.linalg.inv(T).tolist())
with bpy.data.libraries.load(str(R/a['native']),link=False)as(src,dst):dst.objects=list(src.objects)
objects=dst.objects;assert len(objects)==3
for o in oldhair:bpy.data.objects.remove(o,do_unlink=True)
coll=bpy.data.collections.new(pid+' / original physical scalp groom, native and explicit portableLOD');s.collection.children.link(coll)
for o in objects:
 coll.objects.link(o);o.name=pid+' / '+o.name;o.parent=arm;o.parent_type='BONE';o.parent_bone=head.name;bpy.context.view_layer.update();o.matrix_world=accessory_to_rig_world.copy();o['scope']='UNPROMOTED / actual measured source-head UV alignment and head-bone parent, not simulation';o.hide_render=bool(o.get('portable_hair_lod'));o.hide_set(o.hide_render)
bpy.context.view_layer.update();matrix_errors={o.name:max(abs(o.matrix_world[i][j]-accessory_to_rig_world[i][j])for i in range(4)for j in range(4))for o in objects};assert max(matrix_errors.values())<1e-5,('Parent alignment changed',matrix_errors)
# Actual head-bone movement/restore test, preserving all original transform-channel values.
channels={'location':head.location.copy(),'scale':head.scale.copy(),'rotation_euler':head.rotation_euler.copy(),'rotation_quaternion':head.rotation_quaternion.copy(),'rotation_axis_angle':tuple(head.rotation_axis_angle),'rotation_mode':head.rotation_mode};original_basis=head.matrix_basis.copy();start={o.name:o.matrix_world.copy()for o in objects};head.matrix_basis=original_basis@Matrix.Rotation(math.radians(5),4,'Z');bpy.context.view_layer.update();motion={o.name:max(abs(o.matrix_world[i][j]-start[o.name][i][j])for i in range(4)for j in range(4))for o in objects};assert min(motion.values())>1e-5
for prop,value in channels.items():setattr(head,prop,value)
bpy.context.view_layer.update();restored={o.name:max(abs(o.matrix_world[i][j]-start[o.name][i][j])for i in range(4)for j in range(4))for o in objects};assert max(restored.values())<1e-5
nonhair_after={name:non_hair_signature(bpy.data.objects[name].data,set())for name in nonhair_before};assert nonhair_before==nonhair_after,'Original body/clothes/UV/material assignment changed'
out=R/'.cache/groomed-editable-people';out.mkdir(parents=True,exist_ok=True);path=out/(pid+'-physical-groom-UNPROMOTED.blend');report={'rig':pid,'parent_original_rig_sha256':old['sha256'],'groom_accessory_sha256':a['native_sha256'],'actual_body_object':body.name,'actual_armature':arm.name,'actual_head_bone':head.name,'UV_correspondences':len(X),'actual_similarity_scale_rig_world_to_master_local':scale,'actual_UV_alignment_rms_metres':rms,'actual_UV_alignment_max_metres':maxerr,'accessory_to_original_rig_world_matrix':[list(row)for row in accessory_to_rig_world],'actual_parent_world_matrix_error':matrix_errors,'actual_5degree_head_bone_motion':motion,'actual_restored_original_pose_error':restored,'original_nonhair_geometry_UV_material_signatures_before':nonhair_before,'original_nonhair_geometry_UV_material_signatures_after':nonhair_after,'hair_native_objects':[o.name for o in objects],'limitations':'Head-bone rigid parenting actually tested; no dynamic hair simulation or automatic refit to changed face/head shape keys claimed. Native100kcurves, explicitly hidden6ktube PBR portableLOD. Other original rig/body/morph/weights untouched. UNPROMOTED; not photorealism/visual/independent approval.'};t=bpy.data.texts.new('PHYSICAL_GROOM_SOURCE_AND_LIMITATIONS.json');t.write(json.dumps(report,indent=2));t.use_fake_user=True;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);report.update(native=str(path.relative_to(R)),native_sha256=file_sha256(path),native_bytes=path.stat().st_size);(R/'evidence/production'/('R12-groomed-editable-rig-'+pid+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('MEASURED_HEAD_BONE_GROOM_RIG_SAVED',pid,report['native_bytes'],report['native_sha256'],'UV_RMS',rms,'MAX',maxerr,flush=True)
