"""Complete procedural furnishing pass; run on scene/shell.blend.
Blender -b scene/shell.blend --python-exit-code 1 --python assets/interiors/build_interiors.py
"""
import bpy,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'assets/exterior'),str(Path(__file__).parent)]
import model_lib as g
import furniture as f
for args in [('Linen','E4D7BD',.83,0,0,.007),('Upholstery','C37A50',.83,0,0,.006),('OliveFabric','7C8A62',.8,0,0,.006),('Water','6CA9AC',.1,0,.45),('Paper','E3D0AD',.65)]:
 if args[0] not in bpy.data.materials:g.material(*args)
for name in ['Limestone','Plaster','Terracotta','Teal','Bronze','Oak','Walnut','Terrazzo','Tile','Porcelain','Steel','Black','Glass','Linen','Upholstery','OliveFabric','Leaf','Soil','Concrete','Paving','Water','Paper','Glow']:g.M[name]=bpy.data.materials[name]
D=json.loads((ROOT/'assets/exterior/aligned-programme.json').read_text());s=bpy.context.scene
for c in list(bpy.data.collections):
 if c.name.endswith('_FURNITURE'):bpy.data.collections.remove(c)
SCHEDULE=[]

def tv(name,x,y,angle=0):
 from mathutils import Vector
 o=g.ORIGIN.copy();a=g.ANGLE
 with g.scope(origin=(o.x+math.cos(a)*x-math.sin(a)*y,o.y+math.sin(a)*x+math.cos(a)*y,o.z),angle=a+angle,fixture='media_console'):
  g.box(name+'_CONSOLE',(0,0,.28),(1.8,.38,.42),'Oak',.025)
  for xx in [-.60,0,.60]:g.box(name+'_DOOR',(xx,-.205,.28),(.55,.025,.34),'Walnut',.012)
  g.box(name+'_TV_FRAME',(0,.07,1.03),(1.40,.06,.81),'Black',.02);g.box(name+'_SCREEN',(0,.031,1.03),(1.33,.008,.74),'Teal',.012)
  for xx in [-.4,.4]:g.rod(name+'_TV_FOOT',(xx-.08,-.08,.53),(xx,.07,.65),.016,'Black')

def art(name,x,y,z,width=1.2,angle=0):
 # original abstract composition; geometric art, not a downloaded image.
 from mathutils import Vector
 o=g.ORIGIN.copy();a=g.ANGLE
 with g.scope(origin=(o.x+math.cos(a)*x-math.sin(a)*y,o.y+math.sin(a)*x+math.cos(a)*y,o.z+z),angle=a+angle,fixture='art'):
  g.box(name+'_FRAME',(0,0,0),(width,.055,width*.75),'Oak',.012);g.box(name+'_CANVAS',(0,-.035,0),(width-.08,.012,width*.75-.08),'Paper')
  g.box(name+'_BLOCK',(-width*.16,-.046,-width*.12),(width*.4,.008,width*.27),'Terracotta',.01)
  o=g.cylinder(name+'_DISC',(width*.15,-.05,width*.10),width*.16,.009,'Teal',32);o.rotation_euler.x=math.pi/2

def pendant(name,x,y,clear):
 g.cylinder(name+'_ROSETTE',(x,y,clear-.04),.11,.04,'Bronze');g.rod(name+'_CORD',(x,y,clear-.05),(x,y,clear-.64),.008,'Black')
 g.lathe(name+'_SHADE',(x,y,clear-.84),[(.30,0),(.13,.26),(.12,.26),(.28,0)],'Terracotta',28);g.cylinder(name+'_DIFFUSER',(x,y,clear-.84),.27,.012,'Glow')
 g.light(name+'_PENDANT_LIGHT',(x,y,clear-.88),65,.65)

def rug(name,x,y,w,d,mat='Linen'):
 g.box(name,(x,y,.015),(w,d,.025),mat,.035)
 for k in range(5):g.box(name+'_STRIPE',(x-w/2+.12+k*.055,y,.03),(.018,d-.12,.002),'Upholstery')

