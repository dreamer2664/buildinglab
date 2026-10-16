"""Original mesh primitives / materials. Blender 4.3.2, no add-ons or asset downloads.
All dimensions metres. Editable named components; procedural PBR surface response.
"""
import bpy,math
from mathutils import Vector
from contextlib import contextmanager
COL=None; META={}; ORIGIN=Vector((0,0,0));ANGLE=0
M={}
def collection(name,parent=None,**props):
 c=bpy.data.collections.new(name);(parent or bpy.context.scene.collection).children.link(c)
 for k,v in props.items():c[k]=v
 return c
@contextmanager
def scope(c=None,origin=None,angle=0,**tags):
 global COL,META,ORIGIN,ANGLE
 old=COL,META,ORIGIN,ANGLE
 if c is not None:COL=c
 if origin is not None:ORIGIN=Vector(origin);ANGLE=angle
 META={**META,**tags}
 try:yield
 finally:COL,META,ORIGIN,ANGLE=old

def linear(h):
 return tuple(((int(h[i:i+2],16)/255+.055)/1.055)**2.4 for i in (0,2,4))+(1,)
def material(name,h,rough=.5,metal=0,trans=0,noise=0,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');col=linear(h);m.diffuse_color=col
 b.inputs['Base Color'].default_value=col;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;b.inputs['Transmission Weight'].default_value=trans
 if emission:b.inputs['Emission Color'].default_value=col;b.inputs['Emission Strength'].default_value=emission
 if noise:
  tex=m.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=70 if name in ['Linen','Upholstery','OliveFabric'] else 7
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=noise
  m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],b.inputs['Normal'])
 M[name]=m;return m

def materials():
 for args in [('Limestone','D6C7A5',.73,0,0,.02),('Plaster','F2E9DA',.78,0,0,.008),('Terracotta','B95B3F',.63,0,0,.013),('Teal','214E4E',.35,.35),('Bronze','8A7351',.3,.72),('Oak','A76C3F',.49,0,0,.008),('Walnut','66452F',.45,0,0,.006),('Terrazzo','C5BDA6',.52,0,0,.018),('Tile','749D94',.3),('Porcelain','E8E7D9',.22),('Steel','9EA5A4',.24,.85),('Black','232C2E',.38,.2),('Glass','BDD8D7',.08,0,1),('Linen','E4D7BD',.83,0,0,.007),('Upholstery','C37A50',.83,0,0,.006),('OliveFabric','7C8A62',.8,0,0,.006),('Leaf','426B3F',.8),('Soil','493D29',1),('Concrete','ADA994',.76,0,0,.02),('Paving','C5B89C',.8,0,0,.02),('Water','6CA9AC',.1,0,.45),('Paper','E3D0AD',.65),('Glow','FFE3B7',.35,0,0,0,3)]:material(*args)
 # Timber grain, generated coords; portable export falls back to PBR base colour.
 for name in ['Oak','Walnut']:
  m=M[name];nodes=m.node_tree.nodes;links=m.node_tree.links;b=nodes.get('Principled BSDF');tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=2
  coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,2,45)
  links.new(coord.outputs['Generated'],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs['Vector']);ramp=nodes.new('ShaderNodeValToRGB');c=M[name].diffuse_color
  ramp.color_ramp.elements[0].color=tuple(x*.68 for x in c[:3])+(1,);ramp.color_ramp.elements[1].color=c;links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],b.inputs['Base Color'])

def obj(name,verts,faces,mat,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o)
 o.data.materials.append(M[mat] if isinstance(mat,str) else mat)
 for k,v in META.items():o[k]=v
 if smooth:
  for p in me.polygons:p.use_smooth=True
 return o

def place(o,p,rz=0):
 x,y,z=p;c=math.cos(ANGLE);s=math.sin(ANGLE);o.location=ORIGIN+Vector((c*x-s*y,s*x+c*y,z));o.rotation_euler.z=ANGLE+rz;return o

def box(name,p,size,mat='Oak',r=0,rz=0):
 x,y,z=(n/2 for n in size);v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)];f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];o=place(obj(name,v,f,mat),p,rz)
 if r:
  m=o.modifiers.new('Rounded joinery','BEVEL');m.width=r;m.segments=3
  m=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def lathe(name,p,profile,mat='Porcelain',n=24,rz=0):
 v=[]
 for radius,z in profile:
  v += [(radius*math.cos(i*2*math.pi/n),radius*math.sin(i*2*math.pi/n),z) for i in range(n)]
 f=[]
 for j in range(len(profile)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
 f.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);return place(obj(name,v,f,mat,True),p,rz)

