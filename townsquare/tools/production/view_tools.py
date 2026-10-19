"""Native view presets. Can run from embedded Blender text; no add-on/network needed.
exec(bpy.data.texts['VIEW_TOOLS.py'].as_string()); apply_view('B01_L01_cutaway')
All visibility changes are reversible: apply_view('H02') restores the whole town.
Render-only pruning is separate and NEVER modifies the saved source file.
"""
import bpy,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
RENDERABLE_TYPES={'MESH','CURVE','CURVES','SURFACE','META','FONT','VOLUME','LIGHT'}
ARCHITECTURAL_LAYERS={'wall_low','wall_high','ceiling','slab','exterior','roof','door','stairs'}
def _presets():
 import os
 override=os.environ.get('SQUARE_VIEW_PRESETS_FILE')
 if override:
  return json.loads(open(override,encoding='utf-8').read())['frames']
 return json.loads(bpy.data.texts['VIEW_PRESETS.json'].as_string())['frames']
def add_cameras(frames):
 s=bpy.context.scene
 for f in frames:
  name='VIEW|'+f['id'];cam=bpy.data.objects.get(name)
  if not cam:cam=bpy.data.objects.new(name,bpy.data.cameras.new(name));s.collection.objects.link(cam)
  cam.location=f['position'];cam.rotation_euler=(Vector(f['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=f.get('lens_mm',35);cam.data.clip_start=.04;cam.data.clip_end=1000
  if f.get('orthographic'):cam.data.type='ORTHO';cam.data.ortho_scale=f['ortho_scale']
  else:cam.data.type='PERSP'
  cam['view_id']=f['id'];cam['purpose']=f['title'];cam['visibility_script']='apply_view("'+f['id']+'")'
def _area(name,position,target,power,size,color=(1,1,1)):
 s=bpy.context.scene;l=bpy.data.lights.new('VIEWLIGHT/'+name,'AREA');l.energy=power;l.shape='DISK';l.size=size;l.color=color;o=bpy.data.objects.new(l.name,l);s.collection.objects.link(o);o.location=position;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def apply_view(view_id):
 frames=_presets();f=next(x for x in frames if x['id']==view_id);s=bpy.context.scene
 if not s.get('night_world_name') and s.world:s['night_world_name']=s.world.name
 for o in list(s.objects):
  if o.name.startswith('VIEWLIGHT/'):bpy.data.objects.remove(o,do_unlink=True)
 for o in s.objects:o.hide_render=False;o.hide_set(False)
 s.world=bpy.data.worlds.get(s.get('night_world_name','')) or s.world
 if not bpy.data.objects.get('VIEW|'+view_id):add_cameras(frames)
 s.camera=bpy.data.objects['VIEW|'+view_id];s.render.resolution_x,s.render.resolution_y=f['resolution'];s.render.resolution_percentage=100
 s.render.engine='CYCLES';s.cycles.samples=f['samples'];s.cycles.use_denoising=False;s.cycles.max_bounces=f.get('max_bounces',8);s.cycles.diffuse_bounces=f.get('diffuse_bounces',3);s.cycles.glossy_bounces=f.get('glossy_bounces',4);s.cycles.transparent_max_bounces=8;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.07;s.cycles.adaptive_min_samples=8
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.film_transparent=False;s.render.use_border=False;s.render.use_crop_to_border=False
 s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=f['exposure']
 if f['kind'] in ['plan','cutaway','interior']:
  fid=f['floor_id']
  for o in s.objects:
   if o.type not in RENDERABLE_TYPES:continue
   belongs=o.get('floor_id')==fid or any(c.get('floor_id')==fid for c in o.users_collection) or (f['kind']=='interior' and o.get('building_id')==f['building_id'] and (o.get('layer') in ARCHITECTURAL_LAYERS or o.get('floor_id') in ['EXTERIOR','ROOF']))
   o.hide_render=not belongs
   if f['kind'] in ['plan','cutaway'] and o.type!='LIGHT' and (o.get('layer') in ['ceiling','wall_high','exterior','lighting'] or o.get('cutaway_hide')):o.hide_render=True
   o.hide_set(o.hide_render)
  if f['kind'] in ['plan','cutaway']:
   w=bpy.data.worlds.get('VIEWLIGHT/Technical world') or bpy.data.worlds.new('VIEWLIGHT/Technical world');w.use_nodes=True;bg=w.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.72,.79,.92,1);bg.inputs['Strength'].default_value=.55;s.world=w
   target=f['target'];_area('Technical softbox',(target[0]-4,target[1]-5,target[2]+13),target,1800,12);_area('Technical fill',(target[0]+6,target[1]+3,target[2]+10),target,700,10)
 if f['kind']=='people':
  # Isolated, honestly labelled asset-inspection studio. Town integration is shown in H01-H06.
  for o in s.objects:
   if o.type in RENDERABLE_TYPES:
    o.hide_render=not(o.type!='LIGHT' and o.get('person_id') in f['person_ids']);o.hide_set(o.hide_render)
  w=bpy.data.worlds.get('VIEWLIGHT/People studio world') or bpy.data.worlds.new('VIEWLIGHT/People studio world');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.42,.46,.52,1);w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45;s.world=w
  ids=sorted({int(i)for i in f['person_ids']});anchors=[Vector((o.matrix_world.translation.x,o.matrix_world.translation.y,0))for o in s.objects if o.type=='MESH'and o.get('person_id')in ids]
  if len(anchors)>=2:origin=sum(anchors,Vector())/len(anchors)
  else:origin=Vector((f['target'][0],f['target'][1],0))
  # Cyclorama must sit BEHIND the subjects relative to the camera.
  away=origin-Vector((f['position'][0],f['position'][1],0));away.z=0
  top=away
  if top.length>.05:forward=top.normalized()
  else:
   lens=Vector((f['position'][0]-f['target'][0],f['position'][1]-f['target'][1],0)).normalized();right=Vector((lens.y,-lens.x,0));first=anchors[0]if anchors else origin;ordered=sorted(anchors,key=lambda p:(p-first).dot(right));forward=(ordered[-1]-ordered[0]).normalized()if len(ordered)>=2 and (ordered[-1]-ordered[0]).length>.05 else Vector((0,1,0))
  right=Vector((forward.y,-forward.x,0));profile=[(-50,0),(5,0)]+[(5+4*math.sin(i*math.pi/40),4*(1-math.cos(i*math.pi/40))) for i in range(1,21)]+[(9,20)];verts=[tuple(origin+forward*t+right*x+Vector((0,0,z))) for t,z in profile for x in [-50,50]];faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(profile)-1)];mesh=bpy.data.meshes.new('Seamless physical studio cyclorama');mesh.from_pydata(verts,[],faces);mesh.update();ground=bpy.data.objects.new('VIEWLIGHT/Studio inspection cyclorama',mesh);s.collection.objects.link(ground)
  for poly in mesh.polygons:poly.use_smooth=True
  mat=bpy.data.materials.get('VIEWLIGHT/Matte studio ground') or bpy.data.materials.new('VIEWLIGHT/Matte studio ground');mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.18,.2,.23,1);bsdf.inputs['Roughness'].default_value=.82;ground.data.materials.append(mat)
 if f.get('studio_key'):
  p=Vector(f['position'])+Vector((-.5,.2,1.3));_area('Close-human inspection key',p,f['target'],120,3.0,(1,.95,.89))
  q=Vector(f['target'])+(Vector(f['target'])-Vector(f['position']))*.5+Vector((.8,0,1.7));_area('Close-human rim',q,f['target'],70,2.0,(.78,.87,1))
 s['active_view_id']=view_id;s['active_view_description']=f['title']
 for o in s.objects:
  if o.get('portable_hair_lod'):o.hide_render=True;o.hide_set(True)
 bpy.context.view_layer.update();return f