def floorlamp(name,x,y):
 g.cylinder(name+'_BASE',(x,y,.04),.20,.04,'Bronze');g.rod(name+'_STEM',(x,y,.07),(x,y,1.58),.018,'Bronze')
 g.lathe(name+'_SHADE',(x,y,1.45),[(.25,0),(.17,.36),(.16,.36),(.23,0)],'Linen',28);g.sphere(name+'_BULB',(x,y,1.52),(.09,.09,.13),'Glow')
 g.light(name+'_LIGHT',(x,y,1.38),30,.6)

def living(r,home,l,clear):
 x,y,xx,yy=r['rect'];w=xx-x;d=yy-y;name=r['id'];north=y>10
 if north:
  # Cooking run against the hall partition, never cupboards across glazing.
  if home['id'].endswith('B'):
   with g.scope(origin=(x+.35,y+2.8,l['elevation_m']+.04),angle=math.pi/2):f.kitchen(name+'_KITCHEN',0,0,5)
  else:
   with g.scope(origin=(xx-.35,yy-.50,l['elevation_m']+.04),angle=-math.pi/2):f.kitchen(name+'_KITCHEN',0,0,5)
  f.sofa(name+'_SOFA',w*.43,2.25,width=2.35+(int(l['id'][-1])%2)*.2,mat='OliveFabric' if home['id'].endswith('B') else 'Upholstery')
  tv(name+'_MEDIA',w*.43,.34,math.pi);rug(name+'_RUG',w*.43,1.32,2.7,1.8)
  g.cylinder(name+'_COFFEE_TOP',(w*.43,1.10,.39),.43,.065,'Walnut',28)
  for a in [0,2.1,4.2]:g.rod(name+'_COFFEE_LEG',(w*.43+.24*math.cos(a),1.10+.24*math.sin(a),.07),(w*.43+.28*math.cos(a),1.10+.28*math.sin(a),.36),.025,'Walnut')
  f.dining(name+'_DINING',2.35,d-1.9);pendant(name+'_DINING',2.35,d-1.9,clear)
  floorlamp(name+'_FLOORLAMP',w-.55 if home['id'].endswith('B') else .55,2.65);f.plant(name+'_PLANT',w-.6 if home['id'].endswith('B') else .6,d-.6,size=1.2)
  art(name+'_ART',w-1.05,.07,1.7,1.15,math.pi)
 else:
  with g.scope(origin=(x+.35,y+.55,l['elevation_m']+.04),angle=math.pi/2):f.kitchen(name+'_KITCHEN',0,0,5)
  f.sofa(name+'_SOFA',3.35,d*.47,width=2.4,angle=math.pi/2,mat='OliveFabric' if l['id'] in ['L03','L05'] else 'Upholstery')
  tv(name+'_MEDIA',w-.28,d*.45,-math.pi/2);rug(name+'_RUG',5.0,d*.47,2.6,2.6,'OliveFabric')
  g.box(name+'_COFFEE_TOP',(5.10,d*.47,.4),(1.1,.65,.08),'Walnut',.15)
  for dx in [-.38,.38]:g.rod(name+'_COFFEE_FOOT',(5.1+dx,d*.47,.08),(5.1+dx,d*.47,.36),.035,'Walnut')
  f.dining(name+'_DINING',w-2.35,d-1.22);pendant(name+'_DINING',w-2.35,d-1.22,clear)
  f.plant(name+'_PLANT',w-.6,.65,size=1.3);floorlamp(name+'_FLOORLAMP',2.5,d-.7)
  art(name+'_ART',1.35,d-.09,1.72,1.25,0)
  if w>10:
   f.chair(name+'_LOUNGE_CHAIR',7.3,1.5,-math.pi/2,mat='Linen');f.chair(name+'_LOUNGE_CHAIR',7.3,2.8,-math.pi/2,mat='Linen')
 # actual kitchen placement, not the superseded blockout kitchen rectangle
 SCHEDULE.append({'home':home['id'],'level':l['id'],'room':r['id'],'kitchen':'hall-wall run' if north else 'west partition run','primary_objects':'multi-component kitchen / hob / oven / refrigerator / sink / dining / sofa / media / lighting'})

