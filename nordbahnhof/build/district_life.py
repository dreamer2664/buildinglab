import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
from district_core import ROOT

def chair(d,p,x,y,a=0):
 # Bentwood cafe chair: curved back hoop, cane seat and four slender legs.
 saved=d.transform.copy();d.transform=saved@Matrix.Translation((x,y,0))@Matrix.Rotation(a,4,'Z');x=y=0
 for dx in (-.17,.17):
  for dy in (-.17,.17):d.beam('cafe chair leg',(x+dx*1.15,y+dy*1.15,.19),(x+dx,y+dy,.63),.029,p['wood'])
 d.cyl('cane chair seat',(x,y,.65),.235,.035,p['linen'],N=16)
 for i in range(14):
  t=i*math.pi/13;u=(i+1)*math.pi/13
  A=(x+.22*math.cos(t),y+.14,.83+.28*math.sin(t));B=(x+.22*math.cos(u),y+.14,.83+.28*math.sin(u));d.beam('bentwood chair hoop',A,B,.025,p['wood'])
 for dx in (-.22,.22):d.beam('chair back stile',(x+dx,y+.14,.63),(x+dx,y+.14,.83),.025,p['wood'])
 d.transform=saved

def table(d,p,x,y):
 d.cyl('marble cafe table',(x,y,.92),.40,.045,p['marble'],N=32);d.cyl('table iron pedestal',(x,y,.57),.038,.68,p['iron'])
 for j in range(3):
  a=j*math.tau/3;d.beam('table splayed foot',(x,y,.27),(x+.3*math.cos(a),y+.3*math.sin(a),.21),.04,p['iron'])
 for dx,dy in [(-.15,.02),(.16,-.10)]:
  d.cyl('porcelain saucer',(x+dx,y+dy,.954),.075,.009,p['cream'],N=16);d.cyl('coffee cup',(x+dx,y+dy,.988),.037,.064,p['cream'],N=12);d.cyl('coffee surface',(x+dx,y+dy,1.021),.028,.001,p['darkwood'],N=12);d.ring('cup handle',(x+dx+.045,y+dy,.994),.022,.006,p['cream'],'Y',N=12,M=4)
 d.box('folded cafe newspaper',(x-.03,y+.18,.959),(.21,.14,.004),p['paper'],.2)
 d.text('newspaper masthead','NORDSTADT',(x-.03,y+.21,.962),.014,p['black'],(0,0,.2))
 for col in range(3):
  for line in range(8):d.box('newspaper printed column',(x-.095+col*.06,y+.135+line*.007,.962),(.045,.0014,.0002),p['black'],.2)
 for dx,dy in [(-.66,0),(.64,0),(0,.63)]:chair(d,p,x+dx,y+dy,math.atan2(-dx,dy))

def bench(d,p,x,y,angle=0):
 d.location(x,y,.18,angle)
 for yy in (-.22,.22):
  for xx in (-.72,.72):d.beam('park bench leg',(xx,yy,0),(xx,yy,.45),.045,p['iron'])
 for yy in (-.21,-.07,.07,.21):d.box('bench seat slat',(0,yy,.47),(1.85,.115,.045),p['wood'])
 for z in (.68,.84,1.0):d.box('bench back slat',(0,.25,z),(1.85,.045,.12),p['wood'])
 for xx in (-.72,.72):d.beam('bench back support',(xx,.24,.25),(xx,.28,1.05),.035,p['iron'])
 d.location()

def lamp(d,p,x,y):
 d.cyl('streetlamp base',(x,y,.43),.22,.5,p['iron'],N=12);d.cyl('fluted lamp mast',(x,y,2.32),.066,3.7,p['iron'],N=12)
 for z in (.75,3.75,4.15):d.ring('lamp mast collar',(x,y,z),.10,.026,p['iron'],N=16,M=4)
 d.cyl('lantern bottom',(x,y,4.22),.25,.12,p['iron'],N=6)
 for i in range(6):
  a=i*math.tau/6;d.beam('lantern iron frame',(x+.23*math.cos(a),y+.23*math.sin(a),4.25),(x+.3*math.cos(a),y+.3*math.sin(a),4.88),.026,p['iron'])
 d.cyl('lantern frosted light',(x,y,4.54),.21,.53,p['lamp'],N=6);d.cyl('lantern roof',(x,y,4.92),.36,.10,p['iron'],N=6);d.sphere('lamp finial',(x,y,5.08),(.06,.06,.11),p['bronze'])

