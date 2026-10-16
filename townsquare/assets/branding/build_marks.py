"""Original vector-draft shop identities. Not imported real logos; not trademark clearance."""
from pathlib import Path
import json,html,hashlib
R=Path(__file__).resolve().parents[2];D=json.loads((R/'design/programme.json').read_text());out=[]
marks=[
'<path d="M35 46h42l-3 46H38zM45 46c0-23 23-23 23 0"/><path d="M55 66q-12-21 11-23 1 20-11 23z"/>',
'<path d="M25 77c-5-45 68-45 64 0v13H25zM40 57l-5 16M57 50l-5 18M74 54l-5 18"/>',
'<path d="M28 51h46v36H28zM74 55c31-4 25 31 0 23M22 94h63M38 40c-13-11 12-10 0-23M59 40c-13-11 12-10 0-23"/>',
'<path d="M58 38q-21-15-39-6v56q20-7 39 7 21-14 40-7V32q-20-9-40 6zM58 38v57M29 46l19 3M29 58l19 3M69 49l18-3M69 61l18-3"/>',
'<path d="M57 93V52M57 76Q31 52 28 74q19 16 29 2M58 65q24-28 29-5-18 17-29 5"/><circle cx="57" cy="37" r="11"/><circle cx="42" cy="31" r="10"/><circle cx="65" cy="24" r="10"/><circle cx="75" cy="40" r="10"/><circle cx="50" cy="49" r="10"/>',
'<path d="M26 88l50-63 9 7-50 63zM76 25l9 7M66 28c-18-10-34 6-20 20 16 16-17 20-25 7M47 67l35 23"/>',
'<path d="M23 90h69M30 90V52l28-24 28 24v38M49 90V66h18v24M43 48h30"/><circle cx="83" cy="23" r="8"/>',
'<path d="M55 21L24 56l31 28 31-28zM55 21v63M24 56h62M55 84q-23 13-8 20"/>',
'<path d="M21 46l20-22h34l20 22-37 49zM21 46h74M41 24l-5 22 22 49 22-49-5-22M36 46l22-22 22 22"/>',
'<path d="M26 57h64q-6 29-32 29-24 0-32-29zM42 94h32M66 48l16-25 8 5-17 23M42 40q-8-18 10-19 7 15-10 19z"/>',
'<circle cx="29" cy="76" r="20"/><circle cx="86" cy="76" r="20"/><path d="M29 76l22-38 20 38H29l24-26h27l6 26M42 38h18M73 29h13l-6 21"/>',
'<path d="M19 36h78v54H19zM19 36l39 32 39-32M19 90l26-26M97 90L71 64"/>'
]
colors=['#234c37','#764027','#6e2827','#293d59','#35503f','#49404f','#783a31','#31566a','#6c512e','#345956','#37443f','#625033']
for b,mark,color in zip(D['buildings'],marks,colors):
 p=R/'assets/branding'/(b['id']+'.svg');safe=html.escape(b['brand']);svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="200" viewBox="0 0 720 200"><title>{safe} — original vector draft</title><rect width="720" height="200" rx="8" fill="{color}"/><g transform="translate(12 36)" stroke="#f0e5cb" fill="none" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round">{mark}</g><text x="145" y="110" fill="#f0e5cb" font-family="DejaVu Sans,sans-serif" font-size="35" letter-spacing="2">{safe}</text><text x="147" y="145" fill="#e4d2ae" font-family="sans-serif" font-size="13" letter-spacing="4">WINTERLICHTPLATZ</text></svg>'
 p.write_text(svg);out.append({'building':b['id'],'brand':b['brand'],'file':str(p.relative_to(R)),'sha256':hashlib.sha256(svg.encode()).hexdigest(),'origin':'Original project vector paths and type composition','status':'VECTOR DRAFT — not yet applied to saved native or visually approved','applications_planned':['fascia','projecting sign','glazed door','appropriate interior packaging/menus/labels']})
(R/'assets/branding/manifest.json').write_text(json.dumps(out,indent=2)+'\n');print('ORIGINAL_VECTOR_DRAFTS',len(out))