def bicycle(name,x,y):
 with g.scope(fixture='bicycle'):
  for dx in [-.58,.58]:g.torus(name+'_TYRE',(x+dx,y,.37),.31,.028,'Black',axis='Y');g.torus(name+'_RIM',(x+dx,y,.37),.275,.012,'Steel',axis='Y')
  nodes=[(x-.58,y,.37),(x-.12,y,.40),(x-.23,y,.94),(x+.38,y,.91),(x+.58,y,.37)]
  for a,b in [(0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(1,4)]:g.rod(name+'_FRAME',nodes[a],nodes[b],.022,'Teal')
  g.box(name+'_SADDLE',(x-.25,y,1.0),(.25,.15,.055),'Walnut',.035);g.rod(name+'_HANDLE',(x+.38,y,.91),(x+.40,y,1.12),.02,'Steel');g.rod(name+'_BAR',(x+.4,y-.25,1.12),(x+.4,y+.25,1.12),.018,'Steel')
  for dx in [-.58,.58]:
   for k in range(10):
    a=k*math.tau/10;g.rod(name+'_SPOKE',(x+dx,y,.37),(x+dx+.27*math.cos(a),y,.37+.27*math.sin(a)),.0035,'Steel',6)

def public(r,l,clear):
 x,y,xx,yy=r['rect'];w=xx-x;d=yy-y;n=r['id'];id=n.split('_',1)[1]
 if id=='CAFE':
  for px in [1.7,4.9]:
   for py in [1.65,4.75]:
    with g.scope(fixture='cafe_seating'):
     g.cylinder(n+'_TABLE_TOP',(px,py,.76),.45,.06,'Oak',28);g.cylinder(n+'_TABLE_STEM',(px,py,.39),.055,.66,'Teal');g.cylinder(n+'_TABLE_BASE',(px,py,.06),.29,.06,'Teal')
     for dx,dy,a in [(-.8,0,-math.pi/2),(.8,0,math.pi/2),(0,.8,0),(0,-.8,math.pi)]:f.chair(n+'_CHAIR',px+dx,py+dy,a)
     g.lathe(n+'_CUP',(px,py,.80),[(.05,0),(.055,.1),(.045,.102),(.04,.02)],'Porcelain',16)
  pendant(n+'_PENDANT',3.4,3.4,clear);f.plant(n+'_PLANT',.5,d-.5,size=1.3)
 elif id=='PREP':
  with g.scope(origin=(xx-.35,yy-.4,l['elevation_m']+.04),angle=-math.pi/2):f.kitchen(n,0,0,3)
 elif id=='CAFE_PASS':
  with g.scope(fixture='cafe_counter'):
   g.box(n+'_COUNTER',(w-.4,d/2,.49),(.65,1.9,.90),'Terracotta',.05);g.box(n+'_COUNTER_TOP',(w-.4,d/2,.97),(.75,2.0,.07),'Terrazzo',.035)
   g.box(n+'_COFFEE_MACHINE',(w-.4,d/2,1.23),(.48,.65,.45),'Steel',.05)
   for py in [d/2-.18,d/2+.18]:g.rod(n+'_BREW_GROUP',(w-.66,py,1.36),(w-.68,py,1.17),.05,'Steel');g.lathe(n+'_ESPRESSO_CUP',(w-.68,py,1.01),[(.04,0),(.05,.07),(.04,.071)],'Porcelain',16)
   g.box(n+'_MENU',(w-.08,d/2,1.98),(.03,1.3,.63),'Teal',.03)
 elif id=='LOBBY':
  with g.scope(fixture='reception'):
   g.box(n+'_DESK',(.75,2,.48),(1,2.05,.90),'Oak',.06);g.box(n+'_DESK_TOP',(.75,2,.96),(1.10,2.15,.06),'Terrazzo',.035)
   g.box(n+'_MONITOR',(.72,2.2,1.24),(.04,.55,.36),'Black',.015)
   f.chair(n+'_RECEPTION_CHAIR',1.7,2,math.pi/2)
  with g.scope(fixture='mail_parcel'):
   for row in range(4):
    for col in range(4):
     px=3.35+col*.43;pz=.43+row*.37;g.box(n+'_MAILBOX',(px,d-.20,pz),(.40,.30,.33),'Teal',.015);g.box(n+'_MAIL_SLOT',(px,d-.365,pz+.08),(.26,.012,.018),'Black');g.sphere(n+'_MAIL_LOCK',(px+.12,d-.37,pz-.06),(.025,.012,.025),'Bronze',8,6)
   for k in range(3):g.box(n+'_PARCEL',(3.4+k*.45,d-.66,.3),(.35,.35,.50),'Paper',.015)
  art(n+'_WALL_ART',.08,.95,1.9,1,-math.pi/2);f.plant(n+'_PLANT',w-.45,.5,size=1.1)
 elif id=='VESTIBULE':
  rug(n+'_ENTRY_MAT',w/2,d/2,2.2,1.3,'Teal');g.sign(n+'_ENTRY','CASA',(1.7,1.1,.06),.35,'Limestone','XY')
 elif id=='BIKES':
  for py in [1.1,2.6,4.1,5.6]:bicycle(n+'_BIKE',1.3,py)
  with g.scope(fixture='bicycle_rack'):
   for py in [1.1,2.6,4.1,5.6]:g.rod(n+'_RACK',(1.8,py-.25,.08),(1.8,py-.25,.7),.025,'Steel');g.rod(n+'_RACK',(1.8,py-.25,.7),(1.8,py+.25,.7),.025,'Steel')
 elif id=='WASTE':
  with g.scope(fixture='waste_bin'):
   for px,mat in [(1,'Teal'),(2.5,'Terracotta'),(4,'OliveFabric')]:
    g.box(n+'_BIN',(px,d-1.6,.56),(.90,.82,1.0),mat,.10);g.box(n+'_LID',(px,d-1.6,1.10),(.96,.90,.08),'Black',.06)
    for dx in [-.30,.30]:o=g.cylinder(n+'_WHEEL',(px+dx,d-1.25,.12),.10,.08,'Black',16);o.rotation_euler.x=math.pi/2
    g.box(n+'_BIN_SLOT',(px,d-2.06,.83),(.30,.02,.09),'Black',.02)
  
  for k in range(4):g.box(n+'_CLEANING_SHELF',(1.1,.3,.25+k*.4),(1.5,.45,.05),'Steel')
  for k in range(5):g.lathe(n+'_DETERGENT',(.6+k*.25,.3,1.5),[(.06,0),(.06,.20),(.025,.23),(.025,.28)],'Teal',12)
 elif id=='PLANT':
  with g.scope(fixture='plant_equipment'):
   for py in [2,4.5]:
    g.lathe(n+'_DHW_CYLINDER',(1.1,py,.08),[(.35,0),(.43,.1),(.43,1.62),(.33,1.75),(.10,1.78)],'Steel',32)
    g.rod(n+'_HOT_PIPE',(1.1,py,1.85),(1.1,py,2.45),.04,'Bronze');g.rod(n+'_SUPPLY_PIPE',(1.1,py,2.45),(3.6,py,2.45),.04,'Bronze')
   for py in [2,4.5]:
    g.box(n+'_HEAT_EXCHANGER',(w-1,py,.75),(1.25,.75,1.3),'Steel',.06)
    for k in range(9):g.box(n+'_VENT',(w-1,py-.39,.35+k*.1),(1.0,.03,.025),'Teal')
    g.rod(n+'_HEADER',(w-1,py,1.5),(w-1,py,2.45),.055,'Bronze');g.torus(n+'_VALVE',(w-1,py-.15,1.7),.12,.018,'Terracotta',axis='Y')
   g.box(n+'_ELECTRICAL_PANEL',(w-.95,d-.2,1.35),(1.7,.30,1.5),'Teal',.025)
   for k in range(6):g.box(n+'_CIRCUIT_BREAKER',(w-1.60+k*.26,d-.365,1.35),(.10,.03,.25),'Black',.008)
   g.box(n+'_DUCT',(w/2,d/2,clear-.30),(.65,d-.3,.40),'Steel',.035)
 elif id=='PARCEL':
  with g.scope(fixture='parcel_storage'):
   for row in range(3):
    for col in range(8):
     px=.50+col*.81;pz=.47+row*.62;g.box(n+'_LOCKER',(px,d-.25,pz),(.76,.42,.56),'Teal',.02);g.box(n+'_LOCKER_HANDLE',(px+.25,d-.48,pz),(.035,.03,.13),'Bronze',.01)
   for k in range(4):g.box(n+'_PACKAGE',(.6+k*.85,d-1,.3),(.60,.55,.50),'Paper',.025)
 elif id=='WC':
  with g.scope(fixture='accessible_public_toilet'):
   px=.72;py=d-.60;g.lathe(n+'_WC',(px,py,.08),[(.16,0),(.15,.20),(.25,.34),(.26,.38),(.22,.39),(.18,.32),(.06,.25)],'Porcelain',28)
   q=g.torus(n+'_WC_SEAT',(px,py,.48),.25,.03,'Porcelain');q.scale.y=1.25
   g.box(n+'_WC_CISTERN',(px,py+.24,.70),(.45,.20,.45),'Porcelain',.06)
   for xx in [px-.4,px+.4]:g.rod(n+'_GRAB',(xx,py+.25,.79),(xx,py-.5,.79),.02,'Steel');g.rod(n+'_GRAB_SUPPORT',(xx,py+.25,.15),(xx,py+.25,.79),.018,'Steel')
   g.lathe(n+'_SINK',(w-.38,.60,.77),[(.06,0),(.24,.10),(.25,.15),(.22,.16),(.17,.05),(.04,.03)],'Porcelain',28);f.faucet(n,w-.26,.74,.91)
   g.box(n+'_MIRROR',(w-.07,.6,1.5),(.025,.65,.85),'Steel',.025)
 elif id=='CLEANER':
  with g.scope(fixture='cleaning_equipment'):
   g.lathe(n+'_UTILITY_BASIN',(w-.5,.8,.73),[(.10,0),(.32,.20),(.34,.25),(.30,.26),(.25,.05)],'Steel',24)
   for k in range(4):g.box(n+'_SHELF',(w/2,d-.3,.30+k*.45),(w-.4,.5,.05),'Steel',.01)
   for k in range(3):g.rod(n+'_MOP',(.35+k*.22,d-.6,.1),(.35+k*.22,d-.5,1.7),.015,'Oak');g.sphere(n+'_MOP_HEAD',(.35+k*.22,d-.6,.1),(.22,.24,.15),'Linen',12,8)
 else:
  # Reading rooms, winter garden and neighbourhood lounge: complete multi-purpose seating.
  f.sofa(n+'_SOFA',min(w/2,3),2.4,width=2.3,mat='OliveFabric');rug(n+'_RUG',min(w/2,3),1.5,2.8,2.0)
  g.cylinder(n+'_COFFEE',(min(w/2,3),1.15,.40),.50,.07,'Oak',28);g.cylinder(n+'_COFFEE_PEDESTAL',(min(w/2,3),1.15,.20),.10,.35,'Teal')
  f.dining(n+'_SHARED_TABLE',min(w/2,3),d-1.55);pendant(n+'_PENDANT',min(w/2,3),d-1.55,clear)
  with g.scope(origin=(xx-.2,y+2,l['elevation_m']+.04),angle=-math.pi/2):f.bookcase(n+'_LIBRARY',0,0,width=2,height=2)
  for px,py in [(.55,.55),(.55,d-.55),(w-.55,d-.55)]:f.plant(n+'_PLANT',px,py,size=1.4 if id=='WINTER_GARDEN' else 1)
  if id=='WINTER_GARDEN':
   f.sofa(n+'_SECOND_SOFA',w-2,3.2,width=2.3,angle=-math.pi/2,mat='Linen')
   for px in [4.7,6.6,8.2]:f.plant(n+'_WINTER_PLANT',px,d-.55,size=1.7)

for l in D['levels']:
 lid=l['id'];z=l['elevation_m'];clear=l['storey_height_m']-.22;parent=bpy.data.collections[lid];col=g.collection(lid+'_FURNITURE',parent)
 homeby={h['id']:h for h in l['homes']}
 for r in l['rooms']:
  if r['kind'] in ['stair','elevator','service'] and r['id'].endswith(('RISER_E','RISER_W','LIFT','STAIR_A','STAIR_B')):continue
  x,y,xx,yy=r['rect'];w=xx-x;d=yy-y
  with g.scope(col,origin=(x,y,z+.04),angle=0,level=lid,room_id=r['id'],home=r['home'] or '',fixture='furnishing'):
   if r['home']:
    h=homeby[r['home']]
    if r['kind']=='living':living(r,h,l,clear-.04)
    elif r['kind']=='bedroom':
     north=y>10;east_head=(not (r['home'] or '').endswith('B')) if north else int(lid[-1])%2==1
     f.bed(r['id'],w-1.25 if east_head else 1.25,d*(.585 if north else .57),angle=-math.pi/2 if east_head else math.pi/2,width=1.6 if w>3.2 else 1.4)
     if north:f.wardrobe(r['id']+'_WARDROBE',1.2,.33,width=1.8)
     else:f.wardrobe(r['id']+'_WARDROBE',.34 if east_head else w-.34,d-1.03,width=1.65,angle=math.pi/2 if east_head else -math.pi/2)
     art(r['id']+'_ART',.06 if east_head else w-.06,d*.75 if north else d*.43,1.7,.85,-math.pi/2 if east_head else math.pi/2)
    elif r['kind']=='bathroom':f.bathroom(r['id'],0,0,w,d)
    elif r['kind']=='storage':f.wardrobe(r['id']+'_CLOSET',w/2,.35,width=min(w-.15,1.8),angle=math.pi)
    elif r['kind']=='corridor':
     # Shallow entry shelf rather than a wardrobe reducing the clear hall below 1 m.
     if w<2:g.box(r['id']+'_SHELF',(.12,d-.65,.83),(.21,.85,.07),'Oak',.02)
     else:g.box(r['id']+'_ENTRY_SHELF',(w-.9,d-.13,.83),(1.25,.20,.07),'Oak',.02)
   elif r['id'].endswith('_CORE'):
    with g.scope(fixture='corridor_furnishing'):
     for px in [2,13]:
      for j in range(5):g.box(r['id']+'_BENCH_SLAT',(px,3.7+j*.07,.46),(1.5,.05,.04),'Oak',.01)
      for dx in [-.55,.55]:g.box(r['id']+'_BENCH_LEG',(px+dx,3.85,.23),(.06,.28,.43),'Teal',.01)
     f.plant(r['id']+'_PLANT',.55,3.9,size=1.1)
   elif 'RISER_' not in r['id']:public(r,l,clear-.04)
   # Every room has an actual fixture and practical light, not one global light.
   with g.scope(fixture='room_lighting'):
    centres=[(3.5,1.35),(w-3.5,1.35)] if r['id'].endswith('_CORE') else [(w/2,d/2)]
    for lx,ly in centres:
     g.cylinder(r['id']+'_CEILING_DISC',(lx,ly,clear-.16),.24,.055,'Bronze',24);g.cylinder(r['id']+'_DIFFUSER',(lx,ly,clear-.20),.215,.015,'Glow',24)
     g.light(r['id']+'_PRACTICAL',(lx,ly,clear-.24),180 if r['kind'] in ['living','public','garden'] or r['id'].endswith('_CORE') else 65,size=min(2.5,w*.6,d*.6))
 # Save genuine human-eye-level cameras. All room walls/envelope restored for interiors.
 if lid=='L01':
  g.camera('CAM_L01_INTERIOR',(1.2,6.1,1.62),(5.8,1.8,1.3),lens=24)
  g.camera('CAM_L01_DETAIL',(13.1,3.7,1.62),(13.8,6.6,1.35),lens=24)
 elif lid=='L06':
  g.camera('CAM_L06_INTERIOR',(1.2,13.6,z+1.62),(8,17.6,z+1.35),lens=24)
  rr=next(r for r in l['rooms'] if r['home']=='6A' and r['kind']=='living');x,y,xx,yy=rr['rect'];g.camera('CAM_L06_DETAIL',(xx-.7,yy-.7,z+1.62),(x+2.8,y+2.3,z+1.25),lens=24)
 else:
  # Distribute eye-level evidence across distinct homes and room types.
  suffix='B' if lid=='L03' else ('C' if lid=='L04' else 'A')
  rr=next(r for r in l['rooms'] if (r['home'] or '').endswith(suffix) and r['kind']=='living');x,y,xx,yy=rr['rect']
  if suffix=='C':g.camera('CAM_'+lid+'_INTERIOR',(xx-.65,yy-.6,z+1.62),(x+2.5,y+1.6,z+1.2),lens=24)
  elif suffix=='B':g.camera('CAM_'+lid+'_INTERIOR',(xx-.65,y+.65,z+1.62),(x+.8,yy-1,z+1.25),lens=25)
  else:g.camera('CAM_'+lid+'_INTERIOR',(x+.65,y+.60,z+1.62),(xx-.65,yy-1.1,z+1.25),lens=25)
  if lid=='L02':
   rr=next(r for r in l['rooms'] if (r['home'] or '').endswith('C') and r['kind']=='bathroom');x,y,xx,yy=rr['rect']
   g.camera('CAM_'+lid+'_DETAIL',(x+1.1,yy-.40,z+1.62),(x+1.2,y+1.35,z+1.1),lens=18)
  elif lid=='L05':
   rr=next(r for r in l['rooms'] if (r['home'] or '').endswith('B') and r['kind']=='bedroom');x,y,xx,yy=rr['rect']
   g.camera('CAM_'+lid+'_DETAIL',(x+.65,y+.95,z+1.62),(xx-.75,yy-.9,z+1.15),lens=22)
  else:
   rooms=[r for r in l['rooms'] if (r['home'] or '').endswith('C') and r['kind']=='bedroom'];rr=rooms[-1] if lid=='L04' else rooms[0];x,y,xx,yy=rr['rect']
   # The previous north-east camera intersected a wardrobe: move to clear south-east aisle.
   g.camera('CAM_'+lid+'_DETAIL',(xx-.65,y+.60,z+1.62),((x+xx)/2,y+(yy-y)*.60,z+1.1),lens=22)
s['stage']='Detailed shell and furnished interiors; visual QA and independent review outstanding';s['homes_modelled']=14
(ROOT/'assets/interiors/furnishing-schedule.json').write_text(json.dumps(SCHEDULE,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene/interiors.blend'),compress=True)
print('INTERIORS_SAVED',len(s.objects),'objects; 14 kitchen assemblies, bedrooms, bathrooms, storage and lighting; awaiting visual audit')
