"""Save NEW full editable unpromoted town with inspected physical groom candidates.
Old wall-corrected source immutable. Original skin/clothes geometry+UV+material conservation asserted.
High native hair curves and explicit hidden portable tube LOD are different representations.
"""
import bpy,bmesh,sys,json
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256,geometry_uv_pose_material_signature,hair_geometry_signature
from prototype_scalp_groom import non_hair_signature
b=json.loads((R/'evidence/production/R12-wall-corrected-interiors.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];parent_sha=b['native_sha256'];coll=bpy.data.collections.new('PEOPLE / editable physical grooms and hidden portable LOD');bpy.context.scene.collection.children.link(coll);sources=[];changes=[];cache={}
for pid in ['P06','P12']:
 a=json.loads((R/'evidence/production'/('R12-groom-accessory-'+pid+'.json')).read_text());assert a['source_native_sha256']==parent_sha and file_sha256(R/a['native'])==a['native_sha256'];sources.append(a)
 actors=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'and o.name.startswith('CROWD_')and o.name.endswith('_'+pid)),key=lambda o:o.name);assert len(actors)==3
 with bpy.data.libraries.load(str(R/a['native']),link=False)as(x,y):y.objects=list(x.objects)
 templates=y.objects;assert len(templates)==3
 for actor in actors:
  old=actor.data;key=old.as_pointer();slots={i for i,m in enumerate(old.materials)if m and'braid01'in m.name.lower()};assert slots;before=non_hair_signature(old,slots)
  if key not in cache:
   actor.data=old.copy();bm=bmesh.new();bm.from_mesh(actor.data);faces=[f for f in bm.faces if f.material_index in slots];deleted=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES_ONLY');orphan=[v for v in bm.verts if not v.link_faces]
   if orphan:bmesh.ops.delete(bm,geom=orphan,context='VERTS')
   bm.to_mesh(actor.data);bm.free();actor.data.update();cache[key]=(actor.data,deleted)
  else:actor.data=cache[key][0];deleted=cache[key][1]
  after=non_hair_signature(actor.data,slots);assert before==after,'Skin/clothes/UV/materials unexpectedly changed';actor['hair_style']='Original physical short swept-back scalp groom;100k native curves, separate6kportableLOD'
  for template in templates:
   obj=template.copy();obj.data=template.data;kind='LOD'if obj.get('portable_hair_lod')else'CURVES'if obj.type=='CURVES'else'ROOTS';obj.name=f"CROWD_{int(actor['person_id']):02}_HAIR_{kind}_{pid}";coll.objects.link(obj);obj.parent=actor;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4);obj['person_id']=actor['person_id'];obj['variant_id']=pid;obj['layer']='people_hair'
   for prop in ['building_id','floor_id','room_id']:
    if prop in actor and actor[prop]is not None:obj[prop]=actor[prop]
   obj['scope']='UNPROMOTED physical groom in full editable town; no highrealism/final acceptance'
  changes.append({'actor':actor.name,'person_instance_id':actor['person_id'],'variant':pid,'actual_removed_hair_card_faces':deleted,'nonhair_geometry_uv_material_signature_before':before,'nonhair_geometry_uv_material_signature_after':after,'native_groom_curves':a['native_curves'],'portable_lod_strands':a['portable_lod_strands']})
 for obj in templates:bpy.data.objects.remove(obj,do_unlink=True)
scene=bpy.context.scene;scene['candidate_revision']='UNPROMOTED / measured wall and prop fixes plus original physical scalp grooms';scene['hair_portability_notice']='Native physical100kcurves per variant,3shared instances. Portable6ktube mesh per variant/PBR approximation, explicitly not strand-for-strand native/shader match.'
t=bpy.data.texts.get('VIEW_TOOLS.py');t.clear();t.write((R/'tools/production/view_tools.py').read_text())
from view_tools import apply_view
apply_view('H02');bpy.context.view_layer.update();lods=[o for o in scene.objects if o.get('portable_hair_lod')];curves=[o for o in scene.objects if o.type=='CURVES'];assert len(lods)==6 and all(o.hide_render for o in lods),'PortableLOD must be hidden in native';assert len(curves)==6 and all(not o.hide_render for o in curves),'Native physical curves must be visible';g=geometry_uv_pose_material_signature();hg=hair_geometry_signature();out=R/'.cache/scalp-groomed-town';out.mkdir(parents=True,exist_ok=True);native=out/'Winterlichtplatz-physical-groom-UNPROMOTED.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
r=dict(b);r.update(stage='NEW full editable UNPROMOTED physical-groom town; exact saved-source front/profile/P12/portableLOD/rig regression PENDING, no promotion',native=str(native.relative_to(R)),native_sha256=file_sha256(native),native_bytes=native.stat().st_size,parent_wall_corrected_native_sha256=parent_sha,actual_groom_variant_adaptations=changes,actual_groom_asset_sources=sources,geometry_uv_pose_material_signature=g,hair_curve_and_root_fade_signature=hg,images=[],inspection='PENDING / no parent image acceptance rebound');(R/'evidence/production/R12-groomed-town.json').write_text(json.dumps(r,indent=2)+'\n');print('NEW_FULL_EDITABLE_GROOMED_STUDY_SAVED',r['native_bytes'],r['native_sha256'],g,hg,flush=True)
