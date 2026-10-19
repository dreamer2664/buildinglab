"""Read-only exact saved-source technical gates for separate photographic crowd candidate."""
import bpy,json,re,sys,hashlib,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256,geometry_uv_pose_material_signature
from scan_town_signatures import architecture_signature,architectural_material_photo_signature
b=json.loads((R/'evidence/production'/os.environ.get('SQUARE_SCAN_TOWN_BUILD_REPORT','R12-scanned-town.json')).read_text());actual=file_sha256(bpy.data.filepath);assert actual==b['native_sha256'];g=geometry_uv_pose_material_signature();assert g==b['geometry_uv_pose_material_signature'];a=architecture_signature();assert a==b['architecture_geometry_uv_pose_material_index_signature_before']==b['architecture_geometry_uv_pose_material_index_signature_after'];m=architectural_material_photo_signature();assert m==b['architectural_material_graph_and_photo_signature_before']==b['architectural_material_graph_and_photo_signature_after'];s=bpy.context.scene;actors=[o for o in s.objects if re.fullmatch(r'CROWD_\d\d_P\d\d',o.name)];assert len(actors)==36;poses={o['source_pose_id']for o in actors};assert len(poses)==12 and all(sum(o['source_pose_id']==p for o in actors)==3 for p in poses);assert len({p.split('-')[0]for p in poses})==8;assert not any(o.name.startswith('CROWD_')and o.type=='CURVES'for o in s.objects);assert not any(o.get('portable_hair_lod')for o in s.objects);assert len([o for o in s.objects if o.type=='CAMERA'and o.name.startswith('VIEW|')])==92
missing=[i.name for i in bpy.data.images if i.source=='FILE'and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing;floorids=sorted({o.get('floor_id')for o in s.objects if re.fullmatch(r'B\d\d_L\d\d',str(o.get('floor_id','')))});assert len(floorids)==26;soles=[];bounds=[]
for o in actors:
 lo=[min((o.matrix_world@Vector(p))[i]for p in o.bound_box)for i in range(3)];hi=[max((o.matrix_world@Vector(p))[i]for p in o.bound_box)for i in range(3)];assert abs(lo[2]-.006)<1e-5;assert .9<hi[2]-lo[2]<2.2;soles.append({'actor':o.name,'actual_sole_z_m':lo[2],'bounds':[lo,hi]});bounds.append((o.name,lo,hi))
overlap=[]
for i,(name,lo,hi)in enumerate(bounds):
 for other,lo2,hi2 in bounds[i+1:]:
  if all(min(hi[k],hi2[k])-max(lo[k],lo2[k])>1e-4 for k in range(3)):overlap.append([name,other])
images=[]
for image in bpy.data.images:
 if image.name.startswith('HSRD100_'):
  assert image.packed_file;raw=image.packed_file.data;assert raw[:8]==b'\x89PNG\r\n\x1a\n';images.append({'name':image.name,'packed_sha256':hashlib.sha256(raw).hexdigest(),'packed_png_dimensions':[int.from_bytes(raw[16:20],'big'),int.from_bytes(raw[20:24],'big')]})
assert len(images)==12 and all(x['packed_png_dimensions']==[4096,4096]for x in images);r={'status':'EXACT_NATIVE_FRESH_REOPEN_TECHNICAL_PASS_NOT_VISUAL_OR_INDEPENDENT_ACCEPTANCE','native_sha256':actual,'native_bytes':Path(bpy.data.filepath).stat().st_size,'geometry_uv_pose_material_index_signature':g,'unchanged_architecture_signature':a,'unchanged_architectural_material_graph_and_photo_signature':m,'occupied_floor_ids':floorids,'actual_people':36,'source_poses':12,'source_subject_ids':8,'saved_cameras':92,'missing_images':missing,'scan_packed_images':images,'actual_metric_soles_bounds':soles,'crowd_AABB_candidate_overlaps_not_actual_intersections':overlap,'limitations':'AABB overlap is broad phase, not collision certification. Actual scene view/lighting/source-capture patch/heel diagnostics and all92final/independent acceptance remain open.'};(R/'evidence/production'/os.environ.get('SQUARE_SCAN_TOWN_REOPEN_REPORT','R12-scanned-town-reopen.json')).write_text(json.dumps(r,indent=2)+'\n');print('SCANNED_TOWN_EXACT_FRESH_REOPEN_TECHNICAL_PASS',actual,'FLOORS26 PEOPLE36 POSES12 SUBJECTS8 CAMERAS92','AABB_CANDIDATES',overlap,flush=True)
