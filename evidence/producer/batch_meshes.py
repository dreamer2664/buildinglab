"""Purpose-built, lossless evaluated-mesh batching for this scene's RAM budget.
All actual evaluated vertices/faces/material indices and corner normals are copied.
Primary chairs/appliances/fixture families remain distinct editable meshes; no decimation.
Original component names are retained as JSON; unbatched native interiors also delivered.
Generated texture coordinates are retained per vertex, avoiding batch-induced stretching.
"""
import bpy,json,re,math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
R=Path(__file__).resolve().parents[2]

def category(o):
 name=o.name;f=o.get('fixture');room=o.get('room_id','');local=name[len(room)+1:] if room and name.startswith(room+'_') else name
 if o.get('role')=='stair_flight':return name
 if o.get('role')=='door':return name if name.endswith('_LEAF') else 'FRAME_SET'
 if name.startswith(('ENTRANCE_CANOPY','CANOPY_TIE','ENTRANCE_SIGN')):return name.split('.')[0]
 m=re.match(r'(.*_CHAIR)_(BACK_STILE|SEAT_FRAME|SEAT_CUSHION|LEG|BACK)(?:\.(\d+))?$',name)
 if m:
  mult={'LEG':4,'BACK_STILE':2}.get(m[2],1);return m[1]+'_'+str(int(m[3] or 0)//mult)
 if f=='bed':
  if any(t in local for t in ['NIGHTSTAND','DRAWER','LAMP_BASE','LAMP_STEM','SHADE']):return 'BEDSIDE_'+name.split('.')[-1] if '.' in name else 'BEDSIDE_0'
  return 'BED'
 if f=='kitchen':
  for tokens,label in [(['FRIDGE'],'REFRIGERATOR'),(['DISHWASHER'],'DISHWASHER'),(['OVEN'],'OVEN'),(['SINK','TAP','SPOUT','LEVER'],'SINK_AND_TAP'),(['HOOD'],'EXTRACTOR'),(['HOB','INDUCTION','SAUCEPAN','PAN_HANDLE'],'HOB')]:
   if any(t in local for t in tokens):return label
  return 'CABINETRY_AND_WORKTOP'
 if f=='bathroom':
  if local.startswith('WC_'):return 'TOILET'
  if local.startswith(('SHOWER_','DRAIN')):return 'SHOWER'
  if local.startswith(('VANITY','BASIN','MIRROR','TAP','SPOUT','LEVER','KNOB')):return 'VANITY_BASIN_MIRROR'
  return 'BATH_ACCESSORIES'
 if f=='sofa':return 'SECOND_SOFA' if '_SECOND_SOFA_' in name else 'SOFA'
 if f=='cafe_seating':
  m=re.search(r'_TABLE_(?:TOP|STEM|BASE)(?:\.(\d+))?$',name)
  if m:return 'CAFE_TABLE_'+str(int(m[1] or 0))
 return f or o.get('role','mesh')

def batch_scene():
 s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();groups=defaultdict(list)
 for o in list(s.objects):
  if o.type!='MESH':continue
  props=tuple(sorted((k,json.dumps(v)) for k,v in o.items()))
  # Keep parameter-sensitive flights separate; other parts share actual semantic tags.
  groups[(tuple(c.name for c in o.users_collection),props,category(o))].append(o)
 source_n=sum(len(v) for v in groups.values());source_vertices=source_faces=final_vertices=final_faces=0;rows=[]
 for n,(key,objects) in enumerate(groups.items()):
  colnames,props,cat=key;verts=[];faces=[];normals=[];smooth=[];midx=[];generated=[];materials=[];names=[o.name for o in objects];matmap={}
  for o in objects:
   ev=o.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg);world=o.matrix_world.copy();normalmat=world.to_3x3().inverted().transposed();off=len(verts)
   bb=[Vector(v) for v in o.bound_box];lo=[min(v[i] for v in bb) for i in range(3)];size=[max(v[i] for v in bb)-lo[i] for i in range(3)]
   for v in me.vertices:
    verts.append(tuple(world@v.co));generated.append(tuple((v.co[i]-lo[i])/size[i] if size[i]>1e-8 else .5 for i in range(3)))
   local_mats=[]
   for m in me.materials:
    if m.name not in matmap:matmap[m.name]=len(materials);materials.append(bpy.data.materials[m.name])
    local_mats.append(matmap[m.name])
   cn=me.corner_normals
   for p in me.polygons:
    faces.append(tuple(off+i for i in p.vertices));smooth.append(p.use_smooth);midx.append(local_mats[p.material_index])
    for li in p.loop_indices:normals.append(tuple((normalmat@cn[li].vector).normalized()))
   source_vertices+=len(me.vertices);source_faces+=len(me.polygons);ev.to_mesh_clear()
  # A useful object-mode pivot, not a forced origin at the building's world origin.
  low=[min(p[i] for p in verts) for i in range(3)];high=[max(p[i] for p in verts) for i in range(3)];pivot=Vector(tuple((a+b)/2 for a,b in zip(low,high)));localverts=[tuple(Vector(p)-pivot) for p in verts]
  name=names[0] if len(names)==1 else ((objects[0].get('room_id') or objects[0].get('level') or colnames[0])+'__'+cat)
  me=bpy.data.meshes.new(name+'_GEOMETRY');me.from_pydata(localverts,[],faces)
  for m in materials:me.materials.append(bpy.data.materials[m.name])
  me.polygons.foreach_set('use_smooth',smooth);me.polygons.foreach_set('material_index',midx);me.update();me.normals_split_custom_set(normals)
  at=me.attributes.new('SOURCE_GENERATED','FLOAT_VECTOR','POINT');at.data.foreach_set('vector',[c for xyz in generated for c in xyz]);new=bpy.data.objects.new(name+'_BATCH',me)
  for c in colnames:bpy.data.collections[c].objects.link(new)
  new.location=pivot
  for k,v in props:new[k]=json.loads(v)
  new['source_material_names']=json.dumps([m.name for m in materials]);new['component_names']=json.dumps(names,separators=(',',':'));new['component_count']=len(names);new['source_evaluated_vertices']=len(verts);new['source_evaluated_faces']=len(faces)
  new['desired_name']=name
  # Keep source IDs alive until a clean-process cleanup; deleting evaluated IDs in this
  # same dependency graph caused a reproducible Blender/TBB shutdown segfault.
  for o in objects:o.hide_render=True
  final_vertices+=len(me.vertices);final_faces+=len(me.polygons);rows.append({'object':new.name,'source_components':len(names),'vertices':len(me.vertices),'faces':len(me.polygons),'materials':[m.name for m in me.materials]})
  if n%100==0:print('BATCH_PROGRESS',n,len(groups),flush=True)
 # Preserve explicit original per-component Generated coordinates in procedural shaders.
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  nt=m.node_tree;need=[l for l in list(nt.links) if l.from_node.type=='TEX_COORD' and l.from_socket.name=='Generated'];noises=[n for n in nt.nodes if n.type=='TEX_NOISE' and not n.inputs['Vector'].is_linked]
  if not need and not noises:continue
  a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='SOURCE_GENERATED';a.label='Original component coordinates — lossless mesh batching'
  for l in need:to=l.to_socket;nt.links.remove(l);nt.links.new(a.outputs['Vector'],to)
  for node in noises:nt.links.new(a.outputs['Vector'],node.inputs['Vector'])
 assert source_vertices==final_vertices and source_faces==final_faces
 report={'method':'lossless evaluated mesh batching; all vertices/faces/material indices and world-space corner normals copied; no decimation','source_components':source_n,'batched_meshes':len(groups),'source_evaluated_vertices':source_vertices,'final_vertices':final_vertices,'source_evaluated_faces':source_faces,'final_faces':final_faces,'procedural_coordinates':'SOURCE_GENERATED point attribute retains original component-normalised coordinates','rows':rows}
 (R/'evidence/producer/mesh-conservation.json').write_text(json.dumps(report,indent=2)+'\n');print('BATCH_CONSERVATION_PASS',source_n,len(groups),source_vertices,source_faces,flush=True);return report

if __name__=='__main__':
 batch_scene()
 stage=Path.home()/'.cache/buildinglab-batch-stage.blend';stage.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(stage),compress=True)
 print('BATCH_STAGE_SAVED',flush=True)
