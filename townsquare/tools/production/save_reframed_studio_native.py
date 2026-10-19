"""Persist refit studio cameras without leaving unsaved studio/cyclorama objects in the native."""
import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256,geometry_uv_pose_material_signature
b=json.loads((R/'evidence/production/R14-camera-corrected-stocked-town.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];from view_tools import apply_view;apply_view('H02')
for o in list(bpy.context.scene.objects):
 if o.name.startswith('VIEWLIGHT/')or o.name.startswith('VIEW|'):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.context.scene.objects:o.hide_render=False;o.hide_set(False)
bpy.data.orphans_purge(do_recursive=True);frames=json.loads((R/'design/production-views.json').read_text())
fits={x['view']:x for x in json.loads((R/'evidence/production/R14-pair-studio-camera-fits.json').read_text())['views']}
changed=[]
for f in frames['frames']:
 if f['id']in fits:
  fit=fits[f['id']];f['position']=fit['position'];f['target']=fit['target'];f['lens_mm']=fit['lens'];changed.append(f['id'])
assert len(changed)==6,(changed)
(R/'design/production-views.json').write_text(json.dumps(frames,indent=2)+'\n')
t=bpy.data.texts.get('VIEW_PRESETS.json')or bpy.data.texts.new('VIEW_PRESETS.json');t.clear();t.write(json.dumps(frames));t.use_fake_user=True;bpy.context.scene['studio_camera_refit']='Six pair-studio cameras fitted to actual paired actor bounds so both complete silhouettes are inside frame; model geometry unchanged.';path=R/'.cache/stocked-town/Winterlichtplatz-studio-reframed-UNPROMOTED.blend';sig=geometry_uv_pose_material_signature();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);r=dict(b);r.update(native=str(path.relative_to(R)),native_sha256=file_sha256(path),native_bytes=path.stat().st_size,geometry_uv_pose_material_signature=sig,actual_pair_studio_camera_fits=json.loads((R/'evidence/production/R14-pair-studio-camera-fits.json').read_text())['views'],stage='STUDIO_PAIR_FRAMING_CORRECTED_CANDIDATE_NOT_FINAL_ACCEPTANCE');(R/'evidence/production/R14-studio-reframed-town.json').write_text(json.dumps(r,indent=2)+'\n');print('REFIT_STUDIO_TOWN_SAVED',r['native_sha256'],r['native_bytes'],sig,flush=True)
