import bpy,json,hashlib,re,sys,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
image_registry={};all_reports=[]
for key in [f'B{i:02}' for i in range(1,13)]+['PUBLIC']+[f'P{i:02}' for i in range(1,13)]:
 with bpy.data.libraries.load(str(R/'.cache/render-chunks'/(key+('-fixed' if key.startswith('P') and key!='PUBLIC' else '')+'.blend')),link=False) as (a,b):
  if key.startswith('B') or key=='PUBLIC':b.collections=list(a.collections)
  else:b.objects=list(a.objects)
  if key=='PUBLIC':b.worlds=list(a.worlds)
 if key.startswith('B') or key=='PUBLIC':
  children={c for top in b.collections for c in top.children}
  for c in b.collections:
   if c not in children:s.collection.children.link(c)
 else:
  for o in b.objects:s.collection.objects.link(o)
 if key=='PUBLIC' and b.worlds:s.world=b.worlds[0]
 for im in list(bpy.data.images):
  if not im.packed_file:continue
  h=(hashlib.sha256(im.packed_file.data).hexdigest(),im.colorspace_settings.name)
  if h in image_registry and image_registry[h]!=im:
   im.user_remap(image_registry[h]);bpy.data.images.remove(im)
  else:image_registry[h]=im
 print('ASSEMBLED',key,'objects',len(s.objects),'images',len(bpy.data.images),flush=True)
s.name='Winterlichtplatz / memory-bounded render derivative'
s['source_checkpoint_sha256']='4bf44a021c3df796388b61fab54e3ba92a4d823687686928020ef9da1276d776';s['candidate_revision']='R4 / scarf drape and cap fitting corrections';s['derivative_notice']='Original building/public geometry plus documented R4 accessory-fitting corrections on12 anatomically conserved human rigs; photographic maps resampled for rendering. Full-resolution native separately supplied.'
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04
s.cycles.max_bounces=8;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=4;s.cycles.transparent_max_bounces=8
s.render.resolution_x=1024;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
cam=bpy.data.objects.new('VIEW / Christmas square',bpy.data.cameras.new('VIEW / calibrated camera'));s.collection.objects.link(cam);s.camera=cam
cam.location=(30,-25,8);target=Vector((-12,21,5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=32
sys.path.insert(0,str(R/'tools/production'))
import view_tools
views=json.loads((R/'design/production-views.json').read_text())
for name,content in [('VIEW_PRESETS.json',json.dumps(views,indent=2)),('VIEW_TOOLS.py',(R/'tools/production/view_tools.py').read_text()),('READ_ME.txt','Winterlichtplatz R4.12 buildings,26 occupied floors,36 static people /12 separate editable rigs. Select a prepared view using: exec(bpy.data.texts[\'VIEW_TOOLS.py\'].as_string()); apply_view(\'B01_L01_cutaway\'). H02 restores whole-town visibility. Technical views hide ceilings/high walls intentionally. Native has all geometry; render-only culling never changes this saved source. Full-resolution source and lighter render derivative are separately labelled. Source maps are packed. Read external licence/portability and inspection records; no certification or independent acceptance is implied.')]:
 t=bpy.data.texts.new(name);t.write(content);t.use_fake_user=True
view_tools.add_cameras(views['frames']);bpy.data.objects.remove(cam,do_unlink=True);view_tools.apply_view('H02');bpy.context.view_layer.update()
from enrich_interiors import enrich
enrichment=enrich(R,views['frames']);bpy.context.view_layer.update()
# Data-only inventory and room bounds provide exact camera/review planning.
objects=[]
for o in s.objects:
 d={'name':o.name,'type':o.type,'props':dict(o.items()),'matrix_world':[list(row) for row in o.matrix_world]}
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  d.update(bounds_min=[min(p[i] for p in pts) for i in range(3)],bounds_max=[max(p[i] for p in pts) for i in range(3)],vertices=len(o.data.vertices),faces=len(o.data.polygons),materials=[m.name if m else None for m in o.data.materials])
 objects.append(d)
(R/'evidence/production/render-master-inventory.json').write_text(json.dumps({'objects':objects,'collections':[{'name':c.name,'props':dict(c.items())} for c in bpy.data.collections],'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images]},indent=2,default=str)+'\n')
(R/'.cache/master').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'.cache/master/Winterlichtplatz-render-R4.blend'),compress=True)
print('RENDER_MASTER_SAVED',len(s.objects),'images',len(bpy.data.images),flush=True)

def geom_signature():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.type!='MESH':continue
  h.update(o.name.encode());h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
  for seq,field,k,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'material_index',1,'i')]:
   a=array.array(typ,[0])*(len(seq)*k);seq.foreach_get(field,a);h.update(a.tobytes())
  for uv in o.data.uv_layers:
   a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
 return h.hexdigest()
g0=geom_signature()
from image_tools import upgrade_images
photo_restoration=upgrade_images(R,full_resolution=True)
g1=geom_signature();assert g0==g1
s['derivative_notice']='Full-resolution packed photographic source; actual R4 scarf drape/cap-fit corrections. Separate lighter render derivative has identical geometry, UVs, material assignments and poses.'
s['geometry_uv_pose_material_sha256']=g1
full=R/'.cache/master/Winterlichtplatz-R4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(full),compress=True)
h=hashlib.sha256()
with full.open('rb') as f:
 while b:=f.read(1024*1024):h.update(b)
report={'revision':'R4','geometry_uv_pose_material_signature_render_derivative':g0,'geometry_uv_pose_material_signature_full_resolution':g1,'geometry_uv_pose_material_conserved_between_versions':g0==g1,'full_resolution_native':str(full.relative_to(R)),'full_resolution_native_sha256':h.hexdigest(),'render_derivative':'.cache/master/Winterlichtplatz-render-R4.blend','photo_restoration':photo_restoration,'camera_presets':len(views['frames']),'occupied_floors':26,'people_instances':36,'human_variants':12,'visual_acceptance':'PENDING','independent_acceptance':'NOT GRANTED'}
(R/'evidence/production/R4-native-build.json').write_text(json.dumps(report,indent=2)+'\n');print('FULL_RESOLUTION_R4_NATIVE_SAVED_GEOMETRY_MATCH',g1,flush=True)
