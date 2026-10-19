"""Inspect-driven correction: remove rejected optional accessory studies; preserve original licensed outfit.
Preserves the anatomical mesh, photographed skin/clothing, armature and authored pose.
Outputs a full-resolution editable rig and a clearly labelled static render derivative.
"""
import bpy,os,json,hashlib,math,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];pid=os.environ['SQUARE_PERSON'];s=bpy.context.scene;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();changes=[]
def body_pose_signature():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.type=='MESH' and 'ANATOMICAL_BASE' in o.name:
   a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(o.name.encode()+a.tobytes())
  if o.type=='ARMATURE':
   for b in o.pose.bones:h.update((b.name+str(tuple(tuple(row) for row in b.matrix))).encode())
 return h.hexdigest()
before=body_pose_signature();cloth=next(o for o in s.objects if 'male_casualsuit05' in o.name);evaluated=cloth.evaluated_get(deps);me=evaluated.to_mesh();cloth_points=[cloth.matrix_world@v.co for v in me.vertices];evaluated.to_mesh_clear()
# Optional scarf studies failed macro quality (intersection, then raised mouth occlusion).
# Remove the accessory from the final outfit, rather than hide the defect by framing.
# Originals remain explicitly labelled, non-rendering editable alternatives in the rig.
for o in s.objects:
 if '_SCARF_' in o.name:
  o.hide_render=True;o['render_status']='REJECTED_OPTIONAL_ACCESSORY / not part of delivered outfit'
changes.append({'part':'optional scarf and fringe studies','fix':'Removed all optional scarf components from final outfit after actual close-ups rejected collar intersection and raised-wrap mouth occlusion. Original editable study meshes retained explicitly labelled, disabled for rendering; final town static meshes contain none of this rejected geometry. People keep actual licensed jacket, shirt, trousers, shoes, hair.'})
# Preserve the complete licensed hair and original scalp geometry. Experimental
# procedural hats failed a P03 macro fit after subdivision; they are not required
# by the brief. Remove these optional studies entirely from the final outfits,
# rather than crop the camera, alter anatomy, or cover the intersection.
for o in s.objects:
 if '_KNITTED_BEANIE' in o.name or '_BEANIE_RIB' in o.name or o.name==pid+'_RIB' or o.name.startswith(pid+'_RIB.'):
  o.hide_render=True;o['render_status']='REJECTED_OPTIONAL_HAT / not part of delivered outfit'
changes.append({'part':'optional procedural hat studies','fix':'Actual R9 D02 P03 forehead protrudes through subdivided hat: rejected. All optional procedural hat parts disabled in editable rigs and omitted from final static outfits. Full original licensed hair remains unmasked. Original skin, clothing, armature and authored pose conserved; no camera framing workaround.'})
bpy.context.view_layer.update();after=body_pose_signature();assert before==after,'Anatomical mesh or rig pose unexpectedly changed'
for o in s.objects:o['stage']='R10_ACCESSORY_FIT / anatomy and pose conserved'
rigdir=R/'.cache/fixed-people/rigs';rigdir.mkdir(parents=True,exist_ok=True);rigfile=rigdir/(pid+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(rigfile),compress=True)
h=hashlib.sha256()
with rigfile.open('rb') as f:
 while b:=f.read(1024*1024):h.update(b)
rigsha=h.hexdigest()
# Evaluate the actual masks, clothes, pose and UVs into static scene instances.
deps=bpy.context.evaluated_depsgraph_get();temps=[]
for o in list(s.objects):
 if o.type!='MESH' or o.hide_render:continue
 ev=o.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps);ob=bpy.data.objects.new('STATIC/'+o.name,mesh);s.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy();temps.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for o in temps:o.select_set(True)
bpy.context.view_layer.objects.active=temps[0];bpy.ops.object.join();static=bpy.context.view_layer.objects.active;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for o in list(s.objects):
 if o!=static:bpy.data.objects.remove(o,do_unlink=True)
mesh=static.data;sole=min(v.co.z for v in mesh.vertices);crowd=json.loads((R/'.cache/recovery/master/provenance/master-build.json').read_text())['crowd'];instances=[]
for n,item in enumerate(x for x in crowd if x['variant']==pid):
 ob=static if n==0 else bpy.data.objects.new('instance',mesh)
 if n:s.collection.objects.link(ob)
 ob.name=f"CROWD_{item['person_id']:02}_{pid}";ob.location=(*item['xy_m'],.006-sole);ob.rotation_euler=(0,0,item['rotation_rad'])
 for k,v in {'variant_id':pid,'person_id':item['person_id'],'role':item['role'],'building_id':'CROWD','layer':'people','floor_id':'PUBLIC','stage':'R10_ACCESSORY_FITTING_CORRECTED','rig_source_sha256':rigsha}.items():ob[k]=v
 instances.append(ob.name)
bpy.data.orphans_purge(do_recursive=True)
for im in bpy.data.images:
 if im.source!='FILE' or not all(im.size):continue
 oldsize=tuple(im.size);factor=min(1,512/max(oldsize));newsize=(max(1,round(oldsize[0]*factor)),max(1,round(oldsize[1]*factor)))
 if newsize!=oldsize:im.scale(*newsize);im.pack()
 im.buffers_free()
(R/'.cache/render-chunks').mkdir(parents=True,exist_ok=True)
chunk=R/'.cache/render-chunks'/(pid+'-fixed.blend');bpy.ops.wm.save_as_mainfile(filepath=str(chunk),compress=True)
report={'person':pid,'original_rig_public_package':'Winterlichtplatz-People-rigs-4bf44a021c3d.zip','corrected_rig':str(rigfile.relative_to(R)),'corrected_rig_sha256':rigsha,'anatomy_and_pose_signature_before':before,'anatomy_and_pose_signature_after':after,'anatomy_and_pose_conserved':before==after,'fixes':changes,'static_vertices':len(mesh.vertices),'static_faces':len(mesh.polygons),'static_instances':instances,'sole_before_placement_m':sole,'placed_sole_z_m':.006,'visual_reinspection':'PENDING'}
(R/'evidence/production'/('person-fit-'+pid+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('PERSON_ACCESSORIES_FIXED',pid,'static vertices',len(mesh.vertices),'rig preserved',rigsha,flush=True)
