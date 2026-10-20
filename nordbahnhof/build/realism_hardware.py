"""Small, inspectable fabrication details on the photographed locomotive.
Imported by realism_scene before joining. Millimetres, not ornamental lumps.
"""
def add(ns):
 import math,random,bpy
 from mathutils import Vector
 box,cyl,ball,beam,meshobj=(ns[k] for k in ('box','cyl','ball','beam','meshobj'))
 black,steel,red,under,brass=(ns[k] for k in ('black','steel','red','under','brass'))
 painted=ns['painted'];random.seed(11279)
 rust=painted('REAL oxide around non-working fasteners',(.12,.053,.024),rough=.83)
 # Hexagonal heads with washers; never rusty on their polished bearing faces.
 for x in (-50.62,-48.62,-46.62,-44.62,-42.62):
  for side in (-1,1):
   y=93+side*.873
   box('boiler band clamp',(x,y,2.58),(.09,.075,.11),under,.003)
   cyl('band clamp washer',(x,y+side*.043,2.58),.026,.008,rust,'Y',20)
   cyl('band clamp hex nut',(x,y+side*.052,2.58),.020,.018,steel,'Y',6)
 # Front door has a ring of small countersunk fixings and two actual hinges.
 for j in range(36):
  a=2*math.pi*j/36;yy=93+.825*math.sin(a);zz=2.65+.825*math.cos(a)
  cyl('smokebox seam rivet',(-52.922,yy,zz),.010,.012,under,'X',12)
 for z in (2.32,2.98):
  box('door hinge ear',(-53.018,92.37,z),(.08,.11,.11),black,.008)
  cyl('door hinge pivot',(-53.018,92.35,z),.025,.17,steel,'Z',20)
 # Smoke deflector's pressed hems, restrained exposed fasteners, access covers.
 for side in (-1,1):
  y=93+side*1.14
  for x in (-53.28,-50.50):
   for z in (1.86,2.28,2.70,3.12):
    cyl('deflector fixing washer',(x,y+side*.008,z),.023,.008,under,'Y',16)
    cyl('deflector hex fixing',(x,y+side*.018,z),.015,.015,steel,'Y',6)
  for x in (-52.8,-51.8,-50.8):beam('deflector mounting stay',(x,93+side*.84,2.0),(x,y,2.04),.025,.03,under)
  # Polished running gear is made from bored eyes and pins, not fused cubes.
  for x,z in [(-48.34,.84),(-46.09,.84),(-43.84,.84)]:
   cyl('rod boss',(x,93+side*1.13,z),.111,.045,steel,'Y',32)
   cyl('rod oil seal',(x,93+side*1.162,z),.078,.012,under,'Y',32)
   cyl('rod retaining nut',(x,93+side*1.18,z),.054,.031,steel,'Y',6)
   cyl('rod oil nipple',(x,93+side*1.135,z+.117),.015,.036,brass,'Z',12)
  for x in (-51.5,-51.08,-50.72):
   beam('cylinder cover rib',(x,93+side*1.28,.72),(x,93+side*1.28,1.08),.025,.025,under)
  # Tread plate in place of a featureless sheet: compact raised diamonds, not a texture.
  for i in range(15):
   for j in range(3):
    ob=box('cab step anti-slip lozenge',(-40.27+i*.046,93+side*(1.42+j*.06),.926),(.035,.009,.004),under,.001)
    ob.rotation_euler.z=math.pi/4
  # Deck edge paint chips confined to the mechanically exposed lip.
  for k in range(65):
   x=-53.65+k*.232;y=93+side*1.367;z=1.58+random.uniform(-.035,.035)
   if random.random()<.35:continue
   ob=box('small lip paint loss',(x,y,z),(random.uniform(.013,.043),.002,random.uniform(.003,.008)),rust,.001);ob.rotation_euler.y=random.uniform(-.3,.3)
 # Brake/vacuum hoses: actual flexible swept sections and metal end fittings.
 from mathutils import Matrix
 for yy in (92.62,93.38):
  vs=[];fs=[];N=22;M=10
  for i in range(N):
   t=i/(N-1);x=-54.13-.24*math.sin(t*math.pi);z=.98-.56*t;y=yy+.08*math.sin(t*3.14)
   for j in range(M):
    a=j*math.tau/M;rr=.028*(1+.12*math.cos(i*math.pi));vs.append((x+rr*math.cos(a),y+rr*math.sin(a),z))
  for i in range(N-1):
   for j in range(M):q=i*M+j;fs.append((q,i*M+(j+1)%M,(i+1)*M+(j+1)%M,q+M))
  me=bpy.data.meshes.new('vacuum hose swept rubber');me.from_pydata(vs,[],fs)
  for p in me.polygons:p.use_smooth=True
  meshobj('front hanging brake hose',me,mat=under)
  cyl('hose coupling',(-54.13,yy+.08*math.sin(3.14),.415),.043,.055,steel,'Z',12)
 # Realistic litter is sparse and situated, not scattered evenly like confetti.
 paper=painted('REAL damp timetable paper',(.38,.34,.23),rough=.94)
 for i,(x,y) in enumerate([(-57.9,95.7),(-46.1,98.7),(-43.6,96.1)]):
  vs=[(x-.08,y-.05,.764),(x+.07,y-.04,.766),(x+.08,y+.055,.779),(x-.06,y+.06,.767)]
  me=bpy.data.meshes.new('curled paper corner');me.from_pydata(vs,[],[(0,1,2,3)]);meshobj('discarded paper',me,mat=paper)
 # Platform drain with real slots, seated flush, not a black decal.
 for x in (-58.0,-47.5):
  box('drain recess',(x,94.93,.739),(.47,.27,.025),under,.003)
  for k in range(13):box('drain grate bar',(x-.225+k*.0375,94.93,.751),(.018,.25,.014),steel,.002)
 # Double-sided enamel signs: the camera must not see an unlettered white back.
 text=ns['text'];ink=painted('REAL dark blue sign lettering',(.008,.021,.032),rough=.30)
 for xx in (-52,0,52):
  for yy,label in [(96,'7'),(84,'6'),(72,'5')]:
   text('reverse platform numeral','GLEIS  '+label,(xx,yy+.078,4.23),.38,ink,(math.pi/2,0,math.pi))
 # Welting, a stitched lid seam, handles and corner guards on both faces of each case.
 for ob in list(bpy.data.objects):
  if ob.name.startswith('REAL_travel case'):ob.rotation_euler.z=0
 leather=ns['leather']
 for x,y in [(-45.5,97.1),(-44.65,97.25)]:
  for side in (-1,1):
   yy=y+side*.119
   for dx in (-.18,.18):box('case rear strap',(x+dx,yy,1.08),(.034,.010,.60),under,.002)
   for z in (.795,1.365):beam('case stitched horizontal welting',(x-.28,yy,z),(x+.28,yy,z),.006,.006,leather)
   for dx in (-.286,.286):beam('case stitched vertical welting',(x+dx,yy,.81),(x+dx,yy,1.35),.006,.006,leather)
   box('case lid seam',(x,yy+side*.002,1.29),(.57,.003,.004),under,.0005)
   for dx in (-.27,.27):
    for z in (.817,1.345):
     box('case worn corner cap',(x+dx,yy+side*.003,z),(.06,.009,.055),under,.009)
     cyl('case corner rivet',(x+dx,yy+side*.010,z),.004,.005,brass,'Y',10)
  for dx in (-.07,.07):beam('case handle riser',(x+dx,y,1.376),(x+dx,y,1.42),.018,.018,under)
 # Thin luggage labels have one curled corner and a readable printed initial.
 for x,y,label in [(-45.5,97.237,'B'),(-44.65,97.387,'N')]:
  box('case paper luggage label',(x+.08,y,1.16),(.09,.001,.12),paper,.001)
  text('case label initial',label,(x+.08,y+.002,1.125),.06,ink,(math.pi/2,0,math.pi))
