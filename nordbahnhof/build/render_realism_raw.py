"""Physically lit raw Cycles render. No demodulation blur, fake GI or statistic caps."""
import bpy,sys,argparse,json,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--view',type=int,required=True);p.add_argument('--res',type=int,default=1024);p.add_argument('--samples',type=int,default=32);p.add_argument('--tile',default='full');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
r=Path(__file__).resolve().parents[1];scene=bpy.context.scene
# Audit the actual, unculled loaded source before any render-only memory budget changes.
audit=r/'evidence/REALISM_SCENE_AUDIT.json'
if not audit.exists():
 import re,hashlib
 identifiers=sorted({m.group(1) for ob in bpy.data.objects if (m:=re.match(r'TRAIN_(TR[0-9]+_V[0-9]+)',ob.name))})
 images=[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.type=='IMAGE']
 info={'status':'source inventory, not full commission acceptance','source':'source/NORDBAHNHOF_REALISM.blend','source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'mesh_objects':sum(ob.type=='MESH' for ob in bpy.data.objects),'polygons_in_mesh_datablocks':sum(len(me.polygons) for me in bpy.data.meshes),'vehicles':identifiers,'vehicle_count':len(identifiers),'rake_count':len({i.split('_')[0] for i in identifiers}),'scan_objects':[ob.name for ob in bpy.data.objects if ob.name.startswith('SCAN_HERO_')],'materials':len(bpy.data.materials),'cameras':[ob.name for ob in bpy.data.objects if ob.name.startswith('REALVIEW_')],'images':images,'all_image_assets_packed':all(i['packed'] for i in images),'limitations':['Static railway-inspired geometry, not operationally validated mechanisms','Six modern scanned people, not a period crowd of 400','Full room/identity/validator/310-view commission remains incomplete']}
 audit.write_text(json.dumps(info,indent=2))
# Remove saved construction orphans, never visible objects.
bpy.data.orphans_purge(do_recursive=True)
# Release full-resolution decoded buffers before Cycles' separate texture allocation.
for im in list(bpy.data.images):
 if im.type=='IMAGE' and im.name.startswith('diffuse.jpg') and im.size[0]>1024:
  w,h=im.size[:];im.scale(1024,round(h*1024/w));im.pack()
for im in bpy.data.images:
 if im.type=='IMAGE':im.buffers_free()
import ctypes
ctypes.CDLL('libc.so.6').malloc_trim(0)
print('RESIDENT_TEXTURES_BUDGETED',flush=True)
cams=sorted([o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('REALVIEW_')],key=lambda o:o.name);cam=cams[a.view-1];scene.camera=cam
# Render-only LOD: discard distant off-frame trains and closed interior fittings.
# Full station remains intact in the saved source, and structural shadow casters stay.
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
culled=[]
for ob in list(bpy.data.objects):
 if ob.type not in ('MESH','FONT') or not ob.name.startswith(('TRAIN_','RET_','WAIT_','BOARD_','BARRIER_')):continue
 vv=[world_to_camera_view(scene,cam,ob.matrix_world@Vector(q)) for q in ob.bound_box]
 outside=(ob.name.startswith(('RET_','WAIT_','BOARD_','BARRIER_')) or (ob.name.startswith('TRAIN_') and not ob.name.startswith('TRAIN_TR04_' if a.view==6 else 'TRAIN_TR01_')) or all(v.z<0 for v in vv) or all(v.x<-.25 for v in vv) or all(v.x>1.25 for v in vv) or all(v.y<-.25 for v in vv) or all(v.y>1.25 for v in vv))
 if outside:culled.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
ctypes.CDLL('libc.so.6').malloc_trim(0)
print('OFF_FRAME_DETAIL_LOD',len(culled),flush=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=a.samples;scene.cycles.use_adaptive_sampling=False;scene.cycles.use_denoising=False;scene.cycles.use_fast_gi=False;scene.cycles.seed=90124
scene.world.cycles.sampling_method='MANUAL';scene.world.cycles.sample_map_resolution=256
scene.cycles.use_light_tree=True;scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=8;scene.cycles.volume_bounces=1
scene.cycles.sample_clamp_direct=0;scene.cycles.sample_clamp_indirect=10;scene.cycles.filter_width=1.2
scene.use_nodes=False;scene.render.use_compositing=False
# Texture residency budget; the deliverable retains the original packed maps.
scene.render.use_simplify=True;scene.cycles.texture_limit_render='OFF'
scene.render.threads_mode='FIXED';scene.render.threads=2
vl=scene.view_layers[0];vl.use_pass_normal=True;vl.use_pass_diffuse_color=True
scene.render.resolution_x=a.res;scene.render.resolution_y=round(a.res*9/16);scene.render.resolution_percentage=100
W=scene.render.resolution_x;H=scene.render.resolution_y
if a.tile!='full':
 row,column=map(int,a.tile.split(','));x0=column*(W//2);x1=(column+1)*(W//2);y0=row*(H//2);y1=(row+1)*(H//2)
 A=max(0,x0-32);B=min(W,x1+32);C=max(0,y0-32);D=min(H,y1+32)
 scene.render.use_border=True;scene.render.use_crop_to_border=True;scene.render.border_min_x=A/W;scene.render.border_max_x=B/W;scene.render.border_min_y=C/H;scene.render.border_max_y=D/H
else:x0=0;x1=W;y0=0;y1=H;A=0;B=W;C=0;D=H;scene.render.use_border=False
out=r/'renders/realism/.cache';out.mkdir(parents=True,exist_ok=True)
key=cam.name+'_'+str(a.res)+'_'+a.tile.replace(',','-')
scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='16';scene.render.image_settings.exr_codec='ZIP';scene.render.filepath=str(out/(key+'.exr'))
start=time.time();bpy.ops.render.render(write_still=True)
meta={'key':key,'camera':cam.name,'view':a.view,'resolution':[W,H],'samples':a.samples,'source_sha256':json.loads(audit.read_text())['source_sha256'],'render_lod_culled_count':len(culled),'seconds':time.time()-start,'raw_region':[A,B,C,D],'destination':[x0,x1,y0,y1],'exposure':scene.view_settings.exposure,'look':scene.view_settings.look,'status':'raw rendered, not visually inspected'}
(out/(key+'.json')).write_text(json.dumps(meta,indent=2));print('RAW_READY',key,flush=True)
