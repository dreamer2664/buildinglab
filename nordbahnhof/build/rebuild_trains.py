"""NORDBAHNHOF rolling stock rebuild. Original procedural geometry, not an exact locomotive replica.
Six rakes / 34 vehicles. Detailed wheel/rod geometry and hollow windowed coach shells.
"""
import bpy,bmesh,math,sys,json,random
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_bay as b
ROOT=Path(__file__).resolve().parents[1]
COL=b.make_collection('TRAINS_REBUILT')
# Delete original locomotive and superseded coach geometry without deleting the station.
for ob in list(bpy.data.objects):
    if ob.name.startswith(('LOCO_','TENDER_','EMU_','STEAM_','TRAIN_')):bpy.data.objects.remove(ob,do_unlink=True)
for name in ('STATIC_BATCH_Rebuild carriage oxblood','STATIC_BATCH_Rebuild carriage charcoal roof'):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
for name in ('STATIC_BATCH_Rebuild painted petrol iron','STATIC_BATCH_Rebuild aged brass','STATIC_BATCH_Rebuild thin historic glazing'):
    ob=bpy.data.objects.get(name)
    if not ob:continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    dead=[]
    for f in bm.faces:
        p=f.calc_center_median()
        if -87<p.x<58 and .34<p.z<3.9 and any(abs(p.y-y)<1.7 for y in (40,52,64,76,88)):dead.append(f)
    bmesh.ops.delete(bm,geom=dead,context='FACES');bm.to_mesh(ob.data);bm.free()
# Remove obsolete short buffer-stop at the previous locomotive position.
for ob in list(bpy.data.objects):
    if ob.name.startswith('TRK_10_BufferStop'):bpy.data.objects.remove(ob,do_unlink=True)
# Correct the rail-head geometry to 1435 mm clear gauge and Z=0.180 m.
rail_ob=bpy.data.objects.get('STATIC_BATCH_Rebuild rail steel')
if rail_ob:
 for v in rail_ob.data.vertices:
  y0=min((40,46,52,58,64,70,76,82,88,113),key=lambda yy:abs(v.co.y-yy))
  v.co.y += .035 if v.co.y>y0 else -.035
  v.co.z -= .075
for ob in bpy.data.objects:
 if ob.name.startswith('TRK_') and '_Rail_' in ob.name:
  ob.location.y += .036 if 'North' in ob.name else -.036
# Helpers: exact dimensions, shared meshes, actual open spaces between window frames.
cache={};created=[];manifest=[]
def mat(name,color,metal=0,rough=.4):
    ma=b.make_pbr_mat('Train '+name,color,metal,rough,.035,90)
    for node in ma.node_tree.nodes:
        if node.type=='BUMP':node.inputs['Distance'].default_value=.00015
    return ma