def cylinder(name,p,r,depth,mat='Steel',n=20):return lathe(name,p,[(r,-depth/2),(r,depth/2)],mat,n)
def sphere(name,p,size,mat='Linen',n=16,m=10):
 v=[]
 for j in range(m+1):
  a=-math.pi/2+j*math.pi/m
  for i in range(n):b=i*2*math.pi/n;v.append((size[0]/2*math.cos(a)*math.cos(b),size[1]/2*math.cos(a)*math.sin(b),size[2]/2*math.sin(a)))
 f=[]
 for j in range(m):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
 return place(obj(name,v,f,mat,True),p)

def rod(name,a,b,r=.018,mat='Steel',n=10):
 direction=Vector(b)-Vector(a);length=direction.length;v=[]
 for z in [-length/2,length/2]:v.extend([(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n)])
 f=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=obj(name,v,f,mat,True);mid=(Vector(a)+Vector(b))/2;c=math.cos(ANGLE);s=math.sin(ANGLE);o.location=ORIGIN+Vector((c*mid.x-s*mid.y,s*mid.x+c*mid.y,mid.z))
 rot=direction.to_track_quat('Z','Y').to_matrix().to_4x4();from mathutils import Matrix
 o.rotation_euler=(Matrix.Rotation(ANGLE,4,'Z')@rot).to_euler();return o

def torus(name,p,r=.2,tube=.015,mat='Bronze',axis='Z'):
 v=[];f=[];n=24;m=8
 for i in range(n):
  a=i*math.tau/n
  for j in range(m):
   b=j*math.tau/m;q=((r+tube*math.cos(b))*math.cos(a),(r+tube*math.cos(b))*math.sin(a),tube*math.sin(b))
   v.append(q if axis=='Z' else (q[0],q[2],q[1]))
 for i in range(n):
  for j in range(m):f.append((i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m))
 return place(obj(name,v,f,mat,True),p)

def camera(name,pos,target,lens=30,ortho=0):
 data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.clip_start=.08;data.clip_end=300;data.lens=lens
 if ortho:data.type='ORTHO';data.ortho_scale=ortho
 return o

def light(name,p,energy=100,size=1,color=(1,.87,.7),target=None):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);COL.objects.link(o);place(o,p)
 if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 for k,v in META.items():o[k]=v
 return o

# Original single-stroke signage avoids external/bundled font licensing dependencies.
GLYPHS={'0':[(0,0),(0,1),(.6,1),(.6,0),(0,0)],'1':[(.15,.8),(.3,1),(.3,0)],'2':[(0,1),(.6,1),(.6,.5),(0,.5),(0,0),(.6,0)],'3':[(0,1),(.6,1),(.6,0),(0,0),(.6,.5),(0,.5)],'4':[(0,1),(0,.5),(.6,.5),(.6,1),(.6,0)],'5':[(.6,1),(0,1),(0,.5),(.6,.5),(.6,0),(0,0)],'6':[(.6,1),(0,1),(0,0),(.6,0),(.6,.5),(0,.5)],'L':[(0,1),(0,0),(.6,0)],'A':[(0,0),(.3,1),(.6,0),(.45,.5),(.15,.5)],'B':[(0,0),(0,1),(.5,1),(.6,.75),(.5,.5),(0,.5),(.5,.5),(.6,.25),(.5,0),(0,0)],'C':[(.6,1),(0,1),(0,0),(.6,0)],'E':[(.6,1),(0,1),(0,0),(.6,0),(0,0),(0,.5),(.5,.5)],'F':[(0,0),(0,1),(.6,1),(0,1),(0,.5),(.5,.5)],'G':[(.6,1),(0,1),(0,0),(.6,0),(.6,.5),(.3,.5)],'I':[(.3,0),(.3,1)],'T':[(0,1),(.6,1),(.3,1),(.3,0)],'X':[(0,0),(.6,1),(.3,.5),(0,1),(.6,0)],'N':[(0,0),(0,1),(.6,0),(.6,1)],'O':[(0,0),(0,1),(.6,1),(.6,0),(0,0)],'R':[(0,0),(0,1),(.6,1),(.6,.5),(0,.5),(.6,0)],'S':[(.6,1),(0,1),(0,.5),(.6,.5),(.6,0),(0,0)],'P':[(0,0),(0,1),(.6,1),(.6,.5),(0,.5)],'M':[(0,0),(0,1),(.3,.5),(.6,1),(.6,0)],'D':[(0,0),(0,1),(.4,1),(.6,.8),(.6,.2),(.4,0),(0,0)],'U':[(0,1),(0,0),(.6,0),(.6,1)],'W':[(0,1),(.15,0),(.3,.5),(.45,0),(.6,1)]}
def sign(name,body,p,size=.18,mat='Bronze',plane='XZ'):
 x,y,z=p
 for j,ch in enumerate(body.upper()):
  line=GLYPHS.get(ch,[])
  for a,b in zip(line,line[1:]):
   def q(v):
    xx=x+(j*.85+v[0])*size
    return (xx,y,z+v[1]*size) if plane=='XZ' else (xx,y+v[1]*size,z)
   rod(name+'_'+ch,q(a),q(b),size*.035,mat,6)
