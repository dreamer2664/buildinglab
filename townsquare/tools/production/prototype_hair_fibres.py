"""UNSAVED quality study only: actual geometric fine hair, never painted/generated-image substitute.
Frozen source/production output untouched. Must inspect actual native-pixel crop before adoption.
"""
import bpy,math,random,bisect
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def apply():
 rng=random.Random(6117);s=bpy.context.scene;result=[]
 for o in list(s.objects):
  if o.type!='MESH' or not o.get('person_id'):continue
  mesh=o.data;slots={i for i,m in enumerate(mesh.materials)if m and any(x in m.name.lower()for x in ['braid01','ponytail','bob02','short01','short02'])}
  if not slots:continue
  mesh.calc_loop_triangles();tris=[t for t in mesh.loop_triangles if t.material_index in slots];coords=[v.co.copy()for v in mesh.vertices];indices=[tuple(t.vertices)for t in tris];uv=mesh.uv_layers.active;uvs=[[uv.data[i].uv.copy()for i in t.loops]for t in tris];bvh=BVHTree.FromPolygons(coords,indices,all_triangles=True);weights=[];total=0
  for t in tris:total+=t.area;weights.append(total)
  directions=[]
  for t,tex in zip(tris,uvs):
   a,b,c=[coords[i]for i in t.vertices];d1,d2=tex[1]-tex[0],tex[2]-tex[0];det=d1.x*d2.y-d1.y*d2.x;v=((c-a)*d1.x-(b-a)*d2.x)/det if abs(det)>1e-10 else Vector((0,0,-1));n=t.normal;v=v-n*v.dot(n)
   if v.length<1e-6:v=n.cross(Vector((1,0,0)))
   v.normalize()
   if v.z>0:v=-v
   directions.append(v)
  for i in slots:
   m=mesh.materials[i];bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   for link in list(bs.inputs['Base Color'].links):m.node_tree.links.remove(link)
   bs.inputs['Base Color'].default_value=(.012,.006,.0035,1);bs.inputs['Roughness'].default_value=.75
  curve=bpy.data.curves.new('STUDY_REAL_GEOMETRIC_FINE_FIBRES','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=.00011;curve.bevel_resolution=0;curve.resolution_u=1
  for j in range(5):
   m=bpy.data.materials.new('STUDY_FIBRE_PBR_'+str(j));m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');v=.65+j*.2;bs.inputs['Base Color'].default_value=(.019*v,.009*v,.0045*v,1);bs.inputs['Roughness'].default_value=.43;bs.inputs['Anisotropic'].default_value=.8;curve.materials.append(m)
  count=12000
  for z in range(count):
   i=min(len(tris)-1,bisect.bisect_left(weights,rng.random()*total));a,b,c=[coords[k]for k in indices[i]];u,v=rng.random(),rng.random()
   if u+v>1:u,v=1-u,1-v
   p=a+(b-a)*u+(c-a)*v;direction=directions[i];positions=[];wisp=rng.random()<.035;length=rng.uniform(.016,.042);offset=rng.uniform(.00025,.0008)
   for step in range(10):
    q,n,index,d=bvh.find_nearest(p)
    if q is None:break
    new=directions[index]
    if new.dot(direction)<0:new=-new
    direction=(direction*.35+new*.65).normalized();lift=offset+(max(0,step-5)/4)**2*(.005 if wisp else .0004);positions.append(q+n*lift);p=q+direction*(length/9)
   if len(positions)<2:continue
   sp=curve.splines.new('POLY');sp.points.add(len(positions)-1);sp.material_index=rng.randrange(5)
   for k,(point,p)in enumerate(zip(sp.points,positions)):point.co=(*p,1);point.radius=max(.08,1-k/(len(positions)-1))
  obj=bpy.data.objects.new('STUDY_FINE_FIBRES_'+o.name,curve);s.collection.objects.link(obj);obj.matrix_world=o.matrix_world.copy();obj['person_id']=o['person_id'];obj['study_only']=True;result.append({'object':o.name,'actual_splines':len(curve.splines),'radius_metres':curve.bevel_depth,'hair_source_materials':[mesh.materials[i].name for i in slots],'method':'Actual tapered tubular geometry tracks original licensed hair surface and UV fibre direction; physically varied strand colour, no new photo/paint/generation. Original cap changed to dark matte underlayer in UNSAVED study only.'})
  for m in mesh.materials:
   if not m or not m.use_nodes or not m.name.endswith('.body'):continue
   bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   if not bs.inputs['Normal'].is_linked:
    noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1100;noise.inputs['Detail'].default_value=2;bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.000065;bump.inputs['Strength'].default_value=.17;m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
   bs.inputs['Subsurface Weight'].default_value=.07;bs.inputs['Subsurface Scale'].default_value=.0011
 bpy.context.view_layer.update();return result