black=mat('weathered graphite',(.025,.029,.032),.7,.32)
red=mat('vermilion frame',(.34,.018,.012),.45,.35)
steel=mat('machined steel',(.33,.36,.38),.9,.23)
dark=mat('oily underframe',(.012,.016,.018),.7,.48)
brass=mat('muted brass',(.42,.27,.085),.85,.28)
roofmat=mat('roof soot',(.024,.027,.025),.25,.7)
maroon=mat('coach oxblood',(.13,.018,.012),.35,.32)
green=mat('coach bottle green',(.016,.055,.038),.35,.35)
cream=mat('warm ivory lining',(.49,.42,.30),0,.65)
seatmat=mat('woven blue seats',(.025,.07,.09),0,.8)
wood=mat('mahogany partitions',(.12,.042,.018),0,.42)
coalmat=mat('anthracite',(.008,.009,.012),.15,.7)
emublue=mat('electric midnight blue',(.018,.045,.09),.4,.3)
window=bpy.data.materials.new('Train optical window glass');window.use_nodes=True
nt=window.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.24
transparent=nt.nodes.new('ShaderNodeBsdfTransparent');glass=nt.nodes.new('ShaderNodeBsdfGlass');glass.inputs['Color'].default_value=(.84,.93,.95,1);glass.inputs['Roughness'].default_value=.045
nt.links.new(transparent.outputs[0],mix.inputs[1]);nt.links.new(glass.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
vehicle='';prefix=''
def obj(name,mesh,loc,ma,rot=(0,0,0)):
    if not mesh.materials:mesh.materials.append(ma)
    ob=b.add_mesh_obj('TRAIN_'+prefix+'_'+name,mesh,loc,rot,col=COL);created.append(ob);return ob
def box(name,loc,size,ma,bevel=.006):
    key=('box',tuple(round(x,5) for x in size),ma.name,bevel)
    if key not in cache:cache[key]=b.create_box_mesh(name,*size,bevel_m=bevel)
    return obj(name,cache[key],loc,ma)
def cyl(name,loc,r,length,ma,axis='Z',segments=32):
    key=('cyl',r,length,ma.name,axis,segments)
    if key not in cache:cache[key]=b.create_cyl_mesh(name,r,length,segments,axis)
    return obj(name,cache[key],loc,ma)
def sphere(name,loc,size,ma):
    key=('sphere',tuple(size),ma.name)
    if key not in cache:cache[key]=b.create_sphere_mesh(name,*size,segs=20)
    return obj(name,cache[key],loc,ma)
def beam(name,p,q,width,depth,ma):
    mid,rot,length=b.orient_between(Vector(p),Vector(q));ob=box(name,mid,(width,length,depth),ma,.002);ob.rotation_euler=rot;return ob
def ring(name,loc,r,tube,ma,axis='Y'):
    key=('ring',r,tube,ma.name,axis)
    if key not in cache:
        verts=[];faces=[];N=48;M=8
        for i in range(N):
            a=2*math.pi*i/N
            for j in range(M):
                u=2*math.pi*j/M;x=(r+tube*math.cos(u))*math.cos(a);y=(r+tube*math.cos(u))*math.sin(a);z=tube*math.sin(u)
                verts.append((x,z,y) if axis=='Y' else (z,x,y) if axis=='X' else (x,y,z))
        for i in range(N):
            for j in range(M):faces.append((i*M+j,((i+1)%N)*M+j,((i+1)%N)*M+(j+1)%M,i*M+(j+1)%M))
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();b.set_smooth(me);cache[key]=me
    return obj(name,cache[key],loc,ma)
def text(name,body,loc,size,ma,side=-1):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=.001;cu.materials.append(ma)
    ob=bpy.data.objects.new('TRAIN_'+prefix+'_'+name,cu);COL.objects.link(ob);ob.location=loc;ob.rotation_euler=(math.pi/2,0,0 if side<0 else math.pi);created.append(ob)
def endgear(x,y,z=1.04):
    for dy in (-.88,.88):
        cyl('buffer shank',(x,y+dy,z),.07,.35,dark,'X',20)
        cyl('buffer sleeve',(x+.12,y+dy,z),.11,.22,black,'X',24)
        cyl('buffer polished head',(x-.17,y+dy,z),.19,.06,steel,'X',32)
    # Hanging screw coupling and air hose, modelled as linked rings.
    for zz in (z-.12,z-.25,z-.38):ring('coupling chain',(x-.12,y,zz),.075,.013,dark,'Y')
    beam('coupling screw',(x-.12,y,z-.19),(x-.12,y,z-.39),.025,.025,steel)
    for side in (-1,1):
        pts=[(x,y+side*.30,z-.08),(x-.12,y+side*.36,z-.3),(x-.08,y+side*.39,z-.55)]
        for p,q in zip(pts,pts[1:]):beam('air hose',p,q,.035,.035,dark)
def batch_vehicle(kind,location):
    # Batch geometry within each vehicle/material. Mesh components remain modelled, not shader tricks.
    from collections import defaultdict
    groups=defaultdict(list)
    for ob in created:
        if ob.type=='MESH':groups[ob.data.materials[0].name].append(ob)
    count=len(created)
    print('BATCH',prefix,count,flush=True)
    bpy.ops.object.select_all(action='DESELECT')
    for ma,objects in groups.items():
        if len(objects)<2:continue
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];objects[0].data=objects[0].data.copy();bpy.ops.object.join();bpy.context.object.name='TRAIN_'+prefix+'_'+ma
        bpy.ops.object.select_all(action='DESELECT')
    manifest.append({'id':prefix,'type':kind,'origin':location,'authored_parts_before_batching':count})
    created.clear()
    keep=set(cache.values())
    for mesh in list(bpy.data.meshes):
        if mesh.users==0 and mesh not in keep:bpy.data.meshes.remove(mesh)
