"""Anonymous digest/CRC/every-member recovery of12preserved editable rigs; no credentials."""
from pathlib import Path
import urllib.request,hashlib,zipfile,json
R=Path(__file__).resolve().parents[1];doc=json.loads((R/'evidence/production/R11-unchanged-public-editable-rigs.json').read_text());a=doc['unchanged_editable_rig_archive'];out=R/'.cache/restored-editable-people';out.mkdir(parents=True,exist_ok=True);archive=out/a['asset']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
if not archive.exists():
 with urllib.request.urlopen(a['url'],timeout=180)as response,archive.with_suffix('.partial').open('wb')as f:
  while b:=response.read(1024*1024):f.write(b)
 archive.with_suffix('.partial').replace(archive)
assert archive.stat().st_size==a['bytes']and sha(archive)==a['sha256'];rows=[]
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None;m=json.loads(z.read('MANIFEST.json'));assert set(z.namelist())==set(m['members'])|{'MANIFEST.json'}
 for name,r in m['members'].items():
  h=hashlib.sha256();n=0
  with z.open(name)as f:
   while b:=f.read(1024*1024):h.update(b);n+=len(b)
  assert h.hexdigest()==r['sha256']and n==r['bytes'],name
 for rig in doc['all12_actual_current_rigs_exact_public_member_equal']:
  candidates=[n for n,r in m['members'].items()if n.endswith('.blend')and r['sha256']==rig['actual_saved_rig_sha256']];assert len(candidates)==1;name=candidates[0];path=out/(rig['rig']+'.blend')
  if not path.exists():
   with z.open(name)as src,path.open('xb')as dst:
    while b:=src.read(1024*1024):dst.write(b)
  assert sha(path)==rig['actual_saved_rig_sha256'];rows.append({'rig':rig['rig'],'member':name,'path':str(path.relative_to(R)),'sha256':sha(path),'bytes':path.stat().st_size})
report={'status':'PASS','actual_anonymous_archive_sha256':a['sha256'],'actual_archive_bytes':a['bytes'],'all_members_CRC_SHA_size':'PASS','recovered_editable_rigs':rows,'scope':'Actual recovery of exact previously preserved rig bytes, not fresh Blender open/visual quality. Original files immutable; any groom adaptation must save separately.'};(R/'evidence/production/R12-actual-editable-rig-recovery.json').write_text(json.dumps(report,indent=2)+'\n');print('ALL12_EDITABLE_RIGS_ANONYMOUSLY_RECOVERED_AND_VERIFIED',len(rows),a['sha256'],flush=True)
