"""Write the latest camera presets into the native's VIEW_PRESETS text block and save a copy.

Deliberately does NO ray casting and no depsgraph evaluation: this scene needs ~1.4 GB just to
save inside a 2 GB runtime, so the memory-heavy solving lives in its own process.
"""
import bpy, json, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/production'))
from fingerprints import file_sha256, geometry_uv_pose_material_signature

base = json.loads((R / 'evidence/production/R14-exterior-framed-town.json').read_text())
assert file_sha256(bpy.data.filepath) == base['parent_camera_corrected_native_sha256'] or \
    file_sha256(bpy.data.filepath) == json.loads((R / 'evidence/production/R14-camera-corrected-stocked-town.json').read_text())['native_sha256']
design = json.loads((R / 'design/production-views.json').read_text())
t = bpy.data.texts.get('VIEW_PRESETS.json') or bpy.data.texts.new('VIEW_PRESETS.json')
t.clear(); t.write(json.dumps(design)); t.use_fake_user = True
s = bpy.context.scene
s['view_preset_notice'] = ('%d camera presets: 26 floor plans, 26 cutaways, 26 interiors, 6 street-level heroes, '
                           '8 close-human inspection views, 12 measured building exteriors and 4 whole-village orbits. '
                           'Framing changes only; model geometry/materials/lights unchanged by the presets.') % len(design['frames'])
sig = geometry_uv_pose_material_signature()
out = R / '.cache/stocked-town/Winterlichtplatz-final-editable-UNPROMOTED.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
r = dict(base)
r.update(native=str(out.relative_to(R)), native_sha256=file_sha256(out), native_bytes=out.stat().st_size,
         geometry_uv_pose_material_signature=sig,
         parent_camera_corrected_native_sha256=json.loads((R / 'evidence/production/R14-camera-corrected-stocked-town.json').read_text())['native_sha256'],
         view_presets_total=len(design['frames']),
         stage='FULL EDITABLE NATIVE WITH ALL VIEW PRESETS - CANDIDATE, NOT FINAL ACCEPTANCE')
(R / 'evidence/production/R14-final-editable-native.json').write_text(json.dumps(r, indent=2) + '\n')
print('FINAL_EDITABLE_NATIVE_SAVED', r['native_sha256'], r['native_bytes'], sig, flush=True)
