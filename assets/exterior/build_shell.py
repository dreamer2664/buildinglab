"""Casa dei Colori BLDG-2. Run Blender -b --python-exit-code 1 --python assets/exterior/build_shell.py.
Native metric architecture; no image assets/add-ons. Uses accepted-for-development BLDG-1 dimensions.
"""
import bpy,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
import model_lib as g
D=json.loads((ROOT/'design/programme.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
g.materials();s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False
s.cycles.max_bounces=6;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=2;s.cycles.transmission_bounces=4;s.cycles.transparent_max_bounces=4;s.cycles.volume_bounces=0;s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False;s.cycles.sample_clamp_indirect=3
s.view_settings.view_transform='AgX';s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s['project']='Casa dei Colori';s['stage']='Detailed architectural development; independent acceptance outstanding';s['floor_count']=6;s['code_approval']=False
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.69,.79,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35

# Actual room-edge wall union, divided at cutaway datum. Door jamb gaps continue to 2.20 m.
def partitions(l,z,clear,low,high):
 rs=l['rooms'];strips=[];xs={.3,25.7};ys={.3,19.7}
 for r in rs:
  x,y,xx,yy=r['rect']
  edges=[('H',y,x,xx),('H',yy,x,xx),('V',x,y,yy),('V',xx,y,yy)]
  for axis,p,a,b in edges:
   if axis=='H' and (p<.5 or p>19.5):continue
   if axis=='V' and (p<.5 or p>25.5):continue
   # Snap neighbouring room-edge pairs to the same nominal 200 mm partition centreline.
   near=[]
   for rr in rs:
    if rr is r:continue
    v=rr['rect'];vals=[v[1],v[3]] if axis=='H' else [v[0],v[2]]
    near += [q for q in vals if .02<abs(q-p)<.25]
   if near:p=(p+min(near,key=lambda q:abs(q-p)))/2
   q=(a-.1,p-.1,b+.1,p+.1) if axis=='H' else (p-.1,a-.1,p+.1,b+.1)
   strips.append(q);xs.update([q[0],q[2]]);ys.update([q[1],q[3]])
 holes=[]
 for d in l['doors']:
  x,y,w=d['x'],d['y'],d['width'];q=(x-w/2,y-.35,x+w/2,y+.35) if d['orientation']=='H' else (x-.35,y-w/2,x+.35,y+w/2)
  holes.append(q);xs.update([q[0],q[2]]);ys.update([q[1],q[3]])
 xs=sorted(q for q in xs if .2<=q<=25.8);ys=sorted(q for q in ys if .2<=q<=19.8)
 def inside(x,y,r):return r[0]<x<r[2] and r[1]<y<r[3]
 cells=[(a,b,c,d,any(inside((a+b)/2,(c+d)/2,q) for q in holes)) for a,b in zip(xs,xs[1:]) for c,d in zip(ys,ys[1:]) if b-a>1e-5 and d-c>1e-5 and any(inside((a+b)/2,(c+d)/2,q) for q in strips)]
 for zz,h,allow,col in [(z+.04,1.06,False,low),(z+1.10,1.1,False,high),(z+2.2,clear-2.2,True,high)]:
  v=[];f=[]
  for a,b,c,d,hole in cells:
   if hole and not allow:continue
   n=len(v);v.extend([(a,c,zz),(b,c,zz),(b,d,zz),(a,d,zz),(a,c,zz+h),(b,c,zz+h),(b,d,zz+h),(a,d,zz+h)])
   f.extend([tuple(n+k for k in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
  with g.scope(col,role='partition'):g.obj(l['id']+'_PARTITIONS_'+str(zz),v,f,'Plaster')

# Facade bands with genuine openings; generate glazed assemblies from actual room frontage.
WINDOWS=[]
def facade(l,z,clear,col):
 lid=l['id'];opens={k:[] for k in ['S','N','W','E']}
 for r in l['rooms']:
  x,y,xx,yy=r['rect']
  for face,a,b in [('S',x,xx),('N',x,xx),('W',y,yy),('E',y,yy)]:
   touch={'S':y<.5,'N':yy>19.5,'W':x<.5,'E':xx>25.5}[face]
   if not touch:continue
   # Stair/service ventilation is modeled, but not counted as residential daylight.
   if r['kind'] in ['service','storage'] and lid=='L01':sill,head=.95,2.7
   elif r['kind']=='bathroom':sill,head=1.45,2.5
   else:sill,head=(.15,min(3.05,clear-.25)) if lid=='L01' else (.78,2.55)
   length=b-a;count=max(1,round(length/3.8));spacing=length/count
   for k in range(count):
    center=a+(k+.5)*spacing;width=min(2.45,spacing-1)
    if width<.6:continue
    balcony=face=='S' and lid!='L01' and r['kind'] in ['living','bedroom']
    if balcony:sill=.08;head=2.55
    opens[face].append(dict(a=center-width/2,b=center+width/2,sill=sill,head=head,room=r['id'],balcony=balcony,service=r['kind'] in ['service','storage'] and lid=='L01'))
 # Entrance and two independent stair exit doors replace overlapping low window panels.
 if lid=='L01':
  for face,pos,w,room in [('S',13,1.8,'L01_VESTIBULE'),('W',7.75,1.1,'L01_STAIR_A'),('E',7.75,1.1,'L01_STAIR_B'),('E',3.70588,1.2,'L01_WASTE')]:
   opens[face]=[q for q in opens[face] if q['b']<pos-w/2-.1 or q['a']>pos+w/2+.1]
   opens[face].append(dict(a=pos-w/2,b=pos+w/2,sill=.04,head=2.7,room=room,balcony=False,service=False))
 with g.scope(col,role='facade'):
  for face,opening in opens.items():
   length=26 if face in ['S','N'] else 20;start=0
   def cube(a,b,h0,h1,mat='Limestone',depth=.30):
    if b-a<.001 or h1-h0<.001:return
    center=(a+b)/2;loc=(center,.15 if face=='S' else 19.85,z+(h0+h1)/2) if face in ['S','N'] else (.15 if face=='W' else 25.85,center,z+(h0+h1)/2)
    return g.box(lid+'_'+face+'_WALL',loc,(b-a,depth,h1-h0) if face in ['S','N'] else (depth,b-a,h1-h0),mat)
   for q in sorted(opening,key=lambda o:o['a']):
    cube(start,q['a'],0,clear);cube(q['a'],q['b'],0,q['sill']);cube(q['a'],q['b'],q['head'],clear);start=q['b']
    # Window assembly local X along facade, local Y inward, south-facing front.
    center=(q['a']+q['b'])/2;width=q['b']-q['a'];height=q['head']-q['sill'];rotation={'S':0,'N':math.pi,'W':-math.pi/2,'E':math.pi/2}[face]
    origin={'S':(center,.15,z+q['sill']),'N':(center,19.85,z+q['sill']),'W':(.15,center,z+q['sill']),'E':(25.85,center,z+q['sill'])}[face]
    with g.scope(col,origin=origin,angle=rotation,role='window',room_id=q['room']):
     for x in [-width/2,width/2]:g.box(lid+'_WINDOW_REVEAL',(x,-.04,height/2),(.13,.48,height-.12),'Terracotta',.018)
     for zz in [0,height]:g.box(lid+'_WINDOW_SILL',(0,-.04,zz),(width+.18,.48,.12),'Terracotta',.015)
     for x in [-width/2+.055,0,width/2-.055]:g.box(lid+'_WINDOW_MULLION',(x,.015,height/2),(.045,.09,height),'Teal',.005)
     for zz in [.045,height-.045]:g.box(lid+'_WINDOW_FRAME',(0,.015,zz),(width,.09,.045),'Teal',.005)
     if q['service']:
      for k in range(13):g.box(lid+'_VENT_LOUVRE',(0,-.035,.08+k*(height-.16)/12),(width-.12,.10,.045),'Teal')
     else:
      for side in [-1,1]:g.box(lid+'_GLAZING',(side*width/4,.025,height/2),(width/2-.055,.016,height-.10),'Glass')
      g.box(lid+'_GLAZING_HANDLE',(.13,.09,1.05),(.035,.035,.17),'Bronze',.01)
     if q['balcony']:
      with g.scope(role='balcony'):
       g.box(lid+'_BALCONY_SLAB',(0,-.85,-.07),(width+.55,1.6,.18),'Concrete',.025)
       g.box(lid+'_BALCONY_TILE',(0,-.85,.035),(width+.48,1.53,.025),'Terrazzo')
       for x in [-width/2-.2,width/2+.2]:
        g.rod(lid+'_BALCONY_CORNER',(x,-1.55,.08),(x,-1.55,1.15),.025,'Teal');g.rod(lid+'_BALCONY_RETURN',(x,-1.55,1.15),(x,-.15,1.15),.026,'Teal')
       g.rod(lid+'_BALCONY_TOP',(-width/2-.2,-1.55,1.15),(width/2+.2,-1.55,1.15),.03,'Teal')
       for k in range(int((width+.4)/.12)+1):
        xx=-width/2-.2+k*.12
        g.rod(lid+'_BALCONY_BALUSTER',(xx,-1.55,.12),(xx,-1.55,1.14),.012,'Teal',8)
       g.lathe(lid+'_BALCONY_PLANTER',(-width/2+.25,-1.2,.1),[(.14,0),(.2,.32),(.21,.36),(.18,.37),(.16,.30)],'Terracotta',16)
       for k in range(7):g.sphere(lid+'_BALCONY_LEAF',(-width/2+.25+.12*math.sin(k),-1.2+.1*math.cos(k),.50+.04*k),(.3,.15,.24),'Leaf',10,6)
    WINDOWS.append({'level':lid,'room':q['room'],'face':face,'width_m':width,'sill_m':q['sill'],'head_m':q['head']})
   cube(start,length,0,clear)
  # Horizontal terracotta string courses and limestone cornices establish six readable storeys.
  for y in [-.045,20.045]:g.box(lid+'_STRINGCOURSE',(13,y,z+.14),(26.3,.16,.22),'Terracotta',.015)
  for x in [-.045,26.045]:g.box(lid+'_STRINGCOURSE',(x,10,z+.14),(.16,20.3,.22),'Terracotta',.015)

def flight(name,x,y,z,n,rise,direction):
 # Closed sawtooth concrete stair, not separate unsupported planks.
 profile=[(y-direction*.14,z-.18)]
 for k in range(n):
  yy=y+direction*k*.28;zz=z+(k+1)*rise
  profile.extend([(yy-direction*.14,zz),(yy+direction*.14,zz)])
 profile.extend([(y+direction*((n-1)*.28+.14),z+n*rise-.20),(y-direction*.14,z-.18)])
 v=[(xx,yy,zz+.04) for xx in [x,x+1.35] for yy,zz in profile];N=len(profile);f=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 o=g.obj(name,v,f,'Concrete');o['role']='stair_flight';o['risers']=n;o['rise_m']=rise
 for k in range(n):
  yy=y+direction*k*.28;zz=z+(k+1)*rise+.045
  g.box(name+'_NOSING',(x+.675,yy+direction*.11,zz),(1.35,.05,.02),'Oak',.008)
 for xx in [x+.025,x+1.325]:
  g.rod(name+'_HANDRAIL',(xx,y-direction*.14,z+rise+1.04),(xx,y+direction*((n-1)*.28+.14),z+n*rise+1.04),.028,'Teal')
  for k in range(0,n,2):
   yy=y+direction*k*.28;zz=z+(k+1)*rise+.04;g.rod(name+'_POST',(xx,yy,zz),(xx,yy,zz+1),.016,'Teal')

for i,l in enumerate(D['levels']):
 lid=l['id'];z=l['elevation_m'];height=l['storey_height_m'];clear=height-.22
 # Shell refinement: stair entrances moved fully onto 1.11 m bottom landings.
 for d in l['doors']:
  if 'stair_' in d['id'] or 'exit_' in d['id']:d['y']=7.75
  target=next((r for r in l['rooms'] if r['id']==d['b']),None)
  d['swing_sign']=1;d['hinge_side']=1 if 'stair_' in d['id'] else -1;d['opening_degrees']=90;d['hinge_recess_m']=0
  if target:
   tx,ty,txx,tyy=target['rect'];cx,cy=(tx+txx)/2,(ty+tyy)/2
   d['swing_sign']=(1 if cy>d['y'] else -1) if d['orientation']=='H' else (-1 if cx>d['x'] else 1)
   # A door into a long, shallow private hall folds back, not across its walking path.
   if target['kind']=='corridor' and target.get('home') and (txx-tx)>3 and (tyy-ty)<2 and d['orientation']=='H':d['opening_degrees']=160;d['hinge_recess_m']=.13
 lc=g.collection(lid,occupied_level=True,elevation_m=z)
 cs={k:g.collection(lid+'_'+k,lc) for k in ['SLAB','PARTITIONS_LOW','PARTITIONS_HIGH','FACADE','CEILING','STAIRS','LIFT','LIGHTING','SIGNS']}
 with g.scope(cs['SLAB'],origin=(0,0,0),level=lid,role='slab'):
  xs=[0,.3,4.7,11.8,14.2,21.3,25.7,26];ys=[0,7.2,9.74545,12.8,20]
  for a,b in zip(xs,xs[1:]):
   for c,d in zip(ys,ys[1:]):
    opening=((a>=.3 and b<=4.7 or a>=21.3 and b<=25.7) and c>=7.2 and d<=12.8) or (a>=11.8 and b<=14.2 and c>=9.74545 and d<=12.8)
    if i>0 and opening:continue
    g.box(lid+'_STRUCTURAL_SLAB',((a+b)/2,(c+d)/2,z-.11),(b-a,d-c,.22),'Concrete')
  for r in l['rooms']:
   if r['kind'] in ['stair','elevator']:continue
   x,y,xx,yy=r['rect'];mat='Tile' if r['kind']=='bathroom' else 'Oak' if r['home'] else 'Terrazzo'
   with g.scope(role='room_floor',room_id=r['id'],home=r['home'] or '',room_kind=r['kind']):g.box(r['id']+'_FINISH',((x+xx)/2,(y+yy)/2,z+.02),(xx-x,yy-y,.04),mat)
  # Perimeter columns; distinct structural geometry, not approval of engineered sizing.
  for x in [.15,6.5,13,19.5,25.85]:
   for y in [.15,19.85]:
    if y==.15 and x==13:continue
    with g.scope(role='column'):g.box(lid+'_RC_COLUMN',(x,y,z+clear/2),(.32,.32,clear),'Limestone')
 with g.scope(cs['CEILING'],origin=(0,0,0),level=lid,role='ceiling'):
  for r in l['rooms']:
   if r['kind'] in ['stair','elevator']:continue
   x,y,xx,yy=r['rect'];g.box(r['id']+'_CEILING',((x+xx)/2,(y+yy)/2,z+clear-.015),(xx-x,yy-y,.03),'Plaster')
 with g.scope(origin=(0,0,0),level=lid):partitions(l,z,clear,cs['PARTITIONS_LOW'],cs['PARTITIONS_HIGH']);facade(l,z,clear,cs['FACADE'])
 # Solid timber internal doors, frames/handles and stepped skirting.
 with g.scope(cs['PARTITIONS_HIGH'],origin=(0,0,0),level=lid,role='door'):
  for d in l['doors']:
   if d.get('external') or d['id'].endswith('lift_door'):continue
   x,y,w=d['x'],d['y'],d['width'];rz=0 if d['orientation']=='H' else math.pi/2
   with g.scope(origin=(x,y,z),angle=rz,door_id=d['id']):
    # Open into the destination room, not across the private/common hall.
    hs=d['hinge_side'];sg=d['swing_sign'];aa=math.radians(d['opening_degrees']);hx=hs*(w/2-.03);hy=sg*d['hinge_recess_m'];dx=-hs*math.cos(aa);dy=sg*math.sin(aa)
    g.box(d['id']+'_LEAF',(hx+dx*w*.475,hy+dy*w*.475,1.07),(w*.95,.045,2.06),'Oak',.012,rz=math.atan2(dy,dx))
    for q in [-w/2-.045,w/2+.045]:g.box(d['id']+'_JAMB',(q,0,1.09),(.075,.24,2.18),'Walnut',.008)
    g.box(d['id']+'_LINTEL',(0,0,2.22),(w+.16,.24,.08),'Walnut',.008)
    px,py=hx+dx*w*.82,hy+dy*w*.82;nx,ny=-dy,dx
    g.rod(d['id']+'_HANDLE_PIN',(px,py,1.03),(px+nx*.05,py+ny*.05,1.03),.018,'Bronze')
    g.rod(d['id']+'_LEVER',(px+nx*.05,py+ny*.05,1.03),(px+nx*.05-dx*.12,py+ny*.05-dy*.12,1.03),.016,'Bronze')
 with g.scope(cs['STAIRS'],origin=(0,0,0),level=lid,role='stair'):
  for side,x0 in [('A',.3),('B',21.3)]:
   with g.scope(route=side):
    g.box(lid+'_STAIR_'+side+'_LANDING',(x0+2.2,7.755,z-.06),(4.4,1.11,.20),'Concrete')
    if i<5:
     n=11 if i==0 else 10;rise=height/(n*2)
     flight(lid+'_STAIR_'+side+'_UP',x0+.2,8.45,z,n,rise,1)
     end=8.45+(n-1)*.28
     g.box(lid+'_STAIR_'+side+'_MID',(x0+2.2,(end+.14+12.60)/2,z+height/2-.06),(4,12.60-(end+.14),.20),'Concrete')
     flight(lid+'_STAIR_'+side+'_RETURN',x0+2.85,end,z+height/2,n,rise,-1)
     # Landing edge guards, with opening for each arriving flight.
     for xx in [x0+1.6,x0+2.8]:g.rod(lid+'_STAIR_'+side+'_LANDING_GUARD',(xx,8.31,z+.04),(xx,8.31,z+1.09),.022,'Teal')
     g.rod(lid+'_STAIR_'+side+'_LANDING_TOP',(x0+1.6,8.31,z+1.09),(x0+2.8,8.31,z+1.09),.028,'Teal')
    else:
     # At L06 the lower flight terminates: protect its void from the bottom landing.
     g.rod(lid+'_STAIR_'+side+'_TERMINAL_TOP',(x0+.2,8.29,z+1.09),(x0+2.75,8.29,z+1.09),.028,'Teal')
     for k in range(7):
      xx=x0+.2+k*2.55/6
      g.rod(lid+'_STAIR_'+side+'_TERMINAL_POST',(xx,8.29,z+.04),(xx,8.29,z+1.09),.016,'Teal')
    g.sign(lid+'_EXIT_SIGN','EXIT '+side,(x0+.5,7.30,z+.06),.22,'Teal',plane='XY')
 with g.scope(cs['LIFT'],origin=(0,0,0),level=lid,role='lift'):
  for x in [12.0,14.0]:g.rod(lid+'_LIFT_GUIDE',(x,12.45,z),(x,12.45,z+height),.045,'Steel')
  for x in [12.40,13.60]:g.box(lid+'_LIFT_PORTAL',(x,9.72,z+1.18),(.12,.22,2.36),'Steel')
  g.box(lid+'_LIFT_HEADER',(13,9.72,z+2.4),(1.4,.24,.16),'Steel')
  for side in [-1,1]:g.box(lid+'_LIFT_DOOR',(13+side*(.51 if i==0 else .26),9.76,z+1.15),(.5,.045,2.24),'Steel',.008)
  g.box(lid+'_LIFT_CALL',(14,9.60,z+1.15),(.11,.035,.3),'Black',.015);g.cylinder(lid+'_LIFT_BUTTON',(14,9.56,z+1.15),.025,.015,'Glow')
  if i==0:
   g.box('L01_LIFT_CAB_FLOOR',(13,11.1,z+.09),(1.8,2.45,.1),'Terrazzo')
   g.box('L01_LIFT_CAB_BACK',(13,12.3,z+1.3),(1.8,.06,2.4),'Steel')
   for x in [12.10,13.90]:g.box('L01_LIFT_CAB_SIDE',(x,11.1,z+1.3),(.05,2.45,2.4),'Oak')
   g.box('L01_LIFT_CAB_CEILING',(13,11.1,z+2.5),(1.8,2.45,.08),'Glow');g.rod('L01_LIFT_CAB_HANDRAIL',(12.25,12.22,z+.95),(13.75,12.22,z+.95),.03,'Steel')
 with g.scope(cs['SIGNS'],origin=(0,0,0),level=lid,role='wayfinding'):
  g.box(lid+'_FLOOR_PLAQUE',(20.0,7.18,z+1.6),(.9,.04,.4),'Teal',.02);g.sign(lid+'_FLOOR_ID',lid,(19.68,7.15,z+1.48),.21,'Porcelain')
  g.sign(lid+'_FRONT_CUTAWAY_ID',lid,(.7,-.15,z+.20),.28,'Porcelain')
 with g.scope(cs['LIGHTING'],origin=(0,0,0),level=lid,role='light_fixture'):
  for x in [7,10,16,19]:
   g.box(lid+'_CORRIDOR_LUMINAIRE',(x,8.2,z+clear-.10),(.8,.1,.05),'Glow',.02);g.light(lid+'_CORRIDOR_LIGHT',(x,8.2,z+clear-.16),85,1.4)
  for x in [2.5,23.5]:g.light(lid+'_STAIR_LIGHT',(x,10,z+clear-.15),90,1.6)
 g.camera('CAM_'+lid+'_AXON',(38,-35,z+56),(13,10,z),ortho=40)
 g.camera('CAM_'+lid+'_PLAN',(13,10,z+50),(13,10,z),ortho=42)

roof=g.collection('ROOF')
with g.scope(roof,origin=(0,0,0),role='roof'):
 g.box('ROOF_STRUCTURAL_SLAB',(13,10,19.91),(26,20,.22),'Concrete');g.box('ROOF_MEMBRANE',(13,10,20.04),(25.4,19.4,.04),'Limestone')
 for y in [.15,19.85]:g.box('ROOF_PARAPET',(13,y,20.57),(26,.3,1.1),'Limestone');g.box('ROOF_COPING',(13,y,21.08),(26.2,.43,.08),'Terracotta',.02)
 for x in [.15,25.85]:g.box('ROOF_PARAPET',(x,10,20.57),(.3,19.4,1.1),'Limestone');g.box('ROOF_COPING',(x,10,21.08),(.43,19.27,.08),'Terracotta',.02)
 for y in [.15,19.85]:g.box('ROOF_EDGE_BEAM',(13,y,19.69),(26,.30,.22),'Limestone')
 for x in [.15,25.85]:g.box('ROOF_EDGE_BEAM',(x,10,19.69),(.30,19.4,.22),'Limestone')
 # Non-occupiable lift overrun and heat pump enclosure, not an additional floor.
 g.box('LIFT_OVERRUN',(13,11.3,20.5),(2.6,3.5,.9),'Limestone',.05)
 for x in [17,19.5]:
  g.box('ROOF_HEAT_PUMP',(x,14,20.45),(1.7,1,.8),'Steel',.08)
  for j in range(12):g.box('ROOF_LOUVRE',(x,13.48,20.1+j*.06),(1.55,.04,.025),'Teal')
context=g.collection('CONTEXT')
with g.scope(context,origin=(0,0,0),role='context'):
 g.box('CITY_PAVEMENT',(13,10,-.35),(44,38,.4),'Paving',.05);g.box('STREET',(13,-8,-.45),(56,8,.3),'Concrete')
 for x in range(-6,34,2):g.box('PAVING_JOINT',(x,9,-.139),(.02,30,.004),'Walnut')
 for y in range(-4,28,2):g.box('PAVING_JOINT',(13,y,-.138),(40,.02,.004),'Walnut')
 for x in [-3,29]:
  for y in [1,17]:
   g.lathe('STREET_PLANTER',(x,y,-.12),[(.5,0),(.65,.65),(.66,.7),(.58,.72),(.52,.65)],'Terracotta',24);g.cylinder('PLANTER_SOIL',(x,y,.54),.54,.04,'Soil')
   g.rod('TREE_TRUNK',(x,y,.6),(x+.1,y,3),.08,'Walnut')
   for k in range(14):g.sphere('TREE_CANOPY',(x+.8*math.sin(k*2.4),y+.7*math.cos(k*2.4),2.7+.8*math.sin(k)),(1.3,1.1,.8),'Leaf',12,8)
 for x in [4,21]:
  for k in range(5):g.box('STREET_BENCH_SLAT',(x,-3.1+k*.10,.39),(2,.075,.06),'Oak',.015)
  for dx in [-.7,.7]:g.box('STREET_BENCH_LEG',(x+dx,-2.9,.11),(.07,.45,.55),'Teal',.02)
 # Level pedestrian approach to the finished entrance, not an unbridged 150 mm plinth.
 # 185 mm rise over 2.50 m plus 1.80 m level landing; visual accessible intent, not code approval.
 x1,x2,ya,yb=11.8,14.2,-4.0,-1.5
 v=[(x1,ya,-.17),(x2,ya,-.17),(x2,yb,-.17),(x1,yb,-.17),(x1,ya,-.15),(x2,ya,-.15),(x2,yb,.035),(x1,yb,.035)]
 g.obj('ENTRANCE_APPROACH_RAMP',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Limestone')
 g.box('ENTRANCE_LEVEL_LANDING',(13,-.6,-.0575),(2.4,1.8,.185),'Limestone')
 g.box('ENTRANCE_THRESHOLD',(13,.255,.0175),(1.8,.25,.035),'Limestone',.003)
 for x in [11.9,14.1]:
  g.rod('ENTRANCE_APPROACH_HANDRAIL',(x,-4,.75),(x,-1.5,.935),.026,'Teal')
  g.rod('ENTRANCE_LANDING_HANDRAIL',(x,-1.5,.935),(x,-.18,.935),.026,'Teal')
  for y in [-3.8,-2.6,-1.5,-.3]:
   zz=.035+min(0,y+1.5)*.185/2.5
   g.box('ENTRANCE_RAIL_FOOT',(x,y,zz+.01),(.12,.12,.02),'Bronze',.006)
   g.rod('ENTRANCE_RAIL_POST',(x,y,zz+.02),(x,y,zz+.9),.017,'Teal')
 # Front entrance canopy, luminaires and address.
 g.box('ENTRANCE_CANOPY',(13,-.75,3.2),(5,1.8,.18),'Terracotta',.04)
 for x in [11.1,14.9]:g.rod('CANOPY_TIE',(x,-1.4,3.2),(x,.05,3.65),.025,'Bronze')
 g.sign('ENTRANCE_SIGN','CASA DEI COLORI',(10.9,-.16,2.92),.18,'Bronze')
site=g.collection('SITE_LIGHTING')
with g.scope(site,origin=(0,0,0)):
 sun=bpy.data.lights.new('SUN','SUN');sun.energy=2.2;sun.angle=.12;o=bpy.data.objects.new('SUN',sun);site.objects.link(o);o.rotation_euler=(.45,-.5,-.5)
 g.light('SKY_FILL',(13,7,30),1500,22,(.78,.87,1))
g.camera('CAM_EXTERIOR_DAY',(44,-46,29),(13,9,9.8),lens=38)
g.camera('CAM_EXTERIOR_DUSK',(-26,-36,20),(13,9,10),lens=38)
g.camera('CAM_FULL_CUTAWAY',(37,-65,22),(13,8,10),ortho=43)
g.camera('CAM_TECHNICAL',(43,-40,38),(13,10,10),ortho=43)
g.camera('CAM_FACADE_DETAIL',(23,-8,8.5),(17,0,7),lens=45)
s.camera=bpy.data.objects['CAM_EXTERIOR_DAY'];s['shell_window_openings']=len(WINDOWS)
(ROOT/'assets/exterior/window-schedule.json').write_text(json.dumps(WINDOWS,indent=2)+'\n')
(ROOT/'assets/exterior/aligned-programme.json').write_text(json.dumps(D,indent=2)+'\n')
(ROOT/'scene').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene/shell.blend'),compress=True)
print('SHELL_SAVED',len(s.objects),'objects;',len(WINDOWS),'actual facade openings; six levels')
