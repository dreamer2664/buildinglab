"""Anonymous download and per-member verification of immutable production source packages."""
import urllib.request,zipfile,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];out=R/'.cache/recovery';out.mkdir(parents=True,exist_ok=True)
base='https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/production-20261016-4bf44a021c3d/'
records=[]
for key,name,size in [('Buildings','Winterlichtplatz-Buildings-4bf44a021c3d.zip',437436591),('People-rigs','Winterlichtplatz-People-rigs-4bf44a021c3d.zip',502164857),('Public-realm','Winterlichtplatz-Public-realm-4bf44a021c3d.zip',50443138)]:
 p=out/name
 if not p.exists() or p.stat().st_size!=size:
  tmp=p.with_suffix('.partial')
  with urllib.request.urlopen(base+name,timeout=120) as response,tmp.open('wb') as f:
   while b:=response.read(1024*1024):f.write(b)
  assert tmp.stat().st_size==size;tmp.replace(p)
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 members=[]
 with zipfile.ZipFile(p) as z:
  manifest=json.loads(z.read('Package-MANIFEST.json'))
  for member,expected in manifest['members'].items():
   digest=hashlib.sha256();n=0
   with z.open(member) as f:
    while b:=f.read(1024*1024):digest.update(b);n+=len(b)
   assert n==expected['bytes'] and digest.hexdigest()==expected['sha256'],member
   members.append({'name':member,'bytes':n,'sha256':digest.hexdigest()})
  assert z.testzip() is None
  # Retain provenance, not duplicate bulky natives: source remains publicly retrievable.
  for member in z.namelist():
   if member.endswith(('.json','.md','.txt','.py')) and member!='Package-MANIFEST.json':
    dest=R/'evidence/production/recovered-package-notes'/key/member;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(member))
 rec={'package':key,'url':base+name,'archive_bytes':size,'archive_sha256':h.hexdigest(),'crc':'PASS','all_manifest_members':'PASS','members':members};records.append(rec)
 (R/'evidence/production/public-package-recovery.json').write_text(json.dumps(records,indent=2)+'\n');print('PUBLIC_PACKAGE_VERIFIED',key,len(members),size,flush=True)
