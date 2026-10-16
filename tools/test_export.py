"""Export the loaded native candidate, reset to a clean scene and reimport actual GLB.
blender -b scene/building-final.blend --python-exit-code 1 --python tools/test_export.py
Published-asset verification without overwriting it:
... --python tools/test_export.py -- --import-only PATH --report export-redownload-test.json
No renderer process receives transport credentials. GLB has six named level anchors.
"""
import bpy,json,sys,hashlib,gc,argparse
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];p=argparse.ArgumentParser();p.add_argument('--import-only');p.add_argument('--report',default='export-test.json');a=p.parse_args(args)
assert Path(a.report).name==a.report
s=bpy.context.scene
# Restore all reversible collections and object visibility; native file itself is not resaved.
for c in bpy.data.collections:c.hide_render=False;c.hide_viewport=False
for o in s.objects:o.hide_render=False;o.hide_set(False)
bpy.context.view_layer.update()
meshes=[o for o in s.objects if o.type=='MESH'];expected_names={o.name for o in meshes};expected_mats={m.name for o in meshes for m in o.data.materials if m};expected_levels={lid:sum(o.get('level')==lid for o in meshes) for lid in [f'L{i:02}' for i in range(1,7)]}
def bounds(objects):
 low=[float('inf')]*3;high=[-float('inf')]*3
 for o in objects:
  for v in o.bound_box:
   q=o.matrix_world@Vector(v)
   for i in range(3):low[i]=min(low[i],q[i]);high[i]=max(high[i],q[i])
 return low+high
assert {'Limestone','Plaster','Terracotta','Teal','Oak','Glass','Linen','Porcelain','Steel','Glow'}.issubset(expected_mats),'SOURCE PALETTE MISSING: comparison with an already defective source is not an export PASS'
fallback={}
for name in expected_mats:
 m=bpy.data.materials[name];b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');fallback[name]={'base_color':list(m.diffuse_color),'roughness':b.inputs['Roughness'].default_value,'metallic':b.inputs['Metallic'].default_value,'transmission':b.inputs['Transmission Weight'].default_value}
expected_bbox=bounds(meshes);native_digest=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();area_count=sum(o.type=='LIGHT' and o.data.type=='AREA' for o in s.objects)
output=Path(a.import_only) if a.import_only else R/'exports/building-final.glb';output.parent.mkdir(parents=True,exist_ok=True)
if not a.import_only:
 # Preserve all global transforms, while making the otherwise flattened GLB easy to isolate.
 source_objects=list(s.objects)
 for i in range(1,7):
  lid=f'L{i:02}';anchor=bpy.data.objects.new(lid,None);s.collection.objects.link(anchor);anchor['occupied_level']=True;anchor['level']=lid
  for o in source_objects:
   if o.get('level')==lid or (o.type=='CAMERA' and o.name.startswith('CAM_'+lid+'_')):
    world=o.matrix_world.copy();o.parent=anchor;o.matrix_world=world
 bpy.context.view_layer.update()
 # Make the documented portable fallback explicit, never delegate unsupported procedural
 # node handling to an exporter guess. Native materials on disk are never modified/resaved.
 for name in expected_mats:
  m=bpy.data.materials[name];b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  for socket in [b.inputs['Base Color'],b.inputs['Normal']]:
   for link in list(socket.links):m.node_tree.links.remove(link)
  b.inputs['Base Color'].default_value=fallback[name]['base_color']
 bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',export_apply=True,export_extras=True,export_cameras=True,export_lights=True,export_animations=False,export_yup=True,use_selection=False,export_materials='EXPORT')
assert output.exists() and output.stat().st_size>1000
digest=hashlib.sha256(output.read_bytes()).hexdigest();size=output.stat().st_size
# Drop source references and reset every datablock before actual reimport, not overlay import.
del meshes
if 'source_objects' in globals():del source_objects
s=None;bpy.ops.wm.read_factory_settings(use_empty=True);gc.collect()
bpy.ops.import_scene.gltf(filepath=str(output))
s=bpy.context.scene;bpy.context.view_layer.update();imported=[o for o in s.objects if o.type=='MESH'];names={o.name for o in imported};materials={m.name for o in imported for m in o.data.materials if m};levels={lid:sum(o.get('level')==lid for o in imported) for lid in expected_levels};anchors=sorted(o.name for o in s.objects if o.get('occupied_level'));actual_bbox=bounds(imported)
parameter_mismatches=[]
for name in sorted(expected_mats & materials):
 mat=bpy.data.materials[name];bsdf=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not bsdf:parameter_mismatches.append(name+': no Principled PBR node');continue
 for field,socket in [('base_color','Base Color'),('roughness','Roughness'),('metallic','Metallic'),('transmission','Transmission Weight')]:
  x=bsdf.inputs[socket].default_value;y=fallback[name][field];delta=max(abs(a-b) for a,b in zip(x,y)) if field=='base_color' else abs(x-y)
  if delta>1e-4 or bsdf.inputs[socket].is_linked:parameter_mismatches.append(name+': '+field)
missing_meshes=sorted(expected_names-names);missing_mats=sorted(expected_mats-materials);errors=[]
if missing_meshes:errors.append('missing required source mesh objects')
if missing_mats:errors.append('missing required source materials')
if parameter_mismatches:errors.append('portable PBR fallback parameter mismatch')
if len(imported)!=len(expected_names):errors.append('mesh count differs')
if levels!=expected_levels or anchors!=[f'L{i:02}' for i in range(1,7)]:errors.append('six level anchors/mesh allocation do not match')
if max(abs(a-b) for a,b in zip(actual_bbox,expected_bbox))>.0002:errors.append('world geometry bounds drift exceeds 0.2 mm')
external=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
if external or bpy.data.libraries:errors.append('missing external files/linked libraries')
report={'status':'PASS' if not errors else 'FAIL','native_sha256':native_digest,'glb_sha256':digest,'glb_bytes':size,'source_meshes':len(expected_names),'reimport_meshes':len(imported),'source_materials':sorted(expected_mats),'reimport_materials':sorted(materials),'missing_required_meshes':missing_meshes,'missing_required_materials':missing_mats,'material_parameter_mismatches':parameter_mismatches,'documented_source_pbr_fallbacks':fallback,'level_mesh_counts':levels,'six_named_level_anchors':anchors,'source_bbox_m':expected_bbox,'reimport_bbox_m':actual_bbox,'missing_external':external,'errors':errors,'blender':bpy.app.version_string,'settings':{'format':'GLB','axes':'glTF +Y up; clean Blender importer restores Z up','apply_modifiers':True,'extras':True,'cameras':True,'lights':True,'animations':False,'textures':'none; procedural wood/bump use documented PBR-colour/roughness fallbacks','analytic_area_lights_not_portable':area_count,'lighting_note':'Native analytic area lights are not supported by glTF. Luminaire geometry/emissive materials and directional sun retained; GLB viewer requires suitable environment lighting.'}}
(R/'evidence/producer'/a.report).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','source_meshes','reimport_meshes','six_named_level_anchors','missing_required_materials','errors']},indent=2))
if errors:raise RuntimeError('; '.join(errors))
print('PASS — exported actual GLB and clean-reimported with zero missing required mesh objects/materials, six identifiable occupied level groups, stable metric bounds and no missing external files.')
