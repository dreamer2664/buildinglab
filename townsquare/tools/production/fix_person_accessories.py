"""Inspect-driven correction: draped scarf outside evaluated parka, subtle fitted cap.
Preserves the anatomical mesh, photographed skin/clothing, armature and authored pose.
Outputs a full-resolution editable rig and a clearly labelled static render derivative.
"""
import bpy,os,json,hashlib,math,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];pid=os.environ['SQUARE_PERSON'];s=bpy.context.scene;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();changes=[]
def body_pose_signature():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.type=='MESH' and 'ANATOMICAL_BASE' in o.name:
   a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(o.name.encode()+a.tobytes())
  if o.type=='ARMATURE':
   for b in o.pose.bones:h.update((b.name+str(tuple(tuple(row) for row in b.matrix))).encode())
 return h.hexdigest()
before=body_pose_signature();cloth=next(o for o in s.objects if 'male_casualsuit05' in o.name);evaluated=cloth.evaluated_get(deps);me=evaluated.to_mesh();cloth_points=[cloth.matrix_world@v.co for v in me.vertices];evaluated.to_mesh_clear()
tail=next(o for o in s.objects if o.name==pid+'_SCARF_TAIL');ps=[tail.matrix_world@Vector(p) for p in tail.bound_box];xmin,xmax=min(p.x for p in ps),max(p.x for p in ps);zmin,zmax=min(p.z for p in ps),max(p.z for p in ps);xc=(xmin+xmax)/2;width=xmax-xmin;inv=tail.matrix_world.inverted();verts=[];uvs=[];rows=30;cols=8;surface=[]
for j in range(rows+1):
 t=j/rows;z=zmax-(zmax-zmin)*t
 candidates=[p.y for p in cloth_points if abs(p.z-z)<.045 and xmin-.045<p.x<xmax+.045]
 y=min(candidates)-.013 if candidates else min(p.y for p in ps)-.035
 # Non-planar textile folds; every row stays outside the evaluated coat front.
 row=[]
 for i in range(cols+1):
  u=i/cols;x=xc+(u-.5)*width+.006*math.sin(t*math.pi*1.4);yy=y-.004*(1+math.sin(u*math.pi*4+t*2))-.004*math.sin(t*math.pi)
  row.append((x,yy,z+.0025*math.sin(u*math.pi*2+t*3)))
 surface.append(row)
for side in [0,1]:
 for j,row in enumerate(surface):
  for i,p in enumerate(row):verts.append(tuple(inv@Vector((p[0],p[1]+side*.004,p[2]))));uvs.append((i/cols,j/rows*3))
N=(rows+1)*(cols+1);faces=[]
for side in [0,1]:
 for j in range(rows):
  for i in range(cols):
   a=side*N+j*(cols+1)+i;q=(a,a+1,a+cols+2,a+cols+1);faces.append(q if side==0 else tuple(reversed(q)))
for j in range(rows):
 for i in [0,cols]:a=j*(cols+1)+i;b=(j+1)*(cols+1)+i;faces.append((a,b,b+N,a+N))
for j in [0,rows]:
 for i in range(cols):a=j*(cols+1)+i;faces.append((a,a+1,a+1+N,a+N))
old=tail.data;new=bpy.data.meshes.new(pid+'_SCARF_DRAPED_OUTSIDE_COAT');new.from_pydata(verts,[],faces);new.update()
for mat in old.materials:new.materials.append(mat)
uv=new.uv_layers.new(name='UVMap')
for poly in new.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:uv.data[li].uv=uvs[new.loops[li].vertex_index]
tail.data=new
changes.append({'part':tail.name,'fix':'Replaced intersecting flat box tail with double-sided, gently folded textile surface, fitted13mm outside evaluated coat front per height row.','rows':rows,'columns':cols,'source_world_z_interval':[zmin,zmax]})
# Replace stiff fringe blocks with soft round hanging yarn; align to new cloth hem.
for o in list(s.objects):
 if '_SCARF_FRINGE' not in o.name:continue
 ps0=[o.matrix_world@Vector(p) for p in o.bound_box];center=sum(ps0,Vector())/8;idx=min(cols,max(0,round((center.x-xmin)/width*cols)));edge=Vector(surface[-1][idx]);o.location.y+=(edge.y-center.y)/o.parent.scale.y if o.parent else edge.y-center.y
 changes.append({'part':o.name,'fix':'Aligned existing yarn fringe with corrected textile hem'})
