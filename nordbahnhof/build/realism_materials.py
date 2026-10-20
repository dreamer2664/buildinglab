"""Physically scaled material overhaul. CC0 scanned maps, restrained wear, no image stand-ins."""
import bpy,math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'assets/realism'
manifest=json.loads((ASSET/'PROVENANCE.json').read_text())

def scanned(asset,kind):
    e=next(x for x in manifest if x['asset']==asset and x['map']==kind)
    im=bpy.data.images.load(str(ASSET/e['file']),check_existing=True)
    im.colorspace_settings.name='sRGB' if kind=='Diffuse' else 'Non-Color'
    if not im.packed_file:im.pack()
    return im

def newmat(name):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    m.node_tree.nodes.clear();nt=m.node_tree;n=nt.nodes;l=nt.links
    out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');l.new(bs.outputs[0],out.inputs['Surface'])
    return m,n,l,bs

def node(n,kind,**inputs):
    o=n.new(kind)
    for name,val in inputs.items():o.inputs[name.replace('_',' ')].default_value=val
    return o

def mathnode(n,l,op,a,b):
    o=n.new('ShaderNodeMath');o.operation=op
    for idx,v in enumerate((a,b)):
        if isinstance(v,(int,float)):o.inputs[idx].default_value=v
        else:l.new(v,o.inputs[idx])
    return o.outputs[0]
def ramp(n,l,value,stops):
    o=n.new('ShaderNodeValToRGB');r=o.color_ramp
    while len(r.elements)>2:r.elements.remove(r.elements[-1])
    for i,(pos,color) in enumerate(stops):
        e=r.elements[i] if i<2 else r.elements.new(pos);e.position=pos;e.color=(*color,1)
    l.new(value,o.inputs[0]);return o.outputs['Color']
def worldvec(n,l,scale):
    g=n.new('ShaderNodeNewGeometry');v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=scale;l.new(g.outputs['Position'],v.inputs[0]);return v.outputs['Vector']
def noise(n,l,vec,scale,detail=3):
    o=n.new('ShaderNodeTexNoise');o.inputs['Scale'].default_value=scale;o.inputs['Detail'].default_value=detail;o.inputs['Roughness'].default_value=.7;l.new(vec,o.inputs[0]);return o.outputs['Fac']
def texture(n,l,asset,kind,vec):
    t=n.new('ShaderNodeTexImage');t.image=scanned(asset,kind);t.projection='BOX';t.projection_blend=.22;t.extension='REPEAT';l.new(vec,t.inputs['Vector']);return t.outputs['Color']
def mixcolor(n,l,a,b,fac,blend='MIX'):
    o=n.new('ShaderNodeMixRGB');o.blend_type=blend
    for i,v in enumerate((fac,a,b)):
        if isinstance(v,(int,float)):o.inputs[i].default_value=v
        elif isinstance(v,tuple):o.inputs[i].default_value=(*v,1) if len(v)==3 else v
        else:l.new(v,o.inputs[i])
    return o.outputs['Color']

