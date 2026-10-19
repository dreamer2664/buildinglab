"""UNSAVED study2: smooth licensed hair mass + actual Cycles hair curves/fibre BSDF.
No image painting/generation, no native resave; not production adoption.
"""
import bpy,math,random,bisect,os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

def apply():
 rng=random.Random(6117);s=bpy.context.scene;result=[];templates={};geometry_cache={}
 for o in list(s.objects):
  if o.type!='MESH' or not o.get('person_id'):continue
  mesh=o.data;cache_key=mesh.as_pointer()
  if cache_key in geometry_cache:
   oldcap,oldhair=geometry_cache[cache_key]
   for old in [oldcap,oldhair]:
    new=old.copy();new.data=old.data;s.collection.objects.link(new);new.matrix_world=o.matrix_world.copy();new['person_id']=o['person_id'];new['layer']='people_hair';new['study_only']=True
   result.append({'object':o.name,'shared_hair_geometry_from':oldhair.name,'actual_native_hair_curves':len(oldhair.data.curves),'method':'Actual shared original mesh-data group; new curve/cap objects follow this actor matrix. Native source unchanged.'});continue
  slots=[i for i,m in enumerate(mesh.materials)if m and any(x in m.name.lower()for x in ['braid01','ponytail','bob01','bob02','short01','short02','afro01'])]
  if not slots:continue
  afro=any('afro01' in mesh.materials[i].name.lower()for i in slots)
  polys=[p for p in mesh.polygons if p.material_index in slots];used=sorted({v for p in polys for v in p.vertices});remap={old:new for new,old in enumerate(used)};cap=bpy.data.meshes.new('STUDY_SMOOTH_LICENSED_HAIR_SURFACE');cap.from_pydata([mesh.vertices[v].co.copy()for v in used],[],[[remap[v]for v in p.vertices]for p in polys]);cap.update();nape_smoothed=0
  if os.environ.get('SQUARE_HAIR_NAPE_SMOOTH')=='1'and any('braid01'in mesh.materials[i].name.lower()for i in slots):
   a=np.array([tuple(v.co)for v in cap.vertices]);lo=a.min(axis=0);hi=a.max(axis=0);selected=np.where((a[:,1]>lo[1]+.65*(hi[1]-lo[1]))&(a[:,2]<lo[2]+.38*(hi[2]-lo[2])))[0];adj=[set()for v in cap.vertices]
   for e in cap.edges:u,v=e.vertices;adj[u].add(v);adj[v].add(u)
   for iteration in range(18):
    old=a.copy()
    for v in selected:
     if adj[v]:a[v]=old[v]*.55+old[list(adj[v])].mean(axis=0)*.45
   for v in selected:cap.vertices[v].co=a[v]
   cap.update();nape_smoothed=len(selected)
  uv=cap.uv_layers.new(name='UVMap');old_uv=mesh.uv_layers.active
  for src,dst in zip(polys,cap.polygons):
   dst.use_smooth=True;dst.material_index=slots.index(src.material_index)
   for a,b in zip(src.loop_indices,dst.loop_indices):uv.data[b].uv=old_uv.data[a].uv
  for i in slots:
   original=mesh.materials[i]
   if original.name not in templates:templates[original.name]=original.copy()
   m=templates[original.name].copy();m.name='STUDY_MATTE_HAIR_UNDERLAYER_'+original.name;cap.materials.append(m);bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   for link in list(bs.inputs['Base Color'].links):m.node_tree.links.remove(link)
   bs.inputs['Base Color'].default_value=(.0045,.0022,.0012,1);bs.inputs['Roughness'].default_value=.95;bs.inputs['Specular IOR Level'].default_value=.08
   # Explicit replacement of source hair surface in unsaved study, not concealed by camera.
   bs=next(n for n in original.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   for link in list(bs.inputs['Alpha'].links):original.node_tree.links.remove(link)
   bs.inputs['Alpha'].default_value=0
  capobj=bpy.data.objects.new('STUDY_SMOOTH_HAIR_MASS_'+o.name,cap);s.collection.objects.link(capobj);capobj.matrix_world=o.matrix_world.copy();sub=capobj.modifiers.new('Actual hair-surface silhouette refinement','SUBSURF');sub.levels=2;sub.render_levels=2;bpy.context.view_layer.update();ev=capobj.evaluated_get(bpy.context.evaluated_depsgraph_get());work=bpy.data.meshes.new_from_object(ev);work.calc_loop_triangles();tris=list(work.loop_triangles);coords=[v.co.copy()for v in work.vertices];indices=[tuple(t.vertices)for t in tris];uv=work.uv_layers.active;bvh=BVHTree.FromPolygons(coords,indices,all_triangles=True);weights=[];total=0;directions=[]
  for t in tris:
   total+=t.area;weights.append(total);a,b,c=[coords[i]for i in t.vertices];tex=[uv.data[i].uv for i in t.loops];d1,d2=tex[1]-tex[0],tex[2]-tex[0];det=d1.x*d2.y-d1.y*d2.x
   # Follow U, correcting the transverse groove-like V orientation rejected in study1.
   v=((b-a)*d2.y-(c-a)*d1.y)/det if abs(det)>1e-10 else Vector((0,0,-1));n=t.normal;v=v-n*v.dot(n)
   if v.length<1e-6:v=n.cross(Vector((1,0,0)))
   v.normalize()
   if v.z>0:v=-v
   directions.append(v)
  masks={};tri_uvs=[[Vector((uv.data[j].uv.x,uv.data[j].uv.y,0))for j in t.loops]for t in tris]
  for mi,m in enumerate(cap.materials):
   bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');links=bs.inputs['Alpha'].links
   if links and links[0].from_node.type=='TEX_IMAGE':
    im=links[0].from_node.image;w,h=im.size;channels=im.channels
    if channels==4 and w and h:
     a=np.empty(w*h*channels,dtype=np.float32);im.pixels.foreach_get(a);masks[mi]=(w,h,a.reshape(h,w,channels)[:,:,3].copy());del a
  def visible(index,p,threshold):
   mask=masks.get(tris[index].material_index)
   if mask is None:return True
   a,b,c=[coords[j]for j in indices[index]];t=barycentric_transform(p,a,b,c,*tri_uvs[index]);w,h,alpha=mask
   if t.x<0 or t.x>1 or t.y<0 or t.y>1:return False
   return alpha[min(h-1,int(t.y*h)),min(w-1,int(t.x*w))]>=threshold
  points=[];radii=[];counts=[];count=32000
  for z in range(count):
   i=min(len(tris)-1,bisect.bisect_left(weights,rng.random()*total));a,b,c=[coords[k]for k in indices[i]];u,v=rng.random(),rng.random()
   if u+v>1:u,v=1-u,1-v
   p=a+(b-a)*u+(c-a)*v
   if not visible(i,p,.65):continue
   direction=directions[i];positions=[];wisp=rng.random()<.025;length=rng.uniform(.012,.025)if afro else rng.uniform(.018,.048);offset=rng.uniform(.0012,.0016)if afro else rng.uniform(.00015,.00055);phase=rng.random()*math.tau
   for step in range(10):
    q,n,index,d=bvh.find_nearest(p)
    if q is None or not visible(index,q,.5):break
    new=directions[index]
    if new.dot(direction)<0:new=-new
    direction=(direction*.4+new*.6).normalized();lift=offset+(max(0,step-5)/4)**2*(.004 if wisp else .0003);point=q+n*lift
    if afro:
     side=direction.cross(n).normalized();radius=.00075*math.sin(math.pi*step/9);theta=phase+step*math.tau*.34;point+=n*radius*math.cos(theta)+side*radius*math.sin(theta)
    positions.append(point);p=q+direction*(length/9)
   if len(positions)<2:continue
   counts.append(len(positions))
   for k,p in enumerate(positions):points.extend(p);radii.append(.000045*max(.04,1-k/(len(positions)-1)))
  hair=bpy.data.hair_curves.new('STUDY_ACTUAL_CYCLES_HAIR_FIBRES');hair.add_curves(counts);hair.attributes['position'].data.foreach_set('vector',np.array(points,dtype=np.float32));radius=hair.attributes.new('radius','FLOAT','POINT');radius.data.foreach_set('value',np.array(radii,dtype=np.float32));m=bpy.data.materials.new('STUDY_ACTUAL_ABSORPTION_HAIR_BSDF');m.use_nodes=True;tree=m.node_tree;tree.nodes.clear();bs=tree.nodes.new('ShaderNodeBsdfHairPrincipled');bs.parametrization='MELANIN';bs.inputs['Melanin'].default_value=.86;bs.inputs['Melanin Redness'].default_value=.2;bs.inputs['Roughness'].default_value=.38;bs.inputs['Radial Roughness'].default_value=.32;bs.inputs['Random Color'].default_value=.08;bs.inputs['Random Roughness'].default_value=.12;output=tree.nodes.new('ShaderNodeOutputMaterial');tree.links.new(bs.outputs[0],output.inputs['Surface']);hair.materials.append(m);obj=bpy.data.objects.new('STUDY_REAL_HAIR_CURVES_'+o.name,hair);s.collection.objects.link(obj);obj.matrix_world=o.matrix_world.copy();obj['person_id']=o['person_id'];obj['study_only']=True;result.append({'object':o.name,'actual_native_hair_curves':len(counts),'actual_curve_points':len(radii),'root_radius_metres':.000045,'hair_mass_subdivision':2,'original_alpha_masks_respected':len(masks),'actual_curly_fibre_variant':afro,'actual_braid_nape_surface_vertices_locally_smoothed':nape_smoothed,'method':'Actual hair curves with tapered radius and physical melanin absorption fibre BSDF over smoothed licensed hair mass, not geometric-tube/groove or new texture/image. UNSAVED study only; no native/model/archive mutation.'});geometry_cache[cache_key]=(capobj,obj);capobj['person_id']=o['person_id'];capobj['layer']='people_hair';obj['layer']='people_hair';bpy.data.meshes.remove(work)
 bpy.context.view_layer.update();return result
