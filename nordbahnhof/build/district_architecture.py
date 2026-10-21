"""Original street blocks, room reveals and a physically connected station exit."""
import math,random,bpy,bmesh
from mathutils import Vector,Matrix

def window(d,p,x,z,w=1.8,h=2.0,shutters=False,balcony=False,lit=False):
 d.box('window room back',(x,-1.8,z),(w+.3,.10,h+.4),p['darkwood'])
 d.box('window room floor',(x,-.9,z-h/2),(w+.4,1.8,.08),p['wood'])
 d.box('window glass',(x,-.065,z),(w,.008,h),p['glass'])
 for xx in (x-w/2-.055,x+w/2+.055):d.box('window outer jamb',(xx,.075,z),(.11,.15,h+.2),p['stone'])
 for zz in (z-h/2-.055,z+h/2+.055):d.box('window header sill',(x,.075,zz),(w+.3,.22,.11),p['stone'])
 for xx in (x-w/2+.04,x,x+w/2-.04):d.box('sash vertical',(xx,-.01,z),(.045,.065,h),p['cream'])
 for zz in (z-h/2+.04,z+h/2-.04,z+.28):d.box('sash horizontal',(x,-.005,zz),(w,.07,.045),p['cream'])
 # Folded curtains are real wavy cloth surfaces, not an opaque image pasted over glass.
 for side in (-1,1):
  vv=[]
  for j in range(3):
   for i in range(5):
    xx=x+side*w*.39+(i/4-.5)*w*.20;yy=-.18+.022*math.cos(i*math.pi);zz=z-h/2+j*h/2;vv.append((xx,yy,zz))
  d.mesh('folded linen curtain',vv,[(j*5+i,j*5+i+1,(j+1)*5+i+1,(j+1)*5+i) for j in range(2) for i in range(4)],p['linen'],True)
 if lit:
  d.box('lit room shade',(x,-1.63,z+.5),(.65,.03,.28),p['lamp']);d.box('room table',(x,-.85,z-.65),(.65,.55,.06),p['wood']);d.box('room chair back',(x+.4,-1.1,z-.55),(.35,.05,.65),p['wood'])
 if shutters:
  for side in (-1,1):
   xx=x+side*(w*.76)
   d.box('hinged shutter stile',(xx,.08,z),(w*.43,.07,h),p['green'])
   for j in range(12):d.box('shutter louvre',(xx,.13,z-h*.45+j*h*.08),(w*.36,.035,.043),p['darkwood'])
 if balcony:
  d.box('stone balcony slab',(x,.55,z-h/2-.16),(w+.75,1.18,.18),p['stone'])
  for xx in (x-w*.65,x+w*.65):d.box('balcony corbel',(xx,.18,z-h/2-.38),(.18,.43,.38),p['stone'])
  for j in range(13):d.cyl('balcony iron spindle',(x-(w+.6)/2+j*(w+.6)/12,1.02,z-h/2+.38),.013,.95,p['iron'],N=6)
  d.beam('balcony top rail',(x-(w+.65)/2,1.02,z-h/2+.86),(x+(w+.65)/2,1.02,z-h/2+.86),.042,p['iron'])
  for side in (-1,1):
   for j in range(5):d.cyl('balcony return spindle',(x+side*(w+.6)/2,.15+j*.22,z-h/2+.38),.013,.95,p['iron'],N=6)