def fountain(d,p):
 x,y=-19,-10
 for r,h,z in [(5.1,.16,.24),(4.8,.18,.40),(4.5,.30,.57)]:
  d.ring('fountain stepped basin',(x,y,z),r,h,p['stone'],N=80,M=8)
 d.cyl('fountain basin floor',(x,y,.25),4.55,.1,p['stone'],N=80);d.cyl('fountain water surface',(x,y,.46),4.43,.008,p['water'],N=80)
 for r,z in [(1.2,.60),(.8,1.05),(.58,1.65)]:d.cyl('fountain carved pedestal',(x,y,z),r,.4,p['stone'],N=16)
 d.ring('fountain upper bowl',(x,y,2.14),1.65,.13,p['stone'],N=64,M=8);d.cyl('fountain upper water',(x,y,2.12),1.58,.015,p['water'],N=64);d.cyl('fountain central column',(x,y,2.0),.27,2.7,p['stone'],N=16)
 d.sphere('fountain carved pinecone',(x,y,3.49),(.36,.36,.48),p['bronze'],N=16,M=10)
 for j in range(12):
  a=j*math.tau/12
  for k in range(7):
   t=k/7;u=(k+1)/7
   def P(t):return(x+(1.50+1.5*t)*math.cos(a),y+(1.5+1.5*t)*math.sin(a),2.15-.12*t-1.55*t*t)
   d.beam('falling fountain stream',P(t),P(u),.013,p['water'])
 for j in range(9):d.ring('fountain water ripple',(x+2.6,y,.466),.08+j*.14,.002,p['water'],N=40,M=4)

def kiosk(d,p):
 d.location(43,-17,.18);R=2.0
 for j in range(8):
  a=j*math.tau/8;b=(j+1)*math.tau/8;A=(R*math.cos(a),R*math.sin(a));B=(R*math.cos(b),R*math.sin(b))
  d.beam('kiosk corner post',(*A,0),(*A,2.8),.11,p['green']);d.mesh('kiosk lower panel',[(*A,.18),(*B,.18),(*B,.94),(*A,.94)],[(0,1,2,3)],p['green']);d.mesh('kiosk glass pane',[(*A,1.0),(*B,1.0),(*B,2.45),(*A,2.45)],[(0,1,2,3)],p['glass'])
  d.mesh('kiosk copper roof',[(*A,2.8),(*B,2.8),(0,0,3.6)],[(0,1,2)],p['bronze'])
  for k in range(6):
   t=(k+.5)/6;xx=A[0]*(1-t)+B[0]*t;yy=A[1]*(1-t)+B[1]*t
   d.box('newspaper bundle',(xx*.88,yy*.88,1.12),(.20,.16,.32),p['paper'],a)
 d.ring('kiosk eaves',(0,0,2.82),2.08,.10,p['green'],N=8,M=4);d.text('kiosk newspaper sign','ZEITUNGEN',(0,2.07,2.48),.28,p['cream']);d.location()

