"""UNSAVED physical scalp groom2. Continuous clipped/feathered hairline, ears clear, rotational flow.
No altered anatomy/face/photo/lighting, no native save, no quality acceptance from successful render.
"""
import bpy,bmesh,random,math,bisect,os,hashlib
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def non_hair_signature(mesh,hairslots):
 rows=[];uv=mesh.uv_layers.active
 for p in mesh.polygons:
  if p.material_index in hairslots:continue
  corners=[(tuple(mesh.vertices[mesh.loops[i].vertex_index].co),tuple(uv.data[i].uv)if uv else())for i in p.loop_indices];start=min(range(len(corners)),key=lambda i:corners[i]);corners=corners[start:]+corners[:start];rows.append((mesh.materials[p.material_index].name if mesh.materials[p.material_index]else'',tuple(corners)))
 return hashlib.sha256(repr(sorted(rows)).encode()).hexdigest()
def apply():
 result=[];rng=random.Random(171061)
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH'or not o.get('person_id'):continue
  mesh=o.data;hairslots={i for i,m in enumerate(mesh.materials)if m and'braid01'in m.name.lower()};skinslots={i for i,m in enumerate(mesh.materials)if m and(m.name.endswith('.body')or'.body.'in m.name)}
  if not hairslots:continue
  assert skinslots;source_mesh=mesh;nonhair_before=non_hair_signature(source_mesh,hairslots);rawskin={i for p in mesh.polygons if p.material_index in skinslots for i in p.vertices};rawtop=max(mesh.vertices[i].co.z for i in rawskin);faces=[p for p in mesh.polygons if p.material_index in skinslots and max(mesh.vertices[i].co.z for i in p.vertices)>rawtop-.34];used=sorted({i for p in faces for i in p.vertices});remap={old:new for new,old in enumerate(used)};proxy=bpy.data.meshes.new('STUDY_SKIN_SCALP_SMOOTH_PROXY');proxy.from_pydata([mesh.vertices[i].co.copy()for i in used],[],[[remap[i]for i in p.vertices]for p in faces]);proxy.update();temp=bpy.data.objects.new('STUDY_TEMP_SKIN_SCALP_PROXY',proxy);bpy.context.scene.collection.objects.link(temp);sub=temp.modifiers.new('Scalp root surface refinement only; anatomy unchanged','SUBSURF');sub.levels=2;sub.render_levels=2;bpy.context.view_layer.update();mesh=bpy.data.meshes.new_from_object(temp.evaluated_get(bpy.context.evaluated_depsgraph_get()));bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(proxy);mesh.calc_loop_triangles();coords=[v.co.copy()for v in mesh.vertices];skintris=list(mesh.loop_triangles);skinverts={v for t in skintris for v in t.vertices};top=max(coords[i].z for i in skinverts);ring=[coords[i]for i in skinverts if top-.10<coords[i].z<top-.045];cy=(min(p.y for p in ring)+max(p.y for p in ring))/2;cx=(min(p.x for p in ring)+max(p.x for p in ring))/2;hw=max(abs(coords[i].x-cx)for i in skinverts if coords[i].z>top-.18);earpts=[coords[i]for i in skinverts if abs(coords[i].x-cx)>hw*.91 and top-.20<coords[i].z<top-.065];ear_y=sum(p.y for p in earpts)/len(earpts);ear_z=sum(p.z for p in earpts)/len(earpts)
  def mask(p):
   theta=abs(math.atan2(p.x-cx,p.y-cy));depth=.17-.105*smooth((theta-.60)/1.65);recess=.008*math.exp(-((abs(p.x-cx)-.045)/.018)**2)*smooth((theta-1.5)/.4);d=p.z-(top-depth)-recess+.001*math.sin(170*p.x+60*p.y)
   # Keep actual outer ear cartilage bare, not covered in scalp material/curves.
   e=(math.sqrt(((p.y-ear_y)/.031)**2+((p.z-ear_z)/.040)**2)-1)*.03;d=min(d,max(e,(hw*.74-abs(p.x-cx))*3))
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
  # Delete only obsolete hair-card faces on a copied static actor mesh. No hidden transparent
  # layers/transparent-bounce artifacts; original skin/clothes/face coordinates and UVs remain.
  o.data=source_mesh.copy();bm=bmesh.new();bm.from_mesh(o.data);oldfaces=[f for f in bm.faces if f.material_index in hairslots];removed_cards=len(oldfaces);bmesh.ops.delete(bm,geom=oldfaces,context='FACES_ONLY');orphans=[v for v in bm.verts if not v.link_faces]
  if orphans:bmesh.ops.delete(bm,geom=orphans,context='VERTS')
  bm.to_mesh(o.data);bm.free();o.data.update();nonhair_after=non_hair_signature(o.data,hairslots);assert nonhair_before==nonhair_after,'Non-hair geometry/UV/material assignment changed unexpectedly'
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
  result.append({'object':o.name,'nonhair_geometry_uv_material_signature_before':nonhair_before,'nonhair_geometry_uv_material_signature_after':nonhair_after,'actual_removed_source_hair_card_faces':removed_cards,'scalp_root_proxy_subdivision':2,'actual_curves':len(counts),'actual_points':len(radii),'root_attempts':attempts,'hairline_boundary_stops':boundary_stops,'actual_root_surface_m2':total,'clipped_scalp_triangles':len(roots),'body_skin_top_z':top,'head_centre_y':cy,'ear_centre_yz':[ear_y,ear_z],'head_half_width':hw,'root_radius_m':.000038,'underlay_offset_m':.0007,'underlay_hairline_alpha_feather_m':.006,'style':'Original short swept-back physical scalp groom3. Continuous triangle clipping, ear exclusion,6mm root/underlay fade and proper forehead/crown/nape rotational flow. Smoothed actual head root proxy, obsolete hair-card faces physically removed only in copied UNSAVED static actor mesh (no transparent layer artifact); real hair curves, no paint/generation or skin anatomy/face coordinates/lighting change. UNSAVED; not native adoption/quality acceptance.'})
  bpy.data.meshes.remove(mesh)
 bpy.context.view_layer.update();return result
