"""Preserve verified R7 architecture/interiors exactly and replace only corrected R10 people."""
import bpy,sys,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import geometry_uv_pose_material_signature,file_sha256
from image_tools import upgrade_images
s=bpy.context.scene
def architecture_signature():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.type!='MESH' or o.name.startswith('CROWD_'):continue
  h.update(o.name.encode());h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
  for seq,field,k,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'material_index',1,'i')]:
   a=array.array(typ,[0])*(len(seq)*k);seq.foreach_get(field,a);h.update(a.tobytes())
  for uv in o.data.uv_layers:
   a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
 return h.hexdigest()
before=architecture_signature()
for o in list(s.objects):
 if o.name.startswith('CROWD_'):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
for n in range(1,13):
 pid=f'P{n:02}'
 with bpy.data.libraries.load(str(R/'.cache/render-chunks'/(pid+'-fixed.blend')),link=False) as (a,b):b.objects=list(a.objects)
 for o in b.objects:s.collection.objects.link(o)
print('R10_ALL36_PEOPLE_REPLACED',flush=True)
# Keep identical photographic textures shared. No pixels are read/decoded for this step.
registry={}
for im in list(bpy.data.images):
 if not im.packed_file:continue
 key=(hashlib.sha256(im.packed_file.data).hexdigest(),im.colorspace_settings.name)
 if key in registry:im.user_remap(registry[key]);bpy.data.images.remove(im)
 else:registry[key]=im
bpy.context.view_layer.update();after=architecture_signature();assert before==after
assert len([o for o in s.objects if o.name.startswith('CROWD_')])==36
s['candidate_revision']='R10 / original licensed hair/clothing; rejected optional hats and scarves removed'
s['derivative_notice']='R7 architecture/interiors retained exactly; R10 corrected static human instances. Separate full-resolution packed native has identical geometry, UVs, poses and material assignments.'
for t in bpy.data.texts:
 if t.name=='READ_ME.txt':
  text=t.as_string().replace('R7','R10');t.clear();t.write(text)
g0=geometry_uv_pose_material_signature();derivative=R/'.cache/master/Winterlichtplatz-render-R10.blend';bpy.ops.wm.save_as_mainfile(filepath=str(derivative),compress=True)
restoration=upgrade_images(R,full_resolution=True);g1=geometry_uv_pose_material_signature();assert g0==g1
for im in bpy.data.images:
 if im.packed_file:im.filepath='//packed/'+im.name
s['geometry_uv_pose_material_sha256']=g1;s['derivative_notice']='Full-resolution original photographic maps packed. R10 removal of rejected optional accessories with conserved raw anatomy/pose; separate render derivative has identical geometry/UV/pose/material indices.'
full=R/'.cache/master/Winterlichtplatz-R10.blend';bpy.ops.wm.save_as_mainfile(filepath=str(full),compress=True)
report={'revision':'R10','full_resolution_native':str(full.relative_to(R)),'full_resolution_native_sha256':file_sha256(full),'render_derivative':str(derivative.relative_to(R)),'render_derivative_sha256':file_sha256(derivative),'geometry_uv_pose_material_signature_render_derivative':g0,'geometry_uv_pose_material_signature_full_resolution':g1,'geometry_uv_pose_material_conserved_between_versions':True,'architecture_interiors_signature_before':before,'architecture_interiors_signature_after':after,'architecture_interiors_unchanged_from_R7':before==after,'camera_presets':92,'occupied_floors':26,'people_instances':36,'human_variants':12,'photo_restoration':restoration,'visual_acceptance':'PENDING','independent_acceptance':'NOT GRANTED'}
(R/'evidence/production/R10-native-build.json').write_text(json.dumps(report,indent=2)+'\n');print('R10_FULL_NATIVE_AND_DERIVATIVE_SAVED',report['full_resolution_native_sha256'],g1,flush=True)