def shop(d,p,x,w,name,index):
 # The front is genuinely open between piers. Displays occupy a 3D room behind glazing.
 d.box('shop parquet',(x,-2,.30),(w,4,.10),p['wood']);d.box('shop back wall',(x,-3.9,1.9),(w,.15,3.4),p['darkwood'])
 for side in (-1,1):d.box('shop party wall',(x+side*w/2,-2,1.9),(.18,4,3.4),p['stone'])
 d.box('shop fascia',(x,.19,3.66),(w-.16,.24,.53),p[['green','red','blue'][index%3]])
 d.text('shop name',name,(x,.323,3.51),min(.32,w/max(len(name),1)*1.28),p['cream'])
 for xx in (x-w/2+.12,x+w/2-.12):d.box('shop pilaster',(xx,.08,1.72),(.2,.27,3.2),p['stone'])
 door=x-w*.31
 for xx in (door-.43,door+.43):d.box('door frame',(xx,.11,1.55),(.07,.11,2.8),p['darkwood'])
 d.box('door glass',(door,.07,1.8),(.78,.012,2.1),p['glass']);d.box('door kick panel',(door,.1,.49),(.78,.045,.65),p['wood']);d.cyl('door brass handle',(door+.27,.16,1.36),.018,.26,p['bronze'])
 wx=x+w*.15;ww=w*.58
 d.box('shop window',(wx,.045,1.8),(ww,.012,2.4),p['glass'])
 for zz in (.57,3.03):d.box('shop window rail',(wx,.13,zz),(ww+.1,.12,.1),p['wood'])
 for xx in (wx-ww/2,wx+ww/2):d.box('shop mullion',(xx,.13,1.8),(.07,.11,2.55),p['wood'])
 for level in range(3):
  zz=.79+level*.56;d.box('display shelf',(wx,-.45,zz),(ww-.14,.65,.05),p['wood'])
  for k in range(max(2,int(ww/.22))):
   xx=wx-ww*.44+k*.22
   if any(s in name for s in ('BÜCHER','POST','REISE')):d.box('book spine',(xx,-.39,zz+.18),(.075,.21,.34),p[['red','green','cream'][k%3]])
   elif any(s in name for s in ('APOTHEKE','WEIN','KOLONIAL')):
    d.cyl('apothecary bottle',(xx,-.38,zz+.13),.055,.22,p['green'],N=8);d.cyl('bottle stopper',(xx,-.38,zz+.27),.022,.06,p['bronze'],N=8)
   elif any(s in name for s in ('BÄCKEREI','CAFE','FEINKOST')):d.sphere('loaf in shop',(xx,-.39,zz+.08),(.13,.075,.065),p['cream'],N=8,M=4)
   elif 'SCHNEIDER' in name:d.cyl('tailor textile bolt',(xx,-.38,zz+.08),.07,.33,p[['red','blue','cream'][k%3]],'Y',N=10)
   elif 'UHREN' in name:
    d.cyl('clockmaker brass case',(xx,-.38,zz+.16),.09,.06,p['bronze'],'Y',N=16);d.cyl('clockmaker ivory dial',(xx,-.345,zz+.16),.075,.008,p['cream'],'Y',N=16);d.beam('display clock hand',(xx,-.335,zz+.16),(xx+.04,-.335,zz+.20),.007,p['black'])
   elif 'OBST' in name:d.sphere('greengrocer produce',(xx,-.38,zz+.07),(.075,.07,.07),p['fruitgold'] if k%2 else p['fruitred'],N=8,M=5)
   elif 'EISEN' in name:
    d.box('ironmonger tool handle',(xx,-.38,zz+.15),(.025,.04,.27),p['wood']);d.box('ironmonger hammer head',(xx,-.38,zz+.29),(.14,.06,.05),p['iron'])
   else:d.cyl('display flower pot',(xx,-.38,zz+.07),.06,.14,p['red']);d.sphere('flower leaves',(xx,-.38,zz+.23),(.1,.1,.14),p['leaf'],N=8,M=4)
 d.box('warm shop ceiling panel',(x,-2.0,3.35),(w*.55,.8,.025),p['lamp'])
 # Projecting awning, iron stays and a scalloped fabric valance.
 if index%3!=2:
  for k in range(12):
   xx=x-w/2+(k+.5)*w/12;ma=p['linen'] if k%2 else p[['red','green','blue'][index%3]]
   d.mesh('striped canvas awning',[(xx-w/24,.20,3.28),(xx+w/24,.20,3.28),(xx+w/24,1.72,2.98),(xx-w/24,1.72,2.98)],[(0,1,2,3)],ma)
   d.box('awning hanging valance',(xx,1.72,2.87),(w/12,.025,.22),ma)
  for side in (-1,1):d.beam('awning iron stay',(x+side*w*.46,.15,2.24),(x+side*w*.46,1.72,2.97),.025,p['iron'])
 d.text('shop street number',str(12+index),(x-w*.43,.26,3.27),.14,p['black'])

