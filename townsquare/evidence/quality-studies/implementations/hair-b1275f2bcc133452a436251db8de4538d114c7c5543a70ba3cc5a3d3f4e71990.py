"""UNSAVED physical scalp groom2. Continuous clipped/feathered hairline, ears clear, rotational flow.
No altered anatomy/face/photo/lighting, no native save, no quality acceptance from successful render.
"""
import bpy,random,math,bisect,os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 result=[];rng=random.Random(171061)
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH'or not o.get('person_id'):continue
  mesh=o.data;hairslots={i for i,m in enumerate(mesh.materials)if m and'braid01'in m.name.lower()};skinslots={i for i,m in enumerate(mesh.materials)if m and(m.name.endswith('.body')or'.body.'in m.name)}
  if not hairslots:continue
  assert skinslots;mesh.calc_loop_triangles();coords=[v.co.copy()for v in mesh.vertices];skintris=[t for t in mesh.loop_triangles if t.material_index in skinslots];skinverts={v for t in skintris for v in t.vertices};top=max(coords[i].z for i in skinverts);ring=[coords[i]for i in skinverts if top-.10<coords[i].z<top-.045];cy=(min(p.y for p in ring)+max(p.y for p in ring))/2;cx=(min(p.x for p in ring)+max(p.x for p in ring))/2;hw=max(abs(coords[i].x-cx)for i in skinverts if coords[i].z>top-.18);earpts=[coords[i]for i in skinverts if abs(coords[i].x-cx)>hw*.91 and top-.20<coords[i].z<top-.065];ear_y=sum(p.y for p in earpts)/len(earpts);ear_z=sum(p.z for p in earpts)/len(earpts)
  def mask(p):
   theta=abs(math.atan2(p.x-cx,p.y-cy));depth=.17-.095*smooth((theta-.60)/1.65);d=p.z-(top-depth)
   # Keep actual outer ear cartilage bare, not covered in scalp material/curves.
   if abs(p.x-cx)>hw*.74:
    e=(math.sqrt(((p.y-ear_y)/.031)**2+((p.z-ear_z)/.040)**2)-1)*.03;d=min(d,e)
   return d
  roots=[];capverts=[];capnormals=[];capfaces=[];fades=[];weights=[];total=0
  for t in skintris:
   poly=[(coords[i].copy(),mesh.vertices[i].normal.copy(),mask(coords[i]))for i in t.vertices];clipped=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    if a[2]>=0:clipped.append(a)
    if(a[2]>=0)!=(b[2]>=0):
     f=a[2]/(a[2]-b[2]);clipped.append((a[0].lerp(b[0],f),a[1].lerp(b[1],f).normalized(),0))
   if len(clipped)<3:continue
   for j in range(1,len(clipped)-1):
    tri=[clipped[0],clipped[j],clipped[j+1]];a,b,c=[v[0]for v in tri];area=(b-a).cross(c-a).length/2
    if area<1e-12:continue
    total+=area;weights.append(total);roots.append(tri);idx=len(capverts);capverts.extend([v[0]+v[1]*.0007 for v in tri]);capnormals.extend([tuple(v[1])for v in tri]);fades.extend([smooth(max(0,v[2])/.006)for v in tri]);capfaces.append((idx,idx+1,idx+2))
  assert roots;full_indices=[tuple(t.vertices)for t in skintris];bvh=BVHTree.FromPolygons(coords,full_indices,all_triangles=True)
  cap=bpy.data.meshes.new('STUDY_CONTINUOUS_FEATHERED_SCALP_UNDERLAY');cap.from_pydata(capverts,[],capfaces);cap.update()
  for p in cap.polygons:p.use_smooth=True
  cap.normals_split_custom_set_from_vertices(capnormals)
  fade=cap.attributes.new('groom_edge_fade','FLOAT','POINT');fade.data.foreach_set('value',np.array(fades,dtype=np.float32));mat=bpy.data.materials.new('STUDY_FEATHERED_DARK_HAIR_ROOTS');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.006,.0028,.0013,1);bs.inputs['Roughness'].default_value=.92;bs.inputs['Specular IOR Level'].default_value=.08;attr=mat.node_tree.nodes.new('ShaderNodeAttribute');attr.attribute_name='groom_edge_fade';mat.node_tree.links.new(attr.outputs['Fac'],bs.inputs['Alpha']);mat.surface_render_method='DITHERED';cap.materials.append(mat);capob=bpy.data.objects.new('STUDY_FEATHERED_SCALP_UNDERLAY_'+o.name,cap);bpy.context.scene.collection.objects.link(capob);capob.matrix_world=o.matrix_world.copy();capob['person_id']=o['person_id'];capob['layer']='people_hair'
  for i in hairslots:
   mat=mesh.materials[i];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   for link in list(bs.inputs['Alpha'].links):mat.node_tree.links.remove(link)
   bs.inputs['Alpha'].default_value=0
  counts=[];points=[];radii=[];target=int(os.environ.get('SQUARE_SCALP_FIBRES','100000'));steps=12;attempts=0;boundary_stops=0
  while len(counts)<target and attempts<target*2:
   attempts+=1;tri=roots[min(len(roots)-1,bisect.bisect_left(weights,rng.random()*total))];a,b,c=[v[0]for v in tri];u,v=rng.random(),rng.random()
   if u+v>1:u,v=1-u,1-v
   p=a+(b-a)*u+(c-a)*v;md=mask(p)
   if rng.random()>smooth(max(0,md)/.006):continue
   length=rng.uniform(.022,.049);phase=rng.random()*math.tau;fly=rng.random()<.012;path=[]
   for step in range(steps):
    q,n,index,d=bvh.find_nearest(p)
    if q is None:break
    if mask(q)<-.003:boundary_stops+=1;break
    tr=skintris[index];va,vb,vc=[coords[i]for i in tr.vertices];e1=vb-va;e2=vc-va;w=q-va;den=e1.dot(e1)*e2.dot(e2)-e1.dot(e2)**2
    if abs(den)>1e-14:
     beta=(w.dot(e1)*e2.dot(e2)-w.dot(e2)*e1.dot(e2))/den;gamma=(w.dot(e2)*e1.dot(e1)-w.dot(e1)*e1.dot(e2))/den;alpha=1-beta-gamma;n=(mesh.vertices[tr.vertices[0]].normal*alpha+mesh.vertices[tr.vertices[1]].normal*beta+mesh.vertices[tr.vertices[2]].normal*gamma).normalized()
    # Tangent rotation: forehead upward -> crown backward -> nape downward, no anterior sink.
    flow=Vector((-.018,(q.z-(top-.12))*8,-(q.y-cy)*8));direction=flow-n*flow.dot(n)
    if direction.length<.001:direction=n.cross(Vector((1,0,0)))
    direction.normalize();side=direction.cross(n).normalized();t=step/(steps-1);lift=.0008+.008*math.sin(math.pi*t)+(.004*t*t if fly else 0);path.append(q+n*lift+side*(.00022*math.sin(phase+t*math.pi*1.5)));p=q+direction*(length/(steps-1))
   if len(path)<2:continue
   counts.append(len(path))
   for j,p in enumerate(path):points.extend(p);radii.append(.000038*max(.025,1-j/(len(path)-1)))
  curves=bpy.data.hair_curves.new('STUDY_DENSE_CONTINUOUS_HEAD_GROOM');curves.add_curves(counts);curves.attributes['position'].data.foreach_set('vector',np.array(points,dtype=np.float32));rad=curves.attributes.new('radius','FLOAT','POINT');rad.data.foreach_set('value',np.array(radii,dtype=np.float32));mat=bpy.data.materials.new('STUDY_PHYSICAL_BROWN_HAIR_MELANIN');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();hair=nt.nodes.new('ShaderNodeBsdfHairPrincipled');hair.parametrization='MELANIN';hair.inputs['Melanin'].default_value=.72;hair.inputs['Melanin Redness'].default_value=.25;hair.inputs['Roughness'].default_value=.36;hair.inputs['Radial Roughness'].default_value=.38;hair.inputs['Random Color'].default_value=.13;hair.inputs['Random Roughness'].default_value=.12;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(hair.outputs[0],out.inputs['Surface']);curves.materials.append(mat);ob=bpy.data.objects.new('STUDY_CONTINUOUS_SCALP_GROOM_'+o.name,curves);bpy.context.scene.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy();ob['person_id']=o['person_id'];ob['layer']='people_hair'
  result.append({'object':o.name,'actual_curves':len(counts),'actual_points':len(radii),'root_attempts':attempts,'hairline_boundary_stops':boundary_stops,'actual_root_surface_m2':total,'clipped_scalp_triangles':len(roots),'body_skin_top_z':top,'head_centre_y':cy,'ear_centre_yz':[ear_y,ear_z],'head_half_width':hw,'root_radius_m':.000038,'underlay_offset_m':.0007,'underlay_hairline_alpha_feather_m':.006,'style':'Original short swept-back physical scalp groom2. Continuous triangle clipping, ear exclusion,6mm root/underlay fade and proper forehead/crown/nape rotational flow. Real hair curves, no paint/generation or anatomy/face/light change. UNSAVED; not native adoption/quality acceptance.'})
 bpy.context.view_layer.update();return result