# Fit cap against actual posed eyebrows, rather than blind lowering all variants.
cap_parts=[o for o in s.objects if any(k in o.name for k in ['_KNITTED_BEANIE','_BEANIE_RIB'])]
cap=next((o for o in cap_parts if o.name==pid+'_BEANIE_RIB'),None)
if cap:
 brow_points=[]
 for brow in [o for o in s.objects if o.type=='MESH' and o.get('MPFB_GEN_object_type')=='Eyebrows']:
  ev=brow.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();brow_points.extend([brow.matrix_world@v.co for v in em.vertices]);ev.to_mesh_clear()
 old_rim=min((cap.matrix_world@Vector(p)).z for p in cap.bound_box)
 desired_rim=max(p.z for p in brow_points)+.012 if brow_points else old_rim-.008
 dz=desired_rim-old_rim
 for o in cap_parts:
  parent_scale=o.parent.scale if o.parent else Vector((1,1,1));o.location.y-=.012/parent_scale.y;o.location.z+=dz/parent_scale.z
  changes.append({'part':o.name,'fix':'Cap/rib fitted12mm above actual posed eyebrow maximum,12mm forward; avoids blind18mm lowering that covered eyes on P04.','world_z_shift_m':dz,'desired_low_rim_z_m':desired_rim})
 bpy.context.view_layer.update();rim=min((part.matrix_world@Vector(p)).z for part in cap_parts for p in part.bound_box)-.0005
 for hair in [o for o in s.objects if o.type=='MESH' and o.get('MPFB_GEN_object_type')=='Hair']:
  ev=hair.evaluated_get(bpy.context.evaluated_depsgraph_get());hm=ev.to_mesh();zs=[(v.index,(hair.matrix_world@v.co).z) for v in hm.vertices];zlo=min(z for _,z in zs);zhi=max(z for _,z in zs);span=max(.00001,zhi-zlo);weights=[(index,(zhi-z)/span) for index,z in zs];threshold=max(0,min(1,(zhi-rim)/span));ev.to_mesh_clear()
  vg=hair.vertex_groups.new(name='R6_SMOOTH_CROWN_UNDER_CAP')
  for index,weight in weights:vg.add([index],weight,'REPLACE')
  mask=hair.modifiers.new('R6 / smoothly clipped covered crown, editable','MASK');mask.vertex_group=vg.name;mask.threshold=threshold;mask.use_smooth=True
  bpy.context.view_layer.update();checked=hair.evaluated_get(bpy.context.evaluated_depsgraph_get());cm=checked.to_mesh();actual_max=max(((hair.matrix_world@v.co).z for v in cm.vertices),default=-999);checked.to_mesh_clear();assert actual_max<=rim+.00002,(pid,hair.name,actual_max,rim)
  changes.append({'part':hair.name,'fix':'Exact world-z-linear smooth crown clipping0.5mm below lowest cap edge; verified evaluated hair cannot protrude above hem. Corrects R3 sawtooth and R5 high-plane temple protrusions. Anatomical raw mesh/pose unchanged.','cut_plane_world_z_m':rim,'smooth_interpolation':True,'threshold':threshold,'actual_evaluated_hair_max_world_z_m':actual_max,'hair_below_cap_hem_regression':'PASS'})
 # Original subtle fleece/knit microrelief; no external generated texture or fake portrait.
 for mat in {slot.material for o in cap_parts for slot in o.material_slots if slot.material}:
  mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bsdf:continue
  bsdf.inputs['Roughness'].default_value=.86
  if 'Sheen Weight' in bsdf.inputs:bsdf.inputs['Sheen Weight'].default_value=.18
  noise=nodes.new('ShaderNodeTexNoise');noise.name='Original fine wool microrelief';noise.inputs['Scale'].default_value=240;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65
  bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00045;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
 changes.append({'part':'cap wool materials','fix':'Original native fine fleece microrelief/roughness/sheens; procedural normal is a documented portable fallback limitation.'})
