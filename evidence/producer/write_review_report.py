"""Readable report from explicitly recorded observations; no automatic inspection claims."""
from pathlib import Path
import hashlib,json,datetime
R=Path(__file__).resolve().parents[2];p=R/'evidence/producer/visual-review.json';d=json.loads(p.read_text());ns=hashlib.sha256((R/'scene/building-final.blend').read_bytes()).hexdigest();rows=[x for x in d['final_inspections'] if x.get('source_sha256')==ns];unresolved=[x for x in d['defects'] if x['severity'] in ['critical','major'] and x['status']!='closed']
ready=len(rows)==29 and not unresolved and all(x['known_critical_major']==0 for x in rows)
d['current_completion']={'producer_stage':'inspection complete; candidate for independent review' if ready else 'work in progress','current_native_sha256':ns,'explicit_current_source_inspections':len(rows),'required':29,'unresolved_critical_major':[x['id'] for x in unresolved],'independent_acceptance':'pending','updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};p.write_text(json.dumps(d,indent=2)+'\n')
s=['# Producer visual review — Casa dei Colori','', '**'+d['current_completion']['producer_stage']+'. Independent acceptance: PENDING.**','',f'Current native SHA-256: `{ns}`',f'Explicit individually opened current-source originals: **{len(rows)}/29**. These are agent/producer observations, not an independent human-review certificate.','', '## Real inspect → fix → inspect cycles','', 'Earlier checkpoint narratives are retained as originally logged. Their pending wording is superseded only by the current final observations/defect closures below.']
for c in d.get('cycles',[]):
 s+=['','### '+c['phase']]+[f'- **{k.replace("_"," ")}:** {v}' for k,v in c.items() if k!='phase']
s+=['','## Defects and actual reinspection','']
for x in d['defects']:
 s+=['### '+x['id']+f' — {x["severity"]} / {x["status"]}']+[f'- **{k}:** {v}' for k,v in x.items() if k not in ['id','severity','status']]+['']
s+=['## Individually opened final images','']
for x in rows:
 s+=['### '+x['image'],f'- PNG SHA-256: `{x["sha256"]}`',f'- Original dimensions: {x["dimensions"][0]} × {x["dimensions"][1]}; opened individually: true; logged {x["logged_at"]}.',f'- Observation: {x["observations"]}',f'- Known critical/major in this view: {x["known_critical_major"]}.','']
s+=['## Boundaries','', 'Mechanical render success, these producer records and mechanical validators are not non-owner acceptance. No self-review/vote has been cast. Engineering, local code, swept navigation, accessibility/fire/lift/structure/MEP approval are outside this conceptual visual model. Historical diagnostics and negative regressions are deliberately separate from the 29 final PNGs. Publication/upload/redownload/member verification must be recorded in the separate release receipt.']
(R/'evidence/producer/VISUAL_REVIEW.md').write_text('\n'.join(s)+'\n');print('READABLE_PRODUCER_REVIEW',len(rows),'/29; independent pending')