def prune_for_render(frame,border=None,aggressive=False):
 """Memory optimization on an UNSAVED working copy only. Preserve architectural occluders.
 Offscreen clutter can alter reflected detail; aerial hides interior furniture under roofs.
 """
 s=bpy.context.scene;c=s.camera;bpy.context.view_layer.update();removed=[];reasons={}
 lo_x,hi_x,lo_y,hi_y=border if border else (0,1,0,1);margin=.10
 for o in list(s.objects):
  if o.type not in RENDERABLE_TYPES:continue
  reason=None
  behind=False
  if aggressive and o.type=='MESH' and frame['kind'] in ['building','village','town','aerial']:
   try:
    behind=all(world_to_camera_view(s,c,o.matrix_world@Vector(p)).z<0 for p in o.bound_box)
   except Exception:
    behind=False
  if o.hide_render:reason='selected floor / intentional cutaway visibility'
  elif behind:reason='entirely behind the camera plane (no possible visibility)'
  elif aggressive and frame['kind'] in ['building','village','town'] and o.get('layer') in ['furniture','finish','ceiling'] and not (frame['kind']=='building' and o.get('floor_id')==(frame.get('building_id') or '')+'_L01'):reason='interior layers enclosed by opaque exterior/roof in this exterior view; full interiors retained in editable native and rendered separately'
  elif o.type=='MESH' and frame['kind']=='aerial' and o.get('layer')=='furniture':reason='aerial roof-occluded interior furniture LOD; full interior source supplied and separately rendered'
  elif o.type=='MESH' and frame['kind'] not in ['plan','cutaway','interior'] and o.get('layer') not in ARCHITECTURAL_LAYERS:
   pts=[world_to_camera_view(s,c,o.matrix_world@Vector(p)) for p in o.bound_box]
   outside=all(p.z<0 for p in pts) or all(p.x<lo_x-margin for p in pts) or all(p.x>hi_x+margin for p in pts) or all(p.y<lo_y-margin for p in pts) or all(p.y>hi_y+margin for p in pts)
   if outside:reason='off-camera frustum /10percent image margin'
  if reason:removed.append(o.name);reasons[reason]=reasons.get(reason,0)+1;bpy.data.objects.remove(o,do_unlink=True)
 extended=[]
 if aggressive and frame['kind'] in ['village','aerial']:
  # Render-only distant snow field: a plain large plane set below the paved square so the
  # town cobbles keep their real scale and the horizon is not an edge in the frame.
  if not bpy.data.objects.get('VIEWLIGHT/distant snow field'):
   mesh=bpy.data.meshes.new('distant snow field')
   mesh.from_pydata([(-60000,-60000,-0.35),(60000,-60000,-0.35),(60000,60000,-0.35),(-60000,60000,-0.35)],[],[(0,1,2,3)])
   mesh.update()
   plane=bpy.data.objects.new('VIEWLIGHT/distant snow field',mesh);s.collection.objects.link(plane)
   mat=bpy.data.materials.get('VIEWLIGHT/distant snow') or bpy.data.materials.new('VIEWLIGHT/distant snow')
   mat.use_nodes=True;b=mat.node_tree.nodes.get('Principled BSDF')
   b.inputs['Base Color'].default_value=(0.46,0.50,0.58,1);b.inputs['Roughness'].default_value=0.88
   mesh.materials.append(mat);plane['render_only']='flat snow field beyond the modelled square'
  extended.append('VIEWLIGHT/distant snow field')
  bpy.context.view_layer.update()
 bpy.data.orphans_purge(do_recursive=True)
 return {'actual_render_only_ground_extension':extended,'removed_objects':removed,'counts_by_reason':reasons,'architectural_occluders':'retained outside frustum except intentionally hidden floors in technical views','limitation':'Offscreen clutter/reflected detail may differ from uncullled source; all geometry remains in editable native. No painted/image-only interior or people substitute.'}