def driving_wheel(x,y,z,r,side):
    yy=y+side*.82
    # Turned steel tyre: a conical tread and inner flange, not a torus.
    key=('proper railway tyre',r,side)
    if key not in cache:
        profile=[(r-.105,-.125),(r+.012,-.125),(r+.028,-.115),(r+.028,-.108),(r+.016,-.104),(r,-.080),(r-.006,.020),(r-.014,.028),(r-.105,.028)]
        N=96;M=len(profile);vv=[];ff=[]
        for k in range(N):
            a=k*math.tau/N
            for rr,axial in profile:vv.append((rr*math.sin(a),side*axial,rr*math.cos(a)))
        for k in range(N):
            for j in range(M):
                f=(k*M+j,((k+1)%N)*M+j,((k+1)%N)*M+(j+1)%M,k*M+(j+1)%M)
                ff.append(f if side>0 else tuple(reversed(f)))
        me=bpy.data.meshes.new('turned wheel tyre with flange');me.from_pydata(vv,[],ff);me.update()
        for p in me.polygons:p.use_smooth=True
        for e in me.edges:
            a,c=e.vertices
            if a%M==c%M:e.use_edge_sharp=True
        cache[key]=me
    obj('steel tyre and inner flange',cache[key],(x,yy,z),steel)
    ring('wheel inner rim',(x,yy,z),r-.13,.035,red)
    ring('wheel flange',(x,yy-side*.07,z),r-.012,.025,dark)
    cyl('wheel hub',(x,yy,z),.14,.22,red,'Y')
    for k in range(18):
        a=k*math.pi/9
        beam('tapered spoke',(x+.13*math.sin(a),yy,z+.13*math.cos(a)),(x+(r-.13)*math.sin(a),yy,z+(r-.13)*math.cos(a)),.052,.045,red)
    box('counterweight',(x,yy+side*.025,z-r*.53),(.65,.07,.24),red,.015)
    cyl('axle boss',(x,yy+side*.13,z),.083,.065,steel,'Y',24)
# Steam express locomotive, historically inspired 4-6-2 running gear.
prefix='TR01_V01_STEAM';y=93
box('main plate',(-46,y,1.56),(16,2.65,.14),black)
for side in (-1,1):box('plate lip',(-46,y+side*1.34,1.54),(16,.045,.16),red)
for xx,r in [(-53,.43),(-51.8,.43),(-48.5,.95),(-46.25,.95),(-44,.95),(-40.8,.50)]:
    for side in (-1,1):driving_wheel(xx,y,.18+r,r,side)
    cyl('through axle',(xx,y,.18+r),.075,1.65,dark,'Y',20)
for side in (-1,1):
    box('frame rail',(-46.5,y+side*.64,1.13),(13,.12,.28),red)
    for xx in (-48.5,-46.25,-44):
        yy=y+side*1.0;crankz=.18+.95-.29
        cyl('crank pin',(xx+.16,yy,crankz),.075,.08,steel,'Y',20)
        box('axle spring',(xx,y+side*.55,1.55),(1.0,.12,.08),dark)
    beam('coupling rod',(-48.34,y+side*1.05,.84),(-43.84,y+side*1.05,.84),.12,.055,steel)
    cyl('cylinder casting',(-51,y+side*1.05,.91),.33,1.25,black,'X')
    cyl('cylinder cover',(-51.65,y+side*1.05,.91),.34,.05,steel,'X')
    beam('piston rod',(-50.5,y+side*1.07,.91),(-49.3,y+side*1.07,.91),.065,.065,steel)
    beam('main connecting rod',(-49.3,y+side*1.11,.91),(-46.09,y+side*1.11,.84),.14,.055,steel)
    beam('valve reach rod',(-50.4,y+side*1.16,1.2),(-45.9,y+side*1.16,1.38),.035,.04,steel)
    for xx in (-51.2,-50.5):
        for j in range(12):
            a=j*math.pi/6;cyl('cylinder cover bolt',(xx,y+side*1.05+.27*math.sin(a),.91+.27*math.cos(a)),.018,.035,steel,'X',6)
# Barrel and smokebox. Thin bands are rings, not solid cylinders hiding the boiler.
cyl('boiler barrel',(-46.5,y,2.65),.87,9.4,black,'X',64)
cyl('smokebox',(-52,y,2.65),.89,1.8,black,'X',64)
sphere('convex smokebox door',(-52.94,y,2.65),(.08,.75,.75),black)
ring('smokebox door sealing ring',(-53.0,y,2.65),.77,.024,steel,'X')
for j in range(16):
 a=j*math.pi/8;cyl('door dog',(-53.025,y+.69*math.sin(a),2.65+.69*math.cos(a)),.023,.06,steel,'X',6)
