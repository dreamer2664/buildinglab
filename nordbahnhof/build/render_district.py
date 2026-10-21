import bpy,sys,argparse,time,json,ctypes
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--view',type=int,default=1);p.add_argument('--res',type=int,default=800);p.add_argument('--samples',type=int,default=12);p.add_argument('--proof',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;cams=sorted([o for o in bpy.data.objects if o.name.startswith('DISTVIEW_')],key=lambda o:o.name);scene.camera=cams[a.view-1]
# Render-only interior culling. Full railway remains in the saved source.
for ob in list(bpy.data.objects):
 if ob.type in ('MESH','FONT') and not ob.name.startswith(('DIST_','STATIC_BATCH_','CONC_01_Terrazzo_Floor')):bpy.data.objects.remove(ob,do_unlink=True)
 elif ob.name.startswith('STATIC_BATCH_') and not any(t in ob.name for t in ('limestone','painted petrol iron','historic glazing','recess','soot brown brick')):bpy.data.objects.remove(ob,do_unlink=True)
# Render-only whole-zone culling; source retains every building and figure.
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from collections import defaultdict
import re
zones=defaultdict(list)
for ob in bpy.data.objects:
 m=re.match(r'DIST_(B[0-9]+)_',ob.name)
 if m:zones[m.group(1)].append(ob)
for zone,obs in zones.items():
 points=[ob.matrix_world@Vector(q) for ob in obs if ob.type=='MESH' for q in ob.bound_box]
 mn=[min(v[i] for v in points)-4 for i in range(3)];mx=[max(v[i] for v in points)+4 for i in range(3)]
 vv=[world_to_camera_view(scene,scene.camera,Vector((x,y,z))) for x in (mn[0],mx[0]) for y in (mn[1],mx[1]) for z in (mn[2],mx[2])]
 if all(v.z<0 for v in vv) or all(v.x<-.25 for v in vv) or all(v.x>1.25 for v in vv) or all(v.y<-.25 for v in vv) or all(v.y>1.25 for v in vv):
  for ob in obs:bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(bpy.data.objects):
 if ob.type=='FONT' and ob.name.startswith('DIST_') and (ob.matrix_world.translation-scene.camera.location).length>65:bpy.data.objects.remove(ob,do_unlink=True)
 elif ob.name.startswith('DIST_B') and 'unbleached linen' in ob.name and (Vector(tuple(sum(v[i] for v in ob.bound_box)/8 for i in range(3)))-scene.camera.location).length>100:bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(bpy.data.objects):
 if not ob.name.startswith('DIST_PERSON_'):continue
 v=world_to_camera_view(scene,scene.camera,ob.location+Vector((0,0,.9)))
 if v.z<0 or v.x<-.1 or v.x>1.1 or v.y<-.1 or v.y>1.1:bpy.data.objects.remove(ob,do_unlink=True)
# Shared photographic-person geometry LOD, keyed by nearest visible instance.
# Keep close6k scans intact; distant full-body silhouettes do not need all face/finger triangles.
person_groups=defaultdict(list);person_lod=[]
for ob in bpy.data.objects:
 if ob.name.startswith('DIST_PERSON_'):person_groups[ob.data].append(ob)
for me,obs in person_groups.items():
 distance=min((ob.location-scene.camera.location).length for ob in obs);ratio=.25 if distance>30 else .5 if distance>15 else 1.0
 if ratio==1:continue
 temp=bpy.data.objects.new('DIST_TEMP_PERSON_LOD',me.copy());scene.collection.objects.link(temp);bpy.context.view_layer.objects.active=temp;temp.select_set(True)
 mod=temp.modifiers.new('Projected photographic crowd LOD','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);low=temp.data
 person_lod.append({'mesh':me.name,'nearest_metres':round(distance,2),'faces_before':len(me.polygons),'faces_after':len(low.polygons)})
 for ob in obs:ob.data=low
 bpy.data.objects.remove(temp,do_unlink=True)
 if me.users==0:bpy.data.meshes.remove(me)
# Clip only original station faces more than15m behind the camera; never edit the deliverable source.
import bmesh
forward=scene.camera.rotation_euler.to_matrix()@Vector((0,0,-1));origin=scene.camera.location
for ob in list(bpy.data.objects):
 if not ob.name.startswith('STATIC_BATCH_') or ob.type!='MESH':continue
 depths=[(ob.matrix_world@Vector(q)-origin).dot(forward) for q in ob.bound_box]
 if max(depths)<-15:bpy.data.objects.remove(ob,do_unlink=True);continue
 if min(depths)>-15:continue
 bm=bmesh.new();bm.from_mesh(ob.data)
 dead=[f for f in bm.faces if all((ob.matrix_world@v.co-origin).dot(forward)<-15 for v in f.verts)]
 if dead:bmesh.ops.delete(bm,geom=dead,context='FACES')
 loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(ob.data);bm.free()
bpy.data.orphans_purge(do_recursive=True)
# Preserve close photographic faces while budgeting distant pose maps by projected importance.
person_distance={}
for ob in bpy.data.objects:
 if not ob.name.startswith('DIST_PERSON_'):continue
 distance=(ob.location-scene.camera.location).length
 for slot in ob.material_slots:
  if not slot.material or not slot.material.use_nodes:continue
  for node in slot.material.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.image:person_distance[node.image]=min(distance,person_distance.get(node.image,1e9))
for im in bpy.data.images:
 if im.type=='IMAGE':
  limit=512 if a.proof else 1024
  if im in person_distance:
   distance=person_distance[im];preferred=1024 if distance<10 else 512 if distance<28 else 256;limit=min(limit,preferred)
  if im.size[0]>limit:
   im.scale(limit,round(im.size[1]*limit/im.size[0]));im.pack()
  im.buffers_free()
ctypes.CDLL('libc.so.6').malloc_trim(0)
scene.render.engine='CYCLES';scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=a.res;scene.render.resolution_y=round(a.res*9/16);scene.render.resolution_percentage=100
scene.cycles.samples=a.samples;scene.cycles.use_adaptive_sampling=False;scene.cycles.use_denoising=False;scene.cycles.max_bounces=5;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=6;scene.cycles.volume_bounces=0;scene.cycles.sample_clamp_indirect=8
scene.world.cycles.sampling_method='MANUAL';scene.world.cycles.sample_map_resolution=256
out=r/'renders/district';out.mkdir(parents=True,exist_ok=True);key=scene.camera.name+('_proof' if a.proof else '')
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=95;scene.render.filepath=str(out/(key+'.jpg'));start=time.time();print('RENDER_START',key,flush=True);bpy.ops.render.render(write_still=True)
(out/(key+'.json')).write_text(json.dumps({'camera':scene.camera.name,'width':a.res,'samples':a.samples,'elapsed_seconds':time.time()-start,'status':'rendered, pending visual inspection','person_lod_meshes':len(person_lod),'person_lod_faces_before_after':[sum(x['faces_before'] for x in person_lod),sum(x['faces_after'] for x in person_lod)],'render_only_culling':'Original train and interior fittings removed from render memory, not source.'},indent=2));print('RENDER_READY',key,flush=True)
