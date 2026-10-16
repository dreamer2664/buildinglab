"""Blender 4.3+ measured schematic; no addons or external resources.
blender -b -t 8 --python design/build_blockout.py
Then blender -b scene/blockout.blend -t 8 --python design/render_blockout.py
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'design/programme.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection':bpy.data.collections.remove(c)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['stage']='BLDG-1 schematic only; no final furnishing or release acceptance'
scene['occupied_levels']=6;scene['proposed_homes']=14;scene['design']='Casa dei Colori'
scene['footprint_m']='26 x 20';scene['parapet_top_m']=21.12
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.world.color=(.45,.45,.45);scene.view_settings.view_transform='AgX'
materials={}
for k,v in D['palette'].items():
 m=bpy.data.materials.new(k);m.diffuse_color=tuple(((int(v[n:n+2],16)/255+.055)/1.055)**2.4 for n in (1,3,5))+(1,);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.72;materials[k]=m
for k,col in [('wall',(.84,.78,.64,1)),('trim',(.1,.24,.23,1)),('slab',(.58,.53,.43,1)),('door',(.43,.23,.12,1)),('ink',(.08,.15,.14,1))]:
 m=bpy.data.materials.new(k);m.diffuse_color=col;m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=col;materials[k]=m
current=None

def move(obj):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 current.objects.link(obj)

def box(name,loc,size,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(materials[mat]);move(o)
 if bevel:
  mod=o.modifiers.new('Edge softness','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o

def text(name,body,loc,size=.22,mat='ink'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.002
 o=bpy.data.objects.new(name,cu);current.objects.link(o);o.location=loc;o.data.materials.append(materials[mat]);return o

def rod(name,a,b,r=.025):
 direction=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))*.5
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=direction.length,location=mid);o=bpy.context.object;o.name=name;o.rotation_euler=direction.to_track_quat('Z','Y').to_euler();o.data.materials.append(materials['trim']);move(o)
 return o

# Walls are a raster union of room-edge strips, with genuine door holes.
# This avoids duplicate co-planar partitions, keeps layout inspectable, and uses editable mesh.
def walls(l,z):
 rs=l['rooms'];xs={0,26};ys={0,20};strips=[]
 for r in rs:
  x,y,xx,yy=r['rect']
  for b in [(x-.1,y-.1,xx+.1,y+.1),(x-.1,yy-.1,xx+.1,yy+.1),(x-.1,y-.1,x+.1,yy+.1),(xx-.1,y-.1,xx+.1,yy+.1)]:
   strips.append(b);xs.update([max(0,b[0]),min(26,b[2])]);ys.update([max(0,b[1]),min(20,b[3])])
 holes=[]
 for d in l['doors']:
  x,y,w=d['x'],d['y'],d['width']
  b=(x-w/2,y-.3,x+w/2,y+.3) if d['orientation']=='H' else (x-.3,y-w/2,x+.3,y+w/2)
  holes.append(b);xs.update([max(0,b[0]),min(26,b[2])]);ys.update([max(0,b[1]),min(20,b[3])])
 xs=sorted(xs);ys=sorted(ys);verts=[];faces=[]
 def inside(x,y,b):return b[0]<x<b[2] and b[1]<y<b[3]
 for a,b in zip(xs,xs[1:]):
  if b-a<.00001:continue
  for c,d in zip(ys,ys[1:]):
   if d-c<.00001:continue
   x=(a+b)/2;y=(c+d)/2
   if not any(inside(x,y,q) for q in strips) or any(inside(x,y,q) for q in holes):continue
   # 1.05 m cutaway walls intentionally schematic, not complete envelope.
   n=len(verts);verts.extend([(a,c,z),(b,c,z),(b,d,z),(a,d,z),(a,c,z+1.05),(b,c,z+1.05),(b,d,z+1.05),(a,d,z+1.05)])
   faces.extend([tuple(n+j for j in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 me=bpy.data.meshes.new(l['id']+'_wall_mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(l['id']+'_CUTAWAY_WALLS',me);current.objects.link(o);o.data.materials.append(materials['wall']);o['schematic_wall_height']=1.05

for i,l in enumerate(D['levels']):
 lid=l['id'];z=l['elevation_m'];current=bpy.data.collections.new(lid);scene.collection.children.link(current);current['occupied_level']=True;current['elevation_m']=z
 # floor tiles make actual stair and lift openings in upper slabs
 xs=[0,.3,4.7,11.8,14.2,21.3,25.7,26];ys=[0,7.2,9.74545,12.8,20]
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(ys,ys[1:]):
   stair=(a>=.3 and b<=4.7 or a>=21.3 and b<=25.7) and c>=7.2 and d<=12.8
   lift=a>=11.8 and b<=14.2 and c>=9.74545 and d<=12.8
   if i>0 and (stair or lift):continue
   o=box(lid+'_SLAB',((a+b)/2,(c+d)/2,z-.11),(b-a,d-c,.22),'slab');o['role']='slab'
 for r in l['rooms']:
  x,y,xx,yy=r['rect'];rr=r['kind']
  # Do not bridge stair openings with colored floor overlay.
  if rr not in ['stair','elevator']:
   o=box(r['id']+'_ZONE',((x+xx)/2,(y+yy)/2,z+.015),(xx-x,yy-y,.03),rr);o['room_id']=r['id'];o['role']='room_zone';o['home']=r['home'] or '';o['area_m2']=r['area_m2']
  label=(r['home']+' ' if r['home'] else '')+r['name']
  if rr not in ['stair','service','elevator']:
   text(r['id']+'_LABEL',label,((x+xx)/2,(y+yy)/2,z+.042),min(.26,(xx-x)/max(12,len(label))*.95))
 for h in l['homes']:
  x,y,xx,yy=h['kitchen_zone'];box(lid+'_'+h['id']+'_KITCHEN_ZONE',((x+xx)/2,(y+yy)/2,z+.07),(xx-x,yy-y,.1),'kitchen')
  # These are explicitly kitchen planning zones, NOT finished cabinets.
 walls(l,z+.03)
 for d in l['doors']:
  x,y,w=d['x'],d['y'],d['width']
  o=box(d['id']+'_THRESHOLD',(x,y,z+.04),(w,.08,.02) if d['orientation']=='H' else (.08,w,.02),'door');o['role']='door_opening';o['clear_width_m']=w
 # elevator: floor stop threshold and schematic cab outline, no false completed cab claim
 box(lid+'_LIFT_MARKER',(13,11.2,z+.06),(1.8,2.1,.1),'elevator')
 text(lid+'_LIFT_LABEL','LIFT',(13,11,z+.12),.3)
 for side,x0 in [('A',.3),('B',21.3)]:
  height=l['storey_height_m'];n=22 if i==0 else 20;half=n//2;tread=.28;run=(half-1)*tread;start=8.45
  # Bottom + intermediate landings fit 5.6 m core: 1.2 + 2.8 + 1.2 = 5.2.
  box(lid+'_STAIR_'+side+'_BOTTOM',(x0+2.2,7.825,z-.05),(4.0,1.25,.1),'stair')
  if i<5:
   for k in range(half):
    zz=z+(k+1)*height/n
    box(lid+'_STAIR_'+side+f'_F1_{k+1}',(x0+1.0,start+k*tread,zz-.06),(1.35,tread,.12),'stair')
   midy=start+(half-1)*tread+.72
   box(lid+'_STAIR_'+side+'_MID',(x0+2.2,midy,z+height/2-.06),(3.9,1.16,.12),'stair')
   for k in range(half):
    zz=z+height/2+(k+1)*height/n
    box(lid+'_STAIR_'+side+f'_F2_{k+1}',(x0+3.25,start+(half-1-k)*tread,zz-.06),(1.35,tread,.12),'stair')
   for xx in [x0+.30,x0+1.70,x0+2.55,x0+3.95]:
    reverse=xx>x0+2
    z0=z+(height if reverse else height/n)+.95;z1=z+height/2+.95
    rod(lid+'_STAIR_'+side+'_HANDRAIL',(xx,start-.1,z0),(xx,start+run+.1,z1))
    for k in [0,half//2,half-1]:
     zz=z+(height/2+(half-k)*height/n if reverse else (k+1)*height/n)
     rod(lid+'_STAIR_'+side+'_BALUSTER',(xx,start+k*tread,zz),(xx,start+k*tread,zz+.95),.018)
  text(lid+'_STAIR_'+side+'_LABEL','STAIR '+side,(x0+2.2,7.4,z+.08),.3)
 # upright level identity sign, floorplan-readable caption also
 text(lid+'_ID',lid,(19,9,z+.045),.7)
 # floor light fixture positions in named switchable lighting collection (schematic)
 lights=bpy.data.collections.new(lid+'_LIGHTING');current.children.link(lights)
 for j,(x,y) in enumerate([(7,4),(19,4),(7,16),(19,16),(8,8),(18,8)]):
  data=bpy.data.lights.new(lid+f'_AREA_{j}','AREA');data.energy=130;data.shape='DISK';data.size=2
  o=bpy.data.objects.new(data.name,data);lights.objects.link(o);o.location=(x,y,z+2.7)
 # cameras
 current=scene.collection
 def camera(name,pos,target,ortho):
  data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=ortho;data.clip_end=500;return o
 camera('CAM_'+lid+'_AXON',(39,-36,z+65),(13,10,z),38)
 camera('CAM_'+lid+'_PLAN',(13,10,z+50),(13,10,z),31)
current=scene.collection
sun=bpy.data.lights.new('DAYLIGHT','SUN');sun.energy=2;sun.angle=.15;o=bpy.data.objects.new('DAYLIGHT',sun);current.objects.link(o);o.rotation_euler=(math.radians(28),math.radians(-20),math.radians(-35))
camera('CAM_FULL_STACK',(49,-55,43),(13,10,9),47)
scene.camera=bpy.data.objects['CAM_FULL_STACK']
(ROOT/'scene').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene/blockout.blend'))
# machine receipt comes from geometry, not a hardcoded acceptance declaration
receipt={'blender_version':bpy.app.version_string,'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'rooms':sum(o.get('role')=='room_zone' for o in scene.objects),'floor_elevations_m':{c.name:c['elevation_m'] for c in bpy.data.collections if c.get('occupied_level')},'scene':'scene/blockout.blend','stage':'schematic; not final scene validation'}
(ROOT/'design/blockout-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('BLOCKOUT_SAVED',json.dumps(receipt))
