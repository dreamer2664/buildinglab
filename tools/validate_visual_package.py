"""Mechanical final visual package gate. NEVER proves that anyone looked at an image.
Requires explicit, SHA-bound producer inspection records, not render-success inference.
Independent non-owner acceptance is tracked separately and cannot be manufactured here.
"""
from pathlib import Path
import json,hashlib,sys
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'evidence/producer'));from views import VIEWS
errors=[]
def check(q,m):
 if not q:errors.append(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mp=R/'evidence/producer/screenshot-manifest.json';rp=R/'evidence/producer/visual-review.json'
manifest=json.loads(mp.read_text()) if mp.exists() else {'images':[]};review=json.loads(rp.read_text()) if rp.exists() else {'final_inspections':[],'defects':[]};source=R/'scene/building-final.blend';source_sha=sha(source) if source.exists() else 'missing'
images=manifest['images'];expected={v['id']:v for v in VIEWS};actual=[x['id'] for x in images];check(len(actual)==len(set(actual)),'duplicate view IDs');check(set(actual)==set(expected),'all 29 required unique view IDs');digests=[];inspections=review.get('final_inspections',[])
for r in images:
 if r['id'] not in expected:errors.append('unexpected view '+r['id']);continue
 v=expected[r['id']];p=R/r['path'];check(p.exists(),r['id']+' PNG exists')
 if not p.exists():continue
 digest=sha(p);digests.append(digest)
 try:
  with Image.open(p) as im:
   check(im.format=='PNG',r['id']+' PNG format');check(im.size==(v['width'],v['height']),r['id']+' exact/minimum required dimensions');check(im.size==(r['width'],r['height']),r['id']+' declared dimensions match');im.verify()
 except Exception as e:errors.append(r['id']+' unreadable PNG '+type(e).__name__)
 check(p.stat().st_size>1000 and p.stat().st_size==r['bytes'],r['id']+' actual nonzero bytes');check(digest==r['sha256'],r['id']+' screenshot digest');check(r['camera']==v['camera'],r['id']+' camera binding');check(bool(r.get('time')),r['id']+' timestamp');check(r.get('source_sha256')==source_sha,r['id']+' exact current source native SHA')
 meta=R/r['metadata'];check(meta.exists(),r['id']+' render metadata exists')
 if meta.exists():
  m=json.loads(meta.read_text());check(m.get('source_sha256')==source_sha and m['render_percentage']==100,r['id']+' true final-resolution saved-native metadata');check(m['camera']==v['camera'],r['id']+' render camera metadata');check(m.get('postprocess'),r['id']+' disclosed denoising/annotation');check(m.get('saved_camera_matrix_world') is not None and m.get('saved_camera_matrix_world')==m.get('render_camera_matrix_world') and m.get('render_only_camera_revision') is None,r['id']+' saved-native camera pose unchanged during render')
 check(r.get('producer_opened_individually') is True and r.get('review_result','').startswith('inspected'),r['id']+' explicit producer inspection record, not a render log')
 matches=[x for x in inspections if x.get('image')==r['path'] and x.get('sha256')==digest and x.get('opened_individually') is True and x.get('source_sha256')==source_sha]
 check(len(matches)==1,r['id']+' exactly one current SHA-bound individual final inspection')
 if matches:check(bool(matches[0].get('observations')) and matches[0].get('known_critical_major')==0,r['id']+' actual observation and no known critical/major defect')
check(len(digests)==len(set(digests)),'unique final PNG digests');unresolved=[d.get('id','unnamed') for d in review.get('defects',[]) if d.get('severity') in ['critical','major'] and d.get('status')!='closed'];check(not unresolved,'zero unresolved critical/major defects: '+', '.join(unresolved))
check((R/'evidence/producer/VISUAL_REVIEW.md').exists(),'readable producer visual review');check((R/'evidence/producer/ASSET_LICENSES.md').exists(),'rights record');check((R/'HANDOFF.md').exists(),'factual final handoff')
report={'status':'PASS' if not errors else 'FAIL','required_images':29,'manifest_images':len(images),'source_sha256':source_sha,'mechanical_only':True,'not_proof_of_human_inspection':True,'independent_acceptance':review.get('independent_acceptance','pending'),'errors':errors}
(R/'evidence/producer/visual-package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
if errors:
 print('FAIL — '+str(len(errors))+' visual-package gate error(s):');print(*errors,sep='\n');sys.exit(1)
print('PASS — 29 required named final-resolution PNGs, exact dimensions/bytes/digests/cameras/source, disclosed processing, complete SHA-bound producer inspection manifest and no recorded critical/major defects. This is only a mechanical package check; independent non-owner acceptance remains separate.')