beam('smokebox dart',(-53.09,y-.21,2.65),(-53.09,y+.21,2.65),.045,.045,steel)
beam('smokebox latch',(-53.12,y,2.46),(-53.12,y,2.84),.04,.04,steel)
for xx in (-52.8,-52.3):box('smokebox hinge',(xx,y-.69,2.64),(.10,.08,.4),black)
for xx in (-50.6,-48.6,-46.6,-44.6,-42.6):ring('boiler band',(xx,y,2.65),.88,.014,black,'X')
cyl('chimney base',(-52,y,3.53),.29,.15,black)
cyl('chimney',(-52,y,3.89),.21,.62,black)
ring('chimney lip',(-52,y,4.21),.235,.026,black,'Z')
sphere('steam dome',(-47.9,y,3.51),(.39,.39,.43),black)
cyl('dome base',(-47.9,y,3.43),.42,.10,black)
for xx in (-45.9,-45.65):cyl('safety valve',(xx,y,3.67),.055,.38,brass,segments=20)
# Handrails and long external steam pipes.
for side in (-1,1):
 beam('boiler handrail',(-52.5,y+side*.84,3.02),(-41.7,y+side*.84,3.02),.018,.018,steel)
 for xx in (-52,-50,-48,-46,-44,-42):beam('handrail stanchion',(xx,y+side*.72,3.02),(xx,y+side*.85,3.02),.016,.016,steel)
 beam('steam pipe',(-50.4,y+side*.69,1.89),(-42.5,y+side*.69,1.89),.055,.055,black)
 # Rows of fine rivets on running-plate edging.
 for k in range(66):sphere('plate rivet',(-53.7+k*.24,y+side*1.366,1.55),(.012,.009,.012),steel)
# Open cab: piers/sills/headers rather than a solid cube with painted windows.
for side in (-1,1):
 yy=y+side*1.34
 box('cab lower panel',(-40.8,yy,2.0),(2.5,.08,.8),black)
 for xx in (-42,-40.75,-39.55):box('cab window post',(xx,yy,2.94),(.09,.10,1.10),black)
 box('cab cantrail',(-40.8,yy,3.54),(2.55,.10,.13),black)
 for xx in (-41.38,-40.14):
  box('cab window glass',(xx,yy,2.98),(1.12,.012,.96),window,.001)
  for zz in (2.48,3.47):box('cab brass window trim',(xx,yy+side*.055,zz),(1.16,.025,.018),brass,.001)
 box('cab number plate',(-40.8,yy+side*.065,2.12),(.74,.025,.27),red)
 text('cab number','01  164',(-40.8,yy+side*.085,2.04),.16,cream,side)
 for j in range(3):box('cab access step',(-39.7,y+side*(1.38+j*.10),1.5-j*.30),(.65,.34,.05),steel)
# Curved roof, open underside.
verts=[];faces=[]
for xx in (-42.3,-39.2):
 for k in range(25):
  a=-math.pi/2+math.pi*k/24;verts.append((xx,y+1.52*math.sin(a),3.57+.42*math.cos(a)))
for k in range(24):faces.append((k,k+1,25+k+1,25+k))
me=bpy.data.meshes.new('Arched cab roof');me.from_pydata(verts,[],faces);obj('arched cab roof',me,(0,0,0),black)
box('cab floor',(-40.8,y,1.65),(2.55,2.6,.1),wood)
cyl('backhead',(-41.7,y,2.6),.72,.18,dark,'X')
for dy in (-.25,.25):ring('cab valve wheel',(-41.5,y+dy,2.8),.11,.015,red,'X')
box('front buffer beam',(-54,y,1.05),(.18,2.8,.38),red)
endgear(-54.1,y)
for dy in (-.75,.75):
 cyl('headlamp housing',(-54.13,y+dy,1.35),.13,.15,black,'X')
 cyl('headlamp lens',(-54.22,y+dy,1.35),.11,.012,cream,'X')
