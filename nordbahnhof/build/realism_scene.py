"""Physical surface and scene rebuild, extending the inspected train update.
Real geometry, packed scan textures, real volumes and physically motivated wear.
"""
import bpy,bmesh,math,random,sys,json
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from realism_materials import apply_materials,painted,newmat,worldvec,noise,ramp,mathnode,mixcolor
import build_bay as b
ROOT=Path(__file__).resolve().parents[1]
random.seed(90124)
floor,brick,gravel,stone,replacements=apply_materials()
col=b.make_collection('REALISM_CONSTRUCTION');parts=[];cache={}
def meshobj(name,me,loc=(0,0,0),mat=None):
    ob=bpy.data.objects.new('REAL_'+name,me);col.objects.link(ob);ob.location=loc
    if mat and not me.materials:me.materials.append(mat)
    parts.append(ob);return ob
def box(name,loc,size,mat,bevel=.003):
    key=(tuple(round(v,5) for v in size),mat.name,bevel)
    if key not in cache:cache[key]=b.create_box_mesh(name,*size,bevel_m=bevel)
    return meshobj(name,cache[key],loc,mat)
def cyl(name,loc,r,h,mat,axis='Z',segments=24):
    key=('cyl',r,h,mat.name,axis)
    if key not in cache:cache[key]=b.create_cyl_mesh(name,r,h,segments,axis)
    return meshobj(name,cache[key],loc,mat)
def beam(name,p,q,w,d,ma):
    mid,rot,length=b.orient_between(Vector(p),Vector(q));ob=box(name,mid,(w,length,d),ma,.002);ob.rotation_euler=rot;return ob
def ball(name,loc,size,ma):
    key=('ball',tuple(size),ma.name)
    if key not in cache:cache[key]=b.create_sphere_mesh(name,*size,16)
    return meshobj(name,cache[key],loc,ma)
