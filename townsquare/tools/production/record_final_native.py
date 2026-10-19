"""Hash the already-saved final editable native, verify its geometry signature and write the receipt.
No save, no ray casting: stays far below the 2 GB runtime limit."""
import bpy, json, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/production'))
from fingerprints import file_sha256, geometry_uv_pose_material_signature

prev = json.loads((R / 'evidence/production/R14-exterior-framed-town.json').read_text())
camera = json.loads((R / 'evidence/production/R14-camera-corrected-stocked-town.json').read_text())
design = json.loads((R / 'design/production-views.json').read_text())
sha = file_sha256(bpy.data.filepath)
sig = geometry_uv_pose_material_signature()
assert sig == camera['geometry_uv_pose_material_signature'], 'geometry changed by the framing work'
presets = json.loads(bpy.data.texts['VIEW_PRESETS.json'].as_string())
r = dict(prev)
r.update(native=str(Path(bpy.data.filepath).resolve().relative_to(R)), native_sha256=sha,
         native_bytes=Path(bpy.data.filepath).stat().st_size,
         geometry_uv_pose_material_signature=sig,
         parent_camera_corrected_native_sha256=camera['native_sha256'],
         view_presets_in_native=len(presets['frames']),
         view_presets_match_design_file=json.dumps(presets, sort_keys=True) == json.dumps(design, sort_keys=True),
         stage='FULL EDITABLE NATIVE WITH ALL CAMERA PRESETS - CANDIDATE, NOT FINAL ACCEPTANCE')
(R / 'evidence/production/R14-final-editable-native.json').write_text(json.dumps(r, indent=2) + '\n')
print('FINAL_NATIVE_RECORDED', sha, r['native_bytes'], sig, r['view_presets_in_native'], r['view_presets_match_design_file'], flush=True)
