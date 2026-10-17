"""Export the FINAL candidate, not the early recovery chunks. Static GLB + full-map native."""
import bpy,os,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'));key=os.environ['SQUARE_COMPONENT'];source=R/os.environ.get('SQUARE_SOURCE_NATIVE','.cache/master/Winterlichtplatz-R11.blend');assert source.resolve().is_relative_to(R);source_sha256=hashlib.file_digest(source.open('rb'),'sha256').hexdigest();assert not os.environ.get('SQUARE_SOURCE_SHA256')or source_sha256==os.environ['SQUARE_SOURCE_SHA256'];bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False) as (a,b):
 if key.startswith('B'):b.collections=[n for n in a.collections if n.startswith(key+' ')]
 elif key=='PUBLIC':b.collections=[n for n in a.collections if n=='PUBLIC_REALM' or 'FILL' in n or n.startswith('AUXILIARY /')]
 else:b.objects=[n for n in a.objects if n.startswith('CROWD_') and n.endswith('_'+key)]
 if key.startswith('B') or key=='PUBLIC':b.worlds=list(a.worlds)
s=bpy.context.scene
if key.startswith('B') or key=='PUBLIC':
 for c in b.collections:s.collection.children.link(c)
 if b.worlds:s.world=b.worlds[0]
else:
 for o in b.objects:s.collection.objects.link(o)
bpy.context.view_layer.update();out=R/os.environ.get('SQUARE_COMPONENT_OUT','.cache/final-components');(out/'Native').mkdir(parents=True,exist_ok=True);(out/'GLB').mkdir(exist_ok=True)
views=json.loads((R/'design/production-views.json').read_text());subset=[f for f in views['frames'] if f.get('building_id')==key] if key.startswith('B') else []
if subset:
 for name,text in [('VIEW_PRESETS.json',json.dumps({'frames':subset})),('VIEW_TOOLS.py',(R/'tools/production/view_tools.py').read_text()),('READ_ME.txt','Full-map editable building component. Coordinates are the actual town position. Embedded view tools select the prepared floor cameras. This component is not a replacement for the complete master. See master/rights/portability notes.')]:
  t=bpy.data.texts.new(name);t.write(text);t.use_fake_user=True
 import view_tools;view_tools.add_cameras(subset);s.camera=bpy.data.objects['VIEW|'+subset[0]['id']]
# Full-resolution detailed building/public component; people retain their separately supplied editable rig.
if key.startswith('B') or key=='PUBLIC':bpy.ops.wm.save_as_mainfile(filepath=str(out/'Native'/(key+'.blend')),compress=True)
for o in list(s.objects):
 if o.get('auxiliary_background'):bpy.data.objects.remove(o,do_unlink=True)
# Portable crop of the recovered1000m horizon solid, not removal of the town ground.
# Native preserves its full original extent; glTF retains a112x100m snow context and all square/building geometry.
background_omissions=[]
if key=='PUBLIC':
 import bmesh,numpy as np
 for o in [o for o in s.objects if o.type=='MESH' and o.get('layer')=='ground']:
  bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts)
  while unseen:
   first=unseen.pop();component={first};stack=[first]
   while stack:
    v=stack.pop()
    for e in v.link_edges:
     w=e.other_vert(v)
     if w in unseen:unseen.remove(w);component.add(w);stack.append(w)
   pts=[o.matrix_world@v.co for v in component];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
   if max(hi[i]-lo[i] for i in range(2))<=150:continue
   # Preserve linear UV metre density, rather than stretching the1000m mapping over112m.
   uv_maps=[]
   for face in {f for v in component for f in v.link_faces}:
    positions=np.array([tuple(l.vert.co) for l in face.loops]);axes=np.argsort(np.ptp(positions,axis=0))[-2:];A=np.column_stack([positions[:,axes[0]],positions[:,axes[1]],np.ones(len(positions))])
    for layer in bm.loops.layers.uv.values():
     U=np.array([tuple(l[layer].uv) for l in face.loops]);coeff=np.linalg.lstsq(A,U,rcond=None)[0];uv_maps.append((face,layer,axes,coeff))
   inv=o.matrix_world.inverted()
   for v in component:
    p=o.matrix_world@v.co;p.x=max(-56,min(56,p.x));p.y=max(-50,min(50,p.y));v.co=inv@p
   for face,layer,axes,coeff in uv_maps:
    for l in face.loops:l[layer].uv=np.array([l.vert.co[int(axes[0])],l.vert.co[int(axes[1])],1.0])@coeff
   background_omissions.append({'object':o.name,'action':'Cropped only legacy horizon component to112x100m, preserving original local UV metre density and z levels; all town architecture/plaza/people unchanged.','original_vertices':len(component),'original_bounds_min':lo,'original_bounds_max':hi,'portable_bounds_min':[-56,-50,lo[2]],'portable_bounds_max':[56,50,hi[2]]})
  bm.to_mesh(o.data);o.data.update();bm.free()
