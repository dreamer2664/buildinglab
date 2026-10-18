"""UNSAVED original physical groom on actual licensed head skin, not an oversized source hair-card shell.
Only geometry/physical hair material. Source anatomy, face, lighting and saved native remain untouched.
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
  assert skinslots;mesh.calc_loop_triangles();coords=[v.co.copy()for v in mesh.vertices];skintris=[t for t in mesh.loop_triangles if t.material_index in skinslots];skinverts={v for t in skintris for v in t.vertices};top=max(coords[i].z for i in skinverts);crown=[coords[i]for i in skinverts if coords[i].z>top-.018];cy=sum(p.y for p in crown)/len(crown);cx=sum(p.x for p in crown)/len(crown);hw=max(abs(coords[i].x-cx)for i in skinverts if coords[i].z>top-.18)
  def allowed(p):
   front=smooth((cy-p.y+.005)/.080);depth=.205-.11*front
   return p.z>top-depth and not(abs(p.x-cx)>hw*.85 and p.z<top-.11 and p.y<cy+.02)
  roots=[t for t in skintris if all(allowed(coords[i])for i in t.vertices)];assert roots;full_indices=[tuple(t.vertices)for t in skintris];bvh=BVHTree.FromPolygons(coords,full_indices,all_triangles=True);weights=[];total=0
  for t in roots:total+=t.area;weights.append(total)
  # Real thin dark scalp underlay, offset0.7mm; original body surface remains present and unchanged.
  used=sorted({i for t in roots for i in t.vertices});mp={old:new for new,old in enumerate(used)};cap=bpy.data.meshes.new('STUDY_ACTUAL_SCALP_UNDERLAY');cap.from_pydata([coords[i]+mesh.vertices[i].normal*.0007 for i in used],[],[[mp[i]for i in t.vertices]for t in roots]);cap.update()
  for p in cap.polygons:p.use_smooth=True
  mat=bpy.data.materials.new('STUDY_DARK_SCALP_HAIR_ROOTS');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.006,.0028,.0013,1);bs.inputs['Roughness'].default_value=.92;bs.inputs['Specular IOR Level'].default_value=.08;cap.materials.append(mat);capob=bpy.data.objects.new('STUDY_ACTUAL_SCALP_UNDERLAY_'+o.name,cap);bpy.context.scene.collection.objects.link(capob);capob.matrix_world=o.matrix_world.copy();capob['person_id']=o['person_id'];capob['layer']='people_hair'
  # Replace only the source hair card visibility, never the skin or full person object.
  for i in hairslots:
   mat=mesh.materials[i];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   for link in list(bs.inputs['Alpha'].links):mat.node_tree.links.remove(link)
   bs.inputs['Alpha'].default_value=0
  counts=[];points=[];radii=[];target=int(os.environ.get('SQUARE_SCALP_FIBRES','100000'));steps=12
  for strand in range(target):
   tri=roots[min(len(roots)-1,bisect.bisect_left(weights,rng.random()*total))];a,b,c=[coords[i]for i in tri.vertices];u,v=rng.random(),rng.random()
   if u+v>1:u,v=1-u,1-v
   p=a+(b-a)*u+(c-a)*v;length=rng.uniform(.025,.065);phase=rng.random()*math.tau;fly=rng.random()<.012;path=[];normal_previous=None
   for step in range(steps):
    q,n,index,d=bvh.find_nearest(p)
    if q is None:break
    # Smooth actual vertex normal interpolation avoids polygonal direction changes in the groom.
    t=skintris[index];va,vb,vc=[coords[i]for i in t.vertices];e1=vb-va;e2=vc-va;w=q-va;den=e1.dot(e1)*e2.dot(e2)-e1.dot(e2)**2
    if abs(den)>1e-14:
     beta=(w.dot(e1)*e2.dot(e2)-w.dot(e2)*e1.dot(e2))/den;gamma=(w.dot(e2)*e1.dot(e1)-w.dot(e1)*e1.dot(e2))/den;alpha=1-beta-gamma;n=(mesh.vertices[t.vertices[0]].normal*alpha+mesh.vertices[t.vertices[1]].normal*beta+mesh.vertices[t.vertices[2]].normal*gamma).normalized()
    flow=Vector((-.11,.8,-.72));direction=flow-n*flow.dot(n)
    if direction.length<.001:direction=n.cross(Vector((1,0,0)))
    direction.normalize();side=direction.cross(n).normalized();t=step/(steps-1);lift=.0012+.0025*math.sin(math.pi*t)+(.003*t*t if fly else 0);path.append(q+n*lift+side*(.00028*math.sin(phase+t*math.pi*1.5)));p=q+direction*(length/(steps-1))
   if len(path)<2:continue
   counts.append(len(path))
   for j,p in enumerate(path):points.extend(p);radii.append(.000038*max(.025,1-j/(len(path)-1)))
  curves=bpy.data.hair_curves.new('STUDY_DENSE_HEAD_CONFORMING_PHYSICAL_GROOM');curves.add_curves(counts);curves.attributes['position'].data.foreach_set('vector',np.array(points,dtype=np.float32));rad=curves.attributes.new('radius','FLOAT','POINT');rad.data.foreach_set('value',np.array(radii,dtype=np.float32));mat=bpy.data.materials.new('STUDY_PHYSICAL_BROWN_HAIR_MELANIN');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();hair=nt.nodes.new('ShaderNodeBsdfHairPrincipled');hair.parametrization='MELANIN';hair.inputs['Melanin'].default_value=.72;hair.inputs['Melanin Redness'].default_value=.25;hair.inputs['Roughness'].default_value=.36;hair.inputs['Radial Roughness'].default_value=.38;hair.inputs['Random Color'].default_value=.13;hair.inputs['Random Roughness'].default_value=.12;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(hair.outputs[0],out.inputs['Surface']);curves.materials.append(mat);ob=bpy.data.objects.new('STUDY_HEAD_CONFORMING_GROOM_'+o.name,curves);bpy.context.scene.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy();ob['person_id']=o['person_id'];ob['layer']='people_hair'
  result.append({'object':o.name,'actual_curves':len(counts),'actual_points':len(radii),'actual_root_surface_m2':total,'scalp_triangles':len(roots),'body_skin_top_z':top,'crown_centre_y':cy,'head_half_width':hw,'root_radius_m':.000038,'underlay_offset_m':.0007,'style':'Original swept-back short layered procedural groom grown from actual head/neck skin. Original braid01 hair cards made transparent in UNSAVED study; anatomy/face UV/lighting unchanged. No scalp removal or photo/painting/generation. Not native adoption or quality acceptance.'})
 bpy.context.view_layer.update();return result