batch_vehicle('inspired 4-6-2 steam locomotive',[-46,93,0])
# Tender: open coal bunker, water tank, leaf springs, eight wheels.
prefix='TR01_V02_TENDER';x=-34
box('tender chassis',(x,y,.95),(7.1,2.65,.30),red)
box('water tank',(x,y,1.85),(6.8,2.65,1.35),black)
for side in (-1,1):box('bunker side',(x,y+side*1.35,2.75),(7,.09,.45),black)
for xx in (x-3.45,x+3.45):box('bunker end',(xx,y,2.75),(.09,2.65,.45),black)
random.seed(71)
for j in range(180):
 xx=x+random.uniform(-3.1,2.1);yy=y+random.uniform(-1.2,1.2);zz=2.58+.30*max(0,1-abs(xx-x)/3)+random.random()*.13
 sphere('coal chunk',(xx,yy,zz),(.12,.10,.075),coalmat)
cyl('water filler',(x+2.7,y,2.63),.28,.16,black)
for xx in (x-2.5,x-1.2,x+1.2,x+2.5):
 for side in (-1,1):
  driving_wheel(xx,y,.70,.52,side)
  box('tender leaf spring',(xx,y+side*1.0,1.15),(.9,.10,.10),dark)
endgear(x+3.65,y)
batch_vehicle('eight-wheel coal/water tender',[x,y,0])
# Coach shell with curved roofs, real cabin space, fitted seats, doors and bogies.
def coach(x,y,number,paint,electric=False,panto=False):
 global prefix
 prefix=number
 length=22;half=length/2
 box('steel chassis',(x,y,.97),(21.7,2.72,.24),dark)
 box('interior floor',(x,y,1.23),(21.3,2.62,.10),wood)
 for side in (-1,1):
  yy=y+side*1.40
  box('lower side',(x,yy,1.71),(21.8,.075,.86),paint)
  box('upper window rail',(x,yy,3.35),(21.8,.075,.20),paint)
  for j in range(10):
   wx=x-8.7+j*1.93
   box('window pillar',(wx-.88,yy,2.7),(.15,.09,1.15),paint)
   box('glazing',(wx,yy,2.73),(1.57,.008,.99),window,.001)
   for zz in (2.21,3.25):box('window horizontal frame',(wx,yy+side*.015,zz),(1.65,.035,.032),steel,.002)
   for dx in (-.82,.82):box('window vertical frame',(wx+dx,yy+side*.015,2.73),(.032,.035,1.06),steel,.002)
   # Ventilator strip above each window.
   box('window vent',(wx,yy,3.34),(1.45,.08,.065),dark)
  for zz in (1.39,2.12,3.49):box('waist lining',(x,yy+side*.045,zz),(21.9,.02,.025),brass,.001)
  for dx in (-10.25,10.25):
   box('vestibule door',(x+dx,yy,2.23),(1.1,.08,2.12),paint)
   box('door glass',(x+dx,yy+side*.045,2.72),(.64,.008,.71),window,.001)
   for z in (2.34,3.1):box('door glass frame',(x+dx,yy+side*.06,z),(.70,.025,.025),steel,.001)
   beam('door grab rail',(x+dx+.40,yy+side*.12,1.72),(x+dx+.40,yy+side*.12,2.28),.018,.018,steel)
   for k in range(2):box('boarding step',(x+dx,y+side*(1.48+k*.12),1.1-k*.24),(1.0,.33,.045),steel)
  text('class marking','2',(x+9.4,yy+side*.07,2.92),.27,cream,side)
  text('operator lettering','N O R D B A H N',(x,yy+side*.07,1.68),.13,cream,side)
  text('vehicle number',number.replace('_',' '),(x,yy+side*.07,1.45),.085,cream,side)
 # Rounded elliptical roof from swept cross-section.
 verts=[];faces=[]
 for xx in (x-half-.12,x+half+.12):
  for k in range(25):
   a=-math.pi/2+math.pi*k/24;verts.append((xx,y+1.46*math.sin(a),3.44+.46*math.cos(a)))
 for k in range(24):faces.append((k,k+1,25+k+1,25+k))
 me=bpy.data.meshes.new('Coach continuous roof');me.from_pydata(verts,[],faces);me.update();b.set_smooth(me);obj('rounded roof',me,(0,0,0),roofmat)
 for xx in (x-9,x-6,x-3,x,x+3,x+6,x+9):cyl('roof vent',(xx,y,3.97),.09,.13,roofmat,segments=16)
 # End walls with gangway apertures left empty.
 for sign in (-1,1):
  xx=x+sign*10.94
  for sy in (-1,1):box('end wall pier',(xx,y+sy*.96,2.3),(.10,.85,2.15),paint)
  box('end wall header',(xx,y,3.35),(.10,2.7,.30),paint)
  for k in range(5):
   for sy in (-1,1):box('gangway bellows',(xx+sign*(.08+k*.055),y+sy*.56,2.25),(.035,.07,1.8),dark)
   box('gangway top',(xx+sign*(.08+k*.055),y,3.15),(.035,1.18,.07),dark)
  box('gangway footplate',(xx+sign*.18,y,1.33),(.42,1.12,.04),steel)
  endgear(xx+sign*.23,y)
 # Interior benches and partitions are visible through glazing, not black window decals.
 for j in range(9):
  sx=x-8+j*2
  for side in (-1,1):
   sy=y+side*.88
   box('seat cushion',(sx,sy,1.66),(.54,.76,.12),seatmat)
   box('seat back',(sx-.25,sy,1.99),(.10,.76,.57),seatmat)
  box('luggage rack',(sx,y+.95,3.0),(1.5,.60,.035),brass)
 for bx in (x-7.3,x+7.3):
  box('bogie stretcher',(bx,y,.67),(3.5,1.75,.18),dark)
  for side in (-1,1):
   box('bogie side frame',(bx,y+side*1.02,.68),(3.1,.14,.23),dark)
   for dx in (-1.05,1.05):
    xx=bx+dx
    cyl('coach wheel',(xx,y+side*.78,.64),.46,.12,dark,'Y')
    ring('coach wheel tire',(xx,y+side*.80,.64),.425,.035,steel)
    box('axlebox',(xx,y+side*1.03,.65),(.28,.22,.27),black)
    for k in range(4):box('laminated spring',(xx,y+side*1.03,.92+k*.022),(.75-k*.10,.12,.018),dark,.001)
    cyl('axle',(xx,y,.64),.06,1.6,steel,'Y',16)
    # Axle bearing cap, frame fasteners and wheel-adjacent brake shoes.
    cyl('bearing cover',(xx,y+side*1.16,.65),.09,.025,steel,'Y',24)
    for k in range(6):
     a=k*math.pi/3
     cyl('bearing cap bolt',(xx+.11*math.cos(a),y+side*1.18,.65+.11*math.sin(a)),.014,.025,steel,'Y',6)
    for direction in (-1,1):
     ob=box('brake shoe',(xx+direction*.38,y+side*.8,.69),(.08,.16,.23),dark)
     ob.rotation_euler.y=direction*.3
     beam('brake hanger',(xx+direction*.38,y+side*.82,.69),(xx+direction*.48,y+side*.82,.99),.025,.025,steel)

 box('battery box',(x-2.8,y-.75,.77),(1.8,.65,.4),black)
 cyl('air reservoir',(x+2,y,.71),.20,1.6,dark,'X')
 for yy in (-.55,.55):beam('brake rigging',(x-5,y+yy,.80),(x+5,y+yy,.80),.025,.025,steel)
 if electric and number.endswith('V01'):
  # Driving cab addition: raked windscreen, shaped nose panels and lamp clusters.
  xx=x-11
  vs=[(xx,y-1.4,1.35),(xx,y+1.4,1.35),(xx-1.2,y+1.17,1.45),(xx-1.2,y-1.17,1.45),
      (xx,y-1.4,3.44),(xx,y+1.4,3.44),(xx-.95,y+1.1,3.20),(xx-.95,y-1.1,3.20)]
  me=bpy.data.meshes.new('Electric sloped cab');me.from_pydata(vs,[],[(0,1,2,3),(0,3,7,4),(1,5,6,2),(4,7,6,5)]);obj('electric nose side panels',me,(0,0,0),paint)
  box('nose lower front',(xx-1.17,y,1.84),(.09,2.32,.70),paint)
  vs=[(xx-1.22,y-1.04,2.28),(xx-1.22,y+1.04,2.28),(xx-.96,y+1.04,3.15),(xx-.96,y-1.04,3.15)]
  me=bpy.data.meshes.new('Raked panoramic windscreen');me.from_pydata(vs,[],[(0,1,2,3)]);obj('front windshield',me,(0,0,0),window)
  beam('windscreen center mullion',(xx-1.23,y,2.28),(xx-.97,y,3.15),.045,.045,steel)
  for sy in (-1,1):
   cyl('electric headlight housing',(xx-1.24,y+sy*.8,1.93),.14,.06,dark,'X')
   cyl('electric headlight lens',(xx-1.28,y+sy*.8,1.93),.10,.012,cream,'X')
  endgear(xx-1.3,y)
 if panto:
  # Diamond linkage and collector shoe; a visible model, not a bar floating over the roof.
  for side in (-1,1):
   sy=y+side*.44
   for k in (-1,1):
    beam('pantograph lower',(x,sy,4.12),(x+k*1.1,sy,4.78),.05,.045,steel)
    beam('pantograph upper',(x+k*1.1,sy,4.78),(x,sy,5.42),.045,.04,steel)
  box('pantograph collector',(x,y,5.48),(.20,1.48,.04),dark)
  box('pantograph base',(x,y,4.08),(1.8,1.1,.06),dark)
  for sy in (-.44,.44):
   beam('pantograph balancing spring',(x-.7,y+sy,4.12),(x+.7,y+sy,4.12),.08,.06,dark)

  for dx in (-1,1):cyl('roof insulator',(x+dx,y,4.03),.10,.17,cream,segments=16)
 batch_vehicle('electric passenger car' if electric else 'windowed passenger coach',[x,y,0])