def painted(name,base,asset='rusty_painted_metal',scale=1.5,rough=.40,exposed=False):
    m,n,l,bs=newmat(name);vec=worldvec(n,l,(1/scale,)*3)
    # A photographed surface is used for subtle colour/roughness variation, not pasted rust everywhere.
    photo=noise(n,l,worldvec(n,l,(2,2,.35)),9,3) if exposed else texture(n,l,asset,'Diffuse',vec)
    luminosity=n.new('ShaderNodeRGBToBW');l.new(photo,luminosity.inputs[0])
    albedo=ramp(n,l,luminosity.outputs[0],[(.0,tuple(c*.55 for c in base)),(.85,tuple(c*1.20 for c in base))])
    pos=worldvec(n,l,(1,1,1));macro=noise(n,l,pos,1.2)
    fine=noise(n,l,pos,350,2)
    streakvec=worldvec(n,l,(8,8,.25));streak=noise(n,l,streakvec,3)
    dirtmask=ramp(n,l,streak,[(.52,(0,0,0)),(.79,(.45,.45,.45))])
    color=mixcolor(n,l,albedo,(.038,.027,.017),dirtmask)
    l.new(color,bs.inputs['Base Color'])
    roughphoto=noise(n,l,worldvec(n,l,(2,2,.35)),14,3) if exposed else texture(n,l,asset,'Rough',vec)
    roughout=ramp(n,l,roughphoto,[(.05,(max(.10,rough-.16),)*3),(.9,(min(.9,rough+.22),)*3)])
    l.new(roughout,bs.inputs['Roughness'])
    bs.inputs['Metallic'].default_value=.88 if exposed else .05
    if exposed:bs.inputs['Anisotropic'].default_value=.25
    bs.inputs['Coat Weight'].default_value=0 if exposed else .12
    bs.inputs['Coat Roughness'].default_value=.28
    normalmap=n.new('ShaderNodeNormalMap');normalmap.inputs['Strength'].default_value=.12
    if not exposed:l.new(texture(n,l,asset,'nor_gl',vec),normalmap.inputs['Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12 if exposed else .20;bump.inputs['Distance'].default_value=.000035 if exposed else .00016;l.new(fine,bump.inputs['Height'])
    # Tangent-space box projection must not turn turned steel into corrugated chrome.
    if not exposed:l.new(normalmap.outputs[0],bump.inputs['Normal'])
    l.new(bump.outputs[0],bs.inputs['Normal'])
    return m

def masonry(name,asset,meters=3,wet=False):
    m,n,l,bs=newmat(name);vec=worldvec(n,l,(1/meters,)*3)
    photo=texture(n,l,asset,'Diffuse',vec)
    l.new(photo,bs.inputs['Base Color'])
    rough=texture(n,l,asset,'Rough',vec)
    if wet:
        position=worldvec(n,l,(1,1,1));patch=noise(n,l,position,.85,4)
        mask=ramp(n,l,patch,[(.42,(0,0,0)),(.69,(.85,.85,.85))])
        rough=mixcolor(n,l,rough,(.085,.085,.085),mask)
        l.new(mixcolor(n,l,photo,(.18,.18,.18),mask,'MULTIPLY'),bs.inputs['Base Color'])
        bs.inputs['Coat Weight'].default_value=.22;bs.inputs['Coat Roughness'].default_value=.12
    l.new(rough,bs.inputs['Roughness'])
    nor=texture(n,l,asset,'nor_gl',vec);nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.45;l.new(nor,nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
    return m

def glassmat(name):
    m,n,l,bs=newmat(name);bs.inputs['Base Color'].default_value=(.92,.96,.94,1);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.52
    vec=worldvec(n,l,(3,3,.8));fac=noise(n,l,vec,6,3)
    rough=ramp(n,l,fac,[(.33,(.012,)*3),(.70,(.11,)*3)]);l.new(rough,bs.inputs['Roughness'])
    micro=noise(n,l,worldvec(n,l,(4,4,.15)),25,2);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.00010;l.new(micro,bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    # Transmission through thin panes must not turn the entire roof into an opaque shadow caster.
    out=next(x for x in n if x.type=='OUTPUT_MATERIAL');path=n.new('ShaderNodeLightPath');transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(path.outputs['Is Shadow Ray'],mix.inputs[0]);l.new(bs.outputs[0],mix.inputs[1]);l.new(transparent.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
    return m

def apply_materials():
    replacements={}
    specs={
    'Train weathered graphite':((.025,.030,.032),.47,False),
    'Train vermilion frame':((.28,.027,.018),.53,False),
    'Train oily underframe':((.018,.022,.023),.62,True),
    'Train machined steel':((.34,.37,.40),.30,True),
    'Train coach bottle green':((.018,.052,.038),.43,False),
    'Train coach oxblood':((.15,.025,.018),.45,False),
    'Train electric midnight blue':((.022,.043,.065),.42,False),
    'Train roof soot':((.025,.027,.023),.76,False),
    'Rebuild painted petrol iron':((.032,.052,.046),.62,False),
    'Detail blackened iron':((.017,.026,.025),.58,False),
    'Rebuild rail steel':((.29,.30,.32),.3,True),
    'MAT_Steel_RailRunningBand':((.27,.28,.30),.3,True),
    'Train muted brass':((.26,.18,.07),.43,True),
    'Detail brass':((.27,.18,.065),.45,True),
    }
    for old,(base,rgh,exposed) in specs.items():replacements[old]=painted('REAL '+old,base,'metal_plate' if exposed else 'rusty_painted_metal',1.5,rgh,exposed)
    floor=masonry('REAL worn damp stone','concrete_floor_worn_001',3,True)
    brick=masonry('REAL coal-darkened brick','brick_wall_001',1.5)
    gravel=masonry('REAL track crushed rock','gravel_floor',3)
    stone=masonry('REAL eroded limestone','concrete_floor_worn_001',3)
    # Unpainted warm stone, never the peeling green paint of the rejected floor scan.
    nt=stone.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');original=bs.inputs['Base Color'].links[0].from_socket
    nt.links.new(mixcolor(nt.nodes,nt.links,original,(.34,.30,.23),.40),bs.inputs['Base Color'])
    nt=gravel.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');original=bs.inputs['Base Color'].links[0].from_socket;bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(original,bw.inputs[0]);nt.links.new(mixcolor(nt.nodes,nt.links,bw.outputs[0],(.44,.46,.49),1,'MULTIPLY'),bs.inputs['Base Color'])
    window=glassmat('REAL 4mm imperfect glass')
    for old in ['MAT_Stone_GraniteCoping','Rebuild platform blue granite','MAT_Terrazzo_Concourse']:replacements[old]=floor
    for old in ['Rebuild soot brown brick']:replacements[old]=brick
    for old in ['Rebuild crushed dark basalt','MAT_Stone_TrackBallast']:replacements[old]=gravel
    for old in ['Rebuild limestone ashlar','MAT_Stone_SandstoneAshlar']:replacements[old]=stone
    for old in ['Train optical window glass','Rebuild thin historic glazing']:replacements[old]=window
    for ob in bpy.data.objects:
        if ob.type!='MESH':continue
        for slot in ob.material_slots:
            if slot.material and slot.material.name in replacements:slot.material=replacements[slot.material.name]
        if any(s.material==window for s in ob.material_slots):
            # Real plane normals: do not interpolate a window face with its tiny bevel.
            for p in ob.data.polygons:p.use_smooth=False
            # Real pane thickness fixes single-plane refraction.
            if ob.name.startswith('STATIC_BATCH_'):
                mod=ob.modifiers.new('Actual 4 mm glazing thickness','SOLIDIFY');mod.thickness=.004;mod.offset=0
        if ob.name.startswith('TRAIN_'):
            # set_sharp_from_angle also changes polygon shading flags in Blender 4.3.
            # Preserve the authored flat box/glass faces; otherwise every pane turns into foil.
            flat=[not p.use_smooth or len(p.vertices)>8 for p in ob.data.polygons]
            try:ob.data.set_sharp_from_angle(angle=math.radians(48))
            except Exception:pass
            for p,is_flat in zip(ob.data.polygons,flat):p.use_smooth=not is_flat
    return floor,brick,gravel,stone,replacements
