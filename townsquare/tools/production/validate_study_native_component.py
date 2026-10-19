"""Fresh-open actual editable study components; pack/membership/view helper gates, not visual approval."""
import bpy,json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
key=os.environ['SQUARE_COMPONENT'];path=Path(bpy.data.filepath);base=R/os.environ.get('SQUARE_NATIVE_COMPONENT_ROOT','.cache/placement-portable-components/Native');assert path==base/(key+'.blend');s=bpy.context.scene;actual_opened_sha256=file_sha256(path);unit_change=s.unit_settings.system!='METRIC'or s.unit_settings.scale_length!=1
# Only the first unit-metadata normalization saves. Subsequent independent opens are read-only.
if unit_change:
 s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
meshes=[o for o in s.objects if o.type=='MESH'];issues=[];missing=[]
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file():missing.append(im.name)
if missing:issues.append({'missing_unpacked_images':missing})
if not meshes:issues.append('No actual mesh geometry')
if key.startswith('B'):
 expected=json.loads((R/os.environ.get('SQUARE_NATIVE_COMPONENT_REPORTS','evidence/production/placement-portable')/('export-'+key+'.json')).read_text())['expected_geometry'];floor_ids=sorted({str(o.get('floor_id'))for o in meshes});room_ids=sorted({str(o.get('room_id'))for o in meshes})
 if floor_ids!=expected['floor_ids']:issues.append('Floor membership differs from exported source')
 if room_ids!=expected['room_ids']:issues.append('Room membership differs from exported source')
 for name in ['VIEW_TOOLS.py','VIEW_PRESETS.json']:
  if name not in bpy.data.texts:issues.append('Missing offline view helper '+name)
r={'component':key,'status':'PASS'if not issues else'FAIL','path':str(path.relative_to(R)),'sha256':file_sha256(path),'bytes':path.stat().st_size,'actual_opened_native_sha256':actual_opened_sha256,'metric_normalization_resaved':unit_change,'exact_current_file_was_freshly_opened':actual_opened_sha256==file_sha256(path),'mesh_objects':len(meshes),'packed_images':sum(bool(i.packed_file)for i in bpy.data.images),'missing_external_images':missing,'issues':issues,'metric_scale_length':s.unit_settings.scale_length,'blender':bpy.app.version_string,'scope':'Actual separate Blender process open of saved full-map editable component, metric units, mesh presence, packed/existing images and building floor/room membership/offline view tools. Not visual quality/collision/certification.'};(R/os.environ.get('SQUARE_NATIVE_COMPONENT_REPORTS','evidence/production/placement-portable')/('native-subasset-'+key+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_STUDY_NATIVE_COMPONENT_GATE',key,r['status'],r['sha256'],flush=True);assert not issues,issues
