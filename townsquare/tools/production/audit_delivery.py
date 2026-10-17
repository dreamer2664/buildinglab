"""Machine integrity gate; never substitutes for separately recorded actual original-image review."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[2];E=R/'evidence/production';plan=json.loads((R/'design/production-views.json').read_text())['frames'];build=json.loads((E/'R6-native-build.json').read_text());derivative=json.loads((E/'R6-render-derivative-reopen.json').read_text());records=json.loads((E/'final-render-manifest.json').read_text());reviews=json.loads((E/'final-individual-image-inspections.json').read_text())['inspections'];issues=[];passed=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
for f in plan:
 id=f['id'];errors=[];r=records.get(id);q=reviews.get(id)
 if not r:issues.append({'view':id,'issues':['Not rendered']});continue
 p=R/r['image'];noisy=R/r['noisy_original']
 if not p.exists() or sha(p)!=r['final_sha256']:errors.append('Final image absent or bytes mismatch')
 else:
  with Image.open(p) as im:
   im.verify()
  with Image.open(p) as im:
   if list(im.size)!=f['resolution']:errors.append('Native output dimensions mismatch')
 if not noisy.exists() or sha(noisy)!=r['noisy_original_sha256'] or r['noisy_original_sha256']!=r['original_before_denoise_sha256']:errors.append('Noisy provenance mismatch')
 if r['source_native_sha256']!=build['full_resolution_native_sha256']:errors.append('Full-source SHA differs')
 if r['geometry_uv_pose_material_signature']!=build['geometry_uv_pose_material_signature_full_resolution']:errors.append('Geometry signature differs')
 reports=[json.loads((R/n).read_text()) for n in r['render_reports']]
 if len(reports)!=(4 if f['resolution'][0]>=3840 else 1):errors.append('Camera-border tile report count mismatch')
 for t in reports:
  if t['opened_derivative_sha256']!=derivative['sha256']:errors.append('Actual frame working-input bytes differ from actual validated derivative')
  if t['original_source_native_sha256']!=build['full_resolution_native_sha256']:errors.append('Tile full native source SHA differs')
 if len(reports)==4:
  if any(t['render_only_visibility']!=reports[0]['render_only_visibility'] for t in reports):errors.append('Tile-specific visibility differs')
 if not q or not q.get('actual_original_opened') or q.get('image_sha256')!=r['final_sha256'] or q.get('decision')!='PRODUCER_CHECKED':errors.append('Separate actual original-image inspection missing or not tied to current bytes')
 if errors:issues.append({'view':id,'issues':errors})
 else:passed.append(id)
for name in ['R6-full-native-reopen.json','R6-render-derivative-reopen.json','reimport-ALL.json']:
 d=json.loads((E/name).read_text())
 if d.get('status')!='PASS':issues.append({'gate':name,'issues':['Not actual PASS']})
report={'status':'PASS' if not issues and len(passed)==92 else 'INCOMPLETE_OR_FAIL','full_resolution_source_sha256':build['full_resolution_native_sha256'],'working_derivative_sha256':derivative['sha256'],'frame_count_required':92,'actual_frames_with_dimensions_hash_source_noisy_and_separate_producer_visual_check':len(passed),'passed_views':passed,'issues':issues,'scope':'Producer evidence integrity only; individual review is manually recorded after actual original file opens. Not photorealism, regulatory certification, independent non-owner acceptance, or final human approval.'};(E/'R6-final-evidence-integrity.json').write_text(json.dumps(report,indent=2)+'\n');print('FINAL_EVIDENCE_INTEGRITY',report['status'],len(passed),'of92');raise SystemExit(bool(issues))