def market(d,p,x,y,index):
 d.location(x,y,.18,index*.03)
 for xx in (-1.3,1.3):
  for yy in (-.6,.6):d.cyl('market awning post',(xx,yy,1.2),.033,2.4,p['wood'])
 for j in range(12):
  xx=-1.5+j*.25;ma=p['linen'] if j%2 else p['green'] if index%2 else p['red'];d.mesh('market canopy cloth',[(xx,-1,2.3),(xx+.25,-1,2.3),(xx+.25,0,2.7),(xx,0,2.7),(xx,.9,2.3),(xx+.25,.9,2.3)],[(0,1,2,3),(3,2,5,4)],ma)
 d.box('market trestle counter',(0,0,.83),(2.8,1.3,.12),p['wood'])
 for xx in (-1.1,1.1):d.box('market trestle leg',(xx,0,.39),(.09,.9,.78),p['wood'])
 for j in range(4):
  xx=-1.0+j*.67
  for yy in (-.38,.38):
   for z in (.93,1.04):d.box('produce crate slat',(xx,yy,z),(.60,.04,.07),p['wood'])
  for s in (-1,1):d.box('crate end',(xx+s*.30,0,.96),(.04,.8,.21),p['wood'])
  for k in range(15):d.sphere('market fruit',(xx+(k%3-1)*.16,(k//3-2)*.13,1.03),(.08,.075,.07),p['fruitred'] if (j+index)%2 else p['fruitgold'],N=8,M=5)
 d.text('handwritten stall price','FRISCH  ·  25 Pf',(0,.69,1.08),.14,p['cream']);d.location()

def bicycle(d,p,x,y,a=0):
 d.location(x,y,.18,a)
 for xx in (-.53,.53):
  d.ring('bicycle pneumatic tyre',(xx,0,.36),.34,.025,p['black'],'Y',N=32,M=5);d.ring('bicycle wheel rim',(xx,0,.36),.315,.009,p['rail'],'Y',N=32,M=4)
  for k in range(16):
   t=k*math.tau/16;d.beam('bicycle spoke',(xx,0,.36),(xx+.31*math.cos(t),0,.36+.31*math.sin(t)),.003,p['rail'])
 for A,B in [((-.53,0,.36),(-.18,0,.82)),((-.18,0,.82),(.1,0,.39)),((.1,0,.39),(-.53,0,.36)),((-.18,0,.82),(.40,0,.82)),((.40,0,.82),(.1,0,.39)),((.40,0,.82),(.53,0,.36))]:d.beam('bicycle diamond frame',A,B,.023,p['iron'])
 d.beam('bicycle handlebar stem',(.4,0,.82),(.36,0,1.08),.022,p['iron']);d.beam('bicycle handlebar',(.36,-.23,1.08),(.36,.23,1.08),.022,p['iron']);d.box('leather bicycle saddle',(-.22,0,.92),(.23,.17,.045),p['darkwood']);d.beam('saddle stem',(-.18,0,.65),(-.22,0,.92),.02,p['iron']);d.location()

def tram(d,p,x,y,a=0):
 d.location(x,y,0,a)
 # A fully modeled two-axle electric streetcar with a usable enclosed interior.
 for xx in (-2.0,2.0):
  d.cyl('tram axle',(xx,0,.47),.07,1.65,p['iron'],'Y')
  for yy in (-.755,.755):d.cyl('tram steel wheel',(xx,yy,.47),.34,.12,p['rail'],'Y',N=24)
 d.box('tram underframe',(0,0,.79),(7.9,2.0,.25),p['iron']);d.box('tram wooden floor',(0,0,1.02),(8.4,2.20,.14),p['wood'])
 for yy in (-1.12,1.12):
  d.box('tram lower side',(0,yy,1.57),(6.6,.08,1.0),p['green']);d.box('tram waist rail',(0,yy,2.10),(6.75,.12,.10),p['cream'])
  for k in range(7):
   xx=-3.22+k*1.07;d.box('tram window stile',(xx,yy,2.65),(.075,.10,1.05),p['wood'])
   if k<6:d.box('tram glass window',(xx+.535,yy,2.65),(.98,.009,.96),p['glass'])
  d.box('tram upper side rail',(0,yy,3.20),(6.7,.12,.15),p['cream'])
  for xx in (-3.80,3.80):
   d.box('tram platform step',(xx,yy*1.05,.70),(1.0,.48,.16),p['iron']);d.beam('tram boarding grab',(xx,yy,1.18),(xx,yy,2.9),.035,p['bronze'])
  d.text('tram fleet side','NORDSTADT  ·  17',(0,yy*1.044,1.54),.23,p['cream'],(math.pi/2,0,0 if yy<0 else math.pi))
  for xx in (-2.4,-1.2,0,1.2,2.4):
   d.box('tram passenger bench',(xx,yy*.75,1.44),(.80,.40,.10),p['wood']);d.box('tram bench back',(xx,yy*.87,1.79),(.80,.06,.65),p['wood'])
 for xx in (-4.12,4.12):
  d.box('tram cab front',(xx,0,1.6),(.08,2.2,1),p['green']);d.box('tram front glass',(xx,0,2.65),(.009,1.95,.95),p['glass'])
  for yy in (-1.06,0,1.06):d.box('tram cab window frame',(xx,yy,2.65),(.09,.07,1.16),p['cream'])
  d.cyl('tram headlight housing',(xx*1.013,0,1.59),.16,.14,p['bronze'],'X',N=20);d.cyl('tram headlight lens',(xx*1.033,0,1.59),.13,.01,p['lamp'],'X',N=20)
  d.box('tram destination board',(xx,0,3.28),(.10,1.9,.28),p['green']);d.text('tram route','2  BAHNHOF',(xx*1.014,0,3.20),.14,p['cream'],(math.pi/2,0,-math.pi/2 if xx>0 else math.pi/2))
 d.box('tram roof',(0,0,3.42),(8.75,2.45,.18),p['cream']);d.box('tram clerestory',(0,0,3.63),(5.5,1.25,.28),p['green']);d.box('tram clerestory roof',(0,0,3.80),(5.75,1.4,.12),p['cream'])
 for yy in (-.52,.52):
  for A,B in [((-.7,yy,3.85),(.15,yy,4.65)),((.15,yy,4.65),(-.7,yy,5.55)),((.7,yy,3.85),(-.15,yy,4.65)),((-.15,yy,4.65),(.7,yy,5.55))]:d.beam('tram pantograph diamond',A,B,.035,p['iron'])
 d.beam('tram contact strip',(-.8,-.8,5.60),(-.8,.8,5.60),.04,p['bronze']);d.location()

def tree(d,p,x,y,seed):
 rng=random.Random(seed);d.cyl('tree grate',(x,y,.19),1.05,.025,p['iron'],N=24)
 for j in range(7):d.ring('tree grate slot',(x,y,.205),.30+j*.1,.012,p['black'],N=24,M=3)
 d.cyl('street tree trunk',(x,y,2.2),.18,4.0,p['wood'],N=9)
 for j in range(9):
  a=j*2.4;end=(x+1.5*math.cos(a),y+1.5*math.sin(a),3.9+j*.17);d.beam('tree branch',(x,y,2.6+j*.12),end,.075,p['wood'])
  # Individually clustered leaves rather than conspicuous low-poly canopy spheres.
  for k in range(135):
   xx=end[0]+rng.uniform(-1.05,1.05);yy=end[1]+rng.uniform(-1.05,1.05);zz=end[2]+rng.uniform(-.4,1.1)
   t=rng.uniform(0,math.tau);u=Vector((math.cos(t),math.sin(t),rng.uniform(-1.5,1.5))).normalized()*.09;v=Vector((-math.sin(t),math.cos(t),rng.uniform(-1.5,1.5))).normalized()*.04;c=Vector((xx,yy,zz))
   d.mesh('individual tree foliage',[c-u,c-v,c+u,c+v],[(0,1,2,3)],p['leaf'])

def deliverycart(d,p,x,y,a=0):
 d.location(x,y,.13,a)
 for yy in(-.63,.63):
  d.ring('delivery cart iron tyre',(0,yy,.49),.44,.025,p['iron'],'Y',N=40,M=5)
  d.ring('delivery cart wooden felloe',(0,yy,.49),.403,.032,p['wood'],'Y',N=32,M=5)
  d.cyl('delivery cart wheel hub',(0,yy,.49),.095,.22,p['wood'],'Y',N=16)
  for k in range(14):
   t=k*math.tau/14;d.beam('delivery cart oak spoke',(0,yy,.49),(.39*math.cos(t),yy,.49+.39*math.sin(t)),.027,p['wood'])
  d.beam('delivery cart leaf spring',(-.62,yy,.64),(.62,yy,.64),.035,p['iron'])
  d.beam('delivery cart pull handle',(.4,yy*.8,.8),(2.3,yy*.8,1.03),.055,p['wood'])
 d.cyl('delivery cart axle',(0,0,.49),.048,1.45,p['iron'],'Y')
 for j in range(9):d.box('delivery cart bed plank',(-.8+j*.20,0,.78),(.19,1.13,.06),p['wood'])
 for yy in(-.57,.57):
  for z in(.93,1.11,1.29):d.box('delivery cart sideboard',(0,yy,z),(1.85,.045,.14),p['wood'])
  for xx in(-.85,.85):
   d.box('delivery cart upright',(xx,yy,1.1),(.065,.065,.68),p['wood'])
   for zz in(.93,1.11,1.29):d.sphere('cart iron rivet',(xx,yy*1.05,zz),(.012,.009,.012),p['iron'],N=6,M=4)
 for i in range(3):
  xx=-.6+i*.56;d.box('delivery wooden parcel crate',(xx,0,1.1),(.5,.85,.56),p['wood'])
  for z in(.89,1.08,1.27):d.box('crate slat gap',(xx,.429,z),(.47,.005,.016),p['darkwood'])
  for yy in(-.35,.35):d.box('crate steel strap',(xx,yy,1.39),(.52,.025,.012),p['iron'])
 d.text('delivery cart stencil','ADLER  ·  LIEFERDIENST',(0,.602,1.04),.085,p['cream'])
 d.location()

def objects(d,p):
 d.zone='PUBLIC';d.location();fountain(d,p);kiosk(d,p)
 deliverycart(d,p,15,-135,math.pi/2);deliverycart(d,p,4.7,-82,-math.pi/2);deliverycart(d,p,-55,-30,.2)
 rng=random.Random(240)
 for j in range(240):
  x=rng.choice([2.1,17.9])+rng.uniform(-.25,.25);y=rng.uniform(-202,-68);z=.237
  d.mesh('fallen autumn leaf',[(x-.045,y,z),(x,y-.02,z+.008),(x+.045,y,z),(x,y+.025,z+.004)],[(0,1,2,3)],p['cream'] if j%3 else p['red'])
 for x,y in [(-47,5),(-47,-20),(45,5),(63,-30),(-67,-28),(67,22),(-32,22),(35,22)]:lamp(d,p,x,y)
 for y in(-41,-65,-99,-121,-153,-175):
  for x in(-142,-100,-58,51,93,135):lamp(d,p,x,y)
 for x,y in [(-48,9),(-48,-6),(50,10),(50,-4),(-7,-28),(-32,-28),(68,20),(-67,20)]:bench(d,p,x,y)
 for i,(x,y) in enumerate([(-61,-30),(-57,14),(58,13),(65,-26),(-72,-10),(73,-10),(-128,-41),(-82,-41),(94,-41),(137,-41)]):tree(d,p,x,y,i)
 for k in range(9):market(d,p,-67+k*6.1,-33,k)
 for x,y in [(-27,-64),(-32,-64),(-37,-64),(53,-64),(58,-64),(63,-64),(-65,-64),(-70,-64)]:table(d,p,x,y)
 for x,y,a in [(31,22,0),(29,22,.1),(-40,-62,.2),(64,-62,.1),(-66,-31,.8),(44,-20,.2),(49,-20,-.2),(95,-99,.4)]:bicycle(d,p,x,y,a)
 tram(d,p,28,-52);tram(d,p,-90,-57,math.pi)
 for x in (-1.2,21.2):
  for y in (-73,-81,-127,-135,-181,-189):table(d,p,x,y)
  for y in (-95,-147,-199):lamp(d,p,x,y)
 for i,(x,y) in enumerate([(x,y) for x in(-.5,20.5) for y in(-91,-143,-195)]):tree(d,p,x,y,450+i)
 for x,y in [(0,-88),(22,-92),(0,-140),(22,-144),(0,-192),(22,-196)]:bicycle(d,p,x,y,math.pi/2)
 # Bins, bollards, manholes, luggage, a loaded handcart, and paste-up notices.
 for x in range(-71,77,8):
  d.cyl('forecourt bollard',(x,-39.2,.62),.075,.88,p['iron']);d.sphere('bollard rounded cap',(x,-39.2,1.08),(.08,.08,.07),p['iron'])
 for x,y in [(-42,7),(48,8),(-30,-65),(56,-65),(105,-99)]:
  d.cyl('street litter bin',(x,y,.57),.24,.76,p['iron'],N=16);d.ring('bin lip',(x,y,.95),.25,.025,p['bronze'],N=20,M=4)
 for x,y in [(-22,-52),(65,-57),(10,-110)]:
  d.cyl('cast manhole',(x,y,.122),.38,.022,p['iron'],N=32)
  for j in range(6):d.box('manhole rib',(x,y-.25+j*.1,.136),(.5,.025,.012),p['rail'])
 for i in range(18):
  x=5+(i%6)*1.8;y=28+(i//6)*1.3
  if i%3:d.box('leather travel suitcase',(x,y,1.0),(.55,.20,.40),p['darkwood']);d.ring('suitcase handle',(x,y,1.23),.07,.012,p['bronze'],'Y',N=12,M=4)
 d.box('handcart bed',(22,27,.66),(1.5,.8,.13),p['wood'])
 for x in(21.5,22.5):d.ring('handcart wheel',(x,27,.48),.31,.04,p['iron'],'X',N=24,M=4)
 for yy in (26.65,27.35):d.beam('handcart handles',(22.4,yy,.7),(24,yy,.95),.04,p['wood'])
 for i in range(4):d.box('cart parcel',(21.8+(i%2)*.48,26.8+(i//2)*.38,.95),(.42,.34,.47),p['paper'])

def crowds(d,p):
 rng=random.Random(491);masters=[]
 # Existing scans retain their UVs and packed photographic albedo.
 for ob in sorted(bpy.data.objects,key=lambda o:o.name):
  if ob.name.startswith('SCAN_HERO_') and ob.type=='MESH':
   ob['district_subject_id']=['HSR0015','HSR0023','HSR0027','HSR0028','HSR0040','HSR0042'][int(ob.name[-2:])-1];masters.append(ob)
 for folder in sorted((ROOT/'assets/district/scans').iterdir()):
  if not folder.is_dir():continue
  paths=list(folder.glob('*.obj'))
  if not paths:continue
  before=set(bpy.data.objects);bpy.ops.wm.obj_import(filepath=str(paths[0]),forward_axis='Y',up_axis='Z',use_split_objects=False,use_split_groups=False);obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
  if not obs:continue
  ob=obs[0]
  for q in obs[1:]:bpy.data.objects.remove(q,do_unlink=True)
  # Normalize scanned geometry in object local space, independently of OBJ axis conventions.
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);ob.select_set(False)
  mn=Vector(tuple(min(v.co[i] for v in ob.data.vertices) for i in range(3)));mx=Vector(tuple(max(v.co[i] for v in ob.data.vertices) for i in range(3)));height=mx.z-mn.z;scale=1.0 if .8<height<2.2 else 1.75/max(.01,height)
  for v in ob.data.vertices:v.co=(v.co-Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z)))*scale
  dec=ob.modifiers.new('Scan economical street LOD','DECIMATE');dec.ratio=min(1,6000/max(1,len(ob.data.polygons)));bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=dec.name);ob.data.polygons.foreach_set('use_smooth',[True]*len(ob.data.polygons))
  texs=list(folder.glob('*.jpg'))+list(folder.glob('*.png'))
  if texs:
   ma=bpy.data.materials.new('District scanned photographic person '+folder.name);ma.use_nodes=True;nt=ma.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8;im=bpy.data.images.load(str(texs[0]),check_existing=True);im.pack();im.buffers_free();tn=nt.nodes.new('ShaderNodeTexImage');tn.image=im;nt.links.new(tn.outputs[0],bs.inputs['Base Color']);ob.data.materials.clear();ob.data.materials.append(ma)
  ob.name='DIST_SCAN_MASTER_'+folder.name;ob['district_subject_id']=folder.name.split('-')[0];masters.append(ob)
 if not masters:raise RuntimeError('No photographic people; do not substitute primitive figures')
 # Independent local-ground normalization for existing source hero data, without editing source placements.
 normalized=[];subjects=[]
 for i,ob in enumerate(masters):
  me=ob.data.copy();coords=[ob.matrix_world.to_3x3()@v.co for v in me.vertices];mn=Vector(tuple(min(v[j] for v in coords) for j in range(3)));mx=Vector(tuple(max(v[j] for v in coords) for j in range(3)));s=1.0 if ob.name.startswith('DIST_SCAN_MASTER_') else 1.75/(mx.z-mn.z)
  for v,c in zip(me.vertices,coords):v.co=(c-Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z)))*s
  normalized.append(me);subjects.append(ob.get('district_subject_id','unknown'))
  if ob.name.startswith('DIST_SCAN_MASTER_'):
   oldmesh=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
   if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
 pts=[]
 # Foot traffic follows routes, door queues, market aisle and tram stops. Minimum spacing prevents intersections.
 def add(x,y,z=.18,ang=None):
  if any((x-a)**2+(y-b)**2<.63**2 for a,b,_,_ in pts):return False
  tables=[(a,b) for a in (-1.2,21.2) for b in(-73,-81,-127,-135,-181,-189)]+[(-27,-64),(-32,-64),(-37,-64),(53,-64),(58,-64),(63,-64),(-65,-64),(-70,-64)]
  if any((x-a)**2+(y-b)**2<1.12**2 for a,b in tables):return False
  if y<-67 and (x<2.5 or x>17.5):z=.23
  if (x+19)**2+(y+10)**2<5.4**2:return False
  if 2.5<x<18.5 and 23.37<=y<26.4:z=.18+(1+min(3,int((y-23.37)/.76)))*.145
  elif 1.5<x<19.5 and 26.4<=y<62:z=.76
  elif .2<x<3.4 and 17<y<31:z=.18+(y-17)*.58/14
  pts.append((x,y,z,rng.uniform(-math.pi,math.pi) if ang is None else ang));return True
 for i in range(95):add(rng.gauss(10.5,9),rng.uniform(-38,28))
 for i in range(85):add(rng.uniform(-70,72),rng.uniform(-30,20))
 for i in range(70):add(rng.uniform(-70,-16),rng.uniform(-30,-26))
 for y in(-63,-43,-97,-123,-151,-177):
  for i in range(27):add(rng.uniform(-148,151),y+rng.uniform(-.9,.9))
 for i in range(90):
  y=rng.choice([rng.uniform(-97,-69),rng.uniform(-151,-123),rng.uniform(-200,-177)]);x=rng.choice([rng.uniform(-3.5,1.5),rng.uniform(18.5,23.5)]);add(x,y)
 for i in range(22):add(rng.uniform(19,39),-47+rng.uniform(-.7,.7))
 for i in range(14):add(rng.uniform(3,18),rng.uniform(30,36),.76,math.pi)
 pose_used=[0]*len(normalized);assigned=[]
 for i,(x,y,z,a) in enumerate(pts):
  # Prefer less-used poses, avoid identical poses nearby and strongly discourage the same subject at arm's length.
  def score(k):
   penalty=pose_used[k]*2+rng.random()
   for ox,oy,ok in assigned:
    ds=(x-ox)**2+(y-oy)**2
    if ds<15**2 and ok==k:penalty+=1000
    if ds<4.5**2 and subjects[ok]==subjects[k]:penalty+=100
   return penalty
  k=min(range(len(normalized)),key=score);pose_used[k]+=1;assigned.append((x,y,k))
  ob=bpy.data.objects.new(f'DIST_PERSON_{i+1:04d}',normalized[k]);ob['scan_subject_id']=subjects[k];ob['scan_pose_mesh']=normalized[k].name;d.col.objects.link(ob);ob.location=(x,y,z);ob.rotation_euler.z=a;h=rng.uniform(.95,1.055);ob.scale=(h,h,h)
  if i%6==0:
   d.location(x,y,z,a);d.box('traveler leather luggage',(.46,.0,.22),(.42,.17,.40),p['wood']);d.ring('traveler luggage handle',(.46,0,.45),.06,.012,p['bronze'],'Y',N=12,M=4)
 d.location();d.count['photographic scanned people']=len(pts)
 d.records.append({'crowd_instances':len(pts),'scan_poses':len(normalized),'unique_scan_identities':len(set(subjects)),'pose_placement_counts':pose_used,'warning':'Repeated photographic scans; modern clothes, not certified historical costumes. No primitive body substitutes.'})
 return len(pts)