bpy.data.orphans_purge(do_recursive=True)
for im in bpy.data.images:
 if im.source not in ['FILE','GENERATED'] or not all(im.size):continue
 old=tuple(im.size);factor=min(1,512/max(old));new=(max(1,round(old[0]*factor)),max(1,round(old[1]*factor)))
 if new!=old:im.scale(*new);im.pack()
 im.buffers_free()
bpy.context.view_layer.update();meshes=[o for o in s.objects if o.type=='MESH'];pts=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
# export_apply=True uses evaluated modifiers. Raw source polygon counts undercount new rounded joinery.
deps=bpy.context.evaluated_depsgraph_get();evaluated_vertices=evaluated_polygons=evaluated_triangles=0
for ob in meshes:
 ev=ob.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();evaluated_vertices+=len(me.vertices);evaluated_polygons+=len(me.polygons);evaluated_triangles+=len(me.loop_triangles);ev.to_mesh_clear()
expected={'mesh_objects':len(meshes),'vertices_instance_sum':evaluated_vertices,'polygons_instance_sum':evaluated_polygons,'triangles_instance_sum':evaluated_triangles,'geometry_measurement':'Actual evaluated depsgraph meshes, including rounded joinery/bevel modifiers, matching export_apply=True; not raw source face counts.','bounds_min':[min(p[i]for p in pts)for i in range(3)],'bounds_max':[max(p[i]for p in pts)for i in range(3)],'floor_ids':sorted({str(o.get('floor_id'))for o in meshes}),'room_ids':sorted({str(o.get('room_id'))for o in meshes}),'person_ids':sorted([int(o['person_id'])for o in meshes if o.get('person_id')])}
kw={'filepath':str(out/'GLB'/(key+'.glb')),'export_format':'GLB','export_yup':True,'export_apply':True,'export_animations':False,'export_extras':True,'export_lights':True,'export_cameras':False,'export_texcoords':True,'export_normals':True,'export_tangents':True,'export_materials':'EXPORT','export_image_format':'AUTO','export_skins':False,'export_morph':False,'export_draco_mesh_compression_enable':False}
allowed=set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys());kw={k:v for k,v in kw.items() if k in allowed};bpy.ops.export_scene.gltf(**kw)
p=out/'GLB'/(key+'.glb');h=hashlib.sha256()
with p.open('rb') as f:
 while b:=f.read(1024*1024):h.update(b)
report={'component':key,'source_native_sha256':source_sha256,'glb':str(p.relative_to(R)),'glb_sha256':h.hexdigest(),'glb_bytes':p.stat().st_size,'expected_geometry':expected,'texture_cap_px':512,'background_omissions':background_omissions,'scope':'All saved-source town component geometry; source SHA is provenance, not visual acceptance; omit redundant auxiliary500m plane and crop only legacy1000m horizon to112x100m snow context; original64x52m plaza and all buildings/furniture unchanged. Static people, with separate full-resolution editable rigs','portability_limitations':['Blender area lights and photographic world are not faithfully represented by core glTF; punctual lights only where supported.','Procedural shader details fall back to portable Principled/PBR values where unsupported; native is authoritative for lighting/glass/colour management.','Source image maps resampled to512px for portable memory budget; original packed maps remain in full-resolution natives.'],'reimport':'PENDING'}
(R/os.environ.get('SQUARE_COMPONENT_REPORTS','evidence/production')/('export-'+key+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('FINAL_COMPONENT_EXPORTED',key,p.stat().st_size,flush=True)