# Four coaches behind locomotive/tender = six vehicles in train 1.
for j,x in enumerate((-17,7,31,55)):coach(x,93,f'TR01_V{j+3:02}',green)
# Five further rakes, 28 vehicles. Third rake is electric stock.
for train,y,n in [(2,40,6),(3,52,6),(4,64,6),(5,76,5),(6,88,5)]:
 for j in range(n):
  x=-68+j*24
  coach(x,y,f'TR{train:02}_V{j+1:02}',emublue if train==4 else maroon if train%2==0 else green,electric=train==4,panto=train==4 and j in (0,3))
# Continuous contact wire over the electric rake, shoe at Z=5.50 m.
prefix='TR04_CATENARY'
beam('contact wire',(-90,64,5.50),(90,64,5.50),.012,.012,brass)
beam('messenger wire',(-90,64,6.25),(90,64,6.25),.012,.012,brass)
for xx in range(-84,90,12):beam('contact wire dropper',(xx,64,5.50),(xx,64,6.25),.008,.008,brass)
created.clear()
# Train inspection cameras stay independent of previous gallery indices.
for ob in list(bpy.data.objects):
 if ob.type=='CAMERA' and ob.name.startswith('TRAINVIEW_'):bpy.data.objects.remove(ob,do_unlink=True)
