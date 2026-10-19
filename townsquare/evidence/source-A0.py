"""Original metric A0 shell/public-realm study. Not furnished or photorealistic final.
Blender4.3.2 --factory-startup -b --python tools/build_blockout.py
No transport credentials in the Blender environment. Native saved before rendering.
"""
import bpy,math,json,random,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=json.loads((R/'design/programme.json').read_text());random.seed(403)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
s['project']='Winterlichtplatz';s['stage']='A0 SHELL BLOCKOUT — interiors/humans/brand marks NOT complete';s['occupied_floors']=26
col=None;bid='PUBLIC';fid='PUBLIC'
def collection(name,parent=None):
 c=bpy.data.collections.new(name);(parent or s.collection).children.link(c);return c
def put(o,name,mat=None):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o['building_id']=bid;o['floor_id']=fid;o['stage']='A0'
 if mat:o.data.materials.append(mat)
 return o
def material(name,rgb,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*rgb,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def box(name,p,d,mat,bevel=0,angle=0):
 dx,dy,dz=[v/2 for v in d];v=[(x,y,z) for x in [-dx,dx] for y in [-dy,dy] for z in [-dz,dz]];faces=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 o=mesh(name,v,[tuple(reversed(f)) for f in faces],mat);o.location=p;o.rotation_euler.z=angle
 if bevel:
  mod=o.modifiers.new('Physical edge radius','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def rod(name,a,b,r,mat,vertices=10):
 delta=Vector(b)-Vector(a);q=delta.to_track_quat('Z','Y');mid=(Vector(a)+Vector(b))/2;v=[tuple(mid+q@Vector((r*math.cos(j*2*math.pi/vertices),r*math.sin(j*2*math.pi/vertices),z))) for z in [-delta.length/2,delta.length/2] for j in range(vertices)];faces=[tuple(reversed(range(vertices))),tuple(range(vertices,2*vertices))]+[(j,(j+1)%vertices,(j+1)%vertices+vertices,j+vertices) for j in range(vertices)];return mesh(name,v,faces,mat)
def ball(name,p,r,mat):
 N=12;M=6;v=[(p[0]+r*math.sin(k*math.pi/M)*math.cos(j*2*math.pi/N),p[1]+r*math.sin(k*math.pi/M)*math.sin(j*2*math.pi/N),p[2]+r*math.cos(k*math.pi/M)) for k in range(M+1) for j in range(N)];faces=[(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j) for k in range(M) for j in range(N)];o=mesh(name,v,[tuple(reversed(f)) for f in faces],mat)
 for f in o.data.polygons:f.use_smooth=True
 return o
def mesh(name,v,f,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o.data.materials.append(mat);o['building_id']=bid;o['floor_id']=fid;o['stage']='A0';return o
def text(name,string,p,size,mat,rot=(math.pi/2,0,0),align='CENTER'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=string;cu.size=size;cu.align_x=align;cu.extrude=.008;cu.bevel_depth=.002;o=bpy.data.objects.new(name,cu);col.objects.link(o);o.location=p;o.rotation_euler=rot;o.data.materials.append(mat);return o
def area(name,p,target,power,size,color):
 da=bpy.data.lights.new(name,'AREA');da.energy=power;da.shape='DISK';da.size=size;da.color=color;o=bpy.data.objects.new(name,da);col.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
snow=material('Snow — initial accumulation study',(.75,.82,.87),.8)
stone=material('Pale limestone',(.38,.33,.27),.72);wood=material('Oiled oak',(.115,.052,.022),.49);iron=material('Blackened iron',(.025,.032,.031),.3,.75)
slate=material('Weathered slate',(.055,.075,.082),.68);clay=material('Clay roof',(.19,.064,.033),.7);green=material('Fir — silhouette only',(.014,.065,.033),.8);red=material('Oxblood paint',(.21,.018,.026),.48)
gold=material('Brass',(.55,.3,.075),.24,.8);cream=material('Warm sign lettering',(.82,.75,.55),.42)
glass=material('Physical glazing',(.82,.9,.96),.08);bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
warm=material('Warm lamp diffuser',(1,.58,.2),.3);bs=warm.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.48,.15,1);bs.inputs['Emission Strength'].default_value=4
plasters=[material('Mineral plaster '+str(i),c,.83) for i,c in enumerate([(.49,.39,.27),(.55,.5,.39),(.28,.37,.34),(.43,.25,.19),(.48,.43,.33),(.31,.35,.41)])]
paving=material('Poly Haven cobblestone01 — measured2.4m repeat',(.15,.16,.16),.35)
nt=paving.node_tree;n=nt.nodes;l=nt.links;bs=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=1/2.4;l.new(tc.outputs['Object'],mapping.inputs[0])
manifest=json.loads((R/'assets/materials/manifest.json').read_text())
for row in manifest:
 im=bpy.data.images.load(str(R/row['file']));tex=n.new('ShaderNodeTexImage');tex.image=im;l.new(mapping.outputs['Vector'],tex.inputs['Vector'])
 if row['slot']=='Diffuse':l.new(tex.outputs['Color'],bs.inputs['Base Color'])
 elif row['slot']=='Rough':im.colorspace_settings.name='Non-Color';mix=n.new('ShaderNodeMath');mix.operation='MULTIPLY';mix.inputs[1].default_value=.58;l.new(tex.outputs['Color'],mix.inputs[0]);l.new(mix.outputs[0],bs.inputs['Roughness'])
 elif row['slot']=='nor_gl':im.colorspace_settings.name='Non-Color';normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65;l.new(tex.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],bs.inputs['Normal'])
col=collection('00_PUBLIC_REALM');box('Ground apron',(0,0,-.4),(112,100,.6),snow);box('Paved square64x52m',(0,0,-.08),(64,52,.16),paving,.025)
# Inward-facing building coordinates. All opening rectangles are actual empty geometry.
for i,b in enumerate(D['buildings']):
 bid=b['id'];root=collection(bid+'_'+b['brand']);w,d=b['footprint_m'];cx,cy=b['centre_xy_m'];a=math.radians(b['rotation_deg']);co,si=math.cos(a),math.sin(a)
 def P(x,y,z):return (cx+x*co-y*si,cy+x*si+y*co,z)
 def B(name,x,y,z,dx,dy,dz,mat,edge=.015):return box(bid+'_'+name,P(x,y,z),(dx,dy,dz),mat,edge,a)
 for fl in b['floors']:
  fid=fl['id'];col=collection(fid,root);col['occupied_floor']=True;col['floor_id']=fid;col['building_id']=bid;col['furnishing_status']='NOT BUILT';z=fl['datum_m'];h=fl['height_m'];mat=plasters[i%len(plasters)]
  B(fid+'_SLAB',0,0,z-.12,w,d,.24,stone);B(fid+'_SIDE_W',-w/2,0,z+h/2,.3,d,h,mat);B(fid+'_SIDE_E',w/2,0,z+h/2,.3,d,h,mat)
  for back in [False,True]:
   yy=d/2 if back else -d/2
   openings=([(-w/2+3,w/2-3,0,2.8)] if False else [])
   if fl['index']==0 and not back:openings=[(-w/2+.9,-1.1,.28,2.85),(-.85,.85,0,2.8),(1.1,w/2-.9,.28,2.85)]
   elif fl['index']==0:openings=[(-.8,.8,0,2.6),(-w/2+1.1,-w/2+3.0,1.0,2.6),(w/2-3.0,w/2-1.1,1.0,2.6)]
   else:openings=[(xx-.68,xx+.68,.75,2.55) for xx in [-w*.33,-w*.11,w*.11,w*.33]]
   cuts=sorted(set([0,h]+[q for op in openings for q in op[2:]]))
   for lo,hi in zip(cuts,cuts[1:]):
    spans=sorted([(op[0],op[1]) for op in openings if op[2]<(lo+hi)/2<op[3]]);last=-w/2
    for left,right in spans+[(w/2,w/2)]:
     if left-last>.001:B(fid+'_WALL', (left+last)/2,yy,z+(lo+hi)/2,left-last,.3,hi-lo,mat)
     last=right
   for k,(left,right,lo,hi) in enumerate(openings):
    x=(left+right)/2;ww=right-left;hh=hi-lo
    B(fid+'_GLAZING',x,yy,z+(lo+hi)/2,ww-.10,.028,hh-.1,glass,0)
    for xx in [left+.03,right-.03]:B(fid+'_JAMB',xx,yy-.06,z+(lo+hi)/2,.09,.22,hh,wood)
    for zz in [lo+.03,hi-.03]:B(fid+'_HEAD_SILL',x,yy-.06,z+zz,ww,.22,.09,wood)
    if ww>2:B(fid+'_MULLION',x,yy-.07,z+(lo+hi)/2,.07,.20,hh,wood)
  B(fid+'_CORNICE',0,-d/2-.10,z+h-.12,w+.35,.40,.18,stone)
  # A0 floor is visibly empty. No emissive fake interior planes are inserted.
  area(fid+'_INTERIOR_STUDY_LIGHT',P(0,-2,z+h-.45),P(0,-d/2-4,z+1.5),400,4,(1,.67,.38))
 fid='ROOF';col=collection(bid+'_ROOF',root);H=b['floors'][-1]['datum_m']+b['floors'][-1]['height_m'];ridge=H+3.0+(i%3)*.35
 for dy in [-1,1]:
  vv=[P(-w/2-.45,dy*(d/2+.45),H),P(w/2+.45,dy*(d/2+.45),H),P(w/2+.45,0,ridge),P(-w/2-.45,0,ridge)]
  mesh(bid+'_ROOF_SLOPE',vv,[(0,1,2,3)],slate if i%3 else clay)
  mesh(bid+'_ROOF_SNOW_STUDY',[(x,y,z+.045) for x,y,z in vv],[(0,1,2,3)],snow)
 for xx in [-w/2,w/2]:mesh(bid+'_GABLE',[P(xx,-d/2,H),P(xx,d/2,H),P(xx,0,ridge)],[(0,1,2)],plasters[i%len(plasters)])
 B('CHIMNEY',w*.28,1,ridge+.2,.8,.85,1.6,stone);B('CHIMNEY_CAP',w*.28,1,ridge+1.02,1.03,1.08,.14,snow)
 fid='SIGNAGE';col=collection(bid+'_BRAND_STUDY',root);B('FASCIA',0,-d/2-.21,3.22,w-1,.17,.55,iron)
 t=text(bid+'_NAME_ONLY_NOT_FINAL_LOGO',b['brand'],P(0,-d/2-.31,3.06),.36,cream,rot=(math.pi/2,0,a));t['brand_status']='Typography placement only; vector mark/system pending'
# Public seating: actual planks, supports, backs. Detail/clearance review remains pending.
bid='PUBLIC';fid='PUBLIC';col=collection('01_BENCHES_AND_LAMPS')
benchpositions=[]
for x in [-25,-15,-5,5,15,25]:benchpositions += [(x,-21,0),(x,21,math.pi)]
for y in [-15,-9,-3,3,9,15]:benchpositions += [(-28,y,math.pi/2),(28,y,-math.pi/2)]
for i,(x,y,a) in enumerate(benchpositions):
 def Q(dx,dy,z):return (x+dx*math.cos(a)-dy*math.sin(a),y+dx*math.sin(a)+dy*math.cos(a),z)
 for dy in [-.19,-.06,.07,.20]:box('BENCH%02d_SEAT'%i,Q(0,dy,.48),(1.85,.10,.055),wood,.015,a)
 for zz in [.71,.86,1.01]:box('BENCH%02d_BACK'%i,Q(0,.27,zz),(1.85,.045,.11),wood,.01,a)
 for dx in [-.7,.7]:rod('BENCH_LEG',Q(dx,.2,.02),Q(dx,.2,1.05),.035,iron);rod('BENCH_LEG',Q(dx,-.2,.02),Q(dx,-.2,.5),.035,iron);rod('BENCH_ARM',Q(dx,-.22,.68),Q(dx,.27,.68),.025,iron)
for i in range(24):
 if i<12:x,y=[-29,-19,-9,9,19,29][i%6],[-23,23][i//6]
 else:x,y=[-30,30][(i-12)//6],[-17,-10,-3,3,10,17][i%6]
 rod('LAMP%02d_POST'%i,(x,y,.1),(x,y,4.35),.055,iron);box('LAMP_BASE',(x,y,.18),(.3,.3,.36),iron,.04)
 box('LAMP_LANTERN',(x,y,4.25),(.37,.37,.54),glass,.015);box('LAMP_CAP',(x,y,4.57),(.48,.48,.12),iron,.03);ball('LAMP_DIFFUSER',(x,y,4.3),.09,warm)
 area('LAMP%02d_PRACTICAL'%i,(x,y,4.36),(x,y,0),65,.24,(1,.63,.3))
# Initial bare-tree branching scaffold, explicitly not final vegetation.
col=collection('02_TREE_SCAFFOLDS')
for i in range(12):
 x,y=([(-24,-15),(-24,0),(-24,15),(24,-15),(24,0),(24,15),(-16,-23),(0,-23),(16,-23),(-16,23),(0,23),(16,23)][i]);rod('LINDEN_TRUNK',(x,y,0),(x+.15,y,4.7),.17,wood)
 for j in range(7):
  a=j*2.4+i;end=(x+math.cos(a)*2.3,y+math.sin(a)*2.3,5.2+(j%3)*.5);rod('LINDEN_BRANCH',(x,y,2.4+j*.22),end,.065,wood)
  for k in [-1,1]:rod('LINDEN_TWIG',end,(end[0]+math.cos(a+k*.7)*.9,end[1]+math.sin(a+k*.7)*.9,end[2]+.5),.022,wood,7)
col=collection('03_CHRISTMAS_TREE_SILHOUETTE');box('TREE_BASE',(-4,7,.35),(2.8,2.8,.7),stone,.12)
for i in range(14):
 z=.8+i*.76;rr=3.35*(1-i/15);bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=rr,radius2=.05,depth=2.4,location=(-4,7,z+1.2));put(bpy.context.object,'FIR_TIER_A0_NOT_FINAL_NEEDLES',green)
for i in range(110):
 t=i/109;rr=3.18*(1-t);a=t*math.pi*2*7;ball('TREE_LIGHT',(-4+rr*math.cos(a),7+rr*math.sin(a),1.3+t*10.8),.045,warm)
ball('TREE_FINIAL',(-4,7,12.6),.24,gold)
col=collection('04_MARKET_STALLS')
for k,(x,y) in enumerate([(x,y) for y in [-16,16] for x in [-17,-9,8,17]]):
 box('STALL%02d_BASE'%k,(x,y,.6),(4,2.5,1.2),wood,.03)
 for dx in [-1.9,1.9]:
  for dy in [-1.15,1.15]:rod('STALL_POST',(x+dx,y+dy,.6),(x+dx,y+dy,2.55),.055,wood)
 box('STALL_COUNTER',(x,y-1.35,1.1),(4.2,.6,.10),wood,.025)
 mesh('STALL_ROOF',[(x-2.2,y-1.6,2.55),(x+2.2,y-1.6,2.55),(x+2.2,y,3.1),(x-2.2,y,3.1),(x-2.2,y+1.6,2.55),(x+2.2,y+1.6,2.55)],[(0,1,2,3),(3,2,5,4)],snow)
col=collection('05_PLAYGROUND_A0');rubber=material('Impact surface — design study',(.10,.13,.13),.92);box('PLAYGROUND_SURFACE',(21,3,.035),(12,14,.07),rubber,.05)
for x in [17,25]:
 for y in [-1,7]:rod('PLAY_FENCE_POST',(x,y,.05),(x,y,1.1),.045,wood)
# Swing frame and two suspended seats.
for x in [18,22]:
 rod('SWING_AFRAME',(x,-1,.1),(x,1,2.6),.075,iron);rod('SWING_AFRAME',(x,3,.1),(x,1,2.6),.075,iron)
rod('SWING_TOP',(18,1,2.6),(22,1,2.6),.08,iron)
for x in [19,21]:
 box('SWING_SEAT',(x,1,.53),(.55,.36,.06),iron,.045)
 for dx in [-.23,.23]:rod('SWING_CHAIN',(x+dx,1,.56),(x+dx,1,2.6),.012,iron,6)
box('SLIDE_PLATFORM',(24,6,1.5),(1.3,1.4,.15),wood,.02)
for x in [23.5,24.5]:rod('SLIDE_POST',(x,6,0),(x,6,2.3),.06,wood)
for k in range(7):rod('SLIDE_LADDER_RUNG',(23.6,7, .2+k*.2),(24.4,7,.2+k*.2),.025,iron)
mesh('SLIDE_CHUTE',[(23.6,5.3,1.5),(24.4,5.3,1.5),(24.4,2.6,.2),(23.6,2.6,.2)],[(0,1,2,3)],red)
for xx in [23.6,24.4]:rod('SLIDE_RAISED_EDGE',(xx,5.3,1.65),(xx,2.6,.35),.055,red)
# Lighting/calibration study, not calibrated final photometry.
col=collection('90_LIGHTING_CAMERAS');world=bpy.data.worlds.new('Blue-hour lighting study');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.20,.36,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;s.world=world
area('COOL_SKY_KEY',(0,-10,60),(0,0,0),65000,70,(.53,.67,1))
for name,pos,target,ortho in [('CAM_A0_OVERVIEW',(87,-103,84),(0,0,3),None),('CAM_A0_PLAN',(0,0,130),(0,0,0),112),('CAM_PILOT_STREET',(10,-19,1.65),(-20,27,2),None)]:
 da=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,da);col.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();da.lens=44;da.clip_end=500
 if ortho:da.type='ORTHO';da.ortho_scale=ortho
s.camera=bpy.data.objects['CAM_A0_OVERVIEW'];s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.4
s.render.filepath='//../renders/A0-overview.png';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'scene/square-A0.blend'),compress=True)
report={'stage':'A0 blockout only','buildings':12,'occupied_floor_collections':len([c for c in bpy.data.collections if c.get('occupied_floor')]),'objects':len(s.objects),'people_built':0,'furnished_floors':0,'final_brand_logos':0,'packed_images':len([im for im in bpy.data.images if im.packed_file]),'native':'scene/square-A0.blend','limitations':['All26 floor shells exist, but no occupied floor furnishing is complete.','Roof snow, tree silhouettes, playground and street furniture are A0 design studies, not final realism.','No people are modelled or accepted.','Brand typography is placement study, not finished logo system.']}
(R/'evidence/blockout-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print('A0_NATIVE_SAVED',json.dumps(report))
if os.environ.get('SQUARE_RENDER')=='1':bpy.ops.render.render(write_still=True)
