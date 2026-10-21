"""District construction kernel. Metres; flat fabrication faces; deterministic batches."""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
class District:
 def __init__(self):
  self.groups={};self.transform=Matrix.Identity(4);self.zone='PUBLIC';self.count=defaultdict(int);self.records=[];self.materials={};self.master={}
  self.col=bpy.data.collections.new('DISTRICT');bpy.context.scene.collection.children.link(self.col)
 def location(self,x=0,y=0,z=0,angle=0):self.transform=Matrix.Translation((x,y,z))@Matrix.Rotation(angle,4,'Z')
 def mesh(self,name,verts,faces,mat,smooth=False):
  key=(self.zone,mat.name,smooth)
  if key not in self.groups:self.groups[key]=[[],[]]
  v,f=self.groups[key];n=len(v);v.extend(tuple(self.transform@Vector(p)) for p in verts);f.extend(tuple(n+i for i in p) for p in faces);self.count[name]+=1
 def box(self,name,loc,size,mat,angle=0):
  sx,sy,sz=[v/2 for v in size];R=Matrix.Rotation(angle,3,'Z');p=Vector(loc)
  v=[p+R@Vector((a*sx,b*sy,c*sz)) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
  self.mesh(name,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat)
 def beam(self,name,a,b,w,mat):
  a,b=Vector(a),Vector(b);d=b-a;R=d.to_track_quat('Z','Y').to_matrix();p=(a+b)*.5
  vv=[p+R@Vector((u*w/2,v*w/2,t*d.length/2)) for u,v,t in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
  self.mesh(name,vv,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat)
 def cyl(self,name,loc,r,h,mat,axis='Z',N=12):
  R=Matrix.Identity(3) if axis=='Z' else Matrix.Rotation(math.pi/2,3,'Y' if axis=='X' else 'X');p=Vector(loc);v=[]
  for z in (-h/2,h/2):
   for i in range(N):v.append(p+R@Vector((r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)))
  self.mesh(name,v,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],mat)
 def sphere(self,name,loc,size,mat,N=12,M=6):
  v=[]
  for j in range(M+1):
   a=math.pi*j/M
   for i in range(N):
    t=math.tau*i/N;v.append((loc[0]+size[0]*math.sin(a)*math.cos(t),loc[1]+size[1]*math.sin(a)*math.sin(t),loc[2]+size[2]*math.cos(a)))
  f=[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(M) for i in range(N)];self.mesh(name,v,f,mat,True)
 def ring(self,name,loc,r,tube,mat,axis='Z',N=40,M=6):
  v=[];p=Vector(loc);R=Matrix.Identity(3) if axis=='Z' else Matrix.Rotation(math.pi/2,3,'Y' if axis=='X' else 'X')
  for i in range(N):
   a=i*math.tau/N
   for j in range(M):
    b=j*math.tau/M;v.append(p+R@Vector(((r+tube*math.cos(b))*math.cos(a),(r+tube*math.cos(b))*math.sin(a),tube*math.sin(b))))
  self.mesh(name,v,[(i*M+j,((i+1)%N)*M+j,((i+1)%N)*M+(j+1)%M,i*M+(j+1)%M) for i in range(N) for j in range(M)],mat,True)
 def text(self,name,body,loc,size,mat,rot=(math.pi/2,0,math.pi)):
  cu=bpy.data.curves.new('DIST_'+name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.0006;cu.materials.append(mat)
  ob=bpy.data.objects.new('DIST_'+self.zone+'_'+name,cu);self.col.objects.link(ob);ob.matrix_world=self.transform@Matrix.Translation(loc)@__import__('mathutils').Euler(rot).to_matrix().to_4x4();self.count['lettered signs']+=1;return ob
 def flush(self):
  for (zone,mat,smooth),(v,f) in self.groups.items():
   me=bpy.data.meshes.new('District '+zone+' '+mat);me.from_pydata(v,[],f);me.materials.append(bpy.data.materials[mat]);me.update()
   for p in me.polygons:p.use_smooth=smooth
   uv=me.uv_layers.new(name='Metre projected UV')
   for p in me.polygons:
    axis=max(range(3),key=lambda i:abs(p.normal[i]));a,c=(1,2) if axis==0 else (0,2) if axis==1 else (0,1)
    for li in p.loop_indices:
     co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[a],co[c])
   ob=bpy.data.objects.new('DIST_'+zone+'_'+mat,me);self.col.objects.link(ob)
  self.groups.clear()

def material(name,color,rough=.65,metal=0,grain=.00015,emission=0):
 m=bpy.data.materials.new('District '+name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=110;tex.inputs['Detail'].default_value=3;coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs[0]);bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=grain;bump.inputs['Strength'].default_value=.2;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
 if name.startswith('plaster'):
  macro=n.new('ShaderNodeTexNoise');macro.inputs['Scale'].default_value=.62;macro.inputs['Detail'].default_value=4;l.new(coord.outputs['Object'],macro.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*(c*.76 for c in color),1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(*(c*1.08 for c in color),1);l.new(macro.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
 if emission:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
 return m

def maps(name,asset,metres,wet=False):
 m=material(name,(.2,.2,.2));n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');coord=n.new('ShaderNodeNewGeometry');mul=n.new('ShaderNodeVectorMath');mul.operation='SCALE';mul.inputs['Scale'].default_value=1/metres;l.new(coord.outputs['Position'],mul.inputs[0])
 for kind in ['diff','rough','nor_gl']:
  p=ROOT/'assets/district'/(asset+'_'+kind+'.jpg');im=bpy.data.images.load(str(p),check_existing=True);im.colorspace_settings.name='sRGB' if kind=='diff' else 'Non-Color';im.pack();t=n.new('ShaderNodeTexImage');t.image=im;t.projection='BOX';t.projection_blend=.15;l.new(mul.outputs[0],t.inputs[0])
  if kind=='diff':l.new(t.outputs[0],bs.inputs['Base Color'])
  elif kind=='rough':
   if wet:
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.64,.64,.64,1);l.new(t.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],bs.inputs['Roughness']);bs.inputs['Coat Weight'].default_value=.1
   else:l.new(t.outputs[0],bs.inputs['Roughness'])
  else:
   normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.3;l.new(t.outputs[0],normal.inputs['Color']);l.new(normal.outputs[0],bs.inputs['Normal'])
 return m

def palette():
 p={}
 for k,c,r,me in [('iron',(.023,.035,.031),.56,.6),('bronze',(.13,.085,.033),.4,.75),('stone',(.38,.32,.23),.82,0),('mortar',(.12,.115,.09),.94,0),('wood',(.12,.056,.024),.66,0),('darkwood',(.037,.020,.012),.58,0),('cream',(.65,.57,.39),.73,0),('red',(.26,.024,.018),.4,.15),('green',(.025,.095,.055),.47,.1),('blue',(.025,.05,.07),.48,.1),('black',(.008,.009,.008),.78,0),('paper',(.58,.5,.34),.9,0),('rail',(.29,.31,.33),.24,.9),('leaf',(.045,.085,.018),.82,0),('soil',(.046,.031,.018),1,0),('fruitred',(.36,.018,.012),.4,0),('fruitgold',(.55,.29,.015),.49,0)]:p[k]=material(k,c,r,me)
 p['cobble']=maps('weathered granite setts','cobblestone_square',1.65,True);p['paving']=maps('worn pedestrian paving','floor_pavement',2.4,True);p['roof']=maps('aged slate roof','roof_slates_02',2.4)
 p['glass']=material('window glass',(.88,.93,.93),.055,0,.00001);bs=p['glass'].node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.46
 nt=p['glass'].node_tree;n=nt.nodes;l=nt.links;out=n.get('Material Output');ray=n.new('ShaderNodeLightPath');tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(ray.outputs['Is Shadow Ray'],mix.inputs[0]);l.new(bs.outputs[0],mix.inputs[1]);l.new(tr.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
 p['marble']=material('veined cafe marble',(.55,.52,.45),.32,0,.00005)
 nt=p['marble'].node_tree;n=nt.nodes;l=nt.links;bs=n.get('Principled BSDF');coord=n.new('ShaderNodeTexCoord');wave=n.new('ShaderNodeTexWave');wave.inputs['Scale'].default_value=7;wave.inputs['Distortion'].default_value=12;wave.inputs['Detail Scale'].default_value=1.2;l.new(coord.outputs['Object'],wave.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.38;r.color_ramp.elements[0].color=(.55,.52,.45,1);r.color_ramp.elements[1].position=.47;r.color_ramp.elements[1].color=(.24,.25,.22,1);e=r.color_ramp.elements.new(.55);e.color=(.55,.52,.45,1);l.new(wave.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],bs.inputs['Base Color'])
 p['lamp']=material('warm porcelain light',(1,.58,.22),.3,0,0,3);p['water']=material('fountain water',(.055,.09,.075),.075,.22,.0001);p['linen']=material('unbleached linen',(.41,.33,.21),.9,0,.0002)
 p['plaster']=[material('plaster '+str(i),c,.86,0,.00065) for i,c in enumerate([(.42,.32,.20),(.30,.24,.17),(.48,.42,.31),(.23,.29,.27),(.38,.24,.18),(.43,.39,.29),(.27,.30,.32),(.39,.37,.31)])]
 return p