views=[('01_steam_threequarter',(-61,98.5,2.9),(-47,93,2.0),42),('02_driving_wheels',(-49.5,97.3,1.50),(-46.9,93.9,1.20),40),('03_cab_tender',(-44.4,98,3.2),(-40.2,93,2.5),35),('04_coach_platform',(-5,99,2.25),(9,93,2.4),38),('05_bogie_platform_cutaway',(1.6,97,1.05),(-.3,93.7,.75),42),('06_electric_pantograph',(-65,68,6.0),(-68,64,4.7),42)]
for name,loc,target,lens in views:
 data=bpy.data.cameras.new('TRAINVIEW_'+name);data.lens=lens;data.clip_start=.03;data.clip_end=350
 ob=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.view_settings.exposure=-.35
# Broad, plausible skylight bounce to keep mechanical details legible.
for name,loc,target,energy in [('Engine bounce',(-48,98,7),(-47,93,2),2100),('Cab bounce',(-40,98,6),(-40,93,2),1000)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.size=5;data.color=(.85,.91,1)
 ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
for name,loc,target,energy in [('Coach bounce',(0,98,6),(0,93,2),1400),('Electric bounce',(-67,69,8),(-68,64,4.7),1800),('Bogie bounce',(0,96,2.2),(0,93,.65),600)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.size=5;data.color=(.87,.92,1)
 ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
(ROOT/'evidence/TRAIN_BUILD_MANIFEST.json').write_text(json.dumps({'status':'built, requires visual inspection','vehicles':manifest,'vehicle_count':len(manifest),'train_count':6,'reference':'Historically inspired original procedural stock, not certified exact BR01 replica','limitations':['No operational animation/clearance certification','Modern scanned passengers are unchanged','Full station commission remains incomplete']},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_TRAINS.blend'),compress=True)
print('TRAIN BUILD:',len(manifest),'vehicles,',len(bpy.data.objects),'objects. NOT VISUAL ACCEPTANCE.')
