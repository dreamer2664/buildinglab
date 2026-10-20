"""Build immutable candidate ZIP with an allowlist and member hashes; no network/credentials.
Run only after all producer gates/inspections. The separate publication receipt supplies
archive/upload/redownload hashes; no circular self-hashes are invented.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
subprocess.run([sys.executable,str(R/'tools/validate_visual_package.py')],cwd=R,check=True)
native=R/'scene/building-final.blend';ns=sha(native);glb=R/'exports/building-final.glb';gs=sha(glb)
for name in ['scene-validation','export-test','visual-package-validation']:
 d=json.loads((R/'evidence/producer'/(name+'.json')).read_text());assert d['status']=='PASS';assert d.get('native_sha256',d.get('source_sha256'))==ns
assert json.loads((R/'evidence/producer/export-test.json').read_text())['glb_sha256']==gs
files=set()
def add(p):
 p=Path(p);assert p.is_file() and p.resolve().is_relative_to(R);files.add(p)
for name in ['HANDOFF.md','briefs/BLENDER.md','design/programme.json','design/build_design.py','scene/shell.blend','scene/interiors.blend','scene/building-final.blend','exports/building-final.glb','exports/room-schedule.csv','exports/furnishing-schedule.csv','renders/GALLERY.html']:add(R/name)
for folder in ['assets/exterior','assets/interiors','tools','evidence/producer']:
 for p in (R/folder).rglob('*'):
  if p.is_file() and not any(x in p.parts for x in ['__pycache__','.git','.cache']) and p.suffix.lower() in ['.py','.sh','.json','.md','.txt','.ttf','.csv'] and p.name not in ['publication-receipt.json','release-members.json','release-build.json']:add(p)
m=json.loads((R/'evidence/producer/screenshot-manifest.json').read_text());assert len(m['images'])==29
for row in m['images']:add(R/row['path'])
# Historical diagnostics remain explicitly separate from the 29 final PNGs.
for p in (R/'renders/revision-B').glob('*.png'):add(p)
for folder in ['revision-B3','revision-B4','revision-C','revision-E','revision-F','revision-G']:
 for p in (R/'evidence/producer'/folder).glob('*.png'):add(p)
historical_availability=[]
records=json.loads((R/'assets/interiors/visual-review.json').read_text())['observations']+json.loads((R/'assets/exterior/visual-review.json').read_text())+json.loads((R/'evidence/producer/visual-review.json').read_text()).get('preflight_inspections',[])
for record in records:
 p=R/record['image'];available=p.is_file()
 if available:
  assert sha(p)==record['sha256'];add(p)
 historical_availability.append({'image':record['image'],'recorded_original_sha256':record['sha256'],'original_file_available':available,'note':'Actual original included.' if available else 'Original diagnostic PNG not retained by runtime snapshot. Original observation/digest retained as history only; no regenerated substitute is relabelled as the original.'})
hp=R/'evidence/producer/historical-availability.json';hp.write_text(json.dumps({'stage':'historical diagnostics, NOT the 29 required final images','records':historical_availability,'surviving_negative_cycles':'Surviving B3/B4 and C/E/F/G failed/draft PNGs, metadata/failed inspections and executed geometry negatives are included separately from final29.'},indent=2)+'\n');add(hp)
# The charter-level log is a generated ZIP alias, not a write to coordinator-owned repo paths.
alias=(R/'evidence/producer/visual-review.json').read_bytes()
readable_alias=(R/'evidence/producer/VISUAL_REVIEW.md').read_bytes()
entries={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)}
entries['evidence/visual-review.json']={'bytes':len(alias),'sha256':hashlib.sha256(alias).hexdigest(),'generated_alias_of':'evidence/producer/visual-review.json'}
entries['evidence/VISUAL_REVIEW.md']={'bytes':len(readable_alias),'sha256':hashlib.sha256(readable_alias).hexdigest(),'generated_alias_of':'evidence/producer/VISUAL_REVIEW.md'}
# Defence in depth: only public source/assets, never private packets/transport configuration.
patterns=[rb'github_pat_[A-Za-z0-9_]{20,}',rb'gh[pousr]_[A-Za-z0-9]{25,}',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',rb'sk-[A-Za-z0-9_-]{30,}']
for p in files:
 assert not any(x in p.parts for x in ['uploads','.private','.git','.cache'])
 if p.suffix in ['.py','.sh','.json','.md','.txt','.csv','.html']:
  data=p.read_bytes();assert not any(re.search(pattern,data) for pattern in patterns),'secret-like material blocked in '+str(p.relative_to(R))
tag='buildinglab/blender/candidate-20261016-'+ns[:12];filename='Casa-dei-Colori-candidate-20261016-'+ns[:12]+'.zip'
manifest={'format':1,'stage':'producer-checked candidate; independent acceptance pending','native_sha256':ns,'glb_sha256':gs,'source_commit_at_packaging':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'members':entries,'self_hash_note':'This manifest is not self-hashed. Archive SHA and publication/redownload/member verification are in a separate receipt.'}
mp=R/'exports/release-members.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
archive=R/'exports'/filename
# Excluded raw cache avoids duplicating a large immutable ZIP in workspace snapshots.
cache_archive=R/'.cache/release-archives'/filename;cache_archive.parent.mkdir(parents=True,exist_ok=True)
assert not archive.exists() and not archive.is_symlink(),'Immutable local archive name already exists'
with zipfile.ZipFile(cache_archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in sorted(files):z.write(p,str(p.relative_to(R)))
 z.writestr('evidence/visual-review.json',alias);z.writestr('evidence/VISUAL_REVIEW.md',readable_alias);z.write(mp,'exports/release-members.json')
archive.symlink_to(Path('../.cache/release-archives')/filename)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,r in entries.items():assert hashlib.sha256(z.read(name)).hexdigest()==r['sha256'],name
 assert z.read('evidence/visual-review.json')==z.read('evidence/producer/visual-review.json');assert z.read('evidence/VISUAL_REVIEW.md')==z.read('evidence/producer/VISUAL_REVIEW.md')
result={'stage':'built locally; NOT yet uploaded/redownload verified','archive':str(archive.relative_to(R)),'bytes':archive.stat().st_size,'sha256':sha(archive),'release_tag':tag,'release_url':'https://github.com/dreamer2664/storagecode/releases/tag/'+tag,'member_manifest_sha256':sha(mp),'hashed_payload_members':len(entries),'archive_entries_including_manifest':len(entries)+1,'native_sha256':ns,'glb_sha256':gs,'final_pngs':29,'independent_acceptance':'pending'}
(R/'exports/release-build.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