def text(name,body,loc,size,ma,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.001;cu.materials.append(ma)
    ob=bpy.data.objects.new('REAL_'+name,cu);col.objects.link(ob);ob.location=loc;ob.rotation_euler=rot;return ob
black=replacements['Train weathered graphite'];steel=replacements['Train machined steel'];red=replacements['Train vermilion frame'];iron=replacements['Rebuild painted petrol iron'];brass=replacements['Train muted brass'];under=replacements['Train oily underframe']
# Authored wood: longitudinal open grain, damaged lacquer, quiet colour variation.
wood,n,l,bs=newmat('REAL weathered oak slats');vec=worldvec(n,l,(.55,30,30));fac=noise(n,l,vec,7,4)
l.new(ramp(n,l,fac,[(.15,(.055,.028,.011)),(.75,(.24,.13,.055))]),bs.inputs['Base Color']);l.new(ramp(n,l,fac,[(.2,(.34,)*3),(.8,(.72,)*3)]),bs.inputs['Roughness'])
bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0008;bump.inputs['Strength'].default_value=.28;l.new(fac,bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
for ob in bpy.data.objects:
    if ob.type=='MESH':
        for slot in ob.material_slots:
            if slot.material and slot.material.name in ('Detail aged oak','MAT_Timber_CreosoteSleeper','Rebuild creosote'):slot.material=wood
# Strip the perfect painted platform plane and replace with physical individual slabs.
for ob in bpy.data.objects:
    if ob.name.startswith(('PLT_07_GraniteDeck','Platform stone joint','Platform longitudinal joint','PLT_07_YellowLine')):ob.hide_render=True;ob.hide_viewport=True
# Each slab varies by 1-3 mm, not exaggerated arbitrary displacement.
for row in range(6):
    for k in range(120):
        x=-89.25+k*1.5;y=95.25+row*1.5
        sx=1.488-random.choice((0,.002,.004));sy=1.488-random.choice((0,.002,.004));z=.725+random.uniform(-.0015,.0015)
        ob=box('stone slab',(x+random.uniform(-.001,.001),y+random.uniform(-.001,.001),z),(sx,sy,.065),floor,.004)
        ob.rotation_euler.z=random.uniform(-.0007,.0007)
# Deep joint bed below the tiles (dark, not black drawn grid).
bed=painted('REAL joint mortar',(.055,.052,.045),rough=.9)
box('joint bed',(0,99.0,.704),(180,9,.045),bed,.0)
# Worn safety paint: incomplete pigment, physically thin, no luminous perfectly clean stripe.
paint,n,l,bs=newmat('REAL abraded platform warning paint');bs.inputs['Base Color'].default_value=(.47,.29,.025,1);bs.inputs['Roughness'].default_value=.83
v=worldvec(n,l,(12,18,10));grit=noise(n,l,v,11,4);mask=ramp(n,l,grit,[(.35,(0,0,0)),(.42,(1,1,1))]);out=next(x for x in n if x.type=='OUTPUT_MATERIAL');transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(mask,mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(bs.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
for k in range(120):
    box('worn yellow line',(-89.25+k*1.5,95.02,.761),(1.49,.135,.001),paint,.0)
# Chipped platform coping. Real geometry rather than a bump pretending to change silhouette.
for k in range(90):
    x=-89+k*2
    ob=box('coping block',(x,94.62,.705),(1.987,.24,.13),stone,.006)
    # A minority of edges have shallow missing corners.
    if k%11==3:
        me=ob.data.copy();ob.data=me
        for v in me.vertices:
            if v.co.x>.8 and v.co.y<-.08 and v.co.z>.03:v.co.z-=random.uniform(.008,.016)
# Real local track ballast stones: geometry only where the foreground can resolve it.
rock=bpy.data.materials.new('REAL individual basalt stones');rock.use_nodes=True;rbs=rock.node_tree.nodes.get('Principled BSDF');rbs.inputs['Base Color'].default_value=(.10,.095,.083,1);rbs.inputs['Roughness'].default_value=.88
bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=1);unitv=[v.co.copy() for v in bm.verts];bm.verts.index_update();unitf=[[v.index for v in f.verts] for f in bm.faces];bm.free()
verts=[];faces=[]
for k in range(11000):
    x=random.uniform(-66,-37);y=random.uniform(91.5,94.48);z=.08;size=random.uniform(.025,.060)
    # Keep ties and running surfaces exposed, as on a real ballasted track.
    if abs(((x-1.5)%.65)-.13)<.14:continue
    base=len(verts);rot=Matrix.Rotation(random.random()*6.28,3,'Z')
    for v in unitv:
        q=rot@Vector((v.x*size,v.y*size*.85,v.z*size*.58));verts.append((x+q.x,y+q.y,z+q.z))
    faces.extend(tuple(base+i for i in f) for f in unitf)
me=bpy.data.meshes.new('foreground ballast stones');me.from_pydata(verts,[],faces);meshobj('foreground ballast',me,mat=rock)
# Oil-darkened deposits under the locomotive: discrete, thin, irregular patches, not pools on every surface.
oil,n,l,bs=newmat('REAL old oil and water');bs.inputs['Base Color'].default_value=(.018,.015,.010,1);bs.inputs['Roughness'].default_value=.12;bs.inputs['Coat Weight'].default_value=.5
for j in range(8):
    x=-51+j*1.25;y=93+random.uniform(-.5,.5)
    vs=[(x,y,.105)];N=19
    for k in range(N):
        a=2*math.pi*k/N;r=random.uniform(.16,.32);vs.append((x+math.cos(a)*r*1.7,y+math.sin(a)*r,.105))
    me=bpy.data.meshes.new('oil stain');me.from_pydata(vs,[],[(0,k+1,(k+1)%N+1) for k in range(N)]);meshobj('oil stain',me,mat=oil)
# Correct an obviously toy-like front with railway hardware, brackets, number/name plates and smoke deflectors.
for side in (-1,1):
    yy=93+side*1.1515
    # Rolled smoke-deflector sheet with folded top and reinforcing flanges.
    vs=[(-53.4,yy,1.75),(-50.4,yy,1.75),(-50.4,yy,3.6),(-53.0,yy,3.6),(-53.4,yy,3.30),
        (-53.4,yy+side*.0035,1.75),(-50.4,yy+side*.0035,1.75),(-50.4,yy+side*.0035,3.6),(-53.0,yy+side*.0035,3.6),(-53.4,yy+side*.0035,3.30)]
    fs=[(0,1,2,3,4),(9,8,7,6,5)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
    me=bpy.data.meshes.new('rolled smoke deflector');me.from_pydata(vs,[],fs);ob=meshobj('smoke deflector',me,mat=black)
    for x in (-53.1,-51.8,-50.6):
        beam('deflector bracket',(x,93+side*.85,2.2),(x,yy,2.2),.045,.045,steel)
        for z in (1.87,3.45):cyl('deflector bolt',(x,yy+side*.055,z),.014,.018,steel,'Y',6)
    beam('deflector rolled edge',(-53.0,yy,3.61),(-50.4,yy,3.61),.028,.028,black)
# Front number plate lies on the smokebox door, facing the direction of travel.
box('front number backing',(-53.10,93,2.26),(.035,1.10,.26),under,.008)
text('front number','01 164',(-53.125,93,2.18),.19,brass,(math.pi/2,0,-math.pi/2))
# Central handwheel and door hinge pin, rather than a simple cross.
cyl('door handwheel hub',(-53.14,93,2.69),.05,.04,steel,'X')
N=40;vs=[];fs=[]
for i in range(N):
    a=i*2*math.pi/N
    for j in range(8):
        t=j*math.pi/4;vs.append((-53.18+.012*math.sin(t),93+(.15+.012*math.cos(t))*math.cos(a),2.69+(.15+.012*math.cos(t))*math.sin(a)))
for i in range(N):
    for j in range(8):fs.append((i*8+j,((i+1)%N)*8+j,((i+1)%N)*8+(j+1)%8,i*8+(j+1)%8))
me=bpy.data.meshes.new('smokebox handwheel rim');me.from_pydata(vs,[],fs);b.set_smooth(me);meshobj('door handwheel',me,mat=steel)
for a in (0,2*math.pi/3,4*math.pi/3):beam('handwheel spoke',(-53.18,93,2.69),(-53.18,93+.15*math.cos(a),2.69+.15*math.sin(a)),.018,.018,steel)
# Forged rod eyes and grease caps add actual mechanical attachment, not floating flat bars.
for side in (-1,1):
    yy=93+side*1.09
    for x in (-48.34,-46.09,-43.84):
        cyl('rod big end',(x,yy,.84),.12,.07,steel,'Y')
        cyl('rod bronze bush',(x,yy+side*.04,.84),.070,.025,brass,'Y')
        cyl('rod locking nut',(x,yy+side*.065,.84),.05,.024,steel,'Y',6)
        cyl('grease nipple',(x,yy,.96),.014,.035,brass)
# Luminous headlamp lenses with a dark metal reflector surround; actual modest area/point lights.
lamp,n,l,bs=newmat('REAL warm headlamp glass');bs.inputs['Base Color'].default_value=(.8,.65,.35,1);bs.inputs['Emission Color'].default_value=(1,.66,.30,1);bs.inputs['Emission Strength'].default_value=5;bs.inputs['Roughness'].default_value=.18
for y,z in [(92.25,1.35),(93.75,1.35),(93,3.48)]:
    cyl('headlamp housing',(-53.16 if z>3 else -54.18,y,z),.15,.19,black,'X')
    x=-53.27 if z>3 else -54.285
    cyl('headlamp lens',(x,y,z),.115,.015,lamp,'X')
    data=bpy.data.lights.new('Headlamp bulb','POINT');data.energy=7;data.color=(1,.67,.32);data.shadow_soft_size=.04
    ob=bpy.data.objects.new('REAL_headlamp light',data);col.objects.link(ob);ob.location=(x-.02,y,z)
# Small supports on the cab steps: no slabs suspended in thin air.
for side in (-1,1):
    for x in (-40.0,-39.4):beam('step supporting bracket',(x,93+side*1.31,1.65),(x,93+side*1.6,.84),.035,.035,steel)
# Photographic-scale story details: suitcase, trolley, bent luggage straps and readable warning plaques.
leather=painted('REAL battered suitcase leather',(.12,.06,.023),rough=.68)
for x,y in [(-45.5,97.1),(-44.65,97.25)]:
    ob=box('travel case',(x,y,1.08),(.62,.23,.61),leather,.025);ob.rotation_euler.z=.12
    for dx in (-.18,.18):box('case leather strap',(x+dx,y-.122,1.08),(.035,.012,.61),under,.001)
    for dx in (-.23,.23):box('case brass clasp',(x+dx,y-.13,1.25),(.045,.015,.06),brass,.002)
    beam('case handle',(x-.07,y,1.42),(x+.07,y,1.42),.018,.018,under)
# Two genuine scanned passengers moved near the heritage locomotive, no new fake identities.
placements={'SCAN_HERO_01':(-46.0,97.05,.76),'SCAN_HERO_02':(-42.8,97.5,.76),'SCAN_HERO_03':(-44.2,96.6,.76),'SCAN_HERO_04':(-48.0,98.0,.76)}
for name,loc in placements.items():
    ob=bpy.data.objects.get(name)
    if ob:ob.location=loc
# Low real volumetric steam at the cylinder drain cocks; density fades to zero at the boundary.
steam=bpy.data.materials.new('REAL transient cylinder steam');steam.use_nodes=True;nt=steam.node_tree;nt.nodes.clear();n=nt.nodes;l=nt.links
out=n.new('ShaderNodeOutputMaterial');volume=n.new('ShaderNodeVolumePrincipled');volume.inputs['Color'].default_value=(.82,.88,.93,1);volume.inputs['Anisotropy'].default_value=.2
tex=n.new('ShaderNodeTexCoord');dist=n.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,.5);l.new(tex.outputs['Generated'],dist.inputs[0]);edge=mathnode(n,l,'SUBTRACT',.52,dist.outputs['Value']);edge=mathnode(n,l,'MAXIMUM',edge,0);edge=mathnode(n,l,'MULTIPLY',edge,9)
cloud=noise(n,l,worldvec(n,l,(1,1,1)),6,5);cloud=ramp(n,l,cloud,[(.35,(0,0,0)),(.70,(1,1,1))]);density=mathnode(n,l,'MULTIPLY',edge,cloud);density=mathnode(n,l,'MULTIPLY',density,.40);l.new(density,volume.inputs['Density']);l.new(volume.outputs[0],out.inputs['Volume'])
for j,loc in enumerate([(-51.0,94.15,.50),(-51.5,94.50,.64),(-52.2,94.70,.82),(-53.0,94.85,1.0)]):ball('cylinder steam',loc,(.65+j*.12,.45+j*.10,.30+j*.12),steam)
# Replace artificial uniform illumination with a photographed winter environment plus a restrained sun.
world=bpy.data.worlds.new('REAL winter industrial evening');world.use_nodes=True;n=world.node_tree.nodes;l=world.node_tree.links;n.clear();out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');env=n.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(ROOT/'assets/realism/kloofendal_overcast_puresky_2k.hdr'));env.image.pack();env.projection='EQUIRECTANGULAR'
coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=math.radians(105);l.new(coord.outputs['Generated'],mapping.inputs['Vector']);l.new(mapping.outputs[0],env.inputs['Vector']);l.new(env.outputs['Color'],bg.inputs[0]);bg.inputs['Strength'].default_value=.75;l.new(bg.outputs[0],out.inputs[0]);bpy.context.scene.world=world
for ob in bpy.data.objects:
    if ob.type=='LIGHT':
        if ob.data.type=='SUN':
            ob.data.energy=1.6;ob.data.angle=math.radians(2.0);ob.data.color=(1,.85,.66);ob.rotation_euler=Vector((25,-20,-30)).to_track_quat('-Z','Y').to_euler()
        elif any(k in ob.name for k in ('bounce','Skylight','Portrait')):ob.data.energy*=.32
# A large roof aperture light approximates the actual open sky contribution at the train, not a camera flash.
data=bpy.data.lights.new('REAL roof sky bounce','AREA');data.shape='RECTANGLE';data.size=18;data.size_y=8;data.energy=1800;data.color=(.62,.76,1)
ob=bpy.data.objects.new(data.name,data);col.objects.link(ob);ob.location=(-47,94,15);ob.rotation_euler=(0,0,0)
# Construction joints, bolt heads and service labels on columns within the hero bay.
for x in (-64.2857,-38.5714):
    for y in (92,):
        for k in range(8):
            a=k*math.pi/4;cyl('column holding-down bolt',(x+.31*math.cos(a),y+.31*math.sin(a),.78),.023,.07,steel,segments=6)
        box('iron access plate',(x,y+.245,1.4),(.18,.012,.27),iron,.002)
        for dx in (-.07,.07):
            for z in (1.29,1.51):cyl('access plate screw',(x+dx,y+.26,z),.008,.016,steel,'Y',6)
# Hero cameras: photographer-like height, no blur to conceal unresolved geometry.
for ob in list(bpy.data.objects):
    if ob.name.startswith('REALVIEW_'):bpy.data.objects.remove(ob,do_unlink=True)
views=[('01_arrival_after_rain',(-61,98,2.55),(-49.5,93.7,2.25),40),('02_oil_steel_and_spokes',(-49.0,97.0,1.44),(-46.5,93.9,1.25),48),('03_winter_travellers',(-48.2,99.6,2.2),(-45.4,96.7,2.05),42),('04_glass_iron_and_distance',(-69,97.8,2.5),(-39,96.0,4.5),32),('05_coach_at_platform',(-5,99,2.25),(9,93,2.4),38),('06_electric_and_contact_wire',(-75,69,2.3),(-67,64,3.4),38)]
for name,loc,target,lens in views:
    data=bpy.data.cameras.new('REALVIEW_'+name);data.lens=lens;data.clip_start=.035;data.clip_end=400;data.dof.use_dof=False
    ob=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
from realism_hardware import add as add_hardware
add_hardware(globals())
# Batch small static construction detail by material, keeping volumes separate.
from collections import defaultdict
groups=defaultdict(list)
for ob in parts:
    if ob.type=='MESH' and ob.data.materials and ob.data.materials[0]!=steam:groups[ob.data.materials[0].name].append(ob)
bpy.ops.object.select_all(action='DESELECT')
for name,objects in groups.items():
    if len(objects)<2:continue
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];objects[0].data=objects[0].data.copy();bpy.ops.object.join();bpy.context.object.name='REAL_BATCH_'+name;bpy.ops.object.select_all(action='DESELECT')
# Tangent frame for scanned normal maps, using dominant-face world projection on authored meshes.
for ob in bpy.data.objects:
    if ob.type!='MESH' or ob.data.uv_layers or not any(s.material and s.material.name.startswith('REAL') for s in ob.material_slots):continue
    uv=ob.data.uv_layers.new(name='Physical projection');me=ob.data
    for p in me.polygons:
        normal=p.normal;axis=max(range(3),key=lambda i:abs(normal[i]));a,c=(1,2) if axis==0 else (0,2) if axis==1 else (0,1)
        for li in p.loop_indices:
            co=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[a],co[c])
scene=bpy.context.scene;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.1
scene.use_nodes=False;scene.render.use_compositing=False
scene.cycles.use_denoising=False;scene.cycles.samples=128;scene.cycles.use_fast_gi=False;scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=8;scene.cycles.volume_bounces=1
scene.world.cycles.sampling_method='MANUAL';scene.world.cycles.sample_map_resolution=256
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.cycles.use_light_tree=True;scene.cycles.sample_clamp_direct=0;scene.cycles.sample_clamp_indirect=10
scene.camera=bpy.data.objects.get('REALVIEW_01_arrival_after_rain')
scene['realism_status']='work in progress; requires actual rendered visual inspection'
scene['external_texture_attribution']='assets/realism/PROVENANCE.json (CC0 Poly Haven); scanned humans CC BY 4.0 attribution unchanged'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_REALISM.blend'),compress=True)
print('REALISM SCENE SAVED',len(bpy.data.objects),'objects;',len(bpy.data.images),'images. NOT VISUAL ACCEPTANCE.',flush=True)
