import bpy,os,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];key=os.environ['SQUARE_COMPONENT'];base=R/'.cache/final-components';path=base/'Winterlichtplatz-R4.glb' if key=='ALL' else base/'GLB'/(key+'.glb');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));s=bpy.context.scene;bpy.context.view_layer.update();meshes=[o for o in s.objects if o.type=='MESH'];pts=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
actual={'mesh_objects':len(meshes),'triangles_instance_sum':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'bounds_min':[min(p[i] for p in pts) for i in range(3)],'bounds_max':[max(p[i] for p in pts) for i in range(3)],'floor_ids':sorted({str(o.get('floor_id')) for o in meshes}),'room_ids':sorted({str(o.get('room_id')) for o in meshes}),'person_ids':sorted([int(o['person_id']) for o in meshes if o.get('person_id')])}
if key=='ALL':
 expected={};exports=[json.loads(p.read_text())['expected_geometry'] for p in sorted((R/'evidence/production').glob('export-*.json'))]
 expected['mesh_objects']=sum(x['mesh_objects'] for x in exports);expected['triangles_instance_sum']=sum(x['triangles_instance_sum'] for x in exports);expected['bounds_min']=[min(x['bounds_min'][i] for x in exports) for i in range(3)];expected['bounds_max']=[max(x['bounds_max'][i] for x in exports) for i in range(3)]
 for name in ['floor_ids','room_ids']:expected[name]=sorted({v for x in exports for v in x[name]})
 expected['person_ids']=sorted([v for x in exports for v in x['person_ids']])
else:expected=json.loads((R/'evidence/production'/('export-'+key+'.json')).read_text())['expected_geometry']
issues=[]
for name in ['triangles_instance_sum','floor_ids','room_ids','person_ids']:
 if actual[name]!=expected[name]:issues.append({'field':name,'expected':expected[name],'actual':actual[name]})
for name in ['bounds_min','bounds_max']:
 if any(abs(a-b)>.001 for a,b in zip(actual[name],expected[name])):issues.append({'field':name,'expected':expected[name],'actual':actual[name]})
missing_uv=[o.name for o in meshes if not o.data.uv_layers]
# Original plain-colour geometry can legitimately have no UV; textured primitives require UV.
textured_without_uv=[]
for o in meshes:
 if o.data.uv_layers:continue
 if any(mat and mat.use_nodes and any(n.type=='TEX_IMAGE' for n in mat.node_tree.nodes) for mat in o.data.materials):textured_without_uv.append(o.name)
if textured_without_uv:issues.append({'textured_meshes_missing_uv':textured_without_uv})
report={'component':key,'glb':str(path.relative_to(R)),'status':'PASS' if not issues else 'FAIL','fresh_factory_scene_imported_with_blender':bpy.app.version_string,'expected':expected,'actual':actual,'issues':issues,'mesh_objects_without_uv_plain_colour_allowed':missing_uv,'image_count':len(bpy.data.images),'packed_images':sum(bool(im.packed_file) for im in bpy.data.images),'scope':'Actual clean glTF importer roundtrip: triangle-instance count, world bounds, floor/room/person metadata and textured UV presence. This does not assert identical Blender area-light/HDRI/procedural-shader rendering.'}
(R/'evidence/production'/('reimport-'+key+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('ACTUAL_GLB_CLEAN_REIMPORT',key,report['status'],'triangles',actual['triangles_instance_sum'],'issues',issues,flush=True)
if key=='ALL' and not issues:bpy.ops.wm.save_as_mainfile(filepath=str(base/'Winterlichtplatz-GLB-clean-reimport.blend'),compress=True)
if issues:raise RuntimeError('Clean reimport geometry/UV/metadata gate failed')