bpy.context.view_layer.update();after=body_pose_signature();assert before==after,'Anatomical mesh or rig pose unexpectedly changed'
for o in s.objects:o['stage']='R6_ACCESSORY_FIT / anatomy and pose conserved'
rigdir=R/'.cache/fixed-people/rigs';rigdir.mkdir(parents=True,exist_ok=True);rigfile=rigdir/(pid+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(rigfile),compress=True)
h=hashlib.sha256()
with rigfile.open('rb') as f:
 while b:=f.read(1024*1024):h.update(b)
rigsha=h.hexdigest()
# Evaluate the actual masks, clothes, pose and UVs into static scene instances.
deps=bpy.context.evaluated_depsgraph_get();temps=[]
for o in list(s.objects):
 if o.type!='MESH' or o.hide_render:continue
 ev=o.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps);ob=bpy.data.objects.new('STATIC/'+o.name,mesh);s.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy();temps.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for o in temps:o.select_set(True)
bpy.context.view_layer.objects.active=temps[0];bpy.ops.object.join();static=bpy.context.view_layer.objects.active;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for o in list(s.objects):
 if o!=static:bpy.data.objects.remove(o,do_unlink=True)
mesh=static.data;sole=min(v.co.z for v in mesh.vertices);crowd=json.loads((R/'.cache/recovery/master/provenance/master-build.json').read_text())['crowd'];instances=[]
for n,item in enumerate(x for x in crowd if x['variant']==pid):
 ob=static if n==0 else bpy.data.objects.new('instance',mesh)
 if n:s.collection.objects.link(ob)
 ob.name=f"CROWD_{item['person_id']:02}_{pid}";ob.location=(*item['xy_m'],.006-sole);ob.rotation_euler=(0,0,item['rotation_rad'])
 for k,v in {'variant_id':pid,'person_id':item['person_id'],'role':item['role'],'building_id':'CROWD','layer':'people','floor_id':'PUBLIC','stage':'R6_ACCESSORY_FITTING_CORRECTED','rig_source_sha256':rigsha}.items():ob[k]=v
 instances.append(ob.name)
bpy.data.orphans_purge(do_recursive=True)
for im in bpy.data.images:
 if im.source!='FILE' or not all(im.size):continue
 oldsize=tuple(im.size);factor=min(1,512/max(oldsize));newsize=(max(1,round(oldsize[0]*factor)),max(1,round(oldsize[1]*factor)))
 if newsize!=oldsize:im.scale(*newsize);im.pack()
 im.buffers_free()
chunk=R/'.cache/render-chunks'/(pid+'-fixed.blend');bpy.ops.wm.save_as_mainfile(filepath=str(chunk),compress=True)
report={'person':pid,'original_rig_public_package':'Winterlichtplatz-People-rigs-4bf44a021c3d.zip','corrected_rig':str(rigfile.relative_to(R)),'corrected_rig_sha256':rigsha,'anatomy_and_pose_signature_before':before,'anatomy_and_pose_signature_after':after,'anatomy_and_pose_conserved':before==after,'fixes':changes,'static_vertices':len(mesh.vertices),'static_faces':len(mesh.polygons),'static_instances':instances,'sole_before_placement_m':sole,'placed_sole_z_m':.006,'visual_reinspection':'PENDING'}
(R/'evidence/production'/('person-fit-'+pid+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('PERSON_ACCESSORIES_FIXED',pid,'static vertices',len(mesh.vertices),'rig preserved',rigsha,flush=True)
