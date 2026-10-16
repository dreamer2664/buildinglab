"""Finalize producer documentation ONLY after all actual current-source inspections.
Does not publish, infer viewing, grant independent acceptance, or alter model/export.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ns=sha(R/'scene/building-final.blend');gs=sha(R/'exports/building-final.glb');r=json.loads((R/'evidence/producer/visual-review.json').read_text())
rows=[x for x in r['final_inspections'] if x['source_sha256']==ns];assert len(rows)==29 and len({x['image'] for x in rows})==29
assert all(x['opened_individually'] and x['known_critical_major']==0 and sha(R/x['image'])==x['sha256'] for x in rows)
for n in ['scene-validation','export-test','visual-package-validation']:
 d=json.loads((R/'evidence/producer'/(n+'.json')).read_text());assert d['status']=='PASS' and d.get('native_sha256',d.get('source_sha256'))==ns
assert json.loads((R/'evidence/producer/export-test.json').read_text())['glb_sha256']==gs
subprocess.run([sys.executable,str(R/'evidence/producer/write_review_report.py')],cwd=R,check=True)
p=R/'HANDOFF.md';s=p.read_text();a=s.index('**WORK IN PROGRESS');b=s.index('\n\n## Commission',a)
s=s[:a]+'**PRODUCER-CHECKED CANDIDATE — NOT independently accepted.** Original six-storey Mediterranean-city mixed-use residence, 14 furnished homes. Native and clean GLB-reimport gates pass; all 29 exact-source final-resolution originals have actually been opened individually and SHA-bound observations recorded. This packet is frozen before archive upload/redownload verification: consult the separate public publication receipt for that later network result. Mechanical PASS and producer inspection are not independent approval.'+s[b:]
s=s.replace('The exact-native 29-image campaign is regenerating after runtime restoration removed final PNGs;', 'The exact-native 29-image campaign was fully regenerated and all 29 originals individually reopened after runtime restoration removed final PNGs;')
s+='\n\n## Frozen producer evidence summary\n\n- Native SHA-256: `'+ns+'`.\n- GLB SHA-256: `'+gs+'`.\n- Current original inspections: **29/29**, from one unchanged saved native. See `evidence/producer/VISUAL_REVIEW.md` and JSON; no renderer-success inference.\n- `renders/GALLERY.html` is an offline embedded preview of the actual PNGs, not evidence replacements.\n- Ceiling finish seams and shaft caps were physically corrected and re-tested rather than painted out or merely disclosed. Stylised vegetation, technical low-wall art/pendant convention and documented GLB procedural-to-constant PBR approximation are intentional limitations. No unresolved producer-recorded critical/major defect; independent review remains mandatory.\n- Earlier runtime original-image losses are explicitly retained in recovery/history records. Surviving B3/B4 negative PNGs and real failing geometry reports support the correction trail; no absent historical PNG is fabricated.\n- The packager creates an identical `evidence/visual-review.json` ZIP mirror without writing coordinator-owned source paths.\n- Independent reviewer: open actual native/unbatched source and GLB, inspect every original, verify reports/hashes/release receipt against live charter, and record acceptance or failures on the non-owner review card. Producer has cast no vote.\n'
p.write_text(s);print('PRODUCER_HANDOFF_PREPARED; publication verification and independent acceptance remain separate')
