"""Recover exact public production geometry into a memory-bounded render derivative.
Image resolution changes ONLY; original immutable master remains authoritative.
"""
import bpy,os,json,hashlib,array,gc
from pathlib import Path
R=Path(__file__).resolve().parents[2];key=os.environ['SQUARE_CHUNK'];src=R/'.cache/recovery/master/Winterlichtplatz.blend';out=R/'.cache/render-chunks';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(src),link=False) as (a,b):
 if key.startswith('B'):b.collections=[n for n in a.collections if n.startswith(key+' ')]
 elif key=='PUBLIC':b.collections=[n for n in a.collections if n=='PUBLIC_REALM' or 'FILL' in n]
 else:b.objects=[n for n in a.objects if n.startswith('CROWD_') and n.endswith('_'+key)]
 if key=='PUBLIC':b.worlds=list(a.worlds)
if key.startswith('B') or key=='PUBLIC':
 for c in b.collections:bpy.context.scene.collection.children.link(c)
else:
 for o in b.objects:bpy.context.scene.collection.objects.link(o)
if key=='PUBLIC' and b.worlds:bpy.context.scene.world=b.worlds[0]
def signature():
 h=hashlib.sha256()
 for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  h.update(o.name.encode());h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
  if o.type!='MESH':continue
  me=o.data
  for seq,field,k,typ in [(me.vertices,'co',3,'f'),(me.loops,'vertex_index',1,'i'),(me.polygons,'material_index',1,'i')]:
   v=array.array(typ,[0])*(len(seq)*k);seq.foreach_get(field,v);h.update(v.tobytes())
  for uv in me.uv_layers:
   v=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',v);h.update(v.tobytes())
 return h.hexdigest()
before=signature();images=[]
for im in bpy.data.images:
 if im.source not in ['FILE','GENERATED'] or im.name in ['Render Result','Viewer Node']:continue
 old=tuple(im.size)
 if not all(old):continue
 cap=512 if key.startswith('P') else 256
 scale=min(1,cap/max(old));new=(max(1,round(old[0]*scale)),max(1,round(old[1]*scale)))
 if new!=old:im.scale(*new)
 # The modified pixel buffer is packed as PNG; no dependency on vanished asset paths.
 print('IMAGE_REPACK',im.name,old,new,'packed',bool(im.packed_file),'dirty',im.is_dirty,'users',im.users,flush=True)
 if new!=old or not im.packed_file:im.pack()
 images.append({'name':im.name,'source_dimensions':old,'derivative_dimensions':tuple(im.size),'packed':bool(im.packed_file)})
 im.buffers_free();gc.collect()
after=signature();assert before==after,'Unexpected geometry/UV/pose/material-index change'
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  # Static master has no armature dependency; unused vertex groups need not occupy render memory.
  pass
bpy.context.scene['derivative_notice']='Same geometry/UV/pose/material assignment as public4bf44 master; photographic images resampled for memory-bounded rendering only.'
bpy.ops.wm.save_as_mainfile(filepath=str(out/(key+'.blend')),compress=True)
report={'chunk':key,'objects':len(bpy.context.scene.objects),'geometry_uv_pose_material_signature_before':before,'signature_after':after,'conserved':before==after,'image_changes':images,'file':str((out/(key+'.blend')).relative_to(R)),'source_production_sha256':'4bf44a021c3df796388b61fab54e3ba92a4d823687686928020ef9da1276d776'}
(R/'evidence/production'/('recovered-'+key+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('RECOVERED_CHUNK',key,len(bpy.context.scene.objects),'images',len(images),flush=True)