def building(d,p,index,x,y,width,depth,floors,rotation=0):
 d.zone=f'B{index:03d}';d.location(x,y,.18,rotation);rng=random.Random(2800+index);wall=p['plaster'][index%len(p['plaster'])];bay=width/max(3,round(width/3.2));cols=round(width/bay);height=4.2+floors*3.25
 # Side/back walls have real thickness; front windows are actual voids between spandrels.
 saved=d.transform.copy()
 for side in (-1,1):
  from mathutils import Matrix
  d.transform=saved@Matrix.Translation((side*width/2,-depth/2,0))@Matrix.Rotation(-side*math.pi/2,4,'Z')
  sw=depth;wb=1.35
  if (index%14==0 and side==1) or (index%14==7 and side==-1):
   for k in range(3):shop(d,p,-sw/2+(k+.5)*sw/3,sw/3,['CAFE EUROPA','FEINKOST','REISEARTIKEL'][k],index+k)
  else:d.box('side elevation ground wall',(0,-.16,2.0),(sw,.32,4.0),wall)
  for level in range(floors):
   base=4.2+level*3.25;zc=base+1.84
   d.box('side elevation sill wall',(0,-.16,base+.36),(sw,.32,.72),wall);d.box('side elevation head wall',(0,-.16,base+3.03),(sw,.32,.43),wall)
   for a,b in [(-sw/2,-sw*.25-wb/2),(-sw*.25+wb/2,sw*.25-wb/2),(sw*.25+wb/2,sw/2)]:d.box('side elevation wall pier',((a+b)/2,-.16,zc),(b-a,.32,2.25),wall)
   for xx in (-sw*.25,sw*.25):window(d,p,xx,zc,wb,2.07,False,False,False)
  d.text('painted gable advertisement',['KAFFEE  ·  CACAO','HOTEL  EUROPA','REISEBÜRO  ADLER'][index%3],(0,.02,height+1.1),.35,p['mortar'])
 d.transform=saved
 d.box('rear party wall',(0,-depth,height/2),(width,.3,height),wall)
 d.box('ground plinth',(0,.10,.34),(width,.4,.68),p['stone'])
 for j in range(floors+1):
  z=4.2+j*3.25
  d.box('floor plate',(0,-depth/2,z-.10),(width,depth,.20),p['wood'])
  d.box('string course',(0,.13,z),(width+.20,.3,.17),p['stone'])
  if j==floors:break
  d.box('front sill spandrel',(0,-.15,z+.36),(width,.3,.72),wall);d.box('front window head spandrel',(0,-.15,z+3.03),(width,.3,.43),wall)
  for k in range(cols+1):d.box('front masonry pier',(-width/2+k*bay,-.15,z+1.85),(.52,.30,2.25),wall)
  for k in range(cols):
   xx=-width/2+(k+.5)*bay;window(d,p,xx,z+1.84,bay-.68,2.07,index%4==1 and j<2,index%3==0 and j==0,rng.random()<.22)
 # Cornice is built up, not a single floating slab.
 for step,(extra,z,h) in enumerate([(.15,height+.08,.18),(.34,height+.23,.14),(.52,height+.36,.12)]):d.box('layered eaves cornice',(0,.02,z),(width+extra,.62,h),p['stone'])
 for k in range(int(width/.35)):d.box('cornice dentil',(-width/2+.18+k*.35,.27,height-.12),(.14,.28,.19),p['stone'])
 # Pitched roof with ridge, verge boards, dormers and separate chimney pots.
 ridge=height+3.7;vv=[(-width/2-.3,.42,height+.46),(width/2+.3,.42,height+.46),(width/2+.3,-depth/2,ridge),(-width/2-.3,-depth/2,ridge),(-width/2-.3,-depth-.3,height+.46),(width/2+.3,-depth-.3,height+.46)]
 d.mesh('slate pitched roof',vv,[(0,1,2,3),(3,2,5,4)],p['roof'])
 for side in (-1,1):d.mesh('gable masonry',[(side*width/2,.02,height),(side*width/2,-depth,height),(side*width/2,-depth/2,ridge)],[(0,1,2)],wall)
 d.beam('ridge flashing',(-width/2-.35,-depth/2,ridge+.025),(width/2+.35,-depth/2,ridge+.025),.08,p['iron'])
 d.cyl('eaves gutter',(0,.40,height+.43),.065,width+.7,p['iron'],'X',N=10)
 for side in (-1,1):
  xx=side*(width/2-.16);d.cyl('rainwater downpipe',(xx,.31,height/2),.044,height,p['iron'],N=10)
  for z in range(2,int(height),3):d.ring('downpipe retaining collar',(xx,.31,z),.054,.009,p['iron'],N=12,M=4)
 for j in range(2):
  xx=(-.26 if j==0 else .28)*width;d.box('chimney brick shaft',(xx,-depth*.64,ridge-.1),(1.0,.72,2.8),p['stone']);d.box('chimney cap',(xx,-depth*.64,ridge+1.36),(1.15,.89,.15),p['stone'])
  for dx in (-.25,.25):d.cyl('terracotta chimney pot',(xx+dx,-depth*.64,ridge+1.67),.13,.55,p['red'],N=12);d.ring('chimney pot lip',(xx+dx,-depth*.64,ridge+1.95),.145,.018,p['red'],N=16,M=4)
 for k in range(max(1,cols//2)):
  xx=-width*.35+k*width*.7/max(1,cols//2-1);zz=height+1.12
  d.box('dormer cheek',(xx,-1.8,zz),(1.65,1.6,1.5),wall);d.box('dormer glazing',(xx,-.98,zz),(1.15,.01,1.05),p['glass'])
  for dx in (-.63,0,.63):d.box('dormer frame',(xx+dx,-.94,zz),(.07,.09,1.2),p['cream'])
  d.mesh('dormer cap',[(xx-.95,-.85,zz+.76),(xx,-.85,zz+1.35),(xx+.95,-.85,zz+.76),(xx-.95,-2.9,zz+.76),(xx,-2.9,zz+1.35),(xx+.95,-2.9,zz+.76)],[(0,3,4,1),(1,4,5,2)],p['roof'])
 names=['BÜCHER & KARTEN','APOTHEKE','BÄCKEREI ADLER','BLUMENHAUS','CAFE MORGENROT','KOLONIALWAREN','UHREN & OPTIK','SCHNEIDEREI','POST & TELEGRAPH','OBST & GEMÜSE','EISENWAREN','WEINSTUBE']
 nshop=max(2,int(width/5.5));sw=width/nshop
 for k in range(nshop):shop(d,p,-width/2+(k+.5)*sw,sw,names[(index+k)%len(names)],index+k)
 d.records.append({'id':index,'origin':[x,y],'width':width,'depth':depth,'upper_floors':floors,'rotation':rotation,'shop_count':nshop,'type':'original masonry street building with open front reveals and shallow furnished window rooms'})

def cut_exit():
 for ob in list(bpy.data.objects):
  if ob.name.startswith(('RET_','WAIT_')):
   bpy.data.objects.remove(ob,do_unlink=True);continue
  if ob.name.startswith('BARRIER_') and ob.type=='MESH':
   pts=[ob.matrix_world@Vector(q) for q in ob.bound_box];cx=sum(v.x for v in pts)/8;cy=sum(v.y for v in pts)/8
   if 0<cx<23 and 33<cy<39:bpy.data.objects.remove(ob,do_unlink=True)
 # Cut the actual facade, not an opaque door picture. World-space exact split planes.
 for ob in bpy.data.objects:
  if ob.type!='MESH' or not ob.name.startswith('STATIC_BATCH_'):continue
  if not any(s in ob.name for s in ('limestone','recess','glazing','brick','painted petrol iron')):continue
  x0,x1,y0,y1,z1=(2,34,31,38.35,3.6) if 'painted petrol iron' in ob.name else (2,19,31,36,4.5)
  me=ob.data;bm=bmesh.new();bm.from_mesh(me)
  for v in bm.verts:v.co=ob.matrix_world@v.co
  for axis,val in [(0,x0),(0,x1),(1,y0),(1,y1),(2,z1)]:
   f=[f for f in bm.faces if min(v.co.y for v in f.verts)<=y1 and max(v.co.y for v in f.verts)>=y0 and min(v.co.z for v in f.verts)<z1]
   geom=set(f)
   for q in f:geom.update(q.edges);geom.update(q.verts)
   if geom:bmesh.ops.bisect_plane(bm,geom=list(geom),plane_co=Vector(tuple(val if i==axis else 0 for i in range(3))),plane_no=Vector(tuple(1 if i==axis else 0 for i in range(3))),dist=.00001)
  dead=[f for f in bm.faces if x0+.001<f.calc_center_median().x<x1-.001 and y0<f.calc_center_median().y<y1 and f.calc_center_median().z<z1-.001]
  bmesh.ops.delete(bm,geom=dead,context='FACES');bm.to_mesh(me);bm.free();ob.matrix_world=Matrix.Identity(4)

def exit_canopy(d,p):
 d.zone='EXIT';d.location();cut_exit()
 # Raised exit threshold at0.76m; an interior ramp connects back to the original level0concourse.
 d.box('exit landing masonry foundation',(10.5,30.2,.36),(18.0,7.6,.36),p['stone'])
 d.box('exit vestibule landing',(10.5,30.2,.65),(18.0,7.6,.22),p['paving'])
 d.box('interior raised floor foundation',(10.5,36,.27),(17.8,5,.54),p['stone'])
 # The first retained railway rake is atY40. The new concourse route stays entirely south ofY38.5.
 d.box('raised concourse exit route',(10.5,36,.65),(17.8,5,.22),p['paving'])
 d.mesh('interior concourse connection ramp',[(19.4,34,.76),(19.4,38.3,.76),(33.4,38.3,.015),(33.4,34,.015)],[(0,1,2,3)],p['paving'])
 d.mesh('interior ramp masonry foundation',[(19.4,34,.76),(19.4,38.3,.76),(33.4,38.3,.015),(33.4,34,.015),(19.4,34,0),(19.4,38.3,0),(33.4,38.3,0),(33.4,34,0)],[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0),(4,7,6,5)],p['stone'])
 for yy in(34,38.3):
  for xx in(19.4,22.9,26.4,29.9,33.4):
   zz=.76-(xx-19.4)*.745/14;d.cyl('interior ramp baluster',(xx,yy,zz+.48),.022,.96,p['iron'])
  d.beam('interior ramp handrail',(19.4,yy,1.72),(33.4,yy,.975),.045,p['iron'])
 d.box('exit hall rear wall',(17.5,38.55,2.625),(32,.20,5.25),p['plaster'][2])
 d.box('exit hall oak dado',(17.5,38.435,.68),(32,.03,1.36),p['wood'])
 d.box('exit hall west wall',(1.48,36,2.625),(.24,5.2,5.25),p['plaster'][2])
 d.box('exit hall coffered ceiling',(17.5,36,5.25),(32,5.2,.22),p['cream'])
 for xx in(2,6,10,14,18,22,26,30,33):
  d.box('hall rear stone pilaster',(xx,38.39,2.625),(.28,.22,5.25),p['stone'])
  d.box('hall ceiling beam',(xx,36,5.08),(.18,5.2,.24),p['wood'])
 for xx in(5,11,17,23,29):
  d.cyl('hall pendant stem',(xx,36,4.52),.025,1.0,p['bronze'])
  d.sphere('hall opal pendant',(xx,36,3.96),(.22,.22,.20),p['lamp'])
 for xx in(4.3,15.3):
  d.box('hall bench seat',(xx,38.03,1.21),(2.5,.66,.09),p['wood'])
  d.box('hall bench back',(xx,38.35,1.57),(2.5,.06,.68),p['wood'])
  for dx in(-.9,.9):d.box('hall bench foot',(xx+dx,38.05,.98),(.065,.40,.45),p['iron'])
 d.box('hall wayfinding board',(11,38.36,2.9),(10,.08,.50),p['green'])
 d.text('concourse wayfinding','ZU DEN ZÜGEN  ·  GLEIS 1–12  →',(11,38.30,2.75),.28,p['cream'],(math.pi/2,0,0))
 for j in range(4):d.box('exit stair',(10.5,23.75+j*.76,.18+(j+1)*.145/2),(15.8,.77,(j+1)*.145),p['stone'])
 d.mesh('accessible side ramp',[(.2,17,.18),(3.4,17,.18),(3.4,31,.76),(.2,31,.76)],[(0,1,2,3)],p['paving'])
 d.mesh('exterior ramp masonry foundation',[(.2,17,.18),(3.4,17,.18),(3.4,31,.76),(.2,31,.76),(3.4,31,.18),(.2,31,.18)],[(1,4,2),(3,2,4,5),(0,3,5),(0,5,4,1)],p['stone'])
 for side in (0.15,3.45):
  for y in (18,22,26,30):
   z=.18+(y-17)*.58/14;d.cyl('ramp rail upright',(side,y,z+.47),.022,.94,p['iron'])
  d.beam('ramp handrail',(side,17,1.12),(side,31,1.70),.045,p['iron'])
 for xx in (2.15,18.85):
  d.box('exit jamb',(xx,33.25,2.55),(.36,.7,4.4),p['stone'])
  for y in (24,30.7):
   d.cyl('canopy column',(xx,y,2.77),.095,4.05,p['iron'],N=16);d.cyl('canopy column plinth',(xx,y,.91),.19,.33,p['iron'],N=12)
   for k in range(6):a=k*math.tau/6;d.cyl('canopy holding bolt',(xx+.145*math.cos(a),y+.145*math.sin(a),.78),.016,.035,p['rail'],N=6)
 d.box('exit letter board',(10.5,32.85,4.42),(16.9,.18,.50),p['green']);d.text('exit lettering','AUSGANG  ·  BAHNHOFPLATZ',(10.5,32.74,4.27),.32,p['cream'],(math.pi/2,0,0))
 for y in (23.3,26.3,29.3,32.5):
  for i in range(24):
   a=i*math.pi/24;b=(i+1)*math.pi/24
   P=(10.5+8.6*math.cos(a),y,4.8+1.25*math.sin(a));Q=(10.5+8.6*math.cos(b),y,4.8+1.25*math.sin(b));d.beam('curved canopy rib',P,Q,.065,p['iron'])
 for k in range(25):
  a=k*math.pi/24;x=10.5+8.6*math.cos(a);z=4.8+1.25*math.sin(a);d.beam('canopy longitudinal glazing bar',(x,23.3,z),(x,32.5,z),.028,p['iron'])
 for i in range(24):
  for j in range(3):
   a=i*math.pi/24;b=(i+1)*math.pi/24;y=23.3+j*3.06
   vv=[(10.5+8.6*math.cos(t),yy,4.81+1.25*math.sin(t)) for t,yy in [(a,y),(b,y),(b,y+3.04),(a,y+3.04)]];d.mesh('canopy glass pane',vv,[(0,1,2,3)],p['glass'])
 for xx in (5.7,10.5,15.3):
  for side in (-1,1):
   # Door leaves opened outward, with genuinely clear passage between them.
   hinge=(xx+side*1.55,32.8,.76);a=side*1.2
   for z in (1.05,3.50):d.beam('open door rail',(hinge[0],hinge[1],z),(hinge[0]-side*1.55*math.cos(a),hinge[1]-1.55*math.sin(abs(a)),z),.075,p['wood'])
   P=(hinge[0]-side*.77*math.cos(a),hinge[1]-.77*math.sin(abs(a)),2.25)
   d.box('open glass door',P,(1.52,.012,2.40),p['glass'],a)
   for end in (0,1.55):
    q=(hinge[0]-side*end*math.cos(a),hinge[1]-end*math.sin(abs(a)),2.25);d.box('open door stile',q,(.075,.075,2.58),p['wood'])
 for y in (27.5,31):d.text('exit floor direction','BAHNHOFPLATZ  →',(10.5,y,.772),.28,p['cream'],(0,0,0))
 # A new original civic entrance composition gives the exit an architectural address.
 for xx in (-1.4,22.4):
  d.box('entrance rusticated pier',(xx,32.05,7.5),(1.15,1.3,13.5),p['stone'])
  for z in range(1,15):d.box('pier rustication reveal',(xx,31.38,z),(1.16,.035,.035),p['mortar'])
  d.box('pier base',(xx,31.93,1.01),(1.6,1.6,.5),p['stone']);d.box('pier capital',(xx,31.93,14.24),(1.8,1.65,.45),p['stone'])
 for xx in (-.3,21.3):
  d.cyl('entrance engaged column',(xx,31.62,7.6),.29,12.6,p['stone'],N=24)
  for z in (1.15,1.32,13.8,14.02):d.cyl('column classical moulding',(xx,31.62,z),.41,.13,p['stone'],N=24)
 d.box('central clock tympanum',(10.5,32.1,11.7),(20.6,.75,5.0),p['stone'])
 d.box('entrance name frieze',(10.5,31.85,8.5),(23.7,1.0,.88),p['stone']);d.text('station civic title','NORDBAHNHOF',(10.5,31.32,8.18),.75,p['bronze'],(math.pi/2,0,0))
 for z,wx,dep in [(14.45,25.5,1.5),(14.72,26.0,1.7),(15.0,26.5,1.9)]:d.box('entrance entablature',(10.5,32.0,z),(wx,dep,.24),p['stone'])
 for xx in range(-2,24):d.box('entrance cornice dentil',(xx,31.26,14.13),(.17,.30,.25),p['stone'])
 d.mesh('entrance triangular pediment',[(-2.9,31.65,15.12),(23.9,31.65,15.12),(10.5,31.65,19.0)],[(0,1,2)],p['stone'])
 d.beam('pediment sloping cornice',(-3.1,31.57,15.2),(10.5,31.57,19.12),.27,p['stone']);d.beam('pediment sloping cornice',(10.5,31.57,19.12),(24.1,31.57,15.2),.27,p['stone'])
 d.text('entrance foundation date','MDCCCLXXXVIII',(10.5,31.54,16.0),.36,p['bronze'],(math.pi/2,0,0))
 d.cyl('station clock ivory dial',(10.5,31.64,11.65),1.67,.07,p['cream'],'Y',N=96);d.ring('station clock bronze bezel',(10.5,31.56,11.65),1.72,.085,p['bronze'],'Y',N=96,M=8)
 roman=['XII','I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
 for j in range(60):
  a=j*math.tau/60;r=1.48;length=.15 if j%5==0 else .07
  d.beam('clock minute tick',(10.5+r*math.sin(a),31.55,11.65+r*math.cos(a)),(10.5+(r-length)*math.sin(a),31.55,11.65+(r-length)*math.cos(a)),.018,p['black'])
 for j,label in enumerate(roman):
  a=j*math.tau/12;d.text('Roman clock numeral',label,(10.5+1.15*math.sin(a),31.53,11.54+1.15*math.cos(a)),.22,p['black'],(math.pi/2,0,0))
 for a,length,w in [(math.radians(47),1.0,.065),(math.radians(-78),.70,.09)]:d.beam('station clock hand',(10.5,31.49,11.65),(10.5+length*math.sin(a),31.49,11.65+length*math.cos(a)),w,p['black'])
 d.sphere('clock pivot',(10.5,31.45,11.65),(.095,.06,.095),p['bronze'])

def streets(d,p):
 d.zone='GROUND';d.location();d.box('district subgrade',(0,-80,-.25),(410,315,.4),p['soil']);d.box('station forecourt',(0,-2,.08),(174,75,.20),p['paving'])
 for yy in (-54,-110,-164):d.box('cobbled boulevard',(0,yy,.005),(370,18,.20),p['cobble'])
 for x in (10,-170,170):d.box('cobbled cross street',(x,-100,.01),(15,210,.20),p['cobble'])
 for yy in (-42.8,-65.2,-98.8,-121.2,-152.8,-175.2):
  d.box('street sidewalk',(0,yy,.12),(355,4.4,.22),p['paving'])
  for k in range(178):d.box('kerb stone',(-177.5+k*2,yy+(2.1 if yy in (-65.2,-121.2,-175.2) else -2.1),.16),(1.987,.26,.30),p['stone'])
 # Continuous north-south walking routes with real kerbs, interrupted at cross streets.
 for xx in (-1.1,21.1):
  for yy,length in [(-190,30),(-137,32),(-83,32)]:
   d.box('cross avenue sidewalk',(xx,yy,.12),(7.0,length,.22),p['paving'])
   edge=2.42 if xx<10 else 17.58
   for k in range(int(length/2)):d.box('cross avenue kerbstone',(edge,yy-length/2+1+k*2,.16),(.26,1.98,.30),p['stone'])
 # Hero granite setts: modest irregularity, not a perfectly flat bitmap foreground.
 rng=random.Random(171)
 for i in range(180):
  for j in range(18):
   x=-45+i*.32+(j%2)*.16;y=-52.7+j*.27
   if abs(y+52)<.09 or abs(y+57)<.09:continue
   d.box('individual foreground sett',(x,y,.105+rng.uniform(-.002,.002)),(.306,.255,.085),p['stone'])
 # Actual flanged tram rails: the running surfaces follow 1435mm track gauge.
 for track in (-52,-57):
  for side in (-1,1):
   y=track+side*.755;d.box('tram rail head',(0,y,.126),(365,.075,.022),p['rail']);d.box('tram rail groove',(0,y-side*.054,.115),(365,.031,.025),p['black'])
 for y in (-52,-57):d.beam('tram contact wire',(-182,y,5.65),(182,y,5.65),.011,p['bronze'])
 for x in range(-170,180,22):
  d.cyl('tram support mast',(x,-61.5,3.0),.065,6,p['iron']);d.beam('tram wire crossarm',(x,-61.5,5.9),(x,-50,5.9),.06,p['iron'])
 for x in range(-70,90,18):d.box('plaza drainage channel',(x,17,.174),(1.8,.22,.025),p['iron'])

def blocks(d,p):
 idx=0
 for y,rot in [(-67,0),(-101,math.pi),(-121,0),(-155,math.pi),(-175,0)]:
  for side in (-1,1):
   for k in range(7):
    x=(-15-k*22) if side<0 else (36+k*22);w=19.5+(idx%3)*.6;depth=16 if y in(-101,-155) else 18
    building(d,p,idx,x,y,w,depth,3+idx%3,rot);idx+=1
 # The square has framed edges, not a station floating in an empty plane.
 for side in (-1,1):
  for yy in (-22,1,24):building(d,p,idx,side*89,yy,20,16,3+idx%2,side*math.pi/2);idx+=1
 d.zone='PUBLIC';d.location()
